from __future__ import annotations

import pytest
from pydantic import ValidationError

from gpd.core.evaluation import EvaluationResult, evaluation_from_oracles
from gpd.core.oracle_runner import OracleResult


def _oracle(status: str, *, oracle_id: str = "o1") -> OracleResult:
    return OracleResult(
        oracle_id=oracle_id,
        runner="python",
        check_id="5.3",
        status=status,
        passed=status == "passed",
        evidence_ids=["e1"],
        duration_seconds=0.25,
    )


def test_evaluation_from_oracles_preserves_failure_identity() -> None:
    result = evaluation_from_oracles("case", [_oracle("passed"), _oracle("failed", oracle_id="o2")], evaluator="smoke")
    assert result.status == "failed"
    assert result.passed is False
    assert result.failure_kind == "oracle_mismatch"
    assert result.critical_failures == ["o2"]
    assert result.evidence_ids == ["e1"]
    assert result.duration_seconds == 0.5


def test_evaluation_result_rejects_inconsistent_passed_flag() -> None:
    with pytest.raises(ValidationError, match="passed must be true"):
        EvaluationResult(case_id="case", evaluator="smoke", status="failed", passed=True)


def test_evaluation_result_rejects_negative_costs() -> None:
    with pytest.raises(ValidationError, match="token usage values"):
        EvaluationResult(
            case_id="case",
            evaluator="smoke",
            status="passed",
            passed=True,
            token_usage={"input": -1},
        )
