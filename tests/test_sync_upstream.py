from __future__ import annotations

import contextlib
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
SPEC = importlib.util.spec_from_file_location("sync_upstream", ROOT / "tools/sync_upstream.py")
SYNC = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SYNC)


class SyncUpstreamTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="upstream transaction ")
        self.addCleanup(self.temporary.cleanup)
        base = Path(self.temporary.name)
        self.root = base / "derivative"
        self.root.mkdir()
        for relative in ("tools", "overrides", "upstream", *SYNC.build.OUTPUTS):
            source, destination = ROOT / relative, self.root / relative
            if source.is_dir():
                shutil.copytree(source, destination, ignore=shutil.ignore_patterns("__pycache__"))
            else:
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, destination)
        for relative in ("upstream.lock.json", "upstream-reviews.json", "LICENSE", "README.md",
                         ".gitignore", "docs/PORTING.md", "docs/PARITY.md", "docs/RELEASES.md"):
            destination = self.root / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / relative, destination)
        self.source = base / "official"
        shutil.copytree(self.root / "upstream", self.source)
        self.commit = "1" * 40
        self.candidate = base / "candidate-reviews.json"
        self.candidate.write_bytes((self.root / "upstream-reviews.json").read_bytes())

    def state(self) -> dict:
        return {str(path.relative_to(self.root)): (path.read_bytes(), path.stat().st_mode & 0o777)
                for path in self.root.rglob("*")
                if path.is_file() and "__pycache__" not in path.parts}

    def review_candidate(self, relative: str) -> None:
        reviews = json.loads(self.candidate.read_text())
        reviews["reviews"][relative]["sha256"] = hashlib.sha256((self.source / relative).read_bytes()).hexdigest()
        self.candidate.write_text(json.dumps(reviews) + "\n")

    def invoke(self, *extra: str, run=None, actual_commit=None) -> tuple[int, str]:
        argv = ["sync_upstream", "--commit", self.commit, "--source-checkout", str(self.source), *extra]

        def git_output(command, **kwargs):
            if command[:2] == ["git", "status"]:
                return ""
            return (actual_commit or self.commit) + "\n"

        output = io.StringIO()
        with (patch.object(SYNC, "ROOT", self.root), patch.object(SYNC.build, "ROOT", self.root),
              patch.object(sys, "argv", argv), patch.object(SYNC.subprocess, "check_output", side_effect=git_output),
              contextlib.redirect_stdout(output), contextlib.redirect_stderr(output)):
            if run:
                with patch.object(SYNC.subprocess, "run", side_effect=run):
                    result = SYNC.main()
            else:
                result = SYNC.main()
        return result, output.getvalue()

    def test_preview_rejects_masked_improvement_without_mutating_checkout(self) -> None:
        relative = "pstack/skills/poteto-mode/playbooks/feature.md"
        with (self.source / relative).open("a") as stream:
            stream.write("\nA new upstream requirement that the override would hide.\n")
        before = self.state()
        result, output = self.invoke("--dry-run")
        self.assertEqual(result, 1, output)
        self.assertIn("review hash differs from current source", output)
        self.assertEqual(self.state(), before)
        self.assertEqual(list(self.root.glob(".pstack-sync-*")), [])

    def test_reviewed_preview_and_import_keep_source_and_ledger_together(self) -> None:
        relative = "pstack/skills/poteto-mode/playbooks/feature.md"
        with (self.source / relative).open("a") as stream:
            stream.write("\nReviewed fixture change.\n")
        self.review_candidate(relative)
        before = self.state()
        result, output = self.invoke("--reviews", str(self.candidate), "--dry-run")
        self.assertEqual(result, 0, output)
        self.assertEqual(self.state(), before)
        result, output = self.invoke("--reviews", str(self.candidate))
        self.assertEqual(result, 0, output)
        self.assertEqual((self.root / "upstream" / relative).read_bytes(), (self.source / relative).read_bytes())
        self.assertEqual((self.root / "upstream-reviews.json").read_bytes(), self.candidate.read_bytes())
        self.assertEqual(json.loads((self.root / "upstream.lock.json").read_text())["commit"], self.commit)
        self.assertTrue(SYNC.check_upstream.audit(self.root)["valid"])

    def test_partial_build_failure_restores_exact_previous_artifacts(self) -> None:
        before = self.state()

        def fail_build(command, **kwargs):
            if str(command[1]).endswith("build.py"):
                helper = self.root / "skills/poteto-mode/scripts/worktree-audit.sh"
                helper.write_text("partially overwritten")
                helper.chmod(0o600)
                (self.root / "docs/harness/partial.md").write_text("partial output")
                raise subprocess.CalledProcessError(1, command)
            self.fail(f"Unexpected command: {command}")

        result, output = self.invoke(run=fail_build)
        self.assertEqual(result, 1, output)
        self.assertEqual(self.state(), before)
        self.assertEqual(list(self.root.glob(".pstack-sync-*")), [])

    def test_late_validation_failure_restores_snapshot_reviews_and_outputs(self) -> None:
        relative = "pstack/skills/poteto-mode/playbooks/feature.md"
        with (self.source / relative).open("a") as stream:
            stream.write("\nCandidate source.\n")
        self.review_candidate(relative)
        before = self.state()
        real_run = subprocess.run

        def fail_validation(command, **kwargs):
            if str(command[1]).endswith("pstack.py"):
                raise subprocess.CalledProcessError(1, command)
            return real_run(command, **kwargs)

        result, output = self.invoke("--reviews", str(self.candidate), run=fail_validation)
        self.assertEqual(result, 1, output)
        self.assertEqual(self.state(), before)

    def test_changed_mode_anchor_fails_even_with_fresh_source_review(self) -> None:
        relative = "pstack/skills/poteto-mode/SKILL.md"
        source = self.source / relative
        source.write_text(source.read_text().replace("**Defaults for every `Task` call.**", "**Renamed defaults.**"))
        self.review_candidate(relative)
        before = self.state()
        result, output = self.invoke("--reviews", str(self.candidate))
        self.assertEqual(result, 1, output)
        self.assertEqual(self.state(), before)

    def test_wrong_commit_or_malformed_review_candidate_has_no_writes(self) -> None:
        before = self.state()
        result, output = self.invoke(actual_commit="2" * 40)
        self.assertEqual(result, 1, output)
        self.assertEqual(self.state(), before)
        self.candidate.write_text("{")
        result, output = self.invoke("--reviews", str(self.candidate))
        self.assertEqual(result, 1, output)
        self.assertEqual(self.state(), before)


if __name__ == "__main__":
    unittest.main()
