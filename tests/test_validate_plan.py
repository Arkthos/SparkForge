"""Synthetic tests of the planning validator; no product or provider execution."""

from __future__ import annotations

import csv
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import validate_plan as plan


class FixtureCase(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="plan-check-", dir=Path(__file__).parent)
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name) / "repo"
        self.root.mkdir()
        self.requirements = [f"SF-{number:02d}" for number in range(1, 22)]
        self.requirements += [f"NFR-{number:02d}" for number in range(1, 11)]
        for name in plan.REQUIRED:
            self.write(name, "{}\n" if name.endswith(".json") else "# Fixture\n")
        self.write("README.md", "# Fixture\nLocal test with no configured remote.\n")
        self.write("docs/PRODUCT_REQUIREMENTS.md", "# Requirements\n" + "".join(f"| {identifier} | Fixture |\n" for identifier in self.requirements))
        self.write("docs/PROJECT_STATUS.md", "# Status\n\n**Product implementation:** not started.\n\n**Local plugin acceptance:** NOT_ASSESSED.\n")
        self.write("docs/ROADMAP.md", "# Roadmap\n" + "".join(f"| P{number}: fixture | Proposed |\n" for number in range(9)))
        self.write("docs/engineering/TEST_STRATEGY.md", "# Strategy\n**31 planned scenarios**\n")
        self.write("docs/design/CONTRACTS.md", "# Contracts\n\n## C-001: fixture\n\n**Requirements:** " + ", ".join(self.requirements) + "\n**Decisions:** D-001.\n")
        self.write("docs/design/DECISIONS.md", "# Decisions\n\n## D-001: fixture\n\n**Requirements:** SF-01.\n")
        self.write("docs/IMPLEMENTATION_PLAN.md", "# Plan\n\n### WP-000: draft\n\n### WP-001: approval\n\n### WP-080: local deliverable\n")
        self.work = []
        for identifier, dependency in (("WP-000", ""), ("WP-001", "WP-000"), ("WP-080", "WP-001")):
            row = {key: "Fixture" for key in plan.BACKLOG_COLUMNS}
            row.update(
                id=identifier, milestone="P0" if identifier != "WP-080" else "P7",
                status="not_started", depends_on=dependency,
                requirements=";".join(self.requirements), validation="TC-001..TC-031",
            )
            self.work.append(row)
        self.cases = []
        for number, requirement in enumerate(self.requirements, 1):
            row = {key: "Fixture" for key in plan.TEST_COLUMNS}
            row.update(test_id=f"TC-{number:03d}", requirements=requirement, level="documentation", gate="P0")
            self.cases.append(row)
        self.save_csv()
        self.cycle = {
            "schema_version": "sparkforge-engineering-cycle.v1",
            "id": "ENG-20261105-fixture",
            "date": "2026-11-05",
            "work_items": ["WP-000"],
            "workstream": "planning",
            "cycle_type": "governance",
            "status": "validated",
            "objective": "Synthetic planning fixture.",
            "changes": ["Fixture"],
            "validation": [{"check": "Fixture", "scope": "documentation", "outcome": "PASS", "reference": "Fixture"}],
            "results": ["Fixture"],
            "limitations": ["Not product acceptance."],
            "rollback": "Remove owned fixture.",
            "next_steps": ["Fixture"],
            "evidence": ["docs/VALIDATION_HISTORY.md"],
            "public_safe": False,
        }
        self.cycle_path = f"{plan.CYCLE_DIRECTORY}/ENG-20261105-fixture.json"
        self.write(self.cycle_path, json.dumps(self.cycle))

    def write(self, name: str, content: str) -> None:
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def save_csv(self) -> None:
        for name, columns, rows in (
            ("docs/IMPLEMENTATION_BACKLOG.csv", plan.BACKLOG_COLUMNS, self.work),
            ("docs/engineering/ACCEPTANCE_MATRIX.csv", plan.TEST_COLUMNS, self.cases),
        ):
            with (self.root / name).open("w", encoding="utf-8", newline="") as stream:
                writer = csv.DictWriter(stream, fieldnames=columns)
                writer.writeheader()
                writer.writerows(rows)

    def errors(self, base: str | None = None) -> str:
        return "\n".join(plan.validate(self.root, base).errors)


