"""Owned local synthetic journal fixtures, shared with serial coordinator tests."""

import os
from pathlib import Path

from plugins.sparkforge.runtime import contracts as c
from plugins.sparkforge.runtime import migrations as m
from plugins.sparkforge.runtime import policy as p
from plugins.sparkforge.runtime import store
from runtime_fixtures import KINDS, envelope_fixture, intent_fixture, task_fixture


def fixture_ingress(kind: str) -> dict:
    return {"source": "synthetic_fixture", "actor_id": "fixture-" + p.AUTHORITY[kind], "authority": p.AUTHORITY[kind],
            "receipt": {"id": "fixture-origin-" + kind, "sha256": c.record_digest({"fixture": kind + " owner assertion"})}}


def accept_fixture_policy(root: Path, intent: dict, envelope: dict) -> dict:
    decisions = {}
    for kind, value in (("intent", intent), ("envelope", envelope)):
        request = p.decision_request("fixture-request-" + kind, "fixture-job", kind, value, baseline_sha=None,
                                     reason="Explicit synthetic fixture scope, not real operator approval.",
                                     alternatives=["Reject this fictional fixture."], impact=["No live sources, host or model."])
        request_sha = store.append_record(root, "request-" + kind, "fixture-job",
                                         store.record_value("decision_request", request["id"], 1, request))["record_sha"]
        response = {"id": "fixture-decision-" + kind, "request_sha": request_sha, "outcome": "accept"}
        decisions[kind] = store.record_decision(root, "decision-" + kind, request_sha, response,
                                                ingress=fixture_ingress(kind))["record_sha"]
    return store.bind_policy(root, "bind-fixture-policy", intent_sha=c.record_digest(intent), envelope_sha=c.record_digest(envelope),
                              intent_decision_sha=decisions["intent"], envelope_decision_sha=decisions["envelope"])


def create_job(root: Path, workspace: Path, *, accept: bool = True) -> tuple[dict, dict, dict]:
    metadata = m.create_store(root, workspace=workspace, environment="LOCAL_DEVELOPMENT")
    intent, envelope = intent_fixture(), envelope_fixture()
    envelope["workspace_roots"] = [{"id": "workspace", "flavor": "windows" if os.name == "nt" else "posix", "path": str(workspace)}]
    envelope["data_roots"] = []
    store.initialize(root, "initialize", "fixture-job", intent=intent, envelope=envelope, supported_component_kinds=KINDS,
                     context_sha=c.record_digest({"intent": c.record_digest(intent), "envelope": c.record_digest(envelope)}),
                     required_evidence=["review", "controller"])
    if accept:
        accept_fixture_policy(root, intent, envelope)
    return metadata, intent, envelope


def local_task(envelope: dict, role: str = "coder", *, suffix: str = "") -> dict:
    task = task_fixture(role)
    task["binding"]["envelope_sha"] = c.record_digest(envelope)
    task["binding"]["task_id"] += suffix
    task["binding"]["attempt_id"] += suffix
    task["data_root_ids"] = []
    return task


def projection(root: Path, task: dict) -> dict:
    return store.read(root)["entities"]["task:" + task["binding"]["task_id"]]["projection"]


def command(state: dict, action: str, *, key: str | None = None, **fields) -> dict:
    return {
        "schema_version": "sparkforge.command.v1", "key": key or f"{state['id']}-{state['revision']}",
        "entity_id": state["id"], "expected_revision": state["revision"], "context_sha": state["context_sha"],
        "action": action, "target": None, "operation_id": None, "resolution": None, "observation": None,
        "evidence": [], "new_context_sha": None, "reason": None, **fields,
    }


def artifact(identifier: str = "behavior-receipt", *, text: str = "synthetic observed behavior") -> dict:
    return store.record_value("artifact", identifier, 1, {
        "schema_version": "sparkforge.artifact-reference.v1", "id": identifier, "artifact_kind": "evidence",
        "sha256": c.record_digest(text), "assessment": "unassessed",
    })
