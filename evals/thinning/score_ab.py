"""Apply the predeclared GPD thinning non-inferiority and efficiency gates."""

from __future__ import annotations

import argparse
import json
import random
import statistics
from collections import defaultdict
from pathlib import Path

THEORY_DIMENSIONS = (
    "problem_representation",
    "structural_consistency",
    "derivation_depth",
    "approximation_control",
    "mechanism_explanation",
    "falsifiability",
    "exploration_quality",
    "update_capability",
)


def _mean(values: list[float]) -> float:
    return statistics.fmean(values) if values else 0.0


def _paired_rows(rows: list[dict[str, object]]) -> list[tuple[dict[str, object], dict[str, object]]]:
    grouped: dict[tuple[str, int], dict[str, dict[str, object]]] = defaultdict(dict)
    for row in rows:
        key = (str(row["task_id"]), int(row["repetition"]))
        condition = str(row["condition"])
        if condition in grouped[key]:
            raise ValueError(f"duplicate row for {key} condition {condition}")
        grouped[key][condition] = row
    pairs: list[tuple[dict[str, object], dict[str, object]]] = []
    for key, conditions in sorted(grouped.items()):
        if set(conditions) != {"baseline", "candidate"}:
            raise ValueError(f"unpaired conditions for {key}: {sorted(conditions)}")
        pairs.append((conditions["baseline"], conditions["candidate"]))
    if not pairs:
        raise ValueError("at least one paired baseline/candidate row is required")
    return pairs


def _theory_mean(row: dict[str, object]) -> float | None:
    scores = row.get("theory_scores")
    if scores is None:
        return None
    if not isinstance(scores, dict) or set(scores) != set(THEORY_DIMENSIONS):
        raise ValueError(f"invalid theory_scores for {row.get('task_id')}")
    values = [float(scores[name]) for name in THEORY_DIMENSIONS]
    if any(value < 0 or value > 4 for value in values):
        raise ValueError("theory scores must be between 0 and 4")
    return _mean(values)


def _bootstrap_lower_bound(differences: list[float], *, seed: int, draws: int = 10_000) -> float:
    if not differences:
        raise ValueError("theory comparison requires paired theory scores")
    rng = random.Random(seed)
    n = len(differences)
    estimates = sorted(_mean([differences[rng.randrange(n)] for _ in range(n)]) for _ in range(draws))
    return estimates[int(0.025 * (draws - 1))]


