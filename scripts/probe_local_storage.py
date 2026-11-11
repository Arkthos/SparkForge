"""Disposable synthetic filesystem observations; never runtime-store qualification."""

from __future__ import annotations

import argparse
import ctypes
import json
import os
import re
import stat
import subprocess
import sys
import uuid
from pathlib import Path, PureWindowsPath
from typing import BinaryIO


SCOPE = "disposable_local_storage_probe"
CHECK_IDS = (
    "atomic_candidate_replace",
    "exclusive_create_conflict",
    "interrupted_publication",
)
FILE_NAMES = (
    "replace.committed",
    "replace.candidate",
    "writer.lock",
    "interrupt.committed",
    "interrupt.candidate",
)
CHILD_TIMEOUT_SECONDS = 5.0
STOP_TIMEOUT_SECONDS = 2.0
FILE_LIMIT = 256
CONFLICT_EXIT = 23
INTERRUPTION_EXIT = 73
CHILD_IO_EXIT = 74
CHILD_OWNERSHIP_EXIT = 75
CHILD_PROTOCOL_EXIT = 76
Identity = tuple[int, int]


class _Blocked(RuntimeError):
    pass


class _Failed(RuntimeError):
    pass


class _ArgumentsError(ValueError):
    pass


class _Parser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        # Default argparse errors can echo arbitrary caller-supplied paths.
        raise _ArgumentsError("invalid_cli_arguments")


def _valid_scope(value: object) -> bool:
    return isinstance(value, str) and re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,63}", value) is not None


def _redirected(info: os.stat_result) -> bool:
    # The name-surrogate bit distinguishes path redirection from cloud placeholders.
    return stat.S_ISLNK(info.st_mode) or bool(getattr(info, "st_reparse_tag", 0) & 0x20000000)


def _identity(info: os.stat_result) -> Identity:
    if not info.st_ino:
        raise _Blocked("file_identity_unavailable")
    return info.st_dev, info.st_ino


def _directory_identity(path: Path) -> Identity:
    info = path.lstat()
    if not stat.S_ISDIR(info.st_mode) or _redirected(info):
        raise _Blocked("directory_not_plain_or_redirected")
    return _identity(info)


def _drive_type(root: Path) -> int:
    try:
        function = ctypes.WinDLL("kernel32", use_last_error=True).GetDriveTypeW
        function.argtypes = [ctypes.c_wchar_p]
        function.restype = ctypes.c_uint
        return function(root.anchor)
    except OSError as error:
        raise _Blocked("drive_type_unavailable") from error


def _reserved_windows_name(name: str) -> bool:
    predicate = getattr(os.path, "isreserved", None)
    return predicate(name) if predicate is not None else PureWindowsPath(name).is_reserved()


def _validate_root(root: Path) -> Identity:
    if not isinstance(root, Path):
        raise _Blocked("root_must_be_path")
    if not root.is_absolute() or root == Path(root.anchor) or ".." in root.parts:
        raise _Blocked("root_not_explicit_safe_directory")
    if any(ord(character) < 32 for character in str(root)):
        raise _Blocked("root_contains_control_character")
    if os.name != "nt":
        raise _Blocked("platform_backing_not_qualified")
    if re.fullmatch(r"[A-Za-z]:", root.drive) is None:
        raise _Blocked("network_or_device_root_not_allowed")
    if any(":" in part or part.endswith((" ", ".")) or _reserved_windows_name(part) for part in root.parts[1:]):
        raise _Blocked("windows_root_name_unsafe")
    kind = _drive_type(root)
    if kind == 4:
        raise _Blocked("network_drive_not_allowed")
    if kind not in {2, 3, 6}:
        raise _Blocked("drive_type_not_qualified")
    try:
        for path in (*reversed(root.parents), root):
            info = path.lstat()
            if _redirected(info):
                raise _Blocked("root_component_redirected")
            if not stat.S_ISDIR(info.st_mode):
                raise _Blocked("root_not_directory")
        return _identity(info)
    except FileNotFoundError as error:
        raise _Blocked("root_missing") from error
    except NotADirectoryError as error:
        raise _Blocked("root_not_directory") from error


