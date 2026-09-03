"""Conservative, evidence-aware model routing for bounded GPD task segments.

The router does not judge scientific claims.  It converts facts already owned by
plans, contracts, task overlays, and review routing into a minimum model policy.
Unknown or scientifically consequential work stays on tier-1.
"""

from __future__ import annotations

import hashlib
import json
from enum import StrEnum
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from gpd.adapters.runtime_catalog import normalize_runtime_name
from gpd.adapters.task_model_policy import get_task_model_policy_binding
from gpd.core.config import ModelTier, resolve_tier_model, validate_agent_name

POLICY_VERSION = "research-floor-v1"


class RoutingMode(StrEnum):
    """Whether a recommendation is observed or used for dispatch."""

    SHADOW = "shadow"
    ENFORCE = "enforce"


class TaskShape(StrEnum):
    """The reasoning shape of one bounded work segment."""

    DETERMINISTIC = "deterministic"
    BOUNDED_IMPLEMENTATION = "bounded-implementation"
    BOUNDED_ANALYSIS = "bounded-analysis"
    OPEN_RESEARCH = "open-research"
    SCIENTIFIC_JUDGMENT = "scientific-judgment"


class VerificationKind(StrEnum):
    NONE = "none"
    SCHEMA = "schema"
    PYTHON = "python"
    PYTEST = "pytest"
    NUMERIC_TOLERANCE = "numeric-tolerance"
    EVIDENCE = "evidence"
    SCIENTIFIC_REVIEW = "scientific-review"


class VerificationCoverage(StrEnum):
    NONE = "none"
    STRUCTURAL_ONLY = "structural-only"
    PARTIAL = "partial"
    FULL = "full"


class ContextScope(StrEnum):
    LOCAL = "local"
    PHASE = "phase"
    PROJECT = "project"


class PriorFailureKind(StrEnum):
    NONE = "none"
    CONTRACT = "contract"
    ORACLE = "oracle"
    AMBIGUITY = "ambiguity"
    SCIENTIFIC_ANOMALY = "scientific-anomaly"
    INFRASTRUCTURE = "infrastructure"


class ExecutionRoute(StrEnum):
    TOOL_ONLY = "tool-only"
    MODEL = "model"
    CHECKPOINT = "checkpoint"


