"""Deterministic routing for independent GPD review work."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from enum import StrEnum
from typing import Literal


class ReviewKind(StrEnum):
    RESEARCH = "research"
    PLAN = "plan"
    VERIFIER = "verifier"
    PROOF = "proof"
    CITATION = "citation"
    REFEREE = "referee"


@dataclass(frozen=True, slots=True)
class PriorReview:
    review_id: str
    review_kind: ReviewKind
    subject_fingerprint: str
    evidence_fingerprint: str
    cleared: bool


@dataclass(frozen=True, slots=True)
class ReviewRouteFacts:
    review_kind: ReviewKind
    subject: dict[str, object]
    evidence: dict[str, object]
    explicit_user_request: bool = False
    proof_bearing: bool = False
    load_bearing: bool = False
    promotion_requested: bool = False
    expensive_or_irreversible: bool = False
    broad_fanout: bool = False
    convention_changed: bool = False
    source_changed: bool = False
    artifact_changed: bool = False
    unresolved_conflict: bool = False
    requires_user_decision: bool = False
    uncleared_risks: tuple[str, ...] = ()


def _fingerprint(value: dict[str, object]) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return f"sha256:{hashlib.sha256(encoded).hexdigest()}"


def decide_review_route(
    facts: ReviewRouteFacts,
    *,
    prior_review: PriorReview | None = None,
) -> dict[str, object]:
    """Return a route decision; never decide or promote the scientific claim."""

    subject_fingerprint = _fingerprint(facts.subject)
    evidence_fingerprint = _fingerprint(facts.evidence)
    unchanged_cleared_review = (
        prior_review is not None
        and prior_review.cleared
        and prior_review.review_kind is facts.review_kind
        and prior_review.subject_fingerprint == subject_fingerprint
        and prior_review.evidence_fingerprint == evidence_fingerprint
    )

    route: Literal["run", "skip", "checkpoint"]
    reason_codes: list[str] = []
    deduplicated_against: str | None = None
    if facts.requires_user_decision:
        route = "checkpoint"
        reason_codes.append("missing_outcome_changing_user_decision")
    elif unchanged_cleared_review:
        route = "skip"
        reason_codes.append("fresh_equivalent_review_reused")
        deduplicated_against = prior_review.review_id if prior_review is not None else None
    else:
        triggers = (
            (facts.explicit_user_request, "explicit_user_request"),
            (facts.proof_bearing, "proof_bearing"),
            (facts.load_bearing, "load_bearing"),
            (facts.promotion_requested, "promotion_requested"),
            (facts.expensive_or_irreversible, "expensive_or_irreversible"),
            (facts.broad_fanout, "broad_fanout"),
            (facts.convention_changed, "convention_changed"),
            (facts.source_changed, "source_changed"),
            (facts.artifact_changed, "artifact_changed"),
            (facts.unresolved_conflict, "unresolved_conflict"),
        )
        reason_codes.extend(code for active, code in triggers if active)
        reason_codes.extend(f"uncleared:{risk}" for risk in facts.uncleared_risks)
        route = "run" if reason_codes else "skip"
        if route == "skip":
            reason_codes.append("no_independent_review_trigger")

    return {
        "schema_version": 1,
        "route": route,
        "review_kind": facts.review_kind.value,
        "reason_codes": reason_codes,
        "subject_fingerprint": subject_fingerprint,
        "evidence_fingerprint": evidence_fingerprint,
        "deduplicated_against": deduplicated_against,
        "uncleared_risks": list(facts.uncleared_risks),
        "status_ceiling": "working" if route == "checkpoint" else "candidate",
    }
