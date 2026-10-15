### Feature

You own the design. Delegate implementation while retaining the final decision.
Read pstack-harness for native mechanics and its
[effort contract](../../pstack-harness/SKILL.md#task-difficulty-and-effort).

1. Use how to establish the affected contracts, callers, and behavior.
2. Name the data shape and expected user-visible result. For a substantial
   feature, use architect to compare at least two designs before implementation.
   A mechanical one-file edit may skip the comparison with a stated reason.
3. Record a throughput checkpoint: blocking steps, independent work, shared state,
   and the smallest safe decomposition. Each irrelevant dimension gets a reason.
4. Give a bounded implementation worker explicit file scope and acceptance criteria.
   Resolve feature or hardest tasks as appropriate. Use independent worktrees for
   concurrent writers; serialize if isolation is unavailable. When a substantial
   implementation has multiple valid shapes, use arena for at least two candidates
   and independent cross-judging. Every candidate and judge inherits the current
   chat's model. Review actual candidate diffs and record the winning tradeoff.
   Report unavailable comparison or independent judging rather than claiming it ran.
5. Verify the feature through the product entry point and meaningful tests, including
   boundary inputs. Obtain an independent read-only review when available. Address
   supported findings, rerun affected checks, and report gaps honestly.
6. Apply deslop to the changed code and unslop to prose. Summarize the resulting
   behavior, design choice, verification, checkpoint, and open decisions. Commits,
   PRs, pushes, and shipping are separate scope choices, not automatic completion steps.
