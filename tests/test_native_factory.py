"""Executable SFS-001 criteria using synthetic actors and real local check processes."""

from __future__ import annotations

import importlib.util
import json
import os
import sqlite3
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "plugins" / "sparkforge" / "scripts" / "factory.py"
module_spec = importlib.util.spec_from_file_location("sparkforge_factory_test", SCRIPT)
factory = importlib.util.module_from_spec(module_spec)
module_spec.loader.exec_module(factory)


def spec_fixture() -> dict:
    return {
        "schema_version": "sparkforge.spec.v1",
        "id": "SFS-fixture",
        "title": "Synthetic spec-driven component",
        "problem": "Produce a component whose check observes the accepted result.",
        "audience": "Synthetic reviewer",
        "environment": "LOCAL_DEVELOPMENT",
        "builder_actor": "fixture-builder",
        "non_goals": ["No external service, install, model or production action."],
        "knowledge": {
            "wiki_revision": "wiki-fixture-r1", "repository_revision": "repo-fixture-r1",
            "coverage": "SNAPSHOT_SCOPE", "limitations": ["Entirely synthetic source references."],
            "citations": [
                {"source": "wiki", "locator": "fixture:wiki", "revision": "wiki-fixture-r1", "sha256": "a" * 64},
                {"source": "repository", "locator": "fixture:repo", "revision": "repo-fixture-r1", "sha256": "b" * 64},
            ],
        },
        "reuse": {
            "decision": "UPDATE_EXISTING", "target": "fixture-component",
            "rationale": "Improve the supplied synthetic component instead of inventing another.",
            "inspected_candidates": ["fixture-component"],
        },
        "controlled_files": ["component.py"],
        "acceptance": [{"id": "A1", "behavior": "The component emits the expected marker.", "checks": ["behavior"]}],
        "checks": [{
            "id": "behavior", "argv": ["python", "-I", "-B", "component.py"],
            "timeout_seconds": 5, "output_limit_bytes": 4096,
            "max_attempts": 3, "required_markers": ["EXPECTED-BEHAVIOR"],
            "retain_output": False,
        }],
        "required_reviewers": ["quality"],
    }


class FixtureCase(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="native factory ", dir=ROOT / "tests")
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)
        self.workspace = self.base / "workspace with spaces"
        self.workspace.mkdir()
        self.job = self.base / "job"
        self.spec = spec_fixture()
        self.component = self.workspace / "component.py"
        self.component.write_text("print('EXPECTED-BEHAVIOR')\n", encoding="utf-8")

    def init(self, *, approve: bool = True) -> dict:
        report = factory.init_job(self.spec, self.workspace, self.job)
        if approve:
            report = factory.decide(self.job, report["spec_sha"], "accept", "fixture-operator")
        return report

    def run_check(self, identifier: str = "behavior") -> dict:
        return factory.run_check(self.job, identifier, confirm_run=True)

    def error(self, code: str, function, *args, **kwargs) -> None:
        with self.assertRaises(factory.FactoryError) as caught:
            function(*args, **kwargs)
        self.assertEqual(caught.exception.code, code)

    def review(self, *, decision: str = "pass", actor: str = "fixture-reviewer") -> dict:
        current = factory.job_status(self.job)
        return factory.record_review(
            self.job, current["candidate_sha"], "quality", decision, actor,
            "Synthetic reviewer assertion, not an actual human acceptance decision.",
            review_context=current["review_context"],
        )


