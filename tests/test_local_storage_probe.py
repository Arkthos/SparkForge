"""Synthetic engineering-tool tests; not product or actual-host acceptance."""

from __future__ import annotations

import contextlib
import io
import json
import os
import stat
import subprocess
import sys
import time
import unittest
import uuid
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

from scripts import probe_local_storage as probe


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "probe_local_storage.py"
_DEFAULT_ROOT = object()


class ProbeCase(unittest.TestCase):
    def setUp(self) -> None:
        self.keep_fixture = False
        self.directories: set[Path] = set()
        self.files: set[Path] = set()
        self.base = Path(__file__).resolve().parent / (".storage-probe-test-" + uuid.uuid4().hex)
        self.directory(self.base)
        self.addCleanup(self.remove_owned)
        self.root = self.directory(self.base / "caller root with spaces")
        self.sentinel = self.file(self.root / "unrelated-sentinel.txt", b"synthetic unrelated content\n")

    def directory(self, path: Path) -> Path:
        path.mkdir(mode=0o700, parents=False, exist_ok=False)
        self.directories.add(path)
        return path

    def file(self, path: Path, data: bytes) -> Path:
        with path.open("xb") as stream:
            self.files.add(path)
            stream.write(data)
        return path

    def remember_area(self, area: probe._OwnedArea) -> None:
        self.directories.add(area.path)
        self.files.update(area.path / name for name in probe.FILE_NAMES)

    def remove_owned(self) -> None:
        if self.keep_fixture:
            raise AssertionError("Owned test fixture retained because process scope is not reconciled")
        for path in sorted(self.files, key=lambda item: (-len(item.parts), str(item))):
            try:
                path.unlink()
            except FileNotFoundError:
                pass
        for path in sorted(self.directories, key=lambda item: (-len(item.parts), str(item))):
            try:
                path.rmdir()
            except FileNotFoundError:
                pass

    def stop_known_child(self, child: subprocess.Popen) -> None:
        try:
            if child.poll() is None:
                child.kill()
                child.wait(timeout=2)
        except (OSError, subprocess.TimeoutExpired):
            self.keep_fixture = True
            raise

    def call_probe(self, root: object = _DEFAULT_ROOT, *, scope_ref: object = "WP-016-test") -> dict:
        selected = self.root if root is _DEFAULT_ROOT else root
        create = probe._OwnedArea.create

        def tracked_create(area: probe._OwnedArea) -> None:
            try:
                create(area)
            finally:
                if area.created:
                    self.remember_area(area)

        with patch.object(probe._OwnedArea, "create", new=tracked_create):
            return probe.run_probe(selected, scope_ref=scope_ref)

    def assert_clean_root(self) -> None:
        self.assertEqual(set(self.root.iterdir()), {self.sentinel})
        self.assertEqual(self.sentinel.read_bytes(), b"synthetic unrelated content\n")

    def checks(self, report: dict) -> dict:
        return {item["id"]: item for item in report["checks"]}

    def cli(self, *arguments: str) -> tuple[int, dict, str]:
        process = subprocess.Popen(
            [sys.executable, "-I", "-S", "-B", str(SCRIPT), *arguments],
            cwd=self.base,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            shell=False,
            close_fds=True,
        )
        self.addCleanup(self.stop_known_child, process)
        try:
            output, error = process.communicate(timeout=20)
        except subprocess.TimeoutExpired:
            self.keep_fixture = True
            self.stop_known_child(process)
            process.communicate(timeout=2)
            self.fail("Owned CLI exceeded its engineering timeout; fixture retained for reconciliation")
        try:
            report = json.loads(output)
        except json.JSONDecodeError:
            self.keep_fixture = True
            raise
        if report.get("cleanup", {}).get("unconfirmed_owned_child_pid") is not None:
            self.keep_fixture = True
        name = report.get("probe_directory_name")
        if name is not None:
            self.assertRegex(name, r"^\.sparkforge-storage-probe-[0-9a-f]{32}$")
            area = self.root / name
            self.directories.add(area)
            self.files.update(area / item for item in probe.FILE_NAMES)
        return process.returncode, report, error


