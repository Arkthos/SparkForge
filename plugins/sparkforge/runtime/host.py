"""Host protocol and observation validation, not a native launcher or trusted ingress."""

from __future__ import annotations

from typing import Protocol, TypedDict

from . import agent_contracts as a
from . import contracts as c


CAPABILITIES = ("dispatch", "poll", "cancel", "reconcile", "producer_context", "usage", "scope_enforcement")
STATUSES = ("accepted", "running", "completed", "failed", "cancel_requested", "stopped", "not_started", "unknown")
EVIDENCE_CLASSES = ("scripted_fake", "host_observed")


class HostCapabilities(TypedDict):
    schema_version: str
    host: c.Reference
    build: str
    environment: str
    profile: c.Reference
    provider: c.Reference
    evidence_class: str
    support: dict[str, str]
    roles: list[str]
    tools: list[str]
    effects: list[str]


class HostReceipt(TypedDict):
    schema_version: str
    host: c.Reference
    environment: str
    profile: c.Reference
    provider: c.Reference
    evidence_class: str
    operation_key: str
    task_sha: str
    binding: a.TaskBinding
    status: str
    producer: a.Producer | None
    usage: a.Usage
    effect_state: str
    cancel_acknowledged: bool
    stop_observed: bool
    observation: a.DigestReference
    result_sha: str | None
    reason: str


class HostAdapter(Protocol):
    def discover(self) -> HostCapabilities: ...

    def dispatch(self, task: a.TaskAssignment, operation_key: str, *,
                 required: tuple[str, ...] = ("dispatch", "poll", "reconcile", "producer_context")) -> HostReceipt: ...

    def poll(self, task: a.TaskAssignment, operation_key: str) -> HostReceipt: ...

    def cancel(self, task: a.TaskAssignment, operation_key: str) -> HostReceipt: ...

    def reconcile(self, task: a.TaskAssignment, operation_key: str) -> HostReceipt: ...


def validate_capabilities(value: object) -> HostCapabilities:
    record = c._object(value, {
        "schema_version", "host", "build", "environment", "profile", "provider", "evidence_class",
        "support", "roles", "tools", "effects",
    }, "host")
    if record["schema_version"] != "sparkforge.host-capabilities.v1":
        c._fail("UNSUPPORTED_SCHEMA", "host", "Unsupported host capability version.")
    support = c._object(record["support"], set(CAPABILITIES), "host.support")
    result: HostCapabilities = {
        "schema_version": "sparkforge.host-capabilities.v1",
        "host": c._reference(record["host"], "host.host"),
        "build": c._text(record["build"], "host.build", limit=200),
        "environment": c._enum(record["environment"], ("LOCAL_DEVELOPMENT", "CORP", "ACRO"), "host.environment"),
        "profile": c._reference(record["profile"], "host.profile"),
        "provider": c._reference(record["provider"], "host.provider"),
        "evidence_class": c._enum(record["evidence_class"], EVIDENCE_CLASSES, "host.evidence_class"),
        "support": {name: c._enum(support[name], ("supported", "unsupported", "unknown"), "host.support." + name)
                    for name in CAPABILITIES},
        "roles": c._strings(record["roles"], "host.roles", identifiers=True),
        "tools": c._strings(record["tools"], "host.tools", identifiers=True),
        "effects": c._strings(record["effects"], "host.effects", identifiers=True),
    }
    if not set(result["roles"]) <= set(a.RESULT_KINDS):
        c._fail("ROLE_VIOLATION", "host.roles", "Capability list contains an unknown role.")
    c.canonical_json(result)
    return result


def require_capabilities(value: object, task: a.TaskAssignment, required: tuple[str, ...]) -> HostCapabilities:
    """Check selected-host compatibility before effects; not execution authorization."""
    host, task = validate_capabilities(value), a._task(task)
    if type(required) is not tuple or not 1 <= len(required) <= len(CAPABILITIES):
        c._fail("INVALID_CAPABILITIES", "required", "Supply a nonempty bounded tuple of required capabilities.")
    c._unique([c._enum(name, CAPABILITIES, "required") for name in required], "required")
    if (task["environment"] != host["environment"] or task["profile"] != host["profile"]
            or task["routes"]["host"] != host["host"] or task["routes"]["provider"] != host["provider"]):
        c._fail("HOST_CONTEXT_MISMATCH", "host", "Selected host, environment, profile and provider must match the assignment.")
    if task["binding"]["role"] not in host["roles"]:
        c._fail("HOST_UNSUPPORTED", "host.roles", "Assigned role is unsupported.")
    for field in ("tools", "effects"):
        if not set(task[field]) <= set(host[field]):
            c._fail("HOST_UNSUPPORTED", "host." + field, "Assigned scope is unsupported.")
    for name in required:
        if host["support"][name] != "supported":
            c._fail("HOST_UNSUPPORTED", "host.support." + name, "Required capability is unsupported or unassessed.")
    return host


