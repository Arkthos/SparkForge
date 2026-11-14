"""TC-111/112: scripted host behavior is observable, bounded and never live acceptance."""

from copy import deepcopy
from pathlib import Path
import socket
import subprocess
import unittest
from unittest.mock import patch

from plugins.sparkforge.runtime import agent_contracts as a
from plugins.sparkforge.runtime import contracts as c
from plugins.sparkforge.runtime import host as h
from fakes.fake_host import FakeHost, Script
from runtime_fixtures import task_fixture


def capability_fixture():
    return {
        "schema_version": "sparkforge.host-capabilities.v1",
        "host": {"id": "scripted-fake", "revision": 1}, "build": "deterministic-fixture-v1",
        "environment": "LOCAL_DEVELOPMENT", "profile": {"id": "fictional-profile", "revision": 1},
        "provider": {"id": "no-model", "revision": 1}, "evidence_class": "scripted_fake",
        "support": {name: "supported" for name in h.CAPABILITIES}, "roles": list(a.RESULT_KINDS),
        "tools": ["python"], "effects": ["workspace_read", "workspace_write", "check"],
    }


class HostAdapterTests(unittest.TestCase):
    def error(self, code, function, *args, **kwargs):
        with self.assertRaises(c.ContractError) as caught:
            function(*args, **kwargs)
        self.assertEqual(caught.exception.code, code)

    def fake(self, script=Script(), capabilities=None):
        return FakeHost(capability_fixture() if capabilities is None else capabilities, {"op-1": script})

    def test_every_role_has_bound_observations_without_claiming_result_acceptance(self):
        for role in a.RESULT_KINDS:
            with self.subTest(role=role):
                task, fake = task_fixture(role), self.fake()
                host = fake.discover()
                accepted = fake.dispatch(task, "op-1")
                self.assertEqual(accepted["status"], "accepted")
                self.assertEqual(accepted["effect_state"], "possible")
                self.assertIsNone(accepted["result_sha"])
                self.assertEqual(fake.poll(task, "op-1")["status"], "running")
                completed = fake.poll(task, "op-1")
                self.assertEqual(completed["status"], "completed")
                self.assertEqual(completed["evidence_class"], "scripted_fake")
                self.assertEqual(completed["producer"]["role"], role)
                self.assertEqual(completed["usage"]["status"], "unknown")
                self.assertEqual(fake.dispatch_count, 1)
                self.assertNotIn("approved", completed)
                self.assertNotIn("admitted", completed)
                completed["binding"]["role"] = "changed"
                host["support"]["poll"] = "unsupported"
                self.assertEqual(fake.poll(task, "op-1")["binding"]["role"], role)
                self.assertEqual(fake.discover()["support"]["poll"], "supported")

    def test_required_unsupported_or_unknown_capability_refuses_before_dispatch(self):
        for name in h.CAPABILITIES:
            for support in ("unsupported", "unknown"):
                capabilities = capability_fixture()
                capabilities["support"][name] = support
                fake = self.fake(capabilities=capabilities)
                self.error("HOST_UNSUPPORTED", fake.dispatch, task_fixture(), "op-1", required=(name,))
                self.assertEqual(fake.dispatch_count, 0)
        fake = self.fake()
        self.error("INVALID_CAPABILITIES", fake.dispatch, task_fixture(), "op-1", required=())
        self.assertEqual(fake.dispatch_count, 0)

    def test_unsupported_role_tools_effects_and_wrong_routes_have_no_effects(self):
        for field in ("roles", "tools", "effects"):
            capabilities = capability_fixture()
            capabilities[field] = []
            fake = self.fake(capabilities=capabilities)
            self.error("HOST_UNSUPPORTED", fake.dispatch, task_fixture(), "op-1")
            self.assertEqual(fake.dispatch_count, 0)
        for field, value in (("environment", "CORP"), ("profile", {"id": "foreign", "revision": 1}),
                             ("provider", {"id": "foreign", "revision": 1}), ("host", {"id": "foreign", "revision": 1})):
            capabilities = capability_fixture()
            capabilities[field] = value
            fake = self.fake(capabilities=capabilities)
            self.error("HOST_CONTEXT_MISMATCH", fake.dispatch, task_fixture(), "op-1")
            self.assertEqual(fake.dispatch_count, 0)

    def test_lost_dispatch_response_is_reconciled_without_replay(self):
        fake, task = self.fake(Script(("accepted", "unknown", "completed"), lose_dispatch_response=True)), task_fixture()
        self.error("HOST_RESPONSE_LOST", fake.dispatch, task, "op-1")
        self.assertEqual(fake.dispatch_count, 1)
        self.error("HOST_RECONCILIATION_REQUIRED", fake.dispatch, task, "op-1")
        self.assertEqual(fake.reconcile(task, "op-1")["status"], "unknown")
        self.assertEqual(fake.reconcile(task, "op-1")["status"], "completed")
        self.assertEqual(fake.dispatch_count, 1)
        changed = deepcopy(task)
        changed["objective"] = "Different task."
        self.error("HOST_OPERATION_CONFLICT", fake.dispatch, changed, "op-1")
        self.error("HOST_OPERATION_CONFLICT", fake.poll, changed, "op-1")

    def test_deterministic_pre_effect_failure_and_unknown_operation(self):
        fake = self.fake(Script(reject_before_dispatch=True))
        self.error("HOST_DISPATCH_REJECTED", fake.dispatch, task_fixture(), "op-1")
        self.assertEqual(fake.dispatch_count, 0)
        self.error("HOST_OPERATION_UNKNOWN", fake.reconcile, task_fixture(), "op-1")
        self.error("UNSCRIPTED_OPERATION", fake.dispatch, task_fixture(), "other-key")
        self.assertEqual(fake.dispatch_count, 0)

    def test_cancel_ack_is_not_observed_stop_or_no_effect(self):
        task, fake = task_fixture(), self.fake(Script(("accepted", "running", "stopped")))
        fake.dispatch(task, "op-1")
        receipt = fake.cancel(task, "op-1")
        self.assertEqual(receipt["status"], "cancel_requested")
        self.assertFalse(receipt["stop_observed"])
        self.assertEqual(receipt["effect_state"], "possible")
        fake.cancel(task, "op-1")
        self.assertEqual(fake.cancel_count, 1)
        self.assertEqual(fake.poll(task, "op-1")["status"], "running")
        self.assertTrue(fake.reconcile(task, "op-1")["stop_observed"])
        forged = deepcopy(receipt)
        forged.update(status="stopped", effect_state="settled")
        self.error("UNOBSERVED_CANCELLATION", h.validate_receipt, forged, capabilities=fake.discover(), task=task, operation_key="op-1")
        forged = deepcopy(receipt)
        forged["effect_state"] = "not_started"
        self.error("UNRESOLVED_EFFECTS", h.validate_receipt, forged, capabilities=fake.discover(), task=task, operation_key="op-1")

    def test_cancel_can_be_followed_by_late_completion_not_forced_stopped(self):
        task, fake = task_fixture(), self.fake(Script(("accepted", "completed")))
        fake.dispatch(task, "op-1")
        fake.cancel(task, "op-1")
        receipt = fake.reconcile(task, "op-1")
        self.assertEqual(receipt["status"], "completed")
        self.assertTrue(receipt["cancel_acknowledged"])
        self.assertFalse(receipt["stop_observed"])
        self.assertEqual(fake.cancel(task, "op-1"), receipt)

    def test_unsupported_cancel_or_poll_does_not_change_operation(self):
        capabilities = capability_fixture()
        capabilities["support"]["cancel"] = "unsupported"
        capabilities["support"]["poll"] = "unknown"
        fake, task = self.fake(capabilities=capabilities), task_fixture()
        fake.dispatch(task, "op-1", required=("dispatch", "reconcile"))
        self.error("HOST_UNSUPPORTED", fake.cancel, task, "op-1")
        self.error("HOST_UNSUPPORTED", fake.poll, task, "op-1")
        self.assertEqual(fake.cancel_count, 0)
        self.assertEqual(fake.reconcile(task, "op-1")["status"], "running")

    def test_foreign_environment_receipt_role_and_task_are_rejected(self):
        task, fake = task_fixture(), self.fake()
        receipt = fake.dispatch(task, "op-1")
        for key, value, code in (
            ("environment", "ACRO", "HOST_CONTEXT_MISMATCH"),
            ("provider", {"id": "other", "revision": 1}, "HOST_CONTEXT_MISMATCH"),
            ("evidence_class", "host_observed", "HOST_CONTEXT_MISMATCH"),
            ("operation_key", "other", "BINDING_MISMATCH"), ("task_sha", "f" * 64, "BINDING_MISMATCH"),
        ):
            changed = deepcopy(receipt)
            changed[key] = value
            self.error(code, h.validate_receipt, changed, capabilities=fake.discover(), task=task, operation_key="op-1")
        receipt["producer"]["role"] = "reviewer"
        self.error("PRODUCER_MISMATCH", h.validate_receipt, receipt, capabilities=fake.discover(), task=task, operation_key="op-1")

    def test_unavailable_usage_stays_unknown_never_assumed_zero(self):
        capabilities = capability_fixture()
        capabilities["support"]["usage"] = "unsupported"
        task, fake = task_fixture(), self.fake(capabilities=capabilities)
        receipt = fake.dispatch(task, "op-1")
        self.assertIsNone(receipt["usage"]["tokens"])
        receipt["usage"] = {"status": "known", "model_calls": 0, "tokens": 0, "wall_seconds": 0, "reason": None}
        self.error("UNSUPPORTED_OBSERVATION", h.validate_receipt, receipt, capabilities=capabilities, task=task, operation_key="op-1")
        receipt["usage"]["status"] = "unknown"
        self.error("INVALID_USAGE", h.validate_receipt, receipt, capabilities=capabilities, task=task, operation_key="op-1")

    def test_receipt_context_revisions_reject_booleans_and_floats(self):
        task, fake = task_fixture(), self.fake()
        receipt = fake.dispatch(task, "op-1")
        for field in ("host", "profile", "provider"):
            for revision in (True, 1.0):
                with self.subTest(field=field, revision=revision):
                    changed = deepcopy(receipt)
                    changed[field]["revision"] = revision
                    self.error("INVALID_BOUND", h.validate_receipt, c.parse_json(c.canonical_json(changed)),
                               capabilities=fake.discover(), task=task, operation_key="op-1")

    def test_scripted_usage_cannot_create_effects_before_unsupported_refusal(self):
        capabilities = capability_fixture()
        capabilities["support"]["usage"] = "unsupported"
        script = Script(usage={"status": "known", "model_calls": 0, "tokens": 0, "wall_seconds": 0, "reason": None})
        fake = self.fake(script, capabilities=capabilities)
        with self.assertRaises(c.ContractError):
            fake.dispatch(task_fixture(), "op-1")
        self.assertEqual(fake.dispatch_count, 0)

    def test_known_usage_and_other_terminal_observations_remain_distinct(self):
        usage = {"status": "known", "model_calls": 2, "tokens": 100, "wall_seconds": 4, "reason": None}
        task, fake = task_fixture(), self.fake(Script(("accepted", "failed"), usage=usage))
        fake.dispatch(task, "op-1")
        receipt = fake.poll(task, "op-1")
        self.assertEqual(receipt["status"], "failed")
        self.assertEqual(receipt["usage"], usage)
        fake = self.fake(Script(("unknown", "not_started")))
        fake.dispatch(task, "op-1")
        receipt = fake.reconcile(task, "op-1")
        self.assertEqual(receipt["effect_state"], "not_started")
        self.assertIsNone(receipt["producer"])

    def test_fake_has_no_process_file_network_or_live_identity_effects(self):
        with (patch("builtins.open", side_effect=AssertionError("file I/O")),
              patch.object(Path, "open", side_effect=AssertionError("path I/O")),
              patch.object(subprocess, "Popen", side_effect=AssertionError("process")),
              patch.object(socket, "socket", side_effect=AssertionError("network"))):
            task, fake = task_fixture(), self.fake()
            fake.discover()
            fake.dispatch(task, "op-1")
            fake.cancel(task, "op-1")
            fake.poll(task, "op-1")
            fake.reconcile(task, "op-1")
            self.assertEqual(fake.calls, {"discover": 1, "dispatch": 1, "poll": 1, "cancel": 1, "reconcile": 1})
        capabilities = capability_fixture()
        capabilities["evidence_class"] = "host_observed"
        self.error("INVALID_FAKE", self.fake, capabilities=capabilities)


if __name__ == "__main__":
    unittest.main()
