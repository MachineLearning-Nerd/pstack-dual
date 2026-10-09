---
name: how
description: Explain a subsystem's behavior from source, callers, data structures, and runtime evidence. Use for how questions or understanding code before a change.
disable-model-invocation: true
---


## Host compatibility

Read [pstack-harness](../pstack-harness/SKILL.md) before using this workflow.
Its native-tool, role-config, scope, and permission contract takes precedence over
backend-specific examples below. Read only the references needed for this task.

# How

Read ../pstack-harness/SKILL.md. Remain read-only when answering an investigation.
Find the relevant entry point, callers, authoritative types, and the smallest set
of files that establish behavior. Do not dump the whole repository into context.

Delegate independent exploration slices when scope warrants it. Resolve `how
explorer` for source discovery and `how explainer` for synthesis. A small subsystem
may use one explorer; a direct one-file question can be answered inline with
evidence. Brief the explorer with the question and file pointers, not a presumed
answer. Never fabricate delegation or runtime checks.

Explain Overview, Key Concepts, How It Works, Where Things Live, and Gotchas at
the depth the question needs. Cite actual files and symbols. Distinguish observed
runtime results from source inference, and identify missing evidence. For intent
or history, route to why only when that evidence can answer the question.

Apply unslop to the reply. In an investigation, do not create a PR, edit the code,
or trigger implementation merely because a design question arose.
