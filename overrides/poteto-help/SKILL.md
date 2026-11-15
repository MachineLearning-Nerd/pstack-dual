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
It keeps the progress summary short and lists every waiting item with its effect,
evidence, risk and recommendation. It never omits items to meet a word limit.
Small visuals are included when they explain a change.
For context across previous chats, use [recall](../recall/SKILL.md). These are
different scopes. Ketchup stays read-only and follows [bro](../bro/SKILL.md) for
plain language. Use `$ketchup` in Codex or `/ketchup` in Claude.
Use [ketchup-video](../ketchup-video/SKILL.md) for the same catch-up as a short
subtitled slide video, with every waiting decision in text below it. Rendering
requires local video tools and a host that can present the resulting file.

Use [in-your-own-words](../in-your-own-words/SKILL.md) to restate the user's goals
before acting. Use [sharpen](../sharpen/SKILL.md) to rewrite a prompt with expert
methods, primary material and an outside correctness check. It returns only the
rewritten prompt and does not execute the task or decide the user's preferences.

Use [create-formal-verification-skill](../create-formal-verification-skill/SKILL.md)
for a race, invariant or other property tests rarely reach. It creates a local
check with explicit bounds, code links and a demonstrated failing variant. Use
[maintain-formal-verification-skill](../maintain-formal-verification-skill/SKILL.md)
when covered code changes after its recorded sync commit. A passing stale model
does not prove current code correct. Formal verification tools are not bundled.
Use [statechart](../statechart/SKILL.md) to check a TLA+ model and show what the
user sees as a Mermaid chart, with the shortest path to each state that breaks a
rule. Its TypeScript launcher is bundled and needs Node 22.18+, Bun 1.1.5+, or
Deno 2.0+. TLC and Java are separate runtime tools.

Use [weed](../weed/SKILL.md) to find patterns agents copy, such as duplicates,
escape hatches, and quick-fix patches. It migrates callers to one way, deletes
the rest, and adds a lint rule whose message names the fix, then proves the rule
fires. Use `/weed "<correction>"` to turn one correction into a rule.

Core supported workflows are investigation (how), bug fix, feature, and read-only
code review (pstack-review/interrogate). Interrogate keeps only findings an
adversary proved with a run and the lead reproduced. Why answers from the commits
and PR discussion behind the code and says what the record does not answer.
Principles and local verification skills are preserved from upstream. Advanced orchestration, transcript mining, bot UI,
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
