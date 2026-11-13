"""Worker claims and separately supplied host observations; no dispatch or authority."""

from __future__ import annotations

from typing import TypedDict

from . import contracts as c


RESULT_KINDS = {
    "intake": "baseline_proposal",
    "brain": "plan_proposal",
    "controller": "controller_verdict",
    "coder": "candidate",
    "test_author": "tests",
    "test_runner": "check_report",
    "reviewer": "review",
    "diagnostician": "diagnosis",
    "delivery": "delivery_bundle",
    "coordinator": "coordination",
}
WRITERS = ("coder", "test_author", "delivery")
INDEPENDENT_ROLES = ("controller", "test_author", "reviewer")
FAILURE_KINDS = ("implementation", "oracle", "environment", "intent", "authority", "stale", "budget", "unknown_effects", "unknown")
NEXT_ACTIONS = ("complete", "repair", "replan", "reconcile", "request_decision", "stop")


class DigestReference(TypedDict):
    id: str
    sha256: str


class TaskBinding(TypedDict):
    job_id: str
    task_id: str
    attempt_id: str
    role: str
    intent_sha: str
    envelope_sha: str
    plan_sha: str
    candidate_sha: str
    inputs_sha: str


class TaskAssignment(TypedDict):
    schema_version: str
    binding: TaskBinding
    environment: str
    profile: c.Reference
    routes: c.Routes
    workspace_id: str
    data_root_ids: list[str]
    objective: str
    acceptance_ids: list[str]
    inputs: list[DigestReference]
    allowed_writes: list[str]
    protected_paths: list[str]
    dependencies: list[str]
    tools: list[str]
    effects: list[str]
    deadline: str
    allowance: c.AgentBounds
    required_result: str
    stop_conditions: list[str]


class Producer(TypedDict):
    host: c.Reference
    role: str
    session_id: str
    context_id: str


class Usage(TypedDict):
    status: str
    model_calls: int | None
    tokens: int | None
    wall_seconds: int | None
    reason: str | None


class AgentAttempt(TypedDict):
    schema_version: str
    binding: TaskBinding
    task_sha: str
    operation_key: str
    ordinal: int
    producer: Producer | None
    status: str
    started_at: str | None
    finished_at: str | None
    observed_usage: Usage
    observation: DigestReference | None


class Finding(TypedDict):
    schema_version: str
    id: str
    severity: str
    category: str
    message: str
    path: str | None
    acceptance_ids: list[str]
    evidence: list[DigestReference]
    recommendation: str


class Failure(TypedDict):
    schema_version: str
    id: str
    kind: str
    message: str
    evidence: list[DigestReference]
    uncertainty: list[str]
    suggested_action: str


class AgentResult(TypedDict):
    schema_version: str
    id: str
    binding: TaskBinding
    task_sha: str
    producer: Producer
    result_kind: str
    outcome: str
    summary: str
    artifacts: list[DigestReference]
    changed_paths: list[str]
    output_candidate_sha: str | None
    evidence: list[DigestReference]
    findings: list[Finding]
    failures: list[Failure]
    usage_claim: Usage
    uncertainty: list[str]
    next_action: str


def _version(record: dict, expected: str, path: str) -> None:
    if record["schema_version"] != expected:
        c._fail("UNSUPPORTED_SCHEMA", path + ".schema_version", "Unsupported record version.")


def _ref(value: object, path: str) -> DigestReference:
    record = c._object(value, {"id", "sha256"}, path)
    return {"id": c._identifier(record["id"], path + ".id"), "sha256": c._sha(record["sha256"], path + ".sha256")}


def _refs(value: object, path: str) -> list[DigestReference]:
    refs = [_ref(item, f"{path}[{index}]") for index, item in enumerate(c._list(value, path))]
    c._unique([ref["id"] for ref in refs], path)
    return refs


