# Role configuration

Configuration is JSON, schema version 1. Each host has an optional default, roles,
and panels. A project setting beats the user setting for the requested role's
effort and panel size; an unspecified role inherits the host default or session.
Every arm inherits the current chat's model. Panel entries remain separate arms.
Model selection stays in the chat, under the user's control.

```json
{
  "version": 1,
  "codex": {
    "default": {"model": "inherit-parent", "effort": "inherit-parent"},
    "roles": {"bug-fix": {"model": "inherit-parent", "effort": "high"}}
  },
  "claude-code": {
    "default": {"model": "inherit-parent", "effort": "inherit-parent"},
    "roles": {"feature": {"model": "inherit-parent", "effort": "high"}},
    "panels": {"interrogate reviewers": [
      {"model": "inherit-parent", "effort": "high"},
      {"model": "inherit-parent", "effort": "high"}
    ]}
  }
}
```

Use inherit-parent for model fields. Aliases inherit and auto also mean inheritance.
Valid legacy configurations with explicit model names remain readable, but those
choices are ignored. Role resolution always returns `model: null` and reports a
discarded explicit choice as `ignored_model`. It never rewrites the source config.
Efforts are
low, medium, high, xhigh, max, and (Codex only) ultra when the selected model
supports it. Effort changes do not select another model. No provider crossing is implicit.

Code roles: feature, refactoring, bug-fix, perf-issue, hillclimb, swarm workers.
Judgment roles: judgment and prose, hardest tasks, how explainer, why synthesizer,
reflect judgment, reflect divergent, reflect synthesizer, trail reviewer.
Other roles: default, how explorer, why investigators, reflect tooling.
Panels: arena runners, arena cross-judge pool, architect runners, interrogate reviewers.

The resolver never escalates effort, selects a different model, or changes host
configuration. Claude effort agents carry written efforts; if they are not live,
report the inherited effort. A role resolution describes the request, not proof
that the resulting child ran with that identity.
