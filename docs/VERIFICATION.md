# Verification

The release checks are reproducible generated content, complete local references,
valid skill metadata and license payloads, role resolution, conflict-safe install,
and preservation of unrelated files during update/removal. Unit tests cover
observable installation and resolution behavior, including paths with spaces.

Live verification uses tools/evaluate.py. Each case receives a fresh isolated Git
repository with the installed bundle and a minimal application. Both CLIs use
their existing login and normal permission scope; tests do not bypass sandboxing.
Codex uses workspace-write and ignores user config for reproducibility. Claude
uses project settings and explicit allowlisted local development tools.

Cases:
* Investigation: source-grounded explanation and the correct entry-point result;
  original project file hashes remain unchanged.
* Bug fix: CLI reproduction changes from failing contract to passing contract,
  with edge-case assertions outside the fixture; no unrelated files changed.
* Feature: new CLI behavior passes hidden normal, empty, and duplicate-input
  assertions while existing behavior stays intact.
* Review: detect seeded reachable defects, cite the changed file, and keep source
  and test files unchanged. Findings are graded independently of agent self-report.

The runner records exit status, duration, CLI versions, grader outcome, final
response, events, and the resulting source diff. Native delegation is recorded
when events expose it; a transcript not exposing agent execution cannot establish
it. Passing fixtures establishes these cases, not universal correctness or
readiness of advanced cloud/overnight workflows.

Actual live results are written to evals/latest.json and summarized in
docs/LIVE_RESULTS.md after the first completed run. A failed or unavailable case
is not represented as passed.

The completed v1 verification has 19 passing unit tests and 10 passing live cases:
the eight core host/workflow combinations, plus explicit native model/effort
delegation in each host. Installed payload validation and all 11 rendered native
agent definitions were checked from a separate temporary installation. The pinned
upstream update command was exercised without changing the selected source version.

Those live receipts were recorded for the 0.15.15 source. The 0.15.17 update
uses package and unit checks; no new live result or unchanged agent behavior is
implied. See [the source comparison](PARITY.md) for the remaining differences.

When evaluating cases in separate runs, aggregate their saved receipts with:

```sh
python3 tools/report_evaluations.py --runs evals/runs/<run-1> evals/runs/<run-2>
```

Use only actual completed run directories. The aggregator refuses missing inputs.
For the optional inheritance test, run evaluate.py with
`--cases native-delegation`. It checks that native calls omit model overrides
and request the configured effort. It requires a matching completed child state
for Codex or a successful foreground agent result for Claude. A launch event or
the parent's prose alone does not establish completed independent work.
The older model-selection receipts do not verify this current-chat policy.
