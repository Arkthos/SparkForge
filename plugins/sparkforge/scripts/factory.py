"""Spec-bound local factory records and checks; host/operator authority stays external."""

from __future__ import annotations

import argparse
import ctypes
import hashlib
import json
import math
import os
import re
import sqlite3
import stat
import subprocess
import sys
import threading
import time
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path, PureWindowsPath


SPEC_VERSION = "sparkforge.spec.v1"
JOB_VERSION = "sparkforge.job.v1"
MAX_JSON_BYTES = 2 * 1024 * 1024
MAX_FILE_BYTES = 32 * 1024 * 1024
SPEC_FIELDS = {
    "schema_version", "id", "title", "problem", "audience", "environment",
    "builder_actor", "non_goals", "knowledge", "reuse", "controlled_files",
    "acceptance", "checks", "required_reviewers",
}


class FactoryError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


def fail(code: str, message: str) -> None:
    raise FactoryError(code, message)


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def canonical(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def digest(value: object) -> str:
    return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()


def _unique(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            fail("DUPLICATE_JSON_KEY", "Duplicate JSON object keys are not accepted.")
        result[key] = value
    return result


def _nonfinite(value: str) -> None:
    fail("INVALID_JSON", "Non-finite JSON numbers are not accepted.")


def load_json(path: Path) -> object:
    try:
        with path.open("rb") as stream:
            data = stream.read(MAX_JSON_BYTES + 1)
    except OSError as error:
        fail("INPUT_UNAVAILABLE", f"Cannot read the requested JSON input ({type(error).__name__}).")
    if len(data) > MAX_JSON_BYTES:
        fail("INPUT_TOO_LARGE", "JSON input exceeds the two-MiB record limit.")
    try:
        return json.loads(data.decode("utf-8"), object_pairs_hook=_unique, parse_constant=_nonfinite)
    except (UnicodeError, json.JSONDecodeError, RecursionError) as error:
        fail("INVALID_JSON", f"Cannot parse the JSON input ({type(error).__name__}).")


def _object(value: object, fields: set[str], label: str) -> dict:
    if type(value) is not dict or set(value) != fields:
        fail("INVALID_SPEC", f"{label} must contain exactly: {', '.join(sorted(fields))}.")
    return value


def _text(value: object, label: str, *, empty: bool = False, limit: int = 12000) -> str:
    if type(value) is not str or len(value) > limit or "\0" in value or (not empty and not value.strip()):
        fail("INVALID_SPEC", f"{label} must be {'optional' if empty else 'nonempty'} bounded text.")
    return value


def _list(value: object, label: str, *, minimum: int = 1, maximum: int = 128) -> list:
    if type(value) is not list or not minimum <= len(value) <= maximum:
        fail("INVALID_SPEC", f"{label} must have between {minimum} and {maximum} entries.")
    return value


def _strings(value: object, label: str, *, maximum: int = 128) -> list[str]:
    result = _list(value, label, maximum=maximum)
    for item in result:
        _text(item, label)
    if len(result) != len(set(result)):
        fail("INVALID_SPEC", f"{label} has duplicate entries.")
    return result


def _identifier(value: object, label: str) -> str:
    if type(value) is not str or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,79}", value):
        fail("INVALID_SPEC", f"{label} must be a short letters/digits/._- identifier.")
    return value


def _relative(value: object) -> str:
    _text(value, "controlled file", limit=500)
    path = PureWindowsPath(value)
    parts = value.replace("\\", "/").split("/")
    reserved = {"con", "prn", "aux", "nul", *(f"com{i}" for i in range(1, 10)), *(f"lpt{i}" for i in range(1, 10))}
    if path.is_absolute() or path.drive or any(
        not part or part in {".", ".."} or ":" in part or part.endswith((" ", "."))
        or part.split(".")[0].lower() in reserved
        or any(ord(char) < 32 for char in part)
        for part in parts
    ):
        fail("UNSAFE_PATH", "Controlled paths must be unambiguous relative files without traversal.")
    if any(part.lower() == ".git" for part in parts) or (
        parts[-1].startswith(".env") and parts[-1] != ".env.example"
    ):
        fail("UNSAFE_PATH", "Git internals and environment-secret files cannot be candidate inputs.")
    return "/".join(parts)


def validate_spec(value: object) -> dict:
    spec = _object(value, SPEC_FIELDS, "spec")
    if spec["schema_version"] != SPEC_VERSION:
        fail("UNSUPPORTED_SCHEMA", "Unsupported factory spec version.")
    for key in ("id", "builder_actor"):
        _identifier(spec[key], key)
    for key in ("title", "problem", "audience"):
        _text(spec[key], key)
    if spec["environment"] not in ("LOCAL_DEVELOPMENT", "CORP", "ACRO"):
        fail("INVALID_SPEC", "An explicit supported environment is required.")
    _strings(spec["non_goals"], "non_goals")
    knowledge = _object(spec["knowledge"], {
        "wiki_revision", "repository_revision", "citations", "coverage", "limitations",
    }, "knowledge")
    for key in ("wiki_revision", "repository_revision"):
        _text(knowledge[key], key, limit=200)
    if knowledge["coverage"] not in ("SNAPSHOT_SCOPE", "CURRENT_SCOPE"):
        fail("KNOWLEDGE_NOT_ASSESSED", "The spec needs an explicit assessed source scope, not an absence assumption.")
    _strings(knowledge["limitations"], "knowledge limitations")
    sources = set()
    citation_ids = set()
    for item in _list(knowledge["citations"], "citations"):
        citation = _object(item, {"source", "locator", "revision", "sha256"}, "citation")
        if citation["source"] not in ("wiki", "repository"):
            fail("INVALID_SPEC", "Citation source must be wiki or repository.")
        for key in ("locator", "revision"):
            _text(citation[key], f"citation {key}", limit=4000)
        if type(citation["sha256"]) is not str or not re.fullmatch(r"[0-9a-f]{64}", citation["sha256"]):
            fail("INVALID_SPEC", "Each citation requires an exact SHA-256.")
        if citation["revision"] != knowledge["wiki_revision" if citation["source"] == "wiki" else "repository_revision"]:
            fail("FOREIGN_SOURCE_REVISION", "Citation and declared source baseline disagree.")
        identity = (citation["source"], citation["locator"])
        if identity in citation_ids:
            fail("INVALID_SPEC", "Duplicate source citation.")
        citation_ids.add(identity)
        sources.add(citation["source"])
    if sources != {"wiki", "repository"}:
        fail("KNOWLEDGE_NOT_ASSESSED", "Both wiki guidance and repository comparison must be cited.")
    reuse = _object(spec["reuse"], {"decision", "target", "rationale", "inspected_candidates"}, "reuse")
    if reuse["decision"] not in ("REUSE", "UPDATE_EXISTING", "NEW_COMPONENT"):
        fail("REUSE_DECISION_MISSING", "Choose and justify REUSE, UPDATE_EXISTING or NEW_COMPONENT.")
    _text(reuse["target"], "reuse target", empty=reuse["decision"] == "NEW_COMPONENT")
    _text(reuse["rationale"], "reuse rationale")
    _strings(reuse["inspected_candidates"], "inspected candidates")
    normalized = [_relative(item) for item in _strings(spec["controlled_files"], "controlled_files", maximum=512)]
    if len(normalized) != len({item.casefold() for item in normalized}):
        fail("UNSAFE_PATH", "Controlled paths must not alias each other.")
    check_ids = set()
    for item in _list(spec["checks"], "checks", maximum=64):
        check = _object(item, {
            "id", "argv", "timeout_seconds", "output_limit_bytes", "max_attempts",
            "required_markers", "retain_output",
        }, "check")
        _identifier(check["id"], "check id")
        if check["id"] in check_ids:
            fail("INVALID_SPEC", "Check IDs must be unique.")
        check_ids.add(check["id"])
        for argument in _list(check["argv"], "check argv", maximum=128):
            _text(argument, "command argument", empty=True, limit=16000)
        executable = check["argv"][0]
        if executable != "python" and not Path(executable).is_absolute():
            fail("INVALID_SPEC", "Use the current 'python' interpreter or an explicit absolute executable.")
        timeout = check["timeout_seconds"]
        if type(timeout) not in (int, float) or not math.isfinite(timeout) or not 0 < timeout <= 3600:
            fail("INVALID_SPEC", "Each check needs an explicit finite timeout in (0, 3600] seconds.")
        if type(check["output_limit_bytes"]) is not int or not 1 <= check["output_limit_bytes"] <= 16 * 1024 * 1024:
            fail("INVALID_SPEC", "Each check needs an explicit output limit of 1 byte to 16 MiB.")
        if type(check["max_attempts"]) is not int or not 1 <= check["max_attempts"] <= 20:
            fail("INVALID_SPEC", "Each check needs an explicit attempt limit between 1 and 20.")
        _strings(check["required_markers"], "required output markers", maximum=32)
        if type(check["retain_output"]) is not bool:
            fail("INVALID_SPEC", "retain_output must be explicitly true or false.")
    criteria = set()
    covered_checks = set()
    for item in _list(spec["acceptance"], "acceptance"):
        criterion = _object(item, {"id", "behavior", "checks"}, "criterion")
        _identifier(criterion["id"], "criterion id")
        if criterion["id"] in criteria:
            fail("INVALID_SPEC", "Acceptance criterion IDs must be unique.")
        criteria.add(criterion["id"])
        _text(criterion["behavior"], "observable acceptance")
        refs = set(_strings(criterion["checks"], "criterion checks"))
        if not refs <= check_ids:
            fail("INVALID_SPEC", "Acceptance refers to unknown check IDs.")
        covered_checks.update(refs)
    if covered_checks != check_ids:
        fail("INVALID_SPEC", "Every check must trace to observable acceptance.")
    for role in _strings(spec["required_reviewers"], "required_reviewers", maximum=16):
        _identifier(role, "reviewer role")
    return json.loads(canonical(spec))


def _redirected(info: os.stat_result) -> bool:
    return stat.S_ISLNK(info.st_mode) or bool(getattr(info, "st_reparse_tag", 0) & 0x20000000)


def _directory(path: Path) -> Path:
    if (not isinstance(path, Path) or not path.is_absolute() or ".." in path.parts
            or path == Path(path.anchor) or str(path).startswith(("\\\\", "//"))):
        fail("UNSAFE_PATH", "Use an explicit existing absolute directory without traversal.")
    if os.name == "nt":
        if not re.fullmatch(r"[A-Za-z]:", path.drive):
            fail("UNSAFE_PATH", "Network, device and ambiguous drive paths are not local workspaces.")
        try:
            query = ctypes.WinDLL("kernel32", use_last_error=True).GetDriveTypeW
            query.argtypes = [ctypes.c_wchar_p]
            query.restype = ctypes.c_uint
            kind = query(path.anchor)
        except OSError:
            fail("STORAGE_UNQUALIFIED", "The local drive class could not be established.")
        if kind not in (2, 3, 6):
            fail("STORAGE_UNQUALIFIED", "Network, missing or unknown drive classes are not accepted for local jobs.")
    try:
        for component in (*reversed(path.parents), path):
            info = component.lstat()
            if not stat.S_ISDIR(info.st_mode) or _redirected(info):
                fail("UNSAFE_PATH", "The directory route must not contain links or redirected components.")
    except OSError as error:
        fail("DIRECTORY_UNAVAILABLE", f"Directory inspection failed ({type(error).__name__}).")
    return path.resolve()


def _file(root: Path, relative: str) -> Path:
    parts = _relative(relative).split("/")
    path = root.joinpath(*parts)
    for parent in path.parents:
        if parent == root:
            break
        if parent.exists() and _redirected(parent.lstat()):
            fail("UNSAFE_PATH", "Candidate file traverses a redirected directory.")
    try:
        info = path.lstat()
        if not stat.S_ISREG(info.st_mode) or _redirected(info) or info.st_nlink != 1:
            fail("UNSAFE_PATH", "Candidate input must be a plain, non-aliased file.")
        if not path.resolve().is_relative_to(root):
            fail("UNSAFE_PATH", "Candidate path escaped its approved root.")
        if info.st_size > MAX_FILE_BYTES:
            fail("INPUT_TOO_LARGE", "A controlled file exceeds the 32-MiB inspection limit.")
    except OSError as error:
        fail("CANDIDATE_UNAVAILABLE", f"A required controlled file is unavailable ({type(error).__name__}).")
    return path


def candidate_manifest(workspace: Path, spec: dict) -> dict:
    root = _directory(workspace)
    files = []
    for name in sorted(spec["controlled_files"], key=str.casefold):
        path = _file(root, name)
        with path.open("rb") as stream:
            data = stream.read(MAX_FILE_BYTES + 1)
        if len(data) > MAX_FILE_BYTES:
            fail("INPUT_TOO_LARGE", "Controlled input grew beyond its inspection limit.")
        files.append({"path": _relative(name), "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)})
    return {"sha256": digest(files), "files": files}


def _db_path(job_dir: Path) -> Path:
    root = _directory(job_dir)
    path = root / "job.sqlite3"
    try:
        info = path.lstat()
        if not stat.S_ISREG(info.st_mode) or _redirected(info) or info.st_nlink != 1:
            fail("INVALID_JOB", "Job database is not an owned plain file.")
    except OSError as error:
        fail("INVALID_JOB", f"Job database is unavailable ({type(error).__name__}).")
    return path


def _connection(job_dir: Path) -> sqlite3.Connection:
    connection = sqlite3.connect(_db_path(job_dir).as_uri() + "?mode=rw", uri=True, timeout=0, isolation_level=None)
    connection.row_factory = sqlite3.Row
    return connection


def _state(connection: sqlite3.Connection) -> dict:
    row = connection.execute("SELECT body FROM state WHERE id = 1").fetchone()
    if row is None:
        fail("INVALID_JOB", "Missing job state.")
    state = json.loads(row["body"], object_pairs_hook=_unique, parse_constant=_nonfinite)
    required = {
        "schema_version", "job_id", "created_at", "spec", "spec_sha", "revision",
        "workspace", "decision", "cancelled", "active_run", "candidate", "round_id",
        "attempts", "reviews", "previous_specs", "check_sequence",
    }
    if type(state) is not dict or set(state) != required or state.get("schema_version") != JOB_VERSION:
        fail("INVALID_JOB", "Unsupported job state.")
    if any(type(state[key]) is not list for key in ("attempts", "reviews", "previous_specs")):
        fail("INVALID_JOB", "Job histories must be explicit arrays.")
    if type(state["revision"]) is not int or state["revision"] < 1:
        fail("INVALID_JOB", "Invalid job revision.")
    if type(state["check_sequence"]) is not int or state["check_sequence"] < 0:
        fail("INVALID_JOB", "Invalid check-evidence sequence.")
    if state["check_sequence"] != len(state["attempts"]):
        fail("INVALID_JOB", "Check sequence disagrees with the append-only reservation history.")
    if type(state["cancelled"]) is not bool or any(
        type(state[key]) is not str or not state[key] for key in ("job_id", "workspace", "spec_sha")
    ):
        fail("INVALID_JOB", "Invalid job identity or cancellation state.")
    spec = validate_spec(state.get("spec"))
    if digest(spec) != state.get("spec_sha"):
        fail("SPEC_TAMPERED", "Stored spec content and frozen digest disagree.")
    specifications = {state["spec_sha"]: spec}
    old_revisions = set()
    for previous in state["previous_specs"]:
        if type(previous) is not dict or set(previous) != {"spec", "spec_sha", "revision"}:
            fail("INVALID_JOB", "Malformed specification history.")
        old_spec = validate_spec(previous["spec"])
        if (previous["spec_sha"] != digest(old_spec) or old_spec["id"] != spec["id"]
                or type(previous["revision"]) is not int or previous["revision"] in old_revisions
                or not 1 <= previous["revision"] < state["revision"]):
            fail("INVALID_JOB", "Foreign or inconsistent specification history.")
        old_revisions.add(previous["revision"])
        specifications[previous["spec_sha"]] = old_spec
    if old_revisions != set(range(1, state["revision"])):
        fail("INVALID_JOB", "Specification revision history is incomplete.")
    if state["decision"] is not None and (
        type(state["decision"]) is not dict
        or set(state["decision"]) != {"decision", "actor", "spec_sha", "recorded_at", "origin"}
        or state["decision"]["decision"] not in ("accept", "reject", "changes")
        or state["decision"]["spec_sha"] != state["spec_sha"]
        or state["decision"]["origin"] != "OPERATOR_ASSERTION"
        or type(state["decision"]["actor"]) is not str or not state["decision"]["actor"].strip()
    ):
        fail("INVALID_JOB", "Invalid or foreign decision record.")
    candidate = state["candidate"]
    if candidate is not None and (
        type(candidate) is not dict or set(candidate) != {"sha256", "files"}
        or type(candidate["files"]) is not list or digest(candidate["files"]) != candidate["sha256"]
    ):
        fail("INVALID_JOB", "Invalid candidate manifest.")
    if (state["round_id"] is not None and type(state["round_id"]) is not str
            or (candidate is None) != (state["round_id"] is None)):
        fail("INVALID_JOB", "Candidate and check-round identity must agree.")
    run_ids = set()
    attempt_counts = {}
    for item in state["attempts"]:
        fields = {"run_id", "job_id", "check_id", "spec_sha", "candidate_sha", "round_id", "argv", "outcome", "started_at"}
        if type(item) is not dict or not fields <= set(item):
            fail("INVALID_JOB", "Malformed check history.")
        if any(type(item[key]) is not str or not item[key] for key in ("run_id", "check_id", "spec_sha", "candidate_sha", "round_id")):
            fail("INVALID_JOB", "Malformed check binding.")
        if item["job_id"] != state["job_id"] or item["run_id"] in run_ids:
            fail("INVALID_JOB", "Duplicate or foreign run history.")
        if item["outcome"] not in ("RUNNING", "PASS", "FAIL", "ERROR", "CANCELLED"):
            fail("INVALID_JOB", "Unknown check outcome.")
        runner = item.get("runner")
        if (item.get("origin") != "LOCAL_RUNNER" or type(runner) is not dict
                or set(runner) != {"implementation_sha256", "python_version"}
                or type(runner["implementation_sha256"]) is not str
                or not re.fullmatch(r"[0-9a-f]{64}", runner["implementation_sha256"])
                or type(runner["python_version"]) is not str
                or not re.fullmatch(r"[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}", runner["python_version"])):
            fail("INVALID_EVIDENCE", "The record lacks a consistent local runner receipt.")
        bound_spec = specifications.get(item["spec_sha"])
        bound_check = next((check for check in bound_spec["checks"] if check["id"] == item["check_id"]), None) if bound_spec else None
        if bound_check is None or item["argv"] != bound_check["argv"]:
            fail("INVALID_EVIDENCE", "Stored check command is not in its frozen specification.")
        if not re.fullmatch(r"[0-9a-f]{64}", item["candidate_sha"]):
            fail("INVALID_EVIDENCE", "Invalid stored candidate digest.")
        if item["spec_sha"] == state["spec_sha"] and item["round_id"] == state["round_id"]:
            if not state["candidate"] or item["candidate_sha"] != state["candidate"].get("sha256"):
                fail("INVALID_EVIDENCE", "Check receipt and its candidate round disagree.")
        if item["outcome"] == "PASS":
            complete = {
                "completed_at", "exit_code", "reason", "uncertain", "output_truncated",
                "missing_markers", "output_sha256", "output_bytes_observed", "duration_seconds",
            } <= set(item)
            if not complete or (
                type(item["exit_code"]) is not int or item["exit_code"] != 0
                or item["reason"] != "EXPECTED_RESULT_OBSERVED"
                or item["uncertain"] is not False or item["output_truncated"] is not False
                or item["missing_markers"] != []
                or type(item["output_sha256"]) is not str
                or not re.fullmatch(r"[0-9a-f]{64}", item["output_sha256"])
                or type(item["output_bytes_observed"]) is not int
                or not 0 < item["output_bytes_observed"] <= bound_check["output_limit_bytes"]
                or type(item["duration_seconds"]) not in (int, float)
                or not math.isfinite(item["duration_seconds"])
                or not 0 <= item["duration_seconds"] <= bound_check["timeout_seconds"]
                or type(item["completed_at"]) is not str or not item["completed_at"]
            ):
                fail("INVALID_EVIDENCE", "A passing check receipt has incomplete or contradictory observations.")
            if bound_check["retain_output"] and (
                type(item.get("retained_output")) is not str
                or any(marker not in item["retained_output"] for marker in bound_check["required_markers"])
            ):
                fail("INVALID_EVIDENCE", "Retained check output contradicts its passing receipt.")
        count_key = (item["spec_sha"], item["check_id"])
        attempt_counts[count_key] = attempt_counts.get(count_key, 0) + 1
        if attempt_counts[count_key] > bound_check["max_attempts"]:
            fail("INVALID_EVIDENCE", "Stored attempts exceed their accepted allowance.")
        run_ids.add(item["run_id"])
    for item in state["reviews"]:
        fields = {"role", "decision", "actor", "notes", "candidate_sha", "spec_sha", "round_id", "check_sequence", "recorded_at", "origin"}
        if type(item) is not dict or set(item) != fields or item["decision"] not in ("pass", "changes", "incomplete"):
            fail("INVALID_JOB", "Malformed review history.")
        if type(item["role"]) is not str or type(item["check_sequence"]) is not int:
            fail("INVALID_JOB", "Invalid reviewer or evidence binding.")
        bound_spec = specifications.get(item["spec_sha"]) if type(item["spec_sha"]) is str else None
        if (bound_spec is None or item["role"] not in bound_spec["required_reviewers"]
                or type(item["actor"]) is not str or not item["actor"].strip()
                or item["actor"] == bound_spec["builder_actor"]
                or item["origin"] != "REVIEWER_ASSERTION"
                or type(item["notes"]) is not str or not item["notes"].strip()
                or type(item["candidate_sha"]) is not str
                or not re.fullmatch(r"[0-9a-f]{64}", item["candidate_sha"])
                or not 1 <= item["check_sequence"] <= state["check_sequence"]):
            fail("INVALID_REVIEW", "Stored reviewer assertion violates its accepted review contract.")
        if item["spec_sha"] == state["spec_sha"] and item["round_id"] == state["round_id"]:
            if not state["candidate"] or item["candidate_sha"] != state["candidate"].get("sha256"):
                fail("INVALID_REVIEW", "Stored review and its candidate round disagree.")
    active = state["active_run"]
    if active is not None and (
        type(active) is not dict or set(active) != {"run_id", "pid", "uncertain"}
        or type(active["run_id"]) is not str or active["run_id"] not in run_ids
        or type(active["uncertain"]) is not bool
        or (active["pid"] is not None and (type(active["pid"]) is not int or active["pid"] <= 0))
    ):
        fail("INVALID_JOB", "Invalid active-run reservation.")
    return state


def _event(connection: sqlite3.Connection, state: dict, kind: str, payload: dict) -> None:
    connection.execute(
        "INSERT INTO events(recorded_at, kind, spec_sha, payload) VALUES (?, ?, ?, ?)",
        (now(), kind, state["spec_sha"], canonical(payload)),
    )


@contextmanager
def _transaction(job_dir: Path):
    connection = _connection(job_dir)
    try:
        connection.execute("BEGIN IMMEDIATE")
        state = _state(connection)
        yield connection, state
        connection.execute("UPDATE state SET body = ? WHERE id = 1", (canonical(state),))
        connection.execute("COMMIT")
    except BaseException:
        if connection.in_transaction:
            connection.execute("ROLLBACK")
        raise
    finally:
        connection.close()


def init_job(spec: dict, workspace: Path, job_dir: Path) -> dict:
    spec = validate_spec(spec)
    workspace = _directory(workspace)
    if not job_dir.is_absolute() or ".." in job_dir.parts or job_dir == Path(job_dir.anchor):
        fail("UNSAFE_PATH", "The job directory must be a new explicit absolute directory.")
    parent = _directory(job_dir.parent)
    job_dir = parent / job_dir.name
    if job_dir.is_relative_to(workspace) or workspace.is_relative_to(job_dir):
        fail("OVERLAPPING_STATE", "Job state must be separate from the candidate workspace.")
    if job_dir.exists():
        fail("JOB_EXISTS", "Use a fresh job directory; existing content is never adopted or overwritten.")
    job_dir.mkdir(mode=0o700)
    state = {
        "schema_version": JOB_VERSION, "job_id": str(uuid.uuid4()),
        "created_at": now(), "spec": spec, "spec_sha": digest(spec),
        "revision": 1, "workspace": str(workspace), "decision": None,
        "cancelled": False, "active_run": None, "candidate": None, "round_id": None,
        "attempts": [], "reviews": [], "previous_specs": [], "check_sequence": 0,
    }
    connection = sqlite3.connect(job_dir / "job.sqlite3", timeout=0, isolation_level=None)
    try:
        connection.execute("BEGIN IMMEDIATE")
        connection.execute("CREATE TABLE state(id INTEGER PRIMARY KEY CHECK(id=1), body TEXT NOT NULL)")
        connection.execute("CREATE TABLE events(seq INTEGER PRIMARY KEY, recorded_at TEXT NOT NULL, kind TEXT NOT NULL, spec_sha TEXT NOT NULL, payload TEXT NOT NULL)")
        connection.execute("INSERT INTO state(id, body) VALUES (1, ?)", (canonical(state),))
        _event(connection, state, "SPEC_PROPOSED", {"revision": 1})
        connection.execute("COMMIT")
    except BaseException:
        if connection.in_transaction:
            connection.execute("ROLLBACK")
        raise
    finally:
        connection.close()
    return job_status(job_dir)


def _approved(state: dict) -> bool:
    decision = state["decision"]
    return bool(decision and decision["decision"] == "accept" and decision["spec_sha"] == state["spec_sha"])


def decide(job_dir: Path, spec_sha: str, decision: str, actor: str) -> dict:
    _identifier(actor, "operator actor")
    if decision not in ("accept", "reject", "changes"):
        fail("INVALID_DECISION", "Use accept, reject or changes.")
    with _transaction(job_dir) as (connection, state):
        if state["active_run"]:
            fail("ACTIVE_EXECUTION", "Stop or reconcile active execution before changing its authority.")
        if spec_sha != state["spec_sha"]:
            fail("STALE_SPEC", "The decision does not name the current frozen specification.")
        state["decision"] = {
            "decision": decision, "actor": actor, "spec_sha": spec_sha,
            "recorded_at": now(), "origin": "OPERATOR_ASSERTION",
        }
        _event(connection, state, "SPEC_DECISION", state["decision"])
    return job_status(job_dir)


def revise(job_dir: Path, spec: dict) -> dict:
    spec = validate_spec(spec)
    with _transaction(job_dir) as (connection, state):
        if state["active_run"]:
            fail("ACTIVE_EXECUTION", "Reconcile active execution before replacing the specification.")
        if spec["id"] != state["spec"]["id"]:
            fail("FOREIGN_SPEC", "A revision must retain this job's spec identity.")
        if digest(spec) == state["spec_sha"]:
            fail("UNCHANGED_SPEC", "An unchanged spec cannot reset approval or attempt limits.")
        state["previous_specs"].append({"spec": state["spec"], "spec_sha": state["spec_sha"], "revision": state["revision"]})
        state.update(spec=spec, spec_sha=digest(spec), revision=state["revision"] + 1,
                     decision=None, cancelled=False, candidate=None, round_id=None)
        _event(connection, state, "SPEC_REVISED", {"revision": state["revision"], "approval_invalidated": True})
    return job_status(job_dir)


def cancel(job_dir: Path, reason: str) -> dict:
    _text(reason, "cancellation reason", limit=2000)
    with _transaction(job_dir) as (connection, state):
        state["cancelled"] = True
        _event(connection, state, "CANCEL_REQUESTED", {"reason": reason})
    return job_status(job_dir)


def _current_results(state: dict, candidate: dict | None) -> tuple[dict, dict]:
    checks, reviews = {}, {}
    if not candidate or not state["candidate"] or candidate["sha256"] != state["candidate"]["sha256"]:
        return checks, reviews
    for result in state["attempts"]:
        if (result["spec_sha"] == state["spec_sha"] and result["round_id"] == state["round_id"]
                and result["candidate_sha"] == candidate["sha256"]):
            checks[result["check_id"]] = result
    for result in state["reviews"]:
        if (result["spec_sha"] == state["spec_sha"] and result["round_id"] == state["round_id"]
                and result["check_sequence"] == state["check_sequence"]
                and result["candidate_sha"] == candidate["sha256"]):
            reviews[result["role"]] = result
    return checks, reviews


def _review_context(state: dict, candidate: dict | None) -> str | None:
    if not candidate or not state["candidate"] or candidate["sha256"] != state["candidate"]["sha256"]:
        return None
    return digest({
        "job_id": state["job_id"], "spec_sha": state["spec_sha"],
        "candidate_sha": candidate["sha256"], "round_id": state["round_id"],
        "check_sequence": state["check_sequence"],
    })


def job_status(job_dir: Path) -> dict:
    connection = _connection(job_dir)
    try:
        state = _state(connection)
        sequence = connection.execute("SELECT COALESCE(MAX(seq),0) FROM events").fetchone()[0]
    finally:
        connection.close()
    candidate, candidate_error = None, None
    try:
        candidate = candidate_manifest(Path(state["workspace"]), state["spec"])
    except (FactoryError, OSError) as error:
        candidate_error = error.code if isinstance(error, FactoryError) else type(error).__name__
    checks, reviews = _current_results(state, candidate)
    check_states = [
        {"id": check["id"], "outcome": checks.get(check["id"], {}).get("outcome", "NOT_RUN"),
         "run_id": checks.get(check["id"], {}).get("run_id")}
        for check in state["spec"]["checks"]
    ]
    review_states = [
        {"role": role, "decision": reviews.get(role, {}).get("decision", "MISSING")}
        for role in state["spec"]["required_reviewers"]
    ]
    if state["active_run"]:
        status = "RECONCILIATION_REQUIRED" if state["active_run"].get("uncertain") else "RUNNING_OR_INTERRUPTED"
    elif state["cancelled"]:
        status = "CANCELLED"
    elif not _approved(state):
        status = "REJECTED" if state["decision"] and state["decision"]["decision"] == "reject" else "AWAITING_APPROVAL"
    elif candidate_error:
        status = "IMPLEMENTATION_REQUIRED"
    elif state["candidate"] and candidate["sha256"] != state["candidate"]["sha256"]:
        status = "STALE_CANDIDATE"
    elif any(item["outcome"] not in ("PASS", "NOT_RUN") for item in check_states):
        status = "CHECKS_FAILED"
    elif any(item["outcome"] == "NOT_RUN" for item in check_states):
        status = "CHECKS_PENDING"
    elif any(item["decision"] in ("changes", "incomplete") for item in review_states):
        status = "CHANGES_REQUIRED"
    elif any(item["decision"] == "MISSING" for item in review_states):
        status = "REVIEW_PENDING"
    else:
        status = "CANDIDATE_VERIFIED"
    return {
        "scope": "assisted_local_factory", "job_id": state["job_id"], "spec_id": state["spec"]["id"],
        "environment": state["spec"]["environment"],
        "knowledge_scope": state["spec"]["knowledge"]["coverage"],
        "source_revisions": {
            "wiki": state["spec"]["knowledge"]["wiki_revision"],
            "repository": state["spec"]["knowledge"]["repository_revision"],
        },
        "reuse_decision": state["spec"]["reuse"]["decision"],
        "revision": state["revision"], "spec_sha": state["spec_sha"], "status": status,
        "event_sequence": sequence, "decision": state["decision"],
        "candidate_sha": candidate["sha256"] if candidate else None,
        "candidate_error": candidate_error, "checks": check_states, "reviews": review_states,
        "review_context": _review_context(state, candidate),
        "round_id": state["round_id"], "check_sequence": state["check_sequence"],
        "active_run": state["active_run"], "attempt_count": len(state["attempts"]),
        "review_count": len(state["reviews"]), "human_acceptance_required": True,
        "approval_authenticity": "HOST_OR_OPERATOR_RESPONSIBILITY",
        "host_security_qualified": False, "publication_authorized": False,
        "current_source_permission_and_freshness": "HOST_OR_OPERATOR_RESPONSIBILITY",
    }


def record_review(
    job_dir: Path, candidate_sha: str, role: str, decision: str, actor: str, notes: str,
    *, review_context: str | None = None,
) -> dict:
    _identifier(actor, "review actor")
    _text(notes, "review notes", limit=12000)
    if decision not in ("pass", "changes", "incomplete"):
        fail("INVALID_REVIEW", "Use pass, changes or incomplete.")
    with _transaction(job_dir) as (connection, state):
        if state["active_run"] or state["cancelled"] or not _approved(state):
            fail("REVIEW_BLOCKED", "A current approved, non-active candidate is required.")
        if role not in state["spec"]["required_reviewers"]:
            fail("UNKNOWN_REVIEWER", "The reviewer role is not in the accepted inventory.")
        if actor == state["spec"]["builder_actor"]:
            fail("SELF_REVIEW", "The declared builder cannot satisfy an independent reviewer role.")
        candidate = candidate_manifest(Path(state["workspace"]), state["spec"])
        if candidate_sha != candidate["sha256"] or not state["candidate"] or state["candidate"]["sha256"] != candidate_sha:
            fail("STALE_CANDIDATE", "The review does not name the current checked candidate.")
        if review_context is None:
            fail("REVIEW_CONTEXT_REQUIRED", "Capture the review context from status before reviewing this candidate.")
        if review_context != _review_context(state, candidate):
            fail("STALE_REVIEW", "The spec or check evidence changed since this review context was captured; review again.")
        checks, _ = _current_results(state, candidate)
        if any(checks.get(check["id"], {}).get("outcome") != "PASS" for check in state["spec"]["checks"]):
            fail("CHECKS_INCOMPLETE", "All required checks must pass for this candidate before review admission.")
        record = {
            "role": role, "decision": decision, "actor": actor, "notes": notes,
            "candidate_sha": candidate_sha, "spec_sha": state["spec_sha"],
            "round_id": state["round_id"], "recorded_at": now(), "origin": "REVIEWER_ASSERTION",
            "check_sequence": state["check_sequence"],
        }
        state["reviews"].append(record)
        _event(connection, state, "REVIEW_RECORDED", record)
    return job_status(job_dir)


def _cancelled(job_dir: Path, run_id: str) -> bool:
    connection = _connection(job_dir)
    try:
        state = _state(connection)
        if not state["active_run"] or state["active_run"]["run_id"] != run_id:
            fail("RUN_OWNERSHIP_CHANGED", "Active run identity changed during execution.")
        return state["cancelled"]
    finally:
        connection.close()


def _execute(job_dir: Path, run_id: str, check: dict, workspace: Path) -> dict:
    argv = list(check["argv"])
    if argv[0] == "python":
        argv[0] = sys.executable
    if not Path(argv[0]).is_file():
        return {"outcome": "ERROR", "reason": "EXECUTABLE_UNAVAILABLE", "exit_code": None, "uncertain": False}
    output = bytearray()
    output_total = 0
    over_limit = threading.Event()
    reader_error: list[str] = []
    process: subprocess.Popen | None = None
    reader: threading.Thread | None = None
    reason = None
    uncertain = False
    execution_fault = False
    started = time.monotonic()
    try:
        with _transaction(job_dir) as (connection, state):
            if state["cancelled"] or not state["active_run"] or state["active_run"]["run_id"] != run_id:
                return {"outcome": "CANCELLED", "reason": "CANCELLED_BEFORE_DISPATCH", "exit_code": None, "uncertain": False}
            environment = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
            process = subprocess.Popen(
                argv, cwd=workspace, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT, shell=False, close_fds=True, env=environment,
            )
            state["active_run"]["pid"] = process.pid
            _event(connection, state, "CHECK_DISPATCHED", {"run_id": run_id, "pid": process.pid})

        def drain() -> None:
            nonlocal output_total
            try:
                while True:
                    chunk = process.stdout.read1(4096)
                    if not chunk:
                        break
                    output_total += len(chunk)
                    remaining = check["output_limit_bytes"] - len(output)
                    output.extend(chunk[:max(0, remaining)])
                    if output_total > check["output_limit_bytes"]:
                        over_limit.set()
            except OSError as error:
                reader_error.append(type(error).__name__)

        reader = threading.Thread(target=drain, daemon=True)
        reader.start()
        while process.poll() is None:
            if over_limit.is_set():
                reason = "OUTPUT_LIMIT"
                break
            if time.monotonic() - started >= check["timeout_seconds"]:
                reason = "TIMEOUT"
                break
            if _cancelled(job_dir, run_id):
                reason = "CANCELLED"
                break
            time.sleep(0.03)
    except KeyboardInterrupt:
        reason = "INTERRUPTED"
        execution_fault = True
    except (OSError, sqlite3.Error, FactoryError) as error:
        reason = error.code if isinstance(error, FactoryError) else type(error).__name__
        execution_fault = True
    finally:
        if process is not None and process.poll() is None:
            uncertain = True
            try:
                process.kill()
                process.wait(timeout=2)
            except (OSError, subprocess.TimeoutExpired):
                uncertain = True
        if reader is not None:
            reader.join(timeout=2)
            if reader.is_alive():
                uncertain = True
                reason = reason or "OUTPUT_INCOMPLETE"
            elif process is not None and process.stdout is not None:
                process.stdout.close()
    if process is None:
        return {"outcome": "ERROR", "reason": reason or "DISPATCH_FAILED", "exit_code": None, "uncertain": False}
    uncertain = uncertain or execution_fault
    if over_limit.is_set():
        reason = reason or "OUTPUT_LIMIT"
    if reader_error:
        reason = reason or "OUTPUT_READ_ERROR"
    duration = time.monotonic() - started
    if reason is None and duration > check["timeout_seconds"]:
        reason = "TIMEOUT"
    text = bytes(output).decode("utf-8", errors="replace")
    missing = [marker for marker in check["required_markers"] if marker not in text]
    if reason is None and process.returncode != 0:
        reason = "NONZERO_EXIT"
    if reason is None and missing:
        reason = "REQUIRED_OUTPUT_MISSING"
    if reason in {"TIMEOUT", "CANCELLED", "INTERRUPTED", "OUTPUT_LIMIT", "OUTPUT_INCOMPLETE"}:
        # A stopped parent does not establish that every descendant effect stopped.
        uncertain = True
    result = {
        "outcome": "PASS" if reason is None else "FAIL",
        "reason": reason or "EXPECTED_RESULT_OBSERVED",
        "exit_code": process.returncode, "duration_seconds": duration,
        "output_bytes_observed": output_total, "output_sha256": hashlib.sha256(bytes(output)).hexdigest(),
        "output_truncated": over_limit.is_set(), "missing_markers": missing,
        "pid": process.pid, "uncertain": uncertain,
        "descendant_effects": "NOT_ASSESSED",
    }
    if check["retain_output"]:
        result["retained_output"] = text
    return result


def run_check(job_dir: Path, check_id: str, *, confirm_run: bool = False) -> dict:
    if not confirm_run:
        fail("EXECUTION_CONFIRMATION_REQUIRED", "Confirm execution of the accepted check within the host/operator envelope.")
    with _transaction(job_dir) as (connection, state):
        if state["active_run"]:
            fail("ACTIVE_EXECUTION", "Existing execution must finish or be explicitly reconciled; do not replay it.")
        if state["cancelled"]:
            fail("CANCELLED", "This job is cancelled.")
        if not _approved(state):
            fail("APPROVAL_REQUIRED", "An operator decision on the exact frozen spec is required.")
        check = next((item for item in state["spec"]["checks"] if item["id"] == check_id), None)
        if check is None:
            fail("UNKNOWN_CHECK", "The check is absent from the accepted inventory.")
        attempts = [item for item in state["attempts"] if item["spec_sha"] == state["spec_sha"] and item["check_id"] == check_id]
        if len(attempts) >= check["max_attempts"]:
            fail("ATTEMPT_LIMIT", "The approved attempt allowance is exhausted.")
        workspace = Path(state["workspace"])
        candidate = candidate_manifest(workspace, state["spec"])
        if not state["candidate"] or candidate["sha256"] != state["candidate"]["sha256"]:
            state["candidate"] = candidate
            state["round_id"] = str(uuid.uuid4())
            _event(connection, state, "CANDIDATE_BOUND", {"candidate_sha": candidate["sha256"], "round_id": state["round_id"]})
        record = {
            "run_id": str(uuid.uuid4()), "job_id": state["job_id"], "check_id": check_id, "spec_sha": state["spec_sha"],
            "candidate_sha": candidate["sha256"], "round_id": state["round_id"],
            "argv": check["argv"], "outcome": "RUNNING", "started_at": now(),
            "origin": "LOCAL_RUNNER",
            "runner": {
                "implementation_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                "python_version": ".".join(str(item) for item in sys.version_info[:3]),
            },
        }
        state["check_sequence"] += 1
        state["attempts"].append(record)
        state["active_run"] = {"run_id": record["run_id"], "pid": None, "uncertain": False}
        _event(connection, state, "CHECK_RESERVED", record)
        spec = state["spec"]
    result = _execute(job_dir, record["run_id"], check, workspace)
    try:
        after = candidate_manifest(workspace, spec)
        if after["sha256"] != candidate["sha256"]:
            result.update(outcome="FAIL", reason="CANDIDATE_CHANGED_DURING_CHECK")
    except (FactoryError, OSError) as error:
        result.update(outcome="FAIL", reason="CANDIDATE_UNAVAILABLE_AFTER_CHECK",
                      candidate_error=error.code if isinstance(error, FactoryError) else type(error).__name__)
    with _transaction(job_dir) as (connection, state):
        if not state["active_run"] or state["active_run"]["run_id"] != record["run_id"]:
            fail("RUN_OWNERSHIP_CHANGED", "Cannot admit a result under a different active operation.")
        target = next(item for item in state["attempts"] if item["run_id"] == record["run_id"])
        target.update(result, completed_at=now())
        state["active_run"] = (
            {"run_id": record["run_id"], "pid": result.get("pid"), "uncertain": True}
            if result["uncertain"] else None
        )
        _event(connection, state, "CHECK_FINISHED", target)
    return {"check": target, "job": job_status(job_dir)}


def reconcile(job_dir: Path, run_id: str, actor: str, reason: str, *, confirm_stopped: bool = False) -> dict:
    _identifier(actor, "reconciliation actor")
    _text(reason, "reconciliation evidence", limit=4000)
    if not confirm_stopped:
        fail("RECONCILIATION_REQUIRED", "An operator must confirm process/effect reconciliation explicitly.")
    with _transaction(job_dir) as (connection, state):
        if not state["active_run"] or state["active_run"]["run_id"] != run_id:
            fail("FOREIGN_RUN", "Reconciliation must name this job's active operation.")
        target = next(item for item in state["attempts"] if item["run_id"] == run_id)
        if target["outcome"] == "RUNNING":
            target.update(outcome="FAIL", reason="INTERRUPTED_EXECUTION_RECONCILED")
        target["reconciliation"] = {
            "actor": actor, "reason": reason, "recorded_at": now(), "origin": "OPERATOR_ASSERTION",
        }
        state["active_run"] = None
        _event(connection, state, "EXECUTION_RECONCILED", {"run_id": run_id, **target["reconciliation"]})
    return job_status(job_dir)


def history(job_dir: Path) -> list[dict]:
    connection = _connection(job_dir)
    try:
        return [
            {"seq": row["seq"], "recorded_at": row["recorded_at"], "kind": row["kind"],
             "spec_sha": row["spec_sha"], "payload": json.loads(row["payload"])}
            for row in connection.execute("SELECT * FROM events ORDER BY seq")
        ]
    finally:
        connection.close()


class Parser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        fail("INVALID_ARGUMENTS", "Invalid command arguments; use --help for the supported interface.")


def main(argv: list[str] | None = None) -> int:
    parser = Parser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True, parser_class=Parser)
    validate = commands.add_parser("validate-spec")
    validate.add_argument("spec", type=Path)
    init = commands.add_parser("init")
    init.add_argument("--spec", type=Path, required=True)
    init.add_argument("--workspace", type=Path, required=True)
    init.add_argument("--job-dir", type=Path, required=True)
    for name in ("status", "history", "decide", "run-check", "record-review", "revise", "cancel", "reconcile"):
        sub = commands.add_parser(name)
        sub.add_argument("--job-dir", type=Path, required=True)
        if name == "decide":
            sub.add_argument("--spec-sha", required=True)
            sub.add_argument("--decision", choices=("accept", "reject", "changes"), required=True)
            sub.add_argument("--actor", required=True)
        elif name == "run-check":
            sub.add_argument("--check", required=True)
            sub.add_argument("--confirm-run", action="store_true")
        elif name == "record-review":
            for field in ("candidate-sha", "review-context", "role", "actor", "notes"):
                sub.add_argument("--" + field, required=True)
            sub.add_argument("--decision", choices=("pass", "changes", "incomplete"), required=True)
        elif name == "revise":
            sub.add_argument("--spec", type=Path, required=True)
        elif name == "cancel":
            sub.add_argument("--reason", required=True)
        elif name == "reconcile":
            for field in ("run-id", "actor", "reason"):
                sub.add_argument("--" + field, required=True)
            sub.add_argument("--confirm-stopped", action="store_true")
    try:
        args = parser.parse_args(argv)
        if args.command == "validate-spec":
            spec = validate_spec(load_json(args.spec))
            result = {"scope": "spec_consistency_only", "valid": True, "spec_sha": digest(spec), "spec": spec, "approved": False}
        elif args.command == "init":
            result = init_job(load_json(args.spec), args.workspace, args.job_dir)
        elif args.command == "status":
            result = job_status(args.job_dir)
        elif args.command == "history":
            result = {"scope": "local_job_history", "events": history(args.job_dir)}
        elif args.command == "decide":
            result = decide(args.job_dir, args.spec_sha, args.decision, args.actor)
        elif args.command == "run-check":
            result = run_check(args.job_dir, args.check, confirm_run=args.confirm_run)
        elif args.command == "record-review":
            result = record_review(args.job_dir, args.candidate_sha, args.role, args.decision, args.actor, args.notes, review_context=args.review_context)
        elif args.command == "revise":
            result = revise(args.job_dir, load_json(args.spec))
        elif args.command == "cancel":
            result = cancel(args.job_dir, args.reason)
        else:
            result = reconcile(args.job_dir, args.run_id, args.actor, args.reason, confirm_stopped=args.confirm_stopped)
    except FactoryError as error:
        print(json.dumps({"status": "BLOCKED", "error": {"code": error.code, "message": str(error)}}, indent=2))
        return 2
    except (OSError, sqlite3.Error, json.JSONDecodeError, UnicodeError) as error:
        print(json.dumps({"status": "BLOCKED", "error": {"code": type(error).__name__, "message": "The local operation could not complete; inspect the owned input/state without retrying unknown effects."}}, indent=2))
        return 2
    print(json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False))
    if args.command == "run-check" and result["check"]["outcome"] != "PASS":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
