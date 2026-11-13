"""Pure workflow projections and replay guards; storage and evidence ingress are external."""

from __future__ import annotations

from typing import TypedDict

from . import contracts as c
from .agent_contracts import DigestReference, _ref


TRANSITIONS = {
    "job": {
        "intake": ("needs_decision", "planning", "blocked"),
        "needs_decision": ("planning", "blocked"),
        "planning": ("ready", "needs_decision", "blocked"),
        "ready": ("blocked",),
        "running": ("checking", "diagnosing", "blocked"),
        "checking": ("reviewing", "diagnosing", "blocked"),
        "reviewing": ("verified", "diagnosing", "needs_decision", "blocked"),
        "diagnosing": ("repairing", "planning", "needs_decision", "blocked", "failed"),
        "repairing": ("checking", "diagnosing", "blocked"),
        "reconciling": ("ready", "blocked"),
        "blocked": ("planning", "needs_decision", "failed"),
        "verified": ("delivered",),
        "cancelling": ("cancelled",),
        "cancelled": (), "delivered": (), "failed": (),
    },
    "task": {
        "pending": ("ready", "blocked"),
        "ready": ("blocked",),
        "reserved": ("ready", "blocked"),
        "running": ("completed", "failed", "blocked"),
        "unknown": ("ready", "blocked"),
        "blocked": ("ready", "failed"),
        "failed": ("ready",),
        "cancelling": ("cancelled",),
        "completed": (), "cancelled": (),
    },
    "attempt": {
        "reserved": (),
        "accepted": ("running", "completed", "failed"),
        "running": ("completed", "failed"),
        "unknown": ("completed", "failed"),
        "cancel_requested": ("cancelled",),
        "completed": (), "failed": (), "cancelled": (),
    },
}
INITIAL = {"job": "intake", "task": "pending", "attempt": "reserved"}
OPEN_OPERATIONS = ("reserved", "dispatched", "unknown", "cancel_requested")
RESERVABLE = {
    "job": ("planning", "ready", "running", "checking", "reviewing", "repairing"),
    "task": ("ready",),
    "attempt": ("reserved",),
}


class Evidence(TypedDict):
    slot: str
    receipt: DigestReference
    context_sha: str
    outcome: str


class Operation(TypedDict):
    id: str
    status: str
    dispatched: bool


class Projection(TypedDict):
    schema_version: str
    id: str
    kind: str
    revision: int
    status: str
    context_sha: str
    required_evidence: list[str]
    evidence: list[Evidence]
    operations: list[Operation]
    has_dispatched: bool
    stop_requested: bool
    cause: str | None


class Command(TypedDict):
    schema_version: str
    key: str
    entity_id: str
    expected_revision: int
    context_sha: str
    action: str
    target: str | None
    operation_id: str | None
    resolution: str | None
    observation: DigestReference | None
    evidence: list[Evidence]
    new_context_sha: str | None
    reason: str | None


class Event(TypedDict):
    schema_version: str
    id: str
    entity_id: str
    kind: str
    command_key: str
    command_sha: str
    command: Command
    before_revision: int
    after_sha: str
    after: Projection


class TransitionResult(TypedDict):
    projection: Projection
    event: Event
    replayed: bool


def _boolean(value: object, path: str) -> bool:
    if type(value) is not bool:
        c._fail("INVALID_BOOLEAN", path, "Expected an explicit boolean.")
    return value


def _evidence(value: object) -> list[Evidence]:
    result: list[Evidence] = []
    for item in c._list(value, "evidence"):
        record = c._object(item, {"slot", "receipt", "context_sha", "outcome"}, "evidence")
        result.append({
            "slot": c._identifier(record["slot"], "evidence.slot"),
            "receipt": _ref(record["receipt"], "evidence.receipt"),
            "context_sha": c._sha(record["context_sha"], "evidence.context_sha"),
            "outcome": c._enum(record["outcome"], ("pass", "fail", "skipped", "unknown"), "evidence.outcome"),
        })
    c._unique([item["slot"] for item in result], "evidence")
    return result