@unittest.skipUnless(os.name == "nt", "Windows local-drive classification required")
class StorageProbeTests(ProbeCase):
    def test_actual_observations_report_and_cleanup(self) -> None:
        report = self.call_probe()
        self.assertEqual(report["overall"], "PASS", report)
        self.assertEqual(report["scope"], "disposable_local_storage_probe")
        self.assertEqual(report["scope_ref"], "WP-016-test")
        self.assertIs(report["runtime_store_qualified"], False)
        self.assertEqual([item["id"] for item in report["checks"]], list(probe.CHECK_IDS))
        self.assertTrue(all(item["outcome"] == "PASS" for item in report["checks"]))
        self.assertEqual([item["observations"]["child_exit_code"] for item in report["checks"]], [0, 23, 73])
        self.assertEqual(report["cleanup"]["outcome"], "PASS")
        self.assertEqual(report["cleanup"]["owned_files_removed"], 4)
        self.assertTrue(report["cleanup"]["owned_directory_removed"])
        self.assertTrue(all(value == "NOT_ASSESSED" for value in report["limits"].values()))
        self.assertIn("onedrive_cloud_synchronization", report["limits"])
        self.assertIn("power_loss_durability", report["limits"])
        self.assertNotIn(str(self.root), json.dumps(report))
        self.assert_clean_root()

    def test_real_child_exit_and_intermediate_file_states(self) -> None:
        real_child = probe._run_child
        observed: list[tuple[str, int]] = []

        def observe(area: probe._OwnedArea, mode: str) -> int:
            code = real_child(area, mode)
            observed.append((mode, code))
            self.assertIsNone(area.child)
            if mode == "replace":
                self.assertEqual(area.read("replace.committed"), area.new)
                self.assertFalse((area.path / "replace.candidate").exists())
            elif mode == "exclusive":
                self.assertEqual(area.read("writer.lock"), area.writer)
            else:
                self.assertEqual(area.read("interrupt.committed"), area.old)
                self.assertEqual(area.read("interrupt.candidate"), area.new)
            return code

        with patch.object(probe, "_run_child", side_effect=observe):
            report = self.call_probe()
        self.assertEqual(report["overall"], "PASS", report)
        self.assertEqual(observed, [("replace", 0), ("exclusive", 23), ("interrupt", 73)])
        self.assert_clean_root()

    def test_exclusive_child_is_not_hard_coded_to_report_conflict(self) -> None:
        area = probe._OwnedArea(self.root, probe._validate_root(self.root))
        area.create()
        self.remember_area(area)
        self.assertEqual(probe._run_child(area, "exclusive"), 0)
        self.assertEqual((area.path / "writer.lock").read_bytes(), area.new)
        self.assertIsNone(area.child)
        cleanup = area.cleanup()
        self.assertEqual(cleanup["outcome"], "FAIL")
        self.assertTrue((area.path / "writer.lock").exists())

    def test_repeated_runs_get_distinct_owned_directories(self) -> None:
        first = self.call_probe()
        second = self.call_probe()
        self.assertEqual((first["overall"], second["overall"]), ("PASS", "PASS"))
        self.assertNotEqual(first["probe_directory_name"], second["probe_directory_name"])
        self.assert_clean_root()

    def test_missing_file_relative_traversal_and_volume_roots_never_write(self) -> None:
        roots = (
            self.root / "missing",
            self.sentinel,
            Path("relative-root"),
            Path("."),
            self.root / ".." / "caller root with spaces",
            Path(self.root.anchor),
            str(self.root),
            None,
        )
        for root in roots:
            with self.subTest(root_type=type(root).__name__), patch.object(probe._OwnedArea, "create") as create:
                report = self.call_probe(root)
                create.assert_not_called()
                self.assertEqual(report["overall"], "BLOCKED", report)
                self.assertEqual(report["cleanup"]["outcome"], "NOT_NEEDED")
                self.assertIsNone(report["probe_directory_name"])
                self.assert_clean_root()

    def test_invalid_scope_rejected_without_echo_or_writes(self) -> None:
        for value in ("", "contains spaces", "../private", "x" * 65, r"C:\private", None, 12):
            with self.subTest(value_type=type(value).__name__), patch.object(probe._OwnedArea, "create") as create:
                report = self.call_probe(scope_ref=value)
                create.assert_not_called()
                self.assertEqual(report["overall"], "BLOCKED")
                self.assertIsNone(report["scope_ref"])
                self.assertEqual(report["diagnostics"], [{"code": "invalid_scope_ref"}])
                self.assert_clean_root()

    @unittest.skipUnless(os.name == "nt", "Windows path spelling checks")
    def test_windows_network_device_reserved_and_stream_roots_rejected(self) -> None:
        roots = (
            Path(r"\\server\share\probe"),
            Path(r"\\?\C:\probe"),
            Path(r"C:\probe:stream"),
            Path(r"C:\CON"),
            Path("C:\\trailing.\\probe"),
        )
        for root in roots:
            with self.subTest(root_kind=root.drive), patch.object(probe._OwnedArea, "create") as create:
                report = self.call_probe(root)
                create.assert_not_called()
                self.assertEqual(report["overall"], "BLOCKED", report)
                self.assert_clean_root()

    def test_network_and_unknown_drive_types_block_before_filesystem_reads(self) -> None:
        for kind in (0, 1, 4, 5):
            with (
                self.subTest(kind=kind),
                patch.object(probe, "_drive_type", return_value=kind),
                patch.object(Path, "lstat", side_effect=AssertionError("unexpected path access")),
                patch.object(probe._OwnedArea, "create") as create,
            ):
                report = self.call_probe()
                create.assert_not_called()
                self.assertEqual(report["overall"], "BLOCKED")
                expected = "network_drive_not_allowed" if kind == 4 else "drive_type_not_qualified"
                self.assertEqual(report["diagnostics"], [{"code": expected}])
            self.assert_clean_root()

    def test_drive_type_inspection_failure_is_not_a_local_default(self) -> None:
        with (
            patch.object(probe, "_drive_type", side_effect=probe._Blocked("drive_type_unavailable")),
            patch.object(Path, "lstat", side_effect=AssertionError("unexpected path access")),
        ):
            report = self.call_probe()
        self.assertEqual(report["overall"], "BLOCKED")
        self.assertEqual(report["diagnostics"], [{"code": "drive_type_unavailable"}])
        self.assert_clean_root()

    def test_redirecting_root_or_ancestor_metadata_blocks_before_creation(self) -> None:
        real_lstat = Path.lstat
        for target in (self.root, self.base):
            for mode, tag in ((stat.S_IFLNK, 0), (stat.S_IFDIR, 0xA0000003)):
                original = real_lstat(target)
                replacement = SimpleNamespace(
                    st_mode=mode, st_dev=original.st_dev, st_ino=original.st_ino,
                    st_nlink=original.st_nlink, st_reparse_tag=tag,
                )

                def lstat(path: Path, *args, **kwargs):
                    return replacement if path == target else real_lstat(path, *args, **kwargs)

                with self.subTest(target=target.name, tag=tag), patch.object(Path, "lstat", new=lstat):
                    report = self.call_probe()
                self.assertEqual(report["overall"], "BLOCKED", report)
                self.assertEqual(report["cleanup"]["outcome"], "NOT_NEEDED")
                self.assert_clean_root()

    def test_unavailable_root_file_identity_blocks(self) -> None:
        real_lstat = Path.lstat
        original = self.root.lstat()
        replacement = SimpleNamespace(st_mode=original.st_mode, st_dev=original.st_dev, st_ino=0, st_reparse_tag=0)

        def lstat(path: Path, *args, **kwargs):
            return replacement if path == self.root else real_lstat(path, *args, **kwargs)

        with patch.object(Path, "lstat", new=lstat):
            report = self.call_probe()
        self.assertEqual(report["overall"], "BLOCKED")
        self.assertEqual(report["diagnostics"], [{"code": "file_identity_unavailable"}])
        self.assert_clean_root()

    def test_directory_collision_never_adopted_or_retried(self) -> None:
        token = "0" * 32
        existing = self.directory(self.root / (".sparkforge-storage-probe-" + token))
        sentinel = self.file(existing / "keep.txt", b"existing synthetic content")
        with patch.object(probe.uuid, "uuid4", return_value=SimpleNamespace(hex=token)) as generate:
            report = self.call_probe()
        generate.assert_called_once()
        self.assertEqual(report["overall"], "BLOCKED", report)
        self.assertEqual(report["cleanup"]["outcome"], "NOT_NEEDED")
        self.assertIsNone(report["probe_directory_name"])
        self.assertEqual(sentinel.read_bytes(), b"existing synthetic content")
        self.assertEqual(set(self.root.iterdir()), {self.sentinel, existing})

    def test_unrelated_application_shaped_fixture_preserved(self) -> None:
        other = self.directory(self.root / "existing-application")
        data = self.file(other / "state.db", b"synthetic sentinel, not a database")
        report = self.call_probe()
        self.assertEqual(report["overall"], "PASS", report)
        self.assertEqual(data.read_bytes(), b"synthetic sentinel, not a database")
        self.assertEqual(set(self.root.iterdir()), {self.sentinel, other})

    def test_unexpected_exit_fails_without_later_checks(self) -> None:
        with patch.object(probe, "_run_child", return_value=9) as child:
            report = self.call_probe()
        child.assert_called_once()
        self.assertEqual(report["overall"], "FAIL")
        self.assertEqual([item["outcome"] for item in report["checks"]], ["FAIL", "BLOCKED", "BLOCKED"])
        self.assertEqual(report["cleanup"]["outcome"], "PASS")
        self.assert_clean_root()

    def test_false_conflict_or_interruption_exit_cannot_pass(self) -> None:
        real_child = probe._run_child
        for mode, identifier in (("exclusive", "exclusive_create_conflict"), ("interrupt", "interrupted_publication")):
            def wrong_exit(area: probe._OwnedArea, requested: str) -> int:
                return 0 if requested == mode else real_child(area, requested)

            with self.subTest(mode=mode), patch.object(probe, "_run_child", side_effect=wrong_exit):
                report = self.call_probe()
            self.assertEqual(report["overall"], "FAIL", report)
            self.assertEqual(self.checks(report)[identifier]["outcome"], "FAIL")
            self.assert_clean_root()

    def test_corrupt_replacement_fails_and_preserves_unexpected_content(self) -> None:
        real_child = probe._run_child
        changed: list[Path] = []

        def corrupt(area: probe._OwnedArea, mode: str) -> int:
            code = real_child(area, mode)
            if mode == "replace":
                path = area.path / "replace.committed"
                path.write_bytes(b"unexpected synthetic content")
                changed.append(path)
            return code

        with patch.object(probe, "_run_child", side_effect=corrupt):
            report = self.call_probe()
        self.assertEqual(report["overall"], "FAIL", report)
        self.assertEqual(report["checks"][0]["reason"], "replacement_marker_mismatch")
        self.assertEqual(report["cleanup"]["outcome"], "FAIL")
        self.assertEqual(changed[0].read_bytes(), b"unexpected synthetic content")

    def test_child_filesystem_error_is_blocked_not_conflict_or_pass(self) -> None:
        with patch.object(probe, "_CHILD_SOURCE", "import os; os._exit(74)"):
            report = self.call_probe()
        self.assertEqual(report["overall"], "BLOCKED", report)
        self.assertEqual(report["checks"][0]["reason"], "child_filesystem_error")
        self.assertEqual(report["cleanup"]["outcome"], "PASS")
        self.assert_clean_root()

    def test_process_start_failure_is_reported_without_raw_exception_text(self) -> None:
        with patch.object(probe.subprocess, "Popen", side_effect=PermissionError(r"C:\private\sensitive-path")):
            report = self.call_probe()
        self.assertEqual(report["overall"], "BLOCKED", report)
        self.assertEqual(report["checks"][0]["reason"], "filesystem_PermissionError")
        self.assertNotIn("sensitive-path", json.dumps(report))
        self.assertNotIn(str(self.root), json.dumps(report))
        self.assert_clean_root()

    def test_real_timeout_stops_only_owned_child_and_is_bounded(self) -> None:
        real_popen = subprocess.Popen
        children: list[subprocess.Popen] = []

        def start(*args, **kwargs):
            child = real_popen(*args, **kwargs)
            children.append(child)
            self.addCleanup(self.stop_known_child, child)
            return child

        started = time.monotonic()
        with (
            patch.object(probe, "_CHILD_SOURCE", "import time; time.sleep(60)"),
            patch.object(probe, "CHILD_TIMEOUT_SECONDS", 0.1),
            patch.object(probe.subprocess, "Popen", side_effect=start),
        ):
            report = self.call_probe()
        self.assertLess(time.monotonic() - started, 6.0)
        self.assertEqual(len(children), 1)
        self.assertIsNotNone(children[0].poll())
        self.assertEqual(report["overall"], "BLOCKED", report)
        self.assertEqual(report["checks"][0]["reason"], "child_timeout_stopped")
        self.assertEqual(report["cleanup"]["outcome"], "PASS")
        self.assert_clean_root()

    def test_unconfirmed_stop_preserves_files_and_does_not_repeat_kill(self) -> None:
        child = Mock(spec=subprocess.Popen)
        child.pid = 12345
        child.poll.return_value = None
        child.wait.side_effect = subprocess.TimeoutExpired("synthetic-child", 0.1)
        child.kill.side_effect = PermissionError("injected stop refusal")
        with patch.object(probe.subprocess, "Popen", return_value=child):
            report = self.call_probe()
        child.kill.assert_called_once()
        self.assertEqual(report["overall"], "BLOCKED", report)
        self.assertEqual(report["cleanup"]["outcome"], "BLOCKED")
        self.assertEqual(report["cleanup"]["unconfirmed_owned_child_pid"], 12345)
        area = self.root / report["probe_directory_name"]
        self.assertTrue((area / "replace.committed").is_file())
        self.assertTrue((area / "replace.candidate").is_file())

    def test_unknown_nested_content_survives_nonrecursive_cleanup(self) -> None:
        real_child = probe._run_child
        extra: list[Path] = []

        def add_unrelated(area: probe._OwnedArea, mode: str) -> int:
            code = real_child(area, mode)
            if mode == "interrupt":
                folder = self.directory(area.path / "unexpected-directory")
                extra.append(self.file(folder / "keep.txt", b"preserve this synthetic content"))
            return code

        with patch.object(probe, "_run_child", side_effect=add_unrelated):
            report = self.call_probe()
        self.assertTrue(all(item["outcome"] == "PASS" for item in report["checks"]))
        self.assertEqual(report["overall"], "FAIL", report)
        self.assertEqual(report["cleanup"]["outcome"], "FAIL")
        self.assertFalse(report["cleanup"]["owned_directory_removed"])
        self.assertEqual(extra[0].read_bytes(), b"preserve this synthetic content")
        self.assertEqual(set(extra[0].parent.parent.iterdir()), {extra[0].parent})

    def test_replaced_owned_name_is_preserved_instead_of_deleted(self) -> None:
        real_child = probe._run_child
        replacement: list[Path] = []

        def replace_owned_name(area: probe._OwnedArea, mode: str) -> int:
            code = real_child(area, mode)
            if mode == "interrupt":
                source = self.file(area.path / "unrelated-replacement", b"replacement owned by test, not probe")
                target = area.path / "replace.committed"
                self.assertNotEqual(probe._identity(source.stat()), probe._identity(target.stat()))
                os.replace(source, target)
                replacement.append(target)
            return code

        with patch.object(probe, "_run_child", side_effect=replace_owned_name):
            report = self.call_probe()
        self.assertEqual(report["overall"], "FAIL", report)
        self.assertEqual(replacement[0].read_bytes(), b"replacement owned by test, not probe")
        self.assertIn("owned_file_identity_changed", {item["code"] for item in report["cleanup"]["issues"]})

    def test_cleanup_failure_is_explicit_and_never_ignored(self) -> None:
        real_unlink = Path.unlink

        def deny_one(path: Path, *args, **kwargs):
            if path.name == "replace.committed" and path.parent.name.startswith(".sparkforge-storage-probe-"):
                raise PermissionError(r"C:\private\cleanup-path")
            return real_unlink(path, *args, **kwargs)

        with patch.object(Path, "unlink", new=deny_one):
            report = self.call_probe()
        self.assertTrue(all(item["outcome"] == "PASS" for item in report["checks"]))
        self.assertEqual(report["overall"], "FAIL", report)
        self.assertEqual(report["cleanup"]["outcome"], "FAIL")
        self.assertIn("file_cleanup_PermissionError", {item["code"] for item in report["cleanup"]["issues"]})
        self.assertNotIn("cleanup-path", json.dumps(report))
        self.assertTrue((self.root / report["probe_directory_name"] / "replace.committed").exists())


