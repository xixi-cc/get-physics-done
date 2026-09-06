---
name: gpd:numerical-convergence
description: Systematic convergence testing for numerical physics computations
argument-hint: "[phase number or file path]"
context_mode: project-aware
command-policy:
  schema_version: 1
  subject_policy:
    explicit_input_kinds:
      - phase number or file path
  supporting_context_policy:
    project_context_mode: project-aware
    project_reentry_mode: disallowed
    optional_file_patterns:
      - GPD/STATE.md
      - GPD/ROADMAP.md
      - GPD/research-map/VALIDATION.md
      - GPD/analysis/*.md
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
  - search_files
  - find_files
  - ask_user
help:
  group: Validation and analysis
  order: 330
  compact_description: Run convergence checks for a project phase or one explicit current-workspace artifact
  display_signature: gpd:numerical-convergence
  examples:
    - gpd:numerical-convergence results/mesh-study.csv
  notes:
    - Part of the project-aware technical-analysis lane for explicit current-workspace convergence checks.
  root_detail_order: 160
---

<objective>
Execute the `numerical-convergence` operation for `$ARGUMENTS` under its command requirements.
The shared analysis workflow owns target resolution, persistence and checking.
</objective>

<execution_context>
@{GPD_INSTALL_DIR}/workflows/numerical-convergence.md
</execution_context>
