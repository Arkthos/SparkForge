"""Pure serial task-graph validation and selection; no model, store or host calls."""

from __future__ import annotations

from typing import TypedDict

from . import agent_contracts as a
from . import contracts as c


MANDATORY_ROLES = ("coder", "test_author", "test_runner", "reviewer", "controller")


class Schedule(TypedDict):
    schema_version: str
    id: str
    revision: int
    job_id: str
    intent_sha: str
    envelope_sha: str
    plan_sha: str
    candidate_sha: str
    job_context_sha: str
    required_roles: list[str]
    tasks: list[a.TaskAssignment]


def operation_key(task: a.TaskAssignment) -> str:
    return "op-" + c.record_digest(a._task(task))


def validate_schedule(value: object, *, intent: c.IntentBaseline, envelope: c.ExecutionEnvelope) -> Schedule:
    record = c._object(value, {
        "schema_version", "id", "revision", "job_id", "intent_sha", "envelope_sha", "plan_sha", "candidate_sha",
        "job_context_sha", "required_roles", "tasks",
    }, "schedule")
    if record["schema_version"] != "sparkforge.schedule.v1":
        c._fail("UNSUPPORTED_SCHEMA", "schedule", "Unsupported task-graph version.")
    intent = c._intent(intent)
    envelope = c.validate_envelope(envelope, intent=intent)
    if record["intent_sha"] != c.record_digest(intent) or record["envelope_sha"] != c.record_digest(envelope):
        c._fail("BINDING_MISMATCH", "schedule", "Graph refers to another intent or envelope.")
    job_id = c._identifier(record["job_id"], "schedule.job_id")
    plan_sha = c._sha(record["plan_sha"], "schedule.plan_sha")
    candidate_sha = c._sha(record["candidate_sha"], "schedule.candidate_sha")
    required = c._strings(record["required_roles"], "schedule.required_roles", identifiers=True, minimum=1)
    if not set(MANDATORY_ROLES) <= set(required) <= set(a.RESULT_KINDS):
        c._fail("MISSING_ROLE_BARRIER", "schedule.required_roles", "The serial engineering profile requires coder, test author, runner, reviewer and final controller.")
    tasks = [a.validate_task(item, intent=intent, envelope=envelope, plan_sha=plan_sha, candidate_sha=candidate_sha)
             for item in c._list(record["tasks"], "schedule.tasks", minimum=1)]
    identifiers = c._unique([task["binding"]["task_id"] for task in tasks], "schedule.tasks")
    c._unique([task["binding"]["attempt_id"] for task in tasks], "schedule.attempts")
    if any(task["binding"]["job_id"] != job_id for task in tasks):
        c._fail("BINDING_MISMATCH", "schedule.tasks", "Every assignment must belong to this job.")
    if len({task["workspace_id"] for task in tasks}) != 1:
        c._fail("SCOPE_VIOLATION", "schedule.tasks", "This serial profile uses one selected candidate workspace.")
    if not set(required) <= {task["binding"]["role"] for task in tasks}:
        c._fail("MISSING_ROLE_BARRIER", "schedule.tasks", "Required role work cannot be omitted.")
    by_id = dict(zip(identifiers, tasks))
    for task in tasks:
        if not set(task["dependencies"]) <= set(identifiers):
            c._fail("UNKNOWN_DEPENDENCY", "schedule.tasks", "Graph contains a missing dependency.")
    ancestors: dict[str, set[str]] = {}
    active: set[str] = set()

    def visit(identifier: str) -> set[str]:
        if identifier in active:
            c._fail("DEPENDENCY_CYCLE", "schedule.tasks", "Task dependencies contain a cycle.")
        if identifier not in ancestors:
            active.add(identifier)
            predecessors = set(by_id[identifier]["dependencies"])
            for dependency in by_id[identifier]["dependencies"]:
                predecessors.update(visit(dependency))
            ancestors[identifier] = predecessors
            active.remove(identifier)
        return ancestors[identifier]

    for identifier in identifiers:
        visit(identifier)
    criteria = {item["id"] for item in intent["acceptance"]}
    barriers = {
        "test_author": ("coder",),
        "test_runner": ("coder", "test_author"),
        "reviewer": ("coder", "test_author", "test_runner"),
        "controller": ("coder", "test_author", "test_runner", "reviewer"),
        "delivery": ("controller",),
    }
    protected = [path for task in tasks for path in task["protected_paths"]]
    owned: list[str] = []
    for task in tasks:
        identifier, role = task["binding"]["task_id"], task["binding"]["role"]
        required_predecessors = {other["binding"]["task_id"] for other in tasks
                                 if other["binding"]["role"] in barriers.get(role, ())}
        if not required_predecessors <= ancestors[identifier]:
            c._fail("MISSING_ROLE_BARRIER", "schedule.dependencies", "Required producing/checking/review work must precede this role.")
        if role in ("test_runner", "reviewer", "controller") and set(task["acceptance_ids"]) != criteria:
            c._fail("MISSING_CRITERION", "schedule.acceptance", "Runner/reviewer/final controller must cover every intent criterion.")
        for path in task["allowed_writes"]:
            if any(a._overlap(path, other) for other in protected + owned):
                c._fail("OWNERSHIP_CONFLICT", "schedule.allowed_writes", "This initial graph requires disjoint writes outside all protected paths.")
            owned.append(path)
    result: Schedule = {
        "schema_version": "sparkforge.schedule.v1", "id": c._identifier(record["id"], "schedule.id"),
        "revision": c._integer(record["revision"], "schedule.revision"), "job_id": job_id,
        "intent_sha": c.record_digest(intent), "envelope_sha": c.record_digest(envelope),
        "plan_sha": plan_sha, "candidate_sha": candidate_sha, "required_roles": required, "tasks": tasks,
        "job_context_sha": c._sha(record["job_context_sha"], "schedule.job_context_sha"),
    }
    c.canonical_json(result)
    return result


def ready_task(schedule: Schedule, projections: dict[str, dict]) -> a.TaskAssignment | None:
    expected = {task["binding"]["task_id"] for task in schedule["tasks"]}
    if set(projections) != expected:
        c._fail("TASK_INVENTORY_MISMATCH", "schedule", "Registered task inventory differs from the pinned graph.")
    if any(state["status"] in ("reserved", "running", "unknown", "cancelling", "failed", "blocked", "cancelled")
           for state in projections.values()):
        return None
    for task in schedule["tasks"]:
        if projections[task["binding"]["task_id"]]["status"] in ("pending", "ready") and all(
            projections[dependency]["status"] == "completed" for dependency in task["dependencies"]
        ):
            return task
    return None
