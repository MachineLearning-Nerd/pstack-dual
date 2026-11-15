---
name: how
description: Explain a subsystem's behavior from source, callers, data structures, and runtime evidence. Use for how questions or understanding code before a change.
disable-model-invocation: true
---

# How

Read ../pstack-harness/SKILL.md. Remain read-only when answering an investigation.
If the scope is ambiguous, state your interpretation and explore. The user can
redirect.

## 1. Explain

Answer a narrow question about one function or file directly, citing the source.
Otherwise spawn one fresh read-only agent that explores and explains in one pass.
It inherits the current chat's model; resolve `judgment and prose` for its effort
under [the effort contract](../pstack-harness/SKILL.md#task-difficulty-and-effort).
Give it the user's question and this brief:

> You are writing an architectural explanation for a senior engineer. Explore the
> codebase and write an explanation that a senior engineer unfamiliar with this
> area could read and walk away with a solid mental model. They should understand
> the architecture well enough to start working in it confidently. Cite actual
> files and symbols, and separate what you observed running from what you inferred
> from source. You have read-only access to the codebase.

Brief it with the question, not a presumed answer. If delegation is unavailable,
say so and answer from the evidence you gathered yourself. Never claim a
delegation or runtime check that did not run.

## 2. Present

Present the agent's output. Light edits for clarity or context from the
conversation are fine. Do not substantially rewrite it. Name any missing evidence.
For intent or history, route to why only when that evidence can answer the
question. Apply unslop to the reply. In an investigation, do not create a PR, edit
the code, or trigger implementation merely because a design question arose.
