from __future__ import annotations

import json
from pathlib import Path

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
    assert result["evaluation"]["status"] == "failed"
    assert result["evaluation"]["failure_kind"] == "oracle_mismatch"


def test_external_candidate_submission_is_evaluated(tmp_path: Path) -> None:
    source = Path("evals/research_smoke/capsules/theory-limit-recovery/reference.json")
    candidate = tmp_path / "candidate.json"
    candidate.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")

    result = run_capsule("theory-limit-recovery", variant="candidate", submission_path=candidate)

    assert result["variant"] == "candidate"
    assert result["passed"] is True
    assert result["evaluation"]["status"] == "passed"
    assert result["evaluation"]["artifact_paths"] == [str(candidate.resolve())]


def test_external_candidate_requires_manifest_fields(tmp_path: Path) -> None:
    candidate = tmp_path / "candidate.json"
    candidate.write_text(json.dumps({"corrected_zero_mode": 0.0}), encoding="utf-8")

    with pytest.raises(ValueError, match="submission misses required fields"):
        run_capsule("theory-limit-recovery", variant="candidate", submission_path=candidate)
