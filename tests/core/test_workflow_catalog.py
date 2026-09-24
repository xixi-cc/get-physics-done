import json
from pathlib import Path

import pytest

from gpd import registry
from gpd.adapters.codex import CodexAdapter
from gpd.adapters.install_utils import MANIFEST_NAME
from gpd.core.workflow_catalog import operation_group, workflow_catalog


def test_catalog_covers_each_canonical_operation_once():
    operations = [op for ops in workflow_catalog().values() for op in ops]
    assert len(operations) == len(set(operations))
    assert set(operations) == set(registry.list_commands())
    for operation in operations:
        assert registry.get_command(operation).context_mode
        assert registry.get_skill("gpd-" + operation).name
        assert operation_group("gpd:" + operation) == operation_group("gpd-" + operation)
    with pytest.raises(KeyError):
        operation_group("unregistered-operation")


def test_full_lean_full_migration_preserves_user_skill_and_operation_contracts(tmp_path):
    source = Path(registry.__file__).parent
    target, skills = tmp_path / ".codex", tmp_path / "skills"
    target.mkdir()
    skills.mkdir()
    custom = skills / "user-research" / "SKILL.md"
    custom.parent.mkdir()
    custom.write_text("user-owned")
    adapter = CodexAdapter()
    for profile in ["full", "lean", "full"]:
        adapter.install(source, target, skills_dir=skills, projection_profile=profile)
        assert custom.read_text() == "user-owned"
        assert adapter.has_complete_install(target)
        installed = {p.parent.name for p in skills.glob("gpd-*/SKILL.md")}
        manifest = json.loads((target / MANIFEST_NAME).read_text(encoding="utf-8"))
        expected = (
            {"gpd-" + x for x in registry.list_commands()}
            if profile == "full"
            else set(manifest["codex_explicit_only_skill_dirs"]) | {manifest["codex_projection_router_dir"]}
        )
        assert installed == expected
        # Retired native entries still resolve exact command policy and durable roots.
        for name in ["dimensional-analysis", "pause-work", "remove-phase", "review-knowledge"]:
            assert registry.get_skill("gpd-" + name).content
            assert registry.get_command(name).name == "gpd:" + name
