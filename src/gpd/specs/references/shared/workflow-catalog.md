# Research workflow catalog

Choose a responsibility from the actual task; the user need not name a mode.
Load only the selected command and its required contracts via `get_skill`.
Legacy command IDs remain canonical operation aliases; this index grants no
additional write scope, scientific promotion, approval or execution authority.

| Responsibility | Available operations |
| --- | --- |
| navigation | `gpd-start`, `gpd-progress`, `gpd-suggest-next`, `gpd-show-phase`, `gpd-help`, `gpd-tour` |
| continuity | `gpd-new-project`, `gpd-map-research`, `gpd-resume-work`, `gpd-pause-work` |
| planning | `gpd-plan-phase`, `gpd-discuss-phase`, `gpd-discover`, `gpd-research-phase`, `gpd-list-phase-assumptions`, `gpd-literature-review` |
| execution | `gpd-execute-phase`, `gpd-autonomous`, `gpd-quick`, `gpd-derive-equation`, `gpd-debug` |
| verification | `gpd-verify-work`, `gpd-dimensional-analysis`, `gpd-limiting-cases`, `gpd-validate-conventions`, `gpd-numerical-convergence`, `gpd-regression-check` |
| comparison | `gpd-compare-experiment`, `gpd-compare-results`, `gpd-parameter-sweep`, `gpd-sensitivity-analysis`, `gpd-error-propagation` |
| branches | `gpd-branch-hypothesis`, `gpd-compare-branches`, `gpd-tangent`, `gpd-route` |
| roadmap | `gpd-add-phase`, `gpd-insert-phase`, `gpd-remove-phase`, `gpd-merge-phases`, `gpd-revise-phase`, `gpd-new-milestone`, `gpd-audit-milestone`, `gpd-complete-milestone`, `gpd-plan-milestone-gaps` |
| knowledge | `gpd-record-insight`, `gpd-record-backtrack`, `gpd-decisions`, `gpd-error-patterns`, `gpd-add-todo`, `gpd-check-todos`, `gpd-explain`, `gpd-digest-knowledge`, `gpd-review-knowledge`, `gpd-graph` |
| manuscript | `gpd-write-paper`, `gpd-peer-review`, `gpd-respond-to-referees` |
| delivery | `gpd-export`, `gpd-arxiv-submission`, `gpd-slides` |
| maintenance | `gpd-settings`, `gpd-set-profile`, `gpd-set-tier-models`, `gpd-health`, `gpd-sync-state`, `gpd-compact-state`, `gpd-undo`, `gpd-update`, `gpd-reapply-patches`, `gpd-export-logs` |

The lean installation exposes a small set of workflow skills. Other
operation IDs resolve through MCP `get_skill`; they are not separate installed
slash skills. The full installation retains all native command skill entries.
Use CLI help for deterministic maintenance operations. Keep distinct preflights,
output roots, review gates and state applicators when operations share a workflow.
