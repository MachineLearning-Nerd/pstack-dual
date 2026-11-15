# Audit categories

Assume the next contributor is an agent that sees only the files it opened,
copies the nearest example, and takes the shortest path that compiles. Look for
what it would copy wrong.

| Category | What it looks like | Typical fix |
| --- | --- | --- |
| Duplicates | Two or more ways to do one thing: two HTTP clients, date libraries, state stores, error types | Keep one, migrate, ban the others |
| Escape hatches | `any`, `as` casts, `@ts-ignore`, `# type: ignore`, `noqa`, `unwrap()`, `!` on nullable values | Fix the type, ban the hatch in product code |
| Quick-fix patches | `setTimeout(..., 0)`, sleeps, retry loops around races, broad `except: pass` or empty `catch` | Fix the ordering or state flow, ban the patch |
| Justification comments | A comment explaining why a hack is acceptable | Fix the hack, delete the comment |
| Nuanced primitives | APIs that need judgment to use well: effects, raw SQL, manual locks, auth checks, global state | Wrap in one framework API, ban direct use |
| Boundary leaks | Client importing server code, UI importing the DB layer, a feature reaching into another feature's internals | Make the boundary a directory, ban the import |
| Legacy paths | A deprecated API that still has callers | Migrate callers, delete it |

## Candidate shape

Return each candidate as:

```
pattern:      one line naming it
category:     one of the table rows
search:       the grep or AST query that finds every occurrence
occurrences:  count, with up to five file:line examples
harm:         a cited bug, revert, or perf issue, or "none found"
proposed way: the existing API to keep, or "needs design"
```

The `search` line matters: Phase C uses it for the spreading check, and Phase
F often reuses it as the rule.

## Evidence rules

- Count with the search query, not by reading. Report the exact command.
- Do not report style preferences the repo has not chosen. A pattern is a weed
  only when the codebase already shows a better way or a cited harm.
- Exclude tests when the pattern is legitimate there, and say so.
