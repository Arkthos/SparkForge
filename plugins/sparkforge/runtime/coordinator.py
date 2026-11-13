"""Serial scripted-host coordination over the durable journal, not a live factory."""

from __future__ import annotations

from pathlib import Path

from . import agent_contracts as a
from . import contracts as c
from . import host as h
from . import scheduler as s
from . import store
from . import transitions as t


def _key(action: str, identity: object) -> str:
    return action + "-" + c.record_digest(identity)


def _command(projection: dict, action: str, *, key: str | None = None, **fields) -> t.Command:
    return {
        "schema_version": "sparkforge.command.v1", "key": key or _key(action, [projection["kind"], projection["id"], projection["revision"]]),
        "entity_id": projection["id"], "expected_revision": projection["revision"], "context_sha": projection["context_sha"],
        "action": action, "target": None, "operation_id": None, "resolution": None, "observation": None,
        "evidence": [], "new_context_sha": None, "reason": None, **fields,
    }


def _report(status: str, *, task_id: str | None = None, operation_key: str | None = None, reason: str) -> dict:
    return {"status": status, "task_id": task_id, "operation_key": operation_key, "job_ready": False,
            "evidence_class": "scripted_coordination", "reason": reason}


def _task_projection(snapshot: dict, task: a.TaskAssignment) -> dict:
    return snapshot["entities"]["task:" + task["binding"]["task_id"]]["projection"]


