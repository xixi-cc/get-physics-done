# Personal Astra integration — 2026-09-06

This is the maintained personal GPD 1.2.2 integration, not a new upstream
release or a model named mode. Authoritative branch: `local/astra-current`.

Based on `6d2463c5` (includes `7a31b895` and the 2026-09-02
base-model-first work), preserving the validated working-tree quick/explain
and executor changes. Integrates thin-referee commits `54478f3d`, `6813f907`.
The uncommitted thin-planner experiment remains separate; this release retains
the established planner contract surface, with adaptive defaults and task sizing.

Absent project settings now use base-model-first cognition, adaptive research
and review cadence, balanced autonomy, and auto optional workflow agents.
Explicit project settings and scientific gates remain authoritative. New-project
setup infers ordinary settings without requiring the user to name a mode.
Main-context work uses the runtime-selected model. Existing concrete model routes,
including task-specific translation limits, remain in force.

Codex projection defaults to native lean: one router plus eleven ordinary
implicit command skills. Sixty other canonical commands remain explicitly
invocable, with their workflow code retained. No duplicate custom router or
second disabled-command registry is required. Full projection remains available.
The selection is a maintainable initial policy, not a measured global optimum.

The Python runtime, command registry, validators, state schemas, artifact
freshness, proof redteam, and approved write scopes remain necessary harness.
ChatGPT Work can use these runtime-neutral workflows when its environment
actually exposes the GPD runtime and project files. Local installation alone
does not provision a separate cloud Work environment.
