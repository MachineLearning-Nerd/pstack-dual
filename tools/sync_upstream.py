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
import check_upstream

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
    parser.add_argument("--reviews", type=Path, help="Reviewed candidate upstream-reviews.json; installed only with a successful import")
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
            reviews_path = args.reviews or ROOT / "upstream-reviews.json"
            reviews_bytes = reviews_path.read_bytes()
            reviews = json.loads(reviews_bytes)
            coverage = check_upstream.audit(ROOT, snapshot=incoming, lock=lock,
                                            reviews=reviews, check_generated=False)
            print(json.dumps({"commit": actual, "pstack_version": lock["pstack_version"],
                              "changed_files": changes, "dry_run": args.dry_run,
                              "coverage": coverage}, indent=2))
            if not coverage["valid"]:
                raise ValueError("incoming source needs review; inspect coverage.errors and supply --reviews")
            if args.dry_run:
                return 0
            old_reviews = (ROOT / "upstream-reviews.json").read_bytes()
            generated_backup = scratch / "generated"
            for relative in build.OUTPUTS:
                current, saved = ROOT / relative, generated_backup / relative
                if current.exists():
                    saved.parent.mkdir(parents=True, exist_ok=True)
                    if current.is_dir():
                        shutil.copytree(current, saved)
                    else:
                        shutil.copy2(current, saved)
            backup = scratch / "previous"
            (ROOT / "upstream").rename(backup)
            try:
                shutil.copytree(incoming, ROOT / "upstream")
                (ROOT / "upstream.lock.json").write_text(json.dumps(lock, indent=2) + "\n")
                (ROOT / "upstream-reviews.json").write_bytes(reviews_bytes)
                shutil.copyfile(incoming / "pstack/LICENSE", ROOT / "LICENSE")
                subprocess.run([sys.executable, str(ROOT / "tools/build.py")], cwd=ROOT, check=True)
                subprocess.run([sys.executable, str(ROOT / "tools/pstack.py"), "validate"], cwd=ROOT, check=True)
                subprocess.run([sys.executable, str(ROOT / "tools/check_upstream.py")], cwd=ROOT, check=True)
            except BaseException:
                if (ROOT / "upstream").exists():
                    shutil.rmtree(ROOT / "upstream")
                backup.rename(ROOT / "upstream")
                (ROOT / "upstream.lock.json").write_bytes(old_lock)
                (ROOT / "LICENSE").write_bytes(old_license)
                (ROOT / "upstream-reviews.json").write_bytes(old_reviews)
                for relative in build.OUTPUTS:
                    current, saved = ROOT / relative, generated_backup / relative
                    if current.is_dir():
                        shutil.rmtree(current)
                    elif current.exists():
                        current.unlink()
                    if saved.exists():
                        current.parent.mkdir(parents=True, exist_ok=True)
                        if saved.is_dir():
                            shutil.copytree(saved, current)
                        else:
                            shutil.copy2(saved, current)
                raise
            return 0
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        print(f"sync failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
