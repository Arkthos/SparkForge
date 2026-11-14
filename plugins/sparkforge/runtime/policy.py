"""Deterministic materiality and exact decision bindings; ingress assertions are not authentication."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import TypedDict

from . import agent_contracts as a
from . import contracts as c


AUTHORITY = {"intent": "intent_owner", "envelope": "execution_owner"}
DENIALS = {
    "POLICY_REQUIRED", "DECISION_REQUIRED", "STALE_DECISION", "AUTHORITY_REVOKED",
    "ENVELOPE_EXPIRED", "TASK_EXPIRED", "POLICY_BINDING_MISMATCH", "SCOPE_VIOLATION",
}


class Target(TypedDict):
    kind: str
    id: str
    revision: int
    sha256: str


class Ingress(TypedDict):
    source: str
    actor_id: str
    authority: str
    receipt: a.DigestReference


def now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def binding_id(job_id: str) -> str:
    return "policy-" + c.record_digest(c._identifier(job_id, "job_id"))


def target(kind: str, value: dict) -> Target:
    kind = c._enum(kind, tuple(AUTHORITY), "target.kind")
    expected = c.INTENT_VERSION if kind == "intent" else c.ENVELOPE_VERSION
    if type(value) is not dict or value.get("schema_version") != expected:
        c._fail("BINDING_MISMATCH", "target", "Target kind and record version disagree.")
    return {"kind": kind, "id": c._identifier(value["id"], "target.id"),
            "revision": c._integer(value["revision"], "target.revision"), "sha256": c.record_digest(value)}


def _target(value: object) -> Target:
    record = c._object(value, {"kind", "id", "revision", "sha256"}, "target")
    return {"kind": c._enum(record["kind"], tuple(AUTHORITY), "target.kind"),
            "id": c._identifier(record["id"], "target.id"), "revision": c._integer(record["revision"], "target.revision"),
            "sha256": c._sha(record["sha256"], "target.sha256")}


def _ingress(value: object, kind: str, environment: str) -> Ingress:
    record = c._object(value, {"source", "actor_id", "authority", "receipt"}, "ingress")
    source = c._enum(record["source"], ("operator_assertion", "host_assertion", "synthetic_fixture"), "ingress.source")
    authority = c._enum(record["authority"], tuple(AUTHORITY.values()), "ingress.authority")
    if authority != AUTHORITY[kind]:
        c._fail("WRONG_AUTHORITY", "ingress.authority", "The response belongs to a different authority owner.")
    if source == "synthetic_fixture" and environment != "LOCAL_DEVELOPMENT":
        c._fail("WRONG_AUTHORITY", "ingress.source", "Synthetic decisions cannot authorize a real target environment.")
    return {"source": source, "actor_id": c._identifier(record["actor_id"], "ingress.actor_id"),
            "authority": authority, "receipt": a._ref(record["receipt"], "ingress.receipt")}


def decision_request(identifier: str, job_id: str, kind: str, value: dict, *, baseline_sha: str | None,
                     reason: str, alternatives: list[str], impact: list[str]) -> dict:
    return validate_request({
        "schema_version": "sparkforge.decision-request.v1", "id": identifier, "job_id": job_id,
        "target": target(kind, value), "baseline_sha": baseline_sha, "reason": reason,
        "alternatives": alternatives, "impact": impact,
    }, value)


def validate_request(value: object, target_value: dict) -> dict:
    record = c._object(value, {"schema_version", "id", "job_id", "target", "baseline_sha", "reason", "alternatives", "impact"}, "decision_request")
    if record["schema_version"] != "sparkforge.decision-request.v1":
        c._fail("UNSUPPORTED_SCHEMA", "decision_request", "Unsupported request schema.")
    bound = _target(record["target"])
    if bound != target(bound["kind"], target_value):
        c._fail("BINDING_MISMATCH", "decision_request.target", "Request must name the complete exact target.")
    result = {
        "schema_version": record["schema_version"], "id": c._identifier(record["id"], "decision_request.id"),
        "job_id": c._identifier(record["job_id"], "decision_request.job_id"), "target": bound,
        "baseline_sha": None if record["baseline_sha"] is None else c._sha(record["baseline_sha"], "decision_request.baseline_sha"),
        "reason": c._text(record["reason"], "decision_request.reason"),
        "alternatives": c._strings(record["alternatives"], "decision_request.alternatives", minimum=1),
        "impact": c._strings(record["impact"], "decision_request.impact", minimum=1),
    }
    c.canonical_json(result)
    return result


def decide(request: dict, response: object, *, ingress: Ingress, environment: str, at: str) -> dict:
    """Translate a separately supplied ingress assertion, never a worker's authority label."""
    response = c._object(response, {"id", "request_sha", "outcome"}, "response")
    if c._sha(response["request_sha"], "response.request_sha") != c.record_digest(request):
        c._fail("STALE_DECISION", "response", "Response names another request or changed target/impact.")
    value = {
        "schema_version": "sparkforge.decision.v1", "id": c._identifier(response["id"], "response.id"),
        "job_id": request["job_id"], "request_sha": c.record_digest(request), "target": request["target"],
        "outcome": c._enum(response["outcome"], ("accept", "reject", "changes"), "response.outcome"),
        "recorded_at": c._timestamp(at, "response.recorded_at"), "ingress": ingress,
    }
    return validate_decision(value, request, environment=environment, at=at)


