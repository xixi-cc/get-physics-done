<purpose>
Execute `sensitivity-analysis` with the shared technical-analysis workflow.
</purpose>

<operation>
Bind `ANALYSIS_OPERATION=sensitivity-analysis`.
Phase target: `OUTPUT_PATH="${phase_dir}/SENSITIVITY-REPORT.md"`.
File target: `OUTPUT_PATH="GPD/analysis/sensitivity-{slug}.md"`.
No shared-state update except the scoped uncertainty operation below.
Read `{GPD_INSTALL_DIR}/references/analysis/sensitivity-analysis-method.md` for this method.

Only if `state_exists` and `phase_found` are true, the target is phase-backed,
and justified uncertainties were actually computed, use:
```bash
gpd uncertainty add "{target quantity}" --value "{nominal_value}" --uncertainty "{total_uncertainty}" --phase "{phase_number}" --method "sensitivity-analysis"
```
Include actual significant contributions without inventing missing uncertainties.
`REPORT_PATH` is the same resolved path as `OUTPUT_PATH`; include changed state
files in the normal phase documentation commit only when this update occurred.
</operation>

@{GPD_INSTALL_DIR}/workflows/technical-analysis.md
