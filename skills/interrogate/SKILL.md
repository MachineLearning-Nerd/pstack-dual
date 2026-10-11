---
name: interrogate
description: Challenge a code change with independent adversarial reviewers and consolidate evidence-backed findings. Use for interrogate or adversarial review.
disable-model-invocation: true
---


## Host compatibility

Read [pstack-harness](../pstack-harness/SKILL.md) before using this workflow.
Its native-tool, role-config, scope, and permission contract takes precedence over
backend-specific examples below. Every delegate inherits the current chat's model;
never pass a model override, including when an imported example requests one.
Read only the references needed for this task.

# Interrogate

Read ../pstack-harness/SKILL.md. Identify the exact diff, base, and review scope.
State the change's intent from the user's request, commit messages, PR description,
and code. If intent remains uncertain after inspection, ask the user.

Read references/reviewer-prompt.md, references/rubric.md, and
references/code-quality-review.md. Fill the same reviewer template for every arm
with the intent, scoped artifact, rubric, and code-quality lens. Review relevant
lenses without forcing those that do not apply.

Resolve `interrogate reviewers` and spawn one independent read-only reviewer per
arm. Omit model overrides and use only supported effort fields. Do not supply
the lead's suspected findings as the answer. A same-model panel is independent review, not
model diversity. Reviewers cite files, triggers, impact, and evidence.

Wait for all arms or report the failed/missing arms explicitly. Confirm findings
against the artifact, deduplicate, and report disagreement. Do not count inline
self-review as an independent verdict. Read references/lead-judgment.md and put
each finding in Act on, Consider, Noted, or Dismissed, with the reviewers that
raised it and a reason. Give the intent, each reviewer's actual identity and
finding count, and an agreement map. Report agreement among independent instances
of the same model. This panel does not test agreement across models. Editing
requires an implementation request separate from the review itself.
