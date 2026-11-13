"""Bounded transactional coordinated journal. Replay computes state; it never calls a host."""

from __future__ import annotations

from contextlib import contextmanager
from copy import deepcopy
from pathlib import Path
import sqlite3
from typing import Iterator

from . import agent_contracts as a
from . import contracts as c
from . import host as h
from . import migrations as m
from . import transitions as t


TABLES = ("records", "job", "entities", "events", "reservations")
Model = dict[str, dict[str, dict]]


def _checkpoint(stage: str) -> None:
    """Fault-injection seam used by owned rollback/process-crash tests."""


def _key(kind: str, identifier: str) -> str:
    return kind + ":" + identifier


def _empty() -> Model:
    return {name: {} for name in TABLES}


def _decode(text: str) -> object:
    value = c.parse_json(text)
    if c.canonical_json(value) != text:
        c._fail("CORRUPT_STORE", "journal", "Stored JSON is not canonical.")
    return value


def _value(model: Model, sha: str, kind: str | None = None) -> dict:
    row = model["records"].get(c._sha(sha, "record.sha"))
    if row is None or (kind is not None and row["kind"] != kind):
        c._fail("MISSING_RECORD", "record.sha", "Required immutable record is absent or has another kind.")
    return _decode(row["body"])["value"]


def _job(model: Model) -> dict:
    if not model["job"]:
        c._fail("JOB_REQUIRED", "job", "Initialize the coordinated job explicitly.")
    return model["job"]["1"]


def _task(model: Model, sha: str) -> a.TaskAssignment:
    return _value(model, sha, "task")


def _observation(model: Model, reference: a.DigestReference, task_sha: str, operation_key: str) -> tuple[str, dict]:
    matches = [(sha, _value(model, sha)) for sha, row in model["records"].items()
               if row["kind"] == "observation" and _value(model, sha)["observation"] == reference]
    if len(matches) != 1:
        c._fail("MISSING_OBSERVATION", "observation", "An exact stored host observation reference is required.")
    sha, value = matches[0]
    if value["task_sha"] != task_sha or value["operation_key"] != operation_key:
        c._fail("BINDING_MISMATCH", "observation", "Observation belongs to a different assignment or operation.")
    return sha, value


def _artifact(model: Model, reference: a.DigestReference) -> None:
    if not any(row["kind"] == "artifact" and (
        _value(model, sha)["id"], _value(model, sha)["sha256"], _value(model, sha)["artifact_kind"]
    ) == (reference["id"], reference["sha256"], "evidence") for sha, row in model["records"].items()):
        c._fail("MISSING_RECORD", "evidence", "Persist the exact typed evidence reference before using it.")


def record_value(kind: str, identifier: str, revision: int, value: object, *, context: dict | None = None) -> dict:
    """Construct an input record; validation happens transactionally against stored dependencies."""
    return {"kind": kind, "id": identifier, "revision": revision, "value": value,
            "context": {} if context is None else context}


