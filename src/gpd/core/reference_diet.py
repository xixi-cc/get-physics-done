"""Reference loading classes for base-model-first prompt assembly."""

from __future__ import annotations

from enum import StrEnum
from pathlib import PurePosixPath


class ReferenceDietClass(StrEnum):
    KERNEL = "kernel"
    JIT_CHECKLIST = "jit-checklist"
    ARCHIVE_RETRIEVAL = "archive-retrieval"


_ARCHIVE_PARTS = frozenset({"examples"})
_ARCHIVE_NAME_MARKERS = ("worked-example", "cookbook")
_JIT_PREFIXES = (
    "references/protocols/",
    "references/verification/",
    "references/physics-subfields",
    "references/methods/",
    "references/execution/guards/",
    "references/planning/domain-",
)


def classify_reference(authority: str) -> ReferenceDietClass:
    """Classify one authority without deleting or relocating its source file."""

    normalized = authority.strip().lstrip("./")
    path = PurePosixPath(normalized)
    if _ARCHIVE_PARTS.intersection(path.parts) or any(marker in path.name for marker in _ARCHIVE_NAME_MARKERS):
        return ReferenceDietClass.ARCHIVE_RETRIEVAL
    if any(normalized.startswith(prefix) for prefix in _JIT_PREFIXES):
        return ReferenceDietClass.JIT_CHECKLIST
    return ReferenceDietClass.KERNEL
