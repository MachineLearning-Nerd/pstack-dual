---
name: weed
description: "Find the patterns agents copy in a codebase, collapse each to one API, delete the rest, and lock it in with a lint rule whose message names the fix. Use for /weed, 'weed this repo', or a correction that should become a deterministic check."
disable-model-invocation: true
---


## Host compatibility

Read [pstack-harness](../pstack-harness/SKILL.md) before using this workflow.
Its native-tool, role-config, scope, and permission contract takes precedence over
backend-specific examples below. Every delegate inherits the current chat's model;
never pass a model override, including when an imported example requests one.
Read only the references needed for this task.

# Weed

Agents copy the nearest example. A workaround, escape hatch, or second way to
do something becomes the pattern the next agent follows. Weed removes those
patterns and turns each removal into a check the codebase enforces, per the
**encode-lessons-in-structure** principle skill. The check is the record: no
new docs, comments, or rules files.

Two modes:

- **Audit**: `/weed` or `/weed <path>`. Find, rank, and fix the top patterns.
- **Correction**: `/weed "<what the agent got wrong>"`. Skip to Phase D with
  that one pattern.

Add "audit only" to stop after Phase C with the ranked report.

Open a todolist with one entry per phase before starting: Ground, Audit, Rank,
Choose, Migrate, Enforce, Prove, Report.

## Phase A: Ground

1. Detect each stack from its marker files using
   [references/stacks.md](references/stacks.md). A repo can hold several.
2. Record the lint, type-check, and test commands the repo already runs, from
   its scripts, CI config, and AGENTS.md. Run the lint command once and record
   the baseline result.
3. Run the **how** skill on the top-level layout so the audit knows which
   directories are product code, framework code, generated code, and tests.

## Phase B: Audit

Read [references/audit.md](references/audit.md) for the categories and
evidence rules. In a repo too large to read in one context, run the **swarm**
skill with a partition by top-level directory. Resolve `swarm workers`
through pstack-harness. Workers are read-only and return candidates in the
shape audit.md defines. Otherwise audit inline.

Skip generated, vendored, and fixture code. A candidate needs `file:line`
evidence for at least two occurrences, or one occurrence of a nuanced
primitive in product code.

## Phase C: Rank

Score each candidate:

```
score = occurrences × spreading × harm
spreading = 2 if a new occurrence landed in the last 90 days, else 1
harm      = 2 if it caused a bug, perf issue, or revert you can cite, else 1
```

Check spreading with `git log -S '<pattern>' --since=90.days --oneline`.
Take the top three unless the user named a number. List the rest in the
report as remaining, so the next run starts there.

## Phase D: Choose one way

For each selected pattern, name the single correct way:

1. If the codebase already has a good API for it, choose that.
2. If none exists, or the right API crosses a function boundary, run the
   **architect** skill to design it. Nuanced primitives go behind a framework
   API and become banned in product code.
3. If the right answer needs judgment no rule can express, say so. Per
   **encode-lessons-in-structure**, make the instruction prominent with an
   example of the failure, and do not write a rule that would fire on correct
   code.

## Phase E: Migrate and delete

Migrate every caller to the chosen way, then delete the legacy path, per the
**migrate-callers-then-delete-legacy-apis** principle skill. Fix the root cause
at each site rather than rewrapping the workaround, per **fix-root-causes**.

Delegate one implementation agent per pattern with the `refactoring` role.
Concurrent writers each get their own git worktree, per pstack-harness. Review
each returned diff before applying it. Run the recorded type-check and tests
after each pattern lands.

## Phase F: Enforce

Add the rule in the config the repo already uses for that stack. Choose the
tool from [references/stacks.md](references/stacks.md). The rule message
must name the replacement and the reason in one sentence. A message that only
says "don't" sends the agent looking for a workaround.

Prefer the narrowest rule that catches the pattern. Scope boundary rules to the
directories they protect. Exempt the one place that implements the wrapper.

Adding a lint tool the repo does not have is a new dependency. Report the
proposed tool and wait for the user before installing it. The universal grep
check in stacks.md needs no dependency and covers the gap.

## Phase G: Prove

Per the **prove-it-works** principle skill, a rule that never fires is prose.

1. Write a probe file in a path the rule covers, containing one old occurrence.
2. Run the lint command on it. It must fail, and the output must contain the
   rule's message.
3. Delete the probe. Run the full lint command. It must match the Phase A
   baseline or improve on it.

Record the probe path, the command, and the failing output. A rule that does
not fire goes back to Phase F.

## Report

One table: pattern, occurrences before and after, chosen way, rule location,
proof result. Then remaining candidates, any judgment-only patterns, and any
tool the user needs to approve.

Do not commit, push, or open a PR unless the user asked for it.
