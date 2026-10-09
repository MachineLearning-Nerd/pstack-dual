from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import evaluate


class EvaluationTests(unittest.TestCase):
    def test_claude_string_messages_do_not_break_agent_receipts(self) -> None:
        events = "\n".join([json.dumps({"type": "system", "message": "progress"}),
            json.dumps({"type": "assistant", "message": {"content": [{"type": "tool_use", "name": "Agent", "input": {"model": "sonnet", "subagent_type": "pstack-effort-high"}}]}})])
        self.assertEqual(evaluate.claude_agent_calls(events), [{"model": "sonnet", "subagent_type": "pstack-effort-high"}])

    def test_source_text_mention_does_not_establish_delegation(self) -> None:
        output = json.dumps({"type": "item.completed", "item": {"type": "command_execution", "aggregated_output": "Use spawn_agent to delegate"}})
        self.assertFalse(evaluate.delegation_observed(output, "codex"))
        output = json.dumps({"type": "assistant", "message": {"content": [{"type": "text", "text": 'The tool name is "Agent"'}]}})
        self.assertFalse(evaluate.delegation_observed(output, "claude-code"))

    def test_native_spawn_events_are_distinct_from_failed_waits(self) -> None:
        for status, ids, expected in [("completed", ["child-1"], True), ("in_progress", [], False), ("completed", [], False)]:
            output = json.dumps({"type": "item.completed", "item": {"type": "collab_tool_call", "tool": "spawn_agent", "status": status, "receiver_thread_ids": ids}})
            self.assertEqual(evaluate.delegation_observed(output, "codex"), expected)
        output = json.dumps({"type": "assistant", "message": {"content": [{"type": "tool_use", "name": "Agent", "input": {}}]}})
        self.assertTrue(evaluate.delegation_observed(output, "claude-code"))

    def test_grader_rejects_claimed_fix_without_changed_behavior(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp) / "project"
            evaluate.prepare(project, "bug-fix", "codex")
            before = evaluate.fingerprint(project)
            with self.assertRaisesRegex(AssertionError, "normalization"):
                evaluate.grade(project, "bug-fix", before, "I fixed app.py and verified everything.")

    def test_read_only_grader_detects_non_source_side_effects(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp) / "project"
            evaluate.prepare(project, "investigation", "codex")
            before = evaluate.fingerprint(project)
            (project / "unexpected.json").write_text("{}")
            with self.assertRaisesRegex(AssertionError, "read-only"):
                evaluate.grade(project, "investigation", before, "app.py normalize_tags total_cents 1550")


if __name__ == "__main__":
    unittest.main()
