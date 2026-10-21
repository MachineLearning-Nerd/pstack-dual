# Updating the pinned snapshot

Use tools/sync_upstream.py with an explicit full commit ID. It clones the official
cursor/plugins repository into a temporary directory, imports pstack and only the
three required cursor-team-kit skills, records hashes and source version, and
regenerates the bundle. It does not push, install into consumer projects, or pick
an arbitrary newer upstream version.
Staging stays on the project's filesystem so the snapshot backup and rollback
work on mounted Drives folders as well as a normal home filesystem.

`upstream.lock.json` pins the exact commit, version and every source-file hash.
`upstream-reviews.json` records exact source hashes, reasons and evidence for
files whose behavior is replaced, synthesized, dormant or source-only. Its
addition list accounts for local overrides without an upstream counterpart.
The checker classifies every source file, including nested helpers and new
skills. Unmapped source, changed review hashes, removed exceptional files,
orphan overrides, manifest/version disagreement and missing payloads fail.

An unchanged review applies only to unchanged source bytes. Never refresh hashes
in bulk to make the gate pass. Read the diffs and reconcile the behavior first.
The gate enforces review freshness and source accounting; it cannot prove that
a written judgment preserved meaning or that a live host followed the skill.

## Preview before importing

Read every release between the current and proposed pin, not just the final
release notes. Use a clean source checkout at the exact proposed commit when
reviewing the original files locally. First request a read-only preview:

```sh
python3 tools/sync_upstream.py --commit <full-40-character-commit> --dry-run > /tmp/pstack-preview.json
```

The report includes changed paths and per-file coverage. It returns nonzero when
review is needed; inspect `coverage.errors` and the affected source diffs.
It never writes the snapshot, review ledger, generated files or installation.

Reconcile each changed exceptional file. Carry compatible improvements into
overrides and the native adapter. Preserve current-chat model inheritance,
configured effort, scoped permissions and shared installation. Record the
release decisions in `docs/RELEASES.md`, including deliberate exclusions and
behavior changes. New source layouts require an explicit mapping or a reviewed
source-only decision, not a broad ignore rule.

Prepare a separate candidate review JSON with only the entries actually
reviewed. Keep the live ledger at its current hashes until the import. There is
no auto-approval command. Preview and apply with the same candidate:

```sh
python3 tools/sync_upstream.py --commit <full-40-character-commit> --reviews /tmp/pstack-reviewed.json --dry-run
python3 tools/sync_upstream.py --commit <full-40-character-commit> --reviews /tmp/pstack-reviewed.json
python3 tools/build.py --check
python3 tools/pstack.py validate
python3 tools/check_upstream.py
python3 -m unittest discover -s tests
```

`--source-checkout /absolute/path/to/clean/official/checkout` avoids another
fetch. Its HEAD must equal the full requested commit, with no changes to the
selected source. A dry run does not test future generated payloads. A successful
import builds, validates the bundle and checks actual payload coverage.

The updater installs snapshot, lock, license and review ledger together. If a
build or validation step fails, it restores all four plus the exact previous
generated outputs and executable permissions. It does not depend on rerunning
a now-failing generator to reconstruct the old bundle. Changes you make to
overrides, tools or other local files before invoking sync remain your working
changes; the transaction does not undo them.

Review the upstream snapshot diff, generated changes, and overrides together.
Re-run affected live cases for changes to delegation, permissions, or core
workflows when those evaluations are explicitly authorized. Without them, report
live behavior as unverified. Update receipts only from actual execution. Source paths
and the MIT licenses must survive a sync. An unexpected upstream layout change
is a failed update requiring inspection, not permission to guess replacements.
