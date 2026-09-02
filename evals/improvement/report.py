"""Build an auditable promotion report for one sealed GPD candidate."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from evals.thinning.score_ab import score_ab
from gpd.core.evaluation import EvaluationResult

PROTECTED_EVALUATOR_PATHS = (
    "evals/improvement/",
    "evals/thinning/fixtures/",
    "evals/thinning/score_ab.py",
    "evals/research_smoke/capsules/",
    "src/gpd/core/evaluation.py",
    "src/gpd/core/oracle_runner.py",
)
REQUIRED_RESEARCH_SMOKE_CASES = frozenset(
    {
        "literature-evidence",
        "numerical-convergence",
        "state-recovery",
        "theory-limit-recovery",
    }
)


class CandidateManifest(BaseModel):
    """Declared scope and hypothesis for one candidate patch."""

    model_config = ConfigDict(extra="forbid")

    schema_version: Literal["gpd.improvement-candidate.v1"] = "gpd.improvement-candidate.v1"
    candidate_id: str
    baseline_sha: str
    candidate_sha: str
    hypothesis: str
    allowed_paths: list[str]
    expected_effects: list[str]

    @field_validator("candidate_id", "baseline_sha", "candidate_sha", "hypothesis")
    @classmethod
    def _non_empty_text(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("must not be blank")
        return normalized

    @field_validator("allowed_paths", "expected_effects")
    @classmethod
    def _non_empty_list(cls, value: list[str]) -> list[str]:
        normalized = [item.strip() for item in value if item.strip()]
        if not normalized:
            raise ValueError("must contain at least one value")
        return normalized


class ImprovementReport(BaseModel):
    """Promotion evidence; a passing report still requires human approval."""

    model_config = ConfigDict(extra="forbid")

    schema_version: Literal["gpd.improvement-report.v1"] = "gpd.improvement-report.v1"
    candidate: CandidateManifest
    decision: Literal["eligible_for_human_review", "reject"]
    gates: dict[str, bool]
    changed_paths: list[str]
    out_of_scope_paths: list[str] = Field(default_factory=list)
    protected_evaluator_changes: list[str] = Field(default_factory=list)
    smoke_evaluations: list[EvaluationResult]
    ab_score: dict[str, object]
    promotion_requires_human_approval: Literal[True] = True


def _git(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=repo,
        text=True,
        capture_output=True,
        check=check,
        timeout=60,
    )


def _path_allowed(path: str, allowed: list[str]) -> bool:
    for rule in allowed:
        normalized = rule.rstrip("/")
        if path == normalized or path.startswith(normalized + "/"):
            return True
    return False


def _protected(path: str) -> bool:
    return any(path == prefix.rstrip("/") or path.startswith(prefix) for prefix in PROTECTED_EVALUATOR_PATHS)


def _load_smoke_evaluations(paths: list[Path]) -> list[EvaluationResult]:
    evaluations: list[EvaluationResult] = []
    for path in paths:
        payload = json.loads(path.read_text(encoding="utf-8"))
        items = payload if isinstance(payload, list) else [payload]
        for item in items:
            if not isinstance(item, dict):
                raise ValueError(f"{path}: smoke result items must be objects")
            evaluation = item.get("evaluation", item)
            evaluations.append(EvaluationResult.model_validate(evaluation))
    if not evaluations:
        raise ValueError("at least one smoke evaluation is required")
    return evaluations


def build_improvement_report(
    manifest: CandidateManifest,
    *,
    repo: Path,
    ab_rows: list[dict[str, object]],
    smoke_result_paths: list[Path],
    policy: str = "rapid",
) -> ImprovementReport:
    """Evaluate immutable Git scope plus existing scientific and efficiency gates."""

    repo = repo.resolve()
    baseline_exists = _git(repo, "cat-file", "-e", f"{manifest.baseline_sha}^{{commit}}", check=False).returncode == 0
    candidate_exists = _git(repo, "cat-file", "-e", f"{manifest.candidate_sha}^{{commit}}", check=False).returncode == 0
    ancestry = False
    changed_paths: list[str] = []
    if baseline_exists and candidate_exists:
        ancestry = (
            _git(
                repo, "merge-base", "--is-ancestor", manifest.baseline_sha, manifest.candidate_sha, check=False
            ).returncode
            == 0
        )
        if ancestry:
            output = _git(repo, "diff", "--name-only", manifest.baseline_sha, manifest.candidate_sha).stdout
            changed_paths = sorted(path for path in output.splitlines() if path)
    out_of_scope = [path for path in changed_paths if not _path_allowed(path, manifest.allowed_paths)]
    protected_changes = [path for path in changed_paths if _protected(path)]
    smoke = _load_smoke_evaluations(smoke_result_paths)
    smoke_case_ids = [result.case_id for result in smoke]
    smoke_complete = (
        len(smoke_case_ids) == len(REQUIRED_RESEARCH_SMOKE_CASES)
        and set(smoke_case_ids) == REQUIRED_RESEARCH_SMOKE_CASES
    )
    ab = score_ab(ab_rows, policy=policy)
    gates = {
        "baseline_exists": baseline_exists,
        "candidate_exists": candidate_exists,
        "candidate_descends_from_baseline": ancestry,
        "declared_scope_respected": not out_of_scope,
        "evaluator_integrity": not protected_changes,
        "required_smoke_cases_present_once": smoke_complete,
        "smoke_passed": all(result.passed for result in smoke),
        "ab_noninferiority_and_efficiency": ab["decision"] == "pass",
    }
    decision = "eligible_for_human_review" if all(gates.values()) else "reject"
    return ImprovementReport(
        candidate=manifest,
        decision=decision,
        gates=gates,
        changed_paths=changed_paths,
        out_of_scope_paths=out_of_scope,
        protected_evaluator_changes=protected_changes,
        smoke_evaluations=smoke,
        ab_score=ab,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--ab-results", type=Path, required=True)
    parser.add_argument("--smoke-result", type=Path, action="append", required=True)
    parser.add_argument("--policy", choices=("rapid", "strict"), default="rapid")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest = CandidateManifest.model_validate_json(args.manifest.read_text(encoding="utf-8"))
    ab_rows = json.loads(args.ab_results.read_text(encoding="utf-8"))
    if not isinstance(ab_rows, list):
        raise ValueError("A/B results must be a JSON array")
    report = build_improvement_report(
        manifest,
        repo=args.repo,
        ab_rows=ab_rows,
        smoke_result_paths=args.smoke_result,
        policy=args.policy,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(report.model_dump_json(indent=2) + "\n", encoding="utf-8")
    print(report.model_dump_json(indent=2))
    return 0 if report.decision == "eligible_for_human_review" else 1


if __name__ == "__main__":
    raise SystemExit(main())
