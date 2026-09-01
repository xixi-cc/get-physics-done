"""Opt-in main-context planning contracts."""

from pathlib import Path

from gpd.core.config import CognitiveProfile, GPDProjectConfig, supported_config_keys
from gpd.core.workflow_staging import load_workflow_stage_manifest

ROOT = Path(__file__).resolve().parents[2]
WORKFLOWS = ROOT / "src" / "gpd" / "specs" / "workflows"


def test_cognitive_profile_is_opt_in_and_configurable() -> None:
    assert GPDProjectConfig().cognitive_profile is CognitiveProfile.CLASSIC
    assert GPDProjectConfig(cognitive_profile="base-model-first").cognitive_profile is CognitiveProfile.BASE_MODEL_FIRST
    assert "cognitive_profile" in supported_config_keys()


def test_planner_stage_receives_cognitive_profile_without_changing_earlier_stages() -> None:
    manifest = load_workflow_stage_manifest("plan-phase")

    assert "cognitive_profile" not in manifest.stage("phase_bootstrap").required_init_fields
    assert "cognitive_profile" not in manifest.stage("research_routing").required_init_fields
    assert "cognitive_profile" in manifest.stage("planner_authoring").required_init_fields


def test_base_model_first_planning_keeps_contract_and_independence_boundaries() -> None:
    source = (WORKFLOWS / "plan-phase" / "planner-authoring.md").read_text(encoding="utf-8")

    assert "do not spawn `gpd-planner` merely to restate the planning task" in source
    assert "same scoped paths and validators" in source
    assert "proof policy" in source
    assert "checker risk route" in source
    assert "Do not invent a" in source
    assert "child id" in source
