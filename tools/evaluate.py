#!/usr/bin/env python3
"""Run opt-in live pstack cases in disposable repositories using both native CLIs."""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import time
from typing import Any

import pstack

ROOT = Path(__file__).resolve().parent.parent
CORE_CASES = ("investigation", "bug-fix", "feature", "review")
CASES = (*CORE_CASES, "native-delegation")


def prepare(project: Path, case: str, host: str) -> tuple[str, str]:
    project.mkdir()
    (project / ".gitignore").write_text(".pstack-dual/\n.agents/\n.claude/\n.codex/\n__pycache__/\n*.pyc\n")
    (project / "AGENTS.md").write_text("This is an isolated evaluation fixture. Stay within this project. Do not edit installed skills or instructions, commit, publish, access external services, or read other projects. A single implementation worker and a fresh read-only reviewer are sufficient. Respect the original application contract and verify through python3 app.py.\n")
    (project / "CLAUDE.md").write_text("Read AGENTS.md. Use the installed standalone pstack skills and native agents.\n")
    base = """import argparse
import json


def normalize_tags(tags):
    result = []
    for tag in tags:
        value = tag.strip().lower()
        if value and value not in result:
            result.append(value)
    return result


def total_cents(prices, shipping=200):
    return sum(prices) * 9 // 10 + shipping


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    tags = sub.add_parser("tags")
    tags.add_argument("values", nargs="*")
    total = sub.add_parser("total")
    total.add_argument("values", nargs="*", type=int)
    args = parser.parse_args()
    if args.command == "tags":
        print(json.dumps(normalize_tags(args.values)))
    elif args.command == "total":
        print(total_cents(args.values))


if __name__ == "__main__":
    main()
"""
    prompt = {
        "investigation": "Explain how the total command computes checkout totals and how tags are normalized. Run the actual CLI with total 1000 500 and cite the file and functions. This is read-only: do not change files.",
        "bug-fix": "The tags CLI emits duplicates when equivalent tags differ by case or whitespace. Reproduce with tags ' AI ' ai '' ML ml, trace the cause, fix it, and verify. Contract: strip, lowercase, remove empty strings, preserve first-occurrence order, and deduplicate normalized values. Remain within app.py and any regression tests you add; no commits or PRs.",
        "feature": "Add a tag-count CLI subcommand accepting zero or more tag strings. It prints the integer count of distinct normalized nonempty tags, reusing the existing normalization contract. Preserve tags and total commands. Verify normal, duplicate, and empty inputs. Edit only app.py and any behavioral tests you add; no commits or PRs.",
        "review": "Review the working-tree change to app.py. Identify concrete reachable correctness regressions, cite the affected function and triggering input, and obtain independent read-only review if available. Run safe commands for evidence. Do not fix, stage, commit, or change any source or tests.",
        "native-delegation": "Read pstack-harness and resolve this project's feature role. Spawn exactly one read-only delegate with the resolved effort, using a fresh context and inheriting this chat's model. Omit the model argument. Ask it to read app.py and identify the tag normalization function, then wait for its actual completed result. On Claude, use the loaded pstack-effort-high agent and run it in the foreground. On Codex, pass reasoning_effort high with fork_turns none; use pstack-reviewer if agent_type is exposed, otherwise brief the read-only persona. Do not edit any source or installation files. Report the function name and the actual mechanism, including any unavailable persona or effort setting.",
    }[case]
    if case == "bug-fix":
        base = base.replace("if value and value not in result:", "if value:")
    (project / "app.py").write_text(base)
    (project / "README.md").write_text("CLI: python3 app.py tags ... or total <integer cents> ... . Tags strip whitespace, lowercase, ignore empty strings, deduplicate normalized strings, and preserve order. Totals discount the subtotal by 10 percent, round down to cents, then add 200 cents shipping.\n")
    subprocess.run(["git", "init", "-b", "main"], cwd=project, check=True, capture_output=True)
    subprocess.run(["git", "add", "app.py", "README.md", "AGENTS.md", "CLAUDE.md", ".gitignore"], cwd=project, check=True)
    subprocess.run(["git", "-c", "user.name=Pstack Evaluation", "-c", "user.email=pstack-eval@example.invalid", "commit", "-m", "Fixture baseline"], cwd=project, check=True, capture_output=True)
    if case == "review":
        (project / "app.py").write_text(base.replace("if value and value not in result:", "if value:").replace("sum(prices) * 9 // 10 + shipping", "(sum(prices) + shipping) * 9 // 10"))
    pstack.install(project, [host])
    if case == "native-delegation":
        config = {"version": 1, host: {"roles": {"feature": {"model": "inherit-parent", "effort": "high"}}}}
        (project / ".pstack-dual/models.json").write_text(json.dumps(config) + "\n")
    mention = "$pstack-review" if host == "codex" and case == "review" else "/pstack-review" if case == "review" else "$poteto-mode" if host == "codex" else "/poteto-mode"
    return mention + " " + prompt, base


