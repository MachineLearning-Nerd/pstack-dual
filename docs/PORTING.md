# Porting decisions

Keep original source in upstream/ and generate adapted skill payloads. Core
workflow overrides are explicit files; systematic substitutions are in build.py.
This makes differences reviewable without pretending the port is byte-identical.
The [0.15.25 comparison](PARITY.md) accounts for the original source, packaged
content, host adaptations, and workflow choices.

| Upstream assumption | Portable behavior |
| --- | --- |
| Cursor Task calls and model slugs | Native host delegation inheriting the current chat's model; configurable effort |
| Always-applied .cursor rule | Explicit JSON resolver, project before user settings |
| Cursor Markdown personas | Install-time Claude Markdown and Codex TOML wrappers |
| Cloud workers | Isolated local git worktrees; serial writer if isolation fails |
| Cursor custom mode | Explicit invocation and re-read after handoff/compaction |
| Cursor transcript directories | Host-owned records filtered to the current workspace |
| Unbundled cursor-team-kit prerequisites | Three MIT-attributed skills from the same commit |
| Built-in create-skill | Bundled portable authoring guidance |
| Automatically open a PR at completion | Local completion unless publishing is in scope |
| PR review overlaps Babysit | Explicit read-only review routing |
| Design comparisons for features | Architect for substantial features and arena for multiple valid implementation shapes; mechanical one-file shortcut |
| Broad external-action autonomy | User task and real permission policy determine authorization |

Feature and bug-fix overrides retain reproduction, source understanding,
bounded delegation, independent review, and behavioral verification. They remove
automatic commits and PR creation from an ordinary local change. Investigations
and code reviews remain read-only. Effort agents carry Claude's written effort;
their filesystem existence is not proof of loading. Codex spawns that set effort
use a fresh context and omit model overrides.

Native multi-agent work can use more tokens than a single agent. Every worker
inherits the current chat's model. Legacy role model choices are reported as
ignored. Two independent instances
of the same model can provide separate review, but not cross-model evidence.

The core four workflows are the release target. Other imported skills and
playbooks are an experimental library requiring their actual prerequisites.
Cloud automation and cross-provider orchestration are intentionally outside v1.
The imported guide is historical and should not be treated as a tested host manual.

Authoritative host references:
* https://learn.chatgpt.com/docs/build-skills
* https://learn.chatgpt.com/docs/agent-configuration/subagents
* https://code.claude.com/docs/en/skills
* https://code.claude.com/docs/en/sub-agents