class SpecTests(FixtureCase):
    def test_strict_spec_validates_without_mutation_or_approval(self) -> None:
        original = deepcopy(self.spec)
        value = factory.validate_spec(self.spec)
        self.assertEqual(value, original)
        self.assertIsNot(value, self.spec)
        self.assertEqual(factory.digest(value), factory.digest(original))

    def test_unknown_or_missing_fields_cannot_grant_authority(self) -> None:
        for field in ("approved", "allow_all_tools", "execution_authorized"):
            value = deepcopy(self.spec)
            value[field] = True
            self.error("INVALID_SPEC", factory.validate_spec, value)
        value = deepcopy(self.spec)
        del value["acceptance"]
        self.error("INVALID_SPEC", factory.validate_spec, value)

    def test_source_revision_and_two_source_kinds_are_required(self) -> None:
        value = deepcopy(self.spec)
        value["knowledge"]["citations"][0]["revision"] = "foreign"
        self.error("FOREIGN_SOURCE_REVISION", factory.validate_spec, value)
        value = deepcopy(self.spec)
        value["knowledge"]["citations"].pop()
        self.error("KNOWLEDGE_NOT_ASSESSED", factory.validate_spec, value)

    def test_missing_coverage_or_reuse_does_not_become_new_component(self) -> None:
        value = deepcopy(self.spec)
        value["knowledge"]["coverage"] = "NOT_ASSESSED"
        self.error("KNOWLEDGE_NOT_ASSESSED", factory.validate_spec, value)
        value = deepcopy(self.spec)
        value["reuse"]["decision"] = ""
        self.error("REUSE_DECISION_MISSING", factory.validate_spec, value)

    def test_empty_criteria_or_unlinked_checks_fail(self) -> None:
        value = deepcopy(self.spec)
        value["acceptance"] = []
        self.error("INVALID_SPEC", factory.validate_spec, value)
        value = deepcopy(self.spec)
        value["acceptance"][0]["checks"] = ["foreign"]
        self.error("INVALID_SPEC", factory.validate_spec, value)

    def test_duplicate_check_criterion_and_reviewer_ids_fail(self) -> None:
        for field in ("checks", "acceptance", "required_reviewers"):
            value = deepcopy(self.spec)
            value[field].append(deepcopy(value[field][0]))
            self.error("INVALID_SPEC", factory.validate_spec, value)

    def test_explicit_bounds_reject_boolean_unlimited_and_nonfinite(self) -> None:
        for field, values in (
            ("timeout_seconds", [True, 0, -1, float("inf"), float("nan"), 3601, "10"]),
            ("output_limit_bytes", [True, 0, -1, "100", 17 * 1024 * 1024]),
            ("max_attempts", [True, 0, -1, "2", 21]),
            ("retain_output", ["false", 0, None]),
        ):
            for value in values:
                with self.subTest(field=field, value=value):
                    spec = deepcopy(self.spec)
                    spec["checks"][0][field] = value
                    self.error("INVALID_SPEC", factory.validate_spec, spec)

    def test_unsafe_controlled_paths_and_aliases_fail(self) -> None:
        for name in ("../outside.py", r"C:\outside.py", "/root.py", "file:stream", ".git/config", ".env", "folder//file", "CON", "folder./file"):
            with self.subTest(name=name):
                value = deepcopy(self.spec)
                value["controlled_files"] = [name]
                self.error("UNSAFE_PATH", factory.validate_spec, value)
        self.spec["controlled_files"] = ["component.py", "COMPONENT.py"]
        self.error("UNSAFE_PATH", factory.validate_spec, self.spec)

    def test_no_unknown_executable_lookup_or_shell_interpolation(self) -> None:
        for executable in ("node", "powershell", "echo expected", "$(command)", "../runner"):
            value = deepcopy(self.spec)
            value["checks"][0]["argv"][0] = executable
            self.error("INVALID_SPEC", factory.validate_spec, value)

    def test_duplicate_json_and_nonfinite_input_fail(self) -> None:
        path = self.base / "bad.json"
        for text, expected in (
            ('{"approved": false, "approved": true}', "DUPLICATE_JSON_KEY"),
            ('{"number": NaN}', "INVALID_JSON"),
            ('{"broken":', "INVALID_JSON"),
        ):
            path.write_text(text, encoding="utf-8")
            self.error(expected, factory.load_json, path)

    def test_raw_input_limit_is_enforced(self) -> None:
        path = self.base / "large.json"
        path.write_text("x" * 129, encoding="utf-8")
        with patch.object(factory, "MAX_JSON_BYTES", 128):
            self.error("INPUT_TOO_LARGE", factory.load_json, path)