class Coordinator:
    def __init__(self, root: Path, adapter: h.HostAdapter):
        self.root, self.adapter = root, adapter

    def install(self, schedule: s.Schedule) -> dict:
        snapshot = store.read(self.root)
        if snapshot["job"] is None:
            c._fail("JOB_REQUIRED", "coordinator", "Initialize a job before installing a task graph.")
        job = snapshot["job"]
        intent = snapshot["records"][job["intent_sha"]]["value"]
        envelope = snapshot["records"][job["envelope_sha"]]["value"]
        schedule = s.validate_schedule(schedule, intent=intent, envelope=envelope)
        if schedule["job_id"] != job["job_id"]:
            c._fail("BINDING_MISMATCH", "coordinator", "Graph belongs to a different job.")
        if schedule["job_context_sha"] != snapshot["entities"]["job:" + job["job_id"]]["projection"]["context_sha"]:
            c._fail("STALE_CONTEXT", "coordinator", "Graph belongs to an earlier job context.")
        capabilities = h.validate_capabilities(self.adapter.discover())
        if capabilities["evidence_class"] != "scripted_fake":
            c._fail("HOST_NOT_QUALIFIED", "coordinator", "Only the source-neutral scripted host is supported at this stage.")
        for task in schedule["tasks"]:
            h.require_capabilities(capabilities, task, ("dispatch", "poll", "reconcile", "producer_context"))
        caps_sha = store.append_record(self.root, "install-host", job["job_id"], store.record_value(
            "capabilities", capabilities["host"]["id"], capabilities["host"]["revision"], capabilities))["record_sha"]
        store.append_record(self.root, "install-schedule", job["job_id"], store.record_value(
            "schedule", schedule["id"], schedule["revision"], schedule, context={"capabilities_sha": caps_sha}))
        for task in schedule["tasks"]:
            store.register(self.root, _key("register", c.record_digest(task)), "task", task, required_evidence=["worker_result"])
        return self.status()

    def _context(self) -> tuple[dict, s.Schedule, h.HostCapabilities]:
        snapshot = store.read(self.root)
        records = [record for record in snapshot["records"].values() if record["kind"] == "schedule"]
        if len(records) != 1:
            c._fail("SCHEDULE_REQUIRED", "coordinator", "One pinned installed graph is required.")
        record = records[0]
        schedule = record["value"]
        if snapshot["entities"]["job:" + schedule["job_id"]]["projection"]["context_sha"] != schedule["job_context_sha"]:
            c._fail("STALE_CONTEXT", "coordinator", "The pinned graph cannot continue after job-context invalidation.")
        capabilities = snapshot["records"][record["context"]["capabilities_sha"]]["value"]
        expected = {task["binding"]["task_id"]: c.record_digest(task) for task in schedule["tasks"]}
        actual = {name[5:]: entity["task_sha"] for name, entity in snapshot["entities"].items() if name.startswith("task:")}
        if actual != expected:
            c._fail("TASK_INVENTORY_MISMATCH", "coordinator", "Resume installation or reconcile mismatched task inventory before work.")
        for task in schedule["tasks"]:
            state = _task_projection(snapshot, task)
            if state["context_sha"] != c.record_digest(task["binding"]) or state["required_evidence"] != ["worker_result"]:
                c._fail("STALE_CONTEXT", "coordinator", "Pinned graph cannot adopt a changed task context/evidence inventory.")
            if state["status"] == "completed":
                self._completed_result(snapshot, task)
        return snapshot, schedule, capabilities

    def _completed_result(self, snapshot: dict, task: a.TaskAssignment) -> None:
        reservation = snapshot["reservations"].get(s.operation_key(task))
        if reservation is None or reservation["status"] != "completed" or reservation["observation_sha"] is None:
            c._fail("MISSING_RESULT", "coordinator", "Task completion lacks its exact completed host operation.")
        observed = snapshot["records"][reservation["observation_sha"]]["value"]
        record = snapshot["records"].get(observed["result_sha"])
        if (record is None or record["kind"] != "result" or record["value"]["task_sha"] != c.record_digest(task)
                or record["value"]["outcome"] != "completed" or record["value"]["next_action"] != "complete"
                or any(finding["severity"] in ("error", "critical") for finding in record["value"]["findings"])):
            c._fail("MISSING_RESULT", "coordinator", "A host turn or arbitrary passing marker is not a successful structured task result.")

    def _host(self, pinned: h.HostCapabilities) -> None:
        if h.validate_capabilities(self.adapter.discover()) != pinned:
            c._fail("HOST_CONTEXT_MISMATCH", "coordinator", "The installed host capabilities changed; no new work is admitted.")

    def status(self) -> dict:
        return self._status(*self._context())

    def _status(self, snapshot: dict, schedule: s.Schedule, capabilities: h.HostCapabilities) -> dict:
        job = snapshot["entities"]["job:" + schedule["job_id"]]["projection"]
        unresolved = [item for item in snapshot["reservations"].values() if item["status"] in t.OPEN_OPERATIONS]
        if job["stop_requested"]:
            reason = "Job stop request prevents new work; outstanding effects must reconcile."
            if unresolved and capabilities["support"]["cancel"] != "supported":
                reason = "Host cancellation is unsupported/unassessed; new work is stopped, but existing effects can only be observed."
            return _report("CANCELLING" if unresolved or job["status"] != "cancelled" else "CANCELLED",
                           reason=reason)
        if unresolved:
            return _report("RECONCILIATION_REQUIRED", task_id=unresolved[0]["binding"]["task_id"],
                           operation_key=unresolved[0]["operation_key"], reason="An existing reservation must be observed before any new dispatch.")
        states = {task["binding"]["task_id"]: _task_projection(snapshot, task) for task in schedule["tasks"]}
        if all(state["status"] == "completed" for state in states.values()):
            return _report("AWAITING_JOB_ACCEPTANCE", reason="All required role tasks finished; live policy/controller/delivery admission is not implemented.")
        for task in schedule["tasks"]:
            state = states[task["binding"]["task_id"]]
            if state["status"] in ("running", "unknown"):
                return _report("AWAITING_RESULT", task_id=state["id"], operation_key=s.operation_key(task),
                               reason="Observed host completion still requires the bound structured result.")
            if state["status"] in ("failed", "blocked", "cancelled"):
                return _report("BLOCKED", task_id=state["id"], reason=state["cause"] or "Required work is incomplete.")
        candidate = s.ready_task(schedule, states)
        if candidate is None:
            return _report("BLOCKED", reason="No dependency-ready task is available.")
        if s.operation_key(candidate) in snapshot["reservations"]:
            return _report("RETRY_REQUIRES_PLAN", task_id=candidate["binding"]["task_id"],
                           reason="An unused/failed operation is retained; this fixed graph cannot silently allocate another attempt.")
        envelope = snapshot["records"][schedule["envelope_sha"]]["value"]
        if envelope["unknown_usage"] == "stop" and any(
            item["observation_sha"] is not None and
            snapshot["records"][item["observation_sha"]]["value"]["usage"]["status"] == "unknown"
            for item in snapshot["reservations"].values()
        ):
            return _report("USAGE_UNKNOWN", reason="Selected envelope stops new admission when consumption is unobserved.")
        return _report("READY", task_id=candidate["binding"]["task_id"], operation_key=s.operation_key(candidate),
                       reason="Dependencies are complete and no operation is unresolved.")

    def _record_receipt(self, task: a.TaskAssignment, capabilities: h.HostCapabilities, receipt: h.HostReceipt) -> None:
        key = s.operation_key(task)
        receipt = h.validate_receipt(receipt, capabilities=capabilities, task=task, operation_key=key)
        snapshot, schedule, _ = self._context()
        sha = c.record_digest(receipt)
        if sha in snapshot["records"]:
            return
        existing = [record["revision"] for record in snapshot["records"].values()
                    if record["kind"] == "observation" and record["id"] == receipt["observation"]["id"]]
        record = store.record_value("observation", receipt["observation"]["id"], max(existing, default=0) + 1,
                                    receipt, context={"capabilities_sha": c.record_digest(capabilities)})
        resolution = {"completed": "completed", "failed": "failed", "stopped": "cancelled",
                      "not_started": "not_started"}.get(receipt["status"], "unknown")
        state = _task_projection(snapshot, task)
        store.apply(self.root, "task", _command(
            state, "reconcile", key=_key("observe", [key, sha]), operation_id=key, resolution=resolution,
            observation=receipt["observation"], reason=receipt["reason"]), records=(record,))

    def tick(self) -> dict:
        snapshot, schedule, capabilities = self._context()
        report = self._status(snapshot, schedule, capabilities)
        if report["status"] not in ("READY", "RECONCILIATION_REQUIRED", "CANCELLING"):
            return report
        self._host(capabilities)
        unresolved = [item for item in snapshot["reservations"].values() if item["status"] in t.OPEN_OPERATIONS]
        if unresolved:
            reservation = unresolved[0]
            task = next(item for item in schedule["tasks"] if c.record_digest(item) == reservation["task_sha"])
            state, key = _task_projection(snapshot, task), reservation["operation_key"]
            if key != s.operation_key(task) or reservation["owner_kind"] != "task" or reservation["owner_id"] != state["id"]:
                c._fail("OPERATION_CONFLICT", "coordinator", "Reservation is outside this graph's exact task operation.")
            job = snapshot["entities"]["job:" + schedule["job_id"]]["projection"]
            action = "reconcile"
            if reservation["observation_sha"] is not None:
                previous = snapshot["records"][reservation["observation_sha"]]["value"]
                if previous["status"] in ("accepted", "running", "cancel_requested"):
                    action = "poll"
            if job["stop_requested"] and not state["stop_requested"]:
                stopped = store.apply(self.root, "task", _command(state, "cancel", reason="Parent job requested cancellation."))
                if not stopped["replayed"] and capabilities["support"]["cancel"] == "supported":
                    action = "cancel"
            try:
                receipt = getattr(self.adapter, action)(task, key)
            except c.ContractError as error:
                if error.code not in ("HOST_OPERATION_UNKNOWN", "HOST_RESPONSE_LOST"):
                    raise
                return _report("RECONCILIATION_REQUIRED", task_id=state["id"], operation_key=key,
                               reason=f"{error.code}: no no-effect proof; reservation retained.")
            self._record_receipt(task, capabilities, receipt)
            return self.status()
        if report["status"] == "CANCELLING":
            for task in schedule["tasks"]:
                state = _task_projection(store.read(self.root), task)
                if state["status"] not in ("completed", "cancelled"):
                    if not state["stop_requested"]:
                        state = store.apply(self.root, "task", _command(state, "cancel", reason="Parent job stopped."))["projection"]
                    if state["status"] != "cancelled":
                        store.apply(self.root, "task", _command(state, "advance", target="cancelled"))
            job = store.read(self.root)["entities"]["job:" + schedule["job_id"]]["projection"]
            if job["status"] != "cancelled":
                store.apply(self.root, "job", _command(job, "advance", target="cancelled"))
            return self.status()
        task = next(item for item in schedule["tasks"] if item["binding"]["task_id"] == report["task_id"])
        state, key = _task_projection(snapshot, task), s.operation_key(task)
        h.require_capabilities(capabilities, task, ("dispatch", "poll", "reconcile", "producer_context"))
        if state["status"] == "pending":
            state = store.apply(self.root, "task", _command(state, "advance", target="ready"))["projection"]
        reserved = store.apply(self.root, "task", _command(state, "reserve", operation_id=key))
        if reserved["replayed"]:
            return self.status()
        dispatched = store.apply(self.root, "task", _command(reserved["projection"], "dispatch", operation_id=key))
        if dispatched["replayed"]:
            return self.status()
        # A committed dispatch marker is not proof the host ran; failure must remain reconcilable.
        latest_job = store.read(self.root)["entities"]["job:" + schedule["job_id"]]["projection"]
        if latest_job["stop_requested"]:
            return self.status()
        try:
            receipt = self.adapter.dispatch(task, key)
        except c.ContractError as error:
            if error.code not in ("HOST_RESPONSE_LOST", "HOST_DISPATCH_REJECTED", "HOST_RECONCILIATION_REQUIRED"):
                raise
            return _report("RECONCILIATION_REQUIRED", task_id=state["id"], operation_key=key,
                           reason=f"{error.code}: dispatch marker retained; inspect rather than replay.")
        self._record_receipt(task, capabilities, receipt)
        return self.status()

    def cancel(self, reason: str) -> dict:
        snapshot, schedule, _ = self._context()
        job = snapshot["entities"]["job:" + schedule["job_id"]]["projection"]
        if not job["stop_requested"]:
            store.apply(self.root, "job", _command(job, "cancel", reason=reason))
        return self.status()

    def submit_result(self, result: a.AgentResult, attempt: a.AgentAttempt) -> dict:
        snapshot, schedule, _ = self._context()
        task = next((item for item in schedule["tasks"] if item["binding"] == result.get("binding")), None)
        if task is None:
            c._fail("BINDING_MISMATCH", "result", "No current assignment matches this result.")
        job = snapshot["entities"]["job:" + schedule["job_id"]]["projection"]
        state = _task_projection(snapshot, task)
        if job["stop_requested"] or state["stop_requested"]:
            c._fail("STOP_REQUESTED", "result", "Late results cannot resurrect stopped work.")
        reservation = snapshot["reservations"].get(s.operation_key(task))
        if reservation is None or reservation["status"] != "completed" or reservation["observation_sha"] is None:
            c._fail("RESULT_BEFORE_COMPLETION", "result", "The exact host operation must be observed completed first.")
        observed = snapshot["records"][reservation["observation_sha"]]["value"]
        if observed["result_sha"] != c.record_digest(result) or attempt["observation"] != observed["observation"]:
            c._fail("BINDING_MISMATCH", "result", "Result/attempt differ from the host's exact completion reference.")
        predecessors = set(task["dependencies"])
        pending = list(predecessors)
        tasks = {item["binding"]["task_id"]: item for item in schedule["tasks"]}
        while pending:
            for dependency in tasks[pending.pop()]["dependencies"]:
                if dependency not in predecessors:
                    predecessors.add(dependency)
                    pending.append(dependency)
        prior_attempts = [sha for sha, record in snapshot["records"].items()
                          if record["kind"] == "attempt" and record["value"]["binding"]["task_id"] in predecessors]
        normalized_attempt = a.validate_attempt(attempt, task=task)
        normalized_result = a.validate_result(result, task=task, attempt=normalized_attempt,
                                              current_candidate_sha=schedule["candidate_sha"],
                                              prior_producers=tuple(snapshot["records"][sha]["value"]["producer"] for sha in prior_attempts))
        attempt_record = store.record_value("attempt", task["binding"]["attempt_id"], 1, normalized_attempt)
        result_record = store.record_value("result", normalized_result["id"], 1, normalized_result,
                                          context={"attempt_sha": c.record_digest(normalized_attempt), "prior_attempts": prior_attempts})
        passed = (normalized_result["outcome"] == "completed" and normalized_result["next_action"] == "complete"
                  and not normalized_result["changed_paths"]
                  and normalized_result["output_candidate_sha"] in (None, schedule["candidate_sha"])
                  and not any(item["severity"] in ("error", "critical") for item in normalized_result["findings"]))
        if not passed:
            if state["status"] == "blocked" and c.record_digest(normalized_result) in snapshot["records"]:
                return self.status()
            store.apply(self.root, "task", _command(
                state, "advance", target="blocked", reason="Result requires candidate integration, correction or a material decision."),
                records=(attempt_record, result_record))
            return self.status()
        result_sha = c.record_digest(normalized_result)
        evidence = {"schema_version": "sparkforge.artifact-reference.v1", "id": "result-" + result_sha,
                    "artifact_kind": "evidence", "sha256": result_sha, "assessment": "unassessed"}
        evidence_record = store.record_value("artifact", evidence["id"], 1, evidence)
        if state["status"] == "completed":
            self._completed_result(snapshot, task)
            return self.status()
        expected = {"slot": "worker_result", "receipt": {"id": evidence["id"], "sha256": result_sha},
                    "context_sha": state["context_sha"], "outcome": "pass"}
        if expected not in state["evidence"]:
            state = store.apply(self.root, "task", _command(
                state, "evidence", key=_key("result", result_sha), evidence=[expected]),
                records=(attempt_record, result_record, evidence_record))["projection"]
        store.apply(self.root, "task", _command(state, "advance", target="completed"))
        return self.status()
