# Bounded GPD improvement lab

This harness evaluates one already-sealed candidate commit. It does not mutate
prompts, merge branches, install GPD, or deploy to another host.

The candidate manifest declares one hypothesis, its baseline and candidate Git
commits, allowed paths, and expected effects. The report rejects candidates that
change protected evaluators, exceed declared scope, fail a research smoke
evaluation, or fail the existing paired thinning A/B policy.

```bash
uv run python -m evals.improvement.report candidate.json \
  --repo /path/to/get-physics-done \
  --ab-results paired-results.json \
  --smoke-result theory-smoke.json \
  --smoke-result literature-smoke.json \
  --output GPD-IMPROVEMENT-REPORT.json
```

A passing report says only `eligible_for_human_review`. Promotion, installation,
and deployment remain explicit human decisions.
