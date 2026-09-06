# numerical-convergence

Identify observable, algorithm, numerical controls, expected order and benchmark.
A converged wrong benchmark is not a valid result; stop that claim and diagnose.
Check applicable conservation laws, residuals, stability and physicality.
Use enough refinement levels to establish the claimed convergence/order; three
levels are needed to estimate an unknown power from successive differences,
unless independent evidence provides a valid alternative. Separate independent
controls and check coupled limits. Use Richardson extrapolation only in its
asymptotic regime; monotonic change alone does not establish the right limit.
Separate discretization, truncation, statistical, roundoff, approximation and
model errors, accounting for correlation where relevant. Record actual run
configuration, precision, seeds/sample dependence, measured order and tolerance.
Classify converged, insufficient evidence, discrepant or unstable against the
stated criterion; no universal letter grade substitutes for an error estimate.
