from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

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
        self.assertFalse(evaluate.delegation_observed(output, "claude-code"))

    def test_claude_delegation_requires_a_matching_successful_result(self) -> None:
        call = {"type": "assistant", "message": {"content": [
            {"type": "tool_use", "name": "Agent", "id": "delegate-1", "input": {}}]}}
        for result_id, is_error, expected in [("delegate-1", False, True), ("delegate-1", True, False),
                                              ("other-tool", False, False)]:
            result = {"type": "user", "message": {"content": [
                {"type": "tool_result", "tool_use_id": result_id, "is_error": is_error, "content": "normalize_tags"}]}}
            with self.subTest(result_id=result_id, is_error=is_error):
                self.assertEqual(evaluate.delegation_observed("\n".join(map(json.dumps, [call, result])), "claude-code"), expected)

    def test_native_grader_accepts_inherited_model_and_high_effort(self) -> None:
        for host, call in [("codex", {"fork_turns": "none", "reasoning_effort": "high"}),
                           ("claude-code", {"subagent_type": "pstack-effort-high"})]:
            with self.subTest(host=host):
                self.assertEqual(evaluate.grade_native_delegation(host, [call], True),
                                 "successful native delegation omitted a model override and requested high effort")

    def test_native_grader_rejects_every_explicit_model_argument(self) -> None:
        for host, call in [("codex", {"fork_turns": "none", "reasoning_effort": "high"}),
                           ("claude-code", {"subagent_type": "pstack-effort-high"})]:
            for model in [None, "gpt-6.1-sol", "sonnet", "inherit"]:
                with self.subTest(host=host, model=model), self.assertRaisesRegex(AssertionError, "without a model argument"):
                    evaluate.grade_native_delegation(host, [{**call, "model": model}], True)

    def test_native_grader_rejects_failed_spawns_and_incomplete_call_evidence(self) -> None:
        call = {"fork_turns": "none", "reasoning_effort": "high"}
        for calls, completed in [([call], False), ([], True), ([call, call], True),
                                 ([{"fork_turns": "none"}], True), ([{"reasoning_effort": "high"}], True)]:
            with self.subTest(calls=calls, completed=completed), self.assertRaises(AssertionError):
                evaluate.grade_native_delegation("codex", calls, completed)

    def test_native_grader_requires_completion_of_the_spawned_codex_child(self) -> None:
        spawn = {"type": "item.completed", "item": {"type": "collab_tool_call",
            "tool": "spawn_agent", "status": "completed", "receiver_thread_ids": ["child-1"]}}
        call = {"fork_turns": "none", "reasoning_effort": "high"}
        for states, expected in [({}, False), ({"other-child": {"status": "completed"}}, False),
                                 ({"child-1": {"status": "running"}}, False),
                                 ({"child-1": {"status": "errored"}}, False),
                                 ({"child-1": {"status": "completed"}}, True)]:
            wait = {"type": "item.completed", "item": {"type": "collab_tool_call",
                "tool": "wait", "status": "completed", "agents_states": states}}
            events = "\n".join(map(json.dumps, [spawn, wait]))
            with self.subTest(states=states):
                self.assertTrue(evaluate.delegation_observed(events, "codex"))
                completed = evaluate.delegation_completed(events, "codex")
                self.assertEqual(completed, expected)
                if expected:
                    self.assertEqual(evaluate.grade_native_delegation("codex", [call], completed),
                                     "successful native delegation omitted a model override and requested high effort")
                else:
                    with self.assertRaisesRegex(AssertionError, "no completed native delegation"):
                        evaluate.grade_native_delegation("codex", [call], completed)
        self.assertFalse(evaluate.delegation_completed(json.dumps(spawn), "codex"))
        self.assertFalse(evaluate.delegation_completed("\n".join(map(json.dumps, [wait, spawn])), "codex"))
        for event_type, status in [("item.started", "in_progress"), ("item.completed", "in_progress")]:
            wait = {"type": event_type, "item": {"type": "collab_tool_call", "tool": "wait",
                "status": status, "agents_states": {"child-1": {"status": "completed"}}}}
            with self.subTest(event_type=event_type, status=status):
                self.assertFalse(evaluate.delegation_completed("\n".join(map(json.dumps, [spawn, wait])), "codex"))

    def test_native_case_rejects_launch_only_despite_parent_claim_of_completion(self) -> None:
        def prepare(project: Path, case: str, host: str) -> tuple[str, str]:
            project.mkdir()
            (project / "app.py").write_text("def normalize_tags(tags): return tags\n")
            return "delegate", ""

        for completed in [False, True]:
            events = [{"type": "item.completed", "item": {"type": "collab_tool_call", "tool": "spawn_agent",
                "status": "completed", "receiver_thread_ids": ["child-1"]}},
                {"type": "item.completed", "item": {"type": "agent_message",
                    "text": "The delegate completed reading app.py and returned normalize_tags."}}]
            if completed:
                events.append({"type": "item.completed", "item": {"type": "collab_tool_call", "tool": "wait",
                    "status": "completed", "agents_states": {"child-1": {"status": "completed"}}}})

            def launch(command: list[str], **kwargs: object) -> Mock:
                process = Mock(returncode=0)
                process.communicate.side_effect = lambda *args, **options: kwargs["stdout"].write("\n".join(map(json.dumps, events)))
                return process

            with self.subTest(completed=completed), tempfile.TemporaryDirectory() as temp:
                with patch.object(evaluate, "prepare", side_effect=prepare), \
                     patch.object(evaluate.subprocess, "Popen", side_effect=launch), \
                     patch.object(evaluate.subprocess, "run", return_value=Mock(stdout="", returncode=0)), \
                     patch.object(evaluate, "codex_spawn_receipts", return_value=[{"fork_turns": "none", "reasoning_effort": "high"}]):
                    record = evaluate.run_case("codex", "native-delegation", Path(temp), 10)
                self.assertEqual(record["delegation_event_observed"], True)
                self.assertEqual(record["native_completion_observed"], completed)
                self.assertEqual(record["pass"], completed)
                if not completed:
                    self.assertEqual(record["error"], "no completed native delegation observed")

    def test_claude_native_grader_requires_a_foreground_delegate_result(self) -> None:
        for background, result_id, is_error, expected in [(False, "delegate-1", False, True),
                (True, "delegate-1", False, False), (False, "other-tool", False, False),
                (False, "delegate-1", True, False)]:
            call = {"subagent_type": "pstack-effort-high", "run_in_background": background}
            events = "\n".join(map(json.dumps, [
                {"type": "assistant", "message": {"content": [{"type": "tool_use", "name": "Agent",
                    "id": "delegate-1", "input": call}]}},
                {"type": "user", "message": {"content": [{"type": "tool_result", "tool_use_id": result_id,
                    "is_error": is_error, "content": "normalize_tags"}]}}]))
            with self.subTest(background=background, result_id=result_id, is_error=is_error):
                completed = evaluate.delegation_completed(events, "claude-code")
                self.assertEqual(completed, expected)
                if expected:
                    self.assertEqual(evaluate.grade_native_delegation("claude-code", [call], completed),
                                     "successful native delegation omitted a model override and requested high effort")
                else:
                    with self.assertRaises(AssertionError):
                        evaluate.grade_native_delegation("claude-code", [call], completed)
        with self.assertRaisesRegex(AssertionError, "foreground"):
            evaluate.grade_native_delegation("claude-code", [{"subagent_type": "pstack-effort-high",
                "run_in_background": True}], True)

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