def _record(model: Model, raw: object, metadata: m.StoreMetadata) -> str:
    record = c._object(raw, {"kind", "id", "revision", "value", "context"}, "record")
    kind = c._enum(record["kind"], (
        "intent", "envelope", "task", "attempt", "result", "finding", "failure", "capabilities", "observation", "artifact",
    ), "record.kind")
    identifier = c._identifier(record["id"], "record.id")
    revision = c._integer(record["revision"], "record.revision")
    value, context = record["value"], record["context"]
    if kind == "intent":
        context = c._object(context, {"supported_kinds"}, "record.context")
        kinds = c._strings(context["supported_kinds"], "record.supported_kinds", identifiers=True, minimum=1)
        value = c.validate_intent(value, supported_component_kinds=tuple(kinds))
    elif kind == "envelope":
        c._object(context, set(), "record.context")
        value = c.validate_envelope(value, intent=_value(model, value["intent"]["sha256"], "intent"))
        if value["environment"] != metadata["environment"]:
            c._fail("ENVIRONMENT_MISMATCH", "record.envelope", "Envelope belongs to another store environment.")
    elif kind == "task":
        c._object(context, set(), "record.context")
        task = a._task(value)
        value = a.validate_task(task, intent=_value(model, task["binding"]["intent_sha"], "intent"),
                                envelope=_value(model, task["binding"]["envelope_sha"], "envelope"),
                                plan_sha=task["binding"]["plan_sha"], candidate_sha=task["binding"]["candidate_sha"])
        if task["binding"]["job_id"] != _job(model)["job_id"]:
            c._fail("BINDING_MISMATCH", "record.task", "Task belongs to another job.")
    elif kind == "attempt":
        c._object(context, set(), "record.context")
        value = a.validate_attempt(value, task=_task(model, value["task_sha"]))
        if value["observation"] is not None:
            _, observed = _observation(model, value["observation"], value["task_sha"], value["operation_key"])
            if value["producer"] != observed["producer"] or value["observed_usage"] != observed["usage"]:
                c._fail("BINDING_MISMATCH", "record.attempt", "Attempt contradicts its stored host observation.")
            statuses = {"completed": ("completed",), "failed": ("failed",), "cancelled": ("stopped",),
                        "accepted": ("accepted",), "running": ("running",), "cancel_requested": ("cancel_requested",),
                        "unknown": ("unknown", "accepted", "running", "cancel_requested")}
            if observed["status"] not in statuses.get(value["status"], ()):
                c._fail("OUTCOME_MISMATCH", "record.attempt", "Attempt state contradicts its observed host outcome.")
    elif kind == "result":
        context = c._object(context, {"attempt_sha", "prior_attempts"}, "record.context")
        attempt = _value(model, context["attempt_sha"], "attempt")
        prior = [_value(model, sha, "attempt")["producer"] for sha in c._list(context["prior_attempts"], "prior_attempts")]
        task = _task(model, value["task_sha"])
        value = a.validate_result(value, task=task, attempt=attempt, current_candidate_sha=task["binding"]["candidate_sha"],
                                  prior_producers=tuple(prior))
    elif kind in ("finding", "failure"):
        c._object(context, set(), "record.context")
        value = a.validate_finding(value) if kind == "finding" else a.validate_failure(value)
    elif kind == "capabilities":
        c._object(context, set(), "record.context")
        value = h.validate_capabilities(value)
        if value["environment"] != metadata["environment"]:
            c._fail("ENVIRONMENT_MISMATCH", "record.capabilities", "Host belongs to another store environment.")
    elif kind == "observation":
        context = c._object(context, {"capabilities_sha"}, "record.context")
        task = _task(model, value["task_sha"])
        value = h.validate_receipt(value, capabilities=_value(model, context["capabilities_sha"], "capabilities"),
                                   task=task, operation_key=value["operation_key"])
        reservation = model["reservations"].get(value["operation_key"])
        if reservation is None or reservation["task_sha"] != value["task_sha"]:
            c._fail("BINDING_MISMATCH", "record.observation", "No matching durable reservation exists.")
        if any(row["kind"] == kind and _value(model, sha)["observation"] == value["observation"]
               and _value(model, sha) != value for sha, row in model["records"].items()):
            c._fail("RECORD_CONFLICT", "record.observation", "An exact observation reference cannot be rebound to another payload.")
    else:
        c._object(context, set(), "record.context")
        value = c._object(value, {"schema_version", "id", "artifact_kind", "sha256", "assessment"}, "artifact")
        if value["schema_version"] != "sparkforge.artifact-reference.v1" or value["assessment"] != "unassessed":
            c._fail("INVALID_ARTIFACT", "artifact", "Only explicit unassessed artifact references may be stored.")
        c._enum(value["artifact_kind"], ("plan", "evidence", "candidate", "source", "role_output"), "artifact.kind")
        c._identifier(value["id"], "artifact.id")
        c._sha(value["sha256"], "artifact.sha256")
    actual_id = (value["binding"]["attempt_id"] if kind in ("task", "attempt") else
                 value["host"]["id"] if kind == "capabilities" else
                 value["observation"]["id"] if kind == "observation" else value["id"])
    if (identifier != actual_id or (kind in ("intent", "envelope") and revision != value["revision"])
            or (kind == "capabilities" and revision != value["host"]["revision"])):
        c._fail("BINDING_MISMATCH", "record", "Record identity/revision differs from its value.")
    body = c.canonical_json(record_value(kind, identifier, revision, value, context=context))
    sha = c.record_digest(value)
    row = {"sha": sha, "kind": kind, "record_id": identifier, "revision": revision, "body": body}
    for existing in model["records"].values():
        if existing["sha"] == sha or (existing["kind"], existing["record_id"], existing["revision"]) == (kind, identifier, revision):
            if existing != row:
                c._fail("RECORD_CONFLICT", "record", "Immutable record identity/content already has different bytes or validation context.")
            return sha
    model["records"][sha] = row
    return sha


