# pstack-dual

Poteto's rigorous engineering workflows, adapted for **Claude Code and Codex**.
This is an independent MIT-licensed derivative of
[cursor/plugins/pstack](https://github.com/cursor/plugins/tree/main/pstack),
originally authored by Lauren Tan (poteto). It is not an official Cursor,
Anthropic, or OpenAI plugin.

One shared workflow core, two native adapters. Understand the code, reproduce
bugs, make the smallest justified change, and verify actual behavior. The first
release supports investigation, bug fixes, features, and read-only code review.
It includes upstream principles and the deslop, control-cli, and control-ui
dependencies from the same Cursor source commit.

## Thank you, poteto

Thank you to [Lauren Tan (poteto)](https://github.com/poteto) for creating
[pstack](https://github.com/cursor/plugins/tree/main/pstack) and sharing its
engineering workflows under the MIT license. Her work is the foundation of this
project. This derivative brings those workflows to Codex and Claude Code while
preserving the original attribution and making our adaptations explicit.

## Install in a project

Requires Python 3.11+ and whichever coding CLI you use. No Python dependencies.
From this source checkout, name an existing project directory explicitly:

```sh
python3 tools/pstack.py install --target /absolute/path/to/project
python3 tools/pstack.py doctor --project /absolute/path/to/project
```

Both hosts are installed by default. To select one, add `--agents codex` or
`--agents claude-code`. Use `--dry-run` to inspect the destination and file count.
The installer copies a self-contained payload into `.pstack-dual/bundle`, links
skills into `.agents/skills` for Codex and `.claude/skills` for Claude, and writes
native agents under `.codex/agents` and `.claude/agents`. It does not change host
configuration, permissions, credentials, or user instructions. Codex automatically
discovers `.agents/skills`, including symlinked skills, so no duplicate installation
in `.codex/skills` is needed. Conflicts fail
before writing; reruns update only unmodified installer-managed files.

Start a fresh CLI session in the project and inspect its live agent catalog.
File installation alone does not establish activation. Codex project agents may
require project trust; follow your host's normal trust flow. The doctor reports
filesystem readiness separately from live activation.

## Use

In Codex:

```text
$poteto-mode Reproduce the duplicate-job bug, fix its root cause, and verify it.
$poteto-mode Add CSV export and verify its output through the CLI.
$pstack-review Review this branch against main. Remain read-only.
$setup-pstack Check this project's pstack setup, efforts, and panel size.
```

In Claude Code, use `/poteto-mode`, `/pstack-review`, and `/setup-pstack` instead.
You can also explicitly use `how`, `architect`, or `interrogate` for focused work.
Re-invoke the mode for a new task or after a session handoff. Upstream's custom
mode frontmatter is a Cursor feature; it does not imply persistent host behavior.

Every delegate uses the current chat's model. Model selection stays under your
control in the chat; legacy role model settings are ignored and reported by the
resolver. Efforts inherit unless configured. Panels keep two independent
arms, labeled independent same-model review. Native agent roles
include poteto-agent, pstack-reviewer, and comment-sicko. Claude also gets effort
agents for written per-delegate efforts. Claude and Codex do not automatically
call each other.

```sh
python3 tools/pstack.py config-init --project /absolute/path/to/project
python3 tools/pstack.py resolve --host codex --project /absolute/path/to/project --role bug-fix
```

Configure effort and panel size in `.pstack-dual/models.json` using the
[model schema and example](skills/pstack-harness/references/models.md), then run
`validate-config --file /absolute/path/to/project/.pstack-dual/models.json`.
Use `inherit-parent` for every model field. To install at user scope,
explicitly target your home directory; this can affect every project and may
conflict with existing skills, so project scope is recommended first.

## Maintenance and removal

```sh
python3 tools/build.py --check
python3 tools/pstack.py validate
python3 -m unittest discover -s tests
python3 tools/pstack.py uninstall --target /absolute/path/to/project
```

Removal touches only unmodified managed files and keeps model configuration and
unrelated content. Installed skills are independent of the source checkout;
after updating the source, rerun install to update them. If you commit a consumer
installation, include `.pstack-dual/bundle`, the skill links, and native agents;
exclude `.pstack-dual/install.json` from shared version control because agent
wrappers contain machine-local absolute paths. Regenerate wrappers on each machine.

## Source and verification

The immutable upstream snapshot and commit are recorded in `upstream.lock.json`.
Edit `overrides/` or `tools/build.py`, then regenerate the adapted bundle.
The current source is pstack 0.15.17. All 52 original skills are included, with
portable overrides for the hosts. See [the complete comparison](docs/PARITY.md)
for workflow differences and decisions. Use `$ketchup` in Codex or `/ketchup`
in Claude to catch up on the current chat and pending decisions.
See [porting decisions](docs/PORTING.md), [verification](docs/VERIFICATION.md),
and [upstream updates](docs/UPSTREAM.md). Live evaluation is explicit:

```sh
python3 tools/evaluate.py --hosts codex claude-code
```

It runs real CLI sessions in disposable local repositories and can consume your
subscription quota or API budget. It checks investigation and review stay
read-only and grades bug/feature outputs with independent behavioral assertions.
Logs are local under `evals/runs/` and are not committed.

Advanced orchestration and overnight workflows are preserved as an experimental
library, not part of the verified first-release support claim. The historical
upstream guide is reference material; this README and the native harness contract
govern installation and execution here. Benny's files are included as a dormant
Cursor reference pack. No bot automations are registered or enabled.

## License

MIT. Original pstack: Copyright (c) 2026 Lauren Tan. Included cursor-team-kit
skills: Copyright (c) 2026 Cursor. Both license texts are retained in `upstream/`
and copied into the installed skill payloads. See [LICENSE](LICENSE) and
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
