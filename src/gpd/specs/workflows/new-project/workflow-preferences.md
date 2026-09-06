<purpose>
Create or confirm `GPD/config.json` for the full/auto `new-project` path after
scope approval and before downstream project artifacts.
</purpose>

<stage_boundary>
This stage is post-approval only. It must not perform scope intake, scope
approval, project-contract validation, project artifact writing, literature
survey, requirements authoring, roadmapping, or conventions work.

This stage owns only `GPD/config.json` and runtime-owned permission sync. If
approved scope is missing or not authoritative, stop and reload
`scope_approval`.
</stage_boundary>

**Mode-aware behavior:**
- Use `research_mode=adaptive` as the recommended default for new projects.
- Preserve explicit `research_mode=explore`, `research_mode=exploit`, and
  `research_mode=adaptive` choices when the user selects them.

<bootstrap>
Load the stage payload before prompting:

```bash
WORKFLOW_PREFS_INIT=$(gpd --raw init new-project --stage workflow_preferences)
if [ $? -ne 0 ]; then
  echo "ERROR: workflow-preferences init failed: $WORKFLOW_PREFS_INIT"
  # STOP; surface the error.
fi
```

Follow `WORKFLOW_PREFS_INIT.staged_loading.field_access_instruction`; `<INIT>` there means `WORKFLOW_PREFS_INIT`. Do not pull later project/literature/roadmap authorities forward.

If `GPD/config.json` already exists, do not rewrite it in this stage. Confirm
the runtime-permission sync status if autonomy is known, then reload
`project_artifacts`.
</bootstrap>

<runtime_selection>
Before writing `GPD/config.json`, infer or confirm the active runtime id using
the same active-runtime rule as `gpd:settings`. Record it as
`SELECTED_RUNTIME`.

Use `SELECTED_RUNTIME` for every permission sync call in this stage so the
configured project posture and runtime permission target cannot drift.
</runtime_selection>

<allowed_config_keys>
Workflow presets are bundles over existing config keys only. Do not create, persist, or infer a separate preset block.

This stage may write only these keys:

- `autonomy`
- `research_mode`
- `parallelization`
- `planning.commit_docs`
- `execution.review_cadence`
- `execution.max_unattended_minutes_per_plan`
- `execution.max_unattended_minutes_per_wave`
- `execution.checkpoint_after_n_tasks`
- `execution.checkpoint_after_first_load_bearing_result`
- `execution.checkpoint_before_downstream_dependent_tasks`
- `model_profile`
- `workflow.research`
- `workflow.plan_checker`
- `workflow.verifier`

Do not write model override maps, git branching keys, USD budget keys,
convention keys, or a `physics` section. Project conventions are outside this
stage and outside `GPD/config.json`; they stay in `GPD/state.json` and
`GPD/CONVENTIONS.md`.
</allowed_config_keys>

<preset_gate>
After scope approval, infer workflow settings from the authorized task; do not
ask the user to select a mode or approve routine configuration separately.
For an absent configuration use balanced autonomy, adaptive research and review,
base-model-first cognition, and auto research/plan-checker/verifier policies.
Use the effective config defaults for remaining keys. Keep explicit session and
project choices. Model profile remains review unless the task clearly warrants
another supported profile; this does not change the runtime's main model.

Advanced preset selection and customization remain available when explicitly
requested. Resolve a chosen preset into allowed keys; do not create a preset
block. Ask only if a missing choice changes authority, scope, or scientific
meaning. Preserve required independent checks and hard stops.
</preset_gate>

<customize_settings>
If the user chooses customization or wants to adjust a preset, ask only for the
allowed keys:

```text
Autonomy: supervised / balanced / yolo
Research mode: explore / balanced / exploit / adaptive
Review cadence: dense / adaptive / sparse
Parallelization: true / false
Planning commit docs: true / false
Workflow research agent: true / false / auto
Workflow plan checker: true / false / auto
Workflow verifier: true / false / auto
Model profile: deep-theory / numerical / exploratory / review / paper-writing
Unattended minutes per plan / wave: positive integers
Checkpoint after N tasks: positive integer
First load-bearing result checkpoint: true / false
Pre-dependent checkpoint: true / false / auto
```

`planning.commit_docs` is stored here as policy. This stage does not mutate
`.gitignore`; downstream artifact stages and settings workflows must respect
the stored policy at their own write boundaries.
</customize_settings>

<write_config>
Map inferred defaults or explicit preset/custom choices into these variables:

- `SELECTED_AUTONOMY`
- `SELECTED_RESEARCH_MODE`
- `SELECTED_PARALLELIZATION`
- `SELECTED_COMMIT_DOCS`
- `SELECTED_REVIEW_CADENCE`
- `SELECTED_MODEL_PROFILE`
- `SELECTED_WORKFLOW_RESEARCH`
- `SELECTED_WORKFLOW_PLAN_CHECKER`
- `SELECTED_WORKFLOW_VERIFIER`
- `SELECTED_RUNTIME`

Apply values through the config CLI so storage stays canonical:

```bash
gpd config set autonomy "$SELECTED_AUTONOMY"
gpd config set research_mode "$SELECTED_RESEARCH_MODE"
gpd config set parallelization "$SELECTED_PARALLELIZATION"
gpd config set planning.commit_docs "$SELECTED_COMMIT_DOCS"
gpd config set execution.review_cadence "$SELECTED_REVIEW_CADENCE"
gpd config set model_profile "$SELECTED_MODEL_PROFILE"
gpd config set workflow.research "$SELECTED_WORKFLOW_RESEARCH"
gpd config set workflow.plan_checker "$SELECTED_WORKFLOW_PLAN_CHECKER"
gpd config set workflow.verifier "$SELECTED_WORKFLOW_VERIFIER"
```

Pre-check `GPD/config.json`. If project docs are being tracked, commit only that
file with message `chore: add project config`. If the selected policy keeps GPD
docs local-only, leave `GPD/config.json` uncommitted and continue.
</write_config>

<runtime_permission_sync>
After `GPD/config.json` is written, sync runtime-owned permissions with the
selected autonomy:

```bash
PERMISSIONS_SYNC=$(gpd --raw permissions sync --runtime "$SELECTED_RUNTIME" --autonomy "$SELECTED_AUTONOMY" 2>/dev/null || true)
echo "$PERMISSIONS_SYNC"
```

Interpret the sync payload before continuing:

- If `message` is present, summarize it plainly.
- If `requires_relaunch` is `true`, show `next_step` verbatim before moving on.
- If runtime detection or install resolution fails, explain that
  `GPD/config.json` was still created but runtime permissions were not
  synchronized yet.
- This sync only updates runtime-owned permission settings. It does not validate
  the base install, tool readiness, literature access, or workflow readiness.
</runtime_permission_sync>

<handoff>
After config exists and permission sync handling is surfaced, reload:

```bash
gpd --raw init new-project --stage project_artifacts
```
</handoff>