def _unresolved(projection: Projection) -> bool:
    return any(operation["status"] in OPEN_OPERATIONS for operation in projection["operations"])


def _completion(projection: Projection) -> None:
    if _unresolved(projection):
        c._fail("UNRESOLVED_OPERATIONS", "projection", "Completion requires all operations to be reconciled.")
    if not projection["has_dispatched"]:
        c._fail("RESULT_BEFORE_DISPATCH", "projection", "No dispatch or reconciled execution has been observed.")
    if not projection["operations"] or (
        projection["operations"][-1]["status"] != "completed" or not projection["operations"][-1]["dispatched"]
    ):
        c._fail("EXECUTION_NOT_CONFIRMED", "projection.operations", "The latest reserved operation needs confirmed completion; dispatch history is not execution evidence.")
    evidence = {item["slot"]: item for item in projection["evidence"]}
    if any(slot not in evidence or evidence[slot]["outcome"] != "pass"
           or evidence[slot]["context_sha"] != projection["context_sha"] for slot in projection["required_evidence"]):
        c._fail("INCOMPLETE_EVIDENCE", "projection.evidence", "Every expected evidence slot needs a current passing receipt.")


def validate_projection(value: object) -> Projection:
    record = c._object(value, {
        "schema_version", "id", "kind", "revision", "status", "context_sha", "required_evidence",
        "evidence", "operations", "has_dispatched", "stop_requested", "cause",
    }, "projection")
    if record["schema_version"] != "sparkforge.projection.v1":
        c._fail("UNSUPPORTED_SCHEMA", "projection", "Unsupported projection version.")
    kind = c._enum(record["kind"], tuple(TRANSITIONS), "projection.kind")
    operations: list[Operation] = []
    for item in c._list(record["operations"], "projection.operations"):
        operation = c._object(item, {"id", "status", "dispatched"}, "operation")
        operations.append({
            "id": c._identifier(operation["id"], "operation.id"),
            "status": c._enum(operation["status"], OPEN_OPERATIONS + ("completed", "failed", "cancelled", "not_started"), "operation.status"),
            "dispatched": _boolean(operation["dispatched"], "operation.dispatched"),
        })
    c._unique([item["id"] for item in operations], "projection.operations")
    result: Projection = {
        "schema_version": "sparkforge.projection.v1",
        "id": c._identifier(record["id"], "projection.id"), "kind": kind,
        "revision": c._integer(record["revision"], "projection.revision"),
        "status": c._enum(record["status"], tuple(TRANSITIONS[kind]), "projection.status"),
        "context_sha": c._sha(record["context_sha"], "projection.context_sha"),
        "required_evidence": c._strings(record["required_evidence"], "projection.required_evidence", identifiers=True, minimum=1),
        "evidence": _evidence(record["evidence"]), "operations": operations,
        "has_dispatched": _boolean(record["has_dispatched"], "projection.has_dispatched"),
        "stop_requested": _boolean(record["stop_requested"], "projection.stop_requested"),
        "cause": None if record["cause"] is None else c._text(record["cause"], "projection.cause"),
    }
    if any(item["slot"] not in result["required_evidence"] for item in result["evidence"]):
        c._fail("UNEXPECTED_EVIDENCE", "projection.evidence", "Evidence slot is outside the fixed required inventory.")
    if result["status"] in ("verified", "delivered", "completed"):
        _completion(result)
    if result["status"] == "cancelled" and (_unresolved(result) or not result["stop_requested"]):
        c._fail("UNRESOLVED_OPERATIONS", "projection", "Cancelled work needs a stop request and reconciled operations.")
    c.canonical_json(result)
    return result


def initial_projection(kind: str, entity_id: str, context_sha: str, required_evidence: list[str]) -> Projection:
    kind = c._enum(kind, tuple(INITIAL), "kind")
    return validate_projection({
        "schema_version": "sparkforge.projection.v1", "id": entity_id, "kind": kind,
        "revision": 1, "status": INITIAL[kind], "context_sha": context_sha,
        "required_evidence": required_evidence, "evidence": [], "operations": [],
        "has_dispatched": False, "stop_requested": False, "cause": None,
    })


