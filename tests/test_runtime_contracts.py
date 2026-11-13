"""TC-103/TC-104: pure, source-neutral intent/envelope contract acceptance."""

from copy import deepcopy
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from plugins.sparkforge.runtime import contracts
from runtime_fixtures import KINDS, envelope_fixture, intent_fixture


class ContractTests(unittest.TestCase):
    def intent(self, value=None):
        return contracts.validate_intent(intent_fixture() if value is None else value, supported_component_kinds=KINDS)

    def envelope(self, value=None):
        return contracts.validate_envelope(envelope_fixture() if value is None else value, intent=self.intent())

    def error(self, code, function, *args, **kwargs):
        with self.assertRaises(contracts.ContractError) as caught:
            function(*args, **kwargs)
        self.assertEqual(caught.exception.code, code)
        self.assertTrue(caught.exception.path)
        self.assertTrue(str(caught.exception))

    def test_round_trip_is_detached_and_key_order_independent(self):
        for raw, validate in ((intent_fixture(), self.intent), (envelope_fixture(), self.envelope)):
            original = deepcopy(raw)
            normalized = validate(raw)
            self.assertEqual(normalized, original)
            self.assertEqual(validate(contracts.parse_json(contracts.canonical_json(normalized).encode("utf-8"))), original)
            reordered = json.loads(json.dumps(raw, sort_keys=True))
            self.assertEqual(contracts.record_digest(validate(reordered)), contracts.record_digest(normalized))
            self.assertEqual(raw, original)
            self.assertIsNot(normalized, raw)
        baseline = self.intent()
        baseline["acceptance"][0]["behavior"] = "Changed."
        self.assertNotEqual(baseline, intent_fixture())
        self.assertEqual(self.intent(), intent_fixture())

    def test_full_intent_and_envelope_changes_invalidate_binding(self):
        baseline = intent_fixture()
        for key, replacement in (
            ("problem", "Different problem"), ("outcome", "Different behavior"), ("audience", "Different users"),
            ("acceptance", [{"id": "A1", "behavior": "New behavior"}]),
            ("non_goals", ["No network access"]), ("material_constraints", ["Never publish"]),
            ("revision", 2), ("component_kind", "synthetic-agent"),
        ):
            with self.subTest(field=key):
                changed = deepcopy(baseline)
                changed[key] = replacement
                self.assertNotEqual(contracts.record_digest(self.intent(changed)), contracts.record_digest(baseline))
                self.error("INTENT_MISMATCH", contracts.validate_envelope, envelope_fixture(), intent=self.intent(changed))
        raw = envelope_fixture()
        changes = [
            ("environment", "CORP"), ("effects", ["workspace_read"]),
            ("tools", []), ("expires_at", "2030-01-02T00:00:00Z"), ("unknown_usage", "reserve_maximum"),
            ("profile", {"id": "fictional-profile", "revision": 2}),
            ("routes", {"host": {"id": "scripted-fake", "revision": 1},
                        "provider": {"id": "different-route", "revision": 1}}),
            ("revocation", {"revoked_at": "2029-12-01T00:00:00Z", "reason": "Synthetic withdrawal"}),
        ]
        for key, replacement in changes:
            changed = deepcopy(raw)
            changed[key] = replacement
            self.assertNotEqual(contracts.record_digest(self.envelope(changed)), contracts.record_digest(raw))
        for group, fields in raw["bounds"].items():
            for field in fields:
                changed = deepcopy(raw)
                changed["bounds"][group][field] += 1
                self.assertNotEqual(contracts.record_digest(self.envelope(changed)), contracts.record_digest(raw))

    def test_source_unknowns_are_explicit_and_bound_without_fictional_hashes(self):
        baseline = intent_fixture()
        self.assertIsNone(self.intent(baseline)["source_assumptions"][0]["references"][0]["sha256"])
        for status in ("known", "unknown", "unavailable"):
            value = deepcopy(baseline)
            value["source_assumptions"][0]["status"] = status
            self.assertEqual(self.intent(value)["source_assumptions"][0]["status"], status)
        value["source_assumptions"][0]["reason"] = ""
        self.error("INVALID_TEXT", self.intent, value)
        baseline["source_assumptions"] = []
        self.error("INVALID_LIST", self.intent, baseline)

    def test_profile_vocabulary_is_explicit_not_a_platform_claim(self):
        self.error("UNSUPPORTED_COMPONENT", contracts.validate_intent, intent_fixture(),
                   supported_component_kinds=("different-component",))
        self.error("INVALID_PROFILE", contracts.validate_intent, intent_fixture(), supported_component_kinds=())
        self.error("DUPLICATE_VALUE", contracts.validate_intent, intent_fixture(),
                   supported_component_kinds=("synthetic-component", "synthetic-component"))

    def test_missing_duplicate_or_blank_acceptance_is_rejected(self):
        for replacement, code in (
            ([], "INVALID_LIST"),
            ([{"id": "A1", "behavior": ""}], "INVALID_TEXT"),
            ([{"behavior": "Expected output"}], "INVALID_FIELDS"),
            ([{"id": "", "behavior": "Expected output"}], "INVALID_IDENTIFIER"),
            ([{"id": "A1", "behavior": "One"}, {"id": "A1", "behavior": "Two"}], "DUPLICATE_VALUE"),
        ):
            value = intent_fixture()
            value["acceptance"] = replacement
            self.error(code, self.intent, value)

    def test_closed_fields_cannot_embed_approval_authority_or_credentials(self):
        for fixture, validate in ((intent_fixture, self.intent), (envelope_fixture, self.envelope)):
            for field in ("approved", "authority", "password", "api_key", "execution_authorized"):
                value = fixture()
                value[field] = True
                self.error("INVALID_FIELDS", validate, value)
            value = fixture()
            value["schema_version"] = "sparkforge.future.v999"
            self.error("UNSUPPORTED_SCHEMA", validate, value)
        for field in ("profile", "intent", "revocation", "bounds"):
            value = envelope_fixture()
            value[field]["approved"] = True
            self.error("INVALID_FIELDS", self.envelope, value)
        value = envelope_fixture()
        value["routes"]["provider"]["token"] = "synthetic-not-a-secret"
        self.error("INVALID_FIELDS", self.envelope, value)
        value["routes"]["provider"] = {"id": "https://user:password@example.invalid", "revision": 1}
        self.error("INVALID_IDENTIFIER", self.envelope, value)

    def test_all_bounds_reject_unlimited_nonfinite_boolean_and_overflow(self):
        for group, fields in envelope_fixture()["bounds"].items():
            for field in fields:
                for invalid in (True, False, 0, -1, None, "unlimited", 1.5, float("inf"), float("nan"), 10**50):
                    with self.subTest(group=group, field=field, value=invalid):
                        value = envelope_fixture()
                        value["bounds"][group][field] = invalid
                        self.error("INVALID_BOUND", self.envelope, value)
        for revision in (True, 0, -1, "1"):
            value = intent_fixture()
            value["revision"] = revision
            self.error("INVALID_BOUND", self.intent, value)
        value = envelope_fixture()
        value["bounds"]["job"]["wall_seconds"] = 1
        self.error("INCONSISTENT_BOUNDS", self.envelope, value)

    def test_text_is_preserved_and_invalid_text_is_not_silently_trimmed(self):
        value = intent_fixture()
        value["outcome"] = "  Keep spaces.\nKeep accents: \u00e9.\tKeep tabs.  "
        self.assertEqual(self.intent(value)["outcome"], value["outcome"])
        for text in ("", " \n\t", "x" * 12001, "embedded\0control", "bad\x7f", "bad\u202e", "\ud800"):
            value["outcome"] = text
            self.error("INVALID_TEXT", self.intent, value)
        value["outcome"] = "x" * 12000
        self.assertEqual(self.intent(value)["outcome"], value["outcome"])

    def test_json_rejects_duplicate_keys_bad_encoding_and_nonfinite_exponents(self):
        for text, code in (
            ('{"id":"one","id":"two"}', "DUPLICATE_JSON_KEY"),
            ('{"nested":{"approved":false,"approved":true}}', "DUPLICATE_JSON_KEY"),
            ('{"bound":NaN}', "INVALID_JSON"), ('{"bound":1e999}', "INVALID_JSON"),
            ('{"bound":Infinity}', "INVALID_JSON"), ('{"broken":', "INVALID_JSON"),
            (b"\xff", "INVALID_JSON"), ('{"text":"\\ud800"}', "INVALID_JSON"),
            ("[" * 2000 + "]" * 2000, "INVALID_JSON"),
        ):
            with self.subTest(input=repr(text)[:80]):
                self.error(code, contracts.parse_json, text)
        self.error("INPUT_TOO_LARGE", contracts.parse_json, b" " * (contracts.MAX_JSON_BYTES + 1))
        self.error("INVALID_JSON", contracts.canonical_json, {"bound": float("nan")})
        self.error("INPUT_TOO_LARGE", contracts.canonical_json, {"text": "\u00e9" * contracts.MAX_JSON_BYTES})
        self.error("INVALID_JSON", contracts.canonical_json, {1: "not a string key"})
        self.error("INVALID_JSON", contracts.canonical_json, {"tuple": ("not", "a", "JSON", "array")})

    def test_list_order_remains_meaningful_and_input_size_is_bounded(self):
        value = intent_fixture()
        original = contracts.record_digest(self.intent(value))
        value["acceptance"].reverse()
        self.assertNotEqual(contracts.record_digest(self.intent(value)), original)
        value["non_goals"] = [f"Exclusion {index}" for index in range(129)]
        self.error("INVALID_LIST", self.intent, value)
        value = intent_fixture()
        value["non_goals"] = ["x" * 11995 + str(index) for index in range(128)]
        value["material_constraints"] = value["non_goals"][:]
        self.error("INPUT_TOO_LARGE", self.intent, value)

    def test_relative_paths_are_canonical_identifiers_not_host_paths(self):
        self.assertEqual(contracts.relative_path("src/component.py"), "src/component.py")
        for path in ("../out", "/out", r"C:\out", r"src\file", "src//file", "src/./file", "src/../file",
                     "src/file.", "src/file ", "src/CON.txt", "src/CON .txt", "src/file:stream", ".git/config", ".env",
                     "PROGRA~1/file", "a?b", "a\x01b", "src/COM\u00b9", "src/", "src/e\u0301", ""):
            self.error("UNSAFE_PATH", contracts.relative_path, path)

    def test_windows_and_posix_roots_are_validated_without_host_resolution(self):
        self.envelope()
        for flavor, paths in (
            ("windows", (r"c:\work", "C:/work", "C:\\", r"C:relative", r"\\server\share\work",
                         r"\\?\C:\work", r"C:\work\..\outside", "C:\\work\\", r"C:\WORK~1", r"C:\nul")),
            ("posix", ("/", "//server/work", "relative", "/work/../outside", "/work//child", "/work/")),
        ):
            for path in paths:
                with self.subTest(path=path):
                    value = envelope_fixture()
                    value["workspace_roots"][0] = {"id": "workspace", "flavor": flavor, "path": path}
                    self.error("UNSAFE_PATH", self.envelope, value)
        value = envelope_fixture()
        value["workspace_roots"].append({"id": "alias", "flavor": "windows", "path": r"C:\FICTIONAL\Workspace"})
        self.error("UNSAFE_PATH", self.envelope, value)

    def test_intent_id_digest_unknown_usage_expiry_and_revocation_are_explicit(self):
        for key, invalid in (("id", "other"), ("sha256", "f" * 64)):
            value = envelope_fixture()
            value["intent"][key] = invalid
            self.error("INTENT_MISMATCH", self.envelope, value)
        value = envelope_fixture()
        value["unknown_usage"] = "assume_zero"
        self.error("INVALID_ENUM", self.envelope, value)
        for expiry in (None, "never", "2030-02-30T00:00:00Z", "2030-01-01T00:00:00+00:00"):
            value = envelope_fixture()
            value["expires_at"] = expiry
            self.error("INVALID_TIME", self.envelope, value)
        value = envelope_fixture()
        value["revocation"]["reason"] = "Withdrawn"
        self.error("INVALID_REVOCATION", self.envelope, value)

    def test_validation_has_no_file_process_database_network_or_clock_effects(self):
        import socket
        import sqlite3
        import subprocess
        with (patch("builtins.open", side_effect=AssertionError("file I/O")),
              patch.object(Path, "open", side_effect=AssertionError("path I/O")),
              patch.object(Path, "stat", side_effect=AssertionError("path probing")),
              patch.object(Path, "resolve", side_effect=AssertionError("host path resolution")),
              patch.object(sqlite3, "connect", side_effect=AssertionError("database I/O")),
              patch.object(subprocess, "Popen", side_effect=AssertionError("process dispatch")),
              patch.object(socket, "socket", side_effect=AssertionError("network I/O")),
              patch("time.time", side_effect=AssertionError("clock probing"))):
            baseline = self.intent(contracts.parse_json(contracts.canonical_json(intent_fixture())))
            self.assertEqual(self.envelope()["intent"]["sha256"], contracts.record_digest(baseline))


if __name__ == "__main__":
    unittest.main()
