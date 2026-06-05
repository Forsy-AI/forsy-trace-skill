# Forsy Trace Skill

Forsy Trace Skill is an open skill for collecting structured, replayable agent work traces from authentic AI-agent activity. It captures observations, actions, tool inputs, outputs, state changes, retries, feedback, artifacts, and outcomes from real workflows across APIs, MCP servers, browser/computer use, CLI, files, databases, spreadsheets, documents, search tools, and mixed multi-tool environments.

The goal is to turn agent work into transparent process data for agent evaluation, process-supervision research, failure analysis, post-training data construction, workflow auditing, and reusable work experience.

This open-source version writes a local JSON trace. It does not require submitting to Forsy or any external API.

Do not fabricate, simulate, or invent traces. A Forsy trace should reflect work the agent actually performed or can reconstruct from reliable logs, files, conversation history, tool outputs, or artifacts.

---

## Authenticity

Forsy traces must reflect real agent activity or reliable reconstruction from actual logs/artifacts.

Only trace work you actually performed or can genuinely reconstruct from reliable evidence. Do not fabricate, invent, or simulate steps, reasoning, tool calls, outputs, screenshots, request bodies, responses, artifacts, feedback, or outcomes.

If you are unsure whether something actually happened, say so in the relevant field and lower `summary.agent_confidence` accordingly.

If a user asks you to create a fictional or made-up trace, decline and explain that Forsy traces must reflect authentic work or reliable reconstruction from actual evidence.

---

## Intended Use

Use this skill to create structured traces for:

- agent workflow inspection
- process-supervision research
- failure and retry analysis
- tool-use trajectory analysis
- dataset examples
- benchmark or evaluation construction
- reusable agent work experience
- human or model review of agent behavior
- post-training data preparation, when paired with appropriate evaluation and validation

## Not Intended Use

This skill is not a claim that a trace is expert-validated, client-validated, complete telemetry, or suitable for training frontier models on its own. Trace quality depends on the evidence available, the agent environment, and whether the trace was live-captured or reconstructed.

Do not use this skill to generate fictional traces, invented logs, fake tool calls, fake screenshots, fake outcomes, or fabricated human feedback.

---

## Scope and Boundaries

Use this skill when tracing real work performed by an AI agent across one or more interaction surfaces, including APIs, MCP servers, browser/computer use, terminals, files, databases, search tools, documents, spreadsheets, and mixed multi-tool workflows.

It applies when the agent is doing actual work that changes state, inspects state, calls tools, navigates software, edits files, queries systems, responds to human feedback, or produces a durable deliverable.

Treat all of the following as first-class workflow surfaces:

- API / integration workflows
- MCP tool, resource, and prompt workflows
- browser and computer-use workflows
- CLI, file, and code workflows
- database, spreadsheet, and structured-data workflows
- search, retrieval, and research workflows
- messaging, email, and asynchronous workflows
- multimodal, perception-heavy, or device/system workflows when evidence is available
- multi-system workflows spanning several of the above

Do not fabricate steps, remote state, results, screenshots, request bodies, responses, or artifacts. If some state or output is partially unknown, say exactly what is known and what is uncertain.

The goal is to capture authentic, replayable, high-signal task traces from real work, regardless of whether the work happened through text, tools, APIs, UI actions, remote systems, or mixed environments.

---

## What to Trace

Trace the actual task work: the research, reasoning, tool calls, outputs, errors, user interactions, corrections, retries, and artifacts involved in completing the user's task.

Do not trace the trace-collection process itself.

Exclude steps whose only purpose is to satisfy trace administration, such as:

- reading or re-reading this skill file
- planning how to format the trace JSON
- validating the trace JSON
- writing local trace files
- preparing a release package
- submitting a trace to any API or platform
- committing trace files to a repository

Every user message that affected the work must be recorded as its own step. Do not skip user messages or summarize them inside the next agent step.

Each step must be one meaningful action. If you created five files, that is usually five steps. If you ran a command, read the output, and made a decision, that is at least three steps. Do not compress materially separate actions into one step.

---

## Trace Modes and Validation Levels

### trace_mode

One of:

- `live`: traced while the work was happening
- `retraced`: reconstructed after the work from logs, files, conversation history, or memory
- `hybrid`: mix of live tracing and reconstruction

Live traces usually have stronger evidence. Retraced traces may contain approximations and should use lower confidence where evidence is incomplete.

### validation_level

One of:

- `self_traced`: created by the agent or operator without external review
- `retraced_from_logs`: reconstructed from logs, artifacts, files, or conversation history
- `model_reviewed`: reviewed by a separate model/evaluator
- `human_reviewed`: checked by a human general reviewer
- `expert_reviewed`: checked or refined by a domain expert
- `client_validated`: validated by the actual task owner or beneficiary

Use the lowest validation level that accurately describes the trace. Do not imply expert or client validation unless it occurred.

---

## Step Nodes and Causality

Treat each step as a referable node in a workflow graph, not just a line in a timeline.

Every step should be understandable on its own, and later steps should make clear which earlier step or steps caused them. Use `caused_by`, `causal_type`, `causal_note`, and `retry_of` to make those links explicit.

If a step was triggered by a user request, prior tool result, correction, failed step, retry, verification need, earlier plan, subagent result, or multiple earlier steps together, record that relationship explicitly.

