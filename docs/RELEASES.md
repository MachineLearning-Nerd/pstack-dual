# Reviewed upstream releases

The current pin is pstack **0.15.42**, official commit
`bf0c7cd80abdbf7fe47b634978a7d1b4071f71a7`, observed on 2026-11-15.
The original snapshot has 560 pstack files and 58 skills. Most of the growth is
the statechart compiler's test corpus. With the seven portable support skills, the
generated bundle has 65 skills. The selected team-kit inputs add four files,
making 564 locked files. File accounting is reproducible with
`python3 tools/check_upstream.py --json`.

## 0.15.26

Reviewed through `0b8e952052d482ee6de06deebf14d590d77b1b34` from the 0.15.25 pin.

- Added `create-formal-verification-skill` for properties tests rarely reach.
- Ketchup now includes every waiting decision with the evidence and risk needed
  to make it. A fixed word limit cannot remove items.
- Clarified root-cause debugging, premise testing, retry safety and behavioral
  tests. Removed assertion-shape rules that rejected legitimate absence checks.
- TypeScript brands now use a validating type guard rather than an `as` cast.
- Normalized skill names and added a Claude adapter, generated Claude plugin,
  and documentation/tree validation.

The original skills and docs are included. Our standalone Python build and native
harness remain authoritative. The official generated Claude plugin is another
delivery of the same source, not an additional skill collection to install.

## 0.15.27

Reviewed through `0148b78c56c72a1b8412055913c79f767095b217`.

Removed sharpen's explicit ban on returning a rewritten prompt. Its intermediate
instructions still said to perform the task. The final 0.15.29 contract below
supersedes that intermediate state.

## 0.15.28

Reviewed through `d457567332aa6989e753ea289f30ea2bfbc80bc0`.

- Added `maintain-formal-verification-skill`, distinguishing stale verification
  from a real code defect and keeping product fixes outside its default scope.
- Formal skill creation defaults to TLA+ for event ordering. Where a code-level
  verifier is unavailable, it tests real code with generated inputs and states
  that limitation instead of presenting a hand model as a proof of the function.
- Formal checks record covered code, bounds, assumptions and a sync commit.
  A deliberate broken variant must demonstrate that the check can fail.
- Setup offers optional behavioral and formal verification separately. The
  portable setup/help overrides now include these offers and maintenance routes.

These are reusable instructions. No verifier runtime is bundled or installed,
and importing the skills does not mean a formal proof has been run.

## 0.15.29

Reviewed through `88d47514b82e7c44f00f2b2a72ff6dd12158038c`.

**Sharpen returns only a rewritten prompt.** It considers expert methods, primary
material and an independent correctness check, then returns the improved prompt.
It does not execute the underlying task. This replaces our earlier description
of sharpen as an execution workflow.

## 0.15.30

Reviewed through `eb4db2b55b2b7dec3d9282754cddf0a56bf4ff10`.

Added `statechart` to turn a TLA+ model into Mermaid charts with numbered bug
paths, compare a fix or agreed specification, or turn a chart into a TLA+
skeleton. The reader's labels describe observable behavior. Bugs need real-code
replay when the model describes code. Help and guide routes are included.

## 0.15.31

Reviewed through `642289e6b1eb01c25b02ea041dccaf7b5864e131`.

- Adopted statechart fixes for separate model configurations, missing variables,
  unchecked rules, partial TLC evidence, and copying output across file systems.
- Imported the revised renderer using Pele and resvg, regional charts, grouping,
  covered overviews, strict mapping access, and tool discovery through mise.
- Included all 27 current statechart files, including runtime modules, its test
  module, and four Mermaid fixtures. Superseded files deleted upstream are absent.

These scripts need Node. Model commands can download TLC and Java with mise,
about 305 MB on first use. PNG rendering can download `pele@1.8.0` and
`@resvg/resvg-js@2.6.2` with npm into a runtime cache. Importing or installing
instructions does not provision these tools or prove a model.

## 0.15.32

Reviewed through `b1a129891c49f6b84d0613477f5d021a0782b5e0`.

- Added `ketchup-video` for a silent slide video of the work, with every waiting
  decision kept in text. It requires real evidence, rendered-frame inspection,
  readable slide durations, and a disclosed fallback if rendering fails.
- Formal-verification creation now tells generated TLA+ check skills to read
  every result with `statechart` by name, without copying unstable script paths.
- Portable help includes both new routes. Video rendering tools are not bundled.

## Fixes after the 0.15.32 bump

Reviewed every pstack change through the current pinned commit.

- Reflection protects plugin caches, shows the edit destination before approval,
  and forbids PR creation or pushing. Our native contract also protects managed
  bundles and symlinks, and routes derivative changes to source overrides.
- PR watching distinguishes fork heads from upstream branches during stack
  discovery and caps polling and retry sleeps at the remaining deadline.
- Plan checks recognize matching multi-backtick inline code delimiters.
- Orchestration prefers the sole active PR over a branch's closed history while
  retaining historical anchors and rejecting multiple active PRs.
- Worktree auditing supports GNU stat and date on Linux while retaining BSD
  behavior. Native Codex or Claude transcript ownership still needs host evidence.
- Swarm fixes its numbered steps and result-table reference.
- Official Claude plugin documentation explains third-party marketplace updates.
  This standalone package still updates through an explicit exact-commit import.

## 0.15.33 and 0.15.34

Reviewed through `740d2c0` and `164ced1`.

