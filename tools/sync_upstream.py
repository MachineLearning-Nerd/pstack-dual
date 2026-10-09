#!/usr/bin/env python3
"""Update the official upstream snapshot to an explicitly selected commit."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

import build

ROOT = Path(__file__).resolve().parent.parent
REPOSITORY = "https://github.com/cursor/plugins.git"


def snapshot(source: Path, destination: Path) -> dict:
    shutil.copytree(source / "pstack", destination / "pstack")
    for name in ("deslop", "control-cli", "control-ui"):
        shutil.copytree(source / "cursor-team-kit/skills" / name, destination / "cursor-team-kit/skills" / name)
    shutil.copyfile(source / "cursor-team-kit/LICENSE", destination / "cursor-team-kit/LICENSE")
    version = json.loads((destination / "pstack/.cursor-plugin/plugin.json").read_text())["version"]
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=source, text=True).strip()
    files = {str(p.relative_to(destination)): hashlib.sha256(p.read_bytes()).hexdigest()
             for p in sorted(destination.rglob("*")) if p.is_file()}
    return {"repository": REPOSITORY, "commit": commit, "pstack_version": version, "files": files}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--commit", required=True)
    parser.add_argument("--source-checkout", type=Path, help="Use a local checkout of the official source at the exact commit")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if not re.fullmatch(r"[0-9a-f]{40}", args.commit):
        parser.error("--commit must be a full lowercase 40-character Git commit ID")
    try:
        build.verify_snapshot()
        # Staging beside upstream keeps the backup rename on the project's filesystem.
        with tempfile.TemporaryDirectory(prefix=".pstack-sync-", dir=ROOT) as temporary:
            scratch = Path(temporary)
            source = args.source_checkout.resolve() if args.source_checkout else scratch / "checkout"
            if not args.source_checkout:
                source.mkdir()
                for command in (["git", "init"], ["git", "remote", "add", "origin", REPOSITORY],
                                ["git", "config", "core.sparseCheckout", "true"]):
                    subprocess.run(command, cwd=source, check=True, capture_output=True, timeout=30)
                (source / ".git/info/sparse-checkout").write_text("/pstack/\n/cursor-team-kit/\n")
                subprocess.run(["git", "fetch", "--filter=blob:none", "--depth=1", "origin", args.commit], cwd=source, check=True, capture_output=True, timeout=180)
                subprocess.run(["git", "checkout", "--detach", "FETCH_HEAD"], cwd=source, check=True, capture_output=True, timeout=180)
            actual = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=source, text=True).strip()
            if actual != args.commit:
                raise ValueError(f"checkout is at {actual}, requested {args.commit}")
            if args.source_checkout:
                dirty = subprocess.check_output(["git", "status", "--porcelain", "--", "pstack", "cursor-team-kit"], cwd=source, text=True)
                if dirty:
                    raise ValueError("local source checkout has modifications")
            incoming = scratch / "upstream"
            lock = snapshot(source, incoming)
            old_lock = (ROOT / "upstream.lock.json").read_bytes()
            old_license = (ROOT / "LICENSE").read_bytes()
            old = json.loads(old_lock)
            changes = sorted(name for name in set(old["files"]) | set(lock["files"])
                             if old["files"].get(name) != lock["files"].get(name))
            print(json.dumps({"commit": actual, "pstack_version": lock["pstack_version"], "changed_files": changes, "dry_run": args.dry_run}, indent=2))
            if args.dry_run:
                return 0
            backup = scratch / "previous"
            (ROOT / "upstream").rename(backup)
            try:
                shutil.copytree(incoming, ROOT / "upstream")
                (ROOT / "upstream.lock.json").write_text(json.dumps(lock, indent=2) + "\n")
                shutil.copyfile(incoming / "pstack/LICENSE", ROOT / "LICENSE")
                subprocess.run([sys.executable, str(ROOT / "tools/build.py")], cwd=ROOT, check=True)
                subprocess.run([sys.executable, str(ROOT / "tools/pstack.py"), "validate"], cwd=ROOT, check=True)
            except BaseException:
                shutil.rmtree(ROOT / "upstream")
                backup.rename(ROOT / "upstream")
                (ROOT / "upstream.lock.json").write_bytes(old_lock)
                (ROOT / "LICENSE").write_bytes(old_license)
                subprocess.run([sys.executable, str(ROOT / "tools/build.py")], cwd=ROOT, check=True)
                raise
            return 0
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        print(f"sync failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
