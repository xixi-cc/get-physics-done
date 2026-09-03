"""Evidence-aware task model routing."""

import json
from pathlib import Path

from gpd.adapters.runtime_catalog import list_runtime_names
from gpd.adapters.task_model_policy import get_task_model_policy_binding
from gpd.core.config import ModelTier
from gpd.core.model_routing import (
    ContextScope,
    ExecutionRoute,
    PriorFailureKind,
    RoutingMode,
    TaskExecutionFacts,
    TaskShape,
    VerificationCoverage,
    VerificationKind,
    decide_task_execution_policy,
    resolve_project_task_execution_policy,
)

_ROUTING_RUNTIME = next(
    runtime for runtime in list_runtime_names() if get_task_model_policy_binding(runtime).model_by_tier
)


def _facts(**overrides: object) -> TaskExecutionFacts:
    values: dict[str, object] = {
        "role": "gpd-executor",
        "segment_id": "01-implement",
        "task_shape": TaskShape.BOUNDED_IMPLEMENTATION,
        "facts_complete": True,
        "verification_kind": VerificationKind.PYTEST,
        "verification_coverage": VerificationCoverage.FULL,
    }
    values.update(overrides)
    return TaskExecutionFacts(**values)


def _models() -> dict[ModelTier, str]:
    return {
        ModelTier.TIER_1: "sol",
        ModelTier.TIER_2: "terra",
        ModelTier.TIER_3: "luna",
    }


def _efforts() -> dict[ModelTier, str]:
    return {
        ModelTier.TIER_1: "medium",
        ModelTier.TIER_2: "medium",
        ModelTier.TIER_3: "low",
    }


def test_incomplete_facts_fail_closed_to_sol_medium() -> None:
    decision = decide_task_execution_policy(
        _facts(facts_complete=False),
        mode=RoutingMode.ENFORCE,
        model_by_tier=_models(),
        effort_by_tier=_efforts(),
    )

    assert decision.dispatch_tier is ModelTier.TIER_1
    assert decision.dispatch_model == "sol"
    assert decision.dispatch_reasoning_effort == "medium"
    assert decision.reason_codes == ("incomplete_task_facts_default_to_tier_1",)


def test_proof_and_load_bearing_work_cannot_downgrade() -> None:
    for facts in (
        _facts(proof_bearing=True),
        _facts(load_bearing=True),
        _facts(overlay_ids=("executor.proof_bearing",)),
    ):
        decision = decide_task_execution_policy(
            facts,
            mode=RoutingMode.ENFORCE,
            model_by_tier=_models(),
            effort_by_tier=_efforts(),
        )
        assert decision.dispatch_tier is ModelTier.TIER_1
        assert decision.dispatch_model == "sol"


def test_full_mechanical_task_uses_luna_low() -> None:
    decision = decide_task_execution_policy(
        _facts(
            task_shape=TaskShape.DETERMINISTIC,
            deterministic_transform=True,
            context_scope=ContextScope.LOCAL,
        ),
        mode=RoutingMode.ENFORCE,
        model_by_tier=_models(),
        effort_by_tier=_efforts(),
    )

    assert decision.recommended_tier is ModelTier.TIER_3
    assert decision.dispatch_model == "luna"
    assert decision.dispatch_reasoning_effort == "low"


def test_full_numeric_tolerance_oracle_can_bound_local_deterministic_work() -> None:
    decision = decide_task_execution_policy(
        _facts(
            task_shape=TaskShape.DETERMINISTIC,
            deterministic_transform=True,
            verification_kind=VerificationKind.NUMERIC_TOLERANCE,
        ),
        mode=RoutingMode.ENFORCE,
        model_by_tier=_models(),
        effort_by_tier=_efforts(),
    )

    assert decision.dispatch_tier is ModelTier.TIER_3
    assert decision.verification_route == "numeric-tolerance:full"


def test_deterministic_task_uses_no_model_when_not_required() -> None:
    decision = decide_task_execution_policy(
        _facts(
            task_shape=TaskShape.DETERMINISTIC,
            deterministic_transform=True,
            requires_model=False,
        ),
        mode=RoutingMode.ENFORCE,
        model_by_tier=_models(),
        effort_by_tier=_efforts(),
    )

    assert decision.dispatch_route is ExecutionRoute.TOOL_ONLY
    assert decision.dispatch_tier is None
    assert decision.dispatch_model is None


