"""Explicit isolated store creation/copies; assisted-v1 state is referenced read-only."""

from __future__ import annotations

from contextlib import contextmanager
import hashlib
from pathlib import Path
import sqlite3
from typing import Callable, Iterator, TypedDict
import uuid

from plugins.sparkforge.scripts import factory as v1
from . import contracts as c


APPLICATION_ID = 0x53464752
STORE_FAMILY = "sparkforge.coordinated-store"
CURRENT_VERSION = 1
DATABASE_NAME = "coordinated.sqlite3"
BACKUP_NAME = "pre-migration.sqlite3"
MIGRATIONS: dict[int, Callable[[sqlite3.Connection], None]] = {}


class StoreMetadata(TypedDict):
    family: str
    version: int
    store_id: str
    environment: str
    workspace: str


class LegacyReference(TypedDict):
    schema_version: str
    evidence_class: str
    job_id: str
    revision: int
    environment: str
    spec_sha: str
    state_sha: str
    database_sha: str
    has_unresolved_run: bool


class MigrationReceipt(TypedDict):
    scope: str
    store_id: str
    source_version: int
    target_version: int
    source_sha: str
    backup_sha: str
    prepared_sha: str


def _directory(path: Path) -> Path:
    try:
        return v1._directory(path)
    except v1.FactoryError as error:
        c._fail(error.code, "store.directory", str(error))


def _database(root: Path, name: str) -> Path:
    try:
        return v1._file(root, name)
    except v1.FactoryError as error:
        c._fail(error.code, "store.database", str(error))


def _hash_file(path: Path) -> str:
    digest, count = hashlib.sha256(), 0
    with path.open("rb") as stream:
        while chunk := stream.read(64 * 1024):
            count += len(chunk)
            if count > v1.MAX_FILE_BYTES:
                c._fail("INPUT_TOO_LARGE", "store.database", "Database exceeds the existing 32-MiB file inspection limit.")
            digest.update(chunk)
    return digest.hexdigest()


def _new_directory(root: Path, workspace: Path, *, source: Path | None = None) -> Path:
    if (not isinstance(root, Path) or not root.is_absolute() or ".." in root.parts
            or root == Path(root.anchor)):
        c._fail("UNSAFE_PATH", "store.directory", "Use a new explicit absolute store directory.")
    parent, workspace = _directory(root.parent), _directory(workspace)
    c.relative_path(root.name, "store.directory")
    root = parent / root.name
    if root.is_relative_to(workspace) or workspace.is_relative_to(root):
        c._fail("OVERLAPPING_STATE", "store.directory", "Store state must be separate from the candidate workspace.")
    if source is not None and (root.is_relative_to(source) or source.is_relative_to(root)):
        c._fail("OVERLAPPING_STATE", "store.directory", "Prepared copies must be separate from their source store.")
    if (parent / "job.sqlite3").exists():
        c._fail("LEGACY_COLOCATION", "store.directory", "Do not create coordinated state inside an assisted-v1 job.")
    try:
        root.mkdir(mode=0o700)
    except FileExistsError:
        c._fail("STORE_EXISTS", "store.directory", "Existing directories are never adopted or overwritten.")
    return root


@contextmanager
def _read_database(path: Path) -> Iterator[sqlite3.Connection]:
    """Read-lock an offline rollback-journal database; never recover or adopt sidecars."""
    for suffix in ("-wal", "-shm", "-journal"):
        if (path.parent / (path.name + suffix)).exists():
            c._fail("STORE_BUSY", "store.database", "Journal sidecars require explicit owner reconciliation before reading.")
    with path.open("rb") as stream:
        header = stream.read(100)
    if len(header) != 100 or header[:16] != b"SQLite format 3\0":
        c._fail("INVALID_STORE", "store.database", "Database header is not a supported SQLite snapshot.")
    if header[18:20] != b"\x01\x01":
        c._fail("STORE_BUSY", "store.database", "WAL/unknown journal formats are rejected before SQLite opens the source.")
    connection = sqlite3.connect(path.as_uri() + "?mode=ro", uri=True, timeout=0, isolation_level=None)
    connection.row_factory = sqlite3.Row
    try:
        connection.execute("PRAGMA query_only=ON")
        connection.execute("BEGIN")
        connection.execute("SELECT name FROM sqlite_schema LIMIT 1").fetchall()
        if connection.execute("PRAGMA journal_mode").fetchone()[0] != "delete":
            c._fail("STORE_BUSY", "store.database", "Only offline DELETE-journal snapshots are supported by this boundary.")
        if [row[0] for row in connection.execute("PRAGMA quick_check")] != ["ok"]:
            c._fail("INVALID_STORE", "store.database", "SQLite consistency check failed.")
        yield connection
    finally:
        if connection.in_transaction:
            connection.execute("ROLLBACK")
        connection.close()