def _cleanup_report(outcome: str, issues: list[dict] | None = None) -> dict:
    return {
        "outcome": outcome,
        "issues": [] if issues is None else issues,
        "owned_files_removed": 0,
        "owned_directory_removed": False,
        "unconfirmed_owned_child_pid": None,
    }


def _new_report(scope_ref: object) -> dict:
    return {
        "scope": SCOPE,
        "scope_ref": scope_ref if _valid_scope(scope_ref) else None,
        "overall": "BLOCKED",
        "checks": [{"id": identifier, "outcome": "BLOCKED", "reason": "not_run"} for identifier in CHECK_IDS],
        "cleanup": _cleanup_report("NOT_NEEDED"),
        "probe_directory_name": None,
        "runtime_store_qualified": False,
        "diagnostics": [],
        "engineering_timeouts_seconds": {
            "child": CHILD_TIMEOUT_SECONDS,
            "owned_child_stop": STOP_TIMEOUT_SECONDS,
        },
        "limits": {
            "onedrive_cloud_synchronization": "NOT_ASSESSED",
            "power_loss_durability": "NOT_ASSESSED",
            "concurrent_reader_atomicity": "NOT_ASSESSED",
            "database_locking_and_transactions": "NOT_ASSESSED",
            "runtime_store_suitability": "NOT_ASSESSED",
            "mapped_or_virtual_storage_backing": "NOT_ASSESSED",
            "host_security_and_sandboxing": "NOT_ASSESSED",
            "product_recovery_and_acceptance": "NOT_ASSESSED",
            "hard_deadlines_for_kernel_filesystem_calls": "NOT_ASSESSED",
        },
    }