class PlanValidationTests(FixtureCase):
    def test_complete_fixture(self) -> None:
        report = plan.validate(self.root)
        self.assertEqual(report.errors, [])
        self.assertEqual(report.counts["requirements"], 31)

    def test_unknown_requirement(self) -> None:
        self.cases[0]["requirements"] = "SF-99"
        self.save_csv()
        self.assertIn("unknown requirements", self.errors())

    def test_requirement_coverage(self) -> None:
        self.cases[-1]["requirements"] = "SF-01"
        self.save_csv()
        self.assertIn("Matrix missing requirement coverage", self.errors())

    def test_duplicate_test_id(self) -> None:
        self.cases.append(self.cases[0].copy())
        self.save_csv()
        self.assertIn("Duplicate ID: TC-001", self.errors())

    def test_unknown_dependency(self) -> None:
        self.work[1]["depends_on"] = "WP-999"
        self.save_csv()
        self.assertIn("unknown dependency WP-999", self.errors())

    def test_dependency_cycle(self) -> None:
        self.work[0]["depends_on"] = "WP-080"
        self.save_csv()
        self.assertIn("Dependency cycle", self.errors())

    def test_done_requires_done_dependencies(self) -> None:
        self.work[1]["status"] = "done"
        self.save_csv()
        self.assertIn("done before prerequisite", self.errors())

    def test_in_progress_requires_completed_prerequisites(self) -> None:
        self.work[1]["status"] = "in_progress"
        self.save_csv()
        self.assertIn("in_progress before prerequisite WP-000", self.errors())

    def test_awaiting_approval_requires_completed_prerequisites(self) -> None:
        self.work[1]["status"] = "awaiting_approval"
        self.save_csv()
        self.assertIn("awaiting_approval before prerequisite WP-000", self.errors())

    def test_independent_work_can_share_a_completed_prerequisite(self) -> None:
        self.work[0]["status"] = "done"
        self.work[1]["status"] = "done"
        for identifier in ("WP-015", "WP-016"):
            row = self.work[2].copy()
            row.update(id=identifier, milestone="P1", status="in_progress", depends_on="WP-001")
            self.work.append(row)
        report = plan.Report()
        plan.check_dependencies({row["id"]: row for row in self.work}, report)
        self.assertEqual(report.errors, [])

    def test_deferred_transfer_cannot_block_local_delivery(self) -> None:
        row = self.work[0].copy()
        row.update(id="WP-090", milestone="P8", status="deferred", depends_on="")
        self.work.append(row)
        self.work[2]["depends_on"] = "WP-090"
        self.save_csv()
        self.assertIn("incorrectly depends on deferred", self.errors())

    def test_empty_csv_field(self) -> None:
        self.cases[0]["evidence"] = ""
        self.save_csv()
        self.assertIn("empty evidence", self.errors())

    def test_invalid_gate_and_level(self) -> None:
        self.cases[0].update(gate="P9", level="pretend_live")
        self.save_csv()
        result = self.errors()
        self.assertIn("invalid gate", result)
        self.assertIn("invalid level", result)

    def test_extra_csv_column(self) -> None:
        with (self.root / "docs/engineering/ACCEPTANCE_MATRIX.csv").open("a", encoding="utf-8") as stream:
            stream.write("TC-032,SF-01,unit,case,result,evidence,P0,owner,extra\n")
        self.assertIn("wrong column count", self.errors())

    def test_unmapped_case(self) -> None:
        for row in self.work:
            row["validation"] = "TC-001..TC-030"
        self.save_csv()
        self.assertIn("Matrix tests have no work package: ['TC-031']", self.errors())

    def test_unknown_and_reversed_test_range(self) -> None:
        self.work[0]["validation"] = "TC-999;TC-010..TC-001"
        self.save_csv()
        result = self.errors()
        self.assertIn("unknown tests", result)
        self.assertIn("Reversed test range", result)

    def test_unknown_markdown_reference(self) -> None:
        self.write("docs/EXTRA.md", "# Extra\nC-999 is not defined.\n")
        self.assertIn("unknown references ['C-999']", self.errors())

    def test_contract_header_coverage(self) -> None:
        self.write("docs/design/CONTRACTS.md", "# Contracts\n## C-001: fixture\n**Requirements:** SF-01.\n**Decisions:** D-001.\n")
        self.assertIn("Contracts missing requirement coverage", self.errors())

    def test_missing_plan_section(self) -> None:
        self.write("docs/IMPLEMENTATION_PLAN.md", "# Plan\n### WP-000: draft\n")
        self.assertIn("Plan work-package sections differ", self.errors())

    def test_missing_file_and_local_link(self) -> None:
        (self.root / "docs/design/ARCHITECTURE.md").unlink()
        self.write("README.md", "# Fixture\n[Missing](docs/design/ARCHITECTURE.md)\n")
        result = self.errors()
        self.assertIn("Required file missing", result)
        self.assertIn("missing local link", result)

    def test_duplicate_headings_and_code_fences(self) -> None:
        self.write("README.md", "# Fixture\n## Example\n## Example\n[Second](#example-1)\n```text\n[Not a link](absent.md)\nC-999\n```\n")
        self.assertEqual(self.errors(), "")

    def test_missing_anchor(self) -> None:
        self.write("README.md", "# Fixture\n[Missing](#not-present)\n")
        self.assertIn("missing anchor", self.errors())

    def test_missing_image_is_a_link_failure(self) -> None:
        self.write("README.md", "# Fixture\n![Missing](missing-image.png)\n")
        self.assertIn("missing local link", self.errors())

    def test_malformed_url_is_reported(self) -> None:
        self.write("README.md", "# Fixture\n[Bad](https://[broken)\n")
        self.assertIn("malformed link", self.errors())

    def test_link_cannot_escape_approved_roots(self) -> None:
        (self.root.parent / "outside.md").write_text("# Outside\n", encoding="utf-8")
        self.write("README.md", "# Fixture\n[Outside](../outside.md)\n")
        self.assertIn("escapes approved roots", self.errors())

    def test_sibling_docs_are_development_inputs(self) -> None:
        sibling = self.root.parent / "docs"
        sibling.mkdir()
        (sibling / "source.md").write_text("# Source\n", encoding="utf-8")
        self.write("README.md", "# Fixture\n[Source](../docs/source.md#source)\n")
        self.assertEqual(self.errors(), "")

    def test_wrong_documented_scenario_count(self) -> None:
        self.write("docs/engineering/TEST_STRATEGY.md", "# Strategy\n**88 planned scenarios**\n")
        self.assertIn("scenario count differs", self.errors())

    def test_implementation_cannot_advance_without_baseline(self) -> None:
        self.work[2]["status"] = "in_progress"
        self.save_csv()
        self.assertIn("execution advanced before baseline approval", self.errors())

    def test_false_local_readiness_claim(self) -> None:
        self.write("docs/PROJECT_STATUS.md", "# Status\n**Product implementation:** not started.\n**Local plugin acceptance:** PASS.\n")
        self.assertIn("retain NOT_ASSESSED", self.errors())

    def test_invalid_json_and_cycle_date(self) -> None:
        self.write("docs/research/self-improvement-sources.json", "{bad")
        self.cycle["date"] = "2026-11-06"
        self.write(self.cycle_path, json.dumps(self.cycle))
        result = self.errors()
        self.assertIn("invalid JSON", result)
        self.assertIn("date mismatch", result)

    def test_validated_cycle_cannot_hide_pending(self) -> None:
        self.cycle["validation"][0]["outcome"] = "PENDING"
        self.write(self.cycle_path, json.dumps(self.cycle))
        self.assertIn("validated cycle has unresolved checks", self.errors())

    def test_invalid_cycle_scalar_types_do_not_crash(self) -> None:
        self.cycle["status"] = ["validated"]
        self.cycle["validation"][0]["outcome"] = {"claim": "PASS"}
        self.write(self.cycle_path, json.dumps(self.cycle))
        result = self.errors()
        self.assertIn("invalid status", result)
        self.assertIn("invalid outcome", result)

    def test_missing_validator_is_reported(self) -> None:
        (self.root / "scripts/validate_plan.py").unlink()
        self.assertIn("Required file missing: scripts/validate_plan.py", self.errors())

    def test_cycle_unknown_work_and_boolean_privacy(self) -> None:
        self.cycle.update(work_items=["WP-999"], public_safe="false")
        self.write(self.cycle_path, json.dumps(self.cycle))
        result = self.errors()
        self.assertIn("unknown work item", result)
        self.assertIn("public_safe must be boolean", result)

    def test_read_failure_is_reported(self) -> None:
        report = plan.Report()
        self.assertEqual(plan.read_text(self.root / "absent.md", report), "")
        self.assertTrue(report.errors)

    def test_git_failure_is_reported(self) -> None:
        report = plan.Report()
        with patch.object(plan, "git_lines", side_effect=RuntimeError("Synthetic Git failure")):
            plan.check_git(self.root, "HEAD", report)
        self.assertIn("Synthetic Git failure", report.errors)