def validate_decision(value: object, request: dict, *, environment: str, at: str) -> dict:
    record = c._object(value, {"schema_version", "id", "job_id", "request_sha", "target", "outcome", "recorded_at", "ingress"}, "decision")
    if record["schema_version"] != "sparkforge.decision.v1":
        c._fail("UNSUPPORTED_SCHEMA", "decision", "Unsupported decision schema.")
    bound = _target(record["target"])
    if (record["job_id"] != request["job_id"] or bound != request["target"]
            or c._sha(record["request_sha"], "decision.request_sha") != c.record_digest(request)):
        c._fail("STALE_DECISION", "decision", "Decision does not bind this exact current request/target.")
    recorded_at = c._timestamp(record["recorded_at"], "decision.recorded_at")
    if recorded_at > c._timestamp(at, "at"):
        c._fail("STALE_DECISION", "decision.recorded_at", "Future-dated decisions cannot authorize current work.")
    result = {
        "schema_version": record["schema_version"], "id": c._identifier(record["id"], "decision.id"),
        "job_id": request["job_id"], "request_sha": record["request_sha"], "target": bound,
        "outcome": c._enum(record["outcome"], ("accept", "reject", "changes"), "decision.outcome"),
        "recorded_at": recorded_at, "ingress": _ingress(record["ingress"], bound["kind"], environment),
    }
    c.canonical_json(result)
    return result


def _lookup(records: dict[str, dict], sha: str, kind: str) -> dict:
    record = records.get(c._sha(sha, "policy.reference"))
    if record is None or record["kind"] != kind or c.record_digest(record["value"]) != sha:
        c._fail("MISSING_RECORD", "policy.reference", "An exact stored policy dependency is required.")
    return record["value"]


def current_binding(records: dict[str, dict], job_id: str) -> tuple[str | None, dict | None]:
    bindings = [(sha, record["value"]) for sha, record in records.items()
                if record["kind"] == "policy_binding" and record["value"]["job_id"] == job_id]
    return max(bindings, key=lambda item: item[1]["revision"]) if bindings else (None, None)


def _revoked(records: dict[str, dict], job_id: str, kind: str, sha: str) -> bool:
    return any(record["kind"] == "revocation" and record["value"]["job_id"] == job_id
               and record["value"]["subject_kind"] == kind and record["value"]["subject_sha"] == sha
               for record in records.values())


def _grant(records: dict[str, dict], binding: dict, kind: str, *, environment: str, at: str) -> tuple[dict, dict]:
    value = _lookup(records, binding[kind + "_sha"], kind)
    decision_sha = binding[kind + "_decision_sha"]
    decision = _lookup(records, decision_sha, "decision")
    request = _lookup(records, decision["request_sha"], "decision_request")
    validate_request(request, value)
    decision = validate_decision(decision, request, environment=environment, at=at)
    if decision["job_id"] != binding["job_id"] or decision["target"] != target(kind, value):
        c._fail("STALE_DECISION", "policy_binding", "Decision grants another job or target.")
    if decision["outcome"] != "accept":
        c._fail("DECISION_REQUIRED", "policy_binding", "Only an explicit acceptance can bind execution scope.")
    if _revoked(records, binding["job_id"], kind, c.record_digest(value)) or _revoked(records, binding["job_id"], "decision", decision_sha):
        c._fail("AUTHORITY_REVOKED", "policy_binding", "A committed revocation blocks this target or decision.")
    return value, request


