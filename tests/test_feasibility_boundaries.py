"""Coordinator checks of the development tools' public evidence boundaries."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from collections.abc import Iterator
from pathlib import Path

from scripts.probe_local_storage import run_probe
from scripts.validate_host_qualification import validate_record


ROOT = Path(__file__).resolve().parents[1]


def text_values(value: object) -> Iterator[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for item in value.values():
            yield from text_values(item)
    elif isinstance(value, list):
        for item in value:
            yield from text_values(item)


class FeasibilityBoundaryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.root = Path(tempfile.mkdtemp(
            prefix="feasibility integration ", dir=ROOT / "tests"
        ))
        self.keep_fixture = False
        self.files: set[Path] = set()
        self.addCleanup(self.remove_owned)

    def remove_owned(self) -> None:
        if self.keep_fixture:
            raise AssertionError("Integration fixture retained for process reconciliation")
        for path in self.files:
            path.unlink(missing_ok=True)
        self.root.rmdir()

    def command(self, script: str, *arguments: str) -> subprocess.CompletedProcess[str]:
        try:
            return subprocess.run(
                [sys.executable, "-B", str(ROOT / "scripts" / script), *arguments],
                cwd=ROOT,
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=30,
                check=False,
            )
        except subprocess.TimeoutExpired:
            self.keep_fixture = True
            raise

    def test_invalid_host_data_never_authenticates_or_authorizes(self) -> None:
        for payload in (None, [], {}, {"host_qualified": True, "execution_authorized": True}):
            with self.subTest(payload=payload):
                result = validate_record(payload)
                self.assertEqual(result["scope"], "record_consistency_only")
                self.assertIs(result["valid"], False)
                self.assertIs(result["host_qualified"], False)
                self.assertIs(result["execution_authorized"], False)
                self.assertTrue(result["errors"])
                self.assertIsInstance(result["blockers"], list)
                json.dumps(result, allow_nan=False)

    def test_invalid_record_cli_is_nonzero_and_never_qualified(self) -> None:
        path = self.root / "invalid host record.json"
        self.files.add(path)
        path.write_text("{}", encoding="utf-8")
        result = self.command("validate_host_qualification.py", str(path))
        self.assertNotEqual(result.returncode, 0)
        report = json.loads(result.stdout)
        self.assertIs(report["valid"], False)
        self.assertIs(report["host_qualified"], False)
        self.assertIs(report["execution_authorized"], False)
        self.assertEqual(path.read_text(encoding="utf-8"), "{}")

    def test_probe_cli_without_confirmation_writes_nothing(self) -> None:
        sentinel = self.root / "unrelated.txt"
        self.files.add(sentinel)
        sentinel.write_text("keep this content", encoding="utf-8")
        result = self.command(
            "probe_local_storage.py",
            "--root", str(self.root),
            "--scope-ref", "synthetic-integration",
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(set(self.root.iterdir()), {sentinel})
        self.assertEqual(sentinel.read_text(encoding="utf-8"), "keep this content")

    @unittest.skipUnless(os.name == "nt", "Windows local-drive classification required")
    def test_local_probe_observations_do_not_qualify_a_runtime_store(self) -> None:
        sentinel = self.root / "existing user file.txt"
        self.files.add(sentinel)
        sentinel.write_text("unchanged", encoding="utf-8")
        before_cwd = Path.cwd()
        report = run_probe(self.root, scope_ref="synthetic-integration")
        self.assertEqual(report["scope"], "disposable_local_storage_probe")
        self.assertEqual(report["overall"], "PASS", report)
        self.assertIs(report["runtime_store_qualified"], False)
        self.assertTrue(report["checks"])
        self.assertIn("cleanup", report)
        self.assertEqual(Path.cwd(), before_cwd)
        self.assertEqual(set(self.root.iterdir()), {sentinel})
        self.assertEqual(sentinel.read_text(encoding="utf-8"), "unchanged")
        for value in text_values(report):
            self.assertNotIn(str(self.root), value)
        json.dumps(report, allow_nan=False)


if __name__ == "__main__":
    unittest.main()
