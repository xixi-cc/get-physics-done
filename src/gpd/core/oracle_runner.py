"""Narrow executable oracle layer for GPD verification checks."""

from __future__ import annotations

import importlib
import json
import math
import subprocess
import sys
import time
from pathlib import Path
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter, field_validator, model_validator

from gpd.core.research_evidence import ClaimEvidenceLink, ResearchEvidence, verification_evidence_to_evidence

__all__ = [
    "PythonOracleSpec",
    "PytestOracleSpec",
    "NumericToleranceOracleSpec",
    "OracleSpec",
    "OracleResult",
    "load_oracle_spec",
    "run_oracle",
    "run_oracle_file",
    "oracle_result_to_evidence",
]


OracleStatus = Literal["passed", "failed", "error"]


def _required_text(value: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise ValueError("must not be blank")
    return normalized


class _OracleSpecBase(BaseModel):
    model_config = ConfigDict(extra="forbid")

    oracle_id: str
    check_id: str
    claim_id: str | None = None
    acceptance_test_id: str | None = None
    evidence_ids: list[str] = Field(default_factory=list)

    @field_validator("oracle_id", "check_id", mode="before")
    @classmethod
    def _normalize_required(cls, value: str) -> str:
        return _required_text(value)


class PythonOracleSpec(_OracleSpecBase):
    """Call an importable project function returning bool, tuple, or result dict."""

    runner: Literal["python"] = "python"
    callable_ref: str
    args: list[object] = Field(default_factory=list)
    kwargs: dict[str, object] = Field(default_factory=dict)

    @field_validator("callable_ref", mode="before")
    @classmethod
    def _normalize_callable_ref(cls, value: str) -> str:
        normalized = _required_text(value)
        if ":" not in normalized:
            raise ValueError("callable_ref must use 'module:function'")
        return normalized


class PytestOracleSpec(_OracleSpecBase):
    """Run one or more explicitly named pytest nodes."""

    runner: Literal["pytest"] = "pytest"
    tests: list[str]
    extra_args: list[str] = Field(default_factory=list)
    timeout_seconds: float = 120.0

    @field_validator("tests")
    @classmethod
    def _require_tests(cls, value: list[str]) -> list[str]:
        normalized = [_required_text(item) for item in value]
        if not normalized:
            raise ValueError("tests must contain at least one pytest node")
        return normalized


NumericValue = float | list[float]


class NumericToleranceOracleSpec(_OracleSpecBase):
    """Compare a scalar or flat numeric sequence with explicit tolerances."""

    runner: Literal["numeric-tolerance"] = "numeric-tolerance"
    observed: NumericValue
    expected: NumericValue
    atol: float = 0.0
    rtol: float = 1e-7

    @model_validator(mode="after")
    def _validate_shape_and_tolerances(self) -> NumericToleranceOracleSpec:
        if self.atol < 0 or self.rtol < 0:
            raise ValueError("atol and rtol must be non-negative")
        if isinstance(self.observed, list) != isinstance(self.expected, list):
            raise ValueError("observed and expected must both be scalars or both be lists")
        if isinstance(self.observed, list) and isinstance(self.expected, list):
            if not self.observed:
                raise ValueError("numeric lists must not be empty")
            if len(self.observed) != len(self.expected):
                raise ValueError("observed and expected lists must have equal length")
        return self


OracleSpec = Annotated[
    PythonOracleSpec | PytestOracleSpec | NumericToleranceOracleSpec,
    Field(discriminator="runner"),
]
_ORACLE_SPEC_ADAPTER = TypeAdapter(OracleSpec)


class OracleResult(BaseModel):
    """Machine result linked to the scientific claim and canonical check."""

    model_config = ConfigDict(extra="forbid")

    oracle_id: str
    runner: Literal["python", "pytest", "numeric-tolerance"]
    check_id: str
    status: OracleStatus
    passed: bool
    claim_id: str | None = None
    acceptance_test_id: str | None = None
    observed: object | None = None
    expected: object | None = None
    evidence_ids: list[str] = Field(default_factory=list)
    details: str | None = None
    duration_seconds: float = 0.0

    def claim_link(self, evidence: ResearchEvidence) -> ClaimEvidenceLink | None:
        if self.claim_id is None or self.status == "error":
            return None
        return ClaimEvidenceLink(claim_id=self.claim_id, evidence_id=evidence.id, relation="supports" if self.passed else "contradicts")


def load_oracle_spec(path: Path) -> OracleSpec:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return _ORACLE_SPEC_ADAPTER.validate_python(payload)


def _base_result(spec: _OracleSpecBase, *, status: OracleStatus, passed: bool, started: float, **kwargs: object) -> OracleResult:
    return OracleResult(
        oracle_id=spec.oracle_id,
        runner=spec.runner,
        check_id=spec.check_id,
        status=status,
        passed=passed,
        claim_id=spec.claim_id,
        acceptance_test_id=spec.acceptance_test_id,
        evidence_ids=list(spec.evidence_ids),
        duration_seconds=max(0.0, time.monotonic() - started),
        **kwargs,
    )


def _run_numeric(spec: NumericToleranceOracleSpec, *, started: float) -> OracleResult:
    observed = spec.observed if isinstance(spec.observed, list) else [spec.observed]
    expected = spec.expected if isinstance(spec.expected, list) else [spec.expected]
    comparisons = [math.isclose(left, right, abs_tol=spec.atol, rel_tol=spec.rtol) for left, right in zip(observed, expected, strict=True)]
    max_abs_error = max(abs(left - right) for left, right in zip(observed, expected, strict=True))
    passed = all(comparisons)
    return _base_result(
        spec,
        status="passed" if passed else "failed",
        passed=passed,
        started=started,
        observed=spec.observed,
        expected={"value": spec.expected, "atol": spec.atol, "rtol": spec.rtol},
        details=f"max_abs_error={max_abs_error:.12g}",
    )


def _run_python(spec: PythonOracleSpec, *, cwd: Path, started: float) -> OracleResult:
    module_name, function_name = spec.callable_ref.split(":", 1)
    inserted_path = str(cwd.resolve())
    added_to_path = inserted_path not in sys.path
    try:
        if added_to_path:
            sys.path.insert(0, inserted_path)
        function = getattr(importlib.import_module(module_name), function_name)
        raw = function(*spec.args, **spec.kwargs)
        if isinstance(raw, bool):
            passed, observed, expected, details = raw, raw, True, None
        elif isinstance(raw, tuple) and len(raw) == 2:
            passed, observed = bool(raw[0]), raw[1]
            expected, details = None, None
        elif isinstance(raw, dict) and "passed" in raw:
            if type(raw["passed"]) is not bool:
                raise TypeError("python oracle result field 'passed' must be a boolean")
            passed = raw["passed"]
            observed = raw.get("observed")
            expected = raw.get("expected")
            details = str(raw["details"]) if raw.get("details") is not None else None
        else:
            raise TypeError("python oracle must return bool, (bool, observed), or a dict containing 'passed'")
    except Exception as exc:  # noqa: BLE001 - execution failures are data, not process failures
        return _base_result(spec, status="error", passed=False, started=started, details=f"{type(exc).__name__}: {exc}")
    finally:
        if added_to_path and inserted_path in sys.path:
            sys.path.remove(inserted_path)
    return _base_result(
        spec,
        status="passed" if passed else "failed",
        passed=passed,
        started=started,
        observed=observed,
        expected=expected,
        details=details,
    )


def _run_pytest(spec: PytestOracleSpec, *, cwd: Path, started: float) -> OracleResult:
    command = [sys.executable, "-m", "pytest", "-q", "-n", "0", "--capture=no", *spec.extra_args, *spec.tests]
    try:
        completed = subprocess.run(
            command,
            cwd=cwd,
            text=True,
            capture_output=True,
            timeout=spec.timeout_seconds,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return _base_result(spec, status="error", passed=False, started=started, details=f"{type(exc).__name__}: {exc}")
    passed = completed.returncode == 0
    output = "\n".join(part.strip() for part in (completed.stdout, completed.stderr) if part.strip())
    return _base_result(
        spec,
        status="passed" if passed else "failed",
        passed=passed,
        started=started,
        observed={"returncode": completed.returncode},
        expected={"returncode": 0},
        details=output[-4000:] or None,
    )


def run_oracle(spec: OracleSpec, *, cwd: Path | None = None) -> OracleResult:
    """Execute exactly one typed oracle specification."""

    started = time.monotonic()
    if isinstance(spec, NumericToleranceOracleSpec):
        return _run_numeric(spec, started=started)
    if isinstance(spec, PythonOracleSpec):
        return _run_python(spec, cwd=(cwd or Path.cwd()), started=started)
    return _run_pytest(spec, cwd=(cwd or Path.cwd()), started=started)


def run_oracle_file(path: Path, *, cwd: Path | None = None) -> OracleResult:
    return run_oracle(load_oracle_spec(path), cwd=cwd)


def oracle_result_to_evidence(result: OracleResult, *, result_path: str) -> tuple[ResearchEvidence, ClaimEvidenceLink | None]:
    """Bridge one executable result back into the shared evidence protocol."""

    from gpd.contracts import VerificationEvidence

    legacy = VerificationEvidence(
        verifier=f"oracle:{result.runner}",
        method=result.check_id,
        confidence="high" if result.status in {"passed", "failed"} else "unreliable",
        evidence_path=result_path,
        notes=result.details,
        claim_id=result.claim_id,
        acceptance_test_id=result.acceptance_test_id,
    )
    evidence = verification_evidence_to_evidence(legacy, evidence_id=f"oracle:{result.oracle_id}")
    return evidence, result.claim_link(evidence)
