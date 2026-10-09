# Development

This is a standalone derivative of cursor/plugins/pstack. Treat upstream/ as an
immutable snapshot checked by upstream.lock.json. Edit overrides/ or tools/build.py,
then regenerate skills/ and adapters/. Never fix generated files directly.

Use Python 3.11+ and the standard library for packaging. Keep installs scoped to
an explicit destination; never overwrite unrelated skills, agents, or settings.
Run python3 tools/build.py --check, python3 tools/pstack.py validate, and
python3 -m unittest discover -s tests before reporting a release ready.
Live CLI evaluations are opt-in and run only in disposable fixture repositories.
Do not publish, push, or alter the user's global agent setup as part of validation.