class GitLifecycleTests(FixtureCase):
    def git(self, *arguments: str) -> None:
        environment = dict(os.environ, GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull)
        result = subprocess.run(
            [
                "git", "-C", str(self.root),
                "-c", "user.name=Planning Fixture",
                "-c", "user.email=fixture@example.invalid",
                "-c", "commit.gpgsign=false",
                "-c", f"core.hooksPath={self.root / 'no-fixture-hooks'}",
                *arguments,
            ],
            env=environment, capture_output=True, text=True, check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def setUp(self) -> None:
        super().setUp()
        self.git("init", "--quiet")
        self.git("add", "--all")
        self.git("commit", "--quiet", "-m", "Synthetic planning fixture")

    def test_clean_baseline(self) -> None:
        self.assertEqual(self.errors("HEAD"), "")

    def test_missing_living_records_and_cycle(self) -> None:
        self.write("docs/NEW.md", "# New\n")
        result = self.errors("HEAD")
        self.assertIn("missing living records", result)
        self.assertIn("requires a new append-only cycle", result)

    def test_historical_cycle_modification(self) -> None:
        self.cycle["results"] = ["Changed history"]
        self.write(self.cycle_path, json.dumps(self.cycle))
        self.assertIn("Historical cycle modified/deleted", self.errors("HEAD"))

    def test_historical_cycle_deletion(self) -> None:
        (self.root / self.cycle_path).unlink()
        self.assertIn("Historical cycle modified/deleted", self.errors("HEAD"))

    def test_staged_history_change_cannot_hide_behind_restored_worktree(self) -> None:
        original = (self.root / self.cycle_path).read_text(encoding="utf-8")
        self.cycle["results"] = ["Staged historical rewrite"]
        self.write(self.cycle_path, json.dumps(self.cycle))
        self.git("add", self.cycle_path)
        self.write(self.cycle_path, original)
        self.assertIn("Historical cycle modified/deleted", self.errors("HEAD"))

    def test_coherent_boundary(self) -> None:
        for name in plan.LIVING - {"docs/IMPLEMENTATION_BACKLOG.csv"}:
            path = self.root / name
            path.write_text(path.read_text(encoding="utf-8") + "\nUpdated evidence.\n", encoding="utf-8")
        self.work[0]["title"] = "Updated fixture"
        self.save_csv()
        self.cycle["id"] = "ENG-20261105-fixture-next"
        self.write(f"{plan.CYCLE_DIRECTORY}/ENG-20261105-fixture-next.json", json.dumps(self.cycle))
        self.assertEqual(self.errors("HEAD"), "")
        self.git("add", "--all")
        self.git("commit", "--quiet", "-m", "Synthetic coherent boundary")
        self.assertEqual(self.errors("HEAD~"), "")

    def test_remote_contradicts_local_only_claim(self) -> None:
        self.git("remote", "add", "fixture", "https://example.invalid/not-used.git")
        self.assertIn("remote exists despite", self.errors("HEAD"))


if __name__ == "__main__":
    unittest.main()