def test_bounded_verified_work_uses_terra_medium() -> None:
    decision = decide_task_execution_policy(
        _facts(),
        mode=RoutingMode.ENFORCE,
        model_by_tier=_models(),
        effort_by_tier=_efforts(),
    )

    assert decision.dispatch_tier is ModelTier.TIER_2
    assert decision.dispatch_model == "terra"
    assert decision.dispatch_reasoning_effort == "medium"


def test_shadow_mode_keeps_sol_dispatch_and_reports_recommendation() -> None:
    decision = decide_task_execution_policy(
        _facts(),
        mode=RoutingMode.SHADOW,
        model_by_tier=_models(),
        effort_by_tier=_efforts(),
    )

    assert decision.recommended_tier is ModelTier.TIER_2
    assert decision.recommended_model == "terra"
    assert decision.dispatch_tier is ModelTier.TIER_1
    assert decision.dispatch_model == "sol"


def test_infrastructure_failure_checkpoints_instead_of_spending_more_model() -> None:
    decision = decide_task_execution_policy(
        _facts(prior_failure=PriorFailureKind.INFRASTRUCTURE),
        mode=RoutingMode.ENFORCE,
        model_by_tier=_models(),
        effort_by_tier=_efforts(),
    )

    assert decision.dispatch_route is ExecutionRoute.CHECKPOINT
    assert decision.status_ceiling == "working"


def test_single_evidence_driven_escalation_promotes_luna_to_terra() -> None:
    decision = decide_task_execution_policy(
        _facts(
            task_shape=TaskShape.DETERMINISTIC,
            deterministic_transform=True,
            prior_tier=ModelTier.TIER_3,
            prior_failure=PriorFailureKind.ORACLE,
        ),
        mode=RoutingMode.ENFORCE,
        model_by_tier=_models(),
        effort_by_tier=_efforts(),
    )

    assert decision.dispatch_tier is ModelTier.TIER_2
    assert "single_evidence_driven_escalation" in decision.reason_codes


def test_second_failure_checkpoints() -> None:
    decision = decide_task_execution_policy(
        _facts(
            prior_tier=ModelTier.TIER_2,
            prior_failure=PriorFailureKind.ORACLE,
            escalation_count=1,
        ),
        mode=RoutingMode.ENFORCE,
        model_by_tier=_models(),
        effort_by_tier=_efforts(),
    )

    assert decision.dispatch_route is ExecutionRoute.CHECKPOINT
    assert decision.reason_codes == ("single_escalation_budget_exhausted",)


def test_project_binding_defaults_to_requested_model_family(tmp_path: Path) -> None:
    decision = resolve_project_task_execution_policy(
        tmp_path,
        _facts(),
        runtime=_ROUTING_RUNTIME,
        mode=RoutingMode.ENFORCE,
    )

    assert decision.dispatch_model == "gpt-5.6-terra"
    assert decision.dispatch_reasoning_effort == "medium"


def test_explicit_project_override_beats_runtime_family_default(tmp_path: Path) -> None:
    planning = tmp_path / "GPD"
    planning.mkdir()
    payload = {"model_overrides": {_ROUTING_RUNTIME: {"tier-2": "custom-terra"}}}
    (planning / "config.json").write_text(json.dumps(payload), encoding="utf-8")

    decision = resolve_project_task_execution_policy(
        tmp_path,
        _facts(),
        runtime=_ROUTING_RUNTIME,
        mode=RoutingMode.ENFORCE,
    )

    assert decision.dispatch_model == "custom-terra"


def test_unknown_runtime_is_rejected(tmp_path: Path) -> None:
    try:
        resolve_project_task_execution_policy(
            tmp_path,
            _facts(),
            runtime="not-a-runtime",
            mode=RoutingMode.ENFORCE,
        )
    except ValueError as exc:
        assert "Unknown runtime" in str(exc)
    else:
        raise AssertionError("unknown runtime should not silently lose its model binding")
