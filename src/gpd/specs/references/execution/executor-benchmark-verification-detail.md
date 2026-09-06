## Verify Benchmark Values Protocol

Before using any numerical benchmark as ground truth, record source, exact value, units, uncertainty, and convention. Treat values from model memory/training data as `[UNVERIFIED - training data]`, reduce confidence by one level, and surface them for independent verification.

For benchmark provenance, convergence reports, reproducibility metadata, and
numerical failure triage, late-load `executor.numerical_protocol`.