def _command(value: object) -> Command:
    record = c._object(value, {
        "schema_version", "key", "entity_id", "expected_revision", "context_sha", "action", "target",
        "operation_id", "resolution", "observation", "evidence", "new_context_sha", "reason",
    }, "command")
    if record["schema_version"] != "sparkforge.command.v1":
        c._fail("UNSUPPORTED_SCHEMA", "command", "Unsupported command version.")
    result: Command = {
        "schema_version": "sparkforge.command.v1",
        "key": c._identifier(record["key"], "command.key"),
        "entity_id": c._identifier(record["entity_id"], "command.entity_id"),
        "expected_revision": c._integer(record["expected_revision"], "command.expected_revision"),
        "context_sha": c._sha(record["context_sha"], "command.context_sha"),
        "action": c._enum(record["action"], (
            "advance", "reserve", "dispatch", "result", "reconcile", "evidence", "invalidate", "cancel", "cancel_ack",
        ), "command.action"),
        "target": None if record["target"] is None else c._identifier(record["target"], "command.target"),
        "operation_id": None if record["operation_id"] is None else c._identifier(record["operation_id"], "command.operation_id"),
        "resolution": None if record["resolution"] is None else c._enum(record["resolution"], (
            "completed", "failed", "cancelled", "not_started", "unknown",
        ), "command.resolution"),
        "observation": None if record["observation"] is None else _ref(record["observation"], "command.observation"),
        "evidence": _evidence(record["evidence"]),
        "new_context_sha": None if record["new_context_sha"] is None else c._sha(record["new_context_sha"], "command.new_context_sha"),
        "reason": None if record["reason"] is None else c._text(record["reason"], "command.reason"),
    }
    applicable = {
        "advance": {"target", "reason"}, "reserve": {"operation_id"}, "dispatch": {"operation_id"},
        "result": {"operation_id", "resolution", "observation", "reason"},
        "reconcile": {"operation_id", "resolution", "observation", "reason"},
        "evidence": {"evidence"}, "invalidate": {"new_context_sha", "reason"},
        "cancel": {"reason"}, "cancel_ack": {"operation_id", "observation", "reason"},
    }
    for key in ("target", "operation_id", "resolution", "observation", "evidence", "new_context_sha", "reason"):
        if result[key] not in (None, []) and key not in applicable[result["action"]]:
            c._fail("INVALID_COMMAND", "command." + key, "Field is not applicable to this action.")
    required = {
        "advance": ("target",), "reserve": ("operation_id",), "dispatch": ("operation_id",),
        "result": ("operation_id", "resolution", "reason"),
        "reconcile": ("operation_id", "resolution", "observation", "reason"),
        "evidence": ("evidence",), "invalidate": ("new_context_sha", "reason"),
        "cancel": ("reason",), "cancel_ack": ("operation_id", "observation", "reason"),
    }
    if any(result[key] in (None, []) for key in required[result["action"]]):
        c._fail("INVALID_COMMAND", "command", "Action is missing required fields.")
    c.canonical_json(result)
    return result


def _event_id(kind: str, entity_id: str, key: str) -> str:
    return "evt-" + c.record_digest({"kind": kind, "id": entity_id, "key": key})


def _event(value: object) -> Event:
    record = c._object(value, {
        "schema_version", "id", "entity_id", "kind", "command_key", "command_sha", "command", "before_revision", "after_sha", "after",
    }, "event")
    if record["schema_version"] != "sparkforge.event.v1":
        c._fail("UNSUPPORTED_SCHEMA", "event", "Unsupported event version.")
    after = validate_projection(record["after"])
    command = _command(record["command"])
    key = c._identifier(record["command_key"], "event.command_key")
    if (record["kind"] != after["kind"] or record["entity_id"] != after["id"]
            or record["id"] != _event_id(after["kind"], after["id"], key)
            or command["key"] != key or command["entity_id"] != after["id"]
            or command["expected_revision"] != record["before_revision"]
            or record["command_sha"] != c.record_digest(command)
            or record["after_sha"] != c.record_digest(after)
            or c._integer(record["before_revision"], "event.before_revision") + 1 != after["revision"]):
        c._fail("INVALID_EVENT", "event", "Event identity, revision or projection digest is inconsistent.")
    return {
        "schema_version": "sparkforge.event.v1", "id": record["id"], "entity_id": after["id"], "kind": after["kind"],
        "command_key": key, "command_sha": c._sha(record["command_sha"], "event.command_sha"),
        "command": command,
        "before_revision": record["before_revision"], "after_sha": record["after_sha"], "after": after,
    }


