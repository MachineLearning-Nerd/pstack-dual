# Role configuration

Configuration is JSON, schema version 1. Each host has an optional default, roles,
and panels. A project setting beats the user setting for the requested role;
an unspecified role inherits the host default or session. Panel entries remain
separate arms even when they use the same model.

```json
{
  "version": 1,
  "codex": {
    "default": {"model": "inherit-parent", "effort": "inherit-parent"},
    "roles": {"bug-fix": {"model": "gpt-6.1-sol", "effort": "high"}}
  },
  "claude-code": {
    "default": {"model": "inherit-parent", "effort": "inherit-parent"},
    "roles": {"feature": {"model": "sonnet", "effort": "high"}},
    "panels": {"interrogate reviewers": [
      {"model": "sonnet", "effort": "high"},
      {"model": "opus", "effort": "high"}
    ]}
  }
}
```

Model names are examples, not entitlements. Confirm them with the live host.
Aliases inherit-parent, inherit, and auto omit that field at spawn. Efforts are
low, medium, high, xhigh, max, and (Codex only) ultra when the selected model
supports it. Claude supports aliases sonnet, opus, haiku, fable and claude-* IDs.
Codex uses model IDs from its catalog. No provider crossing is implicit.

Code roles: feature, refactoring, bug-fix, perf-issue, hillclimb, swarm workers.
Judgment roles: judgment and prose, hardest tasks, how explainer, why synthesizer,
reflect judgment, reflect divergent, reflect synthesizer, trail reviewer.
Other roles: default, how explorer, why investigators, reflect tooling.
Panels: arena runners, arena cross-judge pool, architect runners, interrogate reviewers.

The resolver never escalates effort, substitutes models silently, or changes host
configuration. Claude effort agents carry written efforts; if they are not live,
report the inherited effort. A role resolution describes the request, not proof
that the resulting child ran with that identity.