def validate_binding(value: object, records: dict[str, dict], *, job_id: str, environment: str, at: str,
                     workspace: str | None = None) -> dict:
    record = c._object(value, {
        "schema_version", "id", "revision", "job_id", "previous_sha", "intent_sha", "envelope_sha",
        "intent_decision_sha", "envelope_decision_sha",
    }, "policy_binding")
    if record["schema_version"] != "sparkforge.policy-binding.v1":
        c._fail("UNSUPPORTED_SCHEMA", "policy_binding", "Unsupported policy binding.")
    previous_sha, previous = current_binding(records, job_id)
    if (record["job_id"] != job_id or record["id"] != binding_id(job_id)
            or c._integer(record["revision"], "policy_binding.revision") != (1 if previous is None else previous["revision"] + 1)
            or record["previous_sha"] != previous_sha):
        c._fail("POLICY_BINDING_MISMATCH", "policy_binding", "Accepted scope must extend the exact current binding, not reset history.")
    for kind in AUTHORITY:
        _, request = _grant(records, record, kind, environment=environment, at=at)
        reused = previous is not None and record[kind + "_sha"] == previous[kind + "_sha"] and (
            record[kind + "_decision_sha"] == previous[kind + "_decision_sha"])
        baseline_sha = None if previous is None else previous[kind + "_sha"]
        if not reused and request["baseline_sha"] != baseline_sha:
            c._fail("STALE_DECISION", "policy_binding", "Decision was requested against another accepted baseline.")
    intent = c._intent(_lookup(records, record["intent_sha"], "intent"))
    envelope = c.validate_envelope(_lookup(records, record["envelope_sha"], "envelope"), intent=intent)
    _envelope_live(envelope, at)
    if envelope["environment"] != environment:
        c._fail("ENVIRONMENT_MISMATCH", "policy_binding", "A job cannot transfer its authority to another environment.")
    if workspace is not None and not any(root["path"] == workspace for root in envelope["workspace_roots"]):
        c._fail("SCOPE_VIOLATION", "policy_binding.workspace", "Accepted scope cannot silently move this store's workspace.")
    c.canonical_json(record)
    return dict(record)


def revocation(identifier: str, job_id: str, subject_kind: str, subject_sha: str, *, reason: str,
               ingress: Ingress, at: str) -> dict:
    return {"schema_version": "sparkforge.revocation.v1", "id": identifier, "job_id": job_id,
            "subject_kind": subject_kind, "subject_sha": subject_sha, "reason": reason, "recorded_at": at, "ingress": ingress}


def validate_revocation(value: object, records: dict[str, dict], *, job_id: str, environment: str, at: str) -> dict:
    record = c._object(value, {"schema_version", "id", "job_id", "subject_kind", "subject_sha", "reason", "recorded_at", "ingress"}, "revocation")
    if record["schema_version"] != "sparkforge.revocation.v1" or record["job_id"] != job_id:
        c._fail("BINDING_MISMATCH", "revocation", "Revocation must name this exact job.")
    kind = c._enum(record["subject_kind"], ("intent", "envelope", "decision"), "revocation.subject_kind")
    subject = _lookup(records, record["subject_sha"], kind)
    owner_kind = subject["target"]["kind"] if kind == "decision" else kind
    if kind == "decision" and subject["job_id"] != job_id:
        c._fail("BINDING_MISMATCH", "revocation", "Decision belongs to another job.")
    recorded_at = c._timestamp(record["recorded_at"], "revocation.recorded_at")
    if recorded_at > c._timestamp(at, "at"):
        c._fail("INVALID_TIME", "revocation", "A revocation receipt cannot be future-dated.")
    result = {
        "schema_version": record["schema_version"], "id": c._identifier(record["id"], "revocation.id"), "job_id": job_id,
        "subject_kind": kind, "subject_sha": record["subject_sha"], "reason": c._text(record["reason"], "revocation.reason"),
        "recorded_at": recorded_at, "ingress": _ingress(record["ingress"], owner_kind, environment),
    }
    c.canonical_json(result)
    return result


def _envelope_live(envelope: c.ExecutionEnvelope, at: str) -> None:
    at = c._timestamp(at, "at")
    if envelope["revocation"]["revoked_at"] is not None:
        c._fail("AUTHORITY_REVOKED", "envelope", "A revoked envelope cannot admit new work.")
    if at >= envelope["expires_at"]:
        c._fail("ENVELOPE_EXPIRED", "envelope.expires_at", "Envelope expiry prevents new admission or successful credit.")


def envelope_membership(task: a.TaskAssignment, *, intent: c.IntentBaseline, envelope: c.ExecutionEnvelope, at: str) -> a.TaskAssignment:
    envelope = c.validate_envelope(envelope, intent=intent)
    _envelope_live(envelope, at)
    task = a._task(task)
    task = a.validate_task(task, intent=intent, envelope=envelope, plan_sha=task["binding"]["plan_sha"],
                           candidate_sha=task["binding"]["candidate_sha"])
    if at >= task["deadline"]:
        c._fail("TASK_EXPIRED", "task.deadline", "The task deadline has elapsed.")
    return task