@unittest.skipUnless(os.name == "nt", "Windows local-drive classification required")
class StorageProbeCliTests(ProbeCase):
    def test_confirmed_cli_success_with_absolute_space_containing_root(self) -> None:
        code, report, error = self.cli("--root", str(self.root), "--scope-ref", "WP-016-cli", "--confirm-disposable")
        self.assertEqual(code, 0, report)
        self.assertEqual(error, "")
        self.assertEqual(report["overall"], "PASS")
        self.assertEqual(report["scope_ref"], "WP-016-cli")
        self.assertNotIn(str(self.root), json.dumps(report))
        self.assert_clean_root()

    def test_missing_required_arguments_or_confirmation_never_write(self) -> None:
        cases = (
            (),
            ("--root", str(self.root), "--scope-ref", "WP-016-cli"),
            ("--scope-ref", "WP-016-cli", "--confirm-disposable"),
            ("--root", str(self.root), "--confirm-disposable"),
            ("--root", str(self.root), "--scope-ref", "WP-016-cli", "--confirm-disposable", "--unknown-private-value"),
        )
        for arguments in cases:
            with self.subTest(argument_count=len(arguments)):
                code, report, error = self.cli(*arguments)
                self.assertEqual(code, 2, report)
                self.assertEqual(error, "")
                self.assertEqual(report["overall"], "BLOCKED")
                self.assertEqual(report["cleanup"]["outcome"], "NOT_NEEDED")
                self.assertIsNone(report["probe_directory_name"])
                self.assertNotIn("unknown-private-value", json.dumps(report))
                self.assert_clean_root()

    def test_confirmed_invalid_root_still_blocks_without_fallback(self) -> None:
        for root in (self.sentinel, self.root / "missing", Path(".")):
            with self.subTest(root_type=root.name):
                code, report, error = self.cli("--root", str(root), "--scope-ref", "WP-016-cli", "--confirm-disposable")
                self.assertEqual(code, 2, report)
                self.assertEqual(error, "")
                self.assertEqual(report["overall"], "BLOCKED")
                self.assert_clean_root()
                self.assertEqual(set(self.base.iterdir()), {self.root})

    def test_cli_failure_returns_one_and_preserves_json_verdict(self) -> None:
        failed = probe._new_report("WP-016-cli")
        failed["overall"] = "FAIL"
        output = io.StringIO()
        with patch.object(probe, "run_probe", return_value=failed), contextlib.redirect_stdout(output):
            code = probe.main(["--root", str(self.root), "--scope-ref", "WP-016-cli", "--confirm-disposable"])
        self.assertEqual(code, 1)
        self.assertEqual(json.loads(output.getvalue())["overall"], "FAIL")
        self.assert_clean_root()


if __name__ == "__main__":
    unittest.main()