Do not force downstream users to infer the dependency chain from prose alone.

---

## Interaction Surface Rules

For every non-`user_message` step, make the interaction surface clear through `tool`, `observation`, `input`, `reasoning`, and `output`.

Use these surface categories conceptually when tracing:

- `api`
- `mcp_tool`
- `mcp_resource`
- `mcp_prompt`
- `browser`
- `computer_use`
- `cli`
- `file`
- `database`
- `spreadsheet`
- `search`
- `messaging`
- `other_tool`
- `other_surface`

You do not need to add a separate surface-type field, but the step should make the surface obvious from the content.

Examples:

- API call through `curl`, SDK, Postman, or internal client = `api`
- Calling an MCP-exposed function = `mcp_tool`
- Reading a schema, file, or context object from MCP = `mcp_resource`
- Using a templated MCP prompt = `mcp_prompt`
- Clicking, typing, navigating, or reading visible UI = `browser` or `computer_use`
- Shell command execution = `cli`
- Reading, writing, or modifying local files = `file`
- Querying or mutating a database table = `database`
- Editing or filtering structured tabular data = `spreadsheet`
- Messaging, email, async jobs, voice, video, mobile, cloud console, device control, or other emerging workflow surfaces = `other_surface`

When a workflow crosses surfaces, trace each meaningful action separately.

---

## State and Evidence Rules

`observation` should describe the concrete state before acting. State may be local, remote, visible, contextual, physical, or inferred from reliable system output.

Types of state to capture when relevant:

- local state: files, directories, repo contents, terminal state, local variables, active process
- remote state: CRM object, ticket, record, order, document, account, queue item, API object, database row
- visible state: page content, selected tab, modal open, field values, error banner, visible table row
- context state: docs/spec version loaded, MCP resource loaded, prompt template used, schema version known
- async state: job ID, webhook delivery state, queue depth, retry count, scheduler status, callback pending/completed
- media/perception state: image region, detected object, OCR output, transcript state, frame set, audio segment, processing stage
- device/system state: mobile app screen, VM/container status, cloud region, instance state, sensor reading, actuator state, device mode

`state_change` should describe what changed after the step.

Make clear whether the change happened:

- locally
- remotely
- visibly
- asynchronously
- physically or at the device/system level
- only in the agent's understanding
- not at all because the action failed

Prefer evidence over summary. When available, preserve the concrete proof of the result:

- exact API response
- exact tool return
- exact UI text
- exact error message
- exact file content or diff
- exact record ID, URL, request ID, job ID, event ID, artifact path, or other system identifier
- exact screenshot, log, transcript, media artifact, or device output when relevant

If a step verifies success, `output` should show what evidence confirmed the result.

---

## Observation vs Reasoning vs Causality

Keep these fields distinct:

- `observation` = concrete state before acting
- `reasoning` = why this was the right next action
- `causal_note` = which earlier step or steps directly caused this step and how

Use `observation` only for what was true before the action: files present or missing, exact error text already visible, current object state, tool availability, numeric values, counts, IDs, versions, or evidence already known.

Do not use `observation` for intentions, plans, causal explanations, or broad summaries. Those belong in `reasoning` or the causality fields.

---

## Machine Replay Guidance

Forsy traces should be structured so another system can reconstruct, verify, or approximate the workflow when enough information was available.

For any tool, file, API, browser, CLI, database, spreadsheet, or executable action, preserve concrete replay details using existing fields:

- `tool`: the specific tool or interface used
- `input`: the exact command, query, request, file path, browser action, API payload, or parameters
- `output`: the exact result, stdout, stderr, API response, file edit result, browser result, or error
- `observation`: what the result showed or meant
- `state_change`: what changed after the action
- `static_output`: artifacts, files, diffs, content, logs, screenshots, reports, hashes, or verification evidence
- `agent_config`: model, runtime, environment, repository, branch, commit, sandbox, internet access, available tools, tool definitions, function-calling protocol, tool constraints, and other replay context when available

Do not invent missing commands, outputs, diffs, hashes, commits, screenshots, logs, or environment details.

If exact replay is not possible, preserve enough evidence for approximate replay, verification, or training-use analysis.

---

## When to Finish a Trace

For retraced tasks, trace the entire activity from start to finish, including all rounds of feedback and iteration that occurred during the original work.

For live tasks, do not finish the trace after the first output if the work is still evolving. Real tasks often involve multiple rounds of feedback and iteration, and later rounds may contain the most valuable learning signals.

Finish the trace when one of the following is true:

- the task reached a natural terminal state
- the user confirmed the work was done
- the agent became blocked and could not proceed
- the session ended or was abandoned
- the trace is intentionally partial and marked as such

Set `termination_reason` accordingly:

- `task_complete`
- `user_confirmed_done`
- `agent_blocked`
- `timeout`
- `error_unrecoverable`
- `partial_then_stopped`
- `user_abandoned`
- `other`

Do not append trace administration as workflow steps.

---

## Top-Level Metadata Fields

Before tracing steps, record these top-level fields.

### schema_version

String. Use `forsy-trace-v0.1` for new open-source traces.

### trace_id

String. A stable unique ID for this trace, such as `forsy_trace_0001` or a UUID.

### prior_trace_id

String or null. If this trace continues or references an earlier trace, include that trace ID. Null if standalone.

