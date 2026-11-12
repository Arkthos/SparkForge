"""Active plans and immutable historical attribution have different obligations."""

import csv
import hashlib
import io
import json
import unittest

from scripts import validate_plan as plan
from test_validate_plan import FixtureCase


class ArchivePlanTests(FixtureCase):
    def archive_csv(self, name, columns, rows):
        stream = io.StringIO(newline="")
        writer = csv.DictWriter(stream, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)
        self.write("docs/archive/old/" + name, stream.getvalue())

    def disposition(self, **entry):
        self.write("docs/archive/old/dispositions.json", json.dumps({
            "schema_version": 1, "entries": [entry],
        }))

    def test_historical_work_and_scenario_refs_are_attributable(self):
        work = dict(self.work[0], id="WP-777")
        case = dict(self.cases[0], test_id="TC-777")
        self.archive_csv("IMPLEMENTATION_BACKLOG.csv", plan.BACKLOG_COLUMNS, [work])
        self.archive_csv("ACCEPTANCE_MATRIX.csv", plan.TEST_COLUMNS, [case])
        self.cycle["work_items"] = ["WP-777"]
        self.write(self.cycle_path, json.dumps(self.cycle))
        self.write("docs/NOTE.md", "# History\nWP-777 and TC-777 refer to the old baseline.\n")
        self.assertEqual(self.errors(), "")

    def test_archived_task_is_not_an_active_dependency(self):
        self.archive_csv("IMPLEMENTATION_BACKLOG.csv", plan.BACKLOG_COLUMNS,
                         [dict(self.work[0], id="WP-777")])
        self.work[1]["depends_on"] = "WP-777"
        self.save_csv()
        self.assertIn("unknown dependency WP-777", self.errors())

    def test_original_relative_links_are_not_reinterpreted_in_snapshot(self):
        self.write("docs/archive/old/OLD.md", "# Historical\n[Original](missing-now.md)\nWP-777\n")
        self.assertEqual(self.errors(), "")

    def test_active_plugin_link_failure_is_checked(self):
        self.write("plugins/example/README.md", "# Active\n[Missing](absent.md)\n")
        self.assertIn("missing local link", self.errors())

    def test_archive_digest_detects_changed_bytes(self):
        relative = "docs/archive/old/frozen.md"
        self.write(relative, "Original\n")
        sha = hashlib.sha256((self.root / relative).read_bytes()).hexdigest()
        self.disposition(disposition="historical_snapshot", original_path="docs/old.md",
                         archive_path=relative, sha256=sha)
        self.assertEqual(self.errors(), "")
        self.write(relative, "Changed\n")
        self.assertIn("Archived bytes changed or missing", self.errors())

    def test_missing_snapshot_and_reintroduced_preview_are_rejected(self):
        self.disposition(disposition="historical_snapshot", archive_path="docs/archive/old/gone.md",
                         sha256="a" * 64)
        self.assertIn("Archived bytes changed or missing", self.errors())
        self.write("preview/model.js", "retired\n")
        self.disposition(disposition="retired_fictional_preview", original_path="preview/model.js")
        self.assertIn("Retired preview path reintroduced", self.errors())

    def test_archive_paths_cannot_escape_or_target_active_source(self):
        for path in ("../../outside.md", "/outside.md", "README.md"):
            with self.subTest(path=path):
                self.disposition(disposition="historical_snapshot", archive_path=path,
                                 sha256="a" * 64)
                self.assertIn("archive verification failed", self.errors())

    def test_new_scenario_numbering_does_not_recycle_old_meanings(self):
        for index, row in enumerate(self.cases, 101):
            row["test_id"] = f"TC-{index:03d}"
        for row in self.work:
            row["validation"] = "TC-101..TC-131"
        self.save_csv()
        self.assertEqual(self.errors(), "")
        self.cases[-1]["test_id"] = "TC-999"
        self.save_csv()
        self.assertIn("identifiers must be unique and contiguous from 101", self.errors())

    def test_coordinated_plan_does_not_require_legacy_task_names(self):
        self.work[0]["id"] = "WP-100"
        self.work[1].update(id="WP-110", depends_on="WP-100")
        self.work[2].update(id="WP-173", depends_on="WP-110")
        self.cycle["work_items"] = ["WP-100"]
        self.write(self.cycle_path, json.dumps(self.cycle))
        self.write("docs/IMPLEMENTATION_PLAN.md", "# Plan\n### WP-100: baseline\n### WP-110: contracts\n### WP-173: release\n")
        self.save_csv()
        self.assertEqual(self.errors(), "")

    def test_current_release_still_cannot_depend_on_optional_adaptation(self):
        report = plan.Report()
        work = {
            "WP-173": dict(self.work[2], id="WP-173", milestone="P7", depends_on="WP-180"),
            "WP-180": dict(self.work[0], id="WP-180", milestone="P8", status="deferred"),
        }
        plan.check_dependencies(work, report)
        self.assertTrue(any("incorrectly depends on deferred" in e for e in report.errors))


if __name__ == "__main__":
    unittest.main()
