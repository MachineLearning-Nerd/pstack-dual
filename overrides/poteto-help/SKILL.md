---
name: poteto-help
description: Explain how to install, configure, or choose a pstack workflow in Claude Code and Codex. Use for explicit pstack help questions.
disable-model-invocation: true
---

# Pstack help

For setup and host capabilities read setup-pstack and pstack-harness. For ordinary
engineering work invoke poteto-mode, which selects a playbook. Use `$poteto-mode`
in Codex and `/poteto-mode` in standalone Claude installs. Re-invoke at a new task
or after a handoff; Cursor's persistent custom-mode controls do not apply here.

For a recap of the current chat, use [ketchup](../ketchup/SKILL.md). It explains
what happened since the user's last message and decisions still waiting on them.
It gives a short plain-language summary and small visuals when they explain a change.
For context across previous chats, use [recall](../recall/SKILL.md). These are
different scopes. Ketchup stays read-only and follows [bro](../bro/SKILL.md) for
plain language. Use `$ketchup` in Codex or `/ketchup` in Claude.

Use [in-your-own-words](../in-your-own-words/SKILL.md) to restate the user's goals
before acting. Use [sharpen](../sharpen/SKILL.md) to improve the task's framing,
choose expert methods and an outside check, then do the work. Sharpen does not
return a rewritten prompt or decide preferences that belong to the user.

Core supported workflows are investigation (how), bug fix, feature, and read-only
code review (pstack-review/interrogate). Principles and local verification skills
are preserved from upstream. Advanced orchestration, transcript mining, bot UI,
and overnight workflows are retained as an experimental library; inspect the
host contract and prerequisites before using them. No automation is installed.

The portable package bundles deslop, control-cli, control-ui, and create-skill.
Every delegate inherits the current chat's model, including two-arm panels.
Setup configures efforts and panel size; legacy model choices are reported as
ignored. Native agents or processes using the verified parent model must perform
independent review. Panels are labeled independent same-model review.

Answer from the relevant skill's actual instructions. Give a short task-specific
prompt and cite the installed file. Do not claim installation, native agent
activation, model diversity, or verification that has not been observed.
Read sibling skill descriptions to route questions beyond the core workflows.