def _binding(value: object) -> TaskBinding:
    record = c._object(value, {
        "job_id", "task_id", "attempt_id", "role", "intent_sha", "envelope_sha", "plan_sha", "candidate_sha", "inputs_sha",
    }, "binding")
    return {
        "job_id": c._identifier(record["job_id"], "binding.job_id"),
        "task_id": c._identifier(record["task_id"], "binding.task_id"),
        "attempt_id": c._identifier(record["attempt_id"], "binding.attempt_id"),
        "role": c._enum(record["role"], tuple(RESULT_KINDS), "binding.role"),
        "intent_sha": c._sha(record["intent_sha"], "binding.intent_sha"),
        "envelope_sha": c._sha(record["envelope_sha"], "binding.envelope_sha"),
        "plan_sha": c._sha(record["plan_sha"], "binding.plan_sha"),
        "candidate_sha": c._sha(record["candidate_sha"], "binding.candidate_sha"),
        "inputs_sha": c._sha(record["inputs_sha"], "binding.inputs_sha"),
    }


def _paths(value: object, path: str) -> list[str]:
    paths = [c.relative_path(item, path) for item in c._list(value, path, maximum=512)]
    c._unique([item.casefold() for item in paths], path)
    return paths


def _overlap(left: str, right: str) -> bool:
    left, right = left.casefold(), right.casefold()
    return left == right or left.startswith(right + "/") or right.startswith(left + "/")


def _allowance(value: object) -> c.AgentBounds:
    record = c._object(value, {"timeout_seconds", "max_attempts", "max_model_calls", "max_tokens"}, "task.allowance")
    return {
        "timeout_seconds": c._integer(record["timeout_seconds"], "task.allowance.timeout_seconds", 86400),
        "max_attempts": c._integer(record["max_attempts"], "task.allowance.max_attempts", 20),
        "max_model_calls": c._integer(record["max_model_calls"], "task.allowance.max_model_calls"),
        "max_tokens": c._integer(record["max_tokens"], "task.allowance.max_tokens", 1_000_000_000),
    }


def _task(value: object) -> TaskAssignment:
    record = c._object(value, {
        "schema_version", "binding", "environment", "profile", "routes", "workspace_id", "data_root_ids",
        "objective", "acceptance_ids", "inputs", "allowed_writes", "protected_paths", "dependencies", "tools",
        "effects", "deadline", "allowance", "required_result", "stop_conditions",
    }, "task")
    _version(record, "sparkforge.task.v1", "task")
    binding = _binding(record["binding"])
    inputs = _refs(record["inputs"], "task.inputs")
    if binding["inputs_sha"] != c.record_digest(inputs):
        c._fail("BINDING_MISMATCH", "task.inputs", "Input inventory differs from its bound digest.")
    writes = _paths(record["allowed_writes"], "task.allowed_writes")
    protected = _paths(record["protected_paths"], "task.protected_paths")
    if any(_overlap(write, excluded) for write in writes for excluded in protected):
        c._fail("SCOPE_VIOLATION", "task.allowed_writes", "Writes overlap protected paths.")
    if writes and binding["role"] not in WRITERS:
        c._fail("ROLE_VIOLATION", "task.allowed_writes", "This role cannot write candidate files.")
    dependencies = c._strings(record["dependencies"], "task.dependencies", identifiers=True)
    if binding["task_id"] in dependencies:
        c._fail("INVALID_DEPENDENCY", "task.dependencies", "A task cannot depend on itself.")
    routes = c._object(record["routes"], {"host", "provider"}, "task.routes")
    required = c._enum(record["required_result"], tuple(RESULT_KINDS.values()), "task.required_result")
    if required != RESULT_KINDS[binding["role"]]:
        c._fail("ROLE_VIOLATION", "task.required_result", "Result kind does not belong to the assigned role.")
    result: TaskAssignment = {
        "schema_version": "sparkforge.task.v1",
        "binding": binding,
        "environment": c._enum(record["environment"], ("LOCAL_DEVELOPMENT", "CORP", "ACRO"), "task.environment"),
        "profile": c._reference(record["profile"], "task.profile"),
        "routes": {"host": c._reference(routes["host"], "task.routes.host"),
                   "provider": c._reference(routes["provider"], "task.routes.provider")},
        "workspace_id": c._identifier(record["workspace_id"], "task.workspace_id"),
        "data_root_ids": c._strings(record["data_root_ids"], "task.data_root_ids", identifiers=True),
        "objective": c._text(record["objective"], "task.objective"),
        "acceptance_ids": c._strings(record["acceptance_ids"], "task.acceptance_ids", identifiers=True, minimum=1),
        "inputs": inputs,
        "allowed_writes": writes,
        "protected_paths": protected,
        "dependencies": dependencies,
        "tools": c._strings(record["tools"], "task.tools", identifiers=True),
        "effects": c._strings(record["effects"], "task.effects", identifiers=True),
        "deadline": c._timestamp(record["deadline"], "task.deadline"),
        "allowance": _allowance(record["allowance"]),
        "required_result": required,
        "stop_conditions": c._strings(record["stop_conditions"], "task.stop_conditions", minimum=1),
    }
    if ("workspace_write" in result["effects"]) != bool(writes):
        c._fail("SCOPE_VIOLATION", "task.effects", "Candidate writes need both explicit files and workspace_write.")
    c.canonical_json(result)
    return result