### trace_mode

String. One of `live`, `retraced`, or `hybrid`.

### validation_level

String. One of `self_traced`, `retraced_from_logs`, `model_reviewed`, `human_reviewed`, `expert_reviewed`, or `client_validated`.

### task

String. The user's actual underlying work or workflow. Use the original user request when available. Do not replace it with trace-collection instructions.

### agent_tools

Array of strings. List every tool available in the session, not just tools used. This defines the action space.

### started_at

String or null. ISO 8601 timestamp when the activity began. For retraced tasks, use the best reliable timestamp from logs, files, or conversation history. Null if unknown.

### ended_at

String or null. ISO 8601 timestamp when the activity ended or the trace became ready for release. Null if genuinely unknown.

### system_prompt

String or null. Original system prompt or initial instructions when accessible and safe to include. Do not include private or sensitive system prompts. Use a hash or summary when safer.

### skills

Array of strings or null. Skill files, plugins, knowledge bases, custom instructions, or specialized capabilities loaded beyond the base model.

### memory

String or null. Persistent memory, saved context, or accumulated project context that materially shaped the work. Omit or summarize sensitive memory.

### agent_config

Object or null. Accessible model, runtime, environment, or provenance settings that shaped how the work was done.

Useful fields include:

- model
- temperature
- max_tokens
- top_p
- reasoning_effort
- framework
- agent or harness name
- agent version
- system prompt hash
- environment_type
- os_platform
- shell
- working_directory
- repository
- git_branch
- base_commit
- commit_sha
- python_version
- node_version
- package manager
- dependency/runtime versions
- memory_enabled
- internet_access
- sandboxed
- sandbox_mode
- containerized
- vm_or_desktop
- runtime_location
- response_style
- planning_enabled
- tool_choice_mode
- token usage, if available
- estimated cost, if available
- content hash, if available
- redaction or security tier, if available
- verification context
- orchestration context for multi-agent traces

Do not expose private system prompts, secrets, API keys, credentials, or sensitive environment values. Store hashes or summaries instead when useful.

### learning

String or null. The generalizable lesson, candidate behavior update, or reusable principle extracted from the entire workflow. It should capture what a future agent should repeat, avoid, verify, or do differently when facing similar tasks.

Good `learning` content can include:

- a better strategy for similar tasks
- a recurring failure pattern to avoid
- a useful verification habit
- a user preference that should shape future responses
- a domain-specific heuristic
- a tool-use or sequencing rule
- a reusable debugging, research, design, or execution principle

Do not claim that the lesson is universally true. Frame it as a candidate behavior update supported by this workflow.

### termination_reason

String. One of `task_complete`, `user_confirmed_done`, `user_abandoned`, `agent_blocked`, `timeout`, `error_unrecoverable`, `partial_then_stopped`, or `other`.

---

## Step Fields

For every step in the activity, record a JSON object with these fields.

### step

Integer. Sequential number starting from 1. Steps must be chronological.

### turn

Integer. Group related steps into turns. Increment when a new exchange starts, typically after a new `user_message` or a clear shift to a new subtask.

### actor

String. Who performed this step. Use stable actor labels consistently.

Allowed examples:

- `user`
- `agent`
- `subagent`
- `system`
- `agent:main`
- `agent:research_1`
- `agent:browser_1`
- `agent:codegen_1`
- `subagent:research_1`

### action

String. High-level step type. Exactly one of:

- `user_message`
- `agent_step`
- `output`
- `error`

Specific operations such as `read`, `write`, `search`, `execute`, `verify`, `ask_user`, or `answer` belong in `operation`, not `action`.

### operation

String or null. The specific operation performed in this step.

Suggested values:

- `plan`
- `analyze`
- `search`
- `read`
- `write`
- `edit`
- `execute`
- `verify`
- `download`
- `install`
- `ask_user`
- `answer`
- `select`
- `other`

For `user_message` steps, `operation` is null.

### tool

String or null. The specific tool, system, or interface used in this step. Use the most specific safe tool name, such as `web.run`, `Bash`, `python`, `browser`, `search`, `file_edit`, `api client`, `database`, `spreadsheet`, `screenshot tool`, or `mcp:server.tool_name`.

For function-calling traces, use the exact function or tool name exposed by the harness when available.

### execution_mode

String or null. One of:

- `serial`
- `parallel`

Use `parallel` when the step intentionally groups simultaneous or fanout operations under one top-level step. For `user_message` steps, use null.

### parallel_group

String or null. Shared identifier for steps that belong to the same parallel branch or grouped execution, such as `pg_001`. Null if not part of parallel work.

### observation

String or null. The concrete state, signal, or evidence visible or known at this point in the workflow.

Good `observation` content:

- files present or missing
- exact error messages already visible
- current UI or API state
- known IDs, counts, coordinates, schema versions, or relevant values
- installed or missing tools
- current queue, job, or device state
- tool result or system output available to the agent
- meaningful signal learned from a tool result
- execution constraints, unavailable capabilities, truncated outputs, missing files, disabled memory, missing tools, timeout limits, stdout caps, or other tool limitations learned from a result

For `user_message` steps, `observation` is null.

### input

String or null. The literal payload of this step.

