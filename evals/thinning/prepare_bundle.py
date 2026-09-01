"""Validate a thinning fixture and prepare a public-only, hash-backed run bundle."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

EXPECTED_CANARY_COUNTS = {
    "state_authority_recovery": 2,
    "deep_theory_proof": 4,
    "theory_construction": 3,
    "numerical_computation": 2,
    "source_writing_review": 1,
}
EXPECTED_MATRIX_COUNTS = {
    "state_authority_recovery": 8,
    "deep_theory_proof": 12,
    "theory_construction": 10,
    "numerical_computation": 6,
    "planning_execution_repair": 6,
    "source_writing_review": 6,
}
REQUIRED_PUBLIC_KEYS = {
    "id",
    "matrix_section",
    "capability",
    "prompt",
    "execution_mode",
    "allowed_writes",
    "network_policy",
    "required_artifacts",
    "zero_tolerance_tags",
}
REQUIRED_PRIVATE_KEYS = {
    "task_id",
    "expected_findings",
    "forbidden_outcomes",
    "theory_rubric",
    "load_bearing",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _read_jsonl(path: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}:{line_number}: invalid JSON: {exc}") from exc
        if not isinstance(value, dict):
            raise ValueError(f"{path}:{line_number}: expected an object")
        rows.append(value)
    return rows


def _fixture_configuration(fixture_dir: Path) -> tuple[list[Path], list[Path], dict[str, int]]:
    descriptor_path = fixture_dir / "fixture.json"
    if not descriptor_path.exists():
        return (
            [fixture_dir / "public.jsonl"],
            [fixture_dir / "private-oracles.jsonl"],
            EXPECTED_CANARY_COUNTS,
        )
    descriptor = json.loads(descriptor_path.read_text(encoding="utf-8"))
    if not isinstance(descriptor, dict):
        raise ValueError("fixture.json must contain an object")
    public_sources = [fixture_dir / str(value) for value in descriptor.get("public_sources", [])]
    private_sources = [fixture_dir / str(value) for value in descriptor.get("private_sources", [])]
    expected_counts = descriptor.get("expected_counts")
    if not public_sources or not private_sources or not isinstance(expected_counts, dict):
        raise ValueError("fixture.json must declare public_sources, private_sources, and expected_counts")
    return public_sources, private_sources, {str(key): int(value) for key, value in expected_counts.items()}


def validate_fixture(fixture_dir: Path) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    public_sources, private_sources, expected_counts = _fixture_configuration(fixture_dir)
    public = [row for source in public_sources for row in _read_jsonl(source)]
    private = [row for source in private_sources for row in _read_jsonl(source)]
    expected_total = sum(expected_counts.values())
    if len(public) != expected_total or len(private) != expected_total:
        raise ValueError(f"fixture must contain exactly {expected_total} public tasks and private oracles")
    for row in public:
        missing = REQUIRED_PUBLIC_KEYS - set(row)
        if missing:
            raise ValueError(f"public task {row.get('id')!r} misses {sorted(missing)}")
    for row in private:
        missing = REQUIRED_PRIVATE_KEYS - set(row)
        if missing:
            raise ValueError(f"private oracle {row.get('task_id')!r} misses {sorted(missing)}")
    public_ids = [str(row["id"]) for row in public]
    private_ids = [str(row["task_id"]) for row in private]
    if len(set(public_ids)) != len(public_ids) or set(public_ids) != set(private_ids):
        raise ValueError("public and private task IDs must be unique and identical")
    counts = Counter(str(row["matrix_section"]) for row in public)
    if dict(counts) != expected_counts:
        raise ValueError(f"unexpected fixture category counts: {dict(counts)}")
    expected_theory_count = expected_counts.get("theory_construction", 0)
    if sum(bool(row["theory_rubric"]) for row in private) != expected_theory_count:
        raise ValueError(f"exactly {expected_theory_count} tasks must use the theory rubric")
    return public, private


def prepare_bundle(fixture_dir: Path, output_dir: Path) -> dict[str, object]:
    public, _private = validate_fixture(fixture_dir)
    output_dir.mkdir(parents=True, exist_ok=False)
    public_target = output_dir / "tasks.jsonl"
    public_target.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in public), encoding="utf-8")
    manifest = {
        "schema_version": "gpd.thinning-eval-bundle.v1",
        "task_count": len(public),
        "task_ids": [row["id"] for row in public],
        "tasks_sha256": _sha256(public_target),
        "private_oracles_included": False,
        "network_policies": sorted({str(row["network_policy"]) for row in public}),
    }
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("fixture_dir", type=Path)
    parser.add_argument("output_dir", type=Path)
    args = parser.parse_args()
    print(json.dumps(prepare_bundle(args.fixture_dir, args.output_dir), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
