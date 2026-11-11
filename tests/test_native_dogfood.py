"""Verify that engineering self-checks exercise the core without inventing user acceptance."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import dogfood_native_factory as dogfood


ROOT = Path(__file__).resolve().parents[1]


class DogfoodTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="native dogfood ", dir=ROOT / "tests")
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)
        self.repo = self.base / "synthetic repo"
        scripts = self.repo / "plugins" / "sparkforge" / "scripts"
        scripts.mkdir(parents=True)
        shutil.copyfile(ROOT / "plugins" / "sparkforge" / "scripts" / "factory.py", scripts / "factory.py")
        (self.repo / "specs").mkdir()
        spec = json.loads((ROOT / "specs" / "native-factory-selfcheck.json").read_text(encoding="utf-8"))
        spec["controlled_files"] = ["component.py"]
        spec["checks"] = [{
            "id": "core-contracts",
            "argv": ["python", "-B", "component.py"],
            "timeout_seconds": 5, "output_limit_bytes": 4096,
            "max_attempts": 1, "required_markers": ["SYNTHETIC-CHECK-COMPLETE"],
            "retain_output": False,
        }]
        self.spec_path = self.repo / "specs" / "native-factory-selfcheck.json"
        self.spec_path.write_text(json.dumps(spec), encoding="utf-8")
        self.component = self.repo / "component.py"
        self.component.write_text("print('SYNTHETIC-CHECK-COMPLETE')\n", encoding="utf-8")
        self.job = self.base / "owned job"

    def test_explicit_engineering_confirmation_precedes_all_operations(self) -> None:
        with patch.object(dogfood, "load_factory", side_effect=AssertionError("must not load without confirmation")):
            with self.assertRaises(ValueError):
                dogfood.run_dogfood(self.repo, self.job)
        self.assertFalse(self.job.exists())

    def test_real_checks_run_but_no_reviewer_or_human_acceptance_is_fabricated(self) -> None:
        report = dogfood.run_dogfood(self.repo, self.job, confirm_engineering_test=True)
        self.assertEqual(report["result"], "CHECKS_PASSED_REVIEW_PENDING")
        self.assertEqual(report["job_status"], "REVIEW_PENDING")
        self.assertTrue(report["approval_is_synthetic"])
        self.assertFalse(report["reviewer_decision_fabricated"])
        self.assertEqual(report["human_acceptance"], "NOT_ASSESSED")
        self.assertFalse(report["native_model_workflow_executed"])
        self.assertFalse(report["publication_authorized"])
        core = dogfood.load_factory(self.repo)
        self.assertEqual(core.job_status(self.job)["review_count"], 0)
        self.assertEqual(report["checks"][0]["exit_code"], 0)
        self.assertNotIn("retained_output", report["checks"][0])

    def test_failed_behavior_is_not_a_successful_selfcheck(self) -> None:
        self.component.write_text("print('Incorrect behavior')\n", encoding="utf-8")
        report = dogfood.run_dogfood(self.repo, self.job, confirm_engineering_test=True)
        self.assertEqual(report["result"], "NOT_PASSED")
        self.assertEqual(report["checks"][0]["reason"], "REQUIRED_OUTPUT_MISSING")
        self.assertEqual(report["human_acceptance"], "NOT_ASSESSED")

    def test_existing_job_is_never_overwritten_or_reused(self) -> None:
        self.job.mkdir()
        sentinel = self.job / "unrelated.txt"
        sentinel.write_text("Preserve me.", encoding="utf-8")
        with self.assertRaises(ValueError) as caught:
            dogfood.run_dogfood(self.repo, self.job, confirm_engineering_test=True)
        self.assertEqual(getattr(caught.exception, "code", None), "JOB_EXISTS")
        self.assertEqual(sentinel.read_text(encoding="utf-8"), "Preserve me.")
        self.assertEqual(set(self.job.iterdir()), {sentinel})

    def test_non_development_environment_is_rejected_before_job_creation(self) -> None:
        spec = json.loads(self.spec_path.read_text(encoding="utf-8"))
        spec["environment"] = "CORP"
        self.spec_path.write_text(json.dumps(spec), encoding="utf-8")
        with self.assertRaises(ValueError):
            dogfood.run_dogfood(self.repo, self.job, confirm_engineering_test=True)
        self.assertFalse(self.job.exists())

    def test_foreign_spec_cannot_use_the_synthetic_decision_harness(self) -> None:
        spec = json.loads(self.spec_path.read_text(encoding="utf-8"))
        spec["id"] = "Unrelated-work"
        self.spec_path.write_text(json.dumps(spec), encoding="utf-8")
        with self.assertRaises(ValueError):
            dogfood.run_dogfood(self.repo, self.job, confirm_engineering_test=True)
        self.assertFalse(self.job.exists())

    def test_cli_without_confirmation_is_blocked_and_creates_nothing(self) -> None:
        result = subprocess.run(
            [sys.executable, "-B", str(ROOT / "scripts" / "dogfood_native_factory.py"), "--job-dir", str(self.job)],
            capture_output=True, text=True, timeout=10, check=False,
        )
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertEqual(json.loads(result.stdout)["result"], "BLOCKED")
        self.assertFalse(self.job.exists())


if __name__ == "__main__":
    unittest.main()
