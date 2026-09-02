# Research smoke capsules

These four small fixtures exercise representative GPD research seams. They are
not a broad scientific leaderboard. Each capsule freezes a task, a passing
reference submission, a representative adversarial submission, and one or more
typed executable oracles.

Run the passing fixtures:

```bash
uv run python -m evals.research_smoke.run
```

Confirm that a capsule rejects its adversarial fixture:

```bash
uv run python -m evals.research_smoke.run theory-limit-recovery --variant adversarial
```

The runner exits zero only when every selected submission passes. Candidate
agents should emit the same JSON shapes as the fixture submissions and can be
evaluated directly:

```bash
uv run python -m evals.research_smoke.run theory-limit-recovery \
  --submission /path/to/candidate.json \
  --result-output /path/to/evaluation.json
```

The manifest checks the capsule's required top-level fields before invoking its
typed oracles. Candidate files remain read-only inputs and the result includes a
shared `gpd.evaluation-result.v1` envelope.
