---
name: gpd:limiting-cases
description: Systematically identify and verify all relevant limiting cases for a result or phase
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
      - GPD/research-map/*.md
      - GPD/analysis/*.md
  output_policy:
    output_mode: managed
    managed_root_kind: gpd_managed_durable
    default_output_subtree: GPD/analysis
    stage_artifact_policy: gpd_owned_outputs_only
allowed-tools:
  - file_read
  - file_write
  - shell
  - search_files
  - find_files
  - ask_user
help:
  group: Validation and analysis
  order: 320
  compact_description: Check known limits for a project phase or one explicit current-workspace file
  display_signature: gpd:limiting-cases
  examples:
    - gpd:limiting-cases results/01-SUMMARY.md
  notes:
    - Part of the project-aware technical-analysis lane for explicit current-workspace limit checks.
  root_detail_order: 150
---

<objective>
Execute the `limiting-cases` operation for `$ARGUMENTS` under its command requirements.
The shared analysis workflow owns target resolution, persistence and checking.
</objective>

<execution_context>
@{GPD_INSTALL_DIR}/workflows/limiting-cases.md
</execution_context>