class TaskExecutionFacts(BaseModel):
    """Normalized read-only facts for one task segment.

    ``facts_complete`` means the caller had enough authoritative plan/contract
    information to classify the segment.  It is never inferred from a fluent
    task description.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    role: str
    segment_id: str
    task_shape: TaskShape
    facts_complete: bool = False
    overlay_ids: tuple[str, ...] = ()

    proof_bearing: bool = False
    load_bearing: bool = False
    scientific_judgment: bool = False
    promotion_requested: bool = False
    unresolved_conflict: bool = False
    convention_changed: bool = False
    expensive_or_irreversible: bool = False
    requires_user_decision: bool = False
    user_forced_tier_1: bool = False

    requires_model: bool = True
    deterministic_transform: bool = False
    verification_kind: VerificationKind = VerificationKind.NONE
    verification_coverage: VerificationCoverage = VerificationCoverage.NONE
    context_scope: ContextScope = ContextScope.LOCAL

    prior_tier: ModelTier | None = None
    prior_failure: PriorFailureKind = PriorFailureKind.NONE
    escalation_count: int = Field(default=0, ge=0)


class ResolvedExecutionPolicy(BaseModel):
    """Auditable routing recommendation and effective dispatch policy."""

    model_config = ConfigDict(frozen=True)

    schema_version: int = 1
    policy_version: str = POLICY_VERSION
    mode: RoutingMode
    task_fingerprint: str
    role: str
    segment_id: str

    recommended_route: ExecutionRoute
    recommended_tier: ModelTier | None
    recommended_model: str | None
    recommended_reasoning_effort: str | None

    dispatch_route: ExecutionRoute
    dispatch_tier: ModelTier | None
    dispatch_model: str | None
    dispatch_reasoning_effort: str | None

    reason_codes: tuple[str, ...]
    verification_route: str
    escalation_target: ModelTier | None
    status_ceiling: str


_FULL_MECHANICAL_ORACLES = frozenset(
    {
        VerificationKind.SCHEMA,
        VerificationKind.PYTHON,
        VerificationKind.PYTEST,
        VerificationKind.NUMERIC_TOLERANCE,
    }
)


def _task_fingerprint(facts: TaskExecutionFacts) -> str:
    encoded = json.dumps(
        facts.model_dump(mode="json"),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return f"sha256:{hashlib.sha256(encoded).hexdigest()}"


def _hard_tier_one_reasons(facts: TaskExecutionFacts) -> list[str]:
    proof_overlay_selected = any(overlay_id.endswith(".proof_bearing") for overlay_id in facts.overlay_ids)
    checks = (
        (facts.user_forced_tier_1, "user_forced_tier_1"),
        (facts.proof_bearing, "proof_bearing"),
        (proof_overlay_selected, "proof_bearing_overlay"),
        (facts.load_bearing, "load_bearing"),
        (facts.scientific_judgment, "scientific_judgment"),
        (facts.promotion_requested, "promotion_requested"),
        (facts.unresolved_conflict, "unresolved_conflict"),
        (facts.convention_changed, "convention_changed"),
        (facts.expensive_or_irreversible, "expensive_or_irreversible"),
        (facts.requires_user_decision, "requires_user_decision"),
        (facts.context_scope is ContextScope.PROJECT, "project_scope"),
        (facts.task_shape is TaskShape.OPEN_RESEARCH, "open_research"),
        (facts.task_shape is TaskShape.SCIENTIFIC_JUDGMENT, "scientific_judgment_shape"),
        (facts.prior_failure is PriorFailureKind.AMBIGUITY, "prior_ambiguity"),
        (facts.prior_failure is PriorFailureKind.SCIENTIFIC_ANOMALY, "prior_scientific_anomaly"),
    )
    return [reason for active, reason in checks if active]


def _base_recommendation(
    facts: TaskExecutionFacts,
) -> tuple[ExecutionRoute, ModelTier | None, list[str]]:
    if facts.prior_failure is PriorFailureKind.INFRASTRUCTURE:
        return ExecutionRoute.CHECKPOINT, None, ["infrastructure_failure_is_not_a_model_problem"]
    if facts.requires_user_decision:
        return ExecutionRoute.CHECKPOINT, None, ["missing_outcome_changing_user_decision"]
    if facts.prior_failure is not PriorFailureKind.NONE and facts.escalation_count >= 1:
        return ExecutionRoute.CHECKPOINT, None, ["single_escalation_budget_exhausted"]

    hard_reasons = _hard_tier_one_reasons(facts)
    if hard_reasons:
        return ExecutionRoute.MODEL, ModelTier.TIER_1, hard_reasons
    if not facts.facts_complete:
        return ExecutionRoute.MODEL, ModelTier.TIER_1, ["incomplete_task_facts_default_to_tier_1"]

    full_mechanical_verification = (
        facts.verification_coverage is VerificationCoverage.FULL
        and facts.verification_kind in _FULL_MECHANICAL_ORACLES
    )
    if (
        not facts.requires_model
        and facts.task_shape is TaskShape.DETERMINISTIC
        and facts.deterministic_transform
        and full_mechanical_verification
    ):
        return ExecutionRoute.TOOL_ONLY, None, ["deterministic_tool_route", "full_mechanical_verification"]

    if (
        facts.requires_model
        and facts.task_shape is TaskShape.DETERMINISTIC
        and facts.deterministic_transform
        and full_mechanical_verification
        and facts.context_scope is ContextScope.LOCAL
    ):
        return ExecutionRoute.MODEL, ModelTier.TIER_3, [
            "deterministic_local_model_task",
            "full_mechanical_verification",
        ]

    bounded = facts.task_shape in {TaskShape.BOUNDED_IMPLEMENTATION, TaskShape.BOUNDED_ANALYSIS}
    has_useful_verification = (
        facts.verification_kind is not VerificationKind.NONE
        and facts.verification_coverage is not VerificationCoverage.NONE
    )
    if bounded and has_useful_verification and facts.context_scope is not ContextScope.PROJECT:
        return ExecutionRoute.MODEL, ModelTier.TIER_2, ["bounded_work", "verification_path_available"]

    return ExecutionRoute.MODEL, ModelTier.TIER_1, ["no_safe_downgrade_proven"]


def _promote_after_failure(
    facts: TaskExecutionFacts,
    route: ExecutionRoute,
    tier: ModelTier | None,
    reasons: list[str],
) -> tuple[ExecutionRoute, ModelTier | None, list[str]]:
    if facts.prior_failure is PriorFailureKind.NONE or route is ExecutionRoute.CHECKPOINT:
        return route, tier, reasons
    if facts.prior_failure in {PriorFailureKind.AMBIGUITY, PriorFailureKind.SCIENTIFIC_ANOMALY}:
        return ExecutionRoute.MODEL, ModelTier.TIER_1, [*reasons, "failure_requires_tier_1"]

    prior_tier = facts.prior_tier
    if prior_tier is ModelTier.TIER_3:
        promoted = ModelTier.TIER_2
    elif prior_tier is ModelTier.TIER_2:
        promoted = ModelTier.TIER_1
    else:
        promoted = ModelTier.TIER_1
    if tier is None or _tier_rank(promoted) < _tier_rank(tier):
        tier = promoted
    return ExecutionRoute.MODEL, tier, [*reasons, "single_evidence_driven_escalation"]


def _tier_rank(tier: ModelTier) -> int:
    return {
        ModelTier.TIER_1: 1,
        ModelTier.TIER_2: 2,
        ModelTier.TIER_3: 3,
    }[tier]


def _next_tier(tier: ModelTier | None) -> ModelTier | None:
    if tier is ModelTier.TIER_3:
        return ModelTier.TIER_2
    if tier is ModelTier.TIER_2:
        return ModelTier.TIER_1
    return None


def decide_task_execution_policy(
    facts: TaskExecutionFacts,
    *,
    mode: RoutingMode = RoutingMode.SHADOW,
    model_by_tier: dict[ModelTier, str] | None = None,
    effort_by_tier: dict[ModelTier, str] | None = None,
) -> ResolvedExecutionPolicy:
    """Resolve one task segment without performing model-based classification."""

    validate_agent_name(facts.role)
    models = model_by_tier or {}
    efforts = effort_by_tier or {}
    route, tier, reasons = _base_recommendation(facts)
    route, tier, reasons = _promote_after_failure(facts, route, tier, reasons)

    recommended_model = models.get(tier) if tier is not None else None
    recommended_effort = efforts.get(tier) if tier is not None else None

    if route is ExecutionRoute.CHECKPOINT:
        dispatch_route = ExecutionRoute.CHECKPOINT
        dispatch_tier = None
    elif mode is RoutingMode.SHADOW:
        dispatch_route = ExecutionRoute.MODEL
        dispatch_tier = ModelTier.TIER_1
    else:
        dispatch_route = route
        dispatch_tier = tier

    return ResolvedExecutionPolicy(
        mode=mode,
        task_fingerprint=_task_fingerprint(facts),
        role=facts.role,
        segment_id=facts.segment_id,
        recommended_route=route,
        recommended_tier=tier,
        recommended_model=recommended_model,
        recommended_reasoning_effort=recommended_effort,
        dispatch_route=dispatch_route,
        dispatch_tier=dispatch_tier,
        dispatch_model=models.get(dispatch_tier) if dispatch_tier is not None else None,
        dispatch_reasoning_effort=efforts.get(dispatch_tier) if dispatch_tier is not None else None,
        reason_codes=tuple(dict.fromkeys(reasons)),
        verification_route=f"{facts.verification_kind.value}:{facts.verification_coverage.value}",
        escalation_target=_next_tier(tier),
        status_ceiling="working" if dispatch_route is ExecutionRoute.CHECKPOINT else "candidate",
    )


def resolve_project_task_execution_policy(
    project_dir: Path,
    facts: TaskExecutionFacts,
    *,
    runtime: str | None,
    mode: RoutingMode = RoutingMode.SHADOW,
) -> ResolvedExecutionPolicy:
    """Bind an abstract decision to project/runtime model overrides.

    Runtime defaults live in the adapter layer. Explicit project tier
    overrides remain authoritative.
    """

    normalized_runtime = normalize_runtime_name(runtime) if runtime else None
    if runtime and normalized_runtime is None:
        raise ValueError(f"Unknown runtime {runtime!r}")
    binding = get_task_model_policy_binding(normalized_runtime)
    model_by_tier = {ModelTier(tier): model for tier, model in binding.model_by_tier.items()}
    effort_by_tier = {ModelTier(tier): effort for tier, effort in binding.effort_by_tier.items()}

    if normalized_runtime is not None:
        for tier in ModelTier:
            explicit_model = resolve_tier_model(project_dir, tier, runtime=normalized_runtime)
            if explicit_model is not None:
                model_by_tier[tier] = explicit_model

    return decide_task_execution_policy(
        facts,
        mode=mode,
        model_by_tier=model_by_tier,
        effort_by_tier=effort_by_tier,
    )