class _OwnedArea:
    def __init__(self, root: Path, root_identity: Identity) -> None:
        token = uuid.uuid4().hex
        self.root = root
        self.root_identity = root_identity
        self.path = root / (".sparkforge-storage-probe-" + token)
        self.created = False
        self.identity: Identity | None = None
        self.files: dict[str, Identity | None] = {}
        self.contents: dict[str, set[bytes]] = {}
        self.replacements: dict[str, str] = {}
        self.old = ("synthetic:" + token + ":committed\n").encode("ascii")
        self.new = ("synthetic:" + token + ":candidate\n").encode("ascii")
        self.writer = ("synthetic:" + token + ":writer\n").encode("ascii")
        self.child: subprocess.Popen | None = None
        self.stop_attempted = False
        self.stop_error: str | None = None

    def create(self) -> None:
        if _directory_identity(self.root) != self.root_identity:
            raise _Blocked("root_identity_changed")
        self.path.mkdir(mode=0o700, parents=False, exist_ok=False)
        self.created = True
        self.identity = _directory_identity(self.path)

    def guard(self) -> None:
        if self.identity is None:
            raise _Blocked("owned_directory_identity_unavailable")
        if _directory_identity(self.root) != self.root_identity:
            raise _Blocked("root_identity_changed")
        if _directory_identity(self.path) != self.identity:
            raise _Blocked("owned_directory_identity_changed")

    def create_file(self, name: str, data: bytes, allowed: set[bytes] | None = None) -> None:
        self.guard()
        if name not in FILE_NAMES or name in self.files:
            raise _Blocked("undeclared_or_repeated_probe_file")
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_BINARY", 0)
        descriptor = os.open(self.path / name, flags, 0o600)
        self.files[name] = None
        self.contents[name] = {data} if allowed is None else set(allowed)
        try:
            self.files[name] = _identity(os.fstat(descriptor))
            with os.fdopen(descriptor, "wb", closefd=False) as stream:
                stream.write(data)
                stream.flush()
        finally:
            os.close(descriptor)

    def accepted_identities(self, name: str) -> set[Identity]:
        values = (self.files.get(name), self.files.get(self.replacements.get(name, "")))
        return {value for value in values if value is not None}

    def open_owned(self, name: str, *, writable: bool = False) -> BinaryIO:
        self.guard()
        if name not in self.files:
            raise _Blocked("file_not_owned")
        flags = (os.O_RDWR if writable else os.O_RDONLY) | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
        info = (self.path / name).lstat()
        if _redirected(info) or not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
            raise _Blocked("owned_file_type_changed")
        if _identity(info) not in self.accepted_identities(name):
            raise _Blocked("owned_file_identity_changed")
        descriptor = os.open(self.path / name, flags)
        try:
            opened = os.fstat(descriptor)
            if not stat.S_ISREG(opened.st_mode) or opened.st_nlink != 1 or _identity(opened) != _identity(info):
                raise _Blocked("opened_file_identity_changed")
            return os.fdopen(descriptor, "r+b" if writable else "rb")
        except (OSError, _Blocked):
            os.close(descriptor)
            raise

    def read(self, name: str) -> bytes:
        with self.open_owned(name) as stream:
            return stream.read(FILE_LIMIT + 1)

    def stop_child(self) -> bool:
        if self.child is None:
            return True
        try:
            if self.child.poll() is not None:
                self.child = None
                return True
            if self.stop_attempted:
                return False
            self.stop_attempted = True
            self.child.kill()
            self.child.wait(timeout=STOP_TIMEOUT_SECONDS)
        except (OSError, subprocess.TimeoutExpired) as error:
            self.stop_error = type(error).__name__
            return False
        self.child = None
        return True

    def cleanup(self) -> dict:
        if not self.created:
            return _cleanup_report("NOT_NEEDED")
        if not self.stop_child():
            result = _cleanup_report("BLOCKED", [{"code": "owned_child_stop_unconfirmed", "error_type": self.stop_error}])
            result["unconfirmed_owned_child_pid"] = self.child.pid if self.child is not None else None
            return result
        result = _cleanup_report("PASS")
        try:
            self.guard()
        except (OSError, _Blocked) as error:
            code = str(error) if isinstance(error, _Blocked) else "directory_check_" + type(error).__name__
            return _cleanup_report("BLOCKED", [{"code": code}])
        for name in self.files:
            try:
                info = (self.path / name).lstat()
                content = self.read(name)
                if content not in self.contents[name]:
                    raise _Blocked("unexpected_content_preserved")
                self.guard()
                current = (self.path / name).lstat()
                if _identity(current) != _identity(info) or _redirected(current):
                    raise _Blocked("changed_file_preserved")
                (self.path / name).unlink()
                result["owned_files_removed"] += 1
            except FileNotFoundError:
                continue
            except (OSError, _Blocked) as error:
                code = str(error) if isinstance(error, _Blocked) else "file_cleanup_" + type(error).__name__
                result["issues"].append({"code": code, "file": name})
        try:
            self.guard()
            self.path.rmdir()
            result["owned_directory_removed"] = True
        except (OSError, _Blocked) as error:
            code = str(error) if isinstance(error, _Blocked) else "owned_directory_not_empty_or_unremovable"
            result["issues"].append({"code": code, "error_type": type(error).__name__})
        if result["issues"]:
            result["outcome"] = "FAIL"
        return result


