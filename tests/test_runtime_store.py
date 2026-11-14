"""TC-115/116: atomic persistence, full replay, ownership and owned process crashes."""

from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
from copy import deepcopy
from pathlib import Path
import json
import os
import socket
import sqlite3
import subprocess
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch

from plugins.sparkforge.runtime import contracts as c
from plugins.sparkforge.runtime import migrations as m
from plugins.sparkforge.runtime import store
from fakes.fake_host import FakeHost, Script
from runtime_fixtures import attempt_fixture, failure_fixture, finding_fixture, result_fixture
from store_fixtures import artifact, command, create_job, local_task, projection
from test_host_adapter import capability_fixture


ROOT = Path(__file__).resolve().parents[1]


class RuntimeStoreTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="coordinated store ", dir=ROOT / "tests")
        self.addCleanup(temporary.cleanup)
        self.base = Path(temporary.name)
        self.workspace = self.base / "workspace"
        self.workspace.mkdir()
        self.root = self.base / "journal"
        self.metadata, self.intent, self.envelope = create_job(self.root, self.workspace)
        self.task = local_task(self.envelope)
        store.register(self.root, "register", "task", self.task, required_evidence=["behavior"])

    def error(self, code, function, *args, **kwargs):
        with self.assertRaises(c.ContractError) as caught:
            function(*args, **kwargs)
        self.assertEqual(caught.exception.code, code)

    def apply(self, action, **fields):
        return store.apply(self.root, "task", command(projection(self.root, self.task), action, **fields))

    def reserve(self):
        self.apply("advance", target="ready")
        return self.apply("reserve", operation_id="op-1")

    def observe(self, *, status="completed", known_usage=False):
        self.reserve()
        self.apply("dispatch", operation_id="op-1")
        caps = capability_fixture()
        caps_sha = store.append_record(self.root, "capabilities", "fixture-job",
                                       store.record_value("capabilities", caps["host"]["id"], 1, caps))["record_sha"]
        usage = {"status": "known", "model_calls": 5, "tokens": 3000, "wall_seconds": 200, "reason": None} if known_usage else None
        fake = FakeHost(caps, {"op-1": Script(("accepted", status), usage=usage)})
        fake.dispatch(self.task, "op-1")
        observed = fake.reconcile(self.task, "op-1")
        record = store.record_value("observation", observed["observation"]["id"], 1, observed,
                                    context={"capabilities_sha": caps_sha})
        state = projection(self.root, self.task)
        store.apply(self.root, "task", command(state, "reconcile", operation_id="op-1", resolution=status,
                                               observation=observed["observation"], reason="Synthetic host reconciliation."),
                    records=(record,))
        return observed, fake

    def test_initialization_and_registration_are_persistent_idempotent_and_not_approval(self):
        original = store.read(self.root)
        state = projection(self.root, self.task)
        self.assertEqual(state["status"], "pending")
        self.assertEqual(original["entities"]["job:fixture-job"]["projection"]["status"], "intake")
        replay = store.register(self.root, "register", "task", self.task, required_evidence=["behavior"])
        self.assertTrue(replay["replayed"])
        self.assertEqual(store.read(self.root), original)
        self.error("ENTITY_EXISTS", store.register, self.root, "other-register", "task", self.task, required_evidence=["behavior"])
        changed = deepcopy(self.task)
        changed["objective"] = "Different assignment."
        self.error("IDEMPOTENCY_CONFLICT", store.register, self.root, "register", "task", changed, required_evidence=["behavior"])
        store.register(self.root, "attempt-register", "attempt", self.task, required_evidence=["observation"])
        self.assertIn("attempt:" + self.task["binding"]["attempt_id"], store.read(self.root)["entities"])

    def test_record_families_round_trip_without_turning_claims_into_authority(self):
        observed, _ = self.observe(known_usage=True)
        attempt = attempt_fixture(self.task)
        attempt.update(operation_key="op-1", producer=observed["producer"], observation=observed["observation"],
                       observed_usage=observed["usage"])
        attempt_sha = store.append_record(self.root, "attempt-record", "fixture-job",
                                         store.record_value("attempt", attempt["binding"]["attempt_id"], 1, attempt))["record_sha"]
        result = result_fixture(self.task)
        result["producer"] = observed["producer"]
        for key, record in (
            ("result-record", store.record_value("result", result["id"], 1, result,
                                                 context={"attempt_sha": attempt_sha, "prior_attempts": []})),
            ("finding-record", store.record_value("finding", finding_fixture()["id"], 1, finding_fixture())),
            ("failure-record", store.record_value("failure", failure_fixture()["id"], 1, failure_fixture())),
            ("evidence-record", artifact()),
        ):
            sha = store.append_record(self.root, key, "fixture-job", record)["record_sha"]
            self.assertEqual(store.read(self.root)["records"][sha], record)
        snapshot = store.read(self.root)
        self.assertEqual(snapshot["records"][attempt_sha]["value"]["observed_usage"]["tokens"], 3000)
        self.assertEqual(projection(self.root, self.task)["status"], "running")
        self.assertFalse(any("approved" in record["value"] for record in snapshot["records"].values()))

    def test_immutable_identity_rejects_rebinding_and_preserves_old_revisions(self):
        record = artifact()
        original_sha = store.append_record(self.root, "artifact-1", "fixture-job", record)["record_sha"]
        original = store.read(self.root)
        changed = deepcopy(record)
        changed["value"]["sha256"] = "f" * 64
        self.error("RECORD_CONFLICT", store.append_record, self.root, "artifact-2", "fixture-job", changed)
        self.assertEqual(store.read(self.root), original)
        changed["revision"] = 2
        new_sha = store.append_record(self.root, "artifact-2", "fixture-job", changed)["record_sha"]
        self.assertNotEqual(original_sha, new_sha)
        self.assertIn(original_sha, store.read(self.root)["records"])

    def test_all_write_boundaries_roll_back_records_events_projections_and_reservations(self):
        self.apply("advance", target="ready")
        state = projection(self.root, self.task)
        request = command(state, "reserve", operation_id="op-1")
        original = store.read(self.root)
        for stage in ("after_records", "after_job", "after_entities", "after_events", "after_reservations", "after_commands", "before_commit"):
            with self.subTest(stage=stage):
                def fail(current):
                    if current == stage:
                        raise RuntimeError("Injected transaction failure")
                with patch.object(store, "_checkpoint", side_effect=fail):
                    with self.assertRaisesRegex(RuntimeError, "Injected"):
                        store.apply(self.root, "task", request, records=(artifact(),))
                self.assertEqual(store.read(self.root), original)
        store.apply(self.root, "task", request, records=(artifact(),))
        after = store.read(self.root)
        self.assertEqual(after["command_count"], original["command_count"] + 1)
        self.assertEqual(len(after["events"]), len(original["events"]) + 1)
        self.assertEqual(after["reservations"]["op-1"]["status"], "reserved")

    def test_lost_commit_reply_is_reconciled_by_original_key_after_cancellation(self):
        state = projection(self.root, self.task)
        request = command(state, "advance", target="ready")
        def lose_reply(stage):
            if stage == "after_commit":
                raise RuntimeError("Lost acknowledgement")
        with patch.object(store, "_checkpoint", side_effect=lose_reply):
            self.error("COMMIT_UNCERTAIN", store.apply, self.root, "task", request)
        self.assertEqual(projection(self.root, self.task)["status"], "ready")
        self.apply("cancel", reason="Stopped after the committed command.")
        original = store.read(self.root)
        replay = store.apply(self.root, "task", request)
        self.assertTrue(replay["replayed"])
        self.assertEqual(replay["projection"]["status"], "cancelled")
        self.assertEqual(store.read(self.root), original)

    def test_conflicting_revisions_payloads_and_ownership_do_not_partially_persist(self):
        state = projection(self.root, self.task)
        request = command(state, "advance", target="ready")
        store.apply(self.root, "task", request)
        changed = deepcopy(request)
        changed["target"] = "blocked"
        changed["reason"] = "Different payload."
        self.error("IDEMPOTENCY_CONFLICT", store.apply, self.root, "task", changed)
        changed["key"] = "different-key"
        self.error("REVISION_CONFLICT", store.apply, self.root, "task", changed)
        self.apply("reserve", operation_id="op-1")
        other = local_task(self.envelope, suffix="-other")
        store.register(self.root, "register-other", "task", other, required_evidence=["behavior"])
        other_state = store.read(self.root)["entities"]["task:" + other["binding"]["task_id"]]["projection"]
        other_state = store.apply(self.root, "task", command(other_state, "advance", target="ready"))["projection"]
        self.error("OPERATION_CONFLICT", store.apply, self.root, "task", command(other_state, "reserve", operation_id="op-1"))
        self.error("DISPATCH_BLOCKED", store.apply, self.root, "task", command(other_state, "reserve", operation_id="op-2"))

    def test_competing_writers_commit_exactly_one_revision(self):
        state = projection(self.root, self.task)
        barrier = threading.Barrier(2)
        def writer(number):
            barrier.wait(timeout=10)
            try:
                store.apply(self.root, "task", command(state, "advance", key=f"writer-{number}", target="ready"))
                return "committed"
            except c.ContractError as error:
                return error.code
        with ThreadPoolExecutor(max_workers=2) as pool:
            outcomes = list(pool.map(writer, (1, 2)))
        self.assertEqual(outcomes.count("committed"), 1)
        self.assertTrue(set(outcomes) <= {"committed", "STORE_BUSY", "REVISION_CONFLICT"}, outcomes)
        self.assertEqual(projection(self.root, self.task)["revision"], state["revision"] + 1)
        self.assertEqual(len(store.read(self.root)["events"]), 1)

    def test_same_key_writers_and_changed_associated_records_have_one_durable_result(self):
        state = projection(self.root, self.task)
        request = command(state, "advance", target="ready", key="same-key")
        barrier = threading.Barrier(2)
        def writer(_number):
            barrier.wait(timeout=10)
            try:
                return store.apply(self.root, "task", request, records=(artifact(),))["replayed"]
            except c.ContractError as error:
                return error.code
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(writer, (1, 2)))
        self.assertIn(False, results)
        self.assertTrue(all(result in (False, True, "STORE_BUSY") for result in results))
        snapshot = store.read(self.root)
        self.assertTrue(store.apply(self.root, "task", request, records=(artifact(),))["replayed"])
        self.error("IDEMPOTENCY_CONFLICT", store.apply, self.root, "task", request, records=(artifact(text="changed"),))
        self.assertEqual(store.read(self.root), snapshot)
        self.assertEqual(len(snapshot["events"]), 1)

    def test_unbacked_or_contradictory_observations_cannot_close_a_reservation(self):
        self.reserve()
        self.apply("dispatch", operation_id="op-1")
        self.error("MISSING_OBSERVATION", self.apply, "result", operation_id="op-1", resolution="completed",
                   observation={"id": "missing", "sha256": "f" * 64}, reason="Unobserved claim.")
        caps = capability_fixture()
        caps_sha = store.append_record(self.root, "caps", "fixture-job",
                                      store.record_value("capabilities", "scripted-fake", 1, caps))["record_sha"]
        fake = FakeHost(caps, {"op-1": Script()})
        observed = fake.dispatch(self.task, "op-1")
        record = store.record_value("observation", observed["observation"]["id"], 1, observed,
                                    context={"capabilities_sha": caps_sha})
        original = store.read(self.root)
        request = command(projection(self.root, self.task), "result", operation_id="op-1", resolution="completed",
                          observation=observed["observation"], reason="Accepted turn is not completion.")
        self.error("OUTCOME_MISMATCH", store.apply, self.root, "task", request, records=(record,))
        self.assertEqual(store.read(self.root), original)
        store.append_record(self.root, "accepted-observation", "fixture-job", record)
        attempt = attempt_fixture(self.task)
        attempt.update(operation_key="op-1", producer=observed["producer"], observation=observed["observation"],
                       observed_usage=observed["usage"])
        self.error("OUTCOME_MISMATCH", store.append_record, self.root, "forged-completion", "fixture-job",
                   store.record_value("attempt", attempt["binding"]["attempt_id"], 1, attempt))
        self.assertEqual(store.read(self.root)["reservations"]["op-1"]["status"], "dispatched")

    def test_followup_observations_version_snapshots_but_never_rebind_exact_references(self):
        self.reserve()
        self.apply("dispatch", operation_id="op-1")
        caps = capability_fixture()
        caps_sha = store.append_record(self.root, "caps", "fixture-job",
                                      store.record_value("capabilities", "scripted-fake", 1, caps))["record_sha"]
        fake = FakeHost(caps, {"op-1": Script(("accepted", "completed"))})
        accepted = fake.dispatch(self.task, "op-1")
        context = {"capabilities_sha": caps_sha}
        store.append_record(self.root, "accepted", "fixture-job",
                            store.record_value("observation", accepted["observation"]["id"], 1, accepted, context=context))
        contradictory = deepcopy(accepted)
        contradictory["reason"] = "Different body under the same exact observation reference."
        self.error("RECORD_CONFLICT", store.append_record, self.root, "contradictory", "fixture-job",
                   store.record_value("observation", contradictory["observation"]["id"], 2, contradictory, context=context))
        completed = fake.reconcile(self.task, "op-1")
        completed_record = store.record_value("observation", completed["observation"]["id"], 2, completed, context=context)
        state = projection(self.root, self.task)
        store.apply(self.root, "task", command(state, "reconcile", operation_id="op-1", resolution="completed",
                                               observation=completed["observation"], reason="Later completion observed."),
                    records=(completed_record,))
        self.assertEqual(store.read(self.root)["reservations"]["op-1"]["status"], "completed")
        self.assertEqual(len([row for row in store.read(self.root)["records"].values() if row["kind"] == "observation"]), 2)

    def test_job_cancel_waits_for_child_effect_reconciliation(self):
        self.reserve()
        self.apply("dispatch", operation_id="op-1")
        job = store.read(self.root)["entities"]["job:fixture-job"]["projection"]
        result = store.apply(self.root, "job", command(job, "cancel", reason="Withdraw job scope."))
        self.assertEqual(result["projection"]["status"], "cancelling")
        self.error("UNRESOLVED_OPERATIONS", store.apply, self.root, "job",
                   command(result["projection"], "advance", target="cancelled"))
        self.assertEqual(store.read(self.root)["reservations"]["op-1"]["status"], "dispatched")
        caps = capability_fixture()
        caps_sha = store.append_record(self.root, "caps", "fixture-job",
                                      store.record_value("capabilities", "scripted-fake", 1, caps))["record_sha"]
        fake = FakeHost(caps, {"op-1": Script(("accepted", "not_started"))})
        fake.dispatch(self.task, "op-1")
        observed = fake.reconcile(self.task, "op-1")
        state = projection(self.root, self.task)
        store.apply(self.root, "task", command(state, "reconcile", operation_id="op-1", resolution="not_started",
                                               observation=observed["observation"], reason="No child execution observed."),
                    records=(store.record_value("observation", observed["observation"]["id"], 1, observed,
                                                context={"capabilities_sha": caps_sha}),))
        job = store.read(self.root)["entities"]["job:fixture-job"]["projection"]
        self.assertEqual(store.apply(self.root, "job", command(job, "advance", target="cancelled"))["projection"]["status"], "cancelled")
        self.error("STOP_REQUESTED", self.apply, "reserve", operation_id="late-op")

    def test_cancelled_scope_retains_late_observations_without_certifying_success(self):
        self.reserve()
        self.apply("dispatch", operation_id="op-1")
        job = store.read(self.root)["entities"]["job:fixture-job"]["projection"]
        store.apply(self.root, "job", command(job, "cancel", reason="Withdraw before response."))
        caps = capability_fixture()
        caps_sha = store.append_record(self.root, "caps", "fixture-job",
                                      store.record_value("capabilities", "scripted-fake", 1, caps))["record_sha"]
        fake = FakeHost(caps, {"op-1": Script(("accepted", "completed"))})
        fake.dispatch(self.task, "op-1")
        observed = fake.reconcile(self.task, "op-1")
        state = projection(self.root, self.task)
        store.apply(self.root, "task", command(state, "reconcile", operation_id="op-1", resolution="completed",
                                               observation=observed["observation"], reason="Late completion retained, not accepted."),
                    records=(store.record_value("observation", observed["observation"]["id"], 1, observed,
                                                context={"capabilities_sha": caps_sha}),))
        evidence = artifact()
        state = projection(self.root, self.task)
        receipt = {"slot": "behavior", "receipt": {"id": evidence["value"]["id"], "sha256": evidence["value"]["sha256"]},
                   "context_sha": state["context_sha"], "outcome": "fail"}
        store.apply(self.root, "task", command(state, "evidence", evidence=[receipt]), records=(evidence,))
        self.assertEqual(store.read(self.root)["reservations"]["op-1"]["status"], "completed")
        self.assertNotEqual(projection(self.root, self.task)["status"], "completed")
        before = store.read(self.root)
        self.error("STOP_REQUESTED", self.apply, "evidence", evidence=[dict(receipt, outcome="pass")])
        self.error("STOP_REQUESTED", self.apply, "advance", target="completed")
        self.assertEqual(store.read(self.root), before)

    def test_legacy_unsafe_admission_history_remains_readable_and_reconcilable(self):
        # Reproduce the old version's synthetic journal, not a new permitted admission.
        with patch.object(store, "COMMAND_VERSION", "sparkforge.store-command.v1", create=True), patch.object(store, "_admit_work"):
            self.apply("advance", target="ready")
            job = store.read(self.root)["entities"]["job:fixture-job"]["projection"]
            job = store.apply(self.root, "job", command(job, "advance", target="blocked", reason="Legacy failure."))["projection"]
            store.apply(self.root, "job", command(job, "advance", target="failed", reason="Legacy terminal job."))
            self.apply("reserve", operation_id="op-1")
            legacy_dispatch = command(projection(self.root, self.task), "dispatch", operation_id="op-1")
            store.apply(self.root, "task", legacy_dispatch)
        snapshot = store.read(self.root)
        self.assertEqual(snapshot["reservations"]["op-1"]["status"], "dispatched")
        self.assertEqual(store.recover(self.root, expected_store_id=self.metadata["store_id"]), snapshot)
        self.assertTrue(store.apply(self.root, "task", legacy_dispatch)["replayed"])
        self.assertEqual(store.read(self.root), snapshot)
        self.error("PARENT_TERMINAL", self.apply, "reserve", operation_id="new-op")
        caps = capability_fixture()
        caps_sha = store.append_record(self.root, "caps", "fixture-job",
                                      store.record_value("capabilities", "scripted-fake", 1, caps))["record_sha"]
        fake = FakeHost(caps, {"op-1": Script(("accepted", "completed"))})
        fake.dispatch(self.task, "op-1")
        observed = fake.reconcile(self.task, "op-1")
        state = projection(self.root, self.task)
        store.apply(self.root, "task", command(state, "reconcile", operation_id="op-1", resolution="completed",
                                               observation=observed["observation"], reason="Settle old effects without new success credit."),
                    records=(store.record_value("observation", observed["observation"]["id"], 1, observed,
                                                context={"capabilities_sha": caps_sha}),))
        self.assertEqual(store.read(self.root)["reservations"]["op-1"]["status"], "completed")
        self.error("PARENT_TERMINAL", self.apply, "advance", target="completed")
        self.assertEqual(fake.dispatch_count, 1)
        legacy_request = store._input("new-legacy-admission", "transition", "task", self.task["binding"]["task_id"],
                                      {"command": legacy_dispatch, "records": []})
        legacy_request["schema_version"] = store.LEGACY_COMMAND_VERSION
        legacy_request.pop("admitted_at", None)
        self.error("UNSUPPORTED_SCHEMA", store._execute, self.root, legacy_request)

    def test_replay_never_calls_host_and_unknown_effects_remain_reserved(self):
        self.reserve()
        self.apply("dispatch", operation_id="op-1")
        fake = FakeHost(capability_fixture(), {"op-1": Script(("accepted", "unknown", "completed"), lose_dispatch_response=True)})
        self.error("HOST_RESPONSE_LOST", fake.dispatch, self.task, "op-1")
        self.apply("result", operation_id="op-1", resolution="unknown", reason="Response lost; effects unresolved.")
        before = store.read(self.root)
        with (patch.object(FakeHost, "dispatch", side_effect=AssertionError("replay dispatch")),
              patch.object(FakeHost, "reconcile", side_effect=AssertionError("replay reconcile")),
              patch.object(subprocess, "Popen", side_effect=AssertionError("replay process")),
              patch.object(socket, "socket", side_effect=AssertionError("replay network"))):
            self.assertEqual(store.recover(self.root, expected_store_id=self.metadata["store_id"]), before)
            self.assertEqual(store.read(self.root), before)
        self.assertEqual(fake.dispatch_count, 1)
        self.assertEqual(before["reservations"]["op-1"]["status"], "unknown")
        self.assertEqual(before["reservations"]["op-1"]["allowance"], self.task["allowance"])
        self.assertIsNone(before["reservations"]["op-1"]["observation_sha"])
        self.error("DISPATCH_BLOCKED", self.apply, "reserve", operation_id="new-key")

    def test_observation_matching_no_start_and_current_evidence_gate_completion(self):
        observed, _ = self.observe(status="not_started")
        state = projection(self.root, self.task)
        self.assertEqual(state["status"], "ready")
        self.assertTrue(store.read(self.root)["reservations"]["op-1"]["dispatched"])
        self.error("INVALID_TRANSITION", self.apply, "advance", target="completed")
        self.error("OPERATION_CONFLICT", self.apply, "reserve", operation_id="op-1")
        self.assertEqual(observed["effect_state"], "not_started")

    def test_current_observed_completion_requires_stored_evidence_and_no_parent_stop(self):
        self.observe()
        evidence = artifact()
        reference = {"id": evidence["value"]["id"], "sha256": evidence["value"]["sha256"]}
        state = projection(self.root, self.task)
        request = command(state, "evidence", evidence=[{"slot": "behavior", "receipt": reference,
                                                       "context_sha": state["context_sha"], "outcome": "pass"}])
        self.error("MISSING_RECORD", store.apply, self.root, "task", request)
        store.apply(self.root, "task", request, records=(evidence,))
        self.assertEqual(self.apply("advance", target="completed")["projection"]["status"], "completed")
        other = local_task(self.envelope, suffix="-later")
        store.register(self.root, "later", "task", other, required_evidence=["behavior"])
        snapshot = store.read(self.root)
        job = snapshot["entities"]["job:fixture-job"]["projection"]
        store.apply(self.root, "job", command(job, "cancel", reason="Job stopped."))
        state = snapshot["entities"]["task:" + other["binding"]["task_id"]]["projection"]
        state = store.apply(self.root, "task", command(state, "advance", target="ready"))["projection"]
        self.error("STOP_REQUESTED", store.apply, self.root, "task", command(state, "reserve", operation_id="late-op"))

    def test_corruption_of_each_materialized_table_is_detected_not_repaired(self):
        self.reserve()
        statements = (
            "UPDATE records SET body='{}'",
            "UPDATE entities SET sha='" + "f" * 64 + "' WHERE kind='task'",
            "UPDATE events SET before_sha='" + "f" * 64 + "'",
            "UPDATE commands SET request_sha='" + "f" * 64 + "' WHERE seq=1",
            "UPDATE reservations SET status='completed'",
            "UPDATE job SET supported_kinds='[]'",
        )
        original = (self.root / m.DATABASE_NAME).read_bytes()
        for statement in statements:
            with self.subTest(statement=statement):
                (self.root / m.DATABASE_NAME).write_bytes(original)
                with closing(sqlite3.connect(self.root / m.DATABASE_NAME)) as connection, connection:
                    connection.execute(statement)
                corrupt = (self.root / m.DATABASE_NAME).read_bytes()
                self.error("CORRUPT_STORE", store.read, self.root)
                self.assertEqual((self.root / m.DATABASE_NAME).read_bytes(), corrupt)
        (self.root / m.DATABASE_NAME).write_bytes(original)

    def test_duplicate_event_ids_fail_without_partial_changes(self):
        self.apply("advance", target="ready")
        existing = store.read(self.root)["events"][0]["id"]
        original = store.read(self.root)
        with patch.object(store.t, "_event_id", return_value=existing):
            self.error("EVENT_CONFLICT", self.apply, "reserve", operation_id="op-1")
        self.assertEqual(store.read(self.root), original)

    def test_process_crashes_before_commit_and_after_commit_preserve_exactly_once_local_effects(self):
        state = projection(self.root, self.task)
        request = command(state, "advance", target="ready", key="crash-command")
        input_path = self.base / "crash-input.json"
        input_path.write_text(json.dumps(request), encoding="utf-8")
        code = (
            "import sys,os,json,sqlite3; from pathlib import Path; "
            "sys.path.insert(0,sys.argv[1]); "
            "from plugins.sparkforge.runtime import store; "
            "real=sqlite3.connect\n"
            "def connect(*args,**kwargs):\n"
            " conn=real(*args,**kwargs); conn.execute('PRAGMA cache_size=1'); return conn\n"
            "store.sqlite3.connect=connect\n"
            "def crash(stage):\n"
            " if stage==sys.argv[4]: os._exit(73)\n"
            "store._checkpoint=crash\n"
            "store.apply(Path(sys.argv[2]),'task',json.loads(Path(sys.argv[3]).read_text(encoding='utf-8')))\n"
        )
        original = store.read(self.root)
        for stage in ("after_entities", "after_commit"):
            result = subprocess.run([sys.executable, "-I", "-B", "-c", code, str(ROOT), str(self.root), str(input_path), stage],
                                    cwd=ROOT, capture_output=True, text=True, timeout=30)
            self.assertEqual(result.returncode, 73, result.stderr)
            if stage == "after_entities":
                self.error("RECOVERY_REQUIRED", store.read, self.root)
            recovered = store.recover(self.root, expected_store_id=self.metadata["store_id"])
            self.assertFalse((self.root / (m.DATABASE_NAME + "-journal")).exists())
            if stage == "after_entities":
                self.assertEqual(recovered, original)
            else:
                self.assertEqual(recovered["command_count"], original["command_count"] + 1)
                replay = store.apply(self.root, "task", request)
                self.assertTrue(replay["replayed"])
                self.assertEqual(store.read(self.root), recovered)

    def test_future_header_and_wrong_store_identity_are_refused(self):
        self.error("STORE_IDENTITY_MISMATCH", store.recover, self.root, expected_store_id="different-store")
        with closing(sqlite3.connect(self.root / m.DATABASE_NAME)) as connection, connection:
            connection.execute("PRAGMA user_version=999")
        before = (self.root / m.DATABASE_NAME).read_bytes()
        self.error("UNSUPPORTED_STORE_VERSION", store.read, self.root)
        self.error("UNSUPPORTED_STORE_VERSION", store.recover, self.root, expected_store_id=self.metadata["store_id"])
        self.assertEqual((self.root / m.DATABASE_NAME).read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
