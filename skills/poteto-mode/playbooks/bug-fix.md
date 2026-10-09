### Bug fix

You own the task. Delegate bounded implementation and review; keep the evidence
and the final decision in the lead. Read pstack-harness for native mechanics.

1. Reproduce through the real entry point. Capture the failing behavior, input,
   and expected result. A missing target is unresolved, not a successful repro.
2. Trace the mechanism through source, callers, and runtime evidence. Use how;
   use why for history when available. Remove hypotheses refuted by evidence.
3. Plan the smallest justified fix. Name the affected data shape. Use architect
   when a boundary or design choice materially affects correctness. Delegate one
   implementation worker on the resolved bug-fix role when available; it writes
   in an isolated worktree, or serially in this checkout if isolation fails.
4. Add a cheap behavioral regression test when it earns its place, proving it
   fails before the fix. Re-run the original entry-point reproduction afterward.
5. Inspect the actual diff and obtain a fresh independent read-only review when
   available. Apply evidence-backed fixes and repeat affected checks. Report any
   missing independent verification honestly. Apply deslop and no-comments to
   changed code when they expose unnecessary complexity; preserve useful contracts.
6. Report root cause, fix, actual failing/passing outputs, review, and limitations.
   Commit, open a PR, or publish only when within the user's requested scope.
