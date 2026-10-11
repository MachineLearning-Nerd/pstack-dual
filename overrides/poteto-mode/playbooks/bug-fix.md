### Bug fix

You own the task. Delegate bounded implementation and review; keep the evidence
and the final decision in the lead. Read pstack-harness for native mechanics.

1. Reproduce through the real entry point. Capture the failing behavior, input,
   and expected result. A missing target is unresolved, not a successful repro.
2. Trace the mechanism through source, callers, and runtime evidence. Use how;
   use why for history when available. Partition plausible causes into testable
   hypotheses and eliminate them systematically. Instrument the relevant values
   at runtime to prove the cause; source inference alone does not prove a runtime
   defect. Revert experimental changes for disproved hypotheses. If reproduction
   is unavailable, report the cause as unconfirmed and name the missing evidence.
3. Plan the smallest justified fix. Name the affected data shape. Use architect
   when the fix crosses a function boundary. Every designer and worker inherits
   the current chat's model. Delegate one
   implementation worker on the resolved bug-fix role when available; it writes
   in an isolated worktree, or serially in this checkout if isolation fails.
   Use a native investigation loop only when available; otherwise continue the
   hypothesis and verification cycle directly without claiming a host loop ran.
4. Add a cheap behavioral regression test when it earns its place, proving it
   fails before the fix. Re-run the original entry-point reproduction afterward.
5. Inspect the actual diff and obtain a fresh independent read-only review when
   available. Apply evidence-backed fixes and repeat affected checks. Report any
   missing independent verification honestly. Apply deslop and no-comments to
   changed code when they expose unnecessary complexity; preserve useful contracts.
6. Report root cause, fix, actual failing/passing outputs, review, and limitations.
   Commit, open a PR, or publish only when within the user's requested scope.
