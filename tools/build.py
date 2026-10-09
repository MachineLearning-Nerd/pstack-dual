#!/usr/bin/env python3
"""Reproduce the adapted bundle from the pinned snapshot and explicit overrides."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import tempfile

ROOT = Path(__file__).resolve().parent.parent
ADAPTER = """\n## Host compatibility\n\nRead [pstack-harness](../pstack-harness/SKILL.md) before using this workflow.\nIts native-tool, role-config, scope, and permission contract takes precedence over\nbackend-specific examples below. Read only the references needed for this task.\n\n"""


def adapt(text: str) -> str:
    substitutions = {
        "~/.cursor/rules/pstack-models.mdc": ".pstack-dual/models.json (resolve through pstack-harness)",
        "pstack-models.mdc": "pstack role configuration (resolve through pstack-harness)",
        "~/.cursor/projects/<slug>/agent-transcripts/<uuid>/<uuid>.jsonl": "the current host's workspace-scoped session record (see pstack-harness)",
        "~/.cursor/projects/*/": "other workspaces' session stores",
        "~/.cursor/skills": "~/.agents/skills", ".cursor/skills": ".agents/skills",
        "~/.cursor/plugins/": "the installed pstack bundle/",
        ".cursor/automations/": ".agents/automations/",
        "Cursor's built-in `create-skill`": "the bundled `create-skill`",
        "Cursor's built-in for authoring SKILL.md files": "bundled portable authoring guidance",
        "Cursor's `/loop` command": "an available host loop (or explicit manual re-invocation)",
        "Cursor cloud agent": "isolated local worker", "Cursor cloud agents": "isolated local workers",
        "cursor-team-kit plugin": "bundled cursor-team-kit skills",
        "`readonly` strips MCP": "read-only access depends on the actual host",
        "readonly strips MCP": "read-only access depends on the actual host",
        "Readonly strips MCPs.": "Read-only access depends on the actual host.",
        "git show origin/main:pstack/skills/": "git show origin/main:skills/",
        "**Just do it.** Use any MCP tool. Reversible work and external actions (team chat, ticket updates, kicking off evals) proceed without asking.":
        "**Act within scope.** Complete authorized reversible work. External messages and other external actions require authorization from the user's task; this skill grants none.",
    }
    for before, after in substitutions.items():
        text = text.replace(before, after)
    text = re.sub(r"(?:claude-(?:opus|fable|sonnet|haiku)-[\w.-]+|grok-\d[\w.-]*)", "inherit-parent", text)
    return text


def verify_snapshot() -> None:
    lock = json.loads((ROOT / "upstream.lock.json").read_text())
    actual = {str(p.relative_to(ROOT / "upstream")): hashlib.sha256(p.read_bytes()).hexdigest()
              for p in sorted((ROOT / "upstream").rglob("*")) if p.is_file()}
    if actual != lock["files"]:
        raise ValueError("upstream snapshot differs from upstream.lock.json")


def generate(destination: Path) -> None:
    verify_snapshot()
    skills = destination / "skills"
    shutil.copytree(ROOT / "upstream/pstack/skills", skills)
    for name in ("deslop", "control-cli", "control-ui"):
        shutil.copytree(ROOT / "upstream/cursor-team-kit/skills" / name, skills / name)
    for path in sorted(skills.rglob("*.md")):
        path.write_text(adapt(path.read_text()))
    for path in sorted((ROOT / "overrides").rglob("*")):
        if path.is_file():
            target = skills / path.relative_to(ROOT / "overrides")
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, target)
    for path in skills.glob("*/SKILL.md"):
        text = path.read_text()
        header, body = text.split("---", 2)[1:]
        header = re.sub(r"^name:.*$", f"name: {path.parent.name}", header, flags=re.M)
        header = re.sub(r"^(mode|icon|color|reminder):.*\n", "", header, flags=re.M)
        if path.parent.name != "pstack-harness":
            body = "\n" + ADAPTER + body.lstrip("\n")
        if path.parent.name == "poteto-mode":
            body = body.replace("## Non-negotiables", "## Review routing\n\nA request to review a diff, branch, or PR uses playbooks/code-review.md and\npstack-review. It remains read-only and does not enter the Babysit lifecycle.\nCore feature and bug-fix playbooks in this derivative govern local completion;\nPR creation and commits require the user's requested scope.\n\n## Non-negotiables", 1)
        path.write_text("---" + header + "---\n" + body)
        license_source = ROOT / ("upstream/cursor-team-kit/LICENSE" if path.parent.name in {"deslop", "control-cli", "control-ui"} else "LICENSE")
        shutil.copyfile(license_source, path.parent / "LICENSE")
        if "disable-model-invocation: true" in header:
            metadata = path.parent / "agents/openai.yaml"
            metadata.parent.mkdir(exist_ok=True)
            metadata.write_text("policy:\n  allow_implicit_invocation: false\n")
    scripts = skills / "pstack-harness/scripts"
    scripts.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(ROOT / "tools/pstack.py", scripts / "pstack.py")
    shutil.copyfile(ROOT / "upstream/pstack/agents/comment-sicko.md", skills / "pstack-harness/references/comment-sicko.md")
    guide = destination / "docs/guide"
    shutil.copytree(ROOT / "upstream/pstack/docs/guide", guide)
    for path in guide.rglob("*.md"):
        path.write_text("<!-- Historical upstream guide adapted for paths; see ../../PORTING.md for support status. -->\n" + adapt(path.read_text()))
    adapters = destination / "adapters"
    adapters.mkdir()
    (adapters / "README.md").write_text("Native agent definitions are rendered at install time with the destination's absolute bundled skill paths. See tools/pstack.py native_agents(). No host settings or credentials are changed.\n")
    lock = json.loads((ROOT / "upstream.lock.json").read_text())
    (destination / "THIRD_PARTY_NOTICES.md").write_text(
        f"# Attribution\n\nThis derivative starts from cursor/plugins commit\n`{lock['commit']}`, pstack version {lock['pstack_version']}.\n\n"
        "* pstack: Lauren Tan (poteto), MIT, upstream/pstack/LICENSE.\n"
        "* deslop, control-cli, control-ui: Cursor, MIT, upstream/cursor-team-kit/LICENSE.\n\n"
        "All imported files are recorded by SHA-256 in upstream.lock.json. Adapted copies\n"
        "are generated with tools/build.py. Native compatibility code and overrides are\n"
        "distributed under the root MIT license. This project does not claim authorship\n"
        "of poteto's engineering principles or represent an official upstream release.\n")


def tree(path: Path) -> dict[str, bytes]:
    return {str(p.relative_to(path)): p.read_bytes() for p in path.rglob("*")
            if p.is_file() and "__pycache__" not in p.parts and p.suffix != ".pyc"}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="pstack-build-") as temporary:
        out = Path(temporary)
        generate(out)
        for relative in ("skills", "docs/guide", "adapters", "THIRD_PARTY_NOTICES.md"):
            current, expected = ROOT / relative, out / relative
            if expected.is_file():
                if args.check:
                    if not current.is_file() or current.read_bytes() != expected.read_bytes():
                        raise SystemExit(f"generated file drifted: {relative}")
                else:
                    shutil.copyfile(expected, current)
                continue
            if args.check:
                if not current.exists() or tree(current) != tree(expected):
                    raise SystemExit(f"generated files drifted: {relative}; run tools/build.py")
            else:
                if current.exists():
                    shutil.rmtree(current)
                shutil.copytree(expected, current)
    print("Generated bundle is current." if args.check else "Generated portable bundle.")


if __name__ == "__main__":
    main()
