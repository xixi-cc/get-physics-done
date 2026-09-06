---
name: gpd:dimensional-analysis
description: Systematic dimensional analysis audit on all equations in a derivation or phase
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
      - GPD/research-map/FORMALISM.md
      - GPD/research-map/VALIDATION.md
  output_policy:
    output_mode: managed
    managed_root_kind: gpd_managed_durable
    default_output_subtree: GPD/analysis
allowed-tools:
  - file_read
  - shell
  - search_files
  - find_files
  - file_write
  - ask_user
help:
  group: Validation and analysis
  order: 310
  compact_description: Check dimensional consistency for a project phase or one explicit current-workspace file
  display_signature: gpd:dimensional-analysis
  examples:
    - gpd:dimensional-analysis results/01-SUMMARY.md
  notes:
    - Part of the project-aware technical-analysis lane; analysis artifacts belong under GPD/analysis/ when a standalone target is supplied.
  root_detail_order: 140
---

<objective>
Execute the `dimensional-analysis` operation for `$ARGUMENTS` under its command requirements.
The shared analysis workflow owns target resolution, persistence and checking.
</objective>

<execution_context>
@{GPD_INSTALL_DIR}/workflows/dimensional-analysis.md
</execution_context>