- For `user_message` steps: the user's exact words in full
- For tool steps: the exact command, query, request, file path, browser action, API payload, parameters, or arguments sent
- For output steps: the exact answer, deliverable, or response content being produced
- For planning or analysis steps: the exact subject being reasoned about

Do not paraphrase. Do not summarize. Do not mix provenance, causal explanation, or evaluation into `input`.

### input_source

Object or null. Describes where the input for this step came from.

Preferred structure:

```json
{
  "actor": "user | agent | subagent | tool | system | external",
  "source_step": 1,
  "source_field": "input | output | observation | directive | feedback_content | external",
  "note": "short clarification"
}
```

Use `input_source` whenever the origin of the current input would otherwise be unclear.

### output

String or null. The exact returned result or produced deliverable for this step.

- For tool steps: stdout, stderr, API response, file content, return value, browser result, file edit result, test result, or exact error
- For output steps: the actual answer, recommendation, code, document text, or deliverable content
- For error steps: the exact error type, code, and message

If raw output is too long, include the most relevant excerpt and summarize what was omitted.

For `user_message` steps, `output` is null.

### state_change

String or null. What changed as a result of this step. Describe the concrete post-step change first.

Examples:

- `src/signup.tsx was modified to add signupSchema validation before form submission.`
- `The API request failed with 401, so no remote object was created.`
- `The test command completed and showed 3 passing tests.`
- `Agent understanding changed because the loaded docs revealed the v2 endpoint requires company_id.`

### reasoning

String or null. Why this was the right next action, given the current observation and context. Use `reasoning` for decision logic, not for repeating the action.

Good reasoning answers the question: why this step now, instead of a plausible alternative?

For `user_message` steps, `reasoning` is null.

### caused_by

Array of step numbers or null. Earlier steps that directly caused this step.

Use this whenever the step was triggered by a user request, prior tool result, correction, failed step, retry, verification need, earlier plan, subagent result, delegation, handoff, or multiple earlier steps.

### causal_type

String or null. Suggested values:

- `user_request`
- `follow_up_user_request`
- `answer_to_agent_question`
- `execution_of_plan`
- `dependency_on_tool_result`
- `retry_after_failure`
- `correction_response`
- `approval_response`
- `verification_of_prior_step`
- `dependency_on_multiple_prior_steps`
- `delegation_to_subagent`
- `delegated_work`
- `used_subagent_result`
- `handoff_from_subagent`
- `parallel_work`
- `other`

### causal_note

String or null. Short explanation of how earlier steps led to this step.

### alternatives_considered

String or null. Other meaningful actions the agent could have taken, and why it did not take them. Null only if the step was mechanical and there was no real choice.

### success

Boolean or null. True if the step worked as intended, false if it failed, null for `user_message` steps.

### eval

Integer. A weak process label / self-evaluation score for this step.

Allowed values:

- `+1`: positive
- `0`: neutral
- `-1`: negative

User message steps are always `0`.

Assign `+1` only if the step produced a concrete, useful, or verifiable result that moved the task closer to completion and did not require later correction.

Assign `-1` if the step produced an incorrect, misleading, incomplete, unusable, failed, wasteful, or later-disproven result.

Assign `0` only for user messages or genuinely neutral setup/inspection steps.

When later evidence shows an earlier step was wrong, update the earlier step to `-1`, add a `directive`, and connect the new correction step with `retry_of`.

### eval_reason

String or null. Brief explanation of why the step received its eval score. For `user_message` steps, null.

### directive

String or null. Hindsight guidance placed on an earlier step that failed or was corrected. It should explain what went wrong and what should be changed.

Do not use `directive` on `user_message` steps or on the initial user request.

### message_role

String or null. For `user_message` steps only. One of:

- `direct_request`
- `answer_to_agent_question`
- `correction`
- `approval`
- `clarification`
- `selection`
- `status_update`
- `new_constraint`
- `other`

### feedback_type

String or null. For `user_message` steps only. One of:

- `correction`
- `approval`
- `clarification`
- `new_instruction`
- `other`

### feedback_content

String or null. For `user_message` steps only. A normalized summary of what the user's feedback meant. Use this only when the message is acting as feedback or judgment.

Do not use `feedback_content` to restate the initial request.

### started_at

String or null. ISO 8601 timestamp when this step began. Null if unknown.

### ended_at

String or null. ISO 8601 timestamp when this step completed. Null if unknown.

### retry_of

Integer or null. Earlier step number this step retries, corrects, or redoes. Use only when the current step genuinely retries or corrects an earlier step.

---

## Hard Invariants for User Message Steps

For `user_message` steps:

- `actor` is always `user`
- `action` is always `user_message`
- `operation` is always null
- `tool` is always null
- `execution_mode` is always null
- `observation` is always null
- `reasoning` is always null
- `success` is always null
- `eval` is always 0
- `eval_reason` is always null
- `directive` is always null
- `output` is always null

If a user corrects, rejects, approves, or clarifies earlier work:

- keep the `user_message` step neutral
- use `caused_by` to point to the earlier step or steps it refers to
- use `feedback_content` on the user message to normalize what the feedback meant
- update the earlier agent step's `eval` and `directive` if needed
- use `retry_of` on the new fix step if a retry occurred

---

## Causality and Retry Consistency

`caused_by` and `retry_of` must be chronologically valid.

Do not point:

- `caused_by` to the current step
- `caused_by` to a later step
- `retry_of` to the current step
- `retry_of` to a later step

