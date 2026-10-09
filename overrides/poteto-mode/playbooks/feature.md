### Feature

You own the design. Delegate implementation while retaining the final decision.
Read pstack-harness for native mechanics.

1. Use how to establish the affected contracts, callers, and behavior.
2. Name the data shape and expected user-visible result. Use architect for real
   competing designs; do not manufacture an arena for a mechanical one-file edit.
3. Record a throughput checkpoint: blocking steps, independent work, shared state,
   and the smallest safe decomposition. Each irrelevant dimension gets a reason.
4. Give a bounded implementation worker explicit file scope and acceptance criteria.
   Resolve feature or hardest tasks as appropriate. Use independent worktrees for
   concurrent writers; serialize if isolation is unavailable. Review its actual diff.
5. Verify the feature through the product entry point and meaningful tests, including
   boundary inputs. Obtain an independent read-only review when available. Address
   supported findings, rerun affected checks, and report gaps honestly.
6. Apply deslop to the changed code and unslop to prose. Summarize the resulting
   behavior, design choice, verification, checkpoint, and open decisions. Commits,
   PRs, pushes, and shipping are separate scope choices, not automatic completion steps.
