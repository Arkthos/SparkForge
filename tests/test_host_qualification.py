"""Synthetic record checks only; no actual host, credential or provider access."""

from __future__ import annotations

import io
import json
import subprocess
import sys
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch

from scripts import validate_host_qualification as host


ROOT = Path(__file__).parent.parent
FIXTURES = ROOT / "tests" / "fixtures" / "host_qualification"
SCRIPT = ROOT / "scripts" / "validate_host_qualification.py"
CLIENT_FIELDS = (
    "product", "distribution", "launcher", "build", "profile_id",
    "profile_revision", "config_revision", "os", "architecture",
)
BAD_TEXT = (None, True, 1, 1.0, [], {}, "", " ", " padded", "padded ")
VALID_EVIDENCE = {
    "DOCUMENTED": ("DOCUMENTATION_CLAIM", "PINNED_SOURCE_OBSERVATION"),
    "SYNTHETIC_ONLY": ("SYNTHETIC_RESULT",),
    "OBSERVED": ("LIVE_HOST_RESULT",),
    "UNSUPPORTED": (
        "DOCUMENTATION_CLAIM", "PINNED_SOURCE_OBSERVATION", "LIVE_HOST_RESULT",
    ),
}


def fixture(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def at(record: dict, path: tuple):
    value = record
    for part in path:
        value = value[part]
    return value


class ReportCase(unittest.TestCase):
    def check_report(self, report: dict, valid: bool) -> None:
        self.assertEqual(set(report), {
            "scope", "valid", "errors", "blockers", "host_qualified", "execution_authorized",
        })
        self.assertEqual(report["scope"], "record_consistency_only")
        self.assertIs(report["valid"], valid)
        self.assertIs(report["host_qualified"], False)
        self.assertIs(report["execution_authorized"], False)
        self.assertIsInstance(report["errors"], list)
        self.assertIsInstance(report["blockers"], list)
        self.assertEqual(bool(report["errors"]), not valid)
        self.assertTrue(all(isinstance(error, str) for error in report["errors"]))
        for blocker in (
            "RECORD_ORIGIN_NOT_AUTHENTICATED",
            "HOST_QUALIFICATION_NOT_ESTABLISHED",
            "EXECUTION_AUTHORIZATION_NOT_ESTABLISHED",
        ):
            self.assertIn(blocker, report["blockers"])
        self.assertEqual("INPUT_INVALID" in report["blockers"], not valid)

    def invalid(self, record: object, message: str = "") -> None:
        report = host.validate_record(record)
        self.check_report(report, False)
        if message:
            self.assertIn(message, "\n".join(report["errors"]))


class RecordTests(ReportCase):
    def setUp(self) -> None:
        self.record = fixture("selected.json")

    def test_unselected_is_valid_with_explicit_blockers(self) -> None:
        report = host.validate_record(fixture("unselected.json"))
        self.check_report(report, True)
        self.assertIn("CLIENT_UNSELECTED", report["blockers"])
        self.assertTrue(any("NOT_ASSESSED" in blocker for blocker in report["blockers"]))

    def test_selected_observed_claim_has_no_authority(self) -> None:
        self.check_report(host.validate_record(self.record), True)

    def test_empty_capabilities_are_valid_but_unassessed(self) -> None:
        for name in ("selected.json", "unselected.json"):
            with self.subTest(name=name):
                record = fixture(name)
                record["capabilities"] = []
                report = host.validate_record(record)
                self.check_report(report, True)
                self.assertIn("CAPABILITY_INVENTORY_NOT_ASSESSED", report["blockers"])

    def test_selected_can_remain_not_assessed(self) -> None:
        self.record["capabilities"][0].update(status="NOT_ASSESSED", evidence=None)
        report = host.validate_record(self.record)
        self.check_report(report, True)
        self.assertTrue(any("NOT_ASSESSED" in blocker for blocker in report["blockers"]))

    def test_invalid_root_types_do_not_crash(self) -> None:
        for value in (None, True, 0, 1.0, "", [], (), {1: "not a JSON key"}):
            with self.subTest(value=value):
                self.invalid(value, "record:")

    def test_objects_require_all_fields_and_reject_unknown_fields(self) -> None:
        paths = (
            (), ("selection",), ("selection", "client"), ("capabilities", 0),
            ("capabilities", 0, "evidence"), ("capabilities", 0, "evidence", "binding"),
            ("capabilities", 0, "evidence", "binding", "client"),
        )
        for path in paths:
            for key in at(self.record, path):
                with self.subTest(path=path, missing=key):
                    record = deepcopy(self.record)
                    del at(record, path)[key]
                    self.invalid(record, "missing fields")
            with self.subTest(path=path, extra=True):
                record = deepcopy(self.record)
                at(record, path)["unexpected"] = True
                self.invalid(record, "unexpected fields")

    def test_text_fields_reject_wrong_types_empty_and_padded_values(self) -> None:
        paths = [
            ("environment_id",), ("record_revision",), ("selection", "reason"),
            ("capabilities", 0, "id"), ("capabilities", 0, "reason"),
            ("capabilities", 0, "evidence", "reference"),
            ("capabilities", 0, "evidence", "revision"),
        ]
        paths += [("selection", "client", field) for field in CLIENT_FIELDS]
        paths += [
            ("capabilities", 0, "evidence", "binding", field)
            for field in ("environment_id", "record_revision", "capability_id")
        ]
        paths += [
            ("capabilities", 0, "evidence", "binding", "client", field)
            for field in CLIENT_FIELDS
        ]
        for path in paths:
            for value in BAD_TEXT:
                with self.subTest(path=path, value=value):
                    record = deepcopy(self.record)
                    at(record, path[:-1])[path[-1]] = value
                    self.invalid(record, "nonempty string")

    def test_unknown_schema_scope_status_and_evidence_class(self) -> None:
        paths = (
            ("schema_version",), ("scope_type",), ("selection", "status"),
            ("capabilities", 0, "status"), ("capabilities", 0, "evidence", "class"),
        )
        for path in paths:
            for value in (*BAD_TEXT, "UNKNOWN"):
                with self.subTest(path=path, value=value):
                    record = deepcopy(self.record)
                    at(record, path[:-1])[path[-1]] = value
                    self.invalid(record, "expected one of")

    def test_scope_and_version_have_no_fallback(self) -> None:
        for field, variants in (
            ("scope_type", ("JOB", "PROJECT", "PACKAGE", "environment")),
            ("schema_version", (1, "sparkforge-host-qualification.v2")),
        ):
            for value in variants:
                with self.subTest(field=field, value=value):
                    record = deepcopy(self.record)
                    record[field] = value
                    self.invalid(record, field)

    def test_wrong_container_types_are_rejected(self) -> None:
        paths = (
            ("selection",), ("selection", "client"), ("capabilities", 0),
            ("capabilities", 0, "evidence"), ("capabilities", 0, "evidence", "binding"),
            ("capabilities", 0, "evidence", "binding", "client"),
        )
        for path in paths:
            for value in (False, 1, "object", []):
                with self.subTest(path=path, value=value):
                    record = deepcopy(self.record)
                    at(record, path[:-1])[path[-1]] = value
                    self.invalid(record, "expected an object")
        for value in (None, False, 1, "array", {}, ()):
            with self.subTest(capabilities=value):
                record = deepcopy(self.record)
                record["capabilities"] = value
                self.invalid(record, "expected an array")

    def test_selected_requires_client_identity(self) -> None:
        for value in (None, {}):
            with self.subTest(client=value):
                self.record["selection"]["client"] = value
                self.invalid(self.record, "record.selection.client")

    def test_unselected_forbids_an_implicit_client(self) -> None:
        self.record["selection"]["status"] = "UNSELECTED"
        self.invalid(self.record, "UNSELECTED requires null")

    def test_not_assessed_forbids_attached_evidence(self) -> None:
        self.record["capabilities"][0]["status"] = "NOT_ASSESSED"
        self.invalid(self.record, "NOT_ASSESSED requires null")

    def test_assessed_states_require_evidence(self) -> None:
        for status in VALID_EVIDENCE:
            with self.subTest(status=status):
                self.record["capabilities"][0].update(status=status, evidence=None)
                self.invalid(self.record, ".evidence: expected an object")

    def test_compatible_claim_classes_preserve_authority_blockers(self) -> None:
        for status, classes in VALID_EVIDENCE.items():
            for evidence_class in classes:
                with self.subTest(status=status, evidence_class=evidence_class):
                    record = deepcopy(self.record)
                    record["capabilities"][0]["status"] = status
                    record["capabilities"][0]["evidence"]["class"] = evidence_class
                    report = host.validate_record(record)
                    self.check_report(report, True)
                    if status != "OBSERVED":
                        self.assertTrue(any(status in blocker for blocker in report["blockers"]))

    def test_incompatible_classes_cannot_be_promoted(self) -> None:
        classes = (
            "DOCUMENTATION_CLAIM", "PINNED_SOURCE_OBSERVATION", "SYNTHETIC_RESULT",
            "LIVE_HOST_RESULT", "OWNER_DECISION", "EXTERNAL_RECEIPT",
        )
        for status, allowed in VALID_EVIDENCE.items():
            for evidence_class in classes:
                if evidence_class in allowed:
                    continue
                with self.subTest(status=status, evidence_class=evidence_class):
                    record = deepcopy(self.record)
                    record["capabilities"][0]["status"] = status
                    record["capabilities"][0]["evidence"]["class"] = evidence_class
                    self.invalid(record, ".evidence.class")

    def test_unselected_rejects_live_claims_including_unsupported(self) -> None:
        self.record["selection"].update(status="UNSELECTED", client=None)
        self.record["capabilities"][0]["evidence"]["binding"]["client"] = None
        for status in ("OBSERVED", "UNSUPPORTED"):
            with self.subTest(status=status):
                self.record["capabilities"][0]["status"] = status
                self.invalid(self.record, "LIVE_HOST_RESULT requires a selected client")

    def test_unselected_can_retain_documented_or_synthetic_claims(self) -> None:
        for status, evidence_class in (
            ("DOCUMENTED", "DOCUMENTATION_CLAIM"),
            ("SYNTHETIC_ONLY", "SYNTHETIC_RESULT"),
            ("UNSUPPORTED", "PINNED_SOURCE_OBSERVATION"),
        ):
            with self.subTest(status=status):
                record = deepcopy(self.record)
                record["selection"].update(status="UNSELECTED", client=None)
                capability = record["capabilities"][0]
                capability["status"] = status
                capability["evidence"]["class"] = evidence_class
                capability["evidence"]["binding"]["client"] = None
                report = host.validate_record(record)
                self.check_report(report, True)
                self.assertIn("CLIENT_UNSELECTED", report["blockers"])

    def test_duplicate_capability_ids_are_rejected(self) -> None:
        self.record["capabilities"].append(deepcopy(self.record["capabilities"][0]))
        self.invalid(self.record, "duplicate capability identifier")

    def test_stale_foreign_environment_record_and_capability_binding(self) -> None:
        for field in ("environment_id", "record_revision", "capability_id"):
            with self.subTest(field=field):
                record = deepcopy(self.record)
                record["capabilities"][0]["evidence"]["binding"][field] = "foreign-revision"
                self.invalid(record, f".binding.{field}: stale or foreign binding")

    def test_every_client_field_is_bound_without_normalization(self) -> None:
        for field in CLIENT_FIELDS:
            for side in ("client", "evidence"):
                with self.subTest(field=field, side=side):
                    record = deepcopy(self.record)
                    target = (
                        record["selection"]["client"] if side == "client"
                        else record["capabilities"][0]["evidence"]["binding"]["client"]
                    )
                    target[field] = "different-claimed-value"
                    self.invalid(record, ".binding.client: stale or foreign binding")

    def test_changed_record_and_capability_revision_invalidate_binding(self) -> None:
        for path in (("environment_id",), ("record_revision",), ("capabilities", 0, "id")):
            with self.subTest(path=path):
                record = deepcopy(self.record)
                at(record, path[:-1])[path[-1]] = "changed"
                self.invalid(record, "stale or foreign binding")

    def test_selected_evidence_cannot_omit_client_binding(self) -> None:
        self.record["capabilities"][0]["evidence"]["binding"]["client"] = None
        self.invalid(self.record, ".binding.client: stale or foreign binding")

    def test_same_reference_can_support_distinct_bound_capabilities(self) -> None:
        second = deepcopy(self.record["capabilities"][0])
        second["id"] = "cancellation"
        second["evidence"]["binding"]["capability_id"] = "cancellation"
        self.record["capabilities"].append(second)
        self.check_report(host.validate_record(self.record), True)

    def test_same_reference_cannot_change_revision_or_class(self) -> None:
        for field, value, status in (
            ("revision", "different-source-revision", "OBSERVED"),
            ("class", "DOCUMENTATION_CLAIM", "DOCUMENTED"),
        ):
            with self.subTest(field=field):
                record = deepcopy(self.record)
                second = deepcopy(record["capabilities"][0])
                second.update(id="cancellation", status=status)
                second["evidence"][field] = value
                second["evidence"]["binding"]["capability_id"] = "cancellation"
                record["capabilities"].append(second)
                self.invalid(record, "conflicting revision or class for one reference")

    def test_authority_claim_fields_are_not_accepted(self) -> None:
        for field in ("host_qualified", "execution_authorized", "approved"):
            with self.subTest(field=field):
                record = deepcopy(self.record)
                record[field] = True
                self.invalid(record, "unexpected fields")

    def test_api_is_pure_and_reference_text_remains_inert(self) -> None:
        self.record["selection"]["client"]["launcher"] = "$(synthetic-never-execute)"
        evidence = self.record["capabilities"][0]["evidence"]
        evidence["reference"] = "file:synthetic-never-read"
        evidence["binding"]["client"] = deepcopy(self.record["selection"]["client"])
        original = deepcopy(self.record)
        with (
            patch("builtins.open", side_effect=AssertionError("unexpected file access")),
            patch.object(Path, "open", side_effect=AssertionError("unexpected path access")),
            patch("subprocess.Popen", side_effect=AssertionError("unexpected process")),
            patch("socket.socket", side_effect=AssertionError("unexpected network")),
        ):
            self.check_report(host.validate_record(self.record), True)
        self.assertEqual(self.record, original)


class CLITests(ReportCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory(prefix="host check ", dir=FIXTURES)
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)

    def run_cli(self, arguments: list[str], valid: bool) -> dict:
        result = subprocess.run(
            [sys.executable, "-B", str(SCRIPT), *arguments],
            cwd=ROOT, capture_output=True, text=True, timeout=15, check=False,
        )
        self.assertEqual(result.returncode, 0 if valid else 1, result.stderr)
        self.assertEqual(result.stderr, "")
        report = json.loads(result.stdout)
        self.check_report(report, valid)
        return report

    def run_text(self, text: str, valid: bool = False) -> dict:
        path = self.root / "record with spaces.json"
        path.write_text(text, encoding="utf-8")
        return self.run_cli([str(path)], valid)

    def test_valid_fixtures_emit_machine_reports_without_authority(self) -> None:
        for name in ("unselected.json", "selected.json"):
            with self.subTest(name=name):
                self.run_cli([str(FIXTURES / name)], True)

    def test_invalid_record_is_nonzero_after_successful_parse(self) -> None:
        record = fixture("selected.json")
        del record["selection"]["client"]["product"]
        report = self.run_text(json.dumps(record))
        self.assertTrue(any("missing fields: product" in error for error in report["errors"]))

    def test_valid_record_path_with_spaces(self) -> None:
        self.run_text(json.dumps(fixture("unselected.json")), True)

    def test_duplicate_key_fixture_is_rejected_before_field_validation(self) -> None:
        report = self.run_cli([str(FIXTURES / "duplicate_keys.json")], False)
        self.assertEqual(report["errors"], ["record: duplicate JSON object key."])

    def test_duplicate_keys_at_multiple_depths_and_escaped_alias(self) -> None:
        for text in (
            '{"x":1,"x":1}',
            '{"nested":[{"x":1,"x":2}]}',
            r'{"status":"UNSELECTED","\u0073tatus":"SELECTED"}',
        ):
            with self.subTest(text=text):
                report = self.run_text(text)
                self.assertEqual(report["errors"], ["record: duplicate JSON object key."])

    def test_malformed_json_and_trailing_content_are_rejected(self) -> None:
        for text in ("", "{", '{"x":}', "{} {}", '{"x":1,}', "\ufeff{}"):
            with self.subTest(text=text):
                report = self.run_text(text)
                self.assertTrue(any("invalid JSON at line" in error for error in report["errors"]))

    def test_nonfinite_json_literals_are_rejected(self) -> None:
        for value in ("NaN", "Infinity", "-Infinity"):
            with self.subTest(value=value):
                report = self.run_text('{"value":' + value + "}")
                self.assertEqual(report["errors"], [
                    "record: non-finite numeric literals are not valid JSON.",
                ])

    def test_deep_nonrecord_is_rejected_across_decoder_limits(self) -> None:
        report = self.run_text("[" * 2000 + "0" + "]" * 2000)
        self.assertIn(report["errors"], (
            ["record: JSON exceeds parser limits."],
            ["record: expected an object."],
        ))

    def test_decoder_recursion_failure_has_an_explicit_report(self) -> None:
        output = io.StringIO()
        with (
            patch.object(Path, "read_text", return_value="{}"),
            patch.object(host.json, "loads", side_effect=RecursionError("synthetic parser limit")),
            patch("sys.stdout", output),
        ):
            result = host.main(["synthetic-record.json"])
        self.assertEqual(result, 1)
        report = json.loads(output.getvalue())
        self.check_report(report, False)
        self.assertEqual(report["errors"], ["record: JSON exceeds parser limits."])

    def test_missing_file_and_directory_return_read_errors(self) -> None:
        for path in (self.root / "missing.json", self.root):
            with self.subTest(path=path):
                report = self.run_cli([str(path)], False)
                self.assertTrue(any("read failed" in error for error in report["errors"]))

    def test_invalid_utf8_is_a_machine_read_error(self) -> None:
        path = self.root / "invalid-encoding.json"
        path.write_bytes(b"\xff")
        report = self.run_cli([str(path)], False)
        self.assertEqual(report["errors"], ["record: read failed (UnicodeDecodeError)."])

    def test_permission_denial_is_explicit_without_retry(self) -> None:
        output = io.StringIO()
        with (
            patch.object(Path, "read_text", side_effect=PermissionError("synthetic denial")) as read,
            patch("sys.stdout", output),
        ):
            result = host.main(["synthetic-denied.json"])
        self.assertEqual(result, 1)
        read.assert_called_once_with(encoding="utf-8")
        report = json.loads(output.getvalue())
        self.check_report(report, False)
        self.assertEqual(report["errors"], ["record: read failed (PermissionError)."])

    def test_invalid_arguments_are_machine_readable(self) -> None:
        for arguments in ([], ["one.json", "two.json"], ["--unknown-option"]):
            with self.subTest(arguments=arguments):
                report = self.run_cli(arguments, False)
                self.assertEqual(report["errors"], [
                    "arguments: expected one record path; use --help for usage.",
                ])


if __name__ == "__main__":
    unittest.main()