Use `caused_by` only for direct dependencies that actually led to the step. Use `retry_of` only when the current step is genuinely retrying, correcting, or redoing an earlier step.

If the dependency chain is ambiguous, explain the ambiguity in `causal_note` rather than inventing a precise but false linkage.

---

## API / Integration Workflow Tracing

If the task involves APIs, webhooks, SDKs, RPC calls, service integrations, or structured remote systems, trace API work as first-class workflow data.

For API-related steps:

- `observation` should include the known pre-call state when relevant
- `input` should include the exact request or request attempt
- `output` should include the exact response or error
- `state_change` should say what changed on the remote system, or that no mutation occurred

When possible, include:

- service or system name
- environment such as sandbox, staging, or production
- API version if known
- HTTP method
- endpoint or path
- query parameters
- masked headers and auth method
- request body or payload
- status code
- response body
- relevant headers such as retry-after, pagination cursor, or request ID
- IDs of created, updated, or deleted resources

Mask credentials and secrets. Never expose raw tokens, API keys, session secrets, webhook secrets, or private auth headers.

---

## MCP Workflow Tracing

If the task involves MCP, trace MCP work as first-class workflow data.

For MCP tool calls:

- record the MCP server name if known
- record the exact tool name
- include the exact arguments passed
- include the exact returned result
- describe any side effect or state change caused by the tool

For MCP resource reads:

- record the MCP server name if known
- record the exact resource URI, name, or identifier
- include what context was loaded
- mention the version or timestamp if known
- state how the loaded resource changed the agent's understanding or next action

For MCP prompt usage:

- record the MCP server name if known
- record the exact prompt name
- include prompt arguments
- include the actual generated instructions, message, or structured content used downstream when accessible
- note whether the prompt was used directly or adapted

Do not collapse MCP resource loading and MCP tool execution into one step if they are meaningfully separate actions.

---

## Browser / Computer-Use Tracing

If the task involves websites, SaaS apps, internal tools, desktop apps, remote desktops, or visible UI interaction, trace browser/computer-use work as first-class workflow data.

`observation` should capture the visible state before acting:

- current app/site/window
- current page or screen
- visible form values, table rows, modal state, or banners
- whether the needed control is visible, disabled, hidden, or missing
- any visible warning or error

`input` should capture the literal action:

- click target
- typed text
- selected option
- hotkey
- drag/drop
- scroll
- navigation
- tab switch
- file upload
- copied/pasted value

`output` should capture the direct visible result:

- page changed
- modal opened
- toast shown
- validation error displayed
- URL changed
- row created
- button disabled
- download started

`state_change` should describe what changed in the UI and, when known, what changed in the underlying system.

When useful and available, include evidence artifacts such as screenshot path, DOM snapshot path, HAR/network log path, exported CSV/report path, or recording path.

If those artifacts were not available, keep the trace honest and text-based. Do not imply that screenshots, recordings, or richer evidence existed when they did not.

---

## CLI, File, Database, and Structured Data Tracing

For CLI and file steps, preserve exact commands in `input`, exact stdout/stderr in `output`, full file content or diffs for write steps when available, and concrete state in `observation`.

For database or structured-data steps, also capture:

- exact query, filter, mutation, or operation in `input`
- target table, collection, sheet, or dataset name
- whether rows or records were created, updated, deleted, or unchanged
- exact error text for failed queries or mutations
- resulting IDs, counts, status values, or changed fields in `output`
- the state of the data before and after in `observation` and `state_change`

For spreadsheet steps:

- include the sheet name, tab, cell range, or filter applied
- capture formulas, pivots, sort/group logic, or conditional formatting when relevant
- record values or formulas before and after the edit

---

## Other / Unclassified Workflow Surface Tracing

If the workflow occurs through a surface not explicitly covered above, still trace it using the same core rules:

- identify the system, environment, or device involved
- record the concrete pre-action state in `observation`
- record the exact action taken in `input`
- record the exact returned signal, output, or visible result in `output`
- record what changed after the step in `state_change`
- attach supporting evidence or artifacts when available

This applies to messaging, email, async/event-driven systems, queues, webhooks, schedulers, background jobs, voice, audio, video, mobile apps, remote VMs, cloud consoles, hardware, robotics, lab workflows, IoT, device-control workflows, and other emerging surfaces.

If the system is asynchronous, capture both the action that triggered the work and the later observation or verification that confirmed the eventual result.

If the workflow is perception-heavy, capture both the raw signal or visible evidence available to the agent and the interpretation the agent used to decide the next action.

---

## Cross-Surface Failure and Verification Rules

High-value traces often include failure, diagnosis, correction, and retry. Capture these precisely.

When a step fails:

- keep the exact error or failure evidence
- set `success` and `eval` appropriately
- put hindsight on the failed step using `directive`
- link the retry step using `retry_of`
- do not move the failure analysis onto the retry step

Common cross-surface failures include:

- wrong auth or expired session
- missing permission
- stale UI state
- stale remote state
- bad endpoint or selector
- wrong file path or missing artifact
- schema drift
- version mismatch
- timeout
- race condition
- partial side effect
- invalid prompt/template/resource/tool selection

If the agent performs a verification step, capture:

- what was checked
- what evidence was used
- whether the check proved completion, partial completion, or failure

