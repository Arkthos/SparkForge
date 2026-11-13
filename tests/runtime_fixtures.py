"""Fictional records only; no platform access, credentials or permission receipts."""

from plugins.sparkforge.runtime import contracts


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
