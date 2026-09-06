---
name: gpd:sensitivity-analysis
description: Systematic sensitivity analysis -- which parameters matter most and how uncertainties propagate
argument-hint: "[--target quantity] [--params p1,p2,...] [--method analytical|numerical]"
context_mode: project-aware
command-policy:
  schema_version: 1
  subject_policy:
    explicit_input_kinds:
      - --target quantity
      - --params p1,p2,...
  supporting_context_policy:
    project_context_mode: project-aware
    project_reentry_mode: disallowed
    optional_file_patterns:
      - GPD/STATE.md
      - GPD/ROADMAP.md
      - GPD/analysis/PARAMETERS.md
  output_policy:
    output_mode: managed
    managed_root_kind: gpd_managed_durable
    default_output_subtree: GPD/analysis
    stage_artifact_policy: gpd_owned_outputs_only
allowed-tools:
  - file_read
  - file_write
  - file_edit
  - shell
  - find_files
  - search_files
  - task
  - ask_user
help:
  group: Validation and analysis
  order: 400
  compact_description: Rank which inputs matter most from project context or explicit current-workspace flags
  display_signature: gpd:sensitivity-analysis
  examples:
    - gpd:sensitivity-analysis --target observable --params alpha,beta --method sobol
  notes:
    - Part of the project-aware technical-analysis lane for ranking influential inputs from project context or explicit current-workspace flags.
  root_detail_order: 200
---

<objective>
Execute the `sensitivity-analysis` operation for `$ARGUMENTS` under its command requirements.
The shared analysis workflow owns target resolution, persistence and checking.
</objective>

<execution_context>
@{GPD_INSTALL_DIR}/workflows/sensitivity-analysis.md
</execution_context>