def validate_task(
    value: object, *, intent: c.IntentBaseline, envelope: c.ExecutionEnvelope, plan_sha: str, candidate_sha: str,
) -> TaskAssignment:
    """Validate an assignment against the caller's current, separately selected records."""
    baseline = c._intent(intent)
    envelope = c.validate_envelope(envelope, intent=baseline)
    task = _task(value)
    expected = {"intent_sha": c.record_digest(baseline), "envelope_sha": c.record_digest(envelope),
                "plan_sha": c._sha(plan_sha, "current.plan_sha"), "candidate_sha": c._sha(candidate_sha, "current.candidate_sha")}
    if any(task["binding"][key] != digest for key, digest in expected.items()):
        c._fail("BINDING_MISMATCH", "task.binding", "Assignment does not match current intent/envelope/plan/candidate.")
    if any(task[key] != envelope[key] for key in ("environment", "profile", "routes")):
        c._fail("ENVIRONMENT_MISMATCH", "task", "Environment, profile and routes must match the envelope.")
    if task["workspace_id"] not in {root["id"] for root in envelope["workspace_roots"]}:
        c._fail("SCOPE_VIOLATION", "task.workspace_id", "Workspace is outside the selected envelope.")
    if not set(task["data_root_ids"]) <= {root["id"] for root in envelope["data_roots"]}:
        c._fail("SCOPE_VIOLATION", "task.data_root_ids", "Data roots are outside the selected envelope.")
    if not set(task["acceptance_ids"]) <= {criterion["id"] for criterion in baseline["acceptance"]}:
        c._fail("UNKNOWN_CRITERION", "task.acceptance_ids", "Assignment refers to unknown behavior.")
    for key in ("tools", "effects"):
        if not set(task[key]) <= set(envelope[key]):
            c._fail("SCOPE_VIOLATION", "task." + key, "Assignment expands the envelope.")
    if task["deadline"] > envelope["expires_at"]:
        c._fail("SCOPE_VIOLATION", "task.deadline", "Deadline exceeds envelope expiry.")
    if any(task["allowance"][key] > envelope["bounds"]["agent"][key] for key in task["allowance"]):
        c._fail("INVALID_BOUND", "task.allowance", "Assignment expands per-agent bounds.")
    return task


def _producer(value: object) -> Producer:
    record = c._object(value, {"host", "role", "session_id", "context_id"}, "producer")
    return {
        "host": c._reference(record["host"], "producer.host"),
        "role": c._enum(record["role"], tuple(RESULT_KINDS), "producer.role"),
        "session_id": c._identifier(record["session_id"], "producer.session_id"),
        "context_id": c._identifier(record["context_id"], "producer.context_id"),
    }


def _usage(value: object, path: str) -> Usage:
    record = c._object(value, {"status", "model_calls", "tokens", "wall_seconds", "reason"}, path)
    status = c._enum(record["status"], ("known", "unknown"), path + ".status")
    values = (record["model_calls"], record["tokens"], record["wall_seconds"])
    if status == "unknown":
        if any(item is not None for item in values):
            c._fail("INVALID_USAGE", path, "Unknown usage must remain null, not zero or a guess.")
        reason = c._text(record["reason"], path + ".reason")
    else:
        if any(type(item) is not int or not 0 <= item <= 10**12 for item in values) or record["reason"] is not None:
            c._fail("INVALID_USAGE", path, "Known usage needs nonnegative bounded integers and a null unknown reason.")
        reason = None
    return {"status": status, "model_calls": record["model_calls"], "tokens": record["tokens"],
            "wall_seconds": record["wall_seconds"], "reason": reason}


