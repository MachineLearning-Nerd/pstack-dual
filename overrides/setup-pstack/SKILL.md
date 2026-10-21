---
name: setup-pstack
description: Check pstack installation and configure role effort and panel size for Codex and Claude Code. Models always inherit the current chat. Use for setup-pstack or pstack configuration requests.
---

# Setup pstack

Read ../pstack-harness/SKILL.md. Resolve the installed skills root and the explicit
project destination. Run its bundled `pstack.py doctor --project <root>` to check
payloads, native agent files, config, and CLI versions. File readiness and live
agent loading are distinct: inspect the session's agent catalog before claiming
activation. Start a fresh session when agent definitions were newly installed.

Every role inherits the current chat's model. The user selects the model in the
chat; setup does not assign separate models to workers or reviewers. Two-arm
panels still run two independent agents, labeled independent same-model review.
Do not change host settings, credentials, global configuration, or permissions.

When the user wants effort or panel-size settings, create `.pstack-dual/models.json` in the
project with `pstack.py config-init --project <root>` if absent. Use user scope
only when requested. Show the resolved role choices before applying preference
changes; existing authorization can supply those choices. The schema and example
are in ../pstack-harness/references/models.md.

Use `inherit-parent` for all model fields. Existing valid configuration files
remain compatible: explicit legacy model choices are ignored and reported through
`ignored_model` in role resolution. Do not rewrite user configuration merely to
remove those choices. Effort and panel size remain configurable independently.

Validate with `pstack.py validate-config --file <path>` and resolve representative
code, judgment, and panel roles with `pstack.py resolve`; every arm must have
`model: null`. Unsupported per-agent
effort inherits and is reported. Configuration updates apply to the next resolved
delegation, not automatically to agents already running.

If the project has no behavioral verification path, offer once to create a
[verification skill](../create-verification-skill/SKILL.md). If it has no formal
verification skill, separately offer once to create a
[formal verification skill](../create-formal-verification-skill/SKILL.md).
Generate either only when accepted; declining does not block setup. For an
existing formal skill whose covered code changed after its sync commit, point
to [formal verification maintenance](../maintain-formal-verification-skill/SKILL.md).
These offers do not authorize installing verification tools or changing product code.
Report the actual checks, unresolved capabilities,
and how to invoke `$poteto-mode` in Codex or `/poteto-mode` in Claude.