def _entity(model: Model, kind: str, identifier: str) -> dict:
    row = model["entities"].get(_key(kind, identifier))
    if row is None:
        c._fail("ENTITY_REQUIRED", "entity", "The requested entity has not been registered.")
    return row


def _unresolved_descendants(model: Model, kind: str, identifier: str) -> bool:
    for reservation in model["reservations"].values():
        if reservation["status"] not in t.OPEN_OPERATIONS:
            continue
        owner = _entity(model, reservation["kind"], reservation["entity_id"])
        while owner["parent_kind"] is not None:
            if (owner["parent_kind"], owner["parent_id"]) == (kind, identifier):
                return True
            owner = _entity(model, owner["parent_kind"], owner["parent_id"])
    return False


def _entity_row(projection: t.Projection, parent: tuple[str, str] | None, task_sha: str | None) -> dict:
    body = c.canonical_json(projection)
    return {"kind": projection["kind"], "entity_id": projection["id"],
            "parent_kind": None if parent is None else parent[0], "parent_id": None if parent is None else parent[1],
            "task_sha": task_sha, "initial": body, "initial_sha": c.record_digest(projection),
            "revision": projection["revision"], "body": body, "sha": c.record_digest(projection), "event_id": None}


def _request(value: object) -> dict:
    request = c._object(value, {"schema_version", "key", "action", "kind", "entity_id", "data"}, "request")
    if request["schema_version"] != "sparkforge.store-command.v1":
        c._fail("UNSUPPORTED_SCHEMA", "request", "Unsupported journal command schema.")
    c._identifier(request["key"], "request.key")
    c._identifier(request["entity_id"], "request.entity_id")
    c._enum(request["action"], ("initialize", "register", "record", "transition"), "request.action")
    c._enum(request["kind"], ("job", "task", "attempt"), "request.kind")
    c.canonical_json(request)
    return deepcopy(request)