_CHILD_SOURCE = r'''
import json
import os
import stat
import sys
from pathlib import Path


def matches(path, expected, directory=False):
    info = path.lstat()
    redirected = stat.S_ISLNK(info.st_mode) or bool(getattr(info, "st_reparse_tag", 0) & 0x20000000)
    kind = stat.S_ISDIR(info.st_mode) if directory else stat.S_ISREG(info.st_mode) and info.st_nlink == 1
    return not redirected and kind and [info.st_dev, info.st_ino] == expected


def main():
    mode, location, encoded = sys.argv[1:]
    spec = json.loads(encoded)
    folder = Path(location)
    if not matches(folder, spec["directory"], directory=True):
        return 75
    if mode == "exclusive":
        try:
            with (folder / "writer.lock").open("xb") as stream:
                stream.write(bytes.fromhex(spec["new"]))
        except FileExistsError:
            return 23
        return 0
    if mode not in ("replace", "interrupt"):
        return 76
    candidate = folder / (mode + ".candidate")
    committed = folder / (mode + ".committed")
    if not matches(candidate, spec["candidate"]) or not matches(committed, spec["committed"]):
        return 75
    flags = os.O_RDWR | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(candidate, flags)
    with os.fdopen(descriptor, "r+b") as stream:
        info = os.fstat(stream.fileno())
        if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1 or [info.st_dev, info.st_ino] != spec["candidate"]:
            return 75
        if stream.read(1):
            return 75
        stream.write(bytes.fromhex(spec["new"]))
        stream.flush()
        os.fsync(stream.fileno())
    if mode == "interrupt":
        os._exit(73)
    if not matches(folder, spec["directory"], directory=True) or not matches(candidate, spec["candidate"]) or not matches(committed, spec["committed"]):
        return 75
    os.replace(candidate, committed)
    return 0


try:
    os._exit(main())
except OSError:
    os._exit(74)
except (ValueError, KeyError, TypeError):
    os._exit(76)
'''


def _run_child(area: _OwnedArea, mode: str) -> int:
    area.guard()
    if area.child is not None:
        raise _Blocked("previous_child_not_reconciled")
    spec = {"directory": area.identity, "new": area.new.hex()}
    if mode in ("replace", "interrupt"):
        spec["candidate"] = area.files[mode + ".candidate"]
        spec["committed"] = area.files[mode + ".committed"]
    area.stop_attempted = False
    area.stop_error = None
    area.child = subprocess.Popen(
        [sys.executable, "-I", "-S", "-B", "-c", _CHILD_SOURCE, mode, str(area.path), json.dumps(spec)],
        cwd=area.path,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        shell=False,
        close_fds=True,
    )
    try:
        code = area.child.wait(timeout=CHILD_TIMEOUT_SECONDS)
    except subprocess.TimeoutExpired as error:
        stopped = area.stop_child()
        raise _Blocked("child_timeout_stopped" if stopped else "child_timeout_stop_unconfirmed") from error
    area.child = None
    if code == CHILD_IO_EXIT:
        raise _Blocked("child_filesystem_error")
    if code == CHILD_OWNERSHIP_EXIT:
        raise _Blocked("child_ownership_changed")
    if code == CHILD_PROTOCOL_EXIT:
        raise _Blocked("child_protocol_error")
    return code


def _prepare_publication(area: _OwnedArea, prefix: str) -> None:
    area.create_file(prefix + ".committed", area.old, {area.old, area.new})
    area.create_file(prefix + ".candidate", b"", {b"", area.new})
    if area.read(prefix + ".committed") != area.old:
        raise _Failed("initial_marker_mismatch")
    if prefix == "replace":
        # Replacement may finish before a timeout; both known file IDs remain ours.
        area.replacements[prefix + ".committed"] = prefix + ".candidate"


def _replace_check(area: _OwnedArea) -> dict:
    _prepare_publication(area, "replace")
    code = _run_child(area, "replace")
    if code != 0:
        raise _Failed("unexpected_child_exit_" + str(code))
    if area.read("replace.committed") != area.new:
        raise _Failed("replacement_marker_mismatch")
    try:
        (area.path / "replace.candidate").lstat()
    except FileNotFoundError:
        return {
            "child_exit_code": code, "initial_marker_matched": True,
            "replacement_marker_matched": True, "candidate_absent": True,
        }
    raise _Failed("replacement_candidate_still_present")


