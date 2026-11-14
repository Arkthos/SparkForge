"""TC-119/120: exact ingress assertions, cumulative scope and revocation without lost history."""

from copy import deepcopy
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from plugins.sparkforge.runtime import contracts as c
from plugins.sparkforge.runtime import policy as p
from plugins.sparkforge.runtime import store
from plugins.sparkforge.runtime import coordinator as co
from fakes.fake_host import FakeHost, Script
from runtime_fixtures import KINDS
from store_fixtures import accept_fixture_policy, artifact, command, create_job, fixture_ingress, local_task
from test_host_adapter import capability_fixture
from test_scheduler import KNOWN_USAGE, bound_result, schedule_fixture
from runtime_fixtures import attempt_fixture


ROOT = Path(__file__).resolve().parents[1]


class MaterialityPolicyTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="materiality policy ", dir=ROOT / "tests")
        self.addCleanup(temporary.cleanup)
        self.base = Path(temporary.name)
        self.workspace = self.base / "workspace"
        self.workspace.mkdir()
        self.root = self.base / "journal"
        self.metadata, self.intent, self.envelope = create_job(self.root, self.workspace, accept=False)
        self.task = local_task(self.envelope)

    def error(self, code, function, *args, **kwargs):
        with self.assertRaises(c.ContractError) as caught:
            function(*args, **kwargs)
        self.assertEqual(caught.exception.code, code)

    def accept(self):
        return accept_fixture_policy(self.root, self.intent, self.envelope)

    def task_state(self):
        return store.read(self.root)["entities"]["task:" + self.task["binding"]["task_id"]]["projection"]

    def ready(self):
        store.register(self.root, "register", "task", self.task, required_evidence=["behavior"])
        state = self.task_state()
        return store.apply(self.root, "task", command(state, "advance", target="ready"))["projection"]

    def request(self, kind, value, *, identifier=None, baseline_sha=None):
        identifier = identifier or "request-" + kind + "-" + str(value["revision"])
        request = p.decision_request(identifier, "fixture-job", kind, value, baseline_sha=baseline_sha,
                                     reason="Synthetic exact-scope decision request.",
                                     alternatives=["Reject or narrow scope."], impact=["Fictional local records only."])
        sha = store.append_record(self.root, identifier, "fixture-job",
                                  store.record_value("decision_request", identifier, 1, request))["record_sha"]
        return request, sha

    def decision(self, kind, request_sha, *, outcome="accept", key=None):
        key = key or "decision-" + request_sha[:24]
        response = {"id": key, "request_sha": request_sha, "outcome": outcome}
        return store.record_decision(self.root, key, request_sha, response, ingress=fixture_ingress(kind))

    def test_explicit_intent_and_execution_acceptance_required_before_new_admission(self):
        state = self.ready()
        before = store.read(self.root)
        self.error("POLICY_REQUIRED", store.apply, self.root, "task", command(state, "reserve", operation_id="op"))
        self.assertEqual(store.read(self.root), before)
        accepted = self.accept()
        authority = store.authority_status(store.read(self.root), task=self.task)
        self.assertTrue(authority["allowed"])
        self.assertFalse(authority["authenticated"])
        self.assertEqual(authority["binding_sha"], accepted["record_sha"])
        self.assertEqual(store.apply(self.root, "task", command(state, "reserve", operation_id="op"))["projection"]["status"], "reserved")

    def test_worker_labels_confidence_silence_and_wrong_owner_do_not_form_decisions(self):
        request, sha = self.request("intent", self.intent)
        response = {"id": "response", "request_sha": sha, "outcome": "accept"}
        for field in ("approved", "confidence", "actor", "authority"):
            self.error("INVALID_FIELDS", p.decide, request, dict(response, **{field: True}),
                       ingress=fixture_ingress("intent"), environment="LOCAL_DEVELOPMENT", at=p.now())
        self.error("INVALID_FIELDS", p.decide, request, None, ingress=fixture_ingress("intent"),
                   environment="LOCAL_DEVELOPMENT", at=p.now())
        worker = dict(fixture_ingress("intent"), source="worker")
        self.error("INVALID_ENUM", store.record_decision, self.root, "worker-response", sha, response, ingress=worker)
        self.error("WRONG_AUTHORITY", store.record_decision, self.root, "wrong-owner", sha, response,
                   ingress=fixture_ingress("envelope"))
        self.error("WRONG_AUTHORITY", p.decide, request, response, ingress=fixture_ingress("intent"),
                   environment="CORP", at=p.now())

    def test_decisions_bind_exact_request_target_and_rejected_outcomes_do_not_authorize(self):
        request, sha = self.request("intent", self.intent)
        changed = deepcopy(request)
        changed["impact"] = ["Changed impact."]
        self.error("STALE_DECISION", p.decide, changed, {"id": "stale", "request_sha": sha, "outcome": "accept"},
                   ingress=fixture_ingress("intent"), environment="LOCAL_DEVELOPMENT", at=p.now())
        rejected = self.decision("intent", sha, outcome="reject")["record_sha"]
        _, env_req = self.request("envelope", self.envelope)
        execution = self.decision("envelope", env_req)["record_sha"]
        self.error("DECISION_REQUIRED", store.bind_policy, self.root, "cannot-bind", intent_sha=c.record_digest(self.intent),
                   envelope_sha=c.record_digest(self.envelope), intent_decision_sha=rejected, envelope_decision_sha=execution)
        self.assertFalse(store.authority_status(store.read(self.root))["allowed"])

    def test_policy_actions_replay_stably_across_clock_changes(self):
        _, intent_req = self.request("intent", self.intent)
        response = {"id": "intent-response", "request_sha": intent_req, "outcome": "accept"}
        decision = store.record_decision(self.root, "intent-response", intent_req, response, ingress=fixture_ingress("intent"))
        _, envelope_req = self.request("envelope", self.envelope)
        env_decision = self.decision("envelope", envelope_req)["record_sha"]
        binding_args = {"intent_sha": c.record_digest(self.intent), "envelope_sha": c.record_digest(self.envelope),
                        "intent_decision_sha": decision["record_sha"], "envelope_decision_sha": env_decision}
        binding = store.bind_policy(self.root, "binding", **binding_args)
        revocation = store.revoke(self.root, "revoke", "decision", decision["record_sha"], reason="Synthetic withdrawal.",
                                 ingress=fixture_ingress("intent"))
        before = store.read(self.root)
        with patch.object(p, "now", return_value="2099-01-01T00:00:00Z"):
            self.assertTrue(store.record_decision(self.root, "intent-response", intent_req, response,
                                                 ingress=fixture_ingress("intent"))["replayed"])
            self.assertEqual(store.bind_policy(self.root, "binding", **binding_args)["record_sha"], binding["record_sha"])
            self.assertEqual(store.revoke(self.root, "revoke", "decision", decision["record_sha"], reason="Synthetic withdrawal.",
                                         ingress=fixture_ingress("intent"))["record_sha"], revocation["record_sha"])
        self.assertEqual(store.read(self.root), before)
        self.error("IDEMPOTENCY_CONFLICT", store.record_decision, self.root, "intent-response", intent_req,
                   dict(response, outcome="reject"), ingress=fixture_ingress("intent"))

    def test_ordinary_in_scope_repairs_refactors_tests_and_replans_need_no_new_decision(self):
        self.accept()
        store.register(self.root, "task", "task", self.task, required_evidence=["behavior"])
        before = store.read(self.root)
        for label in ("repair", "refactor", "supplemental tests", "technical replan"):
            changed = deepcopy(self.task)
            changed["objective"] = label + " while preserving declared behavior."
            changed["binding"]["plan_sha"] = c.record_digest(label)
            changed["allowance"]["max_tokens"] -= 1
            assessment = store.classify(self.root, proposed_intent=self.intent, proposed_envelope=self.envelope,
                                        current_task_sha=c.record_digest(self.task), proposed_task=changed, label=label)
            self.assertEqual(assessment["classification"], "IN_SCOPE_STRUCTURAL")
            self.assertEqual(assessment["required_decisions"], [])
        self.assertEqual(store.read(self.root), before)
        self.assertTrue(store.authority_status(before, task=self.task)["allowed"])

    def test_materiality_is_recomputed_against_accepted_scope_not_labels_or_previous_proposals(self):
        self.accept()
        first = deepcopy(self.intent)
        first["revision"] += 1
        first["outcome"] += " A changed outcome."
        second = deepcopy(first)
        second["revision"] += 1
        second["non_goals"] = []
        for proposed in (first, second):
            envelope = deepcopy(self.envelope)
            envelope["intent"]["sha256"] = c.record_digest(proposed)
            assessment = store.classify(self.root, proposed_intent=proposed, proposed_envelope=envelope, label="harmless repair")
            self.assertEqual(assessment["classification"], "MATERIAL_CHANGE")
            self.assertIn("intent_owner", assessment["required_decisions"])
            self.assertEqual(assessment["accepted_intent_sha"], c.record_digest(self.intent))
        self.assertIn("outcome", assessment["intent_fields"])
        self.assertIn("non_goals", assessment["intent_fields"])

    def test_provider_data_effect_and_resource_expansion_require_execution_owner(self):
        self.accept()
        for field, replacement in (
            ("tools", ["python", "new-tool"]), ("effects", ["workspace_read", "workspace_write", "check", "publish"]),
            ("profile", {"id": "new-profile", "revision": 1}),
            ("routes", {"host": {"id": "scripted-fake", "revision": 1}, "provider": {"id": "new-provider", "revision": 1}}),
            ("data_roots", [{"id": "new-data", "flavor": "posix", "path": "/synthetic/data"}]),
            ("environment", "ACRO"),
        ):
            changed = deepcopy(self.envelope)
            changed[field] = replacement
            assessment = store.classify(self.root, proposed_intent=self.intent, proposed_envelope=changed, label="in-scope")
            self.assertEqual(assessment["required_decisions"], ["execution_owner"])
            self.assertIn(field, assessment["envelope_fields"])
        changed = deepcopy(self.envelope)
        changed["bounds"]["job"]["max_model_calls"] += 1
        self.assertEqual(store.classify(self.root, proposed_intent=self.intent, proposed_envelope=changed)["classification"], "MATERIAL_CHANGE")

    def test_envelope_membership_rejects_tools_roots_routes_bounds_and_expiry(self):
        for key, value in (("tools", ["unlisted"]), ("workspace_id", "outside"), ("data_root_ids", ["unlisted"])):
            changed = deepcopy(self.task)
            changed[key] = value
            self.error("SCOPE_VIOLATION", p.envelope_membership, changed, intent=self.intent, envelope=self.envelope, at=p.now())
        changed = deepcopy(self.task)
        changed["routes"]["provider"]["id"] = "foreign"
        self.error("ENVIRONMENT_MISMATCH", p.envelope_membership, changed, intent=self.intent, envelope=self.envelope, at=p.now())
        changed = deepcopy(self.task)
        changed["allowance"]["max_tokens"] += 1
        self.error("INVALID_BOUND", p.envelope_membership, changed, intent=self.intent, envelope=self.envelope, at=p.now())
        self.error("TASK_EXPIRED", p.envelope_membership, self.task, intent=self.intent, envelope=self.envelope, at=self.task["deadline"])
        self.error("ENVELOPE_EXPIRED", p.envelope_membership, self.task, intent=self.intent, envelope=self.envelope, at=self.envelope["expires_at"])

    def test_expiry_and_backdated_worker_time_cannot_bypass_transaction_admission(self):
        self.accept()
        state = self.ready()
        with patch.object(p, "now", return_value=self.envelope["expires_at"]):
            self.error("ENVELOPE_EXPIRED", store.apply, self.root, "task", command(state, "reserve", operation_id="op"))
        request = store._input("backdated", "transition", "task", state["id"],
                               {"command": command(state, "reserve", key="backdated", operation_id="op"), "records": []})
        request["admitted_at"] = "2000-01-01T00:00:00Z"
        self.error("INVALID_TIME", store._execute, self.root, request)
        self.assertFalse(store.read(self.root)["reservations"])

    def test_protected_criteria_or_role_changes_are_not_ordinary_technical_replans(self):
        for field, replacement in (("acceptance_ids", ["A1"]), ("protected_paths", [])):
            changed = deepcopy(self.task)
            changed[field] = replacement
            result = p.classify_change(accepted_intent=self.intent, accepted_envelope=self.envelope,
                                       proposed_intent=self.intent, proposed_envelope=self.envelope,
                                       current_task=self.task, proposed_task=changed, label="refactor")
            self.assertEqual(result["classification"], "MATERIAL_CHANGE")
            self.assertIn("control_owner", result["required_decisions"])
        result = p.classify_change(accepted_intent=self.intent, accepted_envelope=self.envelope,
                                   proposed_intent=self.intent, proposed_envelope=self.envelope, unresolved_effects=True)
        self.assertEqual(result["classification"], "RECONCILE")

    def test_exact_envelope_reacceptance_preserves_intent_grant_and_stales_old_tasks(self):
        self.accept()
        self.ready()
        snapshot = store.read(self.root)
        previous_sha, previous = p.current_binding(snapshot["records"], "fixture-job")
        changed = deepcopy(self.envelope)
        changed["revision"] += 1
        changed["tools"].append("another-approved-fixture-tool")
        changed_sha = store.append_record(self.root, "new-envelope", "fixture-job",
                                          store.record_value("envelope", changed["id"], changed["revision"], changed))["record_sha"]
        _, request_sha = self.request("envelope", changed, baseline_sha=c.record_digest(self.envelope))
        decision_sha = self.decision("envelope", request_sha)["record_sha"]
        store.bind_policy(self.root, "accept-new-envelope", previous_sha=previous_sha, intent_sha=c.record_digest(self.intent),
                          envelope_sha=changed_sha, intent_decision_sha=previous["intent_decision_sha"], envelope_decision_sha=decision_sha)
        self.error("POLICY_BINDING_MISMATCH", store.apply, self.root, "task", command(self.task_state(), "reserve", operation_id="old"))
        current = store.read(self.root)
        accepted = p.current_binding(current["records"], "fixture-job")[1]
        self.assertEqual(accepted["intent_decision_sha"], previous["intent_decision_sha"])
        self.assertEqual(accepted["previous_sha"], previous_sha)
        self.assertTrue(store.authority_status(current)["allowed"])
        self.assertFalse(store.authority_status(current, task=self.task)["allowed"])

    def test_stale_decision_and_binding_cannot_replace_the_current_accepted_pair(self):
        self.accept()
        snapshot = store.read(self.root)
        previous_sha, binding = p.current_binding(snapshot["records"], "fixture-job")
        self.error("POLICY_BINDING_MISMATCH", store.bind_policy, self.root, "reset-policy",
                   intent_sha=binding["intent_sha"], envelope_sha=binding["envelope_sha"],
                   intent_decision_sha=binding["intent_decision_sha"], envelope_decision_sha=binding["envelope_decision_sha"])
        _, old_request = self.request("envelope", self.envelope, identifier="request-again", baseline_sha=binding["envelope_sha"])
        changed = deepcopy(self.envelope)
        changed["revision"] += 1
        changed["expires_at"] = "2030-01-02T00:00:00Z"
        changed_sha = store.append_record(self.root, "changed", "fixture-job",
                                          store.record_value("envelope", changed["id"], changed["revision"], changed))["record_sha"]
        _, request_sha = self.request("envelope", changed, baseline_sha=binding["envelope_sha"])
        decision = self.decision("envelope", request_sha)["record_sha"]
        store.bind_policy(self.root, "new-scope", previous_sha=previous_sha, intent_sha=binding["intent_sha"],
                          envelope_sha=changed_sha, intent_decision_sha=binding["intent_decision_sha"], envelope_decision_sha=decision)
        self.error("STALE_DECISION", self.decision, "envelope", old_request)

    def test_revocation_between_snapshot_and_dispatch_blocks_transaction_without_losing_reservation(self):
        self.accept()
        state = self.ready()
        state = store.apply(self.root, "task", command(state, "reserve", operation_id="op"))["projection"]
        store.revoke(self.root, "withdraw", "envelope", c.record_digest(self.envelope),
                     reason="Synthetic scope withdrawn.", ingress=fixture_ingress("envelope"))
        self.error("AUTHORITY_REVOKED", store.apply, self.root, "task", command(state, "dispatch", operation_id="op"))
        snapshot = store.read(self.root)
        self.assertEqual(snapshot["reservations"]["op"]["status"], "reserved")
        self.assertEqual(snapshot["reservations"]["op"]["allowance"], self.task["allowance"])
        self.assertFalse(store.authority_status(snapshot)["allowed"])

    def test_observations_and_reconciliation_survive_revocation_but_success_credit_does_not(self):
        self.accept()
        state = self.ready()
        state = store.apply(self.root, "task", command(state, "reserve", operation_id="op"))["projection"]
        store.apply(self.root, "task", command(state, "dispatch", operation_id="op"))
        caps = capability_fixture()
        caps_sha = store.append_record(self.root, "caps", "fixture-job",
                                      store.record_value("capabilities", "scripted-fake", 1, caps))["record_sha"]
        fake = FakeHost(caps, {"op": Script(("accepted", "completed"), KNOWN_USAGE)})
        fake.dispatch(self.task, "op")
        store.revoke(self.root, "withdraw", "envelope", c.record_digest(self.envelope),
                     reason="Scope withdrawn while effects might exist.", ingress=fixture_ingress("envelope"))
        observed = fake.reconcile(self.task, "op")
        store.apply(self.root, "task", command(self.task_state(), "reconcile", operation_id="op", resolution="completed",
                                               observation=observed["observation"], reason="Retain observed history."),
                    records=(store.record_value("observation", observed["observation"]["id"], 1, observed,
                                                context={"capabilities_sha": caps_sha}),))
        evidence = artifact()
        state = self.task_state()
        self.error("AUTHORITY_REVOKED", store.apply, self.root, "task", command(state, "evidence", evidence=[{
            "slot": "behavior", "receipt": {"id": evidence["value"]["id"], "sha256": evidence["value"]["sha256"]},
            "context_sha": state["context_sha"], "outcome": "pass",
        }]), records=(evidence,))
        self.assertEqual(store.read(self.root)["reservations"]["op"]["status"], "completed")
        self.assertEqual(fake.dispatch_count, 1)

    def test_coordinator_revocation_racing_result_submission_is_transactionally_rechecked(self):
        self.accept()
        schedule = schedule_fixture(self.intent, self.envelope)
        task = schedule["tasks"][0]
        from plugins.sparkforge.runtime.scheduler import operation_key
        result = bound_result(task)
        fake = FakeHost(capability_fixture(), {operation_key(task): Script(("accepted", "completed"), KNOWN_USAGE,
                                                                          c.record_digest(result))})
        coordinator = co.Coordinator(self.root, fake)
        coordinator.install(schedule)
        coordinator.tick()
        coordinator.tick()
        snapshot = store.read(self.root)
        receipt = snapshot["records"][snapshot["reservations"][operation_key(task)]["observation_sha"]]["value"]
        attempt = attempt_fixture(task)
        attempt.update(operation_key=operation_key(task), producer=receipt["producer"], observation=receipt["observation"],
                       observed_usage=receipt["usage"])
        original_apply = store.apply
        interleaved = False
        def revoke_before_certification(root, kind, cmd, **kwargs):
            nonlocal interleaved
            if not interleaved and cmd["action"] == "evidence":
                interleaved = True
                store.revoke(root, "race-revoke", "envelope", c.record_digest(self.envelope),
                             reason="Revoke after result preflight.", ingress=fixture_ingress("envelope"))
            return original_apply(root, kind, cmd, **kwargs)
        with patch.object(store, "apply", side_effect=revoke_before_certification):
            self.error("AUTHORITY_REVOKED", coordinator.submit_result, result, attempt)
        self.assertTrue(interleaved)
        self.assertEqual(coordinator.status()["status"], "POLICY_BLOCKED")
        self.assertFalse(self.task_state()["evidence"])
        self.assertEqual(fake.dispatch_count, 1)

    def test_clock_rollback_never_blocks_stop_or_non_authorizing_reconciliation(self):
        with patch.object(p, "now", return_value="2029-01-01T00:00:10Z"):
            self.accept()
            state = self.ready()
            state = store.apply(self.root, "task", command(state, "reserve", operation_id="op"))["projection"]
            store.apply(self.root, "task", command(state, "dispatch", operation_id="op"))
            caps = capability_fixture()
            caps_sha = store.append_record(self.root, "caps", "fixture-job",
                                          store.record_value("capabilities", "scripted-fake", 1, caps))["record_sha"]
            fake = FakeHost(caps, {"op": Script(("accepted", "completed"), KNOWN_USAGE)})
            fake.dispatch(self.task, "op")
            store.revoke(self.root, "withdraw", "envelope", c.record_digest(self.envelope),
                         reason="Retain withdrawal despite clock drift.", ingress=fixture_ingress("envelope"))
            with patch.object(p, "now", return_value="2029-01-01T00:00:09Z"):
                job = store.read(self.root)["entities"]["job:fixture-job"]["projection"]
                store.apply(self.root, "job", command(job, "cancel", reason="Stop even with a corrected wall clock."))
                observed = fake.reconcile(self.task, "op")
                store.apply(self.root, "task", command(self.task_state(), "reconcile", operation_id="op", resolution="completed",
                                                       observation=observed["observation"], reason="Factual late completion."),
                            records=(store.record_value("observation", observed["observation"]["id"], 1, observed,
                                                        context={"capabilities_sha": caps_sha}),))
                snapshot = store.read(self.root)
                self.assertTrue(snapshot["entities"]["job:fixture-job"]["projection"]["stop_requested"])
                self.assertEqual(snapshot["reservations"]["op"]["status"], "completed")
                self.error("ADMISSION_CLOCK_REVERSED", store.apply, self.root, "task",
                           command(self.task_state(), "advance", target="completed"))
                self.assertEqual(fake.dispatch_count, 1)

    def test_accepting_an_envelope_does_not_move_the_immutable_store_workspace(self):
        self.accept()
        snapshot = store.read(self.root)
        previous_sha, binding = p.current_binding(snapshot["records"], "fixture-job")
        changed = deepcopy(self.envelope)
        changed["revision"] += 1
        changed["workspace_roots"][0]["path"] = str(self.base / "other-workspace")
        sha = store.append_record(self.root, "different-workspace", "fixture-job",
                                  store.record_value("envelope", changed["id"], changed["revision"], changed))["record_sha"]
        _, request_sha = self.request("envelope", changed, baseline_sha=binding["envelope_sha"])
        decision_sha = self.decision("envelope", request_sha)["record_sha"]
        self.error("SCOPE_VIOLATION", store.bind_policy, self.root, "move-workspace", previous_sha=previous_sha,
                   intent_sha=binding["intent_sha"], envelope_sha=sha,
                   intent_decision_sha=binding["intent_decision_sha"], envelope_decision_sha=decision_sha)
        self.assertEqual(p.current_binding(store.read(self.root)["records"], "fixture-job")[0], previous_sha)


if __name__ == "__main__":
    unittest.main()
