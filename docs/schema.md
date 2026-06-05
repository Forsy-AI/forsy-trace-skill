# Forsy Trace Schema

Forsy Trace Skill captures structured agent work traces: process data from real agent workflows, including user instructions, observations, tool-use trajectories, retries, feedback signals, state changes, and final outcomes. The seed examples are text-based traces organized into a stable public structure for agent engineers, evaluation researchers, post-training researchers, and data infrastructure builders.

The public schema is defined in `schema/forsy_trace_schema_v0_1.json`. It describes the common trace shape while allowing optional legacy fields so earlier traces remain usable.

## Repository Trace Layout

Each normalized example lives under:

```text
examples/<trace-slug>/
  manifest.json
  trace.json
```

Raw source files are preserved under `raw/` using their original folder and file names. Normalized examples are copies; raw inputs are not edited.

## Top-Level Trace Fields

Core fields:

- `schema_version`: Schema version or preserved legacy schema marker.
- `trace_id`: Canonical trace identifier. When a legacy trace used `collection_id`, the normalized copy maps that value into `trace_id`.
- `collection_id`: Legacy identifier preserved for compatibility.
- `prior_trace_id`: Canonical prior-trace pointer for continuations.
- `prior_collection_id`: Legacy prior-collection pointer preserved for compatibility.
- `trace_slug`: Public filesystem-safe example slug.
- `original_folder_name`: Original raw folder name.
- `trace_mode`: Capture mode, usually `live`, `retraced`, or `hybrid`.
- `task`: The work objective captured by the trace.
- `agent_model`: Model information when available.
- `agent_tools`: Tools available to or used by the agent.
- `started_at` and `ended_at`: Activity timestamps when available.
- `system_prompt`: System prompt or relevant instruction context when included in the source.
- `skills`: Skills or local instructions available to the agent.
- `memory`: Memory or retained context used by the agent.
- `agent_config`: Agent configuration details when present.
- `steps`: Ordered process nodes for the trace.
- `learning`: Outcome, lesson, or reusable experience annotations.
- `termination_reason`: Why the trace ended.
- `final_output`: Final user-facing or durable output.
- `static_output`: Static artifact-like output when present.
- `summary`: Trace-level summary and outcome annotation.
- `dataset_summary`: Dataset-level summary when present in a source trace.

The schema allows `additionalProperties` so legacy trace fields are not discarded. Validation scripts warn about unknown fields rather than removing them.

## Step-Level Fields

Each step is a workflow node. Step records may include:

- `step` or `step_index`: Ordered position in the trace.
- `turn`: Conversation or interaction turn.
- `actor`: Actor responsible for the step, commonly `user` or `agent`.
- `action`: Action type, such as `user_message`, file read, command execution, edit, or tool call.
- `operation`: More specific operation label when present.
- `tool`: Tool, command, API, or interaction surface used.
- `execution_mode`: Sequential, parallel, retraced, or other execution metadata.
- `parallel_group`: Group identifier for parallel work.
- `observation`: Concrete state before the action.
- `input`: Input, prompt, command, request, or data used by the step.
- `input_source`: Source of the input when tracked.
- `output`: Tool result, response, produced text, error, or evidence.
- `state_change`: What changed after the action.
- `reasoning`: Rationale for the action when captured.
- `caused_by`: Prior step or steps that caused this step.
- `causal_type`: Type of causal relationship.
- `causal_note`: Human-readable causal explanation.
- `alternatives_considered`: Alternatives recorded by the agent.
- `success`: Whether the step succeeded.
- `eval`: Step-level evaluation label or score.
- `eval_reason`: Explanation for the evaluation label.
- `directive`: Instructional signal detected in the step.
- `message_role`: Role of a message step.
- `feedback` or `feedback_content`: Feedback attached to the step.
- `feedback_type`: Category of feedback.
- `started_at` and `ended_at`: Step timestamps.
- `retry_of`: Prior step that this step retries.

These fields support process-label views, failure/retry analysis, tool-use trajectory analysis, and feedback/outcome annotation without requiring every trace to contain every field.

## Manifest Fields

`manifest.json` provides trace-level indexing and summary metadata. Common fields include:

- `schema_version`
- `trace_id` or legacy `collection_id`
- `prior_trace_id` or legacy `prior_collection_id`
- `trace_slug`
- `original_folder_name`
- `trace_mode`
- `task`
- `captured_at`
- `total_steps`
- `total_turns`
- `positive_pct`
- `directive_signals`
- `agent_confidence`
- `goal_achieved`
- `goal_notes`
- `human_feedback`
- `formats_available`
- `activity_started_at`
- `activity_ended_at`
- `system_prompt`
- `skills`
- `memory`
- `agent_config`
- `learning`
- `termination_reason`

Manifest records are normalized copies of source metadata with legacy identifiers preserved.

## Legacy Field Mappings

The v0.1 normalizer applies lightweight compatibility mappings:

- `collection_id` -> `trace_id`
- `prior_collection_id` -> `prior_trace_id`

The original legacy fields remain in the normalized output. Empty legacy prior IDs are mapped to `null` in `prior_trace_id` so downstream tools can distinguish "no prior trace" from an omitted field.

Legacy `schema_version` values are preserved. If a source trace omits `schema_version` but its paired manifest includes one, the normalized trace inherits the manifest value.

## Optional and Required Fields

Required for normalized public traces:

- `schema_version`
- `task`
- `steps`
- either `trace_id` or legacy `collection_id`

Optional fields remain optional because historical traces can differ by capture mode, agent environment, tool surface, and available evidence. Optionality prevents data loss while still making the common structure explicit.

## JSONL Exports

The dataset export files are regenerated from `examples/`:

```text
dataset/manifests.jsonl
dataset/traces.jsonl
dataset/steps.jsonl
```

`manifests.jsonl` contains one normalized manifest record per trace.

`traces.jsonl` contains one normalized trace record per trace.

`steps.jsonl` contains one row per step. Every row includes:

- `trace_id`
- `trace_slug`
- `original_folder_name`
- `step_index`
- `actor`
- `action`
- `tool`
- `input`
- `output`
- `observation`
- `state_change`
- `eval`
- `feedback`
- `caused_by`
- `retry_of`

Additional step fields are preserved when present.

## Future Dataset Views

The trace format is designed to support several downstream views:

- Trajectory view: ordered user, agent, and tool-use steps for replay and inspection.
- SFT view: task context paired with successful final outputs or selected high-quality intermediate actions.
- Preference view: alternative attempts, corrections, retries, and feedback labels transformed into comparison records.
- Process-label view: step-level success, failure, retry, feedback, causality, and state-change annotations for evaluation or process supervision.

Forsy Trace Skill Seed demonstrates a structured format for capturing text-based agent work traces across multiple workflow types. The schema and exports provide a foundation for reusable agent work experience and future Agent Apprenticeship work.
