<purpose>
Execute `dimensional-analysis` with the shared technical-analysis workflow.
</purpose>

<operation>
Bind `ANALYSIS_OPERATION=dimensional-analysis`.
Both phase and file targets use `OUTPUT_PATH="GPD/analysis/dimensional-{slug}.md"` in the invoking workspace; record the phase in the report. No direct shared-state update.
Read `{GPD_INSTALL_DIR}/references/analysis/dimensional-analysis-method.md` for this method.
</operation>

@{GPD_INSTALL_DIR}/workflows/technical-analysis.md