Good verification examples:

- GET request confirms created object exists
- returned status changes from pending to completed
- UI shows new record with matching ID
- file hash or diff matches expectation
- database row count increased as expected
- human explicitly approves the result

---

## Artifact Guidance

When the task produces non-chat evidence, include it in `static_output` when available.

Examples:

- cURL repro files
- OpenAPI specs
- Postman collections
- request/response fixtures
- webhook payload samples
- schema diffs
- screenshots
- HAR/network logs
- browser recordings
- SQL query files
- exported CSVs
- generated configs
- logs with request IDs
- MCP resource snapshots
- UI automation scripts
- test reports
- code diffs
- generated documents
- analysis reports

Each artifact should include path, type, role, related steps, description, state, hash when available, content or diff when available, and release sensitivity.

When richer raw evidence is available, prefer it over summaries. If those artifacts were not available, keep the trace honest and text-based.

Do not include trace JSON files, schema files, validation files, or release-preparation files as workflow artifacts unless the user-facing task was actually to create those files.

---

## Candidate Learning Signal Mapping

The fields above can be transformed into common trajectory and learning-signal views used in agent evaluation and post-training research:

- `observation` = candidate state / pre-action context
- `action + operation + input + tool` = candidate action representation
- `eval` = weak reward / process label candidate
- `state_change` = candidate next-state signal
- `alternatives_considered + directive` = preference or correction signal candidate
- `feedback_type + feedback_content` = human feedback signal when genuinely present
- `system_prompt + skills + memory` = agent context
- `agent_tools` = action-space context
- `learning` = candidate reusable lesson / meta-cognitive signal
- `retry_of` = failed-to-corrected step link
- `final_output + static_output` = terminal artifact and evidence

These mappings are candidates, not guarantees. Downstream use should account for trace mode, validation level, confidence, available evidence, and review quality.

Do not inflate the trace's value by calling weak self-evaluations expert labels or client validation.

---

## Sensitivity Handling

Do not include highly sensitive or confidential information in the trace. If the activity involved personal data, credentials, proprietary business details, or other sensitive content, mask or omit that information without disrupting the structure and usefulness of the trace.

Examples:

- API keys → `[CREDENTIAL]`
- private tokens → `[CREDENTIAL]`
- person names when sensitive → `[PERSON_1]`, `[PERSON_2]`
- internal URLs → `[INTERNAL_URL]`
- database credentials → `[CREDENTIAL]`
- private customer identifiers → `[CUSTOMER_ID]`

Use consistent placeholders. Preserve the structure, reasoning, and decision-making process while keeping sensitive details out.

If a detail is necessary to understand reasoning and safe to share, keep it. If it is sensitive filler, mask it.

---

## Agent Confidence

At the end of the trace, assess overall confidence in the accuracy and completeness of the trace, not how good the original work was.

Use:

- `100`: every step fully traced, high accuracy, nothing material missing
- `75`: well traced, minor gaps or approximations
- `50`: partially traced, some uncertainty in recall or execution
- `25`: significant gaps, low confidence in accuracy
- `0`: failed to trace meaningfully

Be honest. Accurate confidence ratings are more valuable than high confidence ratings.

If retracing past work and uncertain about details, state the uncertainty in the relevant step and lower confidence accordingly.

---

## Goal Assessment

Assess whether the user's actual underlying task or workflow goal was achieved.

### goal_achieved

Boolean. True if the user's original task reached its intended outcome, false otherwise.

### goal_notes

String or null. Discuss only the outcome of the original user-facing work.

Do not discuss trace creation, schema compliance, release preparation, or whether the trace was captured well.

Valid examples:

- `The Swift Lambda implementation was created, but it was not compiled or tested, so success is partial.`
- `The requested legal research summary was delivered, but it should not be treated as legal advice and was not reviewed by counsel.`
- `The local AutoDock Vina pipeline was created and a docking run completed, but the result was not experimentally validated.`
- `null`

If failed, explain the failure type, which step or steps caused the failure, what went wrong, what should have happened instead, and whether the failure was recoverable.

---

## Trace Outputs

### final_output

String. The actual main deliverable for the user's work: the code, document, analysis, fix, result, recommendation, or answer produced for the user.

It is not:

- the trace JSON
- a schema summary
- a release note
- a list of trace-bookkeeping actions

If the deliverable was a file and content is available, include the file content or a safe excerpt. If it was an analysis, include the actual analysis text. If it was a code change, include the relevant code or diff.

For retraced work, `final_output` should reflect the original deliverable as faithfully as possible. Do not reconstruct from memory if the actual output is available.

### static_output

Object or null. Structured artifacts and artifact evidence produced by the actual work.

Use `static_output` when the task created, modified, deleted, observed, or generated files or structured artifacts such as code, docs, configs, logs, datasets, screenshots, reports, JSON, CSV, HTML, transcripts, or similar outputs.

Preferred format:

```json
{
  "artifacts": [
    {
      "path": "src/example.js",
      "type": "modified",
      "role": "deliverable",
      "related_steps": [12, 13, 14],
      "description": "Updated payment API version and request handling.",
      "state": "File was modified and used in the final implementation.",
      "hash": "sha256:...",
      "content": null,
      "diff": "...",
      "release_sensitivity": "open"
    }
  ]
}
```

Artifact fields:

