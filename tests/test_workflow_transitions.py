"""TC-107/108: no I/O, duplicate effect, stale completion or lost cancellation."""

from copy import deepcopy
import unittest

from plugins.sparkforge.runtime import contracts as c
from plugins.sparkforge.runtime import transitions as t


CONTEXT = c.record_digest({"fixture": "intent/envelope/plan/candidate/inputs/evidence-sequence"})
OBSERVATION = {"id": "fixture-observation", "sha256": c.record_digest({"fixture": "observed operation"})}


def command_fixture(state, action, **fields):
    return {
        "schema_version": "sparkforge.command.v1", "key": f"command-{state['revision']}",
        "entity_id": state["id"], "expected_revision": state["revision"], "context_sha": state["context_sha"],
        "action": action, "target": None, "operation_id": None, "resolution": None, "observation": None,
        "evidence": [], "new_context_sha": None, "reason": None, **fields,
    }


def receipt(state, slot, outcome="pass"):
    return {"slot": slot, "receipt": {"id": slot + "-receipt", "sha256": c.record_digest({"slot": slot, "outcome": outcome})},
            "context_sha": state["context_sha"], "outcome": outcome}


class WorkflowTransitionTests(unittest.TestCase):
    def initial(self, kind="task"):
        return t.initial_projection(kind, "fixture-" + kind, CONTEXT, ["behavior", "review", "controller"])

    def apply(self, state, action, **fields):
        return t.apply_command(state, command_fixture(state, action, **fields))["projection"]

    def error(self, code, state, action, **fields):
        with self.assertRaises(c.ContractError) as caught:
            self.apply(state, action, **fields)
        self.assertEqual(caught.exception.code, code)

    def running(self, kind="task"):
        state = self.initial(kind)
        if kind == "job":
            state = self.apply(state, "advance", target="planning")
        if kind != "attempt":
            state = self.apply(state, "advance", target="ready")
        state = self.apply(state, "reserve", operation_id="operation-1")
        return self.apply(state, "dispatch", operation_id="operation-1")

    def observed(self, kind="task"):
        state = self.running(kind)
        return self.apply(state, "result", operation_id="operation-1", resolution="completed",
                          observation=OBSERVATION, reason="Synthetic host operation finished.")

    def evidenced(self, kind="task"):
        state = self.observed(kind)
        return self.apply(state, "evidence", evidence=[receipt(state, slot) for slot in state["required_evidence"]])

    def test_task_attempt_and_job_complete_only_with_expected_current_inventory(self):
        for kind in ("task", "attempt", "job"):
            with self.subTest(kind=kind):
                state = self.evidenced(kind)
                if kind == "job":
                    state = self.apply(state, "advance", target="checking")
                    state = self.apply(state, "advance", target="reviewing")
                    state = self.apply(state, "advance", target="verified")
                    state = self.apply(state, "advance", target="delivered")
                    self.assertEqual(state["status"], "delivered")
                else:
                    state = self.apply(state, "advance", target="completed")
                    self.assertEqual(state["status"], "completed")
                self.assertEqual(state["operations"][0]["status"], "completed")

    def test_replay_is_noop_even_after_later_cancellation(self):
        state = self.apply(self.initial(), "advance", target="ready")
        command = command_fixture(state, "reserve", operation_id="operation-1")
        original = deepcopy(state)
        first = t.apply_command(state, command)
        self.assertEqual(state, original)
        replay = t.apply_command(first["projection"], command, previous_event=first["event"])
        self.assertTrue(replay["replayed"])
        self.assertEqual(replay["projection"], first["projection"])
        self.assertEqual(len(replay["projection"]["operations"]), 1)
        cancelled = self.apply(first["projection"], "cancel", reason="Synthetic cancellation.")
        replay = t.apply_command(cancelled, command, previous_event=first["event"])
        self.assertEqual(replay["projection"], cancelled)
        self.assertTrue(replay["projection"]["stop_requested"])
        self.assertEqual(replay["event"]["id"], first["event"]["id"])

    def test_conflicting_replay_and_reused_operation_do_not_dispatch_twice(self):
        state = self.apply(self.initial(), "advance", target="ready")
        command = command_fixture(state, "reserve", operation_id="operation-1")
        first = t.apply_command(state, command)
        command["operation_id"] = "different-operation"
        with self.assertRaises(c.ContractError) as caught:
            t.apply_command(first["projection"], command, previous_event=first["event"])
        self.assertEqual(caught.exception.code, "IDEMPOTENCY_CONFLICT")
        state = self.observed()
        state = self.apply(state, "advance", target="failed", reason="Synthetic failed criterion.")
        state = self.apply(state, "advance", target="ready")
        self.error("OPERATION_CONFLICT", state, "reserve", operation_id="operation-1")

    def test_expected_revision_context_entity_and_tampered_event_fail(self):
        state = self.initial()
        self.error("REVISION_CONFLICT", state, "advance", target="ready", expected_revision=2)
        self.error("STALE_CONTEXT", state, "advance", target="ready", context_sha="f" * 64)
        self.error("ENTITY_MISMATCH", state, "advance", target="ready", entity_id="other")
        command = command_fixture(state, "advance", target="ready")
        result = t.apply_command(state, command)
        prior = deepcopy(result["event"])
        prior["after"]["required_evidence"] = ["behavior"]
        with self.assertRaises(c.ContractError) as caught:
            t.apply_command(result["projection"], command, previous_event=prior)
        self.assertEqual(caught.exception.code, "INVALID_EVENT")
        with self.assertRaises(c.ContractError) as caught:
            t.apply_command(state, command, previous_event=result["event"])
        self.assertEqual(caught.exception.code, "REPLAY_STATE_MISMATCH")

    def test_impossible_progress_and_result_before_dispatch_fail_without_mutation(self):
        state = self.initial()
        self.error("INVALID_TRANSITION", state, "advance", target="completed")
        state = self.apply(state, "advance", target="ready")
        self.error("INVALID_TRANSITION", state, "advance", target="running")
        state = self.apply(state, "reserve", operation_id="operation-1")
        original = deepcopy(state)
        self.error("RESULT_BEFORE_DISPATCH", state, "result", operation_id="operation-1",
                   resolution="completed", observation=OBSERVATION, reason="Unobserved claim.")
        self.assertEqual(state, original)

    def test_unresolved_operations_block_completion_even_with_passing_receipts(self):
        state = self.running()
        state = self.apply(state, "evidence", evidence=[receipt(state, slot) for slot in state["required_evidence"]])
        self.error("UNRESOLVED_OPERATIONS", state, "advance", target="completed")
        self.error("DISPATCH_BLOCKED", state, "reserve", operation_id="second")
        self.error("DISPATCH_BLOCKED", state, "dispatch", operation_id="operation-1")

    def test_missing_failed_skipped_and_unknown_evidence_never_passes(self):
        for outcome in (None, "fail", "skipped", "unknown"):
            state = self.observed()
            evidence = [receipt(state, slot) for slot in ("behavior", "review")]
            if outcome:
                evidence.append(receipt(state, "controller", outcome))
            state = self.apply(state, "evidence", evidence=evidence)
            self.error("INCOMPLETE_EVIDENCE", state, "advance", target="completed")
        state = self.observed()
        self.error("UNEXPECTED_EVIDENCE", state, "evidence", evidence=[receipt(state, "self-approved")])

    def test_candidate_or_evidence_context_invalidation_keeps_old_receipts_stale(self):
        state = self.evidenced()
        old = deepcopy(state)
        new_context = c.record_digest({"fixture": "same bytes, new check/evidence sequence"})
        state = self.apply(state, "invalidate", new_context_sha=new_context, reason="Synthetic check rerun.")
        self.assertEqual(state["evidence"], old["evidence"])
        self.assertEqual(state["required_evidence"], old["required_evidence"])
        self.error("STALE_CONTEXT", state, "evidence", evidence=old["evidence"])
        state = self.apply(state, "reserve", operation_id="operation-2")
        state = self.apply(state, "dispatch", operation_id="operation-2")
        state = self.apply(state, "result", operation_id="operation-2", resolution="completed",
                           observation=OBSERVATION, reason="Fresh operation.")
        self.error("INCOMPLETE_EVIDENCE", state, "advance", target="completed")
        self.assertEqual(len(state["operations"]), 2)

    def test_lost_response_preserves_reservation_until_explicit_reconciliation(self):
        state = self.apply(self.initial(), "advance", target="ready")
        state = self.apply(state, "reserve", operation_id="operation-1")
        self.error("DISPATCH_BLOCKED", state, "reserve", operation_id="another")
        state = self.apply(state, "reconcile", operation_id="operation-1", resolution="unknown",
                           observation=OBSERVATION, reason="Host cannot yet determine whether work ran.")
        self.assertEqual(state["status"], "unknown")
        self.error("DISPATCH_BLOCKED", state, "dispatch", operation_id="operation-1")
        self.error("UNRESOLVED_OPERATIONS", state, "advance", target="ready")
        state = self.apply(state, "reconcile", operation_id="operation-1", resolution="not_started",
                           observation=OBSERVATION, reason="Synthetic host established no invocation.")
        state = self.apply(state, "advance", target="ready")
        self.assertFalse(state["has_dispatched"])
        self.assertEqual(state["operations"][0]["status"], "not_started")

    def test_observed_reconciliation_can_complete_without_dispatching_again(self):
        for kind in ("task", "attempt"):
            for unknown in (False, True):
                with self.subTest(kind=kind, unknown=unknown):
                    if unknown:
                        state = self.running(kind)
                        state = self.apply(state, "result", operation_id="operation-1", resolution="unknown",
                                           reason="The first response was lost.")
                    else:
                        state = self.initial(kind)
                        if kind == "task":
                            state = self.apply(state, "advance", target="ready")
                        state = self.apply(state, "reserve", operation_id="operation-1")
                    state = self.apply(state, "reconcile", operation_id="operation-1", resolution="completed",
                                       observation=OBSERVATION, reason="Existing invocation completion observed.")
                    state = self.apply(state, "evidence", evidence=[receipt(state, slot) for slot in state["required_evidence"]])
                    state = self.apply(state, "advance", target="completed")
                    self.assertEqual(state["status"], "completed")
                    self.assertEqual(len(state["operations"]), 1)

    def test_causes_and_observation_references_are_recoverable_from_events(self):
        state = self.initial()
        command = command_fixture(state, "advance", target="blocked", reason="Required fixture input is unavailable.")
        result = t.apply_command(state, command)
        self.assertIn("cause", result["projection"])
        self.assertEqual(result["projection"]["cause"], command["reason"])
        self.assertIn("command", result["event"])
        self.assertEqual(result["event"]["command"], command)
        state = self.running()
        command = command_fixture(state, "result", operation_id="operation-1", resolution="completed",
                                  observation=OBSERVATION, reason="The invocation ended.")
        result = t.apply_command(state, command)
        self.assertEqual(result["event"]["command"]["observation"], OBSERVATION)

    def test_observed_failure_cannot_complete_against_earlier_passing_receipts(self):
        state = self.running()
        state = self.apply(state, "evidence", evidence=[receipt(state, slot) for slot in state["required_evidence"]])
        state = self.apply(state, "result", operation_id="operation-1", resolution="failed",
                           observation=OBSERVATION, reason="The operation failed after a partial output.")
        self.assertEqual(state["status"], "failed")
        self.assertEqual(state["cause"], "The operation failed after a partial output.")
        self.error("INVALID_TRANSITION", state, "advance", target="completed")

    def test_rerun_receipt_cannot_reuse_the_old_review_context(self):
        state = self.evidenced()
        replacement = receipt(state, "behavior")
        replacement["receipt"]["id"] = "fresh-check-receipt"
        self.error("EVIDENCE_CONFLICT", state, "evidence", evidence=[replacement])
        original = deepcopy(state)
        self.apply(state, "evidence", evidence=state["evidence"])
        self.assertEqual(state, original)

    def test_cancel_ack_does_not_prove_effects_stopped_and_late_results_cannot_resume(self):
        for dispatched in (True, False):
            state = self.running() if dispatched else self.apply(
                self.apply(self.initial(), "advance", target="ready"), "reserve", operation_id="operation-1")
            state = self.apply(state, "cancel", reason="Synthetic withdrawal.")
            state = self.apply(state, "cancel_ack", operation_id="operation-1",
                               observation=OBSERVATION, reason="Host acknowledged request only.")
            self.error("UNRESOLVED_OPERATIONS", state, "advance", target="cancelled")
            self.error("STOP_REQUESTED", state, "dispatch", operation_id="operation-1")
            state = self.apply(state, "reconcile", operation_id="operation-1", resolution="completed",
                               observation=OBSERVATION, reason="Late completion was actually observed.")
            self.error("STOP_REQUESTED", state, "advance", target="completed")
            state = self.apply(state, "advance", target="cancelled")
            self.assertTrue(state["stop_requested"])
            self.error("TERMINAL_STATE", state, "advance", target="ready")

    def test_blocked_failed_and_unknown_have_distinct_recovery(self):
        state = self.initial()
        self.error("MISSING_CAUSE", state, "advance", target="blocked")
        state = self.apply(state, "advance", target="blocked", reason="Missing synthetic prerequisite.")
        self.assertEqual(state["status"], "blocked")
        state = self.apply(state, "advance", target="failed", reason="Unrecoverable within this task.")
        self.assertEqual(state["status"], "failed")
        state = self.apply(state, "advance", target="ready")
        self.assertEqual(state["status"], "ready")
        self.error("INVALID_TRANSITION", state, "advance", target="unknown")

    def test_unknown_fields_boolean_revisions_and_inventory_replacement_are_rejected(self):
        state = self.initial()
        for field, replacement in (("expected_revision", True), ("expected_revision", 0)):
            self.error("INVALID_BOUND", state, "advance", target="ready", **{field: replacement})
        self.error("INVALID_COMMAND", state, "advance", target="ready", new_context_sha="f" * 64)
        command = command_fixture(state, "advance", target="ready")
        command["required_evidence"] = []
        with self.assertRaises(c.ContractError) as caught:
            t.apply_command(state, command)
        self.assertEqual(caught.exception.code, "INVALID_FIELDS")
        with self.assertRaises(c.ContractError) as caught:
            t.initial_projection("job", "fixture", CONTEXT, [])
        self.assertEqual(caught.exception.code, "INVALID_LIST")


if __name__ == "__main__":
    unittest.main()