def _reduce(model: Model, request: dict, metadata: m.StoreMetadata) -> dict:
    action, kind, identifier, data = request["action"], request["kind"], request["entity_id"], request["data"]
    event, projection, record_sha = None, None, None
    if action == "initialize":
        data = c._object(data, {"intent", "envelope", "supported_kinds", "context_sha", "required_evidence"}, "initialize")
        if kind != "job" or model["job"]:
            c._fail("JOB_EXISTS", "initialize", "A store supports one explicitly initialized job, never adoption.")
        intent = c.validate_intent(data["intent"], supported_component_kinds=tuple(c._strings(
            data["supported_kinds"], "supported_kinds", identifiers=True, minimum=1)))
        intent_sha = _record(model, record_value("intent", intent["id"], intent["revision"], intent,
                             context={"supported_kinds": data["supported_kinds"]}), metadata)
        envelope = c.validate_envelope(data["envelope"], intent=intent)
        if not any(root["path"] == metadata["workspace"] for root in envelope["workspace_roots"]):
            c._fail("ENVIRONMENT_MISMATCH", "initialize.workspace", "Envelope must explicitly include this store's workspace.")
        envelope_sha = _record(model, record_value("envelope", envelope["id"], envelope["revision"], envelope), metadata)
        model["job"]["1"] = {"singleton": 1, "job_id": identifier, "intent_sha": intent_sha, "envelope_sha": envelope_sha,
                             "supported_kinds": c.canonical_json(data["supported_kinds"])}
        projection = t.initial_projection("job", identifier, data["context_sha"], data["required_evidence"])
        model["entities"][_key(kind, identifier)] = _entity_row(projection, None, None)
    elif action == "register":
        data = c._object(data, {"task", "required_evidence"}, "register")
        job = _job(model)
        task = a._task(data["task"])
        if kind not in ("task", "attempt") or identifier != task["binding"]["task_id" if kind == "task" else "attempt_id"]:
            c._fail("BINDING_MISMATCH", "register", "Entity must match the assignment's task or attempt ID.")
        if _key(kind, identifier) in model["entities"]:
            c._fail("ENTITY_EXISTS", "register", "Existing entities cannot be overwritten.")
        task_sha = _record(model, record_value("task", task["binding"]["attempt_id"], 1, task), metadata)
        parent = ("job", job["job_id"]) if kind == "task" else ("task", task["binding"]["task_id"])
        parent_row = _entity(model, *parent)
        if kind == "attempt" and parent_row["task_sha"] != task_sha:
            c._fail("BINDING_MISMATCH", "register", "Attempt and parent task need the same assignment.")
        projection = t.initial_projection(kind, identifier, c.record_digest(task["binding"]), data["required_evidence"])
        model["entities"][_key(kind, identifier)] = _entity_row(projection, parent, task_sha)
    elif action == "record":
        c._object(data, {"record"}, "record_command")
        if kind != "job" or _job(model)["job_id"] != identifier:
            c._fail("BINDING_MISMATCH", "record_command", "Records must belong to the initialized job.")
        record_sha = _record(model, data["record"], metadata)
    else:
        data = c._object(data, {"command", "records"}, "transition")
        command = t._command(data["command"])
        if command["key"] != request["key"] or command["entity_id"] != identifier:
            c._fail("BINDING_MISMATCH", "transition", "Outer request and inner command identities differ.")
        for raw in c._list(data["records"], "transition.records"):
            _record(model, raw, metadata)
        entity = _entity(model, kind, identifier)
        before = t.validate_projection(_decode(entity["body"]))
        task_sha = entity["task_sha"]
        operation_key = command["operation_id"]
        operation = model["reservations"].get(operation_key)
        observation_sha = None
        if command["action"] in ("reserve", "dispatch"):
            job_projection = _decode(_entity(model, "job", _job(model)["job_id"])["body"])
            parent = None if entity["parent_kind"] is None else _decode(
                _entity(model, entity["parent_kind"], entity["parent_id"])["body"])
            if job_projection["stop_requested"] or (parent is not None and parent["stop_requested"]):
                c._fail("STOP_REQUESTED", "reservation", "A stopped parent/job cannot admit new work.")
        if command["action"] == "reserve":
            if task_sha is None:
                c._fail("ASSIGNMENT_REQUIRED", "reservation", "External work must be owned by an assigned task/attempt, not a parent job.")
            if operation is not None:
                c._fail("OPERATION_CONFLICT", "reservation", "Operation keys are unique across the store.")
            if any(row["status"] in t.OPEN_OPERATIONS for row in model["reservations"].values()):
                c._fail("DISPATCH_BLOCKED", "reservation", "This serial store already contains unresolved work.")
        elif operation_key is not None:
            if operation is None or (operation["kind"], operation["entity_id"], operation["task_sha"]) != (kind, identifier, task_sha):
                c._fail("OPERATION_CONFLICT", "reservation", "The operation belongs to another owner or assignment.")
        if command["observation"] is not None:
            observation_sha, observed = _observation(model, command["observation"], task_sha, operation_key)
            allowed = {
                "completed": ("completed",), "failed": ("failed",), "cancelled": ("stopped",), "not_started": ("not_started",),
                "unknown": ("unknown", "accepted", "running", "cancel_requested"),
            }
            if command["action"] == "cancel_ack":
                if not observed["cancel_acknowledged"] or observed["status"] not in ("cancel_requested", "running", "unknown"):
                    c._fail("OUTCOME_MISMATCH", "observation", "Observation does not acknowledge pending cancellation.")
            elif observed["status"] not in allowed.get(command["resolution"], ()):
                c._fail("OUTCOME_MISMATCH", "observation", "Observation cannot support the requested operation resolution.")
        for evidence in command["evidence"]:
            _artifact(model, evidence["receipt"])
        result = t.apply_command(before, command, unresolved_descendants=_unresolved_descendants(model, kind, identifier))
        projection, event = result["projection"], result["event"]
        if event["id"] in model["events"]:
            c._fail("EVENT_CONFLICT", "event", "Event identity already exists.")
        model["events"][event["id"]] = {
            "event_id": event["id"], "kind": kind, "entity_id": identifier, "revision": projection["revision"],
            "command_key": request["key"], "before_sha": entity["sha"], "body": c.canonical_json(event), "sha": c.record_digest(event),
        }
        entity.update(revision=projection["revision"], body=c.canonical_json(projection),
                      sha=c.record_digest(projection), event_id=event["id"])
        for projected_operation in projection["operations"]:
            key = projected_operation["id"]
            previous = model["reservations"].get(key)
            if previous is None:
                task = _task(model, task_sha)
                reservation = {
                    "operation_key": key, "task_sha": task_sha, "context_sha": before["context_sha"],
                    "binding": task["binding"], "allowance": task["allowance"], "tools": task["tools"],
                    "effects": task["effects"], "allowed_writes": task["allowed_writes"],
                    "status": projected_operation["status"], "dispatched": projected_operation["dispatched"],
                    "observation_sha": None,
                }
            else:
                reservation = _decode(previous["body"])
                reservation.update(status=projected_operation["status"], dispatched=projected_operation["dispatched"])
            if key == operation_key and observation_sha is not None:
                reservation["observation_sha"] = observation_sha
            body = c.canonical_json(reservation)
            if previous is None or body != previous["body"]:
                model["reservations"][key] = {
                    "operation_key": key, "kind": kind, "entity_id": identifier, "task_sha": task_sha,
                    "context_sha": reservation["context_sha"], "status": reservation["status"], "body": body,
                    "sha": c.record_digest(reservation), "event_id": event["id"], "observation_sha": reservation["observation_sha"],
                }
    return {"projection": projection, "event": event, "record_sha": record_sha}


