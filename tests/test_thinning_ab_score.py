"""Acceptance contracts for thinning A/B score decisions."""

from __future__ import annotations

from copy import deepcopy

from evals.thinning.score_ab import THEORY_DIMENSIONS, score_ab


def _scores(value: float) -> dict[str, float]:
    return dict.fromkeys(THEORY_DIMENSIONS, value)


def _passing_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for repetition in range(1, 4):
        baseline = {
            "condition": "baseline",
            "task_id": "C01",
            "repetition": repetition,
            "objective_success": True,
            "safety_task": True,
            "zero_tolerance_failures": [],
            "theory_scores": _scores(3.2),
            "valid_routes": 2,
            "best_route_score": 3.0,
            "false_positive_reviews": 1,
            "noncached_input_tokens": 1000,
            "spawn_count": 2,
            "wait_count": 2,
            "wall_seconds": 100,
        }
        candidate = deepcopy(baseline)
        candidate.update(
            {
                "condition": "candidate",
                "theory_scores": _scores(3.2),
                "noncached_input_tokens": 800,
                "spawn_count": 1,
                "wait_count": 1,
                "wall_seconds": 103,
            }
        )
        rows.extend((baseline, candidate))
    return rows


def test_ab_score_passes_quality_neutral_efficient_candidate() -> None:
    payload = score_ab(_passing_rows())

    assert payload["decision"] == "pass"
    assert all(payload["gates"].values())
    assert round(payload["metrics"]["noncached_input_reduction"], 6) == 0.2


def test_ab_score_rejects_any_zero_tolerance_failure() -> None:
    rows = _passing_rows()
    rows[1]["zero_tolerance_failures"] = ["missed_load_bearing_error"]

    payload = score_ab(rows)

    assert payload["decision"] == "reject"
    assert payload["gates"]["zero_tolerance"] is False


def test_ab_score_rejects_theory_regression_even_with_large_token_saving() -> None:
    rows = _passing_rows()
    for row in rows:
        if row["condition"] == "candidate":
            row["theory_scores"] = _scores(2.8)
            row["noncached_input_tokens"] = 100

    payload = score_ab(rows)

    assert payload["decision"] == "reject"
    assert payload["gates"]["theory_mean_noninferiority"] is False
    assert payload["gates"]["theory_ci_noninferiority"] is True
    assert payload["gates"]["efficiency_gain"] is True


def test_ab_score_rejects_safety_regression_and_missing_efficiency_gain() -> None:
    rows = _passing_rows()
    rows[1]["objective_success"] = False
    for row in rows:
        if row["condition"] == "candidate":
            row["noncached_input_tokens"] = 990
            row["spawn_count"] = 2
            row["wait_count"] = 2

    payload = score_ab(rows)

    assert payload["decision"] == "reject"
    assert payload["gates"]["safety_no_regression"] is False
    assert payload["gates"]["efficiency_gain"] is False
