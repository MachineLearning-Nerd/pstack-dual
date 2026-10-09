---
name: principle-redesign-from-first-principles
description: "Apply when integrating a new requirement into an existing design. Redesign as if the requirement had been a foundational assumption from day one, instead of bolting it on."
disable-model-invocation: true
---


## Host compatibility

Read [pstack-harness](../pstack-harness/SKILL.md) before using this workflow.
Its native-tool, role-config, scope, and permission contract takes precedence over
backend-specific examples below. Read only the references needed for this task.

# Redesign From First Principles

When integrating a change, don't bolt it onto the existing design. Redesign as if the requirement had been there from the start.

- Read all affected files and understand the current design
- Ask: "if we were writing this from scratch with this new requirement, what would we build?"
- Propagate the change through every reference: types, docs, examples, rationale sections
- Think about the whole redesign, then deliver it incrementally

This is the method for preserving option value when integrating changes into an existing design.