- `path`: file location or artifact identifier
- `type`: `created`, `modified`, `deleted`, `observed`, or `generated`
- `role`: `deliverable`, `intermediate`, `test`, `config`, `log`, `evidence`, or another appropriate role
- `related_steps`: step numbers connected to the artifact, or null
- `description`: what the artifact is
- `state`: what happened to the artifact or what was observed
- `hash`: sha256 if available, otherwise null
- `content`: full artifact content when available and safe, otherwise null
- `diff`: modification diff when available, otherwise null
- `release_sensitivity`: `open`, `redacted`, `private`, or `exclude`

Do not invent artifact content, diffs, hashes, screenshots, logs, or recordings.

---

## Dataset Card Summary Fields

When publishing traces as examples or datasets, include a lightweight summary object.

### title

Concise trace title.

### description

Plain-language description of the traced workflow, including task type, environment, major actions, failures/retries, feedback, outcome, and known limitations.

### tags

Array of tags such as:

- `coding`
- `legal-research`
- `bioscience`
- `tool-use`
- `browser`
- `cli`
- `retraced`
- `live`
- `self-annotated`
- `failure-recovery`
- `agent-work-trace`

### release_tier

One of:

- `open_example`
- `research_preview`
- `private`
- `not_for_release`

### validation_level

Use the same validation levels defined earlier.

---

## Trace JSON Schema Shape

Format the trace as a single JSON object.

```json
{
  "schema_version": "forsy-trace-v0.1",
  "trace_id": "forsy_trace_example_001",
  "prior_trace_id": null,
  "trace_mode": "live",
  "validation_level": "self_traced",
  "task": "Diagnose and fix a Stripe API migration causing checkout failures.",
  "agent_tools": ["web.run", "Bash", "Edit", "Read"],
  "started_at": "2025-03-14T14:00:00Z",
  "ended_at": "2025-03-14T14:45:00Z",
  "system_prompt": "You are a helpful assistant...",
  "skills": ["forsy-trace", "code-review"],
  "memory": "Project uses PostgreSQL with Prisma ORM.",
  "agent_config": {
    "model": "example-model",
    "temperature": 0.7,
    "max_tokens": 4096,
    "framework": "example-agent-framework"
  },
  "learning": "When migrating API versions, check the full changelog for breaking changes before diagnosing only the first visible error.",
  "termination_reason": "task_complete",
  "steps": [
    {
      "step": 1,
      "turn": 1,
      "actor": "user",
      "action": "user_message",
      "operation": null,
      "tool": null,
      "execution_mode": null,
      "parallel_group": null,
      "observation": null,
      "input": "Stripe checkout payments started failing after our API version migration. Please diagnose the issue and fix it.",
      "input_source": null,
      "output": null,
      "state_change": null,
      "reasoning": null,
      "caused_by": null,
      "causal_type": null,
      "causal_note": null,
      "alternatives_considered": null,
      "success": null,
      "eval": 0,
      "eval_reason": null,
      "directive": null,
      "message_role": "direct_request",
      "feedback_type": null,
      "feedback_content": null,
      "started_at": "2025-03-14T14:00:00Z",
      "ended_at": "2025-03-14T14:00:00Z",
      "retry_of": null
    },
    {
      "step": 2,
      "turn": 1,
      "actor": "agent",
      "action": "agent_step",
      "operation": "analyze",
      "tool": null,
      "execution_mode": "serial",
      "parallel_group": null,
      "observation": "Repository contains package.json, prisma/schema.prisma, and src/api/checkout.ts. Stripe checkout requests are failing after an API version migration.",
      "input": "Analyze likely causes of checkout failures after the Stripe API migration.",
      "input_source": {
        "actor": "user",
        "source_step": 1,
        "source_field": "input",
        "note": "The analysis was triggered directly by the user's debugging request."
      },
      "output": "Initial hypothesis list: API version mismatch, missing required fields, broken tax handling, outdated helper usage.",
      "state_change": "A candidate debugging plan now exists.",
      "reasoning": "A structured diagnosis plan is the best first step before calling tools or editing code because it narrows the likely failure modes.",
      "caused_by": [1],
      "causal_type": "user_request",
      "causal_note": "This step was triggered by the user's original debugging request.",
      "alternatives_considered": "Could immediately inspect Stripe docs first, but a quick diagnosis plan helps guide the next tool-assisted steps.",
      "success": true,
      "eval": 1,
      "eval_reason": "This step created a useful diagnosis plan that advanced the workflow.",
      "directive": null,
      "message_role": null,
      "feedback_type": null,
      "feedback_content": null,
      "started_at": "2025-03-14T14:00:05Z",
      "ended_at": "2025-03-14T14:00:08Z",
      "retry_of": null
    }
  ],
  "final_output": "Root cause identified and fix delivered...",
  "static_output": {
    "artifacts": []
  },
  "summary": {
    "total_steps": 2,
    "total_turns": 1,
    "positive_steps": 1,
    "negative_steps": 0,
    "neutral_steps": 1,
    "directive_signals": 0,
    "human_feedback": {
      "corrections": 0,
      "approvals": 0,
      "clarifications": 0,
      "new_instructions": 0
    },
    "agent_confidence": 75,
    "goal_achieved": true,
    "goal_notes": "The requested debugging analysis and fix were delivered, with limitations noted."
  },
  "dataset_summary": {
    "title": "Stripe API Migration Debugging Trace",
    "description": "Structured trace of an agent diagnosing and fixing an API migration issue.",
    "tags": ["coding", "api", "debugging", "tool-use", "failure-recovery"],
    "release_tier": "open_example",
    "validation_level": "self_traced"
  }
}
```

