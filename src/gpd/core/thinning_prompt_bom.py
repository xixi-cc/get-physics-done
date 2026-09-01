"""Deterministic, model-invisible bills of materials for staged prompts."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Iterable
from pathlib import Path

from gpd.core.workflow_staging import load_workflow_stage_manifest
from gpd.specs import SPECS_DIR

SCHEMA_VERSION = "gpd.thinning-prompt-bom.v1"


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _stable_hash(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return _sha256_bytes(encoded)


def _resolve_authority(specs_root: Path, authority: str) -> Path:
    relative = Path(authority)
    if relative.is_absolute() or ".." in relative.parts:
        raise ValueError(f"Authority must stay within the specs root: {authority!r}")
    root = specs_root.resolve()
    resolved = (root / relative).resolve()
    if not resolved.is_relative_to(root):
        raise ValueError(f"Authority escapes the specs root: {authority!r}")
    return resolved


def _authority_entry(
    specs_root: Path,
    authority: str,
    *,
    role: str,
    eager: bool,
    condition: str | None = None,
) -> dict[str, object]:
    path = _resolve_authority(specs_root, authority)
    if not path.is_file():
        raise ValueError(f"Declared authority does not exist: {authority!r}")
    raw = path.read_bytes()
    text = raw.decode("utf-8")
    entry: dict[str, object] = {
        "authority": authority,
        "role": role,
        "eager": eager,
        "sha256": _sha256_bytes(raw),
        "bytes": len(raw),
        "chars": len(text),
        "lines": len(text.splitlines()),
        "words": len(text.split()),
    }
    if condition is not None:
        entry["condition"] = condition
    return entry


def build_stage_prompt_bom(
    workflow_id: str,
    stage_id: str,
    *,
    selected_conditions: Iterable[str] = (),
    specs_root: Path | None = None,
) -> dict[str, object]:
    """Build a deterministic BOM without changing the staged init payload."""

    root = (specs_root or SPECS_DIR).resolve()
    manifest = load_workflow_stage_manifest(workflow_id, specs_root=root)
    stage = manifest.stage(stage_id)
    selected = tuple(dict.fromkeys(condition.strip() for condition in selected_conditions if condition.strip()))
    selected_set = set(selected)
    eager_authorities = stage.eager_authorities(selected_conditions=selected)

    entries: list[dict[str, object]] = []
    for authority in stage.mode_paths:
        entries.append(_authority_entry(root, authority, role="mode", eager=True))
    for authority in stage.loaded_authorities:
        entries.append(_authority_entry(root, authority, role="loaded", eager=True))
    for conditional in stage.conditional_authorities:
        is_selected = conditional.when in selected_set
        role = "conditional_selected" if is_selected else "conditional_unselected"
        for authority in conditional.authorities:
            entries.append(
                _authority_entry(
                    root,
                    authority,
                    role=role,
                    eager=is_selected,
                    condition=conditional.when,
                )
            )

    declared = {str(entry["authority"]) for entry in entries}
    for authority in stage.must_not_eager_load:
        if authority in declared:
            continue
        entries.append(_authority_entry(root, authority, role="must_not_eager", eager=False))

    eager_entries = [entry for entry in entries if entry["eager"]]
    payload = stage.to_staged_loading_payload(manifest.workflow_id)
    return {
        "schema_version": SCHEMA_VERSION,
        "workflow_id": manifest.workflow_id,
        "stage_id": stage.id,
        "selected_conditions": list(selected),
        "staged_loading_payload_sha256": _stable_hash(payload),
        "eager_authorities": list(eager_authorities),
        "totals": {
            "entry_count": len(entries),
            "eager_entry_count": len(eager_entries),
            "eager_bytes": sum(int(entry["bytes"]) for entry in eager_entries),
            "eager_chars": sum(int(entry["chars"]) for entry in eager_entries),
            "eager_words": sum(int(entry["words"]) for entry in eager_entries),
        },
        "entries": entries,
    }
