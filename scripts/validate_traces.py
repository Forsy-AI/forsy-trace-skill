#!/usr/bin/env python3
"""Validate normalized Forsy trace examples and report warnings."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EXAMPLES_DIR = ROOT / "examples"
SCHEMA_PATH = ROOT / "schema" / "forsy_trace_schema_v0_1.json"
REPORT_PATH = ROOT / "dataset" / "normalization_report.json"


CORE_FIELDS = ("schema_version", "task", "steps")
ID_FIELDS = ("trace_id", "collection_id")


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def ordered(values: list[int]) -> bool:
    return values == sorted(values)


def allowed_trace_fields(schema: dict[str, Any]) -> set[str]:
    return set(schema.get("properties", {}).keys())


def allowed_step_fields(schema: dict[str, Any]) -> set[str]:
    return set(schema.get("$defs", {}).get("step", {}).get("properties", {}).keys())


def validate_trace(
    example_dir: Path,
    schema: dict[str, Any],
    warnings: list[str],
    errors: list[str],
) -> bool:
    manifest_path = example_dir / "manifest.json"
    trace_path = example_dir / "trace.json"
    if not manifest_path.exists():
        errors.append(f"{example_dir.name}: missing manifest.json")
        return False
    if not trace_path.exists():
        errors.append(f"{example_dir.name}: missing trace.json")
        return False

    try:
        trace = load_json(trace_path)
    except json.JSONDecodeError as exc:
        errors.append(f"{example_dir.name}: trace.json is not valid JSON: {exc}")
        return False

    passed = True
    for field in CORE_FIELDS:
        if field not in trace:
            errors.append(f"{example_dir.name}: missing core trace field {field}")
            passed = False
    if not any(field in trace for field in ID_FIELDS):
        errors.append(f"{example_dir.name}: missing trace_id or legacy collection_id")
        passed = False

    steps = trace.get("steps")
    if not isinstance(steps, list) or not steps:
        errors.append(f"{example_dir.name}: trace has no steps")
        passed = False
    elif all(isinstance(step, dict) for step in steps):
        step_numbers: list[int] = []
        for fallback_index, step in enumerate(steps, start=1):
            value = step.get("step_index", step.get("step", fallback_index))
            try:
                step_numbers.append(int(value))
            except (TypeError, ValueError):
                warnings.append(f"{example_dir.name}: step {fallback_index} has non-numeric step index {value!r}")
        if step_numbers and not ordered(step_numbers):
            warnings.append(f"{example_dir.name}: step indexes are not ordered")
    else:
        errors.append(f"{example_dir.name}: steps must be objects")
        passed = False

    top_allowed = allowed_trace_fields(schema)
    step_allowed = allowed_step_fields(schema)
    unknown_top = sorted(k for k in trace.keys() if k not in top_allowed)
    if unknown_top:
        warnings.append(f"{example_dir.name}: unknown top-level fields allowed by schema: {', '.join(unknown_top)}")

    if isinstance(steps, list):
        unknown_steps = sorted(
            {
                key
                for step in steps
                if isinstance(step, dict)
                for key in step.keys()
                if key not in step_allowed
            }
        )
        if unknown_steps:
            warnings.append(f"{example_dir.name}: unknown step fields allowed by schema: {', '.join(unknown_steps)}")

    return passed


def update_report(summary: dict[str, Any]) -> None:
    if not REPORT_PATH.exists():
        return
    report = load_json(REPORT_PATH)
    report["validation_warning_summary"] = summary
    REPORT_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--quiet", action="store_true", help="Only print the summary.")
    args = parser.parse_args()

    schema = load_json(SCHEMA_PATH)
    warnings: list[str] = []
    errors: list[str] = []
    checked = 0
    passed = 0
    public_trace_ids: dict[str, str] = {}

    for example_dir in sorted(p for p in EXAMPLES_DIR.glob("*") if p.is_dir()):
        checked += 1
        trace_path = example_dir / "trace.json"
        if trace_path.exists():
            try:
                trace = load_json(trace_path)
                public_trace_id = trace.get("trace_id") or trace.get("collection_id")
                if public_trace_id:
                    public_trace_id = str(public_trace_id)
                    if public_trace_id in public_trace_ids:
                        errors.append(
                            f"{example_dir.name}: duplicate public trace_id {public_trace_id!r}; first seen in {public_trace_ids[public_trace_id]}"
                        )
                    else:
                        public_trace_ids[public_trace_id] = example_dir.name
            except json.JSONDecodeError:
                pass
        if validate_trace(example_dir, schema, warnings, errors):
            passed += 1

    summary = {
        "traces_checked": checked,
        "traces_passed": passed if not errors else max(0, checked - len({e.split(':', 1)[0] for e in errors})),
        "warnings": len(warnings),
        "errors": len(errors),
        "duplicate_public_trace_ids": max(0, checked - len(public_trace_ids)),
    }
    update_report(summary)

    if not args.quiet:
        for warning in warnings:
            print(f"WARNING: {warning}")
        for error in errors:
            print(f"ERROR: {error}")

    print(
        "Validation summary: traces checked={traces_checked}, traces passed={traces_passed}, duplicate public trace IDs={duplicate_public_trace_ids}, warnings={warnings}, errors={errors}".format(
            **summary
        )
    )
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
