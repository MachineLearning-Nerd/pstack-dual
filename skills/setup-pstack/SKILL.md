---
name: setup-pstack
description: Check pstack installation and configure project or user role models for Codex and Claude Code. Use for setup-pstack or requests to configure pstack models and budgets.
---


## Host compatibility

Read [pstack-harness](../pstack-harness/SKILL.md) before using this workflow.
Its native-tool, role-config, scope, and permission contract takes precedence over
backend-specific examples below. Read only the references needed for this task.

# Setup pstack

Read ../pstack-harness/SKILL.md. Resolve the installed skills root and the explicit
project destination. Run its bundled `pstack.py doctor --project <root>` to check
payloads, native agent files, config, and CLI versions. File readiness and live
agent loading are distinct: inspect the session's agent catalog before claiming
activation. Start a fresh session when agent definitions were newly installed.

Default role models and efforts inherit the session. Two-arm panels still run
two independent agents, labeled same-model unless the actual models differ.
Do not change host settings, credentials, global configuration, or permissions.

When the user wants model overrides, create `.pstack-dual/models.json` in the
project with `pstack.py config-init --project <root>` if absent. Use user scope
only when requested. Show the resolved role choices before applying preference
changes; existing authorization can supply those choices. The schema and example
are in ../pstack-harness/references/models.md.

Confirm model availability from the live host catalog; Codex also exposes
`codex debug models`. Claude's supported aliases include sonnet, opus, haiku,
and inherit-parent, but account access is established only by actual execution.
Keep model and effort as separate fields. Never translate a Cursor slug by
guessing or send a Claude model to Codex. A rejected choice inherits only with
explicitly reported substitution; do not claim the requested model ran.

Validate with `pstack.py validate-config --file <path>` and resolve representative
code, judgment, and panel roles with `pstack.py resolve`. Unsupported per-agent
effort inherits and is reported. Configuration updates apply to the next resolved
delegation, not automatically to agents already running.

If the project has no behavioral verification path, use create-verification-skill
when appropriate to the task. Report the actual checks, unresolved capabilities,
and how to invoke `$poteto-mode` in Codex or `/poteto-mode` in Claude.
