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
agents should emit the same JSON shapes as the fixture submissions; replacing a
fixture with a recorded candidate artifact is deliberately left to the existing
A/B bundle preparation layer.
