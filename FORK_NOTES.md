# Research fork notes

This fork is used in active physics-research workflows on two machines. It is
not a renamed mirror of upstream: the `gpd-research-improvements` branch records
a locally developed and tested set of changes aimed at reducing orchestration
overhead while preserving scientific verification boundaries.

## What changed

- Consolidated overlapping research roles and added risk-triggered routing so
  routine work stays in the main research context while load-bearing theory,
  proof, and consistency checks retain independent review.
- Added a lean Codex skill projection. Commands remain available explicitly,
  while only the core workflow surface is automatically discovered.
- Added prompt-BOM and privacy-bounded session tracing utilities for measuring
  model-visible context, tool activity, and thinning regressions.
- Added a shared `ResearchEvidence` protocol with compatibility adapters for
  citations, verification evidence, and authoring claims.
- Added Python, pytest, and numeric-tolerance oracle runners, with real
  literature-review and verifier workflow integrations.
- Added four executable research smoke capsules covering theory-limit recovery,
  numerical convergence, claim-level literature evidence, and state recovery.

The evidence/oracle design is documented in
[`docs/research-evidence-and-oracles.md`](docs/research-evidence-and-oracles.md).
The executable fixtures are documented in
[`evals/research_smoke/README.md`](evals/research_smoke/README.md).

## Verification performed

The deployed source tree corresponding to development commit `c0e7f0f` was
validated on 2026-09-02 before this presentation branch was prepared.

| Environment | Verification | Result |
| --- | --- | --- |
| Local WSL development host | Complete pytest suite with network-only tests disabled | 12,989 passed, 17 skipped |
| Local WSL development host | Ruff on changed Python files and `git diff --check` | Passed |
| Local WSL development host | Four reference smoke capsules | 4/4 accepted |
| Local WSL development host | Four adversarial smoke capsules | 4/4 rejected |
| `office-ubuntu` | Focused evidence/oracle/workflow test set | 25 passed |
| `office-ubuntu` | Reference smoke capsules | 4/4 accepted |
| Both hosts | Codex global install, lean projection | 20 agents, 71 commands |

The full-suite skips were deliberate network exclusions, not converted into
passes. The remote focused run does not claim to be a second complete-suite
run. GitHub Actions provides an additional clean-environment check for this
branch.

## Reproduce the focused checks

```bash
uv sync --dev
TEMP=/tmp TMP=/tmp GPD_ARXIV_NO_NETWORK=1 uv run pytest -n 0 --capture=no -q \
  tests/core/test_research_evidence.py \
  tests/core/test_oracle_runner.py \
  tests/core/test_research_evidence_workflow_seams.py \
  tests/test_evidence_oracle_cli.py \
  tests/test_research_smoke_capsules.py \
  tests/test_literature_review_typed_routing.py
uv run python -m evals.research_smoke.run
```

To confirm the smoke fixtures reject representative bad outputs:

```bash
uv run python -m evals.research_smoke.run --variant adversarial
```

The final command is expected to exit nonzero because all four adversarial
submissions are rejected.

## Deployment status

The validated candidate is installed with the lean Codex projection on the
local WSL host and on `office-ubuntu`. Existing in-flight Codex processes were
not terminated during deployment; newly started tasks load the updated global
installation.

This document reports engineering validation and deployment evidence. It does
not claim that a passing oracle establishes scientific truth beyond the check
encoded by that oracle.
