from __future__ import annotations

import json
import subprocess
from copy import deepcopy
from pathlib import Path

from evals.improvement.report import CandidateManifest, build_improvement_report
from evals.thinning.score_ab import THEORY_DIMENSIONS
from gpd.core.evaluation import EvaluationResult


def _git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args],
        cwd=repo,
        text=True,
        capture_output=True,
        check=True,
    ).stdout.strip()


def _repo_with_candidate(tmp_path: Path, changed_path: str = "src/gpd/agents/planner.md") -> tuple[Path, str, str]:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init")
    _git(repo, "config", "user.email", "test@example.com")
    _git(repo, "config", "user.name", "Test")
    path = repo / changed_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("baseline\n", encoding="utf-8")
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "baseline")
    baseline = _git(repo, "rev-parse", "HEAD")
    path.write_text("candidate\n", encoding="utf-8")
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "candidate")
    return repo, baseline, _git(repo, "rev-parse", "HEAD")


def _passing_rows() -> list[dict[str, object]]:
    baseline = {
        "condition": "baseline",
        "task_id": "C01",
        "repetition": 1,
        "objective_success": True,
        "safety_task": True,
        "zero_tolerance_failures": [],
        "theory_scores": dict.fromkeys(THEORY_DIMENSIONS, 3.2),
        "valid_routes": 2,
        "best_route_score": 3.0,
        "false_positive_reviews": 0,
        "noncached_input_tokens": 1000,
        "spawn_count": 2,
        "wait_count": 2,
        "wall_seconds": 100,
    }
    candidate = deepcopy(baseline)
    candidate.update(
        {
            "condition": "candidate",
            "noncached_input_tokens": 800,
            "spawn_count": 1,
            "wait_count": 1,
            "wall_seconds": 100,
        }
    )
    return [baseline, candidate]


def _smoke_result(tmp_path: Path, *, passed: bool = True) -> Path:
    case_ids = (
        "literature-evidence",
        "numerical-convergence",
        "state-recovery",
        "theory-limit-recovery",
    )
    results = [
        {
            "evaluation": EvaluationResult(
                case_id=case_id,
                evaluator="research-smoke",
                status="failed" if not passed and case_id == "theory-limit-recovery" else "passed",
                passed=passed or case_id != "theory-limit-recovery",
                critical_failures=["theory-audit"] if not passed and case_id == "theory-limit-recovery" else [],
            ).model_dump(mode="json")
        }
        for case_id in case_ids
    ]
    path = tmp_path / "smoke.json"
    path.write_text(json.dumps(results), encoding="utf-8")
    return path


def test_candidate_becomes_eligible_only_for_human_review(tmp_path: Path) -> None:
    repo, baseline, candidate = _repo_with_candidate(tmp_path)
    manifest = CandidateManifest(
        candidate_id="planner-001",
        baseline_sha=baseline,
        candidate_sha=candidate,
        hypothesis="A smaller planner preserves quality.",
        allowed_paths=["src/gpd/agents"],
        expected_effects=["reduce_noncached_input_tokens"],
    )

    report = build_improvement_report(
        manifest,
        repo=repo,
        ab_rows=_passing_rows(),
        smoke_result_paths=[_smoke_result(tmp_path)],
    )

    assert report.decision == "eligible_for_human_review"
    assert report.promotion_requires_human_approval is True
    assert all(report.gates.values())


def test_candidate_is_rejected_when_declared_scope_is_exceeded(tmp_path: Path) -> None:
    repo, baseline, candidate = _repo_with_candidate(tmp_path, "src/gpd/core/state.py")
    manifest = CandidateManifest(
        candidate_id="planner-002",
        baseline_sha=baseline,
        candidate_sha=candidate,
        hypothesis="Planner-only change.",
        allowed_paths=["src/gpd/agents"],
        expected_effects=["reduce_tokens"],
    )

    report = build_improvement_report(
        manifest,
        repo=repo,
        ab_rows=_passing_rows(),
        smoke_result_paths=[_smoke_result(tmp_path)],
    )

    assert report.decision == "reject"
    assert report.gates["declared_scope_respected"] is False
    assert report.out_of_scope_paths == ["src/gpd/core/state.py"]


def test_candidate_cannot_change_its_evaluator(tmp_path: Path) -> None:
    repo, baseline, candidate = _repo_with_candidate(tmp_path, "evals/thinning/score_ab.py")
    manifest = CandidateManifest(
        candidate_id="gaming-001",
        baseline_sha=baseline,
        candidate_sha=candidate,
        hypothesis="Change the score.",
        allowed_paths=["evals/thinning/score_ab.py"],
        expected_effects=["pass"],
    )

    report = build_improvement_report(
        manifest,
        repo=repo,
        ab_rows=_passing_rows(),
        smoke_result_paths=[_smoke_result(tmp_path)],
    )

    assert report.decision == "reject"
    assert report.gates["evaluator_integrity"] is False
    assert report.protected_evaluator_changes == ["evals/thinning/score_ab.py"]


def test_candidate_requires_all_four_smoke_cases(tmp_path: Path) -> None:
    repo, baseline, candidate = _repo_with_candidate(tmp_path)
    manifest = CandidateManifest(
        candidate_id="planner-003",
        baseline_sha=baseline,
        candidate_sha=candidate,
        hypothesis="A smaller planner preserves quality.",
        allowed_paths=["src/gpd/agents"],
        expected_effects=["reduce_tokens"],
    )
    incomplete = tmp_path / "incomplete-smoke.json"
    incomplete.write_text(
        EvaluationResult(
            case_id="theory-limit-recovery",
            evaluator="research-smoke",
            status="passed",
            passed=True,
        ).model_dump_json(),
        encoding="utf-8",
    )

    report = build_improvement_report(
        manifest,
        repo=repo,
        ab_rows=_passing_rows(),
        smoke_result_paths=[incomplete],
    )

    assert report.decision == "reject"
    assert report.gates["required_smoke_cases_present_once"] is False
