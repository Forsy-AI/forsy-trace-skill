# Forsy Trace Skill

[![npm version](https://img.shields.io/npm/v/forsy-trace-skill.svg)](https://www.npmjs.com/package/forsy-trace-skill)
[![npm downloads](https://img.shields.io/npm/dm/forsy-trace-skill.svg)](https://www.npmjs.com/package/forsy-trace-skill)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Structured traces for agent work experience.**

Forsy Trace Skill is an open skill for capturing AI agent workflows as structured, annotated trajectory data.

```bash
npx forsy-trace-skill init
```

It helps agents record the process behind completed work: task context, step traces, tool use, observations, reasoning signals, human feedback, failures, retries, artifacts, outcomes, and other learning signals.

Forsy is building a platform where AI agents exchange real-world work experience. This skill is the early open trace format behind that direction: a way to turn completed agent workflows into inspectable process data that can support evaluation, research, post-training, and reusable agent experience.

## Why structured agent traces matter

Agents increasingly work across tools, files, code, research environments, scientific workflows, legal analysis, product prototyping, and operational tasks.

The final output alone is not enough to understand what happened.

A useful agent work trace should capture:

- what the agent was trying to do
- what context and tools it had
- which actions it took
- what it observed after each action
- where it failed, retried, or corrected course
- what feedback shaped the work
- what artifact or outcome was produced
- what signals could be reused by future agents

Forsy Trace Skill gives those workflows a structured format.

## What is included

```text
skill.md
docs/schema.md
schema/forsy_trace_schema_v0_1.json
examples/
dataset/
scripts/
```

### `skill.md`

The open Forsy Trace Skill.

Use it as an instruction file for agents that need to produce structured traces of completed workflows.

### `schema/`

A JSON Schema for the public trace format.

### `examples/`

A seed set of structured text-based agent work traces across multiple workflow types.

Current examples include:

* molecular docking and computational drug discovery
* agentic product prototyping
* scientific computing
* applied math and code optimization
* legal and policy research
* structured legal drafting
* quantitative Hawkes process estimation
* injection moulding process optimization
* hardware/product planning

Each example is organized as:

```text
examples/<trace-slug>/
  manifest.json
  trace.json
```

### `dataset/`

Machine-readable JSONL exports:

```text
manifests.jsonl
traces.jsonl
steps.jsonl
normalization_report.json
```

### `scripts/`

Utilities for validation and export:

```text
validate_traces.py
build_jsonl_exports.py
normalize_traces.py
```

## Install locally

You can copy the skill and schema into your local agent project:

```bash
npx forsy-trace-skill init
```

By default, this creates:

```text
.forsy/trace-skill/
  skill.md
  schema/
    forsy_trace_schema_v0_1.json
```

Custom output path:

```bash
npx forsy-trace-skill init --out skills/forsy-trace-skill
```

Overwrite existing files:

```bash
npx forsy-trace-skill init --force
```

The installer only copies local files. It does not call external services, run a harness, or submit traces anywhere.

## Trace format

A Forsy trace is a structured record of an agent workflow.

A trace can include:

* `trace_id`
* `schema_version`
* `trace_mode`
* `task`
* `agent_tools`
* `system_prompt`
* `agent_config`
* `steps`
* `learning`
* `termination_reason`
* `final_output`
* `static_output`
* `summary`
* `dataset_summary`

Each step can include:

* actor
* action
* tool
* input
* output
* observation
* state change
* feedback
* retry relationship
* causal relationship
* local evaluation signal

See `docs/schema.md` for the full schema guide.

## Using the skill

A typical workflow:

1. Add `skill.md` to your agent environment.
2. Ask the agent to complete or reconstruct a real workflow.
3. Save the structured trace as `trace.json`.
4. Validate the trace.
5. Export traces into JSONL for downstream analysis.

Validate examples:

```bash
python3 scripts/validate_traces.py
```

Rebuild JSONL exports:

```bash
python3 scripts/build_jsonl_exports.py
```

## What this is useful for

Forsy Trace Skill is designed for:

* agent workflow inspection
* tool-use trajectory analysis
* process-supervision research
* agent evaluation
* failure and retry analysis
* annotated trajectory data construction
* workflow auditability
* reusable agent work experience

The included examples are text-based structured traces that demonstrate the format across different workflow types.

## Repository structure

```text
forsy-trace-skill/
  .gitignore
  CITATION.cff
  skill.md
  docs/
    schema.md
  schema/
    forsy_trace_schema_v0_1.json
  raw/
  examples/
  dataset/
    manifests.jsonl
    traces.jsonl
    steps.jsonl
    normalization_report.json
  scripts/
    normalize_traces.py
    validate_traces.py
    build_jsonl_exports.py
```

## Citation

If you use Forsy Trace Skill, please cite the repository using the metadata in `CITATION.cff`.

## License

See `LICENSE`.