def _metadata(connection: sqlite3.Connection) -> StoreMetadata:
    application_id = connection.execute("PRAGMA application_id").fetchone()[0]
    version = connection.execute("PRAGMA user_version").fetchone()[0]
    if application_id != APPLICATION_ID:
        c._fail("FOREIGN_STORE", "store.database", "This database is not a coordinated store.")
    if type(version) is not int or not 1 <= version <= CURRENT_VERSION:
        c._fail("UNSUPPORTED_STORE_VERSION", "store.version", "Unknown store versions are not opened for writes or migration.")
    table = connection.execute("SELECT type FROM sqlite_schema WHERE name='runtime_metadata'").fetchone()
    if table is None or table[0] != "table":
        c._fail("INVALID_STORE", "store.metadata", "Missing coordinated store metadata table.")
    rows = connection.execute("SELECT * FROM runtime_metadata").fetchall()
    if len(rows) != 1:
        c._fail("INVALID_STORE", "store.metadata", "Expected one metadata row.")
    record = c._object(dict(rows[0]), {"singleton", "family", "store_id", "environment", "workspace"}, "store.metadata")
    if record["singleton"] != 1 or record["family"] != STORE_FAMILY:
        c._fail("FOREIGN_STORE", "store.metadata", "Store family or identity row is invalid.")
    return {
        "family": STORE_FAMILY, "version": version,
        "store_id": c._identifier(record["store_id"], "store.store_id"),
        "environment": c._enum(record["environment"], ("LOCAL_DEVELOPMENT", "CORP", "ACRO"), "store.environment"),
        "workspace": c._text(record["workspace"], "store.workspace", limit=500),
    }


def _store_path(root: Path) -> Path:
    root = _directory(root)
    if (root / "job.sqlite3").exists():
        c._fail("LEGACY_STORE", "store.directory", "Assisted-v1 jobs cannot be adopted as coordinated stores.")
    return _database(root, DATABASE_NAME)


def inspect_store(root: Path) -> StoreMetadata:
    try:
        with _read_database(_store_path(root)) as connection:
            return _metadata(connection)
    except (OSError, sqlite3.Error) as error:
        c._fail("STORE_UNAVAILABLE", "store.database", f"Cannot inspect store ({type(error).__name__}).")


def create_store(root: Path, *, workspace: Path, environment: str) -> StoreMetadata:
    """Create only a new store header. No job, decision, projection or legacy import."""
    environment = c._enum(environment, ("LOCAL_DEVELOPMENT", "CORP", "ACRO"), "store.environment")
    try:
        root = _new_directory(root, workspace)
        path = root / DATABASE_NAME
        with path.open("xb"):
            pass
        connection = sqlite3.connect(path.as_uri() + "?mode=rw", uri=True, timeout=0, isolation_level=None)
        connection.row_factory = sqlite3.Row
        try:
            connection.execute("BEGIN IMMEDIATE")
            connection.execute(f"PRAGMA application_id={APPLICATION_ID}")
            connection.execute(f"PRAGMA user_version={CURRENT_VERSION}")
            connection.execute(
                "CREATE TABLE runtime_metadata(singleton INTEGER PRIMARY KEY CHECK(singleton=1), "
                "family TEXT NOT NULL, store_id TEXT NOT NULL, environment TEXT NOT NULL, workspace TEXT NOT NULL)"
            )
            connection.execute("INSERT INTO runtime_metadata VALUES(1, ?, ?, ?, ?)",
                               (STORE_FAMILY, str(uuid.uuid4()), environment, str(_directory(workspace))))
            metadata = _metadata(connection)
            connection.execute("COMMIT")
        except BaseException:
            if connection.in_transaction:
                connection.execute("ROLLBACK")
            raise
        finally:
            connection.close()
        return metadata
    except (OSError, sqlite3.Error) as error:
        c._fail("STORE_CREATION_FAILED", "store.directory", f"Creation failed; inspect the owned partial directory ({type(error).__name__}).")


