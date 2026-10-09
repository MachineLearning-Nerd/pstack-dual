---
name: pstack-review
description: Review a branch, working diff, or named files for reachable defects and missing behavioral coverage. Produces a read-only review with evidence.
---


## Host compatibility

Read [pstack-harness](../pstack-harness/SKILL.md) before using this workflow.
Its native-tool, role-config, scope, and permission contract takes precedence over
backend-specific examples below. Read only the references needed for this task.

# Code review

Read ../pstack-harness/SKILL.md and ../interrogate/SKILL.md. Establish the exact
artifact and base before reviewing. For a working tree, include tracked and
untracked files relevant to the request. Identify changed contracts and callers.
Do not checkout, stage, fix, commit, or publish anything in a review request.

Use independent reviewers when available, one bounded review per configured
`interrogate reviewers` arm. Every arm receives the same artifact and scope, with
its own context. State whether the actual panel is same-model or diverse-model.
Consolidate findings, confirm reachable behavior against source or a safe repro,
and reject speculation. A command failure or missing tool is not a clean verdict.

Lead with concrete defects in priority order, citing files and symbols, the
trigger, impact, and missing test. Note disagreements and remaining uncertainty.
If no supported finding remains, say so and identify material coverage limits.
