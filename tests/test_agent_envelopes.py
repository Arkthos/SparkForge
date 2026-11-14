"""TC-105/TC-106: bounded role exchanges do not admit their own authority or evidence."""

from copy import deepcopy
import unittest

from plugins.sparkforge.runtime import contracts as c
from plugins.sparkforge.runtime import agent_contracts as a
from runtime_fixtures import (
    CANDIDATE_SHA, PLAN_SHA, attempt_fixture, envelope_fixture, failure_fixture, finding_fixture,
    intent_fixture, producer_fixture, result_fixture, task_fixture,
)


class AgentEnvelopeTests(unittest.TestCase):
    def error(self, code, function, *args, **kwargs):
        with self.assertRaises(c.ContractError) as caught:
            function(*args, **kwargs)
        self.assertEqual(caught.exception.code, code)

    def task(self, value=None):
        return a.validate_task(task_fixture() if value is None else value, intent=intent_fixture(),
                               envelope=envelope_fixture(), plan_sha=PLAN_SHA, candidate_sha=CANDIDATE_SHA)

    def result(self, value=None, *, task=None, attempt=None, candidate=CANDIDATE_SHA, prior=()):
        task = self.task() if task is None else task
        return a.validate_result(result_fixture(task) if value is None else value, task=task,
                                 attempt=attempt_fixture(task) if attempt is None else attempt,
                                 current_candidate_sha=candidate, prior_producers=prior)

    def test_every_role_exchanges_detached_bounded_claims(self):
        for role in a.RESULT_KINDS:
            with self.subTest(role=role):
                raw = task_fixture(role)
                original = deepcopy(raw)
                task = self.task(raw)
                attempt = a.validate_attempt(c.parse_json(c.canonical_json(attempt_fixture(task))), task=task)
                result = self.result(c.parse_json(c.canonical_json(result_fixture(task))), task=task, attempt=attempt,
                                     prior=(producer_fixture("brain" if role == "controller" else "coder"),))
                self.assertEqual(task, original)
                self.assertEqual(raw, original)
                self.assertEqual(result["result_kind"], a.RESULT_KINDS[role])
                self.assertEqual(attempt["observed_usage"]["status"], "unknown")
                result["binding"]["task_id"] = "mutated-copy"
                self.assertEqual(task["binding"]["task_id"], original["binding"]["task_id"])
                self.assertNotIn("admitted", result)
                self.assertNotIn("approved", result)

    def test_every_binding_change_is_rejected(self):
        task = self.task()
        for field, original in task["binding"].items():
            with self.subTest(field=field):
                result = result_fixture(task)
                result["binding"][field] = "reviewer" if field == "role" else ("f" * 64 if field.endswith("_sha") else "foreign")
                self.assertNotEqual(result["binding"][field], original)
                self.error("BINDING_MISMATCH", self.result, result)
                attempt = attempt_fixture(task)
                attempt["binding"] = result["binding"]
                self.error("BINDING_MISMATCH", a.validate_attempt, attempt, task=task)
        self.error("STALE_CANDIDATE", self.result, candidate="f" * 64)
        task["inputs"][0]["sha256"] = "f" * 64
        self.error("BINDING_MISMATCH", self.task, task)

    def test_changed_assignment_invalidates_attempt_and_result(self):
        task = self.task()
        attempt = attempt_fixture(task)
        result = result_fixture(task)
        for field, replacement in (("objective", "Different task"), ("allowed_writes", ["src/other.py"]),
                                   ("deadline", "2029-12-02T00:00:00Z"), ("stop_conditions", ["Different stop condition."])):
            changed = deepcopy(task)
            changed[field] = replacement
            self.error("BINDING_MISMATCH", a.validate_attempt, attempt, task=changed)
            self.error("BINDING_MISMATCH", self.result, result, task=changed, attempt=attempt_fixture(changed))

    def test_task_rejects_foreign_current_context_and_allowance_expansion(self):
        for key in ("intent_sha", "envelope_sha", "plan_sha", "candidate_sha"):
            value = task_fixture()
            value["binding"][key] = "f" * 64
            self.error("BINDING_MISMATCH", self.task, value)
        for field, replacement in (
            ("environment", "CORP"), ("profile", {"id": "fictional-profile", "revision": 2}),
            ("routes", {"host": {"id": "foreign-host", "revision": 1}, "provider": {"id": "no-model", "revision": 1}}),
        ):
            value = task_fixture()
            value[field] = replacement
            self.error("ENVIRONMENT_MISMATCH", self.task, value)
        for field, replacement in (
            ("workspace_id", "foreign"), ("data_root_ids", ["foreign"]), ("tools", ["unlisted-tool"]),
            ("effects", ["workspace_write", "unlisted-effect"]), ("deadline", "2031-01-01T00:00:00Z"),
        ):
            value = task_fixture()
            value[field] = replacement
            self.error("SCOPE_VIOLATION", self.task, value)
        for key in task_fixture()["allowance"]:
            for replacement in (True, 0, -1, float("inf"), task_fixture()["allowance"][key] + 1):
                value = task_fixture()
                value["allowance"][key] = replacement
                self.error("INVALID_BOUND", self.task, value)

    def test_paths_protection_and_exact_write_inventory(self):
        for name in ("../outside", r"C:\absolute", "src//file", "src/*.py", ".git/config", ".env"):
            value = task_fixture()
            value["allowed_writes"] = [name]
            self.error("UNSAFE_PATH", self.task, value)
            result = result_fixture(self.task())
            result["changed_paths"] = [name]
            self.error("UNSAFE_PATH", self.result, result)
        for name in ("evaluation/test.py", "CONTROL/intent.json", "evaluation"):
            value = task_fixture()
            value["allowed_writes"] = [name]
            self.error("SCOPE_VIOLATION", self.task, value)
        value = task_fixture()
        value["allowed_writes"] = ["src/a.py", "src/A.py"]
        self.error("DUPLICATE_VALUE", self.task, value)
        result = result_fixture(self.task())
        result["changed_paths"] = ["src/unassigned.py"]
        self.error("SCOPE_VIOLATION", self.result, result)
        result["changed_paths"] = ["SRC/component.py"]
        self.error("SCOPE_VIOLATION", self.result, result)

    def test_read_only_roles_cannot_become_writers_or_other_roles(self):
        value = task_fixture("reviewer")
        value["allowed_writes"] = ["src/component.py"]
        self.error("ROLE_VIOLATION", self.task, value)
        value = task_fixture()
        value["required_result"] = "controller_verdict"
        self.error("ROLE_VIOLATION", self.task, value)
        value = task_fixture()
        value["effects"] = ["workspace_read"]
        self.error("SCOPE_VIOLATION", self.task, value)
        result = result_fixture(self.task())
        result["result_kind"] = "review"
        self.error("ROLE_VIOLATION", self.result, result)

    def test_observed_producer_must_match_and_cannot_be_relabelled_for_review(self):
        task = self.task()
        for field, replacement in (("role", "reviewer"), ("session_id", "foreign"), ("context_id", "foreign"),
                                   ("host", {"id": "foreign", "revision": 1})):
            result = result_fixture(task)
            result["producer"][field] = replacement
            self.error("PRODUCER_MISMATCH", self.result, result)
        reviewer = self.task(task_fixture("reviewer"))
        self.error("SEPARATION_REQUIRED", self.result, task=reviewer)
        prior = producer_fixture("coder")
        attempt = attempt_fixture(reviewer)
        attempt["producer"]["context_id"] = prior["context_id"]
        result = result_fixture(reviewer)
        result["producer"] = deepcopy(attempt["producer"])
        self.error("PRODUCER_NOT_SEPARATE", self.result, result, task=reviewer, attempt=attempt, prior=(prior,))
        self.result(task=reviewer, prior=(prior,))

    def test_dispatch_acceptance_and_cancel_request_are_not_completion(self):
        task = self.task()
        for status in ("reserved", "accepted", "running", "cancel_requested"):
            attempt = attempt_fixture(task)
            attempt["status"] = status
            attempt["finished_at"] = None
            if status == "reserved":
                attempt["producer"] = attempt["observation"] = attempt["started_at"] = None
            self.error("RESULT_BEFORE_COMPLETION", self.result, task=task, attempt=attempt)
        attempt = attempt_fixture(task)
        attempt["status"] = "cancelled"
        self.error("OUTCOME_MISMATCH", self.result, task=task, attempt=attempt)
        result = result_fixture(task)
        result["outcome"], result["next_action"] = "cancelled", "stop"
        self.result(result, task=task, attempt=attempt)

    def test_host_configuration_revision_does_not_create_a_separate_producer(self):
        prior = producer_fixture("coder")
        envelope = envelope_fixture()
        envelope["routes"]["host"]["revision"] = 2
        task = task_fixture("reviewer")
        task["routes"]["host"]["revision"] = 2
        task["binding"]["envelope_sha"] = c.record_digest(envelope)
        task = a.validate_task(task, intent=intent_fixture(), envelope=envelope,
                               plan_sha=PLAN_SHA, candidate_sha=CANDIDATE_SHA)
        attempt = attempt_fixture(task)
        attempt["producer"].update(host={"id": "scripted-fake", "revision": 2},
                                   session_id=prior["session_id"], context_id=prior["context_id"])
        result = result_fixture(task)
        result["producer"] = deepcopy(attempt["producer"])
        self.error("PRODUCER_NOT_SEPARATE", self.result, result, task=task, attempt=attempt, prior=(prior,))

    def test_unknown_effects_and_usage_do_not_become_zero_or_safe_retries(self):
        task = self.task()
        attempt = attempt_fixture(task)
        attempt["status"], attempt["finished_at"] = "unknown", None
        self.error("OUTCOME_MISMATCH", self.result, task=task, attempt=attempt)
        result = result_fixture(task)
        result["outcome"], result["next_action"] = "unknown", "reconcile"
        self.result(result, task=task, attempt=attempt)
        result["next_action"] = "repair"
        self.error("UNRESOLVED_EFFECTS", self.result, result, task=task, attempt=attempt)
        for field in ("tokens", "model_calls", "wall_seconds"):
            attempt = attempt_fixture(task)
            attempt["observed_usage"][field] = 0
            self.error("INVALID_USAGE", a.validate_attempt, attempt, task=task)
        failure = failure_fixture()
        failure.update(kind="unknown_effects", uncertainty=["Completion was not observed."])
        self.error("UNRESOLVED_EFFECTS", a.validate_failure, failure)
        failure["suggested_action"] = "reconcile"
        a.validate_failure(failure)

    def test_worker_usage_claim_never_overwrites_observed_usage(self):
        task = self.task()
        attempt = attempt_fixture(task)
        attempt["observed_usage"] = {"status": "known", "model_calls": 5, "tokens": 2500, "wall_seconds": 150, "reason": None}
        result = result_fixture(task)
        result["usage_claim"] = {"status": "known", "model_calls": 0, "tokens": 0, "wall_seconds": 0, "reason": None}
        self.result(result, task=task, attempt=attempt)
        self.assertEqual(attempt["observed_usage"]["tokens"], 2500)
        self.assertEqual(result["usage_claim"]["tokens"], 0)
        for invalid in (True, -1, float("nan")):
            result["usage_claim"]["tokens"] = invalid
            self.error("INVALID_USAGE", self.result, result, task=task, attempt=attempt)

    def test_reserved_attempt_cannot_claim_unobserved_consumption(self):
        task = self.task()
        attempt = attempt_fixture(task)
        attempt.update(status="reserved", producer=None, observation=None, started_at=None, finished_at=None)
        for field in ("model_calls", "tokens", "wall_seconds"):
            with self.subTest(field=field):
                attempt["observed_usage"] = {
                    "status": "known", "model_calls": 0, "tokens": 0, "wall_seconds": 0, "reason": None,
                }
                attempt["observed_usage"][field] = 1
                self.error("INVALID_USAGE", a.validate_attempt, attempt, task=task)

    def test_reserved_allowance_stays_separate_from_unknown_consumption(self):
        task = self.task()
        allowance = dict(task["allowance"])
        attempt = attempt_fixture(task)
        attempt.update(status="reserved", producer=None, observation=None, started_at=None, finished_at=None)
        normalized = a.validate_attempt(attempt, task=task)
        self.assertEqual(normalized["observed_usage"]["status"], "unknown")
        self.assertIsNone(normalized["observed_usage"]["tokens"])
        self.assertEqual(task["allowance"], allowance)
        attempt["observed_usage"] = {"status": "known", "model_calls": 0, "tokens": 0, "wall_seconds": 0, "reason": None}
        self.error("INVALID_USAGE", a.validate_attempt, attempt, task=task)

    def test_unknown_attempt_can_retain_only_observation_backed_known_usage(self):
        task = self.task()
        attempt = attempt_fixture(task)
        attempt.update(status="unknown", finished_at=None)
        attempt["observed_usage"] = {"status": "known", "model_calls": 5, "tokens": 2500, "wall_seconds": 150, "reason": None}
        self.assertEqual(a.validate_attempt(attempt, task=task)["observed_usage"], attempt["observed_usage"])
        attempt["observation"] = None
        self.error("MISSING_OBSERVATION", a.validate_attempt, attempt, task=task)

    def test_failed_blocked_and_unknown_results_require_causes(self):
        result = result_fixture(self.task())
        result.update(outcome="failed", next_action="repair")
        self.error("MISSING_FAILURE", self.result, result)
        result["failures"] = [failure_fixture()]
        result["findings"] = [finding_fixture()]
        self.result(result)
        result["outcome"] = "blocked"
        self.result(result)
        result["outcome"] = "completed"
        self.error("OUTCOME_MISMATCH", self.result, result)
        result = result_fixture(self.task())
        result.update(outcome="unknown", next_action="stop", uncertainty=[])
        self.error("MISSING_UNCERTAINTY", self.result, result)

    def test_findings_and_failures_bind_criteria_and_exact_evidence(self):
        result = result_fixture(self.task())
        result["findings"] = [finding_fixture()]
        self.result(result)
        for field, replacement, code in (
            ("severity", "approve", "INVALID_ENUM"), ("path", "../escape", "UNSAFE_PATH"),
            ("message", "", "INVALID_TEXT"), ("acceptance_ids", ["foreign"], "UNKNOWN_CRITERION"),
            ("evidence", [{"id": "behavior-contract", "sha256": "f" * 64}], "EVIDENCE_MISMATCH"),
        ):
            changed = deepcopy(result)
            changed["findings"][0][field] = replacement
            self.error(code, self.result, changed)
        result["findings"].append(finding_fixture())
        self.error("DUPLICATE_VALUE", self.result, result)
        result = result_fixture(self.task())
        result["evidence"][0]["sha256"] = "f" * 64
        self.error("EVIDENCE_MISMATCH", self.result, result)

    def test_reservation_and_observation_timestamp_rules(self):
        task = self.task()
        attempt = attempt_fixture(task)
        attempt["finished_at"] = "2029-10-01T00:00:00Z"
        self.error("INVALID_ATTEMPT", a.validate_attempt, attempt, task=task)
        attempt = attempt_fixture(task)
        attempt["status"] = "reserved"
        self.error("INVALID_ATTEMPT", a.validate_attempt, attempt, task=task)
        attempt = attempt_fixture(task)
        attempt["observation"] = None
        self.error("MISSING_OBSERVATION", a.validate_attempt, attempt, task=task)
        attempt = attempt_fixture(task)
        attempt["ordinal"] = task["allowance"]["max_attempts"] + 1
        self.error("INVALID_BOUND", a.validate_attempt, attempt, task=task)

    def test_unknown_fields_versions_permissions_and_missing_criteria_fail(self):
        task = self.task()
        validators = (
            (task_fixture(), self.task),
            (attempt_fixture(task), lambda value: a.validate_attempt(value, task=task)),
            (result_fixture(task), self.result),
            (finding_fixture(), a.validate_finding),
            (failure_fixture(), a.validate_failure),
        )
        for value, validate in validators:
            changed = deepcopy(value)
            changed["schema_version"] = "future.v999"
            self.error("UNSUPPORTED_SCHEMA", validate, changed)
            for field in ("approved", "authority", "credentials", "admitted"):
                changed = deepcopy(value)
                changed[field] = True
                self.error("INVALID_FIELDS", validate, changed)
        value = task_fixture()
        value["acceptance_ids"] = ["foreign"]
        self.error("UNKNOWN_CRITERION", self.task, value)
        value["acceptance_ids"] = []
        self.error("INVALID_LIST", self.task, value)
        value = task_fixture()
        value["dependencies"] = [value["binding"]["task_id"]]
        self.error("INVALID_DEPENDENCY", self.task, value)


if __name__ == "__main__":
    unittest.main()
