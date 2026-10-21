#!/usr/bin/env python3
"""Install, inspect, and resolve the portable pstack bundle (stdlib only)."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
from typing import Any

HOSTS = ("codex", "claude-code")
INHERIT = {"inherit-parent", "inherit", "auto"}
EFFORTS = {"low", "medium", "high", "xhigh", "max", "ultra"}
ROLES = {"default", "feature", "refactoring", "bug-fix", "perf-issue", "hillclimb",
         "judgment and prose", "hardest tasks", "how explorer", "how explainer",
         "why investigators", "why synthesizer", "reflect tooling", "reflect judgment",
         "reflect divergent", "reflect synthesizer", "swarm workers", "trail reviewer"}
PANELS = {"arena runners", "arena cross-judge pool", "architect runners", "interrogate reviewers"}
LEDGER = ".pstack-dual/install.json"


def skills_root() -> Path:
    script = Path(__file__).resolve()
    if script.parent.name == "scripts":
        return script.parents[2]
    return script.parent.parent / "skills"


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise ValueError(f"{path}: expected an object")
    return value


def validate_entry(entry: Any, host: str) -> None:
    if not isinstance(entry, dict) or set(entry) - {"model", "effort"}:
        raise ValueError("role entries accept only model and effort")
    model = entry.get("model", "inherit-parent")
    effort = entry.get("effort", "inherit-parent")
    if not isinstance(model, str) or not model or not re.fullmatch(r"[\w.\[\]-]+", model):
        raise ValueError("model must be a nonempty model identifier")
    if not isinstance(effort, str) or effort not in EFFORTS | INHERIT:
        raise ValueError(f"unsupported effort: {effort}")
    if host == "claude-code":
        if model not in INHERIT | {"sonnet", "opus", "haiku", "fable"} and not model.startswith("claude-"):
            raise ValueError(f"Claude cannot use model {model}")
        if effort == "ultra":
            raise ValueError("Claude does not accept ultra effort")
    elif model not in INHERIT and (model.startswith(("claude-", "grok-")) or model in {"sonnet", "opus", "haiku", "fable"}):
        raise ValueError(f"Codex cannot use Claude/Grok model {model}")


def validate_config(config: dict[str, Any]) -> None:
    if type(config.get("version")) is not int or config.get("version") != 1 or set(config) - {"version", *HOSTS}:
        raise ValueError("config requires version 1 and codex/claude-code sections")
    for host in HOSTS:
        section = config.get(host, {})
        if not isinstance(section, dict) or set(section) - {"default", "roles", "panels"}:
            raise ValueError(f"invalid {host} section")
        if "default" in section:
            validate_entry(section["default"], host)
        for field, allowed in (("roles", ROLES), ("panels", PANELS)):
            values = section.get(field, {})
            if not isinstance(values, dict) or set(values) - allowed:
                raise ValueError(f"unknown {host} {field}: {set(values) - allowed if isinstance(values, dict) else values}")
            for value in values.values():
                if field == "panels":
                    if not isinstance(value, list) or not value:
                        raise ValueError("panels require a nonempty list")
                    for entry in value:
                        validate_entry(entry, host)
                else:
                    validate_entry(value, host)


def resolve(host: str, project: Path, role: str, user_root: Path | None = None) -> list[dict[str, Any]]:
    if role not in ROLES | PANELS:
        raise ValueError(f"unknown role: {role}")
    field = "panels" if role in PANELS else "roles"
    layers = [("project", project / ".pstack-dual/models.json"),
              ("user", (user_root or Path.home()) / ".pstack-dual/models.json")]
    configs: list[tuple[str, dict[str, Any]]] = []
    for source, path in layers:
        if path.exists():
            config = load_json(path)
            validate_config(config)
            configs.append((source, config.get(host, {})))
    source = "session-default"
    entries = None
    for name, section in configs:
        if role in section.get(field, {}):
            entries = section[field][role]
            source = name + ":" + role
            break
        if "default" in section:
            entries = [section["default"]] * 2 if role in PANELS else section["default"]
            source = name + ":default"
            break
    if entries is None:
        entries = [{"model": "inherit-parent", "effort": "inherit-parent"}] * (2 if role in PANELS else 1)
    elif not isinstance(entries, list):
        entries = [entries]
    arms = []
    for i, entry in enumerate(entries, 1):
        arm = {"host": host, "role": role, "arm": i, "model": None,
               "effort": None if entry.get("effort", "inherit-parent") in INHERIT else entry["effort"],
               "source": source}
        if entry.get("model", "inherit-parent") not in INHERIT:
            arm["ignored_model"] = entry["model"]
        arms.append(arm)
    return arms


def native_agents(root: Path, host: str) -> dict[str, bytes]:
    bundle = root / ".pstack-dual/bundle/skills"
    mode = bundle / "poteto-mode/SKILL.md"
    harness = bundle / "pstack-harness/SKILL.md"
    review = bundle / "pstack-review/SKILL.md"
    briefs = {
        "poteto-agent": ("Implement bounded pstack tasks with behavioral verification.",
                         f"Read {mode} in full before working, including its inline Principles index, and read {harness}. The parent chat owns the playbook and worklist. Execute only the parent's bounded brief, and read each leaf principle skill you apply. Respect the user's explicit scope and actual permissions."),
        "pstack-reviewer": ("Read-only independent review of scoped artifacts.",
                            f"Read {review} and {harness}. Remain read-only. Find reachable defects and cite evidence; do not edit, commit, or publish."),
        "comment-sicko": ("Review comments in the scoped diff without editing code.",
                          f"Read {bundle / 'pstack-harness/references/comment-sicko.md'} and {harness}. Report findings only; do not edit files.")}
    files = {}
    for name, (description, prompt) in briefs.items():
        if host == "codex":
            body = f'name = {json.dumps(name)}\ndescription = {json.dumps(description)}\ndeveloper_instructions = {json.dumps(prompt)}\n'
            if name != "poteto-agent":
                body += 'sandbox_mode = "read-only"\n'
            files[f".codex/agents/{name}.toml"] = body.encode()
        else:
            body = f"---\nname: {name}\ndescription: {description}\n"
            if name != "poteto-agent":
                body += "tools: Read, Glob, Grep, Bash\npermissionMode: plan\n"
            body += f"---\n\n{prompt}\n"
            files[f".claude/agents/{name}.md"] = body.encode()
    if host == "claude-code":
        for effort in sorted(EFFORTS - {"ultra"}):
            body = f"---\nname: pstack-effort-{effort}\ndescription: Pstack delegate with {effort} reasoning effort; takes the persona from its brief.\neffort: {effort}\n---\n\nFollow the provided persona, bounded scope, and {harness}.\n"
            files[f".claude/agents/pstack-effort-{effort}.md"] = body.encode()
    return files


def state(path: Path) -> dict[str, str] | None:
    if path.is_symlink():
        return {"type": "link", "target": os.readlink(path)}
    if path.is_file():
        return {"type": "file", "sha256": digest(path.read_bytes())}
    if path.exists():
        return {"type": "directory"}
    return None


def safe_path(root: Path, relative: str) -> Path:
    rel = Path(relative)
    if rel.is_absolute() or ".." in rel.parts:
        raise ValueError(f"unsafe installation path: {relative}")
    path = root / rel
    if not path.parent.resolve().is_relative_to(root.resolve()):
        raise ValueError(f"installation parent escapes destination: {relative}")
    return path


def installation_plan(root: Path, hosts: list[str]) -> dict[str, bytes | str]:
    source = skills_root()
    plan: dict[str, bytes | str] = {}
    for path in sorted(source.rglob("*")):
        if (path.is_file() and not {"__pycache__", "node_modules"}.intersection(path.relative_to(source).parts)
                and path.suffix != ".pyc"):
            plan[f".pstack-dual/bundle/skills/{path.relative_to(source)}"] = path.read_bytes()
    for relative in ("docs/guide", "docs/harness", "automations", "assets"):
        directory = source.parent / relative
        for path in sorted(directory.rglob("*")):
            if path.is_file():
                plan[f".pstack-dual/bundle/{relative}/{path.relative_to(directory)}"] = path.read_bytes()
    for relative in ("README.md", "LICENSE", "THIRD_PARTY_NOTICES.md", "docs/PORTING.md", "docs/VERIFICATION.md", "docs/UPSTREAM.md", "docs/PARITY.md", "docs/RELEASES.md"):
        path = source.parent / relative
        if path.is_file():
            plan[f".pstack-dual/bundle/{relative}"] = path.read_bytes()
    names = sorted(path.parent.name for path in source.glob("*/SKILL.md"))
    for host in hosts:
        directory = ".agents/skills" if host == "codex" else ".claude/skills"
        for name in names:
            link = root / directory / name
            plan[f"{directory}/{name}"] = os.path.relpath(root / ".pstack-dual/bundle/skills" / name, link.parent)
        plan.update(native_agents(root, host))
    return plan


def install(root: Path, hosts: list[str], dry_run: bool = False) -> dict[str, Any]:
    root = root.resolve()
    if not root.is_dir():
        raise ValueError("destination must be an existing directory")
    ledger_path = safe_path(root, LEDGER)
    if ledger_path.is_symlink():
        raise ValueError("install ledger must not be a symlink")
    ledger = load_json(ledger_path) if ledger_path.exists() else {"version": 1, "hosts": [], "files": {}}
    if ledger.get("version") != 1:
        raise ValueError("unsupported install ledger version")
    hosts = sorted(set(hosts) | set(ledger["hosts"]))
    if set(hosts) - set(HOSTS):
        raise ValueError("unknown host in install ledger")
    plan = installation_plan(root, hosts)
    conflicts = []
    for rel, expected in ledger["files"].items():
        actual = state(safe_path(root, rel))
        if actual is not None and actual not in (expected, ledger.get("previous_files", {}).get(rel)):
            conflicts.append(rel)
    for rel in plan:
        if state(safe_path(root, rel)) is not None and rel not in ledger["files"]:
            conflicts.append(rel)
    if conflicts:
        raise ValueError("installation conflicts (no writes): " + ", ".join(sorted(set(conflicts))))
    if dry_run:
        return {"destination": str(root), "hosts": hosts, "files": len(plan), "dry_run": True}
    desired = {rel: {"type": "link", "target": payload} if isinstance(payload, str)
               else {"type": "file", "sha256": digest(payload)} for rel, payload in plan.items()}
    # A write-ahead ledger makes an interrupted install recoverable without adoption.
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    journal = {"version": 1, "hosts": hosts, "files": {**ledger["files"], **desired},
               "previous_files": {**ledger.get("previous_files", {}), **ledger["files"]}}
    temporary_ledger = ledger_path.with_suffix(".pending")
    with temporary_ledger.open("x") as stream:
        stream.write(json.dumps(journal, indent=2) + "\n")
    temporary_ledger.replace(ledger_path)
    source = skills_root()
    bundle_prefix = ".pstack-dual/bundle/skills/"
    for rel, payload in plan.items():
        path = safe_path(root, rel)
        path.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(payload, str):
            if path.is_symlink() and os.readlink(path) != payload:
                path.unlink()
            if not path.is_symlink():
                path.symlink_to(payload, target_is_directory=True)
        elif not path.is_file() or path.read_bytes() != payload:
            temporary = path.with_name(path.name + ".pstack-tmp")
            with temporary.open("xb") as stream:
                stream.write(payload)
            temporary.replace(path)
        if isinstance(payload, bytes) and rel.startswith(bundle_prefix):
            executable = (source / rel.removeprefix(bundle_prefix)).stat().st_mode & 0o111
            mode = path.stat().st_mode & 0o777
            if executable and mode & executable != executable:
                path.chmod(mode | executable)
    for rel in set(ledger["files"]) - set(plan):
        path = safe_path(root, rel)
        if state(path) is not None:
            path.unlink()
    new_ledger = {"version": 1, "hosts": hosts, "files": {rel: state(root / rel) for rel in plan}}
    ledger_path.write_text(json.dumps(new_ledger, indent=2) + "\n")
    return {"destination": str(root), "hosts": hosts, "files": len(plan), "native_activation": "unverified; start a fresh session and inspect the catalog"}


def uninstall(root: Path) -> dict[str, Any]:
    root = root.resolve()
    ledger_path = safe_path(root, LEDGER)
    if ledger_path.is_symlink():
        raise ValueError("install ledger must not be a symlink")
    ledger = load_json(ledger_path)
    conflicts = [rel for rel, expected in ledger["files"].items()
                 if state(safe_path(root, rel)) not in (None, expected, ledger.get("previous_files", {}).get(rel))]
    if conflicts:
        raise ValueError("modified managed files; nothing removed: " + ", ".join(conflicts))
    for rel in sorted(ledger["files"], reverse=True):
        path = safe_path(root, rel)
        if state(path) is not None:
            path.unlink()
    ledger_path.unlink()
    # Remove only empty directories left by this install; keep models and user files.
    for path in sorted((root / ".pstack-dual/bundle").rglob("*"), reverse=True):
        if path.is_dir() and not path.is_symlink():
            try:
                path.rmdir()
            except OSError:
                pass
    return {"removed_files": len(ledger["files"]), "config_preserved": True}


def validate_bundle() -> dict[str, Any]:
    source = skills_root()
    skills = sorted(source.glob("*/SKILL.md"))
    if not skills:
        raise ValueError("bundle has no skills; run tools/build.py")
    names = set()
    for path in skills:
        text = path.read_text()
        match = re.match(r"---\n(.*?)\n---\n", text, re.S)
        if not match:
            raise ValueError(f"missing frontmatter: {path}")
        header = match[1]
        name_match = re.search(r"^name: ([a-z0-9-]+)$", header, re.M)
        if not name_match or name_match[1] != path.parent.name or not re.search(r"^description: .+", header, re.M):
            raise ValueError(f"invalid skill metadata: {path}")
        if name_match[1] in names:
            raise ValueError(f"duplicate skill name: {name_match[1]}")
        names.add(name_match[1])
        if not (path.parent / "LICENSE").is_file():
            raise ValueError(f"missing attribution: {path}")
    index = source / "poteto-mode/SKILL.md"
    index_text = index.read_text()
    for heading, prefix, suffix in (("Principles", "../principle-", "/SKILL.md"),
                                     ("Playbooks", "playbooks/", ".md")):
        section = re.search(rf"^## {heading}\n(.*?)(?=^## |\Z)", index_text, re.M | re.S)
        if not section:
            raise ValueError(f"missing {heading} index: {index}")
        for title, entry in re.findall(r"^- \*\*([^*]+)\*\*(.*)$", section[1], re.M):
            slug = re.sub(r"\s+", "-", re.sub(r"[^a-z0-9\s-]", "", title.lower()))
            target = prefix + slug + suffix
            if heading == "Principles":
                explicit = re.search(r"\(\*\*(principle-[a-z0-9-]+)\*\*\)", entry)
                if explicit:
                    target = "../" + explicit[1] + "/SKILL.md"
            else:
                explicit = re.search(r"`(playbooks/[^`]+\.md)`", entry)
                if explicit:
                    target = explicit[1]
            if not (index.parent / target).is_file():
                raise ValueError(f"broken indexed reference {target}: {index}")
    for path in source.rglob("*.md"):
        if "node_modules" in path.relative_to(source).parts:
            continue
        text = path.read_text()
        if re.search(r"~?/\.cursor/|grok-\d|claude-opus-\d", text):
            raise ValueError(f"unadapted Cursor path/model: {path}")
        for target in re.findall(r"\]\(([^)\s]+)\)", text):
            if "://" in target or target.startswith(("#", "mailto:")) or any(x in target for x in "<>*"):
                continue
            local = target.split("#", 1)[0]
            if local == "url":  # Literal citation placeholder in the upstream prompt template.
                continue
            if local and not (path.parent / local).exists():
                raise ValueError(f"broken reference {target}: {path}")
    return {"skills": len(skills), "references": "valid", "licenses": "present"}


def doctor(project: Path) -> dict[str, Any]:
    report = {"bundle": validate_bundle(), "clis": {}, "configuration": {}, "native_files": {}}
    for host in HOSTS:
        executable = "claude" if host == "claude-code" else "codex"
        if shutil.which(executable):
            run = subprocess.run([executable, "--version"], capture_output=True, text=True, timeout=10)
            report["clis"][host] = run.stdout.strip() if run.returncode == 0 else "version check failed"
        else:
            report["clis"][host] = "not installed"
        report["configuration"][host] = resolve(host, project, "feature")
        report["native_files"][host] = {rel: "current" if (project / rel).is_file() and (project / rel).read_bytes() == expected
                                       else "modified" if (project / rel).exists() else "missing"
                                       for rel, expected in native_agents(project.resolve(), host).items()}
    report["native_activation"] = "unverified; inspect a fresh session's agent catalog"
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("install", "uninstall"):
        command = commands.add_parser(name)
        command.add_argument("--target", type=Path, required=True)
        if name == "install":
            command.add_argument("--agents", nargs="+", choices=HOSTS, default=list(HOSTS))
            command.add_argument("--dry-run", action="store_true")
    command = commands.add_parser("resolve")
    command.add_argument("--host", choices=HOSTS, required=True)
    command.add_argument("--project", type=Path, required=True)
    command.add_argument("--role", choices=sorted(ROLES | PANELS), required=True)
    command = commands.add_parser("doctor")
    command.add_argument("--project", type=Path, required=True)
    commands.add_parser("validate")
    command = commands.add_parser("validate-config")
    command.add_argument("--file", type=Path, required=True)
    command = commands.add_parser("config-init")
    command.add_argument("--project", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "install":
            result = install(args.target, args.agents, args.dry_run)
        elif args.command == "uninstall":
            result = uninstall(args.target)
        elif args.command == "resolve":
            result = resolve(args.host, args.project.resolve(), args.role)
        elif args.command == "doctor":
            result = doctor(args.project.resolve())
        elif args.command == "validate":
            result = validate_bundle()
        elif args.command == "validate-config":
            validate_config(load_json(args.file))
            result = {"valid": True, "file": str(args.file)}
        else:
            project = args.project.resolve()
            if not project.is_dir():
                raise ValueError("project must be an existing directory")
            path = safe_path(project, ".pstack-dual/models.json")
            path.parent.mkdir(parents=True, exist_ok=True)
            value = {"version": 1, **{host: {"default": {"model": "inherit-parent", "effort": "inherit-parent"}} for host in HOSTS}}
            with path.open("x") as stream:
                stream.write(json.dumps(value, indent=2) + "\n")
            result = {"created": str(path)}
        print(json.dumps(result, indent=2))
        return 0
    except (ValueError, OSError, KeyError, TypeError, subprocess.TimeoutExpired) as error:
        print(f"pstack: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
