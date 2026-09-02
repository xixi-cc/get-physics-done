from __future__ import annotations

import pytest

from evals.research_smoke.run import run_capsule

CAPSULE_IDS = (
    "theory-limit-recovery",
    "numerical-convergence",
    "literature-evidence",
    "state-recovery",
)


@pytest.mark.parametrize("capsule_id", CAPSULE_IDS)
def test_reference_research_smoke_submission_passes(capsule_id: str) -> None:
    result = run_capsule(capsule_id, variant="reference")
    assert result["passed"] is True


@pytest.mark.parametrize("capsule_id", CAPSULE_IDS)
def test_adversarial_research_smoke_submission_is_rejected(capsule_id: str) -> None:
    result = run_capsule(capsule_id, variant="adversarial")
    assert result["passed"] is False
