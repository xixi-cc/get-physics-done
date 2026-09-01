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


def validate_fixture(fixture_dir: Path) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    public_path = fixture_dir / "public.jsonl"
    private_path = fixture_dir / "private-oracles.jsonl"
    public = _read_jsonl(public_path)
    private = _read_jsonl(private_path)
    if len(public) != 12 or len(private) != 12:
        raise ValueError("canary-v1 must contain exactly 12 public tasks and 12 private oracles")
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
    if dict(counts) != EXPECTED_CANARY_COUNTS:
        raise ValueError(f"unexpected canary category counts: {dict(counts)}")
    if sum(bool(row["theory_rubric"]) for row in private) != 3:
        raise ValueError("exactly three canaries must use the theory rubric")
    return public, private


def prepare_bundle(fixture_dir: Path, output_dir: Path) -> dict[str, object]:
    public, _private = validate_fixture(fixture_dir)
    output_dir.mkdir(parents=True, exist_ok=False)
    public_source = fixture_dir / "public.jsonl"
    public_target = output_dir / "tasks.jsonl"
    public_target.write_bytes(public_source.read_bytes())
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
