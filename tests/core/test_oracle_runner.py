from __future__ import annotations

from pathlib import Path

from gpd.core.oracle_runner import (
    NumericToleranceOracleSpec,
    PytestOracleSpec,
    PythonOracleSpec,
    oracle_result_to_evidence,
    run_oracle,
)
from gpd.core.verification_checks import get_verification_check


def test_numeric_tolerance_oracle_reports_observed_error() -> None:
    result = run_oracle(
        NumericToleranceOracleSpec(
            oracle_id="numeric-limit",
            check_id="5.3",
            claim_id="claim-limit",
            observed=[1.0, 2.01],
            expected=[1.0, 2.0],
            atol=0.02,
        )
    )
    assert result.passed is True
    assert result.status == "passed"
    assert "max_abs_error=" in (result.details or "")


def test_python_oracle_calls_importable_function() -> None:
    result = run_oracle(
        PythonOracleSpec(
            oracle_id="finite",
            check_id="5.8",
            callable_ref="math:isfinite",
            args=[3.0],
        )
    )
    assert result.passed is True
    assert result.observed is True


def test_python_oracle_turns_execution_failure_into_error_result() -> None:
    result = run_oracle(
        PythonOracleSpec(
            oracle_id="bad-call",
            check_id="5.8",
            callable_ref="math:does_not_exist",
        )
    )
    assert result.status == "error"
    assert "AttributeError" in (result.details or "")
    evidence, link = oracle_result_to_evidence(result, result_path="GPD/verification/error.json")
    assert evidence.id == "oracle:bad-call"
    assert link is None


def test_python_oracle_imports_project_callable_from_explicit_cwd(tmp_path: Path) -> None:
    (tmp_path / "project_checks.py").write_text(
        "def check_limit(value):\n    return {'passed': abs(value) < 1e-9, 'observed': value, 'expected': 0.0}\n",
        encoding="utf-8",
    )
    result = run_oracle(
        PythonOracleSpec(
            oracle_id="project-limit",
            check_id="5.3",
            callable_ref="project_checks:check_limit",
            args=[1e-12],
        ),
        cwd=tmp_path,
    )
    assert result.passed is True
    assert result.expected == 0.0


def test_pytest_oracle_runs_explicit_node(tmp_path: Path) -> None:
    test_file = tmp_path / "test_capsule.py"
    test_file.write_text("def test_known_limit():\n    assert abs((2.0 / 4.0) - 0.5) < 1e-12\n", encoding="utf-8")
    result = run_oracle(
        PytestOracleSpec(
            oracle_id="pytest-limit",
            check_id="5.16",
            tests=["test_capsule.py::test_known_limit"],
        ),
        cwd=tmp_path,
    )
    assert result.passed is True
    assert result.observed == {"returncode": 0}


def test_oracle_result_bridges_back_to_claim_evidence() -> None:
    result = run_oracle(
        NumericToleranceOracleSpec(
            oracle_id="benchmark",
            check_id="5.16",
            claim_id="claim-benchmark",
            acceptance_test_id="test-benchmark",
            observed=0.501,
            expected=0.5,
            atol=0.01,
        )
    )
    evidence, link = oracle_result_to_evidence(result, result_path="GPD/verification/benchmark.json")
    assert evidence.id == "oracle:benchmark"
    assert evidence.locator.source == "GPD/verification/benchmark.json"
    assert link is not None
    assert link.claim_id == "claim-benchmark"
    assert link.relation == "supports"


def test_verification_registry_exposes_supported_runner_types() -> None:
    benchmark = get_verification_check("5.16")
    assert benchmark is not None
    assert benchmark.oracle_runners == ["python", "pytest", "numeric-tolerance"]

    literature = get_verification_check("5.6")
    assert literature is not None
    assert literature.oracle_runners == []