def validate_attempt(value: object, *, task: TaskAssignment) -> AgentAttempt:
    """Validate a host-observation record, not its authenticity or current job admission."""
    task = _task(task)
    record = c._object(value, {
        "schema_version", "binding", "task_sha", "operation_key", "ordinal", "producer", "status",
        "started_at", "finished_at", "observed_usage", "observation",
    }, "attempt")
    _version(record, "sparkforge.attempt.v1", "attempt")
    binding = _binding(record["binding"])
    task_sha = c._sha(record["task_sha"], "attempt.task_sha")
    if binding != task["binding"] or task_sha != c.record_digest(task):
        c._fail("BINDING_MISMATCH", "attempt", "Attempt does not match the exact assignment.")
    ordinal = c._integer(record["ordinal"], "attempt.ordinal", task["allowance"]["max_attempts"])
    status = c._enum(record["status"], (
        "reserved", "accepted", "running", "completed", "failed", "cancel_requested", "cancelled", "unknown",
    ), "attempt.status")
    producer = None if record["producer"] is None else _producer(record["producer"])
    observation = None if record["observation"] is None else _ref(record["observation"], "attempt.observation")
    if producer is not None and (producer["role"] != binding["role"] or producer["host"] != task["routes"]["host"]):
        c._fail("PRODUCER_MISMATCH", "attempt.producer", "Host or role differs from the assignment.")
    started = None if record["started_at"] is None else c._timestamp(record["started_at"], "attempt.started_at")
    finished = None if record["finished_at"] is None else c._timestamp(record["finished_at"], "attempt.finished_at")
    if status == "reserved" and any(item is not None for item in (producer, observation, started, finished)):
        c._fail("INVALID_ATTEMPT", "attempt", "A reservation cannot claim observed dispatch or completion.")
    if status not in ("reserved", "unknown") and (producer is None or observation is None):
        c._fail("MISSING_OBSERVATION", "attempt", "Observed work needs a producer and observation reference.")
    if status == "running" and started is None:
        c._fail("INVALID_ATTEMPT", "attempt.started_at", "Running work needs an observed start.")
    if (status in ("completed", "failed", "cancelled")) != (finished is not None):
        c._fail("INVALID_ATTEMPT", "attempt.finished_at", "Only terminal observed states have a finish timestamp.")
    if started is not None and finished is not None and finished < started:
        c._fail("INVALID_ATTEMPT", "attempt.finished_at", "Finish precedes start.")
    result: AgentAttempt = {
        "schema_version": "sparkforge.attempt.v1", "binding": binding, "task_sha": task_sha,
        "operation_key": c._identifier(record["operation_key"], "attempt.operation_key"),
        "ordinal": ordinal, "producer": producer, "status": status, "started_at": started, "finished_at": finished,
        "observed_usage": _usage(record["observed_usage"], "attempt.observed_usage"), "observation": observation,
    }
    c.canonical_json(result)
    return result


def validate_finding(value: object) -> Finding:
    record = c._object(value, {
        "schema_version", "id", "severity", "category", "message", "path", "acceptance_ids", "evidence", "recommendation",
    }, "finding")
    _version(record, "sparkforge.finding.v1", "finding")
    result: Finding = {
        "schema_version": "sparkforge.finding.v1",
        "id": c._identifier(record["id"], "finding.id"),
        "severity": c._enum(record["severity"], ("info", "warning", "error", "critical"), "finding.severity"),
        "category": c._enum(record["category"], FAILURE_KINDS, "finding.category"),
        "message": c._text(record["message"], "finding.message"),
        "path": None if record["path"] is None else c.relative_path(record["path"], "finding.path"),
        "acceptance_ids": c._strings(record["acceptance_ids"], "finding.acceptance_ids", identifiers=True),
        "evidence": _refs(record["evidence"], "finding.evidence"),
        "recommendation": c._text(record["recommendation"], "finding.recommendation"),
    }
    c.canonical_json(result)
    return result


