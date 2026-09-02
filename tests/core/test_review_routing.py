"""Deterministic independent-review routing contracts."""

from gpd.core.review_routing import PriorReview, ReviewKind, ReviewRouteFacts, decide_review_route


def _facts(**overrides: object) -> ReviewRouteFacts:
    values: dict[str, object] = {
        "review_kind": ReviewKind.PLAN,
        "subject": {"plan": "07-01", "claim": "dispersion"},
        "evidence": {"plan_sha256": "abc", "convention_sha256": "def"},
    }
    values.update(overrides)
    return ReviewRouteFacts(**values)


def test_clean_ordinary_work_skips_without_promoting() -> None:
    decision = decide_review_route(_facts())

    assert decision["route"] == "skip"
    assert decision["reason_codes"] == ["no_independent_review_trigger"]
    assert decision["status_ceiling"] == "candidate"


def test_load_bearing_or_proof_work_runs_independent_review() -> None:
    plan = decide_review_route(_facts(load_bearing=True))
    proof = decide_review_route(_facts(review_kind=ReviewKind.PROOF, proof_bearing=True))

    assert plan["route"] == "run"
    assert "load_bearing" in plan["reason_codes"]
    assert proof["route"] == "run"
    assert "proof_bearing" in proof["reason_codes"]


def test_exact_cleared_review_is_reused_but_evidence_change_invalidates_it() -> None:
    facts = _facts(load_bearing=True)
    first = decide_review_route(facts)
    prior = PriorReview(
        review_id="review-17",
        review_kind=ReviewKind.PLAN,
        subject_fingerprint=str(first["subject_fingerprint"]),
        evidence_fingerprint=str(first["evidence_fingerprint"]),
        cleared=True,
    )

    reused = decide_review_route(facts, prior_review=prior)
    changed = decide_review_route(
        _facts(load_bearing=True, evidence={"plan_sha256": "changed", "convention_sha256": "def"}),
        prior_review=prior,
    )

    assert reused["route"] == "skip"
    assert reused["deduplicated_against"] == "review-17"
    assert changed["route"] == "run"
    assert changed["evidence_fingerprint"] != first["evidence_fingerprint"]


def test_missing_outcome_changing_decision_checkpoints_before_review() -> None:
    decision = decide_review_route(_facts(requires_user_decision=True, proof_bearing=True))

    assert decision["route"] == "checkpoint"
    assert decision["status_ceiling"] == "working"
