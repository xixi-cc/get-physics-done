"""Validation and leakage checks for the first thinning capability canary."""

from __future__ import annotations

import json
from pathlib import Path

from evals.thinning.prepare_bundle import (
    EXPECTED_CANARY_COUNTS,
    EXPECTED_MATRIX_COUNTS,
    prepare_bundle,
    validate_fixture,
)

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "evals" / "thinning" / "fixtures" / "canary-v1"
MATRIX_FIXTURE = ROOT / "evals" / "thinning" / "fixtures" / "matrix-v1"


def test_canary_fixture_has_planned_category_mix_and_private_pairing() -> None:
    public, private = validate_fixture(FIXTURE)

    assert len(public) == len(private) == 12
    assert sum(EXPECTED_CANARY_COUNTS.values()) == 12
    assert {row["id"] for row in public} == {row["task_id"] for row in private}
    assert sum(bool(row["theory_rubric"]) for row in private) == 3


def test_prepared_bundle_contains_no_private_oracle(tmp_path: Path) -> None:
    bundle = tmp_path / "run-bundle"
    manifest = prepare_bundle(FIXTURE, bundle)

    assert manifest["private_oracles_included"] is False
    assert sorted(path.name for path in bundle.iterdir()) == ["manifest.json", "tasks.jsonl"]
    bundled = (bundle / "tasks.jsonl").read_text(encoding="utf-8")
    private = (FIXTURE / "private-oracles.jsonl").read_text(encoding="utf-8")
    assert "expected_findings" not in bundled
    assert "forbidden_outcomes" not in bundled
    assert private not in bundled


def test_theory_rubric_has_all_eight_dimensions_and_zero_tolerance_gate() -> None:
    rubric = json.loads((ROOT / "evals" / "thinning" / "theory-rubric.json").read_text(encoding="utf-8"))

    assert len(rubric["dimensions"]) == 8
    assert rubric["scale"] == {"minimum": 0, "maximum": 4}
    assert rubric["quality_rules"]["answer_length_is_not_a_dimension"] is True
    assert "missed_load_bearing_error" in rubric["zero_tolerance"]


def test_full_matrix_has_all_48_tasks_and_planned_sections() -> None:
    public, private = validate_fixture(MATRIX_FIXTURE)

    assert len(public) == len(private) == 48
    assert sum(EXPECTED_MATRIX_COUNTS.values()) == 48
    assert len({row["id"] for row in public}) == 48
    assert sum(bool(row["theory_rubric"]) for row in private) == 10


def test_full_matrix_bundle_still_excludes_private_oracles(tmp_path: Path) -> None:
    bundle = tmp_path / "matrix-run"
    manifest = prepare_bundle(MATRIX_FIXTURE, bundle)

    assert manifest["task_count"] == 48
    assert manifest["private_oracles_included"] is False
    content = (bundle / "tasks.jsonl").read_text(encoding="utf-8")
    assert "expected_findings" not in content
    assert "forbidden_outcomes" not in content