def _row_key(table: str, row: dict) -> str:
    return (_key(row["kind"], row["entity_id"]) if table == "entities" else
            str(row[{"records": "sha", "job": "singleton", "events": "event_id", "reservations": "operation_key"}[table]]))


def _reconstruct(connection: sqlite3.Connection, metadata: m.StoreMetadata) -> tuple[Model, list[dict]]:
    model, commands = _empty(), []
    try:
        for seq, row in enumerate(connection.execute("SELECT * FROM commands ORDER BY seq"), 1):
            row = dict(row)
            request = _request(_decode(row["request"]))
            if row["seq"] != seq or row["command_key"] != request["key"] or row["request_sha"] != c.record_digest(request):
                c._fail("CORRUPT_STORE", "commands", "Command order, key or payload digest is inconsistent.")
            result = _reduce(model, request, metadata)
            event_id = None if result["event"] is None else result["event"]["id"]
            if row["result"] != c.canonical_json(result) or row["result_sha"] != c.record_digest(result) or row["event_id"] != event_id:
                c._fail("CORRUPT_STORE", "commands", "Stored command outcome differs from deterministic replay.")
            commands.append(row)
        for table in TABLES:
            actual = {_row_key(table, dict(row)): dict(row) for row in connection.execute(f"SELECT * FROM {table}")}
            if actual != model[table]:
                c._fail("CORRUPT_STORE", table, "Stored records/projections/reservations diverge from committed history.")
        if connection.execute("PRAGMA foreign_key_check").fetchone() is not None:
            c._fail("CORRUPT_STORE", "journal", "Journal contains broken foreign-key bindings.")
    except c.ContractError as error:
        if error.code == "CORRUPT_STORE":
            raise
        c._fail("CORRUPT_STORE", "journal", f"Committed history violates {error.code}.")
    except (KeyError, TypeError, IndexError) as error:
        c._fail("CORRUPT_STORE", "journal", f"Malformed stored command ({type(error).__name__}).")
    return model, commands


def _preflight(root: Path, *, recovery: bool, write: bool = False) -> Path:
    path = m._store_path(root)
    with path.open("rb") as stream:
        header = stream.read(100)
    if len(header) != 100 or header[:16] != b"SQLite format 3\0":
        c._fail("INVALID_STORE", "journal", "Invalid SQLite header.")
    if int.from_bytes(header[68:72], "big") != m.APPLICATION_ID:
        c._fail("FOREIGN_STORE", "journal", "This is not a coordinated store.")
    if int.from_bytes(header[60:64], "big") != 2:
        c._fail("UNSUPPORTED_STORE_VERSION", "journal", "Use an explicitly prepared coordinated schema-v2 copy.")
    if header[18:20] != b"\x01\x01" or any((path.parent / (path.name + suffix)).exists() for suffix in ("-wal", "-shm")):
        c._fail("STORE_UNSUPPORTED", "journal", "WAL/live remote storage is not supported.")
    journal = path.parent / (path.name + "-journal")
    if journal.exists():
        if not recovery:
            c._fail("STORE_BUSY" if write else "RECOVERY_REQUIRED", "journal",
                    "A writer or interrupted transaction has a journal; inspect/recover explicitly, never remove it.")
        m._database(path.parent, journal.name)
    return path


