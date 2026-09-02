"""Run one or all bounded research smoke capsules."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from pydantic import TypeAdapter

from gpd.core.oracle_runner import OracleResult, OracleSpec, run_oracle

ROOT = Path(__file__).resolve().parent
CAPSULES = ROOT / "capsules"
_SPEC_ADAPTER = TypeAdapter(OracleSpec)


def _load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def _materialize_spec(template: dict[str, object], submission: object) -> OracleSpec:
    payload = dict(template)
    inject_submission = bool(payload.pop("inject_submission", False))
    observed_field = payload.pop("observed_field", None)
    if inject_submission:
        kwargs = dict(payload.get("kwargs", {}))
        kwargs["submission"] = submission
        payload["kwargs"] = kwargs
    if observed_field is not None:
        if not isinstance(submission, dict):
            raise ValueError("observed_field requires a JSON object submission")
        payload["observed"] = submission[str(observed_field)]
    return _SPEC_ADAPTER.validate_python(payload)


def run_capsule(capsule_id: str, *, variant: str = "reference") -> dict[str, object]:
    capsule_dir = CAPSULES / capsule_id
    manifest = _load_json(capsule_dir / "manifest.json")
    if not isinstance(manifest, dict):
        raise ValueError(f"{capsule_id}: manifest must be an object")
    submission_name = manifest.get(f"{variant}_submission")
    if not isinstance(submission_name, str):
        raise ValueError(f"{capsule_id}: unknown submission variant {variant!r}")
    submission_path = capsule_dir / submission_name
    submission = _load_json(submission_path)
    templates = manifest.get("oracles")
    if not isinstance(templates, list) or not templates:
        raise ValueError(f"{capsule_id}: oracles must be a non-empty array")
    results: list[OracleResult] = []
    for template in templates:
        if not isinstance(template, dict):
            raise ValueError(f"{capsule_id}: oracle template must be an object")
        results.append(run_oracle(_materialize_spec(template, submission), cwd=capsule_dir))
    passed = all(result.passed for result in results)
    return {
        "capsule_id": capsule_id,
        "variant": variant,
        "passed": passed,
        "results": [result.model_dump(mode="json") for result in results],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("capsule", nargs="?", choices=sorted(path.name for path in CAPSULES.iterdir() if path.is_dir()))
    parser.add_argument("--variant", choices=("reference", "adversarial"), default="reference")
    args = parser.parse_args()
    capsule_ids = [args.capsule] if args.capsule else sorted(path.name for path in CAPSULES.iterdir() if path.is_dir())
    payload = [run_capsule(capsule_id, variant=args.variant) for capsule_id in capsule_ids]
    print(json.dumps(payload, indent=2))
    return 0 if all(item["passed"] for item in payload) else 1


if __name__ == "__main__":
    raise SystemExit(main())
