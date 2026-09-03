"""Runtime-owned default bindings for task-level model routing."""

from __future__ import annotations

from dataclasses import dataclass

from gpd.adapters.runtime_catalog import normalize_runtime_name


@dataclass(frozen=True, slots=True)
class TaskModelPolicyBinding:
    """Model ids and reasoning effort keyed by abstract tier names."""

    model_by_tier: dict[str, str]
    effort_by_tier: dict[str, str]


_EMPTY_BINDING = TaskModelPolicyBinding(model_by_tier={}, effort_by_tier={})

_DEFAULT_BINDINGS = {
    "codex": TaskModelPolicyBinding(
        model_by_tier={
            "tier-1": "gpt-5.6-sol",
            "tier-2": "gpt-5.6-terra",
            "tier-3": "gpt-5.6-luna",
        },
        effort_by_tier={
            "tier-1": "medium",
            "tier-2": "medium",
            "tier-3": "low",
        },
    )
}


def get_task_model_policy_binding(runtime: str | None) -> TaskModelPolicyBinding:
    """Return the adapter-owned routing defaults for *runtime*, if any."""

    normalized = normalize_runtime_name(runtime)
    if normalized is None:
        return _EMPTY_BINDING
    return _DEFAULT_BINDINGS.get(normalized, _EMPTY_BINDING)


__all__ = ["TaskModelPolicyBinding", "get_task_model_policy_binding"]
