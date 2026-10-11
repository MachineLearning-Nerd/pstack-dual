from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import re
import shutil
import tempfile
import tomllib
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("pstack", ROOT / "tools/pstack.py")
assert spec and spec.loader
pstack = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pstack)


class RuntimeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="pstack tests ")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)

    def config(self, base: Path, data: dict) -> None:
        path = base / ".pstack-dual/models.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data))

    def test_generated_bundle_indexes_and_explicit_exceptions_validate(self) -> None:
        self.assertEqual(pstack.validate_bundle()["references"], "valid")
        for target in ("principle-sequence-verifiable-units/SKILL.md",
                       "poteto-mode/playbooks/authoring-a-skill.md",
                       "poteto-mode/playbooks/multi-phase-plan.md",
                       "poteto-mode/playbooks/worktree-cleanup.md"):
            with self.subTest(target=target):
                self.assertTrue((ROOT / "skills" / target).is_file())

    def test_missing_indexed_principle_and_playbook_fail_validation(self) -> None:
        bundle = self.root / "skills"
        shutil.copytree(ROOT / "skills", bundle)
        for target in ("principle-laziness-protocol/SKILL.md",
                       "poteto-mode/playbooks/investigation.md"):
            path = bundle / target
            original = path.read_bytes()
            path.unlink()
            with self.subTest(target=target), patch.object(pstack, "skills_root", return_value=bundle):
                with self.assertRaisesRegex(ValueError, "broken indexed reference"):
                    pstack.validate_bundle()
            path.write_bytes(original)

    def test_session_defaults_keep_two_panel_arms(self) -> None:
        arms = pstack.resolve("codex", self.root, "interrogate reviewers", self.root / "user")
        self.assertEqual([arm["arm"] for arm in arms], [1, 2])
        self.assertTrue(all(arm["model"] is None and arm["effort"] is None for arm in arms))

    def test_project_roles_override_user_without_crossing_hosts(self) -> None:
        user = self.root / "user"
        self.config(user, {"version": 1, "codex": {"roles": {"feature": {"model": "gpt-6-sol", "effort": "high"}}},
                           "claude-code": {"roles": {"feature": {"model": "sonnet"}}}})
        self.config(self.root, {"version": 1, "codex": {"roles": {"feature": {"model": "gpt-6.1-sol", "effort": "medium"}}}})
        self.assertEqual(pstack.resolve("codex", self.root, "feature", user), [
            {"host": "codex", "role": "feature", "arm": 1, "model": None,
             "effort": "medium", "source": "project:feature", "ignored_model": "gpt-6.1-sol"}])
        self.assertEqual(pstack.resolve("claude-code", self.root, "feature", user), [
            {"host": "claude-code", "role": "feature", "arm": 1, "model": None,
             "effort": None, "source": "user:feature", "ignored_model": "sonnet"}])

    def test_legacy_defaults_preserve_effort_and_panel_count(self) -> None:
        self.config(self.root, {"version": 1, "codex": {"default": {"model": "gpt-6-sol", "effort": "max"}}})
        for role, count in [("bug-fix", 1), ("architect runners", 2)]:
            with self.subTest(role=role):
                self.assertEqual(pstack.resolve("codex", self.root, role, self.root / "user"), [
                    {"host": "codex", "role": role, "arm": arm, "model": None,
                     "effort": "max", "source": "project:default", "ignored_model": "gpt-6-sol"}
                    for arm in range(1, count + 1)])

    def test_legacy_panel_preserves_distinct_arms_and_efforts(self) -> None:
        user = self.root / "user"
        self.config(user, {"version": 1, "claude-code": {"panels": {"interrogate reviewers": [
            {"model": "sonnet", "effort": "high"}, {"model": "opus", "effort": "max"},
            {"model": "inherit-parent", "effort": "low"}]}}})
        self.assertEqual(pstack.resolve("claude-code", self.root, "interrogate reviewers", user), [
            {"host": "claude-code", "role": "interrogate reviewers", "arm": 1, "model": None,
             "effort": "high", "source": "user:interrogate reviewers", "ignored_model": "sonnet"},
            {"host": "claude-code", "role": "interrogate reviewers", "arm": 2, "model": None,
             "effort": "max", "source": "user:interrogate reviewers", "ignored_model": "opus"},
            {"host": "claude-code", "role": "interrogate reviewers", "arm": 3, "model": None,
             "effort": "low", "source": "user:interrogate reviewers"}])

    def test_inheritance_aliases_and_missing_models_do_not_report_ignored_models(self) -> None:
        for entry in [{}, {"model": "auto"}, {"model": "inherit"}, {"model": "inherit-parent"}]:
            with self.subTest(entry=entry):
                self.config(self.root, {"version": 1, "codex": {"roles": {"feature": entry}}})
                self.assertEqual(pstack.resolve("codex", self.root, "feature", self.root / "user"), [
                    {"host": "codex", "role": "feature", "arm": 1, "model": None,
                     "effort": None, "source": "project:feature"}])

    def test_partial_entry_does_not_borrow_effort_from_user(self) -> None:
        user = self.root / "user"
        self.config(user, {"version": 1, "codex": {"roles": {"feature": {"model": "gpt-6-sol", "effort": "max"}}}})
        self.config(self.root, {"version": 1, "codex": {"roles": {"feature": {"model": "inherit-parent"}}}})
        arm = pstack.resolve("codex", self.root, "feature", user)[0]
        self.assertIsNone(arm["model"])
        self.assertIsNone(arm["effort"])

    def test_bad_host_models_and_efforts_are_rejected(self) -> None:
        for host, entry in [("codex", {"model": "opus"}), ("claude-code", {"model": "gpt-6-sol"}),
                            ("claude-code", {"effort": "ultra"}), ("codex", {"effort": "typo"})]:
            with self.subTest(host=host, entry=entry), self.assertRaises(ValueError):
                pstack.validate_config({"version": 1, host: {"default": entry}})

    def test_empty_panel_unknown_role_and_unknown_fields_fail(self) -> None:
        for config in [{"version": 1, "codex": {"panels": {"arena runners": []}}},
                       {"version": 1, "codex": {"roles": {"typo": {}}}},
                       {"version": 1, "codex": {"default": {"effrot": "high"}}}]:
            with self.subTest(config=config), self.assertRaises(ValueError):
                pstack.validate_config(config)

    def test_non_scalar_effort_and_boolean_version_fail_cleanly(self) -> None:
        for config in [{"version": True}, {"version": 1, "codex": {"default": {"effort": []}}}]:
            with self.subTest(config=config), self.assertRaises(ValueError):
                pstack.validate_config(config)

    def test_native_codex_manifests_parse_with_read_only_reviewers(self) -> None:
        files = pstack.native_agents(self.root, "codex")
        for path, data in files.items():
            manifest = tomllib.loads(data.decode())
            self.assertIn(str(self.root), manifest["developer_instructions"])
            if "poteto-agent" not in path:
                self.assertEqual(manifest["sandbox_mode"], "read-only")
            self.assertNotIn("model", manifest)

    def test_install_is_self_contained_and_idempotent(self) -> None:
        pstack.install(self.root, list(pstack.HOSTS))
        link = self.root / ".agents/skills/poteto-mode"
        self.assertTrue(link.is_symlink())
        self.assertTrue(link.resolve().is_relative_to(self.root))
        self.assertTrue((link / "playbooks/bug-fix.md").is_file())
        self.assertTrue((self.root / ".pstack-dual/bundle/README.md").is_file())
        before = (self.root / ".codex/agents/poteto-agent.toml").stat().st_mtime_ns
        pstack.install(self.root, ["codex"])
        self.assertEqual((self.root / ".codex/agents/poteto-agent.toml").stat().st_mtime_ns, before)
        self.assertTrue((self.root / ".claude/skills/poteto-mode").is_symlink())

    def test_install_preserves_reference_pack_without_activating_it(self) -> None:
        pstack.install(self.root, list(pstack.HOSTS))
        bundle = self.root / ".pstack-dual/bundle"
        for target in ("automations/benny/FOR_AGENTS.md", "automations/benny/README.md",
                       "automations/benny/skills/setup-benny/SKILL.md", "assets/logo.png",
                       "docs/PARITY.md"):
            with self.subTest(target=target):
                self.assertEqual((bundle / target).read_bytes(), (ROOT / target).read_bytes())
        for guide in (bundle / "docs/guide").rglob("*.md"):
            for target in re.findall(r"\]\(([^)\s]+)\)", guide.read_text()):
                if "://" in target or target.startswith(("#", "mailto:")):
                    continue
                with self.subTest(guide=guide.name, target=target):
                    self.assertTrue((guide.parent / target.split("#", 1)[0]).exists())
        self.assertFalse((self.root / ".agents/skills/setup-benny").exists())
        self.assertFalse((self.root / ".claude/skills/setup-benny").exists())
        self.assertFalse((self.root / ".cursor/settings.json").exists())

    def test_conflicts_fail_before_any_write(self) -> None:
        path = self.root / ".claude/skills/how/SKILL.md"
        path.parent.mkdir(parents=True)
        path.write_text("existing user skill")
        with self.assertRaisesRegex(ValueError, "conflicts"):
            pstack.install(self.root, list(pstack.HOSTS))
        self.assertEqual(path.read_text(), "existing user skill")
        self.assertFalse((self.root / ".pstack-dual").exists())

    def test_modified_payload_prevents_update_and_uninstall(self) -> None:
        pstack.install(self.root, ["codex"])
        path = self.root / ".agents/skills/how/SKILL.md"
        path.write_text("user modification")
        with self.assertRaisesRegex(ValueError, "conflicts"):
            pstack.install(self.root, ["codex"])
        with self.assertRaisesRegex(ValueError, "nothing removed"):
            pstack.uninstall(self.root)
        self.assertEqual(path.read_text(), "user modification")

    def test_uninstall_preserves_config_and_unrelated_files(self) -> None:
        self.config(self.root, {"version": 1})
        extra = self.root / ".claude/agents/user-agent.md"
        extra.parent.mkdir(parents=True)
        extra.write_text("mine")
        pstack.install(self.root, list(pstack.HOSTS))
        pstack.uninstall(self.root)
        self.assertEqual(extra.read_text(), "mine")
        self.assertTrue((self.root / ".pstack-dual/models.json").is_file())
        self.assertFalse((self.root / ".agents/skills/how").exists())

    def test_parent_symlink_escape_and_ledger_symlink_are_rejected(self) -> None:
        outside = self.root / "outside"
        outside.mkdir()
        project = self.root / "project"
        project.mkdir()
        (project / ".codex").symlink_to(outside, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "escapes"):
            pstack.install(project, ["codex"])
        self.assertEqual(list(outside.iterdir()), [])
        (project / ".codex").unlink()
        (project / ".pstack-dual").mkdir()
        ledger = outside / "ledger.json"
        ledger.write_text('{"version":1,"hosts":[],"files":{}}')
        (project / ".pstack-dual/install.json").symlink_to(ledger)
        with self.assertRaisesRegex(ValueError, "symlink"):
            pstack.install(project, ["codex"])

    def test_interrupted_install_can_resume(self) -> None:
        real_symlink = Path.symlink_to
        calls = 0

        def fail_once(path: Path, *args, **kwargs):
            nonlocal calls
            calls += 1
            if calls == 2:
                raise OSError("simulated interrupted installation")
            return real_symlink(path, *args, **kwargs)

        with patch.object(Path, "symlink_to", fail_once), self.assertRaises(OSError):
            pstack.install(self.root, ["codex"])
        pstack.install(self.root, ["codex"])
        self.assertTrue((self.root / ".agents/skills/poteto-mode/SKILL.md").is_file())
        self.assertNotIn("previous_files", pstack.load_json(self.root / pstack.LEDGER))

    def test_dry_run_does_not_write(self) -> None:
        result = pstack.install(self.root, list(pstack.HOSTS), dry_run=True)
        self.assertTrue(result["dry_run"])
        self.assertEqual(list(self.root.iterdir()), [])


if __name__ == "__main__":
    unittest.main()
