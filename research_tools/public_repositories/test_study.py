"""Synthetic checks of research utilities, never of candidate frameworks."""

import hashlib
import json
import shutil
import subprocess
import unittest
from pathlib import Path
from unittest.mock import patch
from uuid import uuid4

from . import collect_github, study


class ResearchUtilityTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(__file__).resolve().parent / (".research-test-" + uuid4().hex)
        self.root.mkdir()
        self.addCleanup(shutil.rmtree, self.root)

    def sample(self):
        data = "first\r\n\u03b2\n".encode("utf-8")
        path = self.root / "source.txt"
        path.write_bytes(data)
        commit = "a" * 40
        metadata = {"repository": "example/project", "commit": commit}
        record = {
            "local_file": "source.txt", "path": "README.md", "commit": commit,
            "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest(),
            "git_blob": hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest(),
            "lines": 2, "is_lfs_pointer": False,
            "source_url": f"https://github.com/example/project/blob/{commit}/README.md",
        }
        return path, metadata, record

    def test_exact_bytes_utf8_and_crlf(self):
        _, metadata, record = self.sample()
        self.assertEqual(study.verify_record(self.root, metadata, record), "first\r\n\u03b2\n")

    def test_modified_bytes_rejected(self):
        path, metadata, record = self.sample()
        path.write_bytes(b"changed")
        with self.assertRaisesRegex(ValueError, "mismatch"):
            study.verify_record(self.root, metadata, record)

    def test_foreign_commit_rejected(self):
        _, metadata, record = self.sample()
        record["commit"] = "b" * 40
        with self.assertRaisesRegex(ValueError, "revision"):
            study.verify_record(self.root, metadata, record)

    def test_mutable_url_rejected(self):
        _, metadata, record = self.sample()
        record["source_url"] = "https://github.com/example/project/blob/main/README.md"
        with self.assertRaisesRegex(ValueError, "immutable"):
            study.verify_record(self.root, metadata, record)

    def test_path_escape_rejected(self):
        for path in ("../outside", r"..\outside", r"C:\outside", "/outside", r"\\host\share", "a/../b"):
            with self.subTest(path=path), self.assertRaises(ValueError):
                study.safe_child(self.root, path)

    def test_eof_read_is_clipped(self):
        self.assertEqual(study.normalize_ranges([[1, 200], [2, -1]], 12), [[1, 12], [2, 12]])

    def test_empty_range_rejected(self):
        with self.assertRaises(ValueError):
            study.normalize_ranges([[13, 30]], 12)

    def test_overlapping_reads_not_double_counted(self):
        self.assertEqual(study.merge_ranges([[1, 10], [5, 15], [20, 25], [16, 19]]), [[1, 25]])

    def test_actual_license_text(self):
        grant = (
            "Permission is hereby granted, free of charge, to deal\n"
            "in the Software without restriction. The above copyright notice "
            "and this permission notice shall be included."
        )
        self.assertEqual(study.classify_license("MIT License\n" + grant), "MIT")
        self.assertEqual(study.classify_license("Copyright 2025\n" + grant), "MIT")
        self.assertEqual(study.classify_license("Licensed under the Apache License, Version 2.0"), "Apache-2.0")
        self.assertEqual(study.classify_license("NOASSERTION"), "NOT_ESTABLISHED")

    def test_github_failure_keeps_reason_without_echoing_credentials(self):
        error = subprocess.CalledProcessError(1, ["gh"], stderr="private detail: Not Found (HTTP 404)")
        with patch.dict("os.environ", {"SYNTHETIC_TOKEN": "inert-not-a-credential"}):
            with patch.object(collect_github.subprocess, "run", side_effect=error):
                with self.assertRaisesRegex(RuntimeError, r"HTTP 404") as raised:
                    collect_github.api(
                        "repos/example/project/contents/missing",
                        token_env="SYNTHETIC_TOKEN", allow_network=True,
                    )
        self.assertNotIn("private detail", str(raised.exception))

    def test_heading_anchor_duplicates(self):
        self.assertEqual(study.heading_ids("# A `gate`\n## A gate\n"), {"a-gate", "a-gate-1"})

    def video_fixture(self):
        image = b"\x89PNG\r\n\x1a\nsynthetic-byte-fixture"
        (self.root / "image.png").write_bytes(image)
        (self.root / "VIDEO.md").write_text("# Fixture review\n", encoding="utf-8")
        metadata = {
            "schema_version": 1, "video_id": "abcdefghijk",
            "url": "https://www.youtube.com/watch?v=abcdefghijk",
            "linked_source": {"repository": "example/project", "commit": "a" * 40},
            "transcript": {
                "unique_segments": 2, "raw_dom_rows": 4, "reviewed_index_ranges": [[0, 1]],
                "all_available_segments_reviewed": True, "sha256_at_review": "b" * 64,
                "full_text_stored": False,
            },
            "user_image": {"path": "image.png", "bytes": len(image), "sha256": hashlib.sha256(image).hexdigest()},
        }
        reference = {"id": "fixture", "candidate": "example", "metadata_file": "source.json", "document": "VIDEO.md"}
        candidates = {"example": {"canonical_repository": "example/project", "commit": "a" * 40}}
        (self.root / "source.json").write_text(json.dumps(metadata), encoding="utf-8")
        return reference, candidates, metadata

    def test_video_metadata_is_not_transcript_byte_verification(self):
        reference, candidates, _ = self.video_fixture()
        result = study.verify_video_reference(self.root, reference, candidates)
        self.assertTrue(result["user_image_digest_verified"])
        self.assertFalse(result["full_transcript_bytes_reverified"])

    def test_changed_video_image_rejected(self):
        reference, candidates, _ = self.video_fixture()
        (self.root / "image.png").write_bytes(b"changed")
        with self.assertRaisesRegex(ValueError, "image bytes"):
            study.verify_video_reference(self.root, reference, candidates)

    def test_video_companion_revision_must_match(self):
        reference, candidates, _ = self.video_fixture()
        candidates["example"]["commit"] = "c" * 40
        with self.assertRaisesRegex(ValueError, "companion revision"):
            study.verify_video_reference(self.root, reference, candidates)

    def test_claimed_full_video_review_requires_all_segments(self):
        reference, candidates, metadata = self.video_fixture()
        metadata["transcript"]["reviewed_index_ranges"] = [[0, 0]]
        (self.root / "source.json").write_text(json.dumps(metadata), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "coverage gap"):
            study.verify_video_reference(self.root, reference, candidates)

    def test_video_url_identity_must_match(self):
        reference, candidates, metadata = self.video_fixture()
        metadata["url"] = "https://www.youtube.com/watch?v=other-video"
        (self.root / "source.json").write_text(json.dumps(metadata), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Video URL"):
            study.verify_video_reference(self.root, reference, candidates)


if __name__ == "__main__":
    unittest.main()