def validate_failure(value: object) -> Failure:
    record = c._object(value, {
        "schema_version", "id", "kind", "message", "evidence", "uncertainty", "suggested_action",
    }, "failure")
    _version(record, "sparkforge.failure.v1", "failure")
    result: Failure = {
        "schema_version": "sparkforge.failure.v1",
        "id": c._identifier(record["id"], "failure.id"),
        "kind": c._enum(record["kind"], FAILURE_KINDS, "failure.kind"),
        "message": c._text(record["message"], "failure.message"),
        "evidence": _refs(record["evidence"], "failure.evidence"),
        "uncertainty": c._strings(record["uncertainty"], "failure.uncertainty"),
        "suggested_action": c._enum(record["suggested_action"], NEXT_ACTIONS[1:], "failure.suggested_action"),
    }
    if result["kind"] in ("unknown", "unknown_effects") and not result["uncertainty"]:
        c._fail("MISSING_UNCERTAINTY", "failure.uncertainty", "Unknown failures need explicit uncertainty.")
    if result["kind"] == "unknown_effects" and result["suggested_action"] not in ("reconcile", "stop"):
        c._fail("UNRESOLVED_EFFECTS", "failure.suggested_action", "Unknown effects must reconcile before retry.")
    if not result["evidence"] and not result["uncertainty"]:
        c._fail("MISSING_EVIDENCE", "failure", "A failure needs evidence or an explicit evidence limitation.")
    c.canonical_json(result)
    return result


