## External Tool Failure Protocol

When a computation crashes, a library is unavailable, or code produces `NaN`/`Inf`, classify first: environment gate, physics/convention bug, numerical convergence issue, or hard blocker.

Never silently replace `NaN` with zero, catch and ignore numerical exceptions, skip a failing computation, or proceed with placeholder results. After 3 failed fix attempts for the same numerical or tool failure, escalate to Deviation Rule 5.

For detailed symptom tables and artifact-specific recovery, late-load
`executor.tool_preflight`; for numerical failure triage, late-load
`executor.numerical_protocol`.
