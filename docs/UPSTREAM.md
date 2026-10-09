# Updating the pinned snapshot

Use tools/sync_upstream.py with an explicit full commit ID. It clones the official
cursor/plugins repository into a temporary directory, imports pstack and only the
three required cursor-team-kit skills, records hashes and source version, and
regenerates the bundle. It does not push, install into consumer projects, or pick
an arbitrary newer upstream version.
Staging stays on the project's filesystem so the snapshot backup and rollback
work on mounted Drives folders as well as a normal home filesystem.

```sh
python3 tools/sync_upstream.py --commit <full-40-character-commit>
python3 tools/build.py --check
python3 tools/pstack.py validate
python3 -m unittest discover -s tests
```

Review the upstream snapshot diff, generated changes, and overrides together.
Re-run affected live cases for changes to delegation, permissions, or core
workflows. Update verification receipts only from actual execution. Source paths
and the MIT licenses must survive a sync. An unexpected upstream layout change
is a failed update requiring inspection, not permission to guess replacements.
