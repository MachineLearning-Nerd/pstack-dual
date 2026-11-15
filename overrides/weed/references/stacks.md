# Stacks

Use the tool the repo already has before adding one. Check the tool's installed
version and its documentation before writing a rule; config formats change
between major versions. Add a section here when you meet a new stack.

## Universal fallback

Works in any repo with git and no new dependency. Add it to the repo's existing
lint or CI script:

```sh
if git grep -nE 'setTimeout\([^,]+,\s*0\)' -- 'src/**' ':!src/primitives/schedule.ts'; then
  echo "setTimeout(fn, 0) hides an ordering bug. Use scheduleAfterRender() from src/primitives/schedule.ts." >&2
  exit 1
fi
```

Use it when the stack's linter cannot express the rule or a tool is awaiting
the user's approval.

## TypeScript and JavaScript

Detect: `package.json`. Linter: ESLint flat config (`eslint.config.*`), or
Biome (`biome.json`).

Banned imports and boundaries, ESLint `no-restricted-imports`:

```js
"no-restricted-imports": ["error", {
  paths: [{ name: "axios", message: "Use http from src/lib/http; it adds auth, retries, and tracing." }],
  patterns: [{ group: ["**/electron-main/**"], message: "Renderer code cannot import main-process code. Move shared types to src/shared." }],
}]
```

Scope a boundary rule with a `files` glob on its config object.

Banned syntax, ESLint `no-restricted-syntax`:

```js
"no-restricted-syntax": ["error", {
  selector: "CallExpression[callee.name='setTimeout'][arguments.1.value=0]",
  message: "setTimeout(fn, 0) hides an ordering bug. Use scheduleAfterRender() from src/primitives/schedule.",
}]
```

Whole-graph boundaries: `dependency-cruiser` `forbidden` rules with `from.path`,
`to.path`, and a `comment` that names the fix.

Biome: `style/noRestrictedImports` with per-path messages.

Prove with `npx eslint <probe-file>`.

## Python

Detect: `pyproject.toml`, `setup.cfg`, `requirements*.txt`. Linter: ruff.

Banned APIs, ruff `TID251` (enable it in `select`):

```toml
[tool.ruff.lint.flake8-tidy-imports.banned-api]
"requests".msg = "Use app.http.client; it adds retries, timeouts, and tracing."
"datetime.datetime.utcnow".msg = "Use app.time.now(); utcnow returns a naive datetime."
```

Boundaries, import-linter (`lint-imports`):

```toml
[tool.importlinter]
root_package = "app"

[[tool.importlinter.contracts]]
name = "UI does not touch the database"
type = "forbidden"
source_modules = ["app.ui"]
forbidden_modules = ["app.db"]
```

Prove with `ruff check <probe-file>` or `lint-imports`.

## Rust

Detect: `Cargo.toml`. Linter: clippy.

Boundaries: split into workspace crates. A crate cannot import what its
`Cargo.toml` does not depend on, so the compiler enforces it.

Banned APIs, `clippy.toml`:

```toml
disallowed-methods = [
  { path = "std::thread::sleep", reason = "Use tokio::time::sleep in async code; a blocking sleep stalls the runtime." },
]
disallowed-types = [
  { path = "std::sync::Mutex", reason = "Use parking_lot::Mutex; it matches the rest of the crate and cannot poison." },
]
```

These lints warn by default. Enforce with `cargo clippy -- -D warnings`, or set
`disallowed_methods = "deny"` under `[lints.clippy]` in `Cargo.toml`.

Prove with `cargo clippy` after adding the probe as a module the crate compiles.

## Dart and Flutter

Detect: `pubspec.yaml`. Linter: `dart analyze` with `analysis_options.yaml`.

Boundaries: split into packages in a pub workspace. A package cannot import
what its `pubspec.yaml` does not depend on.

Banned APIs: the core analyzer has no banned-API rule. Use the universal
fallback, or propose a `custom_lint` rule and wait for approval, since it adds
a dependency.

Prove with `dart analyze <probe-file>`, or run the fallback script.

## Go

Detect: `go.mod`. Linter: golangci-lint.

Boundaries: `internal/` packages are compiler-enforced. For other edges use
`depguard` rules with a `desc` that names the fix.

Banned calls: `forbidigo` patterns with a `msg`. The config layout differs
between golangci-lint v1 and v2; check `golangci-lint version` first.

Prove with `golangci-lint run <probe-dir>`.
