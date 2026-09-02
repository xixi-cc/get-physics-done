"""Small capsule-specific scientific checks.

These checks are intentionally local to the evaluation fixture. They are not
part of the production verification registry.
"""

from __future__ import annotations

import math

from gpd.core.research_evidence import EvidenceBundle


def derivation_audit(*, submission: dict[str, object]) -> dict[str, object]:
    identified = submission.get("identified_error") == "missing-boundary-term"
    consequence = submission.get("affected_claim") == "zero-mode-normalization"
    passed = identified and consequence
    return {
        "passed": passed,
        "observed": {
            "identified_error": submission.get("identified_error"),
            "affected_claim": submission.get("affected_claim"),
        },
        "expected": {
            "identified_error": "missing-boundary-term",
            "affected_claim": "zero-mode-normalization",
        },
        "details": "The load-bearing boundary term and affected claim must both be identified.",
    }


def convergence_audit(*, submission: dict[str, object]) -> dict[str, object]:
    raw = submission.get("estimates")
    if not isinstance(raw, list) or len(raw) < 4:
        return {"passed": False, "observed": raw, "expected": "at least four finite estimates"}
    try:
        values = [float(value) for value in raw]
    except (TypeError, ValueError):
        return {"passed": False, "observed": raw, "expected": "finite numeric estimates"}
    finite = all(math.isfinite(value) for value in values)
    differences = [abs(right - left) for left, right in zip(values, values[1:], strict=False)]
    contracting = all(right < left for left, right in zip(differences, differences[1:], strict=False))
    passed = finite and contracting and abs(values[-1] - 0.5) <= 0.01
    return {
        "passed": passed,
        "observed": {"last": values[-1], "successive_differences": differences},
        "expected": {"limit": 0.5, "atol": 0.01, "contracting_differences": True},
    }


def literature_evidence_audit(*, submission: dict[str, object]) -> dict[str, object]:
    try:
        bundle = EvidenceBundle.model_validate(submission)
    except ValueError as exc:
        return {"passed": False, "observed": "invalid bundle", "expected": "EvidenceBundle v1", "details": str(exc)}
    records = {record.id: record for record in bundle.evidence}
    decisive = records.get("ref-dispersion")
    supporting = any(
        link.claim_id == "claim-long-wave-instability"
        and link.evidence_id == "ref-dispersion"
        and link.relation == "supports"
        and bool(link.scope)
        for link in bundle.links
    )
    limiting = any(
        link.claim_id == "claim-long-wave-instability" and link.relation == "limits" for link in bundle.links
    )
    located = decisive is not None and bool(decisive.locator.equation or decisive.locator.page)
    passed = supporting and limiting and located
    return {
        "passed": passed,
        "observed": {"scoped_support": supporting, "limiting_evidence": limiting, "located": located},
        "expected": {"scoped_support": True, "limiting_evidence": True, "located": True},
    }


def recovery_audit(*, submission: dict[str, object]) -> dict[str, object]:
    authority = submission.get("resume_authority") == "GPD/.continue-here.md"
    blockers = submission.get("preserved_blockers")
    blocker_preserved = isinstance(blockers, list) and "unvalidated-critical-fit" in blockers
    no_promotion = submission.get("claim_status") == "inconclusive"
    next_action = submission.get("next_action") == "rerun-critical-fit-validation"
    passed = authority and blocker_preserved and no_promotion and next_action
    return {
        "passed": passed,
        "observed": {
            "canonical_authority": authority,
            "blocker_preserved": blocker_preserved,
            "no_claim_promotion": no_promotion,
            "next_action": next_action,
        },
        "expected": {"all": True},
    }
