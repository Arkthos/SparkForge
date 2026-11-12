"""Owned synthetic review-preparation cases; no private source or network use."""

from __future__ import annotations

import hashlib
import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch

from scripts import prepare_wiki_review as review


class WikiReviewTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="wiki-review-", dir=Path(__file__).parent)
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)
        self.root = self.base / "source"
        self.root.mkdir()
        self.output = self.base / "new review"
        self.policy = {"schema_version": "sparkforge.wiki-redaction-policy.v1", "literals": ["SampleGroup"]}
        self.original = (
            "Preserve the complete synthetic chapter.\r\n" + "Long-form reasoning stays here. " * 350
            + "\r\nSampleGroup uses https://example.invalid/wiki and user@example.invalid.\r\n"
            + "UnspecifiedName is not automatically safe.\r\n"
        ).encode("utf-8")
        self.manifest = {"snapshot_commit": "a" * 40, "pages": [], "attachments": [], "ancillary_items": []}
        for collection, name, raw in (
            ("pages", "first.md", self.original),
            ("pages", "empty.md", b""),
            ("attachments", "image.bin", b"\x89PNG\r\nSynthetic image bytes"),
            ("ancillary_items", "order.bin", b"first\nempty\n"),
        ):
            path = self.root / name
            path.write_bytes(raw)
            self.manifest[collection].append({
                "key": name, "local_path": name, "snapshot_commit": "a" * 40,
                "status": "EXPORTED", "bytes": len(raw),
                "sha256": hashlib.sha256(raw).hexdigest(),
            })
        self.save()

    def save(self):
        (self.root / "manifest.json").write_text(json.dumps(self.manifest), encoding="utf-8")

    def prepare(self, **overrides):
        args = {"root": self.root, "output": self.output, "policy": self.policy,
                "confirm_local_review": True}
        args.update(overrides)
        # Unit fixtures stay under tests; actual repository refusal is exercised separately.
        with patch.object(review, "_repository_output", return_value=False):
            return review.prepare_review(**args)

    def failure(self, code, **overrides):
        with self.assertRaises(review.ReviewError) as caught:
            self.prepare(**overrides)
        self.assertEqual(caught.exception.code, code)
        self.assertFalse(self.output.exists())

    def test_complete_full_length_pages_and_opaque_items_are_preserved(self):
        result = self.prepare()
        self.assertEqual(result["counts"], {"pages": 2, "attachments": 1, "ancillary_items": 1})
        self.assertFalse(result["publication_authorized"])
        self.assertFalse(result["semantic_review_completed"])
        self.assertFalse((self.output / "INCOMPLETE.json").exists())
        manifest = json.loads((self.output / "review-manifest.private.json").read_text())
        self.assertEqual(len(manifest["items"]), 4)
        for entry in manifest["items"]:
            original = (self.root / entry["source_local_path"]).read_bytes()
            self.assertEqual((self.output / entry["original_path"]).read_bytes(), original)
            self.assertEqual(hashlib.sha256(original).hexdigest(), entry["source_sha256"])
            if entry["collection"] == "pages":
                candidate = (self.output / entry["candidate_path"]).read_bytes()
                self.assertEqual(hashlib.sha256(candidate).hexdigest(), entry["candidate_sha256"])
                text = original.decode("utf-8")
                for span in reversed(entry["redactions"]):
                    text = text[:span["start"]] + span["replacement"] + text[span["end"]:]
                self.assertEqual(candidate, text.encode("utf-8"))
            else:
                self.assertEqual(entry["review_status"], "NOT_REVIEWED")
                self.assertNotIn("candidate_path", entry)
        first = (self.output / manifest["items"][0]["candidate_path"]).read_bytes()
        self.assertGreater(len(first), 6000)
        self.assertIn(b"UnspecifiedName", first)
        self.assertNotIn(b"SampleGroup", first)
        self.assertNotIn(b"example.invalid", first)
        self.assertIn(b"\r\n", first)
        self.assertEqual((self.output / "source-manifest.private.json").read_bytes(),
                         (self.root / "manifest.json").read_bytes())

    def test_confirmation_stops_before_source_or_output_access(self):
        self.failure("CONFIRMATION_REQUIRED", root=self.base / "absent", confirm_local_review=False)
        out = io.StringIO()
        with redirect_stdout(out):
            code = review.main(["--root", str(self.base / "absent"), "--output", str(self.output)])
        self.assertEqual(code, 2)
        self.assertEqual(json.loads(out.getvalue())["error"], "CONFIRMATION_REQUIRED")
        self.assertFalse(self.output.exists())

    def test_redactions_are_literal_span_changes_not_summaries_or_regex_policy(self):
        policy = {"schema_version": "sparkforge.wiki-redaction-policy.v1", "literals": [".*", "GROUP"]}
        text = "prefix .* group suffix https://example.invalid/GROUP/user@example.invalid end"
        output, spans, counts = review.redact_text(text, policy)
        self.assertTrue(output.startswith("prefix "))
        self.assertTrue(output.endswith(" end"))
        self.assertEqual(len(spans), 3)
        self.assertIn("literal_0001", counts)
        self.assertIn("url", spans[-1]["rules"])
        self.assertIn("email", spans[-1]["rules"])
        self.assertEqual(spans[-1]["end"], len(text) - 4)
        unchanged, records, _counts = review.redact_text("SyntheticName and ordinary policy text", policy)
        self.assertEqual(unchanged, "SyntheticName and ordinary policy text")
        self.assertEqual(records, [])

    def test_invalid_incomplete_and_duplicate_records_fail_without_output(self):
        original = deepcopy(self.manifest)
        cases = [
            ("missing_collection", "INCOMPLETE_INVENTORY"),
            ("empty_pages", "INCOMPLETE_INVENTORY"),
            ("bad_status", "INCOMPLETE_SOURCE_RECORD"),
            ("mixed_revision", "INCOMPLETE_SOURCE_RECORD"),
            ("duplicate_key", "INVALID_OR_DUPLICATE_SOURCE_KEY"),
            ("duplicate_path", "DUPLICATE_SOURCE_PATH"),
            ("bool_size", "INCOMPLETE_SOURCE_RECORD"),
            ("unsafe_path", "INVALID_SOURCE_PATH"),
        ]
        for name, expected in cases:
            with self.subTest(name=name):
                self.manifest = deepcopy(original)
                first = self.manifest["pages"][0]
                if name == "missing_collection":
                    del self.manifest["attachments"]
                elif name == "empty_pages":
                    self.manifest["pages"] = []
                elif name == "bad_status":
                    first["status"] = "MISSING"
                elif name == "mixed_revision":
                    first["snapshot_commit"] = "b" * 40
                elif name == "duplicate_key":
                    self.manifest["pages"][1]["key"] = first["key"]
                elif name == "duplicate_path":
                    self.manifest["pages"][1]["local_path"] = first["local_path"].upper()
                elif name == "bool_size":
                    first["bytes"] = True
                else:
                    first["local_path"] = "../outside.md"
                self.save()
                self.failure(expected)

    def test_hash_or_declared_size_mismatch_stops_before_writes(self):
        for field, value in (("sha256", "0" * 64), ("bytes", len(self.original) - 1)):
            with self.subTest(field=field):
                original = self.manifest["pages"][0][field]
                self.manifest["pages"][0][field] = value
                self.save()
                self.failure("SOURCE_HASH_MISMATCH")
                self.manifest["pages"][0][field] = original

    def test_missing_indexed_file_is_not_silently_omitted(self):
        (self.root / "image.bin").unlink()
        with self.assertRaises(FileNotFoundError):
            self.prepare()
        self.assertFalse(self.output.exists())

    def test_existing_output_is_not_adopted_or_cleaned(self):
        self.output.mkdir()
        sentinel = self.output / "user.txt"
        sentinel.write_text("Unrelated synthetic owner")
        with self.assertRaises(review.ReviewError) as caught:
            self.prepare()
        self.assertEqual(caught.exception.code, "OUTPUT_EXISTS")
        self.assertEqual(sentinel.read_text(), "Unrelated synthetic owner")
        self.assertEqual(list(self.output.iterdir()), [sentinel])

    def test_repository_or_overlapping_output_is_refused(self):
        self.assertTrue(review._repository_output(review.CODE_ROOT / "candidate"))
        with self.assertRaises(review.ReviewError) as caught:
            review.prepare_review(self.root, self.output, self.policy, confirm_local_review=True)
        self.assertEqual(caught.exception.code, "SEPARATE_NON_REPOSITORY_OUTPUT_REQUIRED")
        self.assertFalse(self.output.exists())
        with self.assertRaises(review.ReviewError) as caught:
            self.prepare(output=self.root / "candidate")
        self.assertEqual(caught.exception.code, "SEPARATE_NON_REPOSITORY_OUTPUT_REQUIRED")
        self.assertFalse((self.root / "candidate").exists())

    def test_resource_bounds_fail_before_partial_export(self):
        with patch.object(review, "MAX_FILE_BYTES", 3):
            self.failure("RESOURCE_LIMIT")
        with patch.object(review, "MAX_TOTAL_BYTES", len(self.original)):
            self.failure("RESOURCE_LIMIT")
        with patch.object(review, "MAX_ITEMS", 3):
            self.failure("RESOURCE_LIMIT")

    def test_policy_never_accepts_regex_code_or_duplicate_literals(self):
        for policy, code in (
            ({"schema_version": "unknown", "literals": []}, "INVALID_POLICY"),
            ({"schema_version": "sparkforge.wiki-redaction-policy.v1", "literals": [], "regex": ".*"}, "INVALID_POLICY"),
            ({"schema_version": "sparkforge.wiki-redaction-policy.v1", "literals": [None]}, "INVALID_POLICY"),
            ({"schema_version": "sparkforge.wiki-redaction-policy.v1", "literals": ["a\nb"]}, "INVALID_POLICY"),
            ({"schema_version": "sparkforge.wiki-redaction-policy.v1", "literals": ["Group", "group"]}, "DUPLICATE_LITERAL"),
        ):
            with self.subTest(code=code, policy=policy):
                self.failure(code, policy=policy)

    def test_late_source_mutation_is_rejected_before_output_creation(self):
        original_read = review._read

        def change_after_read(root, relative, maximum):
            result = original_read(root, relative, maximum)
            if relative.name == "order.bin":
                (self.root / "first.md").write_bytes(self.original + b"changed")
            return result

        with patch.object(review, "_read", side_effect=change_after_read):
            self.failure("SOURCE_CHANGED")

    def test_output_failure_retains_an_explicit_incomplete_owned_directory(self):
        original_write = review._write

        def refuse_candidate(path, raw):
            if path.parent.name == "candidates":
                raise OSError("Synthetic private-path failure")
            return original_write(path, raw)

        with patch.object(review, "_write", side_effect=refuse_candidate):
            with self.assertRaises(review.ReviewError) as caught:
                self.prepare()
        self.assertEqual(caught.exception.code, "OUTPUT_WRITE_FAILED")
        self.assertTrue(caught.exception.output_created)
        self.assertTrue((self.output / "INCOMPLETE.json").is_file())
        self.assertFalse((self.output / "review-manifest.private.json").exists())
        self.assertEqual((self.root / "first.md").read_bytes(), self.original)

    def test_duplicate_json_and_non_utf8_pages_never_produce_a_candidate(self):
        (self.root / "manifest.json").write_bytes(b'{"pages": [], "pages": []}')
        self.failure("DUPLICATE_JSON_KEY")
        raw = b"\xff\xfe"
        (self.root / "first.md").write_bytes(raw)
        self.manifest["pages"][0].update(bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest())
        self.save()
        self.failure("PAGE_NOT_UTF8")

    def test_cli_failure_does_not_echo_private_roots_or_exception_text(self):
        out = io.StringIO()
        with redirect_stdout(out):
            code = review.main([
                "--root", str(self.base / "missing-private-name"), "--output", str(self.output),
                "--confirm-local-review",
            ])
        self.assertEqual(code, 2)
        report = json.loads(out.getvalue())
        self.assertEqual(report["error"], "FILESYSTEM_UNAVAILABLE")
        self.assertNotIn(str(self.base), out.getvalue())
        self.assertNotIn("missing-private-name", out.getvalue())
        self.assertFalse(report["publication_authorized"])


if __name__ == "__main__":
    unittest.main()