def validate_receipt(
    value: object, *, capabilities: HostCapabilities, task: a.TaskAssignment, operation_key: str,
) -> HostReceipt:
    host, task = validate_capabilities(capabilities), a._task(task)
    operation_key = c._identifier(operation_key, "operation_key")
    record = c._object(value, {
        "schema_version", "host", "environment", "profile", "provider", "evidence_class",
        "operation_key", "task_sha", "binding", "status", "producer", "usage", "effect_state",
        "cancel_acknowledged", "stop_observed", "observation", "result_sha", "reason",
    }, "receipt")
    if record["schema_version"] != "sparkforge.host-receipt.v1":
        c._fail("UNSUPPORTED_SCHEMA", "receipt", "Unsupported host receipt version.")
    for key in ("host", "environment", "profile", "provider", "evidence_class"):
        observed = c._reference(record[key], "receipt." + key) if key in ("host", "profile", "provider") else record[key]
        if observed != host[key]:
            c._fail("HOST_CONTEXT_MISMATCH", "receipt." + key, "Receipt does not belong to the selected host context.")
    if (task["environment"] != host["environment"] or task["profile"] != host["profile"]
            or task["routes"] != {"host": host["host"], "provider": host["provider"]}):
        c._fail("HOST_CONTEXT_MISMATCH", "receipt", "Receipt context differs from the assignment.")
    binding = a._binding(record["binding"])
    task_sha = c._sha(record["task_sha"], "receipt.task_sha")
    if binding != task["binding"] or task_sha != c.record_digest(task) or record["operation_key"] != operation_key:
        c._fail("BINDING_MISMATCH", "receipt", "Receipt names another operation or assignment.")
    status = c._enum(record["status"], STATUSES, "receipt.status")
    producer = None if record["producer"] is None else a._producer(record["producer"])
    if producer is not None and (producer["host"] != host["host"] or producer["role"] != binding["role"]):
        c._fail("PRODUCER_MISMATCH", "receipt.producer", "Producer differs from the assigned host/role.")
    if host["support"]["producer_context"] != "supported" and producer is not None:
        c._fail("UNSUPPORTED_OBSERVATION", "receipt.producer", "Unobservable producer context cannot be presented as known.")
    if host["support"]["producer_context"] == "supported" and status not in ("unknown", "not_started") and producer is None:
        c._fail("MISSING_OBSERVATION", "receipt.producer", "Observed work needs the supported producer context.")
    usage = a._usage(record["usage"], "receipt.usage")
    if host["support"]["usage"] != "supported" and usage["status"] != "unknown":
        c._fail("UNSUPPORTED_OBSERVATION", "receipt.usage", "Unavailable usage must remain unknown, not zero.")
    for field in ("cancel_acknowledged", "stop_observed"):
        if type(record[field]) is not bool:
            c._fail("INVALID_BOOLEAN", "receipt." + field, "Expected an explicit boolean.")
    effects = c._enum(record["effect_state"], ("not_started", "possible", "settled"), "receipt.effect_state")
    expected_effects = {"not_started": "not_started", "completed": "settled", "failed": "settled", "stopped": "settled"}
    if effects != expected_effects.get(status, "possible"):
        c._fail("UNRESOLVED_EFFECTS", "receipt.effect_state", "Receipt status does not establish this effect outcome.")
    if record["stop_observed"] != (status == "stopped"):
        c._fail("UNOBSERVED_CANCELLATION", "receipt.stop_observed", "Cancellation acknowledgement is not proof work stopped.")
    if status == "cancel_requested" and not record["cancel_acknowledged"]:
        c._fail("UNOBSERVED_CANCELLATION", "receipt.cancel_acknowledged", "A cancellation request needs its acknowledgement.")
    if record["cancel_acknowledged"] and host["support"]["cancel"] != "supported":
        c._fail("UNSUPPORTED_OBSERVATION", "receipt.cancel_acknowledged", "Host cannot acknowledge an unsupported cancellation.")
    result_sha = None if record["result_sha"] is None else c._sha(record["result_sha"], "receipt.result_sha")
    if result_sha is not None and status != "completed":
        c._fail("OUTCOME_MISMATCH", "receipt.result_sha", "Only completed host work may provide a result reference.")
    if status == "not_started" and (producer is not None or (
        usage["status"] == "known" and any(usage[field] != 0 for field in ("model_calls", "tokens", "wall_seconds"))
    )):
        c._fail("OUTCOME_MISMATCH", "receipt", "Not-started work cannot claim a producer or consumed usage.")
    result: HostReceipt = {
        "schema_version": "sparkforge.host-receipt.v1",
        "host": dict(host["host"]), "environment": host["environment"], "profile": dict(host["profile"]),
        "provider": dict(host["provider"]), "evidence_class": host["evidence_class"],
        "operation_key": operation_key, "task_sha": task_sha, "binding": binding, "status": status,
        "producer": producer, "usage": usage, "effect_state": effects,
        "cancel_acknowledged": record["cancel_acknowledged"], "stop_observed": record["stop_observed"],
        "observation": a._ref(record["observation"], "receipt.observation"),
        "result_sha": result_sha, "reason": c._text(record["reason"], "receipt.reason"),
    }
    c.canonical_json(result)
    return result
