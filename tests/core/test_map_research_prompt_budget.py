"""Prompt budget assertions for the `map-research` startup surface."""

from __future__ import annotations

from pathlib import Path

from tests.prompt_metrics_support import expanded_prompt_text, measure_prompt_surface

REPO_ROOT = Path(__file__).resolve().parents[2]
AGENTS_DIR = REPO_ROOT / "src" / "gpd" / "agents"
COMMANDS_DIR = REPO_ROOT / "src" / "gpd" / "commands"
WORKFLOWS_DIR = REPO_ROOT / "src" / "gpd" / "specs" / "workflows"
SOURCE_ROOT = REPO_ROOT / "src" / "gpd"
PATH_PREFIX = "/runtime/"
BOOTSTRAP_AUTHORITY = WORKFLOWS_DIR / "map-research" / "map-bootstrap.md"


def test_map_research_command_prompt_budget_stays_close_to_the_bootstrap_surface() -> None:
    command_text = (COMMANDS_DIR / "map-research.md").read_text(encoding="utf-8")
    metrics = measure_prompt_surface(
        COMMANDS_DIR / "map-research.md",
        src_root=SOURCE_ROOT,
        path_prefix=PATH_PREFIX,
    )
    bootstrap = measure_prompt_surface(
        BOOTSTRAP_AUTHORITY,
        src_root=SOURCE_ROOT,
        path_prefix=PATH_PREFIX,
    )

    assert metrics.raw_include_count == 1
    assert "@{GPD_INSTALL_DIR}/workflows/map-research/map-bootstrap.md" in command_text
    assert "@{GPD_INSTALL_DIR}/workflows/map-research.md" not in command_text
    assert "@{GPD_INSTALL_DIR}/references/orchestration/runtime-delegation-note.md" not in command_text
    assert metrics.expanded_line_count > bootstrap.expanded_line_count
    assert metrics.expanded_char_count > bootstrap.expanded_char_count
    assert metrics.expanded_line_count < bootstrap.expanded_line_count + 250
    assert metrics.expanded_char_count < bootstrap.expanded_char_count + 15000

    expanded_command = expanded_prompt_text(
        COMMANDS_DIR / "map-research.md",
        src_root=SOURCE_ROOT,
        path_prefix=PATH_PREFIX,
    )
    assert 'subagent_type="gpd-researcher"' not in expanded_command
    assert "references/orchestration/runtime-delegation-note.md" not in expanded_command


def test_researcher_project_map_mode_keeps_mapping_contract_compact() -> None:
    source = (AGENTS_DIR / "gpd-researcher.md").read_text(encoding="utf-8")

    assert "`project-map`" in source
    assert "read before writing" in source
    assert "stable locators" in source
    assert "`Not detected`" in source
    assert "## Mapping Complete" not in source


def test_researcher_does_not_load_mapping_minitextbook_by_default() -> None:
    source = (AGENTS_DIR / "gpd-researcher.md").read_text(encoding="utf-8")
    guidance = (
        REPO_ROOT / "src" / "gpd" / "specs" / "references" / "templates" / "research-mapper" / "MAPPING-GUIDANCE.md"
    )
    guidance_text = guidance.read_text(encoding="utf-8")

    assert "{GPD_INSTALL_DIR}/references/templates/research-mapper/MAPPING-GUIDANCE.md" not in source
    assert "Step 1: Read the model definition" not in source
    assert "Minimum section structures:" in guidance_text
    assert "## Worked Example" in guidance_text
    assert "## Broken Template Fallback" in guidance_text
