---
name: interrogate
description: Challenge a code change with independent adversarial reviewers and consolidate evidence-backed findings. Use for interrogate or adversarial review.
disable-model-invocation: true
---


## Host compatibility

Read [pstack-harness](../pstack-harness/SKILL.md) before using this workflow.
Its native-tool, role-config, scope, and permission contract takes precedence over
backend-specific examples below. Read only the references needed for this task.

# Interrogate

Read ../pstack-harness/SKILL.md. Identify the exact diff, base, and review scope.
Read references/reviewer-prompt.md if present; otherwise give each reviewer the
same rubric: reachable defects, contract mismatches, failure and concurrency
paths, missing behavioral verification, and unnecessary complexity in the change.

Resolve `interrogate reviewers` and spawn one independent read-only reviewer per
arm. Use only actual supported model and effort fields. Do not supply the lead's
suspected findings as the answer. A same-model panel is independent review, not
model diversity. Reviewers cite files, triggers, impact, and evidence.

Wait for all arms or report the failed/missing arms explicitly. Confirm findings
against the artifact, deduplicate, and report disagreement. Do not count inline
self-review as an independent verdict. Produce a concise prioritized review;
editing requires an implementation request separate from the review itself.
