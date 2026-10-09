---
name: poteto-help
description: Explain how to install, configure, or choose a pstack workflow in Claude Code and Codex. Use for explicit pstack help questions.
disable-model-invocation: true
---


## Host compatibility

Read [pstack-harness](../pstack-harness/SKILL.md) before using this workflow.
Its native-tool, role-config, scope, and permission contract takes precedence over
backend-specific examples below. Read only the references needed for this task.

# Pstack help

For setup and host capabilities read setup-pstack and pstack-harness. For ordinary
engineering work invoke poteto-mode, which selects a playbook. Use `$poteto-mode`
in Codex and `/poteto-mode` in standalone Claude installs. Re-invoke at a new task
or after a handoff; Cursor's persistent custom-mode controls do not apply here.

Core supported workflows are investigation (how), bug fix, feature, and read-only
code review (pstack-review/interrogate). Principles and local verification skills
are preserved from upstream. Advanced orchestration, transcript mining, bot UI,
and overnight workflows are retained as an experimental library; inspect the
host contract and prerequisites before using them. No automation is installed.

The portable package bundles deslop, control-cli, control-ui, and create-skill.
Models default to session inheritance, including two-arm panels. Setup can
configure actual available models and efforts. Separate processes or native agents
must perform independent review; same-model panels are labeled honestly.

Answer from the relevant skill's actual instructions. Give a short task-specific
prompt and cite the installed file. Do not claim installation, native agent
activation, model diversity, or verification that has not been observed.
