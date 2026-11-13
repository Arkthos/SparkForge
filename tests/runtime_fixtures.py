"""Fictional records only; no platform access, credentials or permission receipts."""

from plugins.sparkforge.runtime import contracts
from plugins.sparkforge.runtime import agent_contracts as agents


KINDS = ("synthetic-component", "synthetic-agent")


def intent_fixture() -> contracts.IntentBaseline:
    return {
        "schema_version": contracts.INTENT_VERSION,
        "id": "fixture-intent",
        "revision": 1,
        "problem": "A fictional component must validate a requested greeting.",
        "outcome": "Return a greeting only for a nonblank name.",
        "audience": "Synthetic evaluator",
        "component_kind": "synthetic-component",
        "acceptance": [
            {"id": "A1", "behavior": "A nonblank name returns its greeting."},
            {"id": "A2", "behavior": "A blank name raises a validation error."},
        ],
        "non_goals": ["No external service or deployment."],
        "material_constraints": ["Preserve the caller's name without silent truncation."],
        "source_assumptions": [{
            "id": "platform",
            "status": "unknown",
            "statement": "Only a fictional component interface is available.",
            "reason": "Real platform source comparison is NOT_ASSESSED.",
            "references": [{"id": "fictional-profile", "revision": None, "sha256": None}],
        }],
    }


def envelope_fixture(intent: contracts.IntentBaseline | None = None) -> contracts.ExecutionEnvelope:
    baseline = intent if intent is not None else intent_fixture()
    return {
        "schema_version": contracts.ENVELOPE_VERSION,
        "id": "fixture-envelope",
        "revision": 1,
        "intent": {"id": baseline["id"], "sha256": contracts.record_digest(baseline)},
        "environment": "LOCAL_DEVELOPMENT",
        "profile": {"id": "fictional-profile", "revision": 1},
        "workspace_roots": [{"id": "workspace", "flavor": "windows", "path": r"C:\fictional\workspace"}],
        "data_roots": [{"id": "sources", "flavor": "posix", "path": "/fictional/sources"}],
        "tools": ["python"],
        "effects": ["workspace_read", "workspace_write", "check"],
        "routes": {"host": {"id": "scripted-fake", "revision": 1},
                   "provider": {"id": "no-model", "revision": 1}},
        "bounds": {
            "job": {"wall_seconds": 600, "max_agent_attempts": 6, "max_model_calls": 8,
                    "max_check_runs": 10, "max_replans": 2, "max_tokens": 10000},
            "agent": {"timeout_seconds": 120, "max_attempts": 2, "max_model_calls": 2, "max_tokens": 2000},
            "check": {"timeout_seconds": 30, "max_attempts": 3, "output_limit_bytes": 4096},
        },
        "unknown_usage": "stop",
        "expires_at": "2030-01-01T00:00:00Z",
        "revocation": {"revoked_at": None, "reason": None},
    }


PLAN_SHA = contracts.record_digest({"fixture": "technical plan, not an admitted plan"})
CANDIDATE_SHA = contracts.record_digest({"fixture": "original candidate, no real workspace"})


def task_fixture(role: str = "coder") -> agents.TaskAssignment:
    intent, envelope = intent_fixture(), envelope_fixture()
    inputs = [{"id": "behavior-contract", "sha256": contracts.record_digest(intent)}]
    writes = {"coder": ["src/component.py"], "test_author": ["tests/test_component.py"], "delivery": ["docs/guide.md"]}
    return {
        "schema_version": "sparkforge.task.v1",
        "binding": {
            "job_id": "fixture-job", "task_id": "fixture-" + role, "attempt_id": "fixture-attempt-" + role, "role": role,
            "intent_sha": contracts.record_digest(intent), "envelope_sha": contracts.record_digest(envelope),
            "plan_sha": PLAN_SHA, "candidate_sha": CANDIDATE_SHA, "inputs_sha": contracts.record_digest(inputs),
        },
        "environment": envelope["environment"], "profile": dict(envelope["profile"]),
        "routes": {"host": dict(envelope["routes"]["host"]), "provider": dict(envelope["routes"]["provider"])},
        "workspace_id": "workspace", "data_root_ids": ["sources"],
        "objective": "Satisfy the two fictional greeting criteria within the assigned role.",
        "acceptance_ids": ["A1", "A2"], "inputs": inputs,
        "allowed_writes": writes.get(role, []), "protected_paths": ["evaluation", "control"],
        "dependencies": [], "tools": ["python"],
        "effects": ["workspace_read", "workspace_write"] if role in writes else ["workspace_read"],
        "deadline": "2029-12-01T00:00:00Z", "allowance": dict(envelope["bounds"]["agent"]),
        "required_result": agents.RESULT_KINDS[role],
        "stop_conditions": ["Stop for stale bindings, undeclared effects or exhausted allowance."],
    }


def producer_fixture(role: str = "coder") -> agents.Producer:
    return {"host": {"id": "scripted-fake", "revision": 1}, "role": role,
            "session_id": "fixture-session-" + role, "context_id": "fixture-context-" + role}


def unknown_usage() -> agents.Usage:
    return {"status": "unknown", "model_calls": None, "tokens": None, "wall_seconds": None,
            "reason": "No actual model operation in this fixture."}


def attempt_fixture(task: agents.TaskAssignment) -> agents.AgentAttempt:
    return {
        "schema_version": "sparkforge.attempt.v1", "binding": dict(task["binding"]),
        "task_sha": contracts.record_digest(task), "operation_key": "fixture-operation", "ordinal": 1,
        "producer": producer_fixture(task["binding"]["role"]), "status": "completed",
        "started_at": "2029-11-01T00:00:00Z", "finished_at": "2029-11-01T00:00:01Z",
        "observed_usage": unknown_usage(),
        "observation": {"id": "fake-observation", "sha256": contracts.record_digest({"fixture": "scripted receipt"})},
    }


def result_fixture(task: agents.TaskAssignment) -> agents.AgentResult:
    return {
        "schema_version": "sparkforge.agent-result.v1", "id": "fixture-result",
        "binding": dict(task["binding"]), "task_sha": contracts.record_digest(task),
        "producer": producer_fixture(task["binding"]["role"]), "result_kind": task["required_result"],
        "outcome": "completed", "summary": "Synthetic worker claim, not admitted evidence.",
        "artifacts": [{"id": "role-output", "sha256": contracts.record_digest({"fixture": "role artifact"})}],
        "changed_paths": task["allowed_writes"][:],
        "output_candidate_sha": contracts.record_digest({"fixture": "proposed candidate"}) if task["allowed_writes"] else None,
        "evidence": [dict(ref) for ref in task["inputs"]], "findings": [], "failures": [],
        "usage_claim": unknown_usage(), "uncertainty": ["Live execution remains NOT_ASSESSED."], "next_action": "complete",
    }


def finding_fixture() -> agents.Finding:
    return {
        "schema_version": "sparkforge.finding.v1", "id": "finding-blank", "severity": "error",
        "category": "implementation", "message": "A blank name was not rejected.",
        "path": "src/component.py", "acceptance_ids": ["A2"],
        "evidence": [{"id": "behavior-contract", "sha256": contracts.record_digest(intent_fixture())}],
        "recommendation": "Restore the declared input validation.",
    }


def failure_fixture() -> agents.Failure:
    return {
        "schema_version": "sparkforge.failure.v1", "id": "failure-blank", "kind": "implementation",
        "message": "The declared blank-name criterion failed.",
        "evidence": [{"id": "behavior-contract", "sha256": contracts.record_digest(intent_fixture())}],
        "uncertainty": [], "suggested_action": "repair",
    }
