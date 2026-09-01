"""Contracts for the model-invisible staged prompt BOM."""

from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from gpd.cli import app
from gpd.core.thinning_prompt_bom import build_stage_prompt_bom
from gpd.core.workflow_staging import load_workflow_stage_manifest

ROOT = Path(__file__).resolve().parents[2]
SPECS = ROOT / "src" / "gpd" / "specs"


def test_prompt_bom_is_deterministic_and_matches_eager_authorities() -> None:
    manifest = load_workflow_stage_manifest("plan-phase", specs_root=SPECS)
    stage = manifest.stage("checker_revision")
    before = stage.to_staged_loading_payload(manifest.workflow_id)

    first = build_stage_prompt_bom("plan-phase", "checker_revision", specs_root=SPECS)
    second = build_stage_prompt_bom("plan-phase", "checker_revision", specs_root=SPECS)

    assert first == second
    assert first["schema_version"] == "gpd.thinning-prompt-bom.v1"
    assert first["eager_authorities"] == list(stage.eager_authorities())
    assert stage.to_staged_loading_payload(manifest.workflow_id) == before
    assert first["totals"]["eager_chars"] > 0
    assert all(len(entry["sha256"]) == 64 for entry in first["entries"])


def test_prompt_bom_selects_only_named_conditional_authorities() -> None:
    manifest = load_workflow_stage_manifest("plan-phase", specs_root=SPECS)
    stage = manifest.stage("checker_revision")
    condition = stage.conditional_authorities[0].when

    payload = build_stage_prompt_bom(
        "plan-phase",
        "checker_revision",
        selected_conditions=(condition,),
        specs_root=SPECS,
    )

    assert payload["eager_authorities"] == list(stage.eager_authorities(selected_conditions=(condition,)))
    selected = [entry for entry in payload["entries"] if entry["role"] == "conditional_selected"]
    assert selected
    assert all(entry["condition"] == condition and entry["eager"] is True for entry in selected)


def test_prompt_bom_cli_emits_raw_json() -> None:
    result = CliRunner().invoke(
        app,
        ["--raw", "diagnostics", "prompt-bom", "--workflow", "plan-phase", "--stage", "checker_revision"],
        catch_exceptions=False,
    )

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["workflow_id"] == "plan-phase"
    assert payload["stage_id"] == "checker_revision"
    assert payload["totals"]["eager_entry_count"] >= 1
