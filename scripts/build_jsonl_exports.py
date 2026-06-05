#!/usr/bin/env python3
"""Build JSONL exports from normalized Forsy trace examples."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EXAMPLES_DIR = ROOT / "examples"
DATASET_DIR = ROOT / "dataset"
REPORT_PATH = DATASET_DIR / "normalization_report.json"


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def trace_id_for(manifest: dict[str, Any], trace: dict[str, Any]) -> Any:
    return (
        trace.get("trace_id")
        or manifest.get("trace_id")
        or trace.get("collection_id")
        or manifest.get("collection_id")
    )


def step_index_for(step: dict[str, Any], fallback: int) -> Any:
    value = step.get("step_index", step.get("step", fallback))
    return value if value is not None else fallback


def step_row(
    *,
    step: dict[str, Any],
    fallback_index: int,
    trace_id: Any,
    trace_slug: str,
    original_folder_name: Any,
) -> dict[str, Any]:
    row = {
        "trace_id": trace_id,
        "trace_slug": trace_slug,
        "original_folder_name": original_folder_name,
        "step_index": step_index_for(step, fallback_index),
        "actor": step.get("actor"),
        "action": step.get("action"),
        "tool": step.get("tool"),
        "input": step.get("input"),
        "output": step.get("output"),
        "observation": step.get("observation"),
        "state_change": step.get("state_change"),
        "eval": step.get("eval"),
        "feedback": step.get("feedback", step.get("feedback_content")),
        "caused_by": step.get("caused_by"),
        "retry_of": step.get("retry_of"),
    }
    for optional in (
        "turn",
        "operation",
        "execution_mode",
        "parallel_group",
        "input_source",
        "reasoning",
        "causal_type",
        "causal_note",
        "success",
        "eval_reason",
        "directive",
        "message_role",
        "feedback_type",
        "started_at",
        "ended_at",
    ):
        if optional in step:
            row[optional] = step.get(optional)
    return row


def build_exports() -> dict[str, int]:
    DATASET_DIR.mkdir(parents=True, exist_ok=True)
    manifests: list[dict[str, Any]] = []
    traces: list[dict[str, Any]] = []
    steps: list[dict[str, Any]] = []

    for example_dir in sorted(p for p in EXAMPLES_DIR.glob("*") if p.is_dir()):
        manifest_path = example_dir / "manifest.json"
        trace_path = example_dir / "trace.json"
        if not manifest_path.exists() or not trace_path.exists():
            continue

        manifest = load_json(manifest_path)
        trace = load_json(trace_path)
        trace_slug = trace.get("trace_slug") or manifest.get("trace_slug") or example_dir.name
        original_folder_name = trace.get("original_folder_name") or manifest.get("original_folder_name")
        trace_id = trace_id_for(manifest, trace)

        manifest_record = dict(manifest)
        manifest_record["trace_slug"] = trace_slug
        manifest_record["trace_id"] = trace_id
        manifest_record["original_folder_name"] = original_folder_name
        manifest_record.setdefault("source_trace_id", trace.get("source_trace_id") or manifest.get("source_trace_id"))
        manifests.append(manifest_record)

        trace_record = dict(trace)
        trace_record["trace_slug"] = trace_slug
        trace_record["trace_id"] = trace_id
        trace_record["original_folder_name"] = original_folder_name
        trace_record.setdefault("source_trace_id", trace.get("source_trace_id") or manifest.get("source_trace_id"))
        traces.append(trace_record)

        trace_steps = trace.get("steps")
        if isinstance(trace_steps, list):
            for idx, step in enumerate(trace_steps, start=1):
                if isinstance(step, dict):
                    row = step_row(
                        step=step,
                        fallback_index=idx,
                        trace_id=trace_id,
                        trace_slug=trace_slug,
                        original_folder_name=original_folder_name,
                    )
                    row["source_trace_id"] = trace.get("source_trace_id") or manifest.get("source_trace_id")
                    steps.append(row)

    write_jsonl(DATASET_DIR / "manifests.jsonl", manifests)
    write_jsonl(DATASET_DIR / "traces.jsonl", traces)
    write_jsonl(DATASET_DIR / "steps.jsonl", steps)

    counts = {
        "manifests": len(manifests),
        "traces": len(traces),
        "steps": len(steps),
    }

    if REPORT_PATH.exists():
        report = load_json(REPORT_PATH)
        report["export_counts"] = counts
        REPORT_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")

    return counts


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    counts = build_exports()
    print(
        "Exported {manifests} manifest records, {traces} trace records, and {steps} step records.".format(
            **counts
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
