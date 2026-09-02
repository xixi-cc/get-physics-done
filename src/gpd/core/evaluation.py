"""Small shared result envelope for GPD evaluation harnesses."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from gpd.core.oracle_runner import OracleResult


class EvaluationResult(BaseModel):
    """One evaluator verdict without coupling task definitions to one harness."""

    model_config = ConfigDict(extra="forbid")

    schema_version: Literal["gpd.evaluation-result.v1"] = "gpd.evaluation-result.v1"
    case_id: str
    evaluator: str
    status: Literal["passed", "failed", "error", "inconclusive"]
    passed: bool
    critical_failures: list[str] = Field(default_factory=list)
    quality_dimensions: dict[str, float] = Field(default_factory=dict)
    observed: object | None = None
    expected: object | None = None
    evidence_ids: list[str] = Field(default_factory=list)
    failure_kind: str | None = None
    duration_seconds: float = 0.0
    token_usage: dict[str, int] | None = None
    artifact_paths: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def _validate_verdict(self) -> EvaluationResult:
        if self.passed != (self.status == "passed"):
            raise ValueError("passed must be true exactly when status is 'passed'")
        if self.duration_seconds < 0:
            raise ValueError("duration_seconds must be non-negative")
        if any(value < 0 for value in self.quality_dimensions.values()):
            raise ValueError("quality dimension values must be non-negative")
        if self.token_usage is not None and any(value < 0 for value in self.token_usage.values()):
            raise ValueError("token usage values must be non-negative")
        return self


def evaluation_from_oracles(
    case_id: str,
    results: list[OracleResult],
    *,
    evaluator: str,
    artifact_paths: list[str] | None = None,
) -> EvaluationResult:
    """Aggregate typed oracle results while preserving their detailed payloads."""

    if not results:
        raise ValueError("evaluation requires at least one oracle result")
    errors = [result.oracle_id for result in results if result.status == "error"]
    failures = [result.oracle_id for result in results if result.status == "failed"]
    if errors:
        status = "error"
        failure_kind = "oracle_execution"
    elif failures:
        status = "failed"
        failure_kind = "oracle_mismatch"
    else:
        status = "passed"
        failure_kind = None
    evidence_ids = list(dict.fromkeys(evidence_id for result in results for evidence_id in result.evidence_ids))
    return EvaluationResult(
        case_id=case_id,
        evaluator=evaluator,
        status=status,
        passed=status == "passed",
        critical_failures=[*errors, *failures],
        observed=[result.model_dump(mode="json") for result in results],
        evidence_ids=evidence_ids,
        failure_kind=failure_kind,
        duration_seconds=sum(result.duration_seconds for result in results),
        artifact_paths=artifact_paths or [],
    )