- Statechart is now a TypeScript compiler run through one POSIX launcher,
  `scripts/statechart SPEC.tla`. It checks the model with TLC, draws the Mermaid
  chart, and reports the shortest path to each broken rule. The launcher needs
  Node 22.18+ (or 23.6+), Bun 1.1.5+, or Deno 2.0+, with no build step. All
  previous `.mjs` scripts and the chart-to-TLA+ skeleton and code audit are gone.
- Property traces keep qualified INSTANCE action names such as `C!Up`.

The first model check still installs TLC and Java with mise and needs the
network. Importing or installing the skill does not provision them.

## 0.15.35

Reviewed through `ab1f702`.

- Poteto-mode restates the user's goal in its first message, delegate briefs,
  PR descriptions, and final reports, and steers running agents in the
  background. Explain the Number applies before measuring.
- Interrogate adversaries must prove each finding with a run, and the lead keeps
  only findings a rerun confirms. Its reviewer, rubric, lead-judgment, and
  code-quality references were deleted.
- Arena drops or replaces rejected runner seats. Its cross-judge must come from
  another vendor, and an inherited entry never judges.
- Autopilot playbooks push each finished unit and block a PR only on a problem a
  run shows. Autopilot-stack is Autopilot-full without the merge.
- Ketchup-video adds subtitles and measures slide holds from the rendered file.

## 0.15.36

Reviewed through `c742dd6`.

Orchestrate is agentic. The coordinator uses its own tools, Cursor's Project
tracker and store, and PR and CI event subscriptions. The `orch` scripts and
their tests were deleted.

## 0.15.37 through 0.15.42

Reviewed through `bf0c7cd80abdbf7fe47b634978a7d1b4071f71a7`.

- Sharpen's rewritten prompt asks the agent to prototype any choice an
  experiment can settle. Product and preference calls stay with the user.
- Statechart reports SANY's line and column for unreadable specs and draws
  arrows into a parent state through its border.
- Why is one short file. It answers from the commits and PR discussions behind
  the code, cites the authors, marks inferences, and says what the record does
  not answer. Its investigators, synthesizer, and source references are gone.
  Recall starts its own investigators.
- How is one file with one read-only subagent and a short brief. Poteto-mode and
  its playbooks no longer route to how; they trace the code directly.
- Default models moved to Fable 5.2, Opus 5.5, and Gemini 4 Carbon. Setup drops
  the how and why roles and writes a `# defaults: 2` marker.

## Reconciliation for 0.15.42

- **How** follows the single-subagent design and brief, keeping the direct answer
  for narrow questions. **Interrogate** follows the run-proven design, with a
  worktree per adversary and the panel labeled independent same-model review.
- **Feature and bug-fix** playbooks trace the subsystem directly and carry the
  user's goal into briefs and reports.
- **Arena** is adapted in `tools/build.py`. Runners and the judge inherit the
  current chat's model, so the judge is a fresh agent that wrote no candidate,
  not one from another vendor. Without this, inherited arms would never judge.
  The design guide's arena sentence is adapted to match.
- **Retired roles.** `how explorer`, `how explainer`, `why investigators`, and
  `why synthesizer` are no longer resolvable. Configs that name them stay valid,
  and `validate-config` lists them under `retired_roles`.
- **Orchestrate.** pstack-harness maps the Cursor Project tracker, store, event
  subscriptions, and cloud workers to an approved `notes.md`, local worktree
  workers, and explicit `gh` or `watch-pr` status checks. No polling loop starts.
- **Validation.** Gemini and Fable slugs are rewritten to inheritance, and the
  bundle check rejects any that remain. It also rejects plain-text
  `references/*.md` mentions whose file is missing. That gap had let the old how
  and interrogate overrides point at deleted references.

Excluded: the new default models, the `# defaults: 2` marker and Grok-default
migration, the cross-vendor judge requirement, and cloud workers. Every delegate
still inherits the chat model.

## Additional reconciliation in pstack-dual

The feature override now restores two compatible requirements from the original
0.15.25 playbook: re-ground upstream-derived edits and port shared changes to
every consumer with verification; keep code-coupled implementation under one
owner and refresh the throughput checkpoint at phase boundaries.

The update gate records source-file dispositions and exact reviewed hashes for
overrides, synthesized behavior, dormant automations and source-only material.
Changed exceptional source, orphan overrides and unknown paths stop the update.
Critical mode transformations also require exactly one source match.

## Deliberate host differences

- Every delegate inherits the selected chat model. Effort and panel sizes remain
  configurable. The upstream Claude model rules do not replace this policy.
- Shared `.agents/skills` and `.claude/skills` remain our installation paths.
  The upstream marketplace and generated plugin are not activated alongside them.
- The original Claude adapter is packaged as historical reference with a warning;
  `skills/pstack-harness/SKILL.md` governs actual tool names and capabilities.
- Native host tools, scoped session evidence, isolated writers and actual user
  authorization take precedence over Cursor-only automation assumptions.

The monorepo's external `harness/pstack/claude-code/` is generated delivery,
`scripts/generate-pstack-harness-trees.mjs` and `scripts/check-pstack-docs.mjs`
are upstream validation tools, and marketplace/CI files are monorepo integration.
Their useful validation intent is implemented locally without introducing a
second generated source, a Node packaging dependency or another installation.
They are outside the pinned `pstack/` subtree and selected team-kit inputs.

Source inspection and package checks establish content accounting and local
contracts. Live LLM workflows, host catalog activation, formal proofs and a
numeric agent-quality improvement require separate evidence; none is implied.
