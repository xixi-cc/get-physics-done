For detailed analytical, numerical, implementation, and figure checklists,
late-load `executor.verification_flows`.

Load during `execute_tasks` when performing verification. Select relevant checks:
- **Analytical:** dimensions, symmetries, relevant limiting cases, special values, consistency with prior results
- **Numerical:** conservation laws, convergence, benchmark comparison, error bars
- **Code:** known-answer tests, regression tests, scaling, reproducibility
- **Figures:** labels+units, legends, physical reasonableness

Name the checks that can detect material errors in this result. Preserve explicit acceptance and independent-evidence gates; do not add unrelated checks to satisfy a fixed count. Recheck after changes or unresolved failures, not merely because another step elapsed.

Research log location: `GPD/phases/XX-name/{phase}-{plan}-LOG.md` --- write entries DURING execution, not after.

State tracking location: `GPD/phases/XX-name/{phase}-{plan}-STATE-TRACKING.md` --- update after each task.