def legacy_reference(job_dir: Path) -> LegacyReference:
    """Use the unchanged v1 state validator on a read-only connection; copy no approvals."""
    try:
        root = _directory(job_dir)
        path = _database(root, "job.sqlite3")
        with _read_database(path) as connection:
            source_sha = _hash_file(path)
            try:
                state = v1._state(connection)
            except v1.FactoryError as error:
                c._fail(error.code, "legacy.state", str(error))
            if _hash_file(path) != source_sha:
                c._fail("SOURCE_CHANGED", "legacy.database", "Legacy source changed while its reference was being captured.")
            return {
                "schema_version": "sparkforge.legacy-reference.v1", "evidence_class": "assisted_v1_reference_only",
                "job_id": state["job_id"], "revision": state["revision"], "environment": state["spec"]["environment"],
                "spec_sha": state["spec_sha"], "state_sha": v1.digest(state), "database_sha": source_sha,
                "has_unresolved_run": state["active_run"] is not None,
            }
    except (OSError, sqlite3.Error) as error:
        c._fail("LEGACY_UNAVAILABLE", "legacy.database", f"Cannot read legacy reference ({type(error).__name__}).")


def _copy_exact(source: Path, destination: Path, expected_sha: str) -> None:
    count = 0
    with source.open("rb") as reader, destination.open("xb") as writer:
        while chunk := reader.read(64 * 1024):
            count += len(chunk)
            if count > v1.MAX_FILE_BYTES:
                c._fail("INPUT_TOO_LARGE", "migration.copy", "Database exceeds the bounded copy limit.")
            writer.write(chunk)
        writer.flush()
    if _hash_file(destination) != expected_sha:
        c._fail("COPY_MISMATCH", "migration.copy", "Prepared copy does not match the locked source bytes.")


def _migration_sql(action: int, _first: str | None, _second: str | None, _database_name: str | None, _trigger: str | None) -> int:
    if action in (sqlite3.SQLITE_TRANSACTION, sqlite3.SQLITE_SAVEPOINT, sqlite3.SQLITE_ATTACH,
                  sqlite3.SQLITE_DETACH, sqlite3.SQLITE_PRAGMA):
        return sqlite3.SQLITE_DENY
    return sqlite3.SQLITE_OK


def migrate_copy(source_root: Path, destination_root: Path) -> MigrationReceipt:
    """Prepare a verified copy/backup; never replace or activate the source store."""
    try:
        source_path = _store_path(source_root)
        with _read_database(source_path) as source:
            metadata = _metadata(source)
            source_version = metadata["version"]
            for version in range(source_version, CURRENT_VERSION):
                if version not in MIGRATIONS:
                    c._fail("MIGRATION_UNAVAILABLE", "migration.version", "No implemented migration path exists for this version.")
            source_sha = _hash_file(source_path)
            destination_root = _new_directory(destination_root, Path(metadata["workspace"]), source=source_path.parent)
            backup, prepared = destination_root / BACKUP_NAME, destination_root / DATABASE_NAME
            _copy_exact(source_path, backup, source_sha)
            _copy_exact(backup, prepared, source_sha)
            connection = sqlite3.connect(prepared.as_uri() + "?mode=rw", uri=True, timeout=0, isolation_level=None)
            connection.row_factory = sqlite3.Row
            try:
                connection.execute("BEGIN IMMEDIATE")
                connection.set_authorizer(_migration_sql)
                for version in range(source_version, CURRENT_VERSION):
                    MIGRATIONS[version](connection)
                    if not connection.in_transaction:
                        c._fail("MIGRATION_TRANSACTION_LOST", "migration.transaction", "A migration rolled back its transaction; no version was stamped.")
                connection.set_authorizer(None)
                if not connection.in_transaction:
                    c._fail("MIGRATION_TRANSACTION_LOST", "migration.transaction", "Version stamping requires the original active transaction.")
                connection.execute(f"PRAGMA user_version={CURRENT_VERSION}")
                upgraded = _metadata(connection)
                if upgraded != {**metadata, "version": CURRENT_VERSION}:
                    c._fail("MIGRATION_IDENTITY_CHANGED", "migration.metadata", "Migration cannot change store/environment/workspace identity.")
                if [row[0] for row in connection.execute("PRAGMA quick_check")] != ["ok"]:
                    c._fail("INVALID_STORE", "migration.database", "Prepared database failed consistency checks.")
                connection.execute("COMMIT")
            except BaseException:
                connection.set_authorizer(None)
                if connection.in_transaction:
                    connection.execute("ROLLBACK")
                raise
            finally:
                connection.close()
            if _hash_file(source_path) != source_sha or _hash_file(backup) != source_sha:
                c._fail("SOURCE_CHANGED", "migration.source", "Source or preserved backup changed during preparation.")
            return {
                "scope": "prepared_copy_only", "store_id": metadata["store_id"],
                "source_version": source_version, "target_version": CURRENT_VERSION,
                "source_sha": source_sha, "backup_sha": _hash_file(backup), "prepared_sha": _hash_file(prepared),
            }
    except (OSError, sqlite3.Error) as error:
        c._fail("MIGRATION_FAILED", "migration", f"Preparation failed; source is not replaced; inspect the owned copy ({type(error).__name__}).")