def fingerprint(project: Path) -> dict[str, str]:
    return {str(p.relative_to(project)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in project.rglob("*") if p.is_file()
            and not any(part in {".git", ".pstack-dual", ".agents", ".claude", ".codex", "__pycache__"} for part in p.relative_to(project).parts)}


def cli(project: Path, *args: str) -> str:
    result = subprocess.run([sys.executable, "app.py", *args], cwd=project, capture_output=True, text=True, timeout=10)
    if result.returncode:
        raise AssertionError(f"CLI {' '.join(args)} failed: {result.stderr}")
    return result.stdout.strip()


def grade(project: Path, case: str, before: dict[str, str], response: str) -> dict[str, Any]:
    checks = []
    after = fingerprint(project)
    if case in {"investigation", "review", "native-delegation"}:
        if before != after:
            raise AssertionError("read-only workflow changed project files")
        checks.append("project files unchanged")
        if "app.py" not in response:
            raise AssertionError("response omitted source citation")
    else:
        for relative, sha in before.items():
            if relative != "app.py" and after.get(relative) != sha:
                raise AssertionError(f"unrelated existing file changed: {relative}")
        for relative in set(after) - set(before):
            path = Path(relative)
            if not (path.suffix == ".py" and (path.name.startswith("test_") or "tests" in path.parts)):
                raise AssertionError(f"unrelated file added: {relative}")
    if case == "native-delegation":
        if "normalize_tags" not in response:
            raise AssertionError("delegation did not return the actual function")
        checks.append("read-only delegate returned the source symbol")
    elif case == "investigation":
        if "1550" not in response or "normalize_tags" not in response or "total_cents" not in response:
            raise AssertionError("explanation lacks the observed total or relevant symbols")
        checks.append("correct source-grounded total and normalization explanation")
    elif case in {"bug-fix", "feature"}:
        for values, expected in [([], []), ([" AI ", "ai", "", "ML", "ml"], ["ai", "ml"]), (["B", "a", "b"], ["b", "a"])]:
            if json.loads(cli(project, "tags", *values)) != expected:
                raise AssertionError(f"normalization contract failed for {values}")
            if case == "feature" and cli(project, "tag-count", *values) != str(len(expected)):
                raise AssertionError(f"tag-count failed for {values}")
        if cli(project, "total", "1000", "500") != "1550":
            raise AssertionError("existing total behavior regressed")
        checks.append("independent CLI assertions: empty, normalization, duplicates, order, existing total")
    else:
        lowered = response.lower()
        if not (any(w in lowered for w in ("duplicate", "deduplic", "dedup")) and "shipping" in lowered
                and any(w in lowered for w in ("discount", "1530", "20 cents"))):
            raise AssertionError("review did not identify both seeded reachable regressions")
        checks.append("both seeded defects identified")
    return {"pass": True, "checks": checks}


def final_response(events: str, host: str) -> str:
    parts = []
    for line in events.splitlines():
        try:
            value = json.loads(line)
        except ValueError:
            continue
        if host == "claude-code" and value.get("type") == "result":
            parts.append(value.get("result", ""))
        if host == "codex" and value.get("type") == "item.completed":
            item = value.get("item", {})
            if item.get("type") == "agent_message":
                parts.append(item.get("text", ""))
    return "\n".join(parts)


def claude_agent_calls(events: str) -> list[dict[str, Any]]:
    calls = []
    for line in events.splitlines():
        try:
            value = json.loads(line)
        except ValueError:
            continue
        message = value.get("message")
        if value.get("type") != "assistant" or not isinstance(message, dict):
            continue
        for item in message.get("content", []):
            if item.get("type") == "tool_use" and item.get("name") in {"Agent", "Task"}:
                calls.append(item.get("input", {}))
    return calls


def delegation_observed(events: str, host: str) -> bool:
    if host == "claude-code":
        calls = set()
        completed = set()
        for line in events.splitlines():
            try:
                value = json.loads(line)
            except ValueError:
                continue
            message = value.get("message")
            if not isinstance(message, dict):
                continue
            content = message.get("content", [])
            if not isinstance(content, list):
                continue
            for item in content:
                if item.get("type") == "tool_use" and item.get("name") in {"Agent", "Task"} and item.get("id"):
                    calls.add(item["id"])
                elif item.get("type") == "tool_result" and not item.get("is_error") and item.get("tool_use_id"):
                    completed.add(item["tool_use_id"])
        return bool(calls & completed)
    for line in events.splitlines():
        try:
            value = json.loads(line)
        except ValueError:
            continue
        if host == "codex":
            item = value.get("item", {})
            if item.get("type") == "collab_tool_call" and item.get("tool") == "spawn_agent" and item.get("status") == "completed" and item.get("receiver_thread_ids"):
                return True
    return False


def delegation_completed(events: str, host: str) -> bool:
    delegates = set()
    for line in events.splitlines():
        try:
            value = json.loads(line)
        except ValueError:
            continue
        if host == "codex":
            item = value.get("item", {})
            if value.get("type") != "item.completed" or item.get("type") != "collab_tool_call" or item.get("status") != "completed":
                continue
            if item.get("tool") == "spawn_agent":
                delegates.update(item.get("receiver_thread_ids", []))
            elif item.get("tool") == "wait":
                states = item.get("agents_states", {})
                if any(receiver in delegates and state.get("status") == "completed"
                       for receiver, state in states.items()):
                    return True
        elif host == "claude-code":
            message = value.get("message")
            if not isinstance(message, dict) or not isinstance(message.get("content"), list):
                continue
            for item in message["content"]:
                if item.get("type") == "tool_use" and item.get("name") in {"Agent", "Task"} and item.get("id"):
                    if not item.get("input", {}).get("run_in_background"):
                        delegates.add(item["id"])
                elif item.get("type") == "tool_result" and not item.get("is_error") and item.get("tool_use_id") in delegates:
                    return True
    return False


def codex_spawn_receipts(events: str, project: Path) -> list[dict[str, Any]]:
    """Inspect only this evaluation's exact parent rollout, never other messages."""
    thread_id = None
    for line in events.splitlines():
        try:
            event = json.loads(line)
        except ValueError:
            continue
        if event.get("type") == "thread.started":
            thread_id = event.get("thread_id")
            break
    if not isinstance(thread_id, str) or not re.fullmatch(r"[0-9a-f-]{36}", thread_id):
        return []
    sessions = Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex"))) / "sessions"
    receipts = []
    for path in sessions.glob(f"*/*/*/*{thread_id}*.jsonl"):
        with path.open() as stream:
            header = json.loads(stream.readline())
            if header.get("type") != "session_meta" or Path(header.get("payload", {}).get("cwd", "")).resolve() != project.resolve():
                continue
            for line in stream:
                try:
                    event = json.loads(line)
                except ValueError:
                    continue
                payload = event.get("payload", {})
                if payload.get("type") == "function_call" and payload.get("name", "").rsplit(".", 1)[-1] == "spawn_agent":
                    arguments = json.loads(payload.get("arguments", "{}"))
                    receipts.append({key: arguments[key] for key in ("task_name", "agent_type", "fork_turns", "model", "reasoning_effort") if key in arguments})
    return receipts


def grade_native_delegation(host: str, calls: list[dict[str, Any]], completed: bool) -> str:
    if not completed:
        raise AssertionError("no completed native delegation observed")
    if len(calls) != 1:
        raise AssertionError("expected exactly one native delegate")
    call = calls[0]
    if "model" in call:
        raise AssertionError("native delegate must inherit the current chat model without a model argument")
    if host == "claude-code" and call.get("run_in_background"):
        raise AssertionError("native evaluation requires a completed foreground Claude delegate")
    if host == "codex":
        if call.get("reasoning_effort") != "high" or call.get("fork_turns") != "none":
            raise AssertionError("inherited Codex model with fresh context and high effort was not observed")
    elif call.get("subagent_type") != "pstack-effort-high":
        raise AssertionError("Claude's inherited-model high-effort agent was not observed")
    return "successful native delegation omitted a model override and requested high effort"


def run_case(host: str, case: str, run_dir: Path, timeout: int) -> dict[str, Any]:
    label = f"{host}-{case}"
    out = run_dir / label
    out.mkdir()
    print(f"START {label}", flush=True)
    started = time.monotonic()
    record: dict[str, Any] = {"host": host, "case": case, "pass": False}
    with tempfile.TemporaryDirectory(prefix=f"pstack-eval-{label}-") as temp:
        project = Path(temp) / "project"
        prompt, _ = prepare(project, case, host)
        before = fingerprint(project)
        if host == "codex":
            command = ["codex", "exec", "--ignore-user-config", "--model", "gpt-6.1-sol", "-c", 'model_reasoning_effort="high"', "--sandbox", "workspace-write", "--json", "--color", "never", "-"]
        else:
            command = ["claude", "-p", "--model", "sonnet", "--effort", "high", "--output-format", "stream-json", "--verbose", "--no-session-persistence", "--setting-sources", "project", "--strict-mcp-config", "--mcp-config", '{"mcpServers":{}}', "--permission-mode", "acceptEdits", "--max-budget-usd", "5", "--allowedTools", "Read", "Glob", "Grep", "Edit", "Write", "Bash(python3 *)", "Bash(git diff *)", "Bash(git status *)", "Bash(git worktree *)", "Bash(git show *)", "Bash(git log *)", "Bash(git branch *)", "Agent", "Task", "Skill", "TodoWrite", "TaskCreate", "TaskUpdate", "TaskList", "TaskGet"]
        environment = dict(os.environ)
        environment["CLAUDE_CODE_ENABLE_TODO_TOOLS"] = "1"
        environment.pop("CLAUDECODE", None)
        try:
            with (out / "events.jsonl").open("w") as stdout, (out / "stderr.log").open("w") as stderr:
                process = subprocess.Popen(command, cwd=project, env=environment, stdin=subprocess.PIPE, stdout=stdout, stderr=stderr, text=True, start_new_session=True)
                try:
                    process.communicate(prompt, timeout=timeout)
                except subprocess.TimeoutExpired:
                    import signal
                    os.killpg(process.pid, signal.SIGTERM)
                    try:
                        process.wait(timeout=10)
                    except subprocess.TimeoutExpired:
                        os.killpg(process.pid, signal.SIGKILL)
                        process.wait()
                    raise TimeoutError(f"case exceeded {timeout}s")
            events = (out / "events.jsonl").read_text()
            response = final_response(events, host)
            (out / "response.md").write_text(response)
            (out / "app.py").write_text((project / "app.py").read_text())
            diff = subprocess.run(["git", "diff"], cwd=project, text=True, capture_output=True, check=True).stdout
            (out / "diff.patch").write_text(diff)
            record["exit_code"] = process.returncode
            record["delegation_event_observed"] = delegation_observed(events, host)
            if host == "codex":
                record["native_spawn_receipts"] = codex_spawn_receipts(events, project)
            if process.returncode:
                raise AssertionError(f"CLI exit {process.returncode}; inspect local logs")
            record.update(grade(project, case, before, response))
            if case == "native-delegation":
                observed = record["native_spawn_receipts"] if host == "codex" else claude_agent_calls(events)
                record["native_completion_observed"] = delegation_completed(events, host)
                record["checks"].append(grade_native_delegation(host, observed, record["native_completion_observed"]))
        except (OSError, TimeoutError, AssertionError, ValueError, subprocess.SubprocessError) as error:
            record["pass"] = False
            record["error"] = str(error)
        record["duration_seconds"] = round(time.monotonic() - started, 1)
        record["cli_version"] = subprocess.run(["claude" if host == "claude-code" else "codex", "--version"], text=True, capture_output=True, timeout=10).stdout.strip()
    (out / "result.json").write_text(json.dumps(record, indent=2) + "\n")
    print(f"DONE {label}: {'PASS' if record['pass'] else 'FAIL'} ({record['duration_seconds']}s) {record.get('error', '')}", flush=True)
    return record


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--hosts", nargs="+", choices=pstack.HOSTS, required=True)
    parser.add_argument("--cases", nargs="+", choices=CASES, default=list(CORE_CASES))
    parser.add_argument("--timeout", type=int, default=600)
    args = parser.parse_args()
    run_dir = ROOT / "evals/runs" / time.strftime("%Y%m%d-%H%M%S")
    run_dir.mkdir(parents=True)
    records = []
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = [pool.submit(run_case, host, case, run_dir, args.timeout) for case in args.cases for host in args.hosts]
        for future in as_completed(futures):
            records.append(future.result())
    summary = {"upstream_commit": json.loads((ROOT / "upstream.lock.json").read_text())["commit"],
               "run_directory": str(run_dir.relative_to(ROOT)), "results": sorted(records, key=lambda r: (r["case"], r["host"]))}
    (ROOT / "evals/latest.json").write_text(json.dumps(summary, indent=2) + "\n")
    rows = ["# Live evaluation results", "", f"Run: `{summary['run_directory']}`.", "", "| Host | Case | Result | Seconds | Native delegation observed |", "| --- | --- | --- | --- | --- |"]
    for record in summary["results"]:
        rows.append(f"| {record['host']} | {record['case']} | {'PASS' if record['pass'] else 'FAIL'} | {record['duration_seconds']} | {record.get('delegation_event_observed', False)} |")
        if not record["pass"]:
            rows.append(f"\nFailure: {record.get('error', 'unavailable')}\n")
    rows += ["", "These are actual CLI runs with independent graders. Logs are local and ignored by Git.", "An observed delegation event establishes an attempt; the transcript must establish completion.", "Passing these cases does not establish advanced-workflow coverage.", ""]
    (ROOT / "docs/LIVE_RESULTS.md").write_text("\n".join(rows))
    return 0 if all(record["pass"] for record in records) else 1


if __name__ == "__main__":
    raise SystemExit(main())
