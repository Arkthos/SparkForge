"""Synthetic checkpoint tests, restricted to newly created owned fixtures."""

import copy
import hashlib
import shutil
import unittest
from pathlib import Path
from uuid import uuid4
from zipfile import ZipFile

from . import freeze_workspace


class CheckpointTests(unittest.TestCase):
    def setUp(self):
        self.workspace = Path(__file__).resolve().parent / (".checkpoint-test-" + uuid4().hex)
        self.workspace.mkdir()
        self.addCleanup(shutil.rmtree, self.workspace)
        self.checkpoint = self.workspace / "checkpoint"
        self.checkpoint.mkdir()
        self.source = self.workspace / "sample.txt"
        self.source.write_bytes(b"sample\r\n")
        self.archive = self.checkpoint / "snapshot.zip"
        with ZipFile(self.archive, "w") as archive:
            archive.write(self.source, "sample.txt")
        self.manifest = {
            "schema_version": 1, "state": "FROZEN_VERIFIED", "checkpoint_id": "fixture",
            "counts": {"files": 1, "bytes": 8},
            "archive": {
                "file": "snapshot.zip", "bytes": self.archive.stat().st_size,
                "sha256": hashlib.sha256(self.archive.read_bytes()).hexdigest(),
            },
            "files": [{"path": "sample.txt", "bytes": 8, "sha256": hashlib.sha256(b"sample\r\n").hexdigest()}],
        }
        self.verifier = freeze_workspace.verifier()

    def verify(self, working=False):
        return self.verifier.verify(self.manifest, self.checkpoint, self.workspace, working)

    def test_exact_snapshot_and_working_files(self):
        self.assertEqual(self.verify(working=True)["status"], "PASS")

    def test_archive_survives_later_working_edit(self):
        self.source.write_bytes(b"later")
        self.assertEqual(self.verify()["status"], "PASS")
        self.assertEqual(self.verify(working=True)["status"], "FAIL")

    def test_missing_working_file_reported(self):
        self.source.unlink()
        self.assertEqual(self.verify(working=True)["differences"][0]["reason"], "missing")

    def test_modified_archive_rejected(self):
        self.archive.write_bytes(self.archive.read_bytes() + b"x")
        with self.assertRaises(ValueError):
            self.verify()

    def test_wrong_entry_digest_rejected(self):
        self.manifest["files"][0]["sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "entry digest"):
            self.verify()

    def test_extra_zip_entry_rejected(self):
        with ZipFile(self.archive, "a") as archive:
            archive.writestr("extra.txt", b"extra")
        self.manifest["archive"]["bytes"] = self.archive.stat().st_size
        self.manifest["archive"]["sha256"] = hashlib.sha256(self.archive.read_bytes()).hexdigest()
        with self.assertRaisesRegex(ValueError, "entries"):
            self.verify()

    def test_duplicate_manifest_entry_rejected(self):
        self.manifest["files"].append(copy.deepcopy(self.manifest["files"][0]))
        with self.assertRaisesRegex(ValueError, "duplicated"):
            self.verify()

    def test_unsealed_manifest_rejected(self):
        self.manifest["state"] = "PREPARING"
        with self.assertRaisesRegex(ValueError, "unsealed"):
            self.verify()

    def test_unsafe_paths_rejected(self):
        for relative in ("../outside", r"..\outside", "/absolute", "C:/outside", "a//b", "a/./b"):
            with self.subTest(path=relative), self.assertRaises(ValueError):
                self.verifier.safe_path(self.workspace, relative)

    def test_existing_checkpoint_artifact_not_overwritten(self):
        target = self.checkpoint / "receipt.json"
        target.write_text("original", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "overwrite"):
            freeze_workspace.write_new_json(target, {"new": True})
        self.assertEqual(target.read_text(encoding="utf-8"), "original")


if __name__ == "__main__":
    unittest.main()
