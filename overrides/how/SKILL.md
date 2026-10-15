---
name: how
description: Explain a subsystem's behavior from source, callers, data structures, and runtime evidence. Use for how questions or understanding code before a change.
disable-model-invocation: true
---

# How

Read ../pstack-harness/SKILL.md. Remain read-only when answering an investigation.
Find the relevant entry point, callers, authoritative types, and the smallest set
of files that establish behavior. Do not dump the whole repository into context.

Answer narrow questions about one function or file directly with evidence.
For a substantial single-module explanation, delegate a fresh read-only explainer
using references/explainer-prompt.md without its explorer-findings section.
Replace its synthesis premise with an instruction to explore the source and
explain it in one pass; remove statements that prior explorers did the research.
For work spanning subsystems, delegate two
to four read-only explorers using references/explorer-prompt.md, with distinct
questions and file pointers. Resolve `how explorer` for discovery and `how
explainer` for synthesis. Every delegate inherits the current chat's model.
Assess each brief under [the effort contract](../pstack-harness/SKILL.md#task-difficulty-and-effort).

Give a fresh explainer the explorer findings and original question. The explainer
owns the final explanation; the lead makes only light factual or clarity edits.
Brief researchers with questions, not presumed answers. If delegation is
unavailable, explain the missing independent research or synthesis and answer
from the evidence available. Never fabricate delegation or runtime checks.

Explain Overview, Key Concepts, How It Works, Where Things Live, and Gotchas at
the depth the question needs. Cite actual files and symbols. Distinguish observed
runtime results from source inference, and identify missing evidence. For intent
or history, route to why only when that evidence can answer the question.

Apply unslop to the reply. In an investigation, do not create a PR, edit the code,
or trigger implementation merely because a design question arose.