class LifecycleTests(FixtureCase):
    def test_proposal_does_not_approve_or_run_anything(self) -> None:
        report = self.init(approve=False)
        self.assertEqual(report["status"], "AWAITING_APPROVAL")
        self.assertIsNone(report["decision"])
        self.error("APPROVAL_REQUIRED", self.run_check)
        self.assertEqual(len(factory.history(self.job)), 1)

    def test_stale_rejected_and_changes_decisions_block_checks(self) -> None:
        initial = self.init(approve=False)
        self.error("STALE_SPEC", factory.decide, self.job, "f" * 64, "accept", "fixture-operator")
        for decision in ("reject", "changes"):
            report = factory.decide(self.job, initial["spec_sha"], decision, "fixture-operator")
            self.assertFalse(report["publication_authorized"])
            self.error("APPROVAL_REQUIRED", self.run_check)

    def test_accepted_spec_still_requires_explicit_command_execution(self) -> None:
        self.init()
        self.error("EXECUTION_CONFIRMATION_REQUIRED", factory.run_check, self.job, "behavior")
        self.assertEqual(factory.job_status(self.job)["attempt_count"], 0)

    def test_job_does_not_adopt_existing_state_or_overlap_candidate(self) -> None:
        self.init(approve=False)
        self.error("JOB_EXISTS", factory.init_job, self.spec, self.workspace, self.job)
        self.error("OVERLAPPING_STATE", factory.init_job, self.spec, self.workspace, self.workspace / "state")

    def test_volume_and_relative_workspaces_are_rejected(self) -> None:
        self.error("UNSAFE_PATH", factory.init_job, self.spec, Path(self.workspace.anchor), self.job)
        self.error("UNSAFE_PATH", factory.init_job, self.spec, Path("relative-workspace"), self.job)
        self.assertFalse(self.job.exists())

    @unittest.skipUnless(os.name == "nt", "Windows network path spelling")
    def test_network_workspace_is_rejected_without_inspecting_it(self) -> None:
        with patch.object(Path, "lstat", side_effect=AssertionError("must not access remote path")):
            self.error("UNSAFE_PATH", factory.init_job, self.spec, Path(r"\\server\share\workspace"), self.job)

    def test_missing_candidate_is_implementation_needed_not_empty_pass(self) -> None:
        self.component.unlink()
        report = self.init()
        self.assertEqual(report["status"], "IMPLEMENTATION_REQUIRED")
        self.error("CANDIDATE_UNAVAILABLE", self.run_check)

    def test_real_command_executes_and_review_stays_separate(self) -> None:
        self.init()
        result = self.run_check()
        self.assertEqual(result["check"]["outcome"], "PASS")
        self.assertEqual(result["check"]["exit_code"], 0)
        self.assertEqual(result["check"]["missing_markers"], [])
        self.assertNotIn("retained_output", result["check"])
        self.assertEqual(result["job"]["status"], "REVIEW_PENDING")
        self.assertEqual(result["check"]["spec_sha"], result["job"]["spec_sha"])
        self.assertEqual(result["check"]["candidate_sha"], result["job"]["candidate_sha"])

    def test_zero_exit_without_expected_behavior_is_not_pass(self) -> None:
        self.component.write_text("print('Wrong result')\n", encoding="utf-8")
        self.init()
        result = self.run_check()
        self.assertEqual(result["check"]["exit_code"], 0)
        self.assertEqual(result["check"]["outcome"], "FAIL")
        self.assertEqual(result["check"]["reason"], "REQUIRED_OUTPUT_MISSING")
        self.assertEqual(result["job"]["status"], "CHECKS_FAILED")

    def test_nonzero_exit_cannot_hide_behind_success_text(self) -> None:
        self.component.write_text("print('EXPECTED-BEHAVIOR')\nraise SystemExit(4)\n", encoding="utf-8")
        self.init()
        result = self.run_check()
        self.assertEqual(result["check"]["outcome"], "FAIL")
        self.assertEqual(result["check"]["reason"], "NONZERO_EXIT")

    def test_required_output_retention_is_an_explicit_spec_choice(self) -> None:
        self.spec["checks"][0]["retain_output"] = True
        self.init()
        self.assertIn("EXPECTED-BEHAVIOR", self.run_check()["check"]["retained_output"])

    def test_missing_review_and_builder_self_review_block_verification(self) -> None:
        self.init()
        self.run_check()
        self.error("SELF_REVIEW", self.review, actor="fixture-builder")
        self.assertEqual(factory.job_status(self.job)["status"], "REVIEW_PENDING")
        for decision in ("changes", "incomplete"):
            self.assertEqual(self.review(decision=decision)["status"], "CHANGES_REQUIRED")

    def test_current_review_produces_only_scoped_candidate_verification(self) -> None:
        self.init()
        self.run_check()
        report = self.review()
        self.assertEqual(report["status"], "CANDIDATE_VERIFIED")
        self.assertTrue(report["human_acceptance_required"])
        self.assertFalse(report["publication_authorized"])
        self.assertFalse(report["host_security_qualified"])
        self.assertEqual(report["approval_authenticity"], "HOST_OR_OPERATOR_RESPONSIBILITY")

    def test_rerunning_evidence_requires_a_fresh_review_even_for_identical_bytes(self) -> None:
        self.init()
        self.run_check()
        self.review()
        result = self.run_check()
        self.assertEqual(result["job"]["status"], "REVIEW_PENDING")
        self.assertEqual(result["job"]["reviews"][0]["decision"], "MISSING")

    def test_delayed_review_cannot_adopt_a_new_same_byte_check_round(self) -> None:
        self.init()
        original = self.run_check()["job"]
        self.run_check()
        self.error(
            "STALE_REVIEW", factory.record_review, self.job, original["candidate_sha"],
            "quality", "pass", "fixture-reviewer", "Review of earlier evidence.",
            review_context=original["review_context"],
        )
        self.assertEqual(factory.job_status(self.job)["status"], "REVIEW_PENDING")

    def test_delayed_review_cannot_adopt_a_new_spec_with_same_candidate_bytes(self) -> None:
        self.init()
        original = self.run_check()["job"]
        changed = deepcopy(self.spec)
        changed["acceptance"][0]["behavior"] += " A new acceptance qualification."
        revised = factory.revise(self.job, changed)
        factory.decide(self.job, revised["spec_sha"], "accept", "fixture-operator")
        self.run_check()
        self.error(
            "STALE_REVIEW", factory.record_review, self.job, original["candidate_sha"],
            "quality", "pass", "fixture-reviewer", "Review of the earlier specification.",
            review_context=original["review_context"],
        )

    def test_a_review_without_caller_captured_context_is_rejected(self) -> None:
        self.init()
        current = self.run_check()["job"]
        self.error(
            "REVIEW_CONTEXT_REQUIRED", factory.record_review, self.job, current["candidate_sha"],
            "quality", "pass", "fixture-reviewer", "No review context supplied.",
        )

    def test_single_field_evidence_corruption_cannot_certify_the_candidate(self) -> None:
        self.init()
        self.run_check()
        self.review()
        connection = sqlite3.connect(self.job / "job.sqlite3")
        original = json.loads(connection.execute("SELECT body FROM state").fetchone()[0])
        cases = [
            ("attempts", "candidate_sha", "c" * 64, "INVALID_EVIDENCE"),
            ("attempts", "exit_code", 7, "INVALID_EVIDENCE"),
            ("attempts", "output_truncated", True, "INVALID_EVIDENCE"),
            ("attempts", "uncertain", True, "INVALID_EVIDENCE"),
            ("attempts", "missing_markers", ["EXPECTED-BEHAVIOR"], "INVALID_EVIDENCE"),
            ("attempts", "argv", ["python", "-c", "print('forged')"], "INVALID_EVIDENCE"),
            ("reviews", "candidate_sha", "c" * 64, "INVALID_REVIEW"),
            ("reviews", "actor", "fixture-builder", "INVALID_REVIEW"),
        ]
        for collection, field, value, code in cases:
            with self.subTest(collection=collection, field=field):
                altered = deepcopy(original)
                altered[collection][0][field] = value
                connection.execute("UPDATE state SET body = ?", (json.dumps(altered),))
                connection.commit()
                self.error(code, factory.job_status, self.job)
        connection.execute("UPDATE state SET body = ?", (json.dumps(original),))
        connection.commit()
        connection.close()
        self.assertEqual(factory.job_status(self.job)["status"], "CANDIDATE_VERIFIED")

    def test_check_counter_rollback_cannot_resurrect_a_stale_review(self) -> None:
        self.init()
        self.run_check()
        self.review()
        self.assertEqual(self.run_check()["job"]["status"], "REVIEW_PENDING")
        connection = sqlite3.connect(self.job / "job.sqlite3")
        state = json.loads(connection.execute("SELECT body FROM state").fetchone()[0])
        state["check_sequence"] = 1
        connection.execute("UPDATE state SET body = ?", (json.dumps(state),))
        connection.commit()
        connection.close()
        self.error("INVALID_JOB", factory.job_status, self.job)

    def test_passing_evidence_requires_the_local_runner_receipt(self) -> None:
        self.init()
        self.run_check()
        self.review()
        connection = sqlite3.connect(self.job / "job.sqlite3")
        original = json.loads(connection.execute("SELECT body FROM state").fetchone()[0])
        for mutation in ("missing-runner", "worker-origin", "bad-runner-digest", "missing-runner-version"):
            with self.subTest(mutation=mutation):
                state = deepcopy(original)
                attempt = state["attempts"][0]
                if mutation == "missing-runner":
                    del attempt["runner"]
                elif mutation == "worker-origin":
                    attempt["origin"] = "WORKER_CLAIM"
                elif mutation == "bad-runner-digest":
                    attempt["runner"]["implementation_sha256"] = "not-a-digest"
                else:
                    del attempt["runner"]["python_version"]
                connection.execute("UPDATE state SET body = ?", (json.dumps(state),))
                connection.commit()
                self.error("INVALID_EVIDENCE", factory.job_status, self.job)
        connection.close()

    def test_unknown_role_and_foreign_candidate_are_not_reviews(self) -> None:
        self.init()
        result = self.run_check()
        self.error(
            "UNKNOWN_REVIEWER", factory.record_review, self.job, result["job"]["candidate_sha"],
            "invented", "pass", "fixture-reviewer", "A synthetic assertion.",
        )
        self.error(
            "STALE_CANDIDATE", factory.record_review, self.job, "d" * 64,
            "quality", "pass", "fixture-reviewer", "A synthetic assertion.",
        )

    def test_candidate_change_invalidates_every_old_result_and_review(self) -> None:
        self.init()
        first = self.run_check()
        self.review()
        self.component.write_text("print('EXPECTED-BEHAVIOR')\n# changed candidate\n", encoding="utf-8")
        report = factory.job_status(self.job)
        self.assertEqual(report["status"], "STALE_CANDIDATE")
        self.assertEqual(report["checks"][0]["outcome"], "NOT_RUN")
        second = self.run_check()
        self.assertNotEqual(first["check"]["round_id"], second["check"]["round_id"])
        self.assertEqual(second["job"]["status"], "REVIEW_PENDING")
        self.assertEqual(second["job"]["attempt_count"], 2)

    def test_failure_repair_and_new_review_are_a_real_end_to_end_slice(self) -> None:
        self.component.write_text("raise AssertionError('seeded synthetic defect')\n", encoding="utf-8")
        self.init()
        failure = self.run_check()
        self.assertEqual(failure["check"]["outcome"], "FAIL")
        self.component.write_text("print('EXPECTED-BEHAVIOR')\n", encoding="utf-8")
        corrected = self.run_check()
        self.assertEqual(corrected["check"]["outcome"], "PASS")
        self.assertNotEqual(failure["check"]["candidate_sha"], corrected["check"]["candidate_sha"])
        self.assertEqual(self.review()["status"], "CANDIDATE_VERIFIED")
        finished = [event for event in factory.history(self.job) if event["kind"] == "CHECK_FINISHED"]
        self.assertEqual([event["payload"]["outcome"] for event in finished], ["FAIL", "PASS"])

    def test_multiple_required_checks_cannot_be_replaced_by_one_green_check(self) -> None:
        second = deepcopy(self.spec["checks"][0])
        second["id"] = "regression"
        self.spec["checks"].append(second)
        self.spec["acceptance"][0]["checks"].append("regression")
        self.init()
        self.assertEqual(self.run_check()["job"]["status"], "CHECKS_PENDING")
        self.error("CHECKS_INCOMPLETE", self.review)
        self.run_check("regression")
        self.assertEqual(self.review()["status"], "CANDIDATE_VERIFIED")

    def test_attempt_allowance_is_not_reset_by_candidate_changes(self) -> None:
        self.spec["checks"][0]["max_attempts"] = 1
        self.init()
        self.run_check()
        self.component.write_text("print('EXPECTED-BEHAVIOR')\n# another candidate\n", encoding="utf-8")
        self.error("ATTEMPT_LIMIT", self.run_check)

    def test_spec_revision_rejects_old_approval_and_preserves_history(self) -> None:
        initial = self.init()
        self.run_check()
        revised = deepcopy(self.spec)
        revised["problem"] += " A materially revised requirement."
        current = factory.revise(self.job, revised)
        self.assertEqual(current["status"], "AWAITING_APPROVAL")
        self.assertNotEqual(current["spec_sha"], initial["spec_sha"])
        self.assertEqual(current["attempt_count"], 1)
        self.error("STALE_SPEC", factory.decide, self.job, initial["spec_sha"], "accept", "fixture-operator")
        self.error("APPROVAL_REQUIRED", self.run_check)

    def test_environment_changes_do_not_inherit_the_old_decision_or_host_claims(self) -> None:
        original = self.init()
        self.assertEqual(original["environment"], "LOCAL_DEVELOPMENT")
        self.assertEqual(original["knowledge_scope"], "SNAPSHOT_SCOPE")
        changed = deepcopy(self.spec)
        changed["environment"] = "ACRO"
        report = factory.revise(self.job, changed)
        self.assertEqual(report["environment"], "ACRO")
        self.assertEqual(report["status"], "AWAITING_APPROVAL")
        self.assertNotEqual(report["spec_sha"], original["spec_sha"])
        self.assertFalse(report["host_security_qualified"])
        self.error("APPROVAL_REQUIRED", self.run_check)

    def test_unchanged_or_foreign_specs_cannot_reset_limits(self) -> None:
        self.init()
        self.error("UNCHANGED_SPEC", factory.revise, self.job, self.spec)
        revised = deepcopy(self.spec)
        revised["id"] = "foreign-job"
        self.error("FOREIGN_SPEC", factory.revise, self.job, revised)

    def test_cancelled_job_cannot_run(self) -> None:
        self.init()
        self.assertEqual(factory.cancel(self.job, "Synthetic operator cancellation.")["status"], "CANCELLED")
        self.error("CANCELLED", self.run_check)

    def test_timeout_remains_uncertain_until_explicit_reconciliation(self) -> None:
        self.component.write_text("import time\ntime.sleep(3)\n", encoding="utf-8")
        self.spec["checks"][0]["timeout_seconds"] = 0.1
        self.init()
        result = self.run_check()
        self.assertEqual(result["check"]["reason"], "TIMEOUT")
        self.assertEqual(result["job"]["status"], "RECONCILIATION_REQUIRED")
        self.error("ACTIVE_EXECUTION", self.run_check)
        self.error("RECONCILIATION_REQUIRED", factory.reconcile, self.job, result["check"]["run_id"], "fixture-operator", "Synthetic single child has stopped.")
        final = factory.reconcile(
            self.job, result["check"]["run_id"], "fixture-operator",
            "This synthetic script spawned no children; its owned process has exited.",
            confirm_stopped=True,
        )
        self.assertEqual(final["status"], "CHECKS_FAILED")
        self.assertEqual(final["attempt_count"], 1)

    def test_output_overflow_cannot_pass_even_with_success_marker(self) -> None:
        self.component.write_text("print('EXPECTED-BEHAVIOR' + 'x'*10000)\n", encoding="utf-8")
        self.spec["checks"][0]["output_limit_bytes"] = 128
        self.init()
        result = self.run_check()
        self.assertEqual(result["check"]["reason"], "OUTPUT_LIMIT")
        self.assertTrue(result["check"]["output_truncated"])
        self.assertEqual(result["job"]["status"], "RECONCILIATION_REQUIRED")
        factory.reconcile(
            self.job, result["check"]["run_id"], "fixture-operator",
            "Synthetic bounded printer completed without descendants.", confirm_stopped=True,
        )

    def test_small_flushed_output_overflow_stops_before_the_timeout(self) -> None:
        self.component.write_text("import time\nprint('x'*217, flush=True)\ntime.sleep(3)\n", encoding="utf-8")
        self.spec["checks"][0].update(output_limit_bytes=128, timeout_seconds=2)
        self.init()
        result = self.run_check()
        self.assertEqual(result["check"]["reason"], "OUTPUT_LIMIT")
        self.assertLess(result["check"]["duration_seconds"], 1.5)
        factory.reconcile(
            self.job, result["check"]["run_id"], "fixture-operator",
            "Synthetic single child was stopped after its flushed output exceeded the allowance.",
            confirm_stopped=True,
        )
    def test_check_that_changes_controlled_bytes_cannot_certify_itself(self) -> None:
        self.component.write_text(
            "from pathlib import Path\n"
            "p=Path(__file__)\np.write_text(p.read_text()+'\\n# mutation\\n')\n"
            "print('EXPECTED-BEHAVIOR')\n",
            encoding="utf-8",
        )
        self.init()
        result = self.run_check()
        self.assertEqual(result["check"]["reason"], "CANDIDATE_CHANGED_DURING_CHECK")
        self.assertEqual(result["check"]["outcome"], "FAIL")
        self.assertEqual(result["job"]["status"], "STALE_CANDIDATE")

    def test_check_cannot_select_an_undeclared_command(self) -> None:
        self.init()
        self.error("UNKNOWN_CHECK", self.run_check, "model-supplied-command")
        self.assertEqual(factory.job_status(self.job)["attempt_count"], 0)

    def test_process_start_failure_is_explicit_and_consumes_one_attempt(self) -> None:
        self.init()
        with patch.object(factory.subprocess, "Popen", side_effect=PermissionError("synthetic denial")):
            result = self.run_check()
        self.assertEqual(result["check"]["outcome"], "ERROR")
        self.assertEqual(result["check"]["reason"], "PermissionError")
        self.assertEqual(result["job"]["attempt_count"], 1)
        self.assertIsNone(result["job"]["active_run"])

    def test_status_is_a_read_only_projection(self) -> None:
        self.init()
        events = factory.history(self.job)
        factory.job_status(self.job)
        factory.job_status(self.job)
        self.assertEqual(events, factory.history(self.job))

    def test_spec_corruption_stops_before_execution(self) -> None:
        self.init()
        connection = sqlite3.connect(self.job / "job.sqlite3")
        state = json.loads(connection.execute("SELECT body FROM state").fetchone()[0])
        state["spec"]["problem"] = "Changed without reapproval."
        connection.execute("UPDATE state SET body = ?", (json.dumps(state),))
        connection.commit()
        connection.close()
        self.error("SPEC_TAMPERED", factory.job_status, self.job)

    def test_malformed_job_containers_fail_explicitly(self) -> None:
        self.init()
        connection = sqlite3.connect(self.job / "job.sqlite3")
        state = json.loads(connection.execute("SELECT body FROM state").fetchone()[0])
        state["attempts"] = "not-a-list"
        connection.execute("UPDATE state SET body = ?", (json.dumps(state),))
        connection.commit()
        connection.close()
        self.error("INVALID_JOB", self.run_check)

    def test_malformed_candidate_state_is_rejected_before_receipt_selection(self) -> None:
        self.init()
        self.run_check()
        connection = sqlite3.connect(self.job / "job.sqlite3")
        original = json.loads(connection.execute("SELECT body FROM state").fetchone()[0])
        for value in ("not-a-manifest", [], 4, {"sha256": "a" * 64, "files": []}):
            with self.subTest(value=value):
                changed = deepcopy(original)
                changed["candidate"] = value
                connection.execute("UPDATE state SET body = ?", (json.dumps(changed),))
                connection.commit()
                self.error("INVALID_JOB", factory.job_status, self.job)
        connection.close()

    def test_run_reservation_prevents_blind_replay_after_interruption(self) -> None:
        self.init()
        with patch.object(factory, "_execute", side_effect=RuntimeError("simulated host interruption")):
            with self.assertRaises(RuntimeError):
                self.run_check()
        status = factory.job_status(self.job)
        self.assertEqual(status["status"], "RUNNING_OR_INTERRUPTED")
        self.error("ACTIVE_EXECUTION", self.run_check)
        self.error("ACTIVE_EXECUTION", factory.revise, self.job, self.spec)
        factory.reconcile(
            self.job, status["active_run"]["run_id"], "fixture-operator",
            "Synthetic interruption happened before the mocked dispatch.", confirm_stopped=True,
        )
        self.assertEqual(factory.job_status(self.job)["status"], "CHECKS_FAILED")

    def test_running_check_observes_cancellation_from_another_client(self) -> None:
        self.component.write_text("import time\ntime.sleep(3)\nprint('EXPECTED-BEHAVIOR')\n", encoding="utf-8")
        self.init()
        result = {}

        def execute() -> None:
            try:
                result.update(self.run_check())
            except BaseException as error:
                result["error"] = error

        thread = threading.Thread(target=execute)
        thread.start()
        deadline = time.monotonic() + 2
        active = None
        while time.monotonic() < deadline:
            try:
                active = factory.job_status(self.job)["active_run"]
                if active and active.get("pid"):
                    break
            except sqlite3.OperationalError:
                pass
            time.sleep(0.02)
        self.assertTrue(active and active.get("pid"))
        factory.cancel(self.job, "Synthetic operator stop during execution.")
        thread.join(timeout=8)
        self.assertFalse(thread.is_alive())
        self.assertNotIn("error", result, result)
        self.assertEqual(result["check"]["reason"], "CANCELLED")
        factory.reconcile(
            self.job, result["check"]["run_id"], "fixture-operator",
            "Synthetic sleeping child terminated; no descendants were spawned.", confirm_stopped=True,
        )
        self.assertEqual(factory.job_status(self.job)["status"], "CANCELLED")


class CliTests(FixtureCase):
    def test_validate_cli_is_structured_and_does_not_approve(self) -> None:
        path = self.base / "spec with spaces.json"
        path.write_text(json.dumps(self.spec), encoding="utf-8")
        result = subprocess.run(
            [sys.executable, "-B", str(SCRIPT), "validate-spec", str(path)],
            capture_output=True, text=True, timeout=10, check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertIs(report["approved"], False)
        self.assertEqual(report["spec_sha"], factory.digest(self.spec))
        self.assertFalse(self.job.exists())

    def test_invalid_cli_and_missing_input_have_nonzero_json(self) -> None:
        for arguments in ([], ["validate-spec", str(self.base / "missing.json")], ["--unknown"]):
            result = subprocess.run(
                [sys.executable, "-B", str(SCRIPT), *arguments],
                capture_output=True, text=True, timeout=10, check=False,
            )
            self.assertEqual(result.returncode, 2, result.stderr)
            self.assertEqual(json.loads(result.stdout)["status"], "BLOCKED")


if __name__ == "__main__":
    unittest.main()
