"""CI must inspect the actual change boundary, never silently validate a clean HEAD."""

import unittest

from scripts.check_repository import ci_base


class CiBoundaryTests(unittest.TestCase):
    def test_push_validates_all_commits_since_before(self):
        before = "a" * 40
        self.assertEqual(ci_base({"before": before, "after": "b" * 40}, "push"), before)

    def test_pull_request_uses_trusted_base_not_title_or_head(self):
        base = "c" * 40
        event = {"pull_request": {"base": {"sha": base}, "title": "$(untrusted)",
                                  "head": {"sha": "d" * 40}}}
        self.assertEqual(ci_base(event, "pull_request"), base)

    def test_manual_run_checks_last_commit(self):
        self.assertEqual(ci_base({}, "workflow_dispatch"), "HEAD~")

    def test_malformed_or_root_boundaries_fail_closed(self):
        for value in (None, "HEAD", "--output=elsewhere", "0" * 40, 123, "f" * 41):
            with self.subTest(value=value), self.assertRaises(ValueError):
                ci_base({"before": value}, "push")
        for event in (None, [], {"pull_request": None}, {"pull_request": {"base": []}}):
            with self.subTest(event=event), self.assertRaises(ValueError):
                ci_base(event, "pull_request")

    def test_unknown_event_cannot_skip_boundary_validation(self):
        with self.assertRaises(ValueError):
            ci_base({}, "pull_request_target")


if __name__ == "__main__":
    unittest.main()
