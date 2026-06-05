#!/usr/bin/env python3
"""Normalize raw Forsy trace folders into public examples."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "raw"
EXAMPLES_DIR = ROOT / "examples"
DATASET_DIR = ROOT / "dataset"
REPORT_PATH = DATASET_DIR / "normalization_report.json"

GENERATED_DIRS = {
    ".git",
    ".github",
    "dataset",
    "docs",
    "examples",
    "raw",
    "schema",
    "scripts",
}

TRACE_TOP_LEVEL_FIELDS = {
    "schema_version",
    "trace_id",
    "source_trace_id",
    "collection_id",
    "prior_trace_id",
    "prior_collection_id",
    "trace_slug",
    "original_folder_name",
    "source_folder_names",
    "trace_mode",
    "task",
    "agent_model",
    "agent_tools",
    "captured_at",
    "started_at",
    "ended_at",
    "system_prompt",
    "skills",
    "memory",
    "agent_config",
    "steps",
    "learning",
    "termination_reason",
    "final_output",
    "static_output",
    "summary",
    "dataset_summary",
    "source_files",
}

STEP_FIELDS = {
    "step",
    "step_index",
    "turn",
    "actor",
    "action",
    "operation",
    "tool",
    "execution_mode",
    "parallel_group",
    "observation",
    "input",
    "input_source",
    "output",
    "state_change",
    "reasoning",
    "caused_by",
    "causal_type",
    "causal_note",
    "alternatives_considered",
    "success",
    "eval",
    "eval_reason",
    "directive",
    "message_role",
    "feedback",
    "feedback_type",
    "feedback_content",
    "started_at",
    "ended_at",
    "retry_of",
}


def load_json(path: Path) -> dict[str, Any] | list[Any] | None:
    try:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")


def canonical_hash(data: dict[str, Any]) -> str:
    canonical = json.dumps(data, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def is_candidate_source_dir(path: Path) -> bool:
    if not path.is_dir() or path.name in GENERATED_DIRS or path.name.startswith("."):
        return False
    return any(child.suffix.lower() == ".json" for child in path.iterdir() if child.is_file())


def bootstrap_raw(copy_report: list[dict[str, Any]]) -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    for source_dir in sorted(p for p in ROOT.iterdir() if is_candidate_source_dir(p)):
        target_dir = RAW_DIR / source_dir.name
        if target_dir.exists():
            copy_report.append(
                {
                    "source": source_dir.name,
                    "raw_target": str(target_dir.relative_to(ROOT)),
                    "status": "already_present",
                }
            )
            continue
        shutil.copytree(source_dir, target_dir)
        copy_report.append(
            {
                "source": source_dir.name,
                "raw_target": str(target_dir.relative_to(ROOT)),
                "status": "copied",
            }
        )


def classify_json_file(path: Path, data: Any) -> str:
    if not isinstance(data, dict):
        return "unmatched"
    if isinstance(data.get("steps"), list):
        return "trace"
    manifest_signals = {
        "formats_available",
        "total_steps",
        "total_turns",
        "positive_pct",
        "activity_started_at",
        "activity_ended_at",
    }
    if manifest_signals.intersection(data.keys()):
        return "manifest"
    if "final_output" in data or "static_output" in data:
        return "trace"
    if path.name.lower() == "manifest.json":
        return "manifest"
    if path.name.lower() in {"data.json", "trace.json"}:
        return "trace"
    return "unmatched"


def pair_folder(folder: Path) -> tuple[Path | None, Path | None, list[str], list[str]]:
    trace_candidates: list[Path] = []
    manifest_candidates: list[Path] = []
    unmatched: list[str] = []
    assumptions: list[str] = []

    for path in sorted(folder.glob("*.json")):
        data = load_json(path)
        kind = classify_json_file(path, data)
        if kind == "trace":
            trace_candidates.append(path)
        elif kind == "manifest":
            manifest_candidates.append(path)
        else:
            unmatched.append(str(path.relative_to(ROOT)))

    trace_path = trace_candidates[0] if trace_candidates else None
    manifest_path = manifest_candidates[0] if manifest_candidates else None
    if len(trace_candidates) > 1:
        assumptions.append(f"{folder.name}: selected {trace_path.name} as trace from {len(trace_candidates)} candidates.")
    if len(manifest_candidates) > 1:
        assumptions.append(f"{folder.name}: selected {manifest_path.name} as manifest from {len(manifest_candidates)} candidates.")
    if trace_path and manifest_path:
        assumptions.append(f"{folder.name}: paired trace and manifest by raw folder grouping.")
    elif trace_path:
        assumptions.append(f"{folder.name}: trace found without matching manifest.")
    elif manifest_path:
        assumptions.append(f"{folder.name}: manifest found without matching trace.")

    return trace_path, manifest_path, unmatched, assumptions


def compact_text(value: Any) -> str:
    if isinstance(value, str):
        return value.lower()
    if isinstance(value, dict):
        return " ".join(compact_text(v) for v in value.values())
    if isinstance(value, list):
        return " ".join(compact_text(v) for v in value)
    return ""


def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = re.sub(r"-+", "-", text).strip("-")
    return text[:90].strip("-")


def infer_slug(manifest: dict[str, Any], trace: dict[str, Any], folder_name: str) -> str:
    text = " ".join(
        compact_text(value)
        for value in (
            trace.get("task"),
            manifest.get("task"),
            trace.get("summary"),
            trace.get("final_output"),
            manifest.get("goal_notes"),
        )
    )
    patterns = [
        (("autodock", "vina", "combinatorial"), "autodock-vina-combinatorial-docking-workflow"),
        (("braf", "v600e", "docking"), "braf-v600e-docking-pipeline-trace"),
        (("laptop", "shopping", "prototype"), "agentic-commerce-workflow-prototyping"),
        (("pollard", "rho"), "applied-math-code-optimization-trace"),
        (("metropolis", "hastings"), "metropolis-hastings-scientific-computing-trace"),
        (("hawkes", "quant"), "quantitative-hawkes-estimation-workflow"),
        (("shareholders", "non-compete"), "structured-legal-drafting-analysis-trace"),
        (("cfo", "resignation", "ontario"), "ontario-employment-law-analysis-trace"),
        (("injection", "moulder"), "injection-moulding-process-optimization-trace"),
        (("tablet app", "energy company"), "energy-tablet-app-waterfall-planning-trace"),
    ]
    for needles, slug in patterns:
        if all(needle in text for needle in needles):
            return slug

    task = trace.get("task") or manifest.get("task")
    if isinstance(task, str) and task.strip():
        words = [
            word
            for word in re.findall(r"[a-zA-Z0-9]+", task.lower())
            if word not in {"the", "and", "for", "with", "into", "from", "this", "that", "using", "create"}
        ]
        candidate = slugify("-".join(words[:8]) + "-agent-workflow")
        if candidate:
            return candidate
    return slugify(f"{folder_name}-agent-workflow")


def unique_slug(base_slug: str, trace_id: Any, counts: Counter[str]) -> str:
    counts[base_slug] += 1
    if counts[base_slug] == 1:
        return base_slug
    suffix_source = str(trace_id or counts[base_slug]).replace("fsy_c_", "")
    suffix = slugify(suffix_source)[:12] or str(counts[base_slug])
    candidate = f"{base_slug}-{suffix}"
    if counts[base_slug] > 2:
        candidate = f"{candidate}-{counts[base_slug]}"
    return candidate


def normalize_id_fields(record: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(record)
    if "trace_id" not in normalized and normalized.get("collection_id") is not None:
        normalized["trace_id"] = normalized.get("collection_id")
    if "prior_trace_id" not in normalized and "prior_collection_id" in normalized:
        prior = normalized.get("prior_collection_id")
        normalized["prior_trace_id"] = prior if prior not in ("", None) else None
    return normalized


def infer_actor(step: dict[str, Any]) -> str | None:
    if step.get("actor"):
        return step.get("actor")
    action = step.get("action")
    if action == "user_message":
        return "user"
    if action:
        return "agent"
    return None


def normalize_trace(
    trace: dict[str, Any],
    manifest: dict[str, Any],
    *,
    slug: str,
    original_folder_name: str,
    source_folder_names: list[str],
    trace_source: Path,
    manifest_source: Path | None,
) -> dict[str, Any]:
    normalized = normalize_id_fields(trace)
    source_trace_id = trace.get("trace_id") or trace.get("collection_id") or manifest.get("trace_id") or manifest.get("collection_id")
    normalized["source_trace_id"] = source_trace_id
    if "schema_version" not in normalized and manifest.get("schema_version") is not None:
        normalized["schema_version"] = manifest.get("schema_version")
    if "trace_mode" not in normalized and manifest.get("trace_mode") is not None:
        normalized["trace_mode"] = manifest.get("trace_mode")
    normalized["trace_slug"] = slug
    normalized["original_folder_name"] = original_folder_name
    normalized["source_folder_names"] = source_folder_names
    normalized["source_files"] = {
        "trace": str(trace_source.relative_to(ROOT)),
        "manifest": str(manifest_source.relative_to(ROOT)) if manifest_source else None,
    }

    steps = normalized.get("steps")
    if isinstance(steps, list):
        normalized_steps: list[Any] = []
        for idx, step in enumerate(steps, start=1):
            if not isinstance(step, dict):
                normalized_steps.append(step)
                continue
            normalized_step = dict(step)
            normalized_step.setdefault("step_index", normalized_step.get("step", idx))
            actor = infer_actor(normalized_step)
            if actor is not None:
                normalized_step["actor"] = actor
            normalized_steps.append(normalized_step)
        normalized["steps"] = normalized_steps
    return normalized


def normalize_manifest(
    manifest: dict[str, Any],
    trace: dict[str, Any],
    *,
    slug: str,
    original_folder_name: str,
    source_folder_names: list[str],
    trace_source: Path,
    manifest_source: Path | None,
) -> dict[str, Any]:
    normalized = normalize_id_fields(manifest)
    source_trace_id = trace.get("trace_id") or trace.get("collection_id") or manifest.get("trace_id") or manifest.get("collection_id")
    normalized["source_trace_id"] = source_trace_id
    if "schema_version" not in normalized and trace.get("schema_version") is not None:
        normalized["schema_version"] = trace.get("schema_version")
    if "task" not in normalized and trace.get("task") is not None:
        normalized["task"] = trace.get("task")
    if "trace_mode" not in normalized and trace.get("trace_mode") is not None:
        normalized["trace_mode"] = trace.get("trace_mode")
    normalized["trace_slug"] = slug
    normalized["original_folder_name"] = original_folder_name
    normalized["source_folder_names"] = source_folder_names
    normalized["source_files"] = {
        "trace": str(trace_source.relative_to(ROOT)),
        "manifest": str(manifest_source.relative_to(ROOT)) if manifest_source else None,
    }
    return normalized


def detect_schema_differences(traces: list[dict[str, Any]]) -> dict[str, Any]:
    top_level_keys: dict[str, list[str]] = defaultdict(list)
    unknown_top_level: dict[str, list[str]] = {}
    unknown_step_fields: dict[str, list[str]] = {}
    missing_core_fields: dict[str, list[str]] = {}
    legacy_mappings: list[str] = []
    trace_ids: list[Any] = []

    for trace in traces:
        slug = str(trace.get("trace_slug"))
        trace_ids.append(trace.get("trace_id") or trace.get("collection_id"))
        for key in trace.keys():
            top_level_keys[key].append(slug)
        unknown = sorted(key for key in trace.keys() if key not in TRACE_TOP_LEVEL_FIELDS)
        if unknown:
            unknown_top_level[slug] = unknown
        missing = sorted(key for key in ("schema_version", "task", "steps") if key not in trace)
        if not (trace.get("trace_id") or trace.get("collection_id")):
            missing.append("trace_id_or_collection_id")
        if missing:
            missing_core_fields[slug] = missing
        if "collection_id" in trace:
            legacy_mappings.append(f"{slug}: collection_id mapped to trace_id")
        if "prior_collection_id" in trace:
            legacy_mappings.append(f"{slug}: prior_collection_id mapped to prior_trace_id")

        steps = trace.get("steps")
        if isinstance(steps, list):
            unknown_steps = sorted(
                {
                    key
                    for step in steps
                    if isinstance(step, dict)
                    for key in step.keys()
                    if key not in STEP_FIELDS
                }
            )
            if unknown_steps:
                unknown_step_fields[slug] = unknown_steps

    duplicate_ids = sorted(str(item) for item, count in Counter(trace_ids).items() if item and count > 1)
    return {
        "top_level_field_inventory": {key: sorted(set(value)) for key, value in sorted(top_level_keys.items())},
        "unknown_top_level_fields_allowed": unknown_top_level,
        "unknown_step_fields_allowed": unknown_step_fields,
        "missing_core_fields": missing_core_fields,
        "legacy_mappings": sorted(set(legacy_mappings)),
        "duplicate_trace_ids": duplicate_ids,
    }


def normalize(force: bool) -> dict[str, Any]:
    DATASET_DIR.mkdir(parents=True, exist_ok=True)
    EXAMPLES_DIR.mkdir(parents=True, exist_ok=True)
    if force:
        for existing_example in EXAMPLES_DIR.iterdir():
            if existing_example.is_dir():
                shutil.rmtree(existing_example)
    copy_report: list[dict[str, Any]] = []
    bootstrap_raw(copy_report)

    raw_folders = sorted(p for p in RAW_DIR.iterdir() if p.is_dir())
    slug_counts: Counter[str] = Counter()
    mapping: dict[str, str] = {}
    generated_public_slugs: list[str] = []
    normalized_traces: list[dict[str, Any]] = []
    unmatched_files: list[str] = []
    assumptions: list[str] = []
    manifests_found = 0
    traces_found = 0
    normalized_examples = 0
    raw_trace_id_by_folder: dict[str, Any] = {}
    final_public_trace_ids: dict[str, Any] = {}
    duplicate_content_resolution: list[dict[str, Any]] = []
    candidate_records: list[dict[str, Any]] = []

    for folder in raw_folders:
        trace_path, manifest_path, folder_unmatched, folder_assumptions = pair_folder(folder)
        unmatched_files.extend(folder_unmatched)
        assumptions.extend(folder_assumptions)
        if manifest_path:
            manifests_found += 1
        if trace_path:
            traces_found += 1
        if not trace_path:
            continue

        trace_data = load_json(trace_path)
        manifest_data = load_json(manifest_path) if manifest_path else {}
        if not isinstance(trace_data, dict):
            unmatched_files.append(str(trace_path.relative_to(ROOT)))
            continue
        if not isinstance(manifest_data, dict):
            manifest_data = {}
            if manifest_path:
                unmatched_files.append(str(manifest_path.relative_to(ROOT)))
        trace_id = trace_data.get("trace_id") or trace_data.get("collection_id") or manifest_data.get("trace_id") or manifest_data.get("collection_id")
        raw_trace_id_by_folder[folder.name] = trace_id
        candidate_records.append(
            {
                "folder": folder,
                "trace_path": trace_path,
                "manifest_path": manifest_path,
                "trace_data": trace_data,
                "manifest_data": manifest_data,
                "trace_id": trace_id,
                "content_hash": canonical_hash(trace_data),
            }
        )

    records_by_hash: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in candidate_records:
        records_by_hash[record["content_hash"]].append(record)

    seen_hash_to_slug: dict[str, str] = {}
    for record in candidate_records:
        folder = record["folder"]
        trace_path = record["trace_path"]
        manifest_path = record["manifest_path"]
        trace_data = record["trace_data"]
        manifest_data = record["manifest_data"]
        trace_id = record["trace_id"]
        content_hash = record["content_hash"]
        duplicate_group = records_by_hash[content_hash]
        source_folder_names = [str(item["folder"].name) for item in duplicate_group]

        if content_hash in seen_hash_to_slug:
            kept_slug = seen_hash_to_slug[content_hash]
            mapping[folder.name] = kept_slug
            duplicate_content_resolution.append(
                {
                    "source_trace_id": trace_id,
                    "content_hash": content_hash,
                    "duplicate_raw_folder": folder.name,
                    "kept_public_slug": kept_slug,
                    "kept_raw_folder": source_folder_names[0],
                    "resolution": "exact_duplicate_content_skipped_public_example",
                }
            )
            continue

        base_slug = infer_slug(manifest_data, trace_data, folder.name)
        slug = unique_slug(base_slug, trace_id, slug_counts)
        seen_hash_to_slug[content_hash] = slug
        example_dir = EXAMPLES_DIR / slug
        if example_dir.exists() and not force:
            raise FileExistsError(f"{example_dir} exists; pass --force to overwrite normalized examples.")
        if example_dir.exists() and force:
            shutil.rmtree(example_dir)
        example_dir.mkdir(parents=True, exist_ok=True)

        normalized_trace = normalize_trace(
            trace_data,
            manifest_data,
            slug=slug,
            original_folder_name=folder.name,
            source_folder_names=source_folder_names,
            trace_source=trace_path,
            manifest_source=manifest_path,
        )
        normalized_manifest = normalize_manifest(
            manifest_data,
            trace_data,
            slug=slug,
            original_folder_name=folder.name,
            source_folder_names=source_folder_names,
            trace_source=trace_path,
            manifest_source=manifest_path,
        )

        write_json(example_dir / "trace.json", normalized_trace)
        write_json(example_dir / "manifest.json", normalized_manifest)

        mapping[folder.name] = slug
        generated_public_slugs.append(slug)
        final_public_trace_ids[slug] = normalized_trace.get("trace_id") or normalized_trace.get("collection_id")
        normalized_traces.append(normalized_trace)
        normalized_examples += 1

    report = {
        "raw_folders_found": len(raw_folders),
        "original_folder_names": [folder.name for folder in raw_folders],
        "raw_copy_report": copy_report,
        "generated_public_slugs": generated_public_slugs,
        "original_folder_to_public_example": mapping,
        "final_public_trace_ids": final_public_trace_ids,
        "original_source_trace_ids": raw_trace_id_by_folder,
        "traces_found": traces_found,
        "manifests_found": manifests_found,
        "normalized_examples": normalized_examples,
        "schema_differences_detected": detect_schema_differences(normalized_traces),
        "duplicate_trace_id_resolution": duplicate_content_resolution,
        "unmatched_files": sorted(set(unmatched_files)),
        "assumptions_made_while_pairing_files": sorted(set(assumptions)),
        "export_counts": {
            "manifests": 0,
            "traces": 0,
            "steps": 0,
        },
        "validation_warning_summary": {},
    }
    write_json(REPORT_PATH, report)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true", help="Overwrite existing normalized examples.")
    args = parser.parse_args()
    report = normalize(force=args.force)
    print(
        "Normalized {normalized_examples} examples from {traces_found} traces and {manifests_found} manifests.".format(
            **report
        )
    )
    print(f"Wrote {REPORT_PATH.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
