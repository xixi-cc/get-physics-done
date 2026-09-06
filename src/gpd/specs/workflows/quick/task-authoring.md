<purpose>
Complete a self-contained quick task in the current main context after staged bootstrap. Keep local evidence and structured state; delegate only for requested isolation or a concrete context/resource need.
</purpose>

<stage_boundary>
Start only after task_bootstrap created ${QUICK_DIR}. Reload `gpd --raw init quick "$DESCRIPTION" --stage task_authoring` and follow `staged_loading.field_access_instruction`. Do not load the workflow index or unrelated roles.
</stage_boundary>

<quick_authorities>
@{GPD_INSTALL_DIR}/references/quick/quick-mode-boundary.md
@{GPD_INSTALL_DIR}/references/quick/quick-durability-minimum.md
@{GPD_INSTALL_DIR}/references/quick/quick-reroute-rules.md
</quick_authorities>

<process>
1. Apply the active project contract, anchor and forbidden-proxy gates. Missing or invalid required contract context blocks execution; do not infer absent state. Theorem-style, proof-bearing, publication-grade, referee-response and proof_obligation work must reroute to the full workflow, including proof-redteam where required. A generic claim is not itself a theorem.
2. For targeted source lookup, active reference artifacts or protocol context, reload `gpd --raw init quick "$DESCRIPTION" --stage reference_context`. The default small-task path covers self-contained local calculations, dimensional checks, unit conversions and bounded code or formatting changes.
3. Write `${QUICK_DIR}/${next_num}-PLAN.md` directly: objective, authorized scope, necessary work and relevant acceptance checks. Use the task's natural size; do not add tasks to satisfy a fixed count. Do not load gpd-planner or gpd-executor just to perform this main-context route. Honor any explicitly required plan approval; already granted execution authority does not need repeating.
4. If `tool_requirements` is non-empty, run `gpd validate plan-preflight <PLAN.md>` and resolve blocking requirements before execution. Perform the bounded work, preserving unrelated changes. Check relevant invariants at meaningful transformation boundaries and verify the actual output; repeat checks only for changed inputs, failures or unresolved concerns.
5. Write `${QUICK_DIR}/${next_num}-SUMMARY.md` with actual artifacts, checks and results, unresolved issues and completion status. Verify both plan and summary are fresh current-task artifacts. Do not invent a child id or child return for main-context execution. Do not run `gpd apply-return-updates` without a real delegated return.
6. Only on completed work, record durable state through `gpd state add-decision --phase "quick-${next_num}" --summary "Quick task ${next_num}: ${DESCRIPTION}" --rationale "Ad-hoc task completed outside planned phases"` and `gpd state update "Last Activity" "${date}"`. Do not edit ROADMAP.md or hand-maintain STATE.md tables. Report incomplete work without a completion decision.
7. Run `gpd pre-commit-check --files` on the actual changed quick artifacts and state files, including GPD/state.json when changed. A failing check blocks the commit. Honor commit_docs and explicit user commit instructions; if enabled, use `gpd commit` with an explicit file allowlist. Report the actual commit or that changes remain local.
8. Return the result, summary path, checks and any remaining issue concisely. No fixed banner or task-count ceremony is needed.

The direct route writes only within the active staged writes_allowed paths. If the task needs edits outside that scope, independent execution is explicitly requested or a concrete isolation/context need justifies delegation, load `{GPD_INSTALL_DIR}/references/quick/quick-delegated-authoring.md`. That path owns real child-artifact gates, freshness and return application. Do not mix direct completion with a pending child, and do not bypass a failed child gate by relabeling it direct success.
</process>