def _sqlite_error(error: sqlite3.Error) -> None:
    code = getattr(error, "sqlite_errorcode", 0) & 0xFF
    label = ("STORE_BUSY" if code in (sqlite3.SQLITE_BUSY, sqlite3.SQLITE_LOCKED) else
             "STORE_CONFLICT" if code == sqlite3.SQLITE_CONSTRAINT else
             "STORE_LIMIT" if code == sqlite3.SQLITE_FULL else "STORE_UNAVAILABLE")
    c._fail(label, "journal", f"SQLite operation failed ({type(error).__name__}); no success is inferred.")


@contextmanager
def _connection(root: Path, *, write: bool = False, recovery: bool = False) -> Iterator[tuple[sqlite3.Connection, m.StoreMetadata]]:
    connection = None
    try:
        path = _preflight(root, recovery=recovery, write=write)
        connection = sqlite3.connect(path.as_uri() + ("?mode=rw" if write or recovery else "?mode=ro"),
                                     uri=True, timeout=0, isolation_level=None)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys=ON")
        if write or recovery:
            connection.execute("PRAGMA synchronous=FULL")
            page_size = connection.execute("PRAGMA page_size").fetchone()[0]
            connection.execute(f"PRAGMA max_page_count={m.v1.MAX_FILE_BYTES // page_size}")
        else:
            connection.execute("PRAGMA query_only=ON")
        connection.execute("BEGIN IMMEDIATE" if write or recovery else "BEGIN")
        metadata = m._metadata(connection)
        if connection.execute("PRAGMA journal_mode").fetchone()[0] != "delete":
            c._fail("STORE_UNSUPPORTED", "journal", "DELETE-journal mode is required.")
        if [row[0] for row in connection.execute("PRAGMA quick_check")] != ["ok"]:
            c._fail("CORRUPT_STORE", "journal", "SQLite consistency check failed.")
        yield connection, metadata
    except sqlite3.Error as error:
        _sqlite_error(error)
    except OSError as error:
        c._fail("STORE_UNAVAILABLE", "journal", f"Store access failed ({type(error).__name__}).")
    finally:
        if connection is not None:
            try:
                if connection.in_transaction:
                    connection.execute("ROLLBACK")
            finally:
                connection.close()


def _commit(connection: sqlite3.Connection) -> None:
    _checkpoint("before_commit")
    try:
        connection.execute("COMMIT")
        _checkpoint("after_commit")
    except Exception as error:
        c._fail("COMMIT_UNCERTAIN", "journal", f"Commit acknowledgement failed ({type(error).__name__}); inspect the original command key.")


def _persist(connection: sqlite3.Connection, before: Model, after: Model) -> None:
    for table in TABLES:
        for key, row in after[table].items():
            old = before[table].get(key)
            if old == row:
                continue
            if old is None:
                columns = list(row)
                connection.execute(f"INSERT INTO {table}({','.join(columns)}) VALUES({','.join('?' for _ in columns)})",
                                   [row[column] for column in columns])
            elif table == "entities":
                cursor = connection.execute(
                    "UPDATE entities SET revision=?,body=?,sha=?,event_id=? WHERE kind=? AND entity_id=? AND revision=?",
                    (row["revision"], row["body"], row["sha"], row["event_id"], row["kind"], row["entity_id"], old["revision"]))
                if cursor.rowcount != 1:
                    c._fail("REVISION_CONFLICT", "entity", "Projection revision changed before persistence.")
            elif table == "reservations":
                connection.execute("UPDATE reservations SET status=?,body=?,sha=?,event_id=?,observation_sha=? WHERE operation_key=?",
                                   (row["status"], row["body"], row["sha"], row["event_id"], row["observation_sha"], key))
            else:
                c._fail("IMMUTABLE_RECORD", table, "Existing immutable data cannot be overwritten.")
        _checkpoint("after_" + table)


