"""TC-117/118: one scripted worker at a time; role completion is not job acceptance."""

from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from pathlib import Path
import tempfile
import threading
import unittest
from unittest.mock import patch

from plugins.sparkforge.runtime import contracts as c
from plugins.sparkforge.runtime import coordinator as co
from plugins.sparkforge.runtime import scheduler as s
from plugins.sparkforge.runtime import store
from fakes.fake_host import FakeHost, Script
from runtime_fixtures import PLAN_SHA, CANDIDATE_SHA, attempt_fixture, result_fixture, finding_fixture
from store_fixtures import create_job, local_task
from test_host_adapter import capability_fixture


ROOT = Path(__file__).resolve().parents[1]
KNOWN_USAGE = {"status": "known", "model_calls": 0, "tokens": 0, "wall_seconds": 0, "reason": None}


def schedule_fixture(intent, envelope):
    tasks = [local_task(envelope, role) for role in s.MANDATORY_ROLES]
    for index, task in enumerate(tasks):
        task["dependencies"] = [] if index == 0 else [tasks[index - 1]["binding"]["task_id"]]
    return {
        "schema_version": "sparkforge.schedule.v1", "id": "fixture-schedule", "revision": 1, "job_id": "fixture-job",
        "intent_sha": c.record_digest(intent), "envelope_sha": c.record_digest(envelope),
        "plan_sha": PLAN_SHA, "candidate_sha": CANDIDATE_SHA, "required_roles": list(s.MANDATORY_ROLES), "tasks": tasks,
        "job_context_sha": c.record_digest({"intent": c.record_digest(intent), "envelope": c.record_digest(envelope)}),
    }


def bound_result(task):
    result = result_fixture(task)
    token = c.record_digest({"operation_key": s.operation_key(task)})[:24]
    result["producer"] = {
        "host": dict(task["routes"]["host"]), "role": task["binding"]["role"],
        "session_id": "fake-session-" + token, "context_id": "fake-context-" + token,
    }
    result["id"] = "result-" + task["binding"]["task_id"]
    result["changed_paths"], result["output_candidate_sha"] = [], None
    result["usage_claim"] = dict(KNOWN_USAGE)
    return result


class SchedulerTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="serial coordinator ", dir=ROOT / "tests")
        self.addCleanup(temporary.cleanup)
        self.base = Path(temporary.name)
        self.workspace = self.base / "workspace"
        self.workspace.mkdir()
        self.root = self.base / "journal"
        self.metadata, self.intent, self.envelope = create_job(self.root, self.workspace)
        self.schedule = schedule_fixture(self.intent, self.envelope)

    def validate(self, value):
        return s.validate_schedule(value, intent=self.intent, envelope=self.envelope)

    def error(self, code, function, *args, **kwargs):
        with self.assertRaises(c.ContractError) as caught:
            function(*args, **kwargs)
        self.assertEqual(caught.exception.code, code)

    def setup_coordinator(self, *, scripts=None, results=None, capabilities=None):
        results = results or {task["binding"]["task_id"]: bound_result(task) for task in self.schedule["tasks"]}
        if scripts is None:
            scripts = {s.operation_key(task): Script(usage=KNOWN_USAGE, result_sha=c.record_digest(results[task["binding"]["task_id"]]))
                       for task in self.schedule["tasks"]}
        self.fake = FakeHost(capability_fixture() if capabilities is None else capabilities, scripts)
        self.coordinator = co.Coordinator(self.root, self.fake)
        self.coordinator.install(self.schedule)
        self.results = results
        return self.coordinator

    def complete_host(self, task):
        for _ in range(4):
            report = self.coordinator.tick()
            if report["status"] == "AWAITING_RESULT":
                self.assertEqual(report["task_id"], task["binding"]["task_id"])
                return
        self.fail(f"Host did not reach structured-result boundary: {report}")

    def submit(self, task):
        snapshot = store.read(self.root)
        reservation = snapshot["reservations"][s.operation_key(task)]
        observed = snapshot["records"][reservation["observation_sha"]]["value"]
        attempt = attempt_fixture(task)
        attempt.update(operation_key=s.operation_key(task), producer=observed["producer"],
                       observation=observed["observation"], observed_usage=observed["usage"])
        return self.coordinator.submit_result(self.results[task["binding"]["task_id"]], attempt)

    def test_graph_rejects_cycles_unknown_dependencies_and_missing_role_barriers(self):
        value = deepcopy(self.schedule)
        value["tasks"][0]["dependencies"] = [value["tasks"][1]["binding"]["task_id"]]
        self.error("DEPENDENCY_CYCLE", self.validate, value)
        value = deepcopy(self.schedule)
        value["tasks"][0]["dependencies"] = ["missing"]
        self.error("UNKNOWN_DEPENDENCY", self.validate, value)
        for role in s.MANDATORY_ROLES:
            value = deepcopy(self.schedule)
            value["required_roles"].remove(role)
            self.error("MISSING_ROLE_BARRIER", self.validate, value)
        value = deepcopy(self.schedule)
        value["tasks"][-1]["dependencies"] = [value["tasks"][0]["binding"]["task_id"]]
        self.error("MISSING_ROLE_BARRIER", self.validate, value)
        value = deepcopy(self.schedule)
        value["tasks"].pop()
        self.error("MISSING_ROLE_BARRIER", self.validate, value)

    def test_graph_rejects_duplicate_attempts_missing_criteria_and_ownership_overlap(self):
        value = deepcopy(self.schedule)
        value["tasks"][1]["binding"]["attempt_id"] = value["tasks"][0]["binding"]["attempt_id"]
        self.error("DUPLICATE_VALUE", self.validate, value)
        value = deepcopy(self.schedule)
        value["tasks"][-1]["acceptance_ids"] = ["A1"]
        self.error("MISSING_CRITERION", self.validate, value)
        value = deepcopy(self.schedule)
        value["tasks"][1]["allowed_writes"] = value["tasks"][0]["allowed_writes"][:]
        self.error("OWNERSHIP_CONFLICT", self.validate, value)
        value = deepcopy(self.schedule)
        value["tasks"][1]["protected_paths"].append("src")
        self.error("OWNERSHIP_CONFLICT", self.validate, value)
        value = deepcopy(self.schedule)
        value["tasks"][0]["binding"]["candidate_sha"] = "f" * 64
        self.error("BINDING_MISMATCH", self.validate, value)

    def test_install_is_resumable_idempotent_and_graph_is_pinned_before_effects(self):
        fake = FakeHost(capability_fixture(), {})
        coordinator = co.Coordinator(self.root, fake)
        real_register = store.register
        count = 0
        def interrupted(*args, **kwargs):
            nonlocal count
            result = real_register(*args, **kwargs)
            count += 1
            if count == 1:
                raise RuntimeError("Interrupted partial installation")
            return result
        with patch.object(store, "register", side_effect=interrupted):
            with self.assertRaisesRegex(RuntimeError, "Interrupted partial"):
                coordinator.install(self.schedule)
        self.error("TASK_INVENTORY_MISMATCH", coordinator.tick)
        coordinator.install(self.schedule)
        original = store.read(self.root)
        coordinator.install(self.schedule)
        self.assertEqual(store.read(self.root), original)
        changed = deepcopy(self.schedule)
        changed["tasks"][0]["objective"] = "Changed work."
        self.error("IDEMPOTENCY_CONFLICT", coordinator.install, changed)
        self.assertEqual(fake.dispatch_count, 0)

    def test_complete_serial_graph_preserves_all_role_barriers_and_never_grants_job_acceptance(self):
        self.setup_coordinator()
        for index, task in enumerate(self.schedule["tasks"]):
            with self.subTest(role=task["binding"]["role"]):
                self.assertEqual(self.coordinator.status()["task_id"], task["binding"]["task_id"])
                self.complete_host(task)
                self.assertEqual(self.fake.dispatch_count, index + 1)
                original = store.read(self.root)
                self.assertEqual(self.coordinator.tick()["status"], "AWAITING_RESULT")
                self.assertEqual(store.read(self.root), original)
                report = self.submit(task)
                self.assertFalse(report["job_ready"])
                self.assertEqual(self.fake.dispatch_count, index + 1)
        self.assertEqual(report["status"], "AWAITING_JOB_ACCEPTANCE")
        before = store.read(self.root)
        self.assertEqual(self.coordinator.tick(), report)
        self.assertEqual(store.read(self.root), before)
        self.assertEqual(self.fake.dispatch_count, 5)

    def test_lost_dispatch_response_and_coordinator_restart_do_not_duplicate_work(self):
        results = {task["binding"]["task_id"]: bound_result(task) for task in self.schedule["tasks"]}
        task = self.schedule["tasks"][0]
        script = Script(("accepted", "running", "completed"), KNOWN_USAGE,
                        c.record_digest(results[task["binding"]["task_id"]]), lose_dispatch_response=True)
        self.setup_coordinator(scripts={s.operation_key(task): script}, results=results)
        self.assertEqual(self.coordinator.tick()["status"], "RECONCILIATION_REQUIRED")
        self.assertEqual(self.fake.dispatch_count, 1)
        self.coordinator = co.Coordinator(self.root, self.fake)
        self.assertEqual(self.coordinator.tick()["status"], "RECONCILIATION_REQUIRED")
        self.assertEqual(self.coordinator.tick()["status"], "AWAITING_RESULT")
        self.assertEqual(self.fake.dispatch_count, 1)
        self.assertEqual(self.submit(task)["status"], "READY")

    def test_unknown_effects_never_select_another_task_or_new_operation(self):
        task = self.schedule["tasks"][0]
        self.setup_coordinator(scripts={s.operation_key(task): Script(("accepted", "unknown"))})
        for _ in range(4):
            self.assertEqual(self.coordinator.tick()["status"], "RECONCILIATION_REQUIRED")
        snapshot = store.read(self.root)
        self.assertEqual(self.fake.dispatch_count, 1)
        self.assertEqual(len(snapshot["reservations"]), 1)
        self.assertEqual(snapshot["reservations"][s.operation_key(task)]["status"], "unknown")
        self.assertEqual(snapshot["reservations"][s.operation_key(task)]["allowance"], task["allowance"])

    def test_failure_after_dispatch_marker_before_host_requires_reconciliation(self):
        task = self.schedule["tasks"][0]
        self.setup_coordinator()
        with patch.object(self.fake, "dispatch", side_effect=RuntimeError("Process died before host call")):
            with self.assertRaisesRegex(RuntimeError, "Process died"):
                self.coordinator.tick()
        self.assertEqual(self.fake.dispatch_count, 0)
        self.coordinator = co.Coordinator(self.root, self.fake)
        for _ in range(2):
            self.assertEqual(self.coordinator.tick()["status"], "RECONCILIATION_REQUIRED")
        self.assertEqual(self.fake.dispatch_count, 0)
        self.assertEqual(store.read(self.root)["reservations"][s.operation_key(task)]["status"], "dispatched")

    def test_unknown_usage_policy_blocks_new_work_without_turning_it_into_zero(self):
        task = self.schedule["tasks"][0]
        result = bound_result(task)
        self.setup_coordinator(scripts={s.operation_key(task): Script(result_sha=c.record_digest(result))})
        self.complete_host(task)
        self.assertEqual(self.submit(task)["status"], "USAGE_UNKNOWN")
        self.assertEqual(self.coordinator.tick()["status"], "USAGE_UNKNOWN")
        self.assertEqual(self.fake.dispatch_count, 1)

    def test_no_start_does_not_silently_allocate_another_attempt(self):
        task = self.schedule["tasks"][0]
        self.setup_coordinator(scripts={s.operation_key(task): Script(("accepted", "not_started"), KNOWN_USAGE)})
        self.coordinator.tick()
        self.assertEqual(self.coordinator.tick()["status"], "RETRY_REQUIRES_PLAN")
        self.assertEqual(self.coordinator.tick()["status"], "RETRY_REQUIRES_PLAN")
        self.assertEqual(self.fake.dispatch_count, 1)

    def test_parent_cancel_waits_for_observed_stop_without_duplicate_cancel(self):
        task = self.schedule["tasks"][0]
        self.setup_coordinator(scripts={s.operation_key(task): Script(("accepted", "running", "stopped"), KNOWN_USAGE)})
        self.coordinator.tick()
        self.assertEqual(self.coordinator.cancel("Synthetic user withdrawal.")["status"], "CANCELLING")
        self.assertEqual(self.coordinator.tick()["status"], "CANCELLING")
        self.assertEqual(self.fake.cancel_count, 1)
        self.assertEqual(self.coordinator.tick()["status"], "CANCELLING")
        self.assertEqual(self.coordinator.tick()["status"], "CANCELLING")
        self.assertEqual(self.coordinator.tick()["status"], "CANCELLED")
        self.assertEqual(self.fake.dispatch_count, 1)
        self.assertEqual(self.fake.cancel_count, 1)
        self.assertFalse(self.coordinator.status()["job_ready"])

    def test_concurrent_ticks_dispatch_at_most_once(self):
        self.setup_coordinator()
        barrier = threading.Barrier(2)
        def tick(_index):
            barrier.wait(timeout=10)
            try:
                return co.Coordinator(self.root, self.fake).tick()["status"]
            except c.ContractError as error:
                return error.code
        with ThreadPoolExecutor(max_workers=2) as pool:
            reports = list(pool.map(tick, (1, 2)))
        self.assertLessEqual(self.fake.dispatch_count, 1, reports)
        self.assertTrue(all(report in ("RECONCILIATION_REQUIRED", "STORE_BUSY", "RECOVERY_REQUIRED",
                                       "REVISION_CONFLICT", "DISPATCH_BLOCKED") for report in reports), reports)
        self.assertLessEqual(len(store.read(self.root)["reservations"]), 1)

    def test_structured_result_binding_and_blocking_findings_cannot_be_bypassed(self):
        results = {task["binding"]["task_id"]: bound_result(task) for task in self.schedule["tasks"]}
        task = self.schedule["tasks"][0]
        results[task["binding"]["task_id"]]["findings"] = [finding_fixture()]
        self.setup_coordinator(results=results)
        self.complete_host(task)
        self.assertEqual(self.submit(task)["status"], "BLOCKED")
        self.assertEqual(self.coordinator.tick()["status"], "BLOCKED")
        self.assertEqual(self.fake.dispatch_count, 1)

    def test_candidate_changes_block_pinned_graph_until_real_integration_exists(self):
        task = self.schedule["tasks"][0]
        results = {item["binding"]["task_id"]: bound_result(item) for item in self.schedule["tasks"]}
        results[task["binding"]["task_id"]]["changed_paths"] = task["allowed_writes"][:]
        results[task["binding"]["task_id"]]["output_candidate_sha"] = "f" * 64
        self.setup_coordinator(results=results)
        self.complete_host(task)
        self.assertEqual(self.submit(task)["status"], "BLOCKED")
        self.assertEqual(self.fake.dispatch_count, 1)

    def test_result_commit_reply_loss_resumes_without_duplicate_evidence(self):
        task = self.schedule["tasks"][0]
        self.setup_coordinator()
        self.complete_host(task)
        def lost_reply(stage):
            if stage == "after_commit":
                raise RuntimeError("Lost result acknowledgement")
        with patch.object(store, "_checkpoint", side_effect=lost_reply):
            self.error("COMMIT_UNCERTAIN", self.submit, task)
        self.assertEqual(self.submit(task)["status"], "READY")
        before = store.read(self.root)
        self.assertEqual(self.submit(task)["status"], "READY")
        self.assertEqual(store.read(self.root), before)

    def test_capability_or_identity_changes_refuse_before_effects(self):
        self.setup_coordinator()
        changed = capability_fixture()
        changed["support"]["dispatch"] = "unsupported"
        with patch.object(self.fake, "discover", return_value=changed):
            self.error("HOST_CONTEXT_MISMATCH", self.coordinator.tick)
        self.assertEqual(self.fake.dispatch_count, 0)
        native = capability_fixture()
        native["evidence_class"] = "host_observed"
        with patch.object(self.fake, "discover", return_value=native):
            self.error("HOST_NOT_QUALIFIED", self.coordinator.install, self.schedule)
        self.assertEqual(self.fake.dispatch_count, 0)

    def test_stale_tick_cannot_skip_host_cancellation_after_another_tick_dispatches(self):
        task = self.schedule["tasks"][0]
        self.setup_coordinator(scripts={s.operation_key(task): Script(("accepted", "running", "stopped"), KNOWN_USAGE)})
        other = co.Coordinator(self.root, self.fake)
        original_context = self.coordinator._context
        interrupted = False
        def interleaved_context():
            nonlocal interrupted
            context = original_context()
            if not interrupted:
                interrupted = True
                other.tick()
                other.cancel("Cancellation arrived while the first tick held an older snapshot.")
            return context
        with patch.object(self.coordinator, "_context", side_effect=interleaved_context):
            try:
                self.coordinator.tick()
            except c.ContractError as error:
                self.assertIn(error.code, ("UNRESOLVED_OPERATIONS", "STOP_REQUESTED", "DISPATCH_BLOCKED", "REVISION_CONFLICT"))
        for _ in range(4):
            other.tick()
        self.assertEqual(self.fake.cancel_count, 1)
        self.assertEqual(self.fake.dispatch_count, 1)
        self.assertEqual(other.status()["status"], "CANCELLED")

    def test_unsupported_cancellation_still_reconciles_observed_completion(self):
        task = self.schedule["tasks"][0]
        capabilities = capability_fixture()
        capabilities["support"]["cancel"] = "unsupported"
        self.setup_coordinator(scripts={s.operation_key(task): Script(("accepted", "completed"), KNOWN_USAGE)},
                               capabilities=capabilities)
        self.coordinator.tick()
        self.coordinator.cancel("Stop admission even though this host cannot cancel.")
        self.coordinator.tick()
        report = self.coordinator.tick()
        self.assertEqual(report["status"], "CANCELLED")
        self.assertEqual(self.fake.cancel_count, 0)
        self.assertEqual(self.fake.dispatch_count, 1)
        self.assertEqual(store.read(self.root)["reservations"][s.operation_key(task)]["status"], "completed")

    def test_same_job_and_task_identifier_do_not_collide_in_command_keys(self):
        self.schedule["tasks"][-1]["binding"]["task_id"] = self.schedule["job_id"]
        self.setup_coordinator()
        self.coordinator.tick()
        self.coordinator.cancel("Cancel graph with a task sharing the job's identifier.")
        for _ in range(5):
            report = self.coordinator.tick()
            if report["status"] == "CANCELLED":
                break
        self.assertEqual(report["status"], "CANCELLED")
        self.assertEqual(store.read(self.root)["entities"]["task:fixture-job"]["projection"]["status"], "cancelled")

    def test_job_context_invalidation_stops_the_pinned_graph_and_cannot_drop_active_work(self):
        self.setup_coordinator()
        job = store.read(self.root)["entities"]["job:fixture-job"]["projection"]
        store.apply(self.root, "job", co._command(job, "invalidate", new_context_sha="f" * 64, reason="Candidate/plan changed."))
        self.error("STALE_CONTEXT", self.coordinator.tick)
        self.assertEqual(self.fake.dispatch_count, 0)
        # A separate unchanged synthetic job exercises the active-descendant guard.
        other_workspace = self.base / "other-workspace"
        other_workspace.mkdir()
        other_root = self.base / "other-journal"
        _, intent, envelope = create_job(other_root, other_workspace)
        schedule = schedule_fixture(intent, envelope)
        task = schedule["tasks"][0]
        fake = FakeHost(capability_fixture(), {s.operation_key(task): Script(("accepted", "unknown"))})
        coordinator = co.Coordinator(other_root, fake)
        coordinator.install(schedule)
        coordinator.tick()
        job = store.read(other_root)["entities"]["job:fixture-job"]["projection"]
        self.error("INVALID_INVALIDATION", store.apply, other_root, "job",
                   co._command(job, "invalidate", new_context_sha="f" * 64, reason="Cannot discard outstanding effects."))
        self.assertEqual(store.read(other_root)["reservations"][s.operation_key(task)]["status"], "unknown")


if __name__ == "__main__":
    unittest.main()