---

## Pre-Release Checks

Before publishing or sharing a trace, review and fix any issue that fails a check below.

A trace is ready for release only if:

- every traced step reflects the user's actual work rather than trace administration
- the first-turn direct user request remains in `input` as one coherent request
- every `user_message` step has `eval = 0`
- every `user_message` step has `observation = null`, `reasoning = null`, `success = null`, and `eval_reason = null`
- every non-`user_message` step has `feedback_content = null`
- every `input` field contains the actual payload for that step rather than a summary
- every `output` field contains the actual response or actual produced content, or an explicit excerpt with omissions noted
- every `observation` describes concrete pre-step state rather than intention, plan, or hindsight
- every `reasoning` field explains why the step was chosen
- every `caused_by` link is chronologically valid and points only to earlier steps
- every `retry_of` link points only to an earlier step that was genuinely retried, corrected, or redone
- `final_output` contains the actual deliverable rather than a summary of the trace
- `static_output` contains structured artifacts when those artifacts were available
- no secret, credential, private system prompt, or sensitive personal data is exposed
- `trace_mode`, `validation_level`, and `summary.agent_confidence` honestly reflect evidence quality
- `dataset_summary.description` truthfully reflects the evidence in the trace and does not imply richer evidence than the trace contains

---

## Local Output

When the trace is complete:

1. Verify the JSON is valid.
2. Compute summary counts accurately.
3. Save the trace as `trace.json`.
4. Save manifest metadata as `manifest.json` when available.
5. Save supporting artifacts under an `artifacts/` folder when available.
6. Do not include secrets, credentials, private system prompts, or sensitive personal data.

Suggested folder layout:

```text
trace-name/
  manifest.json
  trace.json
  artifacts/
  README.md
```

---

## License and Citation

This skill is released for research, engineering, and dataset-construction use. When publishing traces generated with this skill, include:

- skill name and version
- trace mode
- validation level
- known limitations
- whether the trace is live, retraced, or hybrid
- whether outputs were self-annotated, model-reviewed, human-reviewed, expert-reviewed, or client-validated
- license and usage restrictions for any included artifacts

---

## Quick Reference

Recommended top-level fields:

`schema_version`, `trace_id`, `prior_trace_id`, `trace_mode`, `validation_level`, `task`, `agent_tools`, `started_at`, `ended_at`, `system_prompt`, `skills`, `memory`, `agent_config`, `learning`, `termination_reason`, `steps`, `final_output`, `static_output`, `summary`, `dataset_summary`

Step fields:

| # | Field | Type | Required |
|---|---|---|---|
| 1 | step | int | always |
| 2 | turn | int | always |
| 3 | actor | string | always |
| 4 | action | string | always |
| 5 | operation | string/null | always |
| 6 | tool | string/null | always |
| 7 | execution_mode | string/null | always |
| 8 | parallel_group | string/null | always |
| 9 | observation | string/null | always |
| 10 | input | string/null | always |
| 11 | input_source | object/null | always |
| 12 | output | string/null | always |
| 13 | state_change | string/null | always |
| 14 | reasoning | string/null | always |
| 15 | caused_by | int[]/null | always |
| 16 | causal_type | string/null | always |
| 17 | causal_note | string/null | always |
| 18 | alternatives_considered | string/null | always |
| 19 | success | bool/null | always |
| 20 | eval | int | always |
| 21 | eval_reason | string/null | always |
| 22 | directive | string/null | always |
| 23 | message_role | string/null | always |
| 24 | feedback_type | string/null | always |
| 25 | feedback_content | string/null | always |
| 26 | started_at | string/null | always |
| 27 | ended_at | string/null | always |
| 28 | retry_of | int/null | always |

Action types:

- `user_message`
- `agent_step`
- `output`
- `error`

Suggested operation values:

- `plan`
- `analyze`
- `search`
- `read`
- `write`
- `edit`
- `execute`
- `verify`
- `download`
- `install`
- `ask_user`
- `answer`
- `select`
- `other`

Suggested causal types:

- `user_request`
- `follow_up_user_request`
- `answer_to_agent_question`
- `execution_of_plan`
- `dependency_on_tool_result`
- `retry_after_failure`
- `correction_response`
- `approval_response`
- `verification_of_prior_step`
- `dependency_on_multiple_prior_steps`
- `delegation_to_subagent`
- `delegated_work`
- `used_subagent_result`
- `handoff_from_subagent`
- `parallel_work`
- `other`

Message roles:

- `direct_request`
- `answer_to_agent_question`
- `correction`
- `approval`
- `clarification`
- `selection`
- `status_update`
- `new_constraint`
- `other`

Feedback types:

- `correction`
- `approval`
- `clarification`
- `new_instruction`
- `other`

Eval scores:

- `+1`: positive process signal
- `0`: neutral process signal
- `-1`: negative process signal

---

## Self-Refresh

If you are unsure about the exact open Forsy trace format at any point during tracing, re-read this file before finalizing the trace.