def validate_result(
    value: object, *, task: TaskAssignment, attempt: AgentAttempt, current_candidate_sha: str,
    prior_producers: tuple[Producer, ...] = (),
) -> AgentResult:
    """Check claims against supplied observations. This does not admit evidence or effects."""
    task = _task(task)
    attempt = validate_attempt(attempt, task=task)
    if c._sha(current_candidate_sha, "current.candidate_sha") != task["binding"]["candidate_sha"]:
        c._fail("STALE_CANDIDATE", "result", "The assignment inspected a superseded candidate.")
    if attempt["status"] not in ("completed", "failed", "cancelled", "unknown") or attempt["producer"] is None:
        c._fail("RESULT_BEFORE_COMPLETION", "result", "Dispatch acceptance alone is not a completed worker turn.")
    record = c._object(value, {
        "schema_version", "id", "binding", "task_sha", "producer", "result_kind", "outcome", "summary", "artifacts",
        "changed_paths", "output_candidate_sha", "evidence", "findings", "failures", "usage_claim", "uncertainty", "next_action",
    }, "result")
    _version(record, "sparkforge.agent-result.v1", "result")
    binding = _binding(record["binding"])
    task_sha = c._sha(record["task_sha"], "result.task_sha")
    if binding != task["binding"] or task_sha != c.record_digest(task):
        c._fail("BINDING_MISMATCH", "result", "Result does not match the exact current assignment.")
    producer = _producer(record["producer"])
    if producer != attempt["producer"]:
        c._fail("PRODUCER_MISMATCH", "result.producer", "Claimed producer differs from the supplied host observation.")
    if type(prior_producers) is not tuple or len(prior_producers) > c.MAX_ITEMS:
        c._fail("INVALID_PRODUCERS", "prior_producers", "Supply at most 128 prior producers as a tuple.")
    prior = [_producer(item) for item in prior_producers]
    if binding["role"] in INDEPENDENT_ROLES:
        if not prior:
            c._fail("SEPARATION_REQUIRED", "result.producer", "Supply the relevant prior producer observations.")
        if any(item["host"]["id"] == producer["host"]["id"] and item["context_id"] == producer["context_id"] for item in prior):
            c._fail("PRODUCER_NOT_SEPARATE", "result.producer", "A relabeled prior context cannot supply independent work.")
    kind = c._enum(record["result_kind"], tuple(RESULT_KINDS.values()), "result.result_kind")
    if kind != task["required_result"]:
        c._fail("ROLE_VIOLATION", "result.result_kind", "Result kind differs from the assigned role.")
    outcome = c._enum(record["outcome"], ("completed", "failed", "blocked", "unknown", "cancelled"), "result.outcome")
    permitted_outcomes = {
        "completed": ("completed", "failed", "blocked", "unknown"),
        "failed": ("failed", "unknown"), "cancelled": ("cancelled", "unknown"), "unknown": ("unknown",),
    }
    if outcome not in permitted_outcomes[attempt["status"]]:
        c._fail("OUTCOME_MISMATCH", "result.outcome", "Worker claim contradicts the supplied host observation.")
    changed = _paths(record["changed_paths"], "result.changed_paths")
    if not set(changed) <= set(task["allowed_writes"]):
        c._fail("SCOPE_VIOLATION", "result.changed_paths", "Claimed changes exceed the exact assigned files.")
    output_sha = None if record["output_candidate_sha"] is None else c._sha(record["output_candidate_sha"], "result.output_candidate_sha")
    if changed and output_sha is None:
        c._fail("MISSING_CANDIDATE", "result.output_candidate_sha", "Changed files need a proposed output candidate digest.")
    if output_sha is not None and binding["role"] not in WRITERS:
        c._fail("ROLE_VIOLATION", "result.output_candidate_sha", "Only a candidate-writing role can propose changed bytes.")
    evidence = _refs(record["evidence"], "result.evidence")
    inventory = {ref["id"]: ref["sha256"] for ref in task["inputs"]}
    for ref in evidence:
        if ref["id"] in inventory and inventory[ref["id"]] != ref["sha256"]:
            c._fail("EVIDENCE_MISMATCH", "result.evidence", "An input reference cannot be rebound to different bytes.")
        inventory[ref["id"]] = ref["sha256"]
    findings = [validate_finding(item) for item in c._list(record["findings"], "result.findings")]
    failures = [validate_failure(item) for item in c._list(record["failures"], "result.failures")]
    for records, path in ((findings, "result.findings"), (failures, "result.failures")):
        c._unique([item["id"] for item in records], path)
        for item in records:
            if any(inventory.get(ref["id"]) != ref["sha256"] for ref in item["evidence"]):
                c._fail("EVIDENCE_MISMATCH", path, "Finding/failure evidence must match the declared inventory.")
    if any(not set(finding["acceptance_ids"]) <= set(task["acceptance_ids"]) for finding in findings):
        c._fail("UNKNOWN_CRITERION", "result.findings", "Finding refers to unassigned acceptance.")
    uncertainty = c._strings(record["uncertainty"], "result.uncertainty")
    next_action = c._enum(record["next_action"], NEXT_ACTIONS, "result.next_action")
    if outcome in ("failed", "blocked") and not failures:
        c._fail("MISSING_FAILURE", "result.failures", "Failed/blocked work needs a structured cause.")
    if outcome == "completed" and failures:
        c._fail("OUTCOME_MISMATCH", "result.failures", "An unresolved failure cannot be labeled completed.")
    if outcome == "unknown" and not uncertainty:
        c._fail("MISSING_UNCERTAINTY", "result.uncertainty", "Unknown completion must preserve what is unknown.")
    if (outcome == "unknown" or any(failure["kind"] == "unknown_effects" for failure in failures)) and next_action not in ("reconcile", "stop"):
        c._fail("UNRESOLVED_EFFECTS", "result.next_action", "Unknown completion/effects cannot become a safe retry.")
    if outcome != "completed" and next_action == "complete":
        c._fail("OUTCOME_MISMATCH", "result.next_action", "Incomplete work cannot request a completed handoff.")
    result: AgentResult = {
        "schema_version": "sparkforge.agent-result.v1",
        "id": c._identifier(record["id"], "result.id"), "binding": binding, "task_sha": task_sha,
        "producer": producer, "result_kind": kind, "outcome": outcome,
        "summary": c._text(record["summary"], "result.summary"),
        "artifacts": _refs(record["artifacts"], "result.artifacts"), "changed_paths": changed,
        "output_candidate_sha": output_sha, "evidence": evidence, "findings": findings, "failures": failures,
        "usage_claim": _usage(record["usage_claim"], "result.usage_claim"),
        "uncertainty": uncertainty, "next_action": next_action,
    }
    c.canonical_json(result)
    return result
