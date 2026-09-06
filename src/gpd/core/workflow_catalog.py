"""Canonical responsibility groups; operation contracts remain registry-owned."""

from __future__ import annotations

import json
from functools import lru_cache

from gpd.specs import SPECS_DIR


@lru_cache(maxsize=1)
def workflow_catalog() -> dict[str, tuple[str, ...]]:
    data = json.loads((SPECS_DIR / "references/shared/workflow-catalog.json").read_text())
    seen: set[str] = set()
    result: dict[str, tuple[str, ...]] = {}
    for group, operations in data.items():
        if not isinstance(group, str) or not group or not isinstance(operations, list) or not operations:
            raise ValueError("Invalid workflow group")
        for operation in operations:
            if not isinstance(operation, str) or not operation or operation in seen:
                raise ValueError("Invalid or duplicate workflow operation")
            seen.add(operation)
        result[group] = tuple(operations)
    return result


def operation_group(name: str) -> str:
    from gpd.command_labels import command_slug_from_label

    slug = command_slug_from_label(name)
    for group, operations in workflow_catalog().items():
        if slug in operations:
            return group
    raise KeyError(name)


def grouped_operation_skills() -> frozenset[str]:
    return frozenset("gpd-" + op for ops in workflow_catalog().values() for op in ops)


if __name__ == "__main__":
    import sys

    catalog = workflow_catalog()
    if len(sys.argv) > 1:
        group = sys.argv[1]
        if group not in catalog:
            raise SystemExit("Unknown workflow group: " + group)
        catalog = {group: catalog[group]}
    print(json.dumps(catalog, indent=2))
