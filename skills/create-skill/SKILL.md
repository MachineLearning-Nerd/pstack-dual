---
name: create-skill
description: Author or update a portable pstack skill with precise triggers, self-contained resources, and realistic behavioral verification.
---


## Host compatibility

Read [pstack-harness](../pstack-harness/SKILL.md) before using this workflow.
Its native-tool, role-config, scope, and permission contract takes precedence over
backend-specific examples below. Every delegate inherits the current chat's model;
never pass a model override, including when an imported example requests one.
Read only the references needed for this task.

# Author a portable skill

Use an existing skill when it already owns the task. Put a new project skill in
`.agents/skills/<lowercase-hyphenated-name>/SKILL.md`; for Claude discovery also
link it from `.claude/skills/` if the project uses standalone skills. Include name
and a concise description in YAML frontmatter. Keep essential decisions in the
entry point and substantial conditional details in linked references.

Preserve user intent and permissions. Do not make external integrations mandatory
when local resources suffice. Give example requests and check the workflow against
a realistic input and its observable outcome, not a wording snapshot. New scripts
must be run. Read pstack-harness when host capabilities affect the skill.