def apply_command(value: object, command: object, *, previous_event: Event | None = None) -> TransitionResult:
    """Return a new projection/event or a no-op replay. Never write a journal or dispatch."""
    state, command = validate_projection(value), _command(command)
    payload_sha = c.record_digest(command)
    if command["entity_id"] != state["id"]:
        c._fail("ENTITY_MISMATCH", "command.entity_id", "Command targets a different entity.")
    if previous_event is not None:
        prior = _event(previous_event)
        if (prior["entity_id"] != state["id"] or prior["kind"] != state["kind"]
                or prior["command_key"] != command["key"] or prior["command_sha"] != payload_sha):
            c._fail("IDEMPOTENCY_CONFLICT", "command.key", "Stored key is bound to a different command or entity.")
        if state["revision"] < prior["after"]["revision"] or (
            state["revision"] == prior["after"]["revision"] and c.record_digest(state) != prior["after_sha"]
        ):
            c._fail("REPLAY_STATE_MISMATCH", "projection", "Current projection does not contain the recorded command.")
        return {"projection": state, "event": prior, "replayed": True}
    if command["expected_revision"] != state["revision"]:
        c._fail("REVISION_CONFLICT", "command.expected_revision", "Expected revision differs from the current projection.")
    if command["context_sha"] != state["context_sha"]:
        c._fail("STALE_CONTEXT", "command.context_sha", "Command uses a superseded intent/plan/candidate/evidence context.")
    action, kind, status = command["action"], state["kind"], state["status"]
    if not TRANSITIONS[kind][status] and status != INITIAL[kind]:
        c._fail("TERMINAL_STATE", "projection.status", "Terminal work cannot admit a new command.")
    if state["stop_requested"] and action not in ("result", "reconcile", "cancel_ack", "advance"):
        c._fail("STOP_REQUESTED", "command", "Cancellation stops new work.")
    if action == "advance":
        target = command["target"]
        if state["stop_requested"]:
            if target != "cancelled":
                c._fail("STOP_REQUESTED", "command.target", "Late results cannot resurrect cancelled scope.")
        elif target not in TRANSITIONS[kind][status]:
            c._fail("INVALID_TRANSITION", "command.target", "The requested transition is not legal.")
        if _unresolved(state) and not (kind == "attempt" and status == "accepted" and target == "running"):
            c._fail("UNRESOLVED_OPERATIONS", "projection", "Resolve operations before advancing the workflow.")
        if target in ("blocked", "failed", "needs_decision", "diagnosing") and command["reason"] is None:
            c._fail("MISSING_CAUSE", "command.reason", "This transition must retain its cause.")
        if target in ("verified", "delivered", "completed"):
            _completion(state)
        state["status"] = target
    elif action == "reserve":
        if status not in RESERVABLE[kind] or _unresolved(state):
            c._fail("DISPATCH_BLOCKED", "projection", "This state cannot reserve additional work.")
        if any(operation["id"] == command["operation_id"] for operation in state["operations"]):
            c._fail("OPERATION_CONFLICT", "command.operation_id", "Operation identities are never reused.")
        if len(state["operations"]) >= c.MAX_ITEMS:
            c._fail("OPERATION_LIMIT", "projection.operations", "This bounded projection already contains 128 reservations.")
        state["operations"].append({"id": command["operation_id"], "status": "reserved", "dispatched": False})
        if kind == "task":
            state["status"] = "reserved"
    elif action in ("dispatch", "result", "reconcile", "cancel_ack"):
        operation = next((item for item in state["operations"] if item["id"] == command["operation_id"]), None)
        if operation is None or operation["status"] not in OPEN_OPERATIONS:
            c._fail("OPERATION_CONFLICT", "command.operation_id", "No unresolved reservation matches this operation.")
        if action == "dispatch":
            if operation["status"] != "reserved":
                c._fail("DISPATCH_BLOCKED", "operation", "Unknown or already-dispatched work cannot be replayed.")
            operation["status"], operation["dispatched"] = "dispatched", True
            state["has_dispatched"] = True
            if kind != "job" or status == "ready":
                state["status"] = "accepted" if kind == "attempt" else "running"
        elif action == "cancel_ack":
            if not state["stop_requested"]:
                c._fail("INVALID_TRANSITION", "command", "No cancellation was requested.")
            operation["status"] = "cancel_requested"
        else:
            resolution = command["resolution"]
            if action == "result" and not operation["dispatched"]:
                c._fail("RESULT_BEFORE_DISPATCH", "operation", "An undispatched reservation requires explicit reconciliation.")
            if action == "result" and resolution == "not_started":
                c._fail("INVALID_COMMAND", "command.resolution", "Only reconciliation can establish unused work.")
            if resolution != "unknown" and command["observation"] is None:
                c._fail("MISSING_OBSERVATION", "command.observation", "Known outcomes require an admitted observation reference.")
            operation["status"] = resolution
            if resolution in ("completed", "failed", "cancelled"):
                state["has_dispatched"] = True
                operation["dispatched"] = True
            if resolution == "unknown":
                state["status"] = "reconciling" if kind == "job" else "unknown"
            elif not state["stop_requested"]:
                if resolution == "not_started":
                    state["status"] = "failed" if kind == "attempt" else "ready"
                elif resolution in ("failed", "cancelled"):
                    state["status"] = "diagnosing" if kind == "job" else "failed"
                elif resolution == "completed" and (
                    status in ("reserved", "unknown", "reconciling") or (kind == "job" and status == "ready")
                ):
                    state["status"] = "running"
    elif action == "evidence":
        inventory = {item["slot"]: item for item in state["evidence"]}
        for item in command["evidence"]:
            if item["slot"] not in state["required_evidence"]:
                c._fail("UNEXPECTED_EVIDENCE", "command.evidence", "The required inventory cannot be expanded or replaced by a worker.")
            if item["context_sha"] != state["context_sha"]:
                c._fail("STALE_CONTEXT", "command.evidence", "Receipt belongs to a superseded context.")
            prior = inventory.get(item["slot"])
            if prior is not None and prior["context_sha"] == state["context_sha"] and prior != item:
                c._fail("EVIDENCE_CONFLICT", "command.evidence", "A changed receipt requires a new evidence context.")
            inventory[item["slot"]] = item
        state["evidence"] = list(inventory.values())
    elif action == "invalidate":
        if kind == "attempt" or _unresolved(state) or command["new_context_sha"] == state["context_sha"]:
            c._fail("INVALID_INVALIDATION", "command", "Use a new context on a reconciled job/task; attempts are not recycled.")
        state["context_sha"] = command["new_context_sha"]
        state["status"] = "planning" if kind == "job" else "ready"
        state["has_dispatched"] = False
    elif action == "cancel":
        state["stop_requested"] = True
        for operation in state["operations"]:
            if operation["status"] in OPEN_OPERATIONS:
                operation["status"] = "cancel_requested"
        state["status"] = ("cancel_requested" if kind == "attempt" else "cancelling") if _unresolved(state) else "cancelled"
    before_revision = state["revision"]
    if command["reason"] is not None:
        state["cause"] = command["reason"]
    state["revision"] += 1
    state = validate_projection(state)
    event: Event = {
        "schema_version": "sparkforge.event.v1", "id": _event_id(kind, state["id"], command["key"]),
        "entity_id": state["id"], "kind": kind, "command_key": command["key"], "command_sha": payload_sha, "command": command,
        "before_revision": before_revision, "after_sha": c.record_digest(state), "after": state,
    }
    return {"projection": state, "event": _event(event), "replayed": False}
