<purpose>
Shared execution for a selected technical-analysis operation. The caller binds
`ANALYSIS_OPERATION`, method reference and output rules; it does not grant any
additional state or scientific-promotion authority.
</purpose>

<process>
Resolve `$ARGUMENTS` through centralized preflight before computation:

```bash
gpd --raw validate command-context "${ANALYSIS_OPERATION}" "$ARGUMENTS"
gpd --raw init progress --include state,config --no-project-reentry
```

Stop on failed preflight/init. Parse workspace/project existence, state,
conventions, approximations, and commit policy from the actual response.
A bare number requires a real current-workspace project phase; an explicit file
is a file target even inside a project. Empty or ambiguous input follows the
command's context policy; use the existing request when it already identifies
the target and ask only for a missing material decision. Never reenter an
ancestor or recent project to manufacture phase authority.

For a phase target only, resolve the phase before selecting output paths:

```bash
gpd --raw init phase-op --include state,config "${PHASE_ARG}"
```

Require `phase_found` and actual `phase_dir`/`phase_number`. Never infer a phase
from the newest directory. Bind `TARGET_KIND`, `TARGET_FILE` when applicable,
`TARGET_FILES`, a stable ASCII `slug`, and `OUTPUT_PATH` from the caller's rules.
For file mode create `GPD/analysis/` under the invoking workspace; never write
file-target reports under `GPD/phases/**`.

Read the selected source equations/data and relevant conventions. Follow
`{GPD_INSTALL_DIR}/references/results/result-lookup-policy.md` for canonical lookup. Reuse canonical
results through `gpd result search`, then `gpd result show "{result_id}"` and,
when dependencies matter, `gpd result deps "{result_id}"`. Keep
`gpd query search` for SUMMARY/frontmatter lookup. Check a project convention
lock with `gpd --raw convention check` when applicable. Resolve conflicting
conventions before comparisons; absence of a complete lock does not erase
conventions explicitly supplied in authoritative source material.

Inspect required benchmarks, prior artifacts and contract anchors before
claiming verification. For phase targets, missing/stale/malformed or decisively
failing mandatory evidence blocks the verification report and routes to
`gpd:plan-phase {phase_number} --gaps`. Preserve diagnostic evidence without
presenting it as a passing validation artifact.

Read only the selected method reference. Execute checks appropriate to its
observable and actual failure modes; retain mandatory project checks. Record
source locations, assumptions, method, actual calculations or run receipts,
comparison criteria, discrepancies and unresolved checks. Do not fabricate
numerical runs, sources, error bars or proof. Use
`{GPD_INSTALL_DIR}/references/analysis/physics-validation-recipes.md` only for
needed specialized recipes. Proof-bearing claims retain the existing
proof-redteam gate in
`{GPD_INSTALL_DIR}/references/verification/core/proof-redteam-workflow-gate.md`;
these diagnostic checks do not independently close it. Use
`{GPD_INSTALL_DIR}/references/verification/verification-status-authority.md`
for canonical verification status vocabulary.

Write `${OUTPUT_PATH}` with target/source identity, relevant conventions,
checkable evidence, per-check status and scientific validity boundaries.
A failed check is a result, not permission to repair the source or promote a
claim silently. Report the precise discrepancy and next useful action.

File mode ends with the report: no STATE.md/state.json mutation, uncertainty
registry update or unconditional docs commit. Phase mode may use only the
caller's state-update allowance; a report does not automatically mark a phase
complete. Commit only when `commit_docs` is enabled and the operation is in
the project's normal documentation path. Review the intended diff, run
`gpd pre-commit-check --files` for exactly those paths, and stop if it fails;
then use `gpd commit --files` with those paths. Never mask failure with `|| true`.
</process>
