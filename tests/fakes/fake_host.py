"""Scripted observations only: no files, subprocesses, models or native host APIs."""

from dataclasses import dataclass

from plugins.sparkforge.runtime import agent_contracts as a
from plugins.sparkforge.runtime import contracts as c
from plugins.sparkforge.runtime import host as h


@dataclass(frozen=True)
class Script:
    statuses: tuple[str, ...] = ("accepted", "running", "completed")
    usage: a.Usage | None = None
    result_sha: str | None = None
    lose_dispatch_response: bool = False
    reject_before_dispatch: bool = False


class FakeHost:
    def __init__(self, capabilities: h.HostCapabilities, scripts: dict[str, Script]) -> None:
        self._capabilities = h.validate_capabilities(capabilities)
        if self._capabilities["evidence_class"] != "scripted_fake":
            c._fail("INVALID_FAKE", "host", "A fake cannot claim actual host observations.")
        if type(scripts) is not dict or len(scripts) > 128:
            c._fail("INVALID_FAKE", "scripts", "Provide at most 128 owned operation scripts.")
        self._scripts: dict[str, Script] = {}
        self._operations: dict[str, dict] = {}
        self.calls = {name: 0 for name in ("discover", "dispatch", "poll", "cancel", "reconcile")}
        self.dispatch_count = 0
        self.cancel_count = 0
        for key, script in scripts.items():
            c._identifier(key, "script.operation_key")
            if not isinstance(script, Script) or type(script.statuses) is not tuple or not 1 <= len(script.statuses) <= 128:
                c._fail("INVALID_FAKE", "script", "Expected a bounded nonempty script.")
            for index, status in enumerate(script.statuses):
                c._enum(status, h.STATUSES, "script.status")
                if status in ("completed", "failed", "stopped", "not_started") and index != len(script.statuses) - 1:
                    c._fail("INVALID_FAKE", "script", "Terminal observations cannot be followed by more work.")
            usage = None if script.usage is None else a._usage(script.usage, "script.usage")
            result_sha = None if script.result_sha is None else c._sha(script.result_sha, "script.result_sha")
            if type(script.lose_dispatch_response) is not bool or type(script.reject_before_dispatch) is not bool:
                c._fail("INVALID_FAKE", "script", "Failure switches must be booleans.")
            self._scripts[key] = Script(script.statuses, usage, result_sha, script.lose_dispatch_response, script.reject_before_dispatch)

    def discover(self) -> h.HostCapabilities:
        self.calls["discover"] += 1
        return h.validate_capabilities(self._capabilities)

    def dispatch(self, task: a.TaskAssignment, operation_key: str, *,
                 required: tuple[str, ...] = ("dispatch", "poll", "reconcile", "producer_context")) -> h.HostReceipt:
        self.calls["dispatch"] += 1
        h.require_capabilities(self._capabilities, task, required)
        h.require_capabilities(self._capabilities, task, ("dispatch",))
        task = a._task(task)
        operation_key = c._identifier(operation_key, "operation_key")
        if operation_key in self._operations:
            if self._operations[operation_key]["task_sha"] != c.record_digest(task):
                c._fail("HOST_OPERATION_CONFLICT", "operation_key", "Operation is already bound to another assignment.")
            c._fail("HOST_RECONCILIATION_REQUIRED", "operation_key", "Inspect existing work instead of dispatching it again.")
        script = self._scripts.get(operation_key)
        if script is None:
            c._fail("UNSCRIPTED_OPERATION", "operation_key", "No fake observation script was supplied.")
        if script.usage is not None and script.usage["status"] == "known":
            h.require_capabilities(self._capabilities, task, ("usage",))
        if "cancel_requested" in script.statuses:
            h.require_capabilities(self._capabilities, task, ("cancel",))
        if script.reject_before_dispatch:
            c._fail("HOST_DISPATCH_REJECTED", "dispatch", "Scripted refusal occurred before simulated dispatch.")
        self._operations[operation_key] = {
            "task_sha": c.record_digest(task), "task": task, "index": 0, "cancel_requested": False,
        }
        self.dispatch_count += 1
        receipt = self._receipt(operation_key)
        if script.lose_dispatch_response:
            c._fail("HOST_RESPONSE_LOST", "dispatch", "Simulated dispatch happened; reconcile this operation key before retry.")
        return receipt

    def _operation(self, task: a.TaskAssignment, key: str, capability: str) -> dict:
        h.require_capabilities(self._capabilities, task, (capability,))
        c._identifier(key, "operation_key")
        operation = self._operations.get(key)
        if operation is None:
            c._fail("HOST_OPERATION_UNKNOWN", "operation_key", "This fake has no observed operation for the requested key.")
        if operation["task_sha"] != c.record_digest(a._task(task)):
            c._fail("HOST_OPERATION_CONFLICT", "operation_key", "Operation belongs to another assignment.")
        return operation

    def _advance(self, task: a.TaskAssignment, key: str, capability: str) -> h.HostReceipt:
        operation = self._operation(task, key, capability)
        operation["index"] = min(operation["index"] + 1, len(self._scripts[key].statuses) - 1)
        return self._receipt(key)

    def poll(self, task: a.TaskAssignment, operation_key: str) -> h.HostReceipt:
        self.calls["poll"] += 1
        return self._advance(task, operation_key, "poll")

    def reconcile(self, task: a.TaskAssignment, operation_key: str) -> h.HostReceipt:
        self.calls["reconcile"] += 1
        return self._advance(task, operation_key, "reconcile")

    def cancel(self, task: a.TaskAssignment, operation_key: str) -> h.HostReceipt:
        self.calls["cancel"] += 1
        operation = self._operation(task, operation_key, "cancel")
        current = self._scripts[operation_key].statuses[operation["index"]]
        if current in ("completed", "failed", "stopped", "not_started"):
            return self._receipt(operation_key)
        if not operation["cancel_requested"]:
            self.cancel_count += 1
            operation["cancel_requested"] = True
        return self._receipt(operation_key, status="cancel_requested")

    def _receipt(self, key: str, *, status: str | None = None) -> h.HostReceipt:
        operation, script, host = self._operations[key], self._scripts[key], self._capabilities
        task = operation["task"]
        status = script.statuses[operation["index"]] if status is None else status
        token = c.record_digest({"operation_key": key})[:24]
        producer = None
        if host["support"]["producer_context"] == "supported" and status != "not_started":
            producer = {"host": dict(host["host"]), "role": task["binding"]["role"],
                        "session_id": "fake-session-" + token, "context_id": "fake-context-" + token}
        usage = script.usage if script.usage is not None else {
            "status": "unknown", "model_calls": None, "tokens": None, "wall_seconds": None,
            "reason": "Scripted fake: no real model usage observed.",
        }
        value = {
            "schema_version": "sparkforge.host-receipt.v1",
            "host": dict(host["host"]), "environment": host["environment"], "profile": dict(host["profile"]),
            "provider": dict(host["provider"]), "evidence_class": "scripted_fake", "operation_key": key,
            "task_sha": operation["task_sha"], "binding": dict(task["binding"]), "status": status,
            "producer": producer, "usage": usage,
            "effect_state": "not_started" if status == "not_started" else (
                "settled" if status in ("completed", "failed", "stopped") else "possible"),
            "cancel_acknowledged": operation["cancel_requested"] or status == "cancel_requested",
            "stop_observed": status == "stopped",
            "result_sha": script.result_sha if status == "completed" else None,
            "reason": "Scripted observation only; no native task, model or OS effect was performed.",
        }
        value["observation"] = {"id": "fake-receipt-" + token, "sha256": c.record_digest(value)}
        return h.validate_receipt(value, capabilities=host, task=task, operation_key=key)
