# How pstack-dual differs from pstack 0.15.17

The original source is pinned to official cursor/plugins commit
`978ca6e9c0e012047cd5058b8e829240336e704e`, pstack 0.15.17.
The complete pstack source is preserved in `upstream/pstack/`.
`upstream.lock.json` records every imported file's hash.

All 52 original top-level skills and all their supporting files are present in
the generated package. The six additions are control-cli, control-ui, deslop,
create-skill, pstack-harness, and pstack-review. The first three come from the
same official Cursor commit. The other three provide portable authoring,
host compatibility, and read-only review routing.

File presence does not mean identical behavior. This audit compares source
instructions and packaging. It does not prove every workflow runs on both hosts.

## The release changes are included

[PR #538](https://github.com/cursor/plugins/pull/538) shortens 35 Markdown files
and corrects architect's requested how output to an architectural explanation.
Its reported reduction is 9.7% in bytes and 9.0% in words across those files.
Those counts do not establish equivalent behavior or task speed on our hosts.

[PR #539](https://github.com/cursor/plugins/pull/539) adds ketchup. Its skill,
read-only rules, bro reference, and current-chat scope are included. Our help
override now routes to ketchup and distinguishes it from recall.

The how and interrogate entry points use explicit portable overrides instead
of copying the original entry points. Their original reference files receive
the release's edits. Interrogate now loads the original intent, rubric,
code-quality lens, lead-judgment framework, and agreement map.

## Chosen workflow policy

The user chose current-chat models only and accepted the recommendations below.
Substantial tasks now follow the original research, design, and debugging gates.
Narrow questions and mechanical edits retain the documented shortcuts.

| Original pstack | pstack-dual | Decision |
| --- | --- | --- |
| Chooses Opus and Grok for different roles by default. | Every delegate inherits the current chat's model. Legacy explicit model choices are ignored and reported. Effort and panel size remain configurable. | The user controls model selection in the chat. Panels provide independent same-model review, not model diversity. |
| A simple how question gets an explainer agent. A complex question gets two to four explorers and a separate explainer. | Narrow one-function or one-file questions can be answered directly. Substantial single-module work gets a fresh explainer. Cross-subsystem work gets two to four explorers and a fresh explainer. | Restore separate research and synthesis for substantial investigations. Keep the small-question shortcut. |
| Features always run architect. Several valid implementation shapes require arena. | Substantial features compare at least two designs. Substantial implementations with multiple valid shapes use arena and independent cross-judging. Mechanical one-file edits may skip with a reason. | Restore the original comparison gates for substantial features. Keep the mechanical-edit shortcut. |
| Bug hunting explicitly narrows hypotheses and proves the mechanism at runtime before the design step. Architect runs whenever the fix crosses a function boundary. | Explicit hypothesis elimination, runtime cause proof, and architect for fixes crossing function boundaries are restored. Unavailable runtime evidence is reported as unconfirmed. | Follow the original debugging gates with host-compatible delegation. |
| Saves small ordered commits and ends core tasks by opening a PR. Cheap bug tests precede the fix in commit history. | Completes ordinary changes locally. It checks that a regression test fails before the fix when that test earns its place, without requiring separate commits. | Keep commits and PRs within the requested scope. Use ordered failing-test and fix commits when committing is requested. |
| Grants broad permission for reversible external actions, including team chat, tickets, and evaluations. | Requires authorization from the user's task and actual host permissions. Live CLI evaluations remain opt-in. | Keep the current authorization rules. |

The relevant local sources are `overrides/how/SKILL.md`,
`overrides/interrogate/SKILL.md`, the feature and bug-fix playbooks under
`overrides/poteto-mode/playbooks/`, `overrides/pstack-harness/SKILL.md`, and
`tools/build.py`. The core playbooks govern their design gates. The generated
mode now states that precedence so its general triggers do not contradict them.

## Changes required by the host

Cursor Task calls become native host delegation. Workers use local worktrees
instead of assuming Cursor cloud workers. Native agent definitions replace
Cursor's plugin registration. Effort is configurable; models always inherit.

Cursor's persistent custom mode is not available through this package. Invoke
poteto-mode for a new task and reread it after a handoff or compaction. A loop
runs only when the host supports one. There is no guaranteed background wakeup.

The resolver uses project settings before user settings for effort and panel
size. Every resolved arm returns `model: null`. Existing valid explicit model
choices are reported as `ignored_model` and cannot select another worker model.
Setup does not write global configuration unless requested. A separate-process
fallback is allowed only with the verified, unchanged parent model; a guessed
CLI default cannot establish inheritance.

Host transcripts are limited to the active project. Built-in create-skill and
the cursor-team-kit prerequisites are bundled instead of assumed installed.

Read-only review has an explicit route. Comment Sicko reports findings through
a read-only native wrapper. The original persona can describe edits, but the
wrapper requires the lead to make accepted edits within the task's scope.

The portable poteto-agent wrapper reads poteto-mode and its playbook instead of
copying Cursor's background-agent metadata. Claude effort wrappers carry
written effort settings where the host supports them. None of those files
alone proves that a live host loaded the agent.

## Source material that remains inactive

The generated package and consumer installation include Benny under
`automations/benny/`, with a dormant-reference notice. Its original setup
instructions describe Cursor services. They require a separate port before
use in Codex or Claude Code. The pack is not registered as skills, enabled,
connected to Slack, or configured. The guide's Benny links resolve.

The logo and guide images are included. The original README, plugin metadata,
gitignore, agent source, and license remain in the complete source snapshot.
The installed README and native wrappers explain this derivative's behavior.
They replace Cursor's registration files rather than install Cursor settings.

Overnight orchestration, transcript mining, bot UI, and other advanced workflows
remain present as an experimental library. The supported verification target
is investigation, bug fix, feature, and read-only review. Existing live receipts
were recorded before this source update. No new live evaluation is claimed for
0.15.17 or the current-chat-only model policy. Package checks and synthetic
native-event tests do not establish live agent behavior under these instructions.

## Checks to repeat

Run the source and package checks from this checkout.

```sh
python3 tools/build.py --check
python3 tools/pstack.py validate
python3 -m unittest discover -s tests
```

The build checks every snapshot hash and reproduces the generated files. The
validator checks the derived principle and playbook paths as well as explicit
links, metadata, and licenses. Packaging tests install into temporary projects,
check guide links and dormant content, and verify that unrelated setup is not
enabled or overwritten. These checks establish package completeness and local
contracts. Live agent behavior requires separate opt-in evaluations.
