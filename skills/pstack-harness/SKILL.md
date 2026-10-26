---
name: pstack-harness
description: Adapt pstack delegation, role configuration, skill paths, verification, and session handling to Claude Code or Codex. Read when a pstack workflow delegates or uses a host-specific capability.
---


# Native harness contract

This file is the authority for host mechanics in this derivative. Upstream
examples describe intent; do not call a tool or use a model just because an example
names it. Inspect the live tools. User instructions and actual permissions govern
scope, including external messages, commits, pushes, merges, and deployments.

Resolve `PSTACK_SKILLS_ROOT` to the absolute logical directory containing this
skill and its siblings. Follow installed symlinks when needed. Resolve the project
root separately; never assume the source checkout is the consumer project.
Read sibling skills and their references directly, even if they are absent from
the host's skill selector. Do not read the entire suite for one task.

## Roles and models

Resolve each role before delegation with the bundled command:

```sh
python3 "$PSTACK_SKILLS_ROOT/pstack-harness/scripts/pstack.py" resolve --host codex --project "$PROJECT_ROOT" --role "bug-fix"
```

Use `claude-code` for Claude. The result lists arms with `model` and `effort`;
null means inherit. Every delegate uses the current chat's model. Never pass a
model override, choose a different role model, or change models after a rejected
spawn. This policy supersedes model-selection examples in imported workflows.
The user controls the model by selecting it in the chat.

Project `.pstack-dual/models.json` overrides user settings for effort and panel
size. Legacy explicit model settings remain readable but are ignored; the
resolver reports them as `ignored_model`. Preserve separate panel arms and label
them independent same-model review. Different efforts do not establish model
diversity. Do not claim cross-provider execution.

## Task difficulty and effort

Before each spawn, assess the task's difficulty, subtlety, and urgency. Select the
role that describes the work, then resolve its configured effort. Use that exact
effort only if the live host supports it for the current chat's model. A null
effort inherits the parent. Assessment informs the brief, scope, and verification;
it does not authorize raising or lowering configured effort, choosing another
role to obtain a different effort, or changing the user's settings.

Do not encode effort or fast mode in a model slug. Do not guess another effort
after a rejected spawn. If the host cannot honor an effort, inherit and report
the requested and inherited result. If speed controls are unavailable, report
that limitation when relevant; do not substitute another model or CLI default.
Verification workers follow the same configured-effort contract.

## Claude Code

Use the live Agent/delegation tool (older releases call it Task). Omit its `model`
argument so the delegate inherits the chat. Use `poteto-agent` when loaded for implementation;
otherwise brief a general-purpose agent to read poteto-mode and the matched
playbook at their absolute paths. For read-only reviews, use `pstack-reviewer`
when loaded; it has read-only tools. Resolve names from the live agent catalog.
A written effort uses `pstack-effort-<level>` only if that agent is loaded; give
it the complete persona brief and report any inherited effort otherwise.
Use the host's supported background/wait mechanisms. Do not invent fields.

## Codex

Use native `spawn_agent` when available and omit `model`. Set `fork_turns: "none"`
when setting `reasoning_effort`; a full-history fork inherits the parent's identity.
Pass the resolved effort only when supported without changing the model. Set the custom agent type when the
live tool exposes it; otherwise include the persona and absolute skill paths in
the brief. Use the host's message, wait, and close capabilities as exposed.
For a read-only reviewer, select `pstack-reviewer` if loaded and always state the
read-only scope. Its installed TOML requests a read-only sandbox; when the live
tool cannot select it, the brief is an instruction, not an enforced sandbox.
For full-history inheritance, the host may need a persisted parent session. Codex
0.162.0's ephemeral mode can reject spawning with "no rollout found". Treat a
failed spawn as failed: it creates no live worker. Do not wait on missing IDs or
report that a worker is implementing. Retry once with a fresh-context native
spawn when supported; otherwise use the bounded separate-process fallback.

## Isolation and fallbacks

Native subagents are preferred. If unavailable, a separate `codex exec` or
`claude -p` process may implement a bounded brief only when the actual parent
model identity is known and can be selected unchanged, with the same permission
scope. A CLI default or guessed model is insufficient. If that identity cannot
be established, report unavailable delegation and continue inline within scope.
Do not bypass permission checks to make it work. Report unavailable independent
verification if neither mechanism works; inline self-review is not independent.
Each concurrent writer gets its own git worktree. Record its path and base commit.
Review the returned diff before cherry-picking or applying it in the lead checkout.
When isolation cannot be created, use one writer at a time in the current checkout.
Use local workers in place of cloud workers; cloud-only launch fields do not apply.
Delegate bounded tasks and return file references, evidence, and a thin report.

## Tasks, sessions, and verification

Use a native task/plan tracker when available; otherwise maintain a concise worklist
in progress messages. No host config changes are needed just to obtain a tracker.
Explicitly invoke poteto-mode at the start of a new task; Cursor's custom-mode
frontmatter and reminder mechanism have no portable persistence guarantee.
Re-read the mode and active playbook after context compaction or a session handoff.
Use a host loop only if it exists, and otherwise state that re-invocation is manual.
Do not start timers or unattended publishing just because a playbook mentions them.

For transcripts, use the current session's known path first. Claude's project
store is under `~/.claude/projects/`; Codex's store is under `$CODEX_HOME/sessions`
or `~/.codex/sessions`. For Codex, select records whose session metadata `cwd`
belongs to this project before reading messages. Claude workspace encoding can
vary by release: verify the directory's recorded workspace. Never bulk-read
other projects' messages. If session access is unavailable, use the current
conversation and say which evidence is missing.

Drive the product's actual entry point. Reuse a project verification skill or the
bundled control-cli/control-ui skills, and capture before/after evidence. A green
test that did not run assertions is not proof. Read-only investigation and review
may run safe commands but must not edit project files. Preserve explicit scope;
the skill's autonomy language never grants external actions on its own.

## Skill changes and optional runtimes

Before applying an approved reflection edit, identify the skill's actual source
and show the destination. Never edit a plugin cache, `.pstack-dual/bundle`, or a
managed skill symlink. A path under `.agents/skills` or `.claude/skills` may point
into that managed bundle. Editing through the link edits the bundle too.
For this derivative, change `overrides/` or `tools/build.py` in its source checkout
and regenerate, rather than editing generated `skills/`. For an independent
skill copy, choose an unmanaged project or user skill directory and preserve
existing managed links and unrelated skills. Reflection still requires approval
of the accepted edits and does not open a PR or push.

The `statechart` skill bundles Node scripts, not TLC, Java, or the PNG renderer.
Its model commands can install TLC and Java with mise, and PNG rendering can
download Pele and resvg with npm into a runtime cache. Importing the skill does
not run those installers or verify a model. Keep validation in disposable
fixtures with isolated caches. Use only the runtime work authorized by the task.
The `ketchup-video` skill needs local video rendering tools. When the host cannot
embed a video, provide the actual file and keep waiting decisions readable in
text. If rendering fails, report it and follow the skill's text fallback.

Use the host's available visualization tools or Mermaid for diagrams. An imported
`/visualize` example does not establish that command exists. Screenshots and
videos must come from actual captured artifacts.

The bundled `worktree-audit.sh` inspects Cursor transcript locations. Missing
Cursor evidence does not establish that a Codex or Claude worktree is inactive.
Before cleanup, inspect the actual git state and the relevant host's scoped
session evidence. Report uncertain ownership and preserve a worktree when its
activity cannot be established.
