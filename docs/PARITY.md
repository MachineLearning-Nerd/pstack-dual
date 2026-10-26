# How pstack-dual differs from pstack 0.15.32

The original source is pinned to official cursor/plugins commit
`99b609a72323b70204eab407c622f436e858e112`, pstack 0.15.32.
The complete pstack source is preserved in `upstream/pstack/`.
`upstream.lock.json` records every imported file's hash.

All 58 original top-level skills and all their supporting files are present in
the generated package. The six additions are control-cli, control-ui, deslop,
create-skill, pstack-harness, and pstack-review. The first three come from the
same official Cursor commit. The other three provide portable authoring,
host compatibility, and read-only review routing.

File presence does not mean identical behavior. This audit compares source
instructions and packaging. It does not prove every workflow runs on both hosts.

## The release changes are included

The current snapshot preserves all 200 pstack source files. The generated bundle
contains 64 skills. The required cursor-team-kit skills are unchanged from 0.15.25.
The [release-by-release review](RELEASES.md) accounts for 0.15.26 through 0.15.32,
including both formal-verification skills, complete ketchup decision lists,
sharpen's prompt-only contract, corrected principles and TypeScript guidance.
The new upstream Claude adapter is packaged as historical reference; the portable
host contract remains authoritative.

The 0.15.30 through 0.15.32 update adds statechart and ketchup-video, formal-check
result routing, and every pstack fix through the pinned October 26 commit.
All statechart scripts, tests, and fixtures are included. Model checking needs
TLC and Java, and optional PNG rendering needs npm packages. Those runtimes are
not bundled. Video rendering and host embedding depend on local capabilities.
Reflection edits preserve managed bundles and links by changing the source or
an approved unmanaged copy. No marketplace auto-update is enabled.

The previous 0.15.17 to 0.15.25 update imported these improvements:

- [In your own words](https://github.com/cursor/plugins/pull/602) restates the
  user's goal and problem before work. [Sharpen](https://github.com/cursor/plugins/pull/615)
  introduced expert framing and an outside correctness check. Its current
  0.15.29 behavior returns only a rewritten prompt without executing the task.
- [Ketchup](https://github.com/cursor/plugins/pull/628) explains changes in fewer
  than 150 words, with existing screenshots, videos, or small diagrams when useful.
  It stays read-only and cannot invent visual evidence or start an app for a recap.
- [Review-thread pagination](https://github.com/cursor/plugins/pull/484) reads all
  thread pages and correctly identifies owner approval gates.
- [Plan checks](https://github.com/cursor/plugins/pull/536) handle Markdown fences
  correctly. [Worktree audits](https://github.com/cursor/plugins/pull/574) support
  explicit merge bases and the repository's default branch.
- [Workflow updates](https://github.com/cursor/plugins/pull/613) replace Graphite
  orchestration with gh or optional Origin, refine verification reuse and topology
  ownership, and match delegation effort to the job. Model selection is adapted
  to the user's current-chat-only requirement below.

Verification-skill authoring now checks usable startup from empty data, migrations,
seed data, and missing journey preconditions. Evidence from a substitute environment
must identify setup steps that remain unverified on the real target. Deep debugging
also proposes a cheap ongoing signal when it would catch the cause earlier.

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

The main chat runs the playbook and owns its worklist. The portable poteto-agent
wrapper reads the absolute poteto-mode path and executes only its bounded brief.
It must not take over the whole playbook. Claude effort wrappers carry
written effort settings where the host supports them. None of those files
alone proves that a live host loaded the agent. Task difficulty is assessed
without changing model families, selecting fast model variants, or overriding
configured effort. Unset effort inherits the chat. Unsupported effort or speed
controls are reported rather than invented.

Ketchup's optional `/visualize` reference is not a bundled tool. Use an available
visualization capability or Mermaid. The bundled worktree audit still reads
Cursor transcripts. Missing Cursor activity cannot establish that a Codex or
Claude worktree is inactive; cleanup needs host-session evidence and git state.

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
0.15.17, 0.15.25, 0.15.29, 0.15.32, or the current-chat-only model policy. Package checks and synthetic
native-event tests do not establish live agent behavior under these instructions.

## Checks to repeat

Run the source and package checks from this checkout.

```sh
python3 tools/build.py --check
python3 tools/pstack.py validate
python3 tools/check_upstream.py
python3 -m unittest discover -s tests
```

The build checks every snapshot hash and reproduces the generated files. The
validator checks the derived principle and playbook paths as well as explicit
links, metadata, and licenses. Packaging tests install into temporary projects,
check guide links and dormant content, and verify that unrelated setup is not
enabled or overwritten. These checks establish package completeness and local
contracts. Live agent behavior requires separate opt-in evaluations.