def _exclusive_check(area: _OwnedArea) -> dict:
    area.create_file("writer.lock", area.writer)
    with area.open_owned("writer.lock", writable=True):
        code = _run_child(area, "exclusive")
        if code != CONFLICT_EXIT:
            raise _Failed("exclusive_create_not_rejected_" + str(code))
        if area.read("writer.lock") != area.writer:
            raise _Failed("writer_content_changed")
    return {
        "child_exit_code": code, "exclusive_create_rejected": True,
        "owner_content_unchanged": True,
    }


def _interruption_check(area: _OwnedArea) -> dict:
    _prepare_publication(area, "interrupt")
    code = _run_child(area, "interrupt")
    if code != INTERRUPTION_EXIT:
        raise _Failed("expected_interruption_not_observed_" + str(code))
    if area.read("interrupt.committed") != area.old:
        raise _Failed("interrupted_marker_changed")
    if area.read("interrupt.candidate") != area.new:
        raise _Failed("interrupted_candidate_incomplete")
    return {
        "child_exit_code": code, "committed_marker_unchanged": True,
        "complete_unpublished_candidate_present": True,
    }


def _overall(report: dict) -> str:
    outcomes = [item["outcome"] for item in report["checks"]] + [report["cleanup"]["outcome"]]
    if "FAIL" in outcomes:
        return "FAIL"
    if all(outcome == "PASS" for outcome in outcomes) and not report["diagnostics"]:
        return "PASS"
    return "BLOCKED"


def run_probe(root: Path, *, scope_ref: str) -> dict:
    """Use only an explicitly authorized existing root; never choose a fallback."""
    report = _new_report(scope_ref)
    area: _OwnedArea | None = None
    try:
        if not _valid_scope(scope_ref):
            raise _Blocked("invalid_scope_ref")
        root_identity = _validate_root(root)
        area = _OwnedArea(root, root_identity)
        try:
            area.create()
        finally:
            if area.created:
                report["probe_directory_name"] = area.path.name
        for result, check in zip(report["checks"], (_replace_check, _exclusive_check, _interruption_check)):
            try:
                result["observations"] = check(area)
                result.update(outcome="PASS", reason="observed")
            except _Failed as error:
                result.update(outcome="FAIL", reason=str(error))
                break
            except _Blocked as error:
                result.update(outcome="BLOCKED", reason=str(error))
                break
            except OSError as error:
                result.update(outcome="BLOCKED", reason="filesystem_" + type(error).__name__)
                break
    except _Blocked as error:
        report["diagnostics"].append({"code": str(error)})
    except OSError as error:
        report["diagnostics"].append({"code": "filesystem_" + type(error).__name__})
    except KeyboardInterrupt:
        report["diagnostics"].append({"code": "operator_interrupted"})
    finally:
        if area is not None:
            report["cleanup"] = area.cleanup()
    report["overall"] = _overall(report)
    return report


def main(argv: list[str] | None = None) -> int:
    parser = _Parser(prog="probe_local_storage.py", description=__doc__)
    parser.add_argument("--root", required=True, help="Existing authorized absolute directory; no default.")
    parser.add_argument("--scope-ref", required=True, help="Non-sensitive scope label, 1-64 ASCII letters/digits/._-.")
    parser.add_argument("--confirm-disposable", action="store_true", help="Confirm newly owned synthetic artifacts and bounded owned children.")
    try:
        args = parser.parse_args(argv)
        if not args.confirm_disposable:
            raise _ArgumentsError("disposable_confirmation_required")
    except _ArgumentsError as error:
        report = _new_report(None)
        report["diagnostics"].append({"code": str(error)})
    else:
        report = run_probe(Path(args.root), scope_ref=args.scope_ref)
    print(json.dumps(report, sort_keys=True))
    return {"PASS": 0, "FAIL": 1, "BLOCKED": 2}[report["overall"]]


if __name__ == "__main__":
    raise SystemExit(main())
