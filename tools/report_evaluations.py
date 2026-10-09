#!/usr/bin/env python3
"""Aggregate actual saved evaluation receipts, including native Codex rollout calls."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re

import evaluate

ROOT = Path(__file__).resolve().parent.parent


def parent_workspace(events: str) -> Path | None:
    for line in events.splitlines():
        try:
            event = json.loads(line)
        except ValueError:
            continue
        thread_id = event.get("thread_id") if event.get("type") == "thread.started" else None
        if not isinstance(thread_id, str) or not re.fullmatch(r"[0-9a-f-]{36}", thread_id):
            continue
        sessions = Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex"))) / "sessions"
        for path in sessions.glob(f"*/*/*/*{thread_id}*.jsonl"):
            with path.open() as stream:
                header = json.loads(stream.readline())
            cwd = header.get("payload", {}).get("cwd", "")
            if header.get("type") == "session_meta" and cwd.startswith("/tmp/pstack-eval-"):
                return Path(cwd)
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs", nargs="+", type=Path, required=True)
    args = parser.parse_args()
    selected = {}
    for run in args.runs:
        run = run.resolve()
        paths = sorted(run.glob("*/result.json"))
        if not run.is_dir() or not paths:
            parser.error(f"no completed receipts in {run}")
        for path in paths:
            record = json.loads(path.read_text())
            events = (path.parent / "events.jsonl").read_text()
            record["delegation_event_observed"] = evaluate.delegation_observed(events, record["host"])
            if record["host"] == "codex":
                workspace = parent_workspace(events)
                if workspace:
                    record["native_spawn_receipts"] = evaluate.codex_spawn_receipts(events, workspace)
                    record["delegation_event_observed"] |= bool(record["native_spawn_receipts"])
            record["receipt_directory"] = str(path.parent.relative_to(ROOT))
            selected[record["host"], record["case"]] = record
    missing = [f"{host}:{case}" for host in evaluate.pstack.HOSTS for case in evaluate.CORE_CASES if (host, case) not in selected]
    summary = {"upstream_commit": json.loads((ROOT / "upstream.lock.json").read_text())["commit"],
               "missing_core_cases": missing, "results": sorted(selected.values(), key=lambda item: (item["case"], item["host"]))}
    (ROOT / "evals/latest.json").write_text(json.dumps(summary, indent=2) + "\n")
    rows = ["# Live evaluation results", "", "Actual CLI runs; no simulated agent results.", "",
            "| Host | Case | Result | Seconds | Native delegation observed |", "| --- | --- | --- | --- | --- |"]
    for record in summary["results"]:
        rows.append(f"| {record['host']} | {record['case']} | {'PASS' if record['pass'] else 'FAIL'} | {record['duration_seconds']} | {record.get('delegation_event_observed', False)} |")
    rows += ["", f"Missing core cases: {', '.join(missing) if missing else 'none'}.", "",
             "Investigation and review graders assert project files remain unchanged. Bug/feature", "graders independently exercise CLI edge cases and existing behavior. The native-delegation",
             "case checks explicit model/effort arguments and the returned source symbol.", "",
             "Native observation comes from Claude tool events or the exact evaluation parent's",
             "Codex rollout. It establishes a recorded delegation attempt; parent reports and",
             "application checks supply completion evidence. No unrelated session messages are read.", "",
             "Local logs are ignored by Git; evals/latest.json retains the nonsecret grader receipts.",
             "Codex 0.162.0 ephemeral sessions failed full-context delegation during the initial",
             "run. The final tests use normal sessions, and the adapter handles rejected spawns.",
             "This Codex tool catalog did not expose agent_type, so the native spawns received",
             "persona briefings. Claude's native pstack-reviewer and pstack-effort-high loaded.",
             "These cases do not establish advanced cloud/overnight workflow coverage.", ""]
    (ROOT / "docs/LIVE_RESULTS.md").write_text("\n".join(rows))
    print(json.dumps({"cases": len(selected), "passed": sum(bool(r["pass"]) for r in selected.values()), "missing_core_cases": missing}))
    return 0 if not missing and all(record["pass"] for record in selected.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