def authorize(records: dict[str, dict], *, job_id: str, environment: str, at: str,
              task: a.TaskAssignment | None = None, workspace: str | None = None) -> dict:
    sha, binding = current_binding(records, job_id)
    if binding is None:
        c._fail("POLICY_REQUIRED", "admission", "Bind explicit intent-owner and execution-owner acceptance before new work.")
    intent, _ = _grant(records, binding, "intent", environment=environment, at=at)
    envelope, _ = _grant(records, binding, "envelope", environment=environment, at=at)
    envelope = c.validate_envelope(envelope, intent=intent)
    if envelope["environment"] != environment:
        c._fail("ENVIRONMENT_MISMATCH", "admission", "Accepted envelope belongs to another environment.")
    _envelope_live(envelope, at)
    if task is not None:
        if task["binding"]["job_id"] != job_id:
            c._fail("POLICY_BINDING_MISMATCH", "admission", "Task belongs to another job.")
        if task["binding"]["intent_sha"] != binding["intent_sha"] or task["binding"]["envelope_sha"] != binding["envelope_sha"]:
            c._fail("POLICY_BINDING_MISMATCH", "admission", "Assignment uses superseded accepted scope.")
        envelope_membership(task, intent=intent, envelope=envelope, at=at)
        if workspace is not None and not any(root["id"] == task["workspace_id"] and root["path"] == workspace
                                             for root in envelope["workspace_roots"]):
            c._fail("SCOPE_VIOLATION", "task.workspace_id", "Task targets a different workspace than this store.")
    return {"binding_sha": sha, "intent_sha": binding["intent_sha"], "envelope_sha": binding["envelope_sha"],
            "authority_origin": "EXTERNAL_INGRESS_ASSERTION", "authenticated": False}


def classify_change(*, accepted_intent: c.IntentBaseline, accepted_envelope: c.ExecutionEnvelope,
                    proposed_intent: c.IntentBaseline, proposed_envelope: c.ExecutionEnvelope,
                    current_task: a.TaskAssignment | None = None, proposed_task: a.TaskAssignment | None = None,
                    label: str = "technical change", unresolved_effects: bool = False) -> dict:
    before_intent, after_intent = c._intent(accepted_intent), c._intent(proposed_intent)
    before_envelope = c.validate_envelope(accepted_envelope, intent=before_intent)
    after_envelope = c.validate_envelope(proposed_envelope, intent=after_intent)
    c._text(label, "change.label")
    if type(unresolved_effects) is not bool:
        c._fail("INVALID_BOOLEAN", "change.unresolved_effects", "Expected an explicit uncertainty state.")
    intent_fields = [key for key in before_intent if c.canonical_json(before_intent[key]) != c.canonical_json(after_intent[key])]
    envelope_fields = [key for key in before_envelope if c.canonical_json(before_envelope[key]) != c.canonical_json(after_envelope[key])]
    control_fields = []
    if (current_task is None) != (proposed_task is None):
        c._fail("INVALID_CHANGE", "change.task", "Task comparison needs both the accepted and proposed assignment.")
    if proposed_task is not None:
        current_task = a.validate_task(current_task, intent=before_intent, envelope=before_envelope,
                                       plan_sha=current_task["binding"]["plan_sha"], candidate_sha=current_task["binding"]["candidate_sha"])
        proposed_task = a.validate_task(proposed_task, intent=after_intent, envelope=after_envelope,
                                        plan_sha=proposed_task["binding"]["plan_sha"], candidate_sha=proposed_task["binding"]["candidate_sha"])
        control_fields = [key for key in ("acceptance_ids", "protected_paths", "required_result")
                          if current_task[key] != proposed_task[key]]
        if current_task["binding"]["role"] != proposed_task["binding"]["role"]:
            control_fields.append("role")
    required = (["intent_owner"] if intent_fields else []) + (["execution_owner"] if envelope_fields else [])
    if control_fields:
        required.append("control_owner")
    classification = ("RECONCILE" if unresolved_effects else "MATERIAL_CHANGE" if required else "IN_SCOPE_STRUCTURAL")
    return {
        "classification": classification, "required_decisions": required,
        "intent_fields": intent_fields, "envelope_fields": envelope_fields, "control_fields": control_fields,
        "accepted_intent_sha": c.record_digest(before_intent), "accepted_envelope_sha": c.record_digest(before_envelope),
        "proposed_intent_sha": c.record_digest(after_intent), "proposed_envelope_sha": c.record_digest(after_envelope),
        "limitation": "Structural scope classification is not semantic intent acceptance, execution permission or an approved graph replan.",
    }