def score_ab(
    rows: list[dict[str, object]],
    *,
    seed: int = 1729,
    policy: str = "rapid",
) -> dict[str, object]:
    if policy not in {"rapid", "strict"}:
        raise ValueError("policy must be 'rapid' or 'strict'")
    pairs = _paired_rows(rows)
    baseline_rows = [baseline for baseline, _candidate in pairs]
    candidate_rows = [candidate for _baseline, candidate in pairs]

    zero_tolerance_failures = [
        {
            "task_id": candidate["task_id"],
            "repetition": candidate["repetition"],
            "failures": candidate.get("zero_tolerance_failures", []),
        }
        for candidate in candidate_rows
        if candidate.get("zero_tolerance_failures")
    ]
    objective_delta = _mean([float(row["objective_success"]) for row in candidate_rows]) - _mean(
        [float(row["objective_success"]) for row in baseline_rows]
    )
    safety_regressions = [
        {"task_id": baseline["task_id"], "repetition": baseline["repetition"]}
        for baseline, candidate in pairs
        if bool(baseline.get("safety_task"))
        and bool(baseline["objective_success"])
        and not bool(candidate["objective_success"])
    ]

    theory_differences: list[float] = []
    for baseline, candidate in pairs:
        baseline_theory = _theory_mean(baseline)
        candidate_theory = _theory_mean(candidate)
        if (baseline_theory is None) != (candidate_theory is None):
            raise ValueError("theory scores must be paired")
        if baseline_theory is not None and candidate_theory is not None:
            theory_differences.append(candidate_theory - baseline_theory)
    theory_delta = _mean(theory_differences) if theory_differences else None
    theory_ci_lower = (
        _bootstrap_lower_bound(theory_differences, seed=seed)
        if policy == "strict" and theory_differences
        else None
    )

    baseline_routes = sum(float(row.get("valid_routes", 0)) for row in baseline_rows)
    candidate_routes = sum(float(row.get("valid_routes", 0)) for row in candidate_rows)
    route_ratio = candidate_routes / baseline_routes if baseline_routes else 1.0
    best_route_delta = _mean([float(row.get("best_route_score", 0)) for row in candidate_rows]) - _mean(
        [float(row.get("best_route_score", 0)) for row in baseline_rows]
    )
    baseline_false_positive = sum(float(row.get("false_positive_reviews", 0)) for row in baseline_rows)
    candidate_false_positive = sum(float(row.get("false_positive_reviews", 0)) for row in candidate_rows)
    false_positive_ratio = (
        candidate_false_positive / baseline_false_positive
        if baseline_false_positive
        else (1.0 if candidate_false_positive == 0 else float("inf"))
    )

    baseline_input = sum(float(row.get("noncached_input_tokens", 0)) for row in baseline_rows)
    candidate_input = sum(float(row.get("noncached_input_tokens", 0)) for row in candidate_rows)
    input_reduction = 1.0 - candidate_input / baseline_input if baseline_input else 0.0
    baseline_orchestration = sum(
        float(row.get("spawn_count", 0)) + float(row.get("wait_count", 0)) for row in baseline_rows
    )
    candidate_orchestration = sum(
        float(row.get("spawn_count", 0)) + float(row.get("wait_count", 0)) for row in candidate_rows
    )
    orchestration_reduction = (
        1.0 - candidate_orchestration / baseline_orchestration if baseline_orchestration else 0.0
    )
    baseline_wall = sum(float(row.get("wall_seconds", 0)) for row in baseline_rows)
    candidate_wall = sum(float(row.get("wall_seconds", 0)) for row in candidate_rows)
    wall_ratio = candidate_wall / baseline_wall if baseline_wall else 1.0

    limits = (
        {
            "objective_delta": -0.02,
            "theory_delta": -0.2,
            "route_ratio": 0.9,
            "false_positive_ratio": 1.1,
            "input_reduction": 0.15,
            "orchestration_reduction": 0.25,
            "wall_ratio": 1.05,
        }
        if policy == "strict"
        else {
            "objective_delta": -0.05,
            "theory_delta": -0.35,
            "route_ratio": 0.8,
            "false_positive_ratio": 1.25,
            "input_reduction": 0.1,
            "orchestration_reduction": 0.15,
            "wall_ratio": 1.15,
        }
    )
    gates = {
        "zero_tolerance": not zero_tolerance_failures,
        "objective_noninferiority": objective_delta >= limits["objective_delta"],
        "safety_no_regression": not safety_regressions,
        "theory_mean_noninferiority": theory_delta is None or theory_delta >= limits["theory_delta"],
        "theory_ci_noninferiority": theory_ci_lower is None or theory_ci_lower >= -0.2,
        "route_diversity": route_ratio >= limits["route_ratio"],
        "best_route_quality": best_route_delta >= 0.0,
        "false_positive_review": false_positive_ratio <= limits["false_positive_ratio"],
        "efficiency_gain": (
            input_reduction >= limits["input_reduction"]
            or orchestration_reduction >= limits["orchestration_reduction"]
        ),
        "wall_time": wall_ratio <= limits["wall_ratio"],
    }
    return {
        "schema_version": "gpd.thinning-ab-score.v1",
        "policy": policy,
        "decision": "pass" if all(gates.values()) else "reject",
        "pair_count": len(pairs),
        "gates": gates,
        "metrics": {
            "objective_delta": objective_delta,
            "theory_delta": theory_delta,
            "theory_bootstrap_95pct_lower": theory_ci_lower,
            "valid_route_ratio": route_ratio,
            "best_route_score_delta": best_route_delta,
            "false_positive_review_ratio": false_positive_ratio,
            "noncached_input_reduction": input_reduction,
            "spawn_wait_reduction": orchestration_reduction,
            "wall_time_ratio": wall_ratio,
        },
        "zero_tolerance_failures": zero_tolerance_failures,
        "safety_regressions": safety_regressions,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("results", type=Path, help="JSON array of paired reviewed run rows")
    parser.add_argument("--seed", type=int, default=1729)
    parser.add_argument("--policy", choices=("rapid", "strict"), default="rapid")
    args = parser.parse_args()
    rows = json.loads(args.results.read_text(encoding="utf-8"))
    if not isinstance(rows, list):
        raise ValueError("results must be a JSON array")
    print(json.dumps(score_ab(rows, seed=args.seed, policy=args.policy), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
