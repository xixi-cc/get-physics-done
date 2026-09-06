from pathlib import Path

import pytest

from gpd import registry
from gpd.core.command_preflight import build_command_context_preflight

OPERATIONS = ("dimensional-analysis", "limiting-cases", "numerical-convergence", "sensitivity-analysis")


@pytest.mark.parametrize("operation", OPERATIONS)
def test_explicit_standalone_analysis_stays_in_workspace_and_is_read_only(tmp_path, operation):
    (tmp_path / "equation.md").write_text("u = v t")
    args = "--target u --params v,t" if operation == "sensitivity-analysis" else "equation.md"
    before = {p: p.read_bytes() for p in tmp_path.rglob("*") if p.is_file()}
    result = build_command_context_preflight(operation, cwd=tmp_path, arguments=args)
    assert result.passed and not result.project_exists
    assert any(c.name == "managed_output_root" and "GPD/analysis" in c.detail for c in result.checks)
    assert before == {p: p.read_bytes() for p in tmp_path.rglob("*") if p.is_file()}


@pytest.mark.parametrize("operation", OPERATIONS)
def test_missing_standalone_inputs_fail_without_creating_project(tmp_path, operation):
    result = build_command_context_preflight(operation, cwd=tmp_path, arguments="")
    assert not result.passed
    assert not list(tmp_path.iterdir())


@pytest.mark.parametrize("operation", OPERATIONS[:3])
@pytest.mark.parametrize("target", ["3", "4.1", "02.3.1"])
def test_numeric_standalone_target_cannot_manufacture_phase(tmp_path, operation, target):
    result = build_command_context_preflight(operation, cwd=tmp_path, arguments=target)
    assert not result.passed
    assert any(c.name == "standalone_target" and c.blocking and not c.passed for c in result.checks)


@pytest.mark.parametrize("operation", OPERATIONS)
def test_shared_workflow_composition_preserves_method_and_output_authority(operation):
    source = Path(registry.__file__).parent / "specs"
    wrapper = (source / "workflows" / f"{operation}.md").read_text()
    expanded = registry._inline_model_visible_includes(wrapper)
    assert expanded.count("Shared execution for a selected technical-analysis operation") == 1
    assert "no STATE.md/state.json mutation" in expanded
    assert "stop if it fails" in expanded
    method = source / "references/analysis" / f"{operation}-method.md"
    assert method.is_file() and str(method.relative_to(source)) in wrapper
    assert "GPD/analysis/" in wrapper
    if operation == "dimensional-analysis":
        assert "${phase_dir}/" not in wrapper
    else:
        assert "${phase_dir}/" in wrapper
