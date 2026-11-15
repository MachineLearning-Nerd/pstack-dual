---
name: interrogate
description: Challenge a code change or design with independent adversaries and keep only findings a rerun proves. Use for interrogate or adversarial review.
disable-model-invocation: true
---

# Interrogate

Read ../pstack-harness/SKILL.md. Adversaries try to break a change or a design.
A finding survives only when a run proves it. Report the findings. Editing
requires an implementation request separate from the review itself.

## Frame

The scope is what the user names. Otherwise it is the branch diff from its merge
base with the base branch, through the working tree. State the intent with the
[in-your-own-words](../in-your-own-words/SKILL.md) skill, from the user's message,
the commits, and the PR description. Ask the user when the intent is unclear.

## Fan out

Run Phase A steps 3 and 4 and Phase B of the [arena](../arena/SKILL.md) skill,
with these changes. Resolve `interrogate reviewers` in place of `arena runners`;
spawn one independent adversary per resolved arm. Every adversary inherits the
current chat's model; omit model overrides. Assess each brief under
[the effort contract](../pstack-harness/SKILL.md#task-difficulty-and-effort).
Give each adversary its own git worktree and copy the scope's uncommitted changes
into it. If isolation is unavailable, run the adversaries one at a time and
restore the checkout between them. Do not supply the lead's suspected findings.
In place of the arena task and rationale, give each adversary the scope, the
intent, and this brief:

> Break this change. Prove each finding with a run against the real code, such as
> a failing test, a repro script, or command output that shows the wrong behavior.
> For a design or plan, run a prototype or probe the current tree. Keep repros in
> your own worktree and do not edit the lead's checkout. Report each finding with
> a title, the exact command, the output it printed, and the output the intent
> requires. Leave out anything you did not run. That covers style, naming,
> structure, and risks that need a future change to matter. No findings is a
> valid result.

## Verify

Verify each finding per arena Phase F by rerunning its command yourself. Keep a
finding when the output shows the failure and the failure breaks the intent. Drop
the rest. Merge findings that share a root cause. Inline self-review is not an
independent verdict; wait for every arm or report the failed or missing arms.

Skip arena Phases C, D, and E. Adversaries find different failures, so the verdict
keeps every verified finding, not one adversary's list.

## Output

- **Intent**: the restatement.
- **Adversaries**: each arm's identity and effort, labeled independent same-model
  review. This panel does not test agreement across models.
- **Findings**: for each verified finding, the command, its output, how it breaks
  the intent, and the adversaries that found it. Say "no verified findings" when
  none survive.
- **Dropped**: for each adversary, the count of dropped findings and why.