def _execute(root: Path, request: dict) -> dict:
    request = _request(request)
    with _connection(root, write=True) as (connection, metadata):
        model, commands = _reconstruct(connection, metadata)
        prior = next((row for row in commands if row["command_key"] == request["key"]), None)
        if prior is not None:
            if prior["request_sha"] != c.record_digest(request) or prior["request"] != c.canonical_json(request):
                c._fail("IDEMPOTENCY_CONFLICT", "request.key", "Durable command key is already bound to another payload.")
            result = _decode(prior["result"])
            if result["projection"] is not None:
                result["projection"] = _decode(_entity(model, request["kind"], request["entity_id"])["body"])
            return {**result, "replayed": True}
        before = deepcopy(model)
        try:
            result = _reduce(model, request, metadata)
        except (KeyError, TypeError, IndexError) as error:
            c._fail("INVALID_RECORD", "request", f"Malformed record dependencies ({type(error).__name__}).")
        _persist(connection, before, model)
        connection.execute("INSERT INTO commands VALUES(?,?,?,?,?,?,?)", (
            len(commands) + 1, request["key"], c.canonical_json(request), c.record_digest(request),
            c.canonical_json(result), c.record_digest(result), None if result["event"] is None else result["event"]["id"]))
        _checkpoint("after_commands")
        if connection.execute("PRAGMA foreign_key_check").fetchone() is not None:
            c._fail("CORRUPT_STORE", "journal", "Transaction contains a broken reference.")
        _commit(connection)
        return {**result, "replayed": False}


def _input(key: str, action: str, kind: str, identifier: str, data: dict) -> dict:
    return {"schema_version": "sparkforge.store-command.v1", "key": key, "action": action,
            "kind": kind, "entity_id": identifier, "data": data}


def initialize(root: Path, key: str, job_id: str, *, intent: c.IntentBaseline, envelope: c.ExecutionEnvelope,
               supported_component_kinds: tuple[str, ...], context_sha: str, required_evidence: list[str]) -> dict:
    return _execute(root, _input(key, "initialize", "job", job_id, {
        "intent": intent, "envelope": envelope, "supported_kinds": list(supported_component_kinds),
        "context_sha": context_sha, "required_evidence": required_evidence,
    }))


def register(root: Path, key: str, kind: str, task: a.TaskAssignment, *, required_evidence: list[str]) -> dict:
    task = a._task(task)
    kind = c._enum(kind, ("task", "attempt"), "register.kind")
    return _execute(root, _input(key, "register", kind, task["binding"]["task_id" if kind == "task" else "attempt_id"],
                                {"task": task, "required_evidence": required_evidence}))


def append_record(root: Path, key: str, job_id: str, record: dict) -> dict:
    return _execute(root, _input(key, "record", "job", job_id, {"record": record}))


def apply(root: Path, kind: str, command: t.Command, *, records: tuple[dict, ...] = ()) -> dict:
    command = t._command(command)
    return _execute(root, _input(command["key"], "transition", kind, command["entity_id"],
                                {"command": command, "records": list(records)}))


def _snapshot(model: Model, metadata: m.StoreMetadata, commands: list[dict]) -> dict:
    return {
        "metadata": metadata, "job": None if not model["job"] else dict(_job(model)),
        "records": {sha: _decode(row["body"]) for sha, row in model["records"].items()},
        "entities": {key: {"projection": _decode(row["body"]), "task_sha": row["task_sha"],
                           "parent_kind": row["parent_kind"], "parent_id": row["parent_id"]}
                     for key, row in model["entities"].items()},
        "reservations": {key: {**_decode(row["body"]), "owner_kind": row["kind"], "owner_id": row["entity_id"]}
                         for key, row in model["reservations"].items()},
        "events": [_decode(row["body"]) for row in model["events"].values()],
        "command_count": len(commands),
    }


def read(root: Path) -> dict:
    with _connection(root) as (connection, metadata):
        model, commands = _reconstruct(connection, metadata)
        return _snapshot(model, metadata, commands)


def recover(root: Path, *, expected_store_id: str) -> dict:
    """Explicit SQLite rollback recovery only. Pending host operations remain pending."""
    c._identifier(expected_store_id, "expected_store_id")
    with _connection(root, recovery=True) as (connection, metadata):
        if metadata["store_id"] != expected_store_id:
            c._fail("STORE_IDENTITY_MISMATCH", "recovery", "Recovered database is not the selected store.")
        model, commands = _reconstruct(connection, metadata)
        # Let SQLite finalize even a cold leftover journal; never unlink sidecars ourselves.
        connection.execute("PRAGMA user_version=2")
        connection.execute("COMMIT")
        return _snapshot(model, metadata, commands)
