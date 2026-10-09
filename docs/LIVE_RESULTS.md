# Live evaluation results

Actual CLI runs; no simulated agent results.

| Host | Case | Result | Seconds | Native delegation observed |
| --- | --- | --- | --- | --- |
| claude-code | bug-fix | PASS | 74.4 | True |
| codex | bug-fix | PASS | 164.6 | True |
| claude-code | feature | PASS | 63.7 | True |
| codex | feature | PASS | 187.7 | True |
| claude-code | investigation | PASS | 28.2 | False |
| codex | investigation | PASS | 50.3 | False |
| claude-code | native-delegation | PASS | 28.1 | True |
| codex | native-delegation | PASS | 84.2 | True |
| claude-code | review | PASS | 58.9 | True |
| codex | review | PASS | 88.2 | True |

Missing core cases: none.

Investigation and review graders assert project files remain unchanged. Bug/feature
graders independently exercise CLI edge cases and existing behavior. The native-delegation
case checks explicit model/effort arguments and the returned source symbol.

Native observation comes from Claude tool events or the exact evaluation parent's
Codex rollout. It establishes a recorded delegation attempt; parent reports and
application checks supply completion evidence. No unrelated session messages are read.

Local logs are ignored by Git; evals/latest.json retains the nonsecret grader receipts.
Codex 0.162.0 ephemeral sessions failed full-context delegation during the initial
run. The final tests use normal sessions, and the adapter handles rejected spawns.
This Codex tool catalog did not expose agent_type, so the native spawns received
persona briefings. Claude's native pstack-reviewer and pstack-effort-high loaded.
These cases do not establish advanced cloud/overnight workflow coverage.
