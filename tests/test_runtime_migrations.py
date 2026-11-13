"""TC-109/110: owned synthetic stores; v1 approval and original bytes never migrate."""

from contextlib import closing
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

from plugins.sparkforge.runtime import contracts as c
from plugins.sparkforge.runtime import migrations as m
from test_native_factory import factory as v1, spec_fixture


ROOT = Path(__file__).resolve().parents[1]


class RuntimeMigrationTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="coexistence ", dir=ROOT / "tests")
        self.addCleanup(temporary.cleanup)
        self.base = Path(temporary.name)
        self.workspace = self.base / "workspace"
        self.workspace.mkdir()
        (self.workspace / "component.py").write_text("print('EXPECTED-BEHAVIOR')\n", encoding="utf-8")
        self.source = self.base / "coordinated"
        self.legacy = self.base / "assisted"

    def create(self):
        return m.create_store(self.source, workspace=self.workspace, environment="LOCAL_DEVELOPMENT")

    def error(self, code, function, *args, **kwargs):
        with self.assertRaises(c.ContractError) as caught:
            function(*args, **kwargs)
        self.assertEqual(caught.exception.code, code)

    def legacy_job(self, *, approve=False):
        state = v1.init_job(spec_fixture(), self.workspace, self.legacy)
        if approve:
            v1.decide(self.legacy, state["spec_sha"], "accept", "synthetic-operator")
        return self.legacy / "job.sqlite3"

    def test_new_store_is_a_separate_header_without_job_or_decision(self):
        metadata = self.create()
        self.assertEqual(m.inspect_store(self.source), metadata)
        self.assertEqual(metadata["version"], 1)
        self.assertEqual(metadata["environment"], "LOCAL_DEVELOPMENT")
        self.assertFalse((self.source / "job.sqlite3").exists())
        with closing(sqlite3.connect(self.source / m.DATABASE_NAME)) as connection, connection:
            tables = [row[0] for row in connection.execute("SELECT name FROM sqlite_schema WHERE type='table'")]
        self.assertEqual(tables, ["runtime_metadata"])

    def test_legacy_references_preserve_bytes_and_do_not_import_approval(self):
        path = self.legacy_job(approve=True)
        before = path.read_bytes()
        children = sorted(item.name for item in self.legacy.iterdir())
        with patch.object(m.v1, "_connection", side_effect=AssertionError("v1 writable API must not be used")):
            reference = m.legacy_reference(self.legacy)
        self.assertEqual(path.read_bytes(), before)
        self.assertEqual(sorted(item.name for item in self.legacy.iterdir()), children)
        self.assertEqual(reference["evidence_class"], "assisted_v1_reference_only")
        self.assertFalse(reference["has_unresolved_run"])
        self.assertNotIn("decision", reference)
        self.assertNotIn("approved", reference)
        self.assertNotIn("workspace", reference)
        self.error("LEGACY_STORE", m.inspect_store, self.legacy)
        self.error("LEGACY_STORE", m.migrate_copy, self.legacy, self.base / "adoption")
        self.assertFalse((self.base / "adoption").exists())
        self.assertEqual(path.read_bytes(), before)

    def test_unaccepted_v1_job_still_requires_its_real_exact_spec_decision(self):
        path = self.legacy_job()
        before = path.read_bytes()
        m.legacy_reference(self.legacy)
        with self.assertRaises(v1.FactoryError) as caught:
            v1.run_check(self.legacy, "behavior", confirm_run=True)
        self.assertEqual(caught.exception.code, "APPROVAL_REQUIRED")
        self.assertEqual(path.read_bytes(), before)

    def test_read_only_connection_denies_writes(self):
        path = self.legacy_job()
        before = path.read_bytes()
        with m._read_database(path) as connection:
            with self.assertRaises(sqlite3.OperationalError):
                connection.execute("DELETE FROM state")
        self.assertEqual(path.read_bytes(), before)

    def test_existing_overlapping_legacy_and_foreign_stores_are_not_adopted(self):
        self.create()
        before = (self.source / m.DATABASE_NAME).read_bytes()
        self.error("STORE_EXISTS", m.create_store, self.source, workspace=self.workspace, environment="LOCAL_DEVELOPMENT")
        self.error("OVERLAPPING_STATE", m.create_store, self.workspace / "state",
                   workspace=self.workspace, environment="LOCAL_DEVELOPMENT")
        self.error("UNSAFE_PATH", m.create_store, Path("relative"), workspace=self.workspace, environment="LOCAL_DEVELOPMENT")
        self.legacy_job()
        self.error("LEGACY_COLOCATION", m.create_store, self.legacy / "coordinated",
                   workspace=self.workspace, environment="LOCAL_DEVELOPMENT")
        self.error("OVERLAPPING_STATE", m.migrate_copy, self.source, self.source / "nested")
        foreign = self.base / "foreign"
        foreign.mkdir()
        with closing(sqlite3.connect(foreign / m.DATABASE_NAME)) as connection, connection:
            connection.execute("CREATE TABLE unrelated(value TEXT)")
        self.error("FOREIGN_STORE", m.inspect_store, foreign)
        self.assertEqual((self.source / m.DATABASE_NAME).read_bytes(), before)

    def test_unknown_version_fails_before_creating_destination(self):
        self.create()
        with closing(sqlite3.connect(self.source / m.DATABASE_NAME)) as connection, connection:
            connection.execute("PRAGMA user_version=999")
        before = (self.source / m.DATABASE_NAME).read_bytes()
        destination = self.base / "future"
        self.error("UNSUPPORTED_STORE_VERSION", m.migrate_copy, self.source, destination)
        self.assertFalse(destination.exists())
        self.assertEqual((self.source / m.DATABASE_NAME).read_bytes(), before)

    def test_same_version_copy_is_verified_and_never_activated(self):
        metadata = self.create()
        before = (self.source / m.DATABASE_NAME).read_bytes()
        destination = self.base / "prepared"
        receipt = m.migrate_copy(self.source, destination)
        self.assertEqual(receipt["scope"], "prepared_copy_only")
        self.assertEqual(receipt["source_sha"], receipt["backup_sha"])
        self.assertEqual(m.inspect_store(destination), metadata)
        self.assertEqual((destination / m.BACKUP_NAME).read_bytes(), before)
        self.assertEqual((self.source / m.DATABASE_NAME).read_bytes(), before)
        self.error("STORE_EXISTS", m.migrate_copy, self.source, destination)

    def test_future_fixture_migration_observes_verified_backup_before_any_write(self):
        metadata = self.create()
        original = (self.source / m.DATABASE_NAME).read_bytes()
        destination = self.base / "upgraded-fixture"
        calls = []

        def migrate(connection):
            self.assertEqual((destination / m.BACKUP_NAME).read_bytes(), original)
            self.assertEqual((self.source / m.DATABASE_NAME).read_bytes(), original)
            connection.execute("CREATE TABLE fixture_revision_two(value TEXT NOT NULL)")
            connection.execute("INSERT INTO fixture_revision_two VALUES('synthetic')")
            calls.append("migration")

        with patch.object(m, "CURRENT_VERSION", 2), patch.dict(m.MIGRATIONS, {1: migrate}):
            receipt = m.migrate_copy(self.source, destination)
            self.assertEqual(m.inspect_store(destination), {**metadata, "version": 2})
        self.assertEqual(calls, ["migration"])
        self.assertEqual(receipt["source_version"], 1)
        self.assertEqual(receipt["target_version"], 2)
        self.assertEqual((self.source / m.DATABASE_NAME).read_bytes(), original)
        self.assertEqual((destination / m.BACKUP_NAME).read_bytes(), original)
        self.error("UNSUPPORTED_STORE_VERSION", m.inspect_store, destination)

    def test_interrupted_migration_rolls_back_and_preserves_source_and_backup(self):
        self.create()
        original = (self.source / m.DATABASE_NAME).read_bytes()
        destination = self.base / "interrupted"

        def migrate(connection):
            connection.execute("CREATE TABLE partial_change(value TEXT)")
            connection.execute("INSERT INTO partial_change VALUES('must roll back')")
            raise RuntimeError("Synthetic migration interruption")

        with patch.object(m, "CURRENT_VERSION", 2), patch.dict(m.MIGRATIONS, {1: migrate}):
            with self.assertRaisesRegex(RuntimeError, "Synthetic migration interruption"):
                m.migrate_copy(self.source, destination)
        with closing(sqlite3.connect(destination / m.DATABASE_NAME)) as connection, connection:
            self.assertEqual(connection.execute("PRAGMA user_version").fetchone()[0], 1)
            self.assertIsNone(connection.execute("SELECT name FROM sqlite_schema WHERE name='partial_change'").fetchone())
        self.assertEqual((self.source / m.DATABASE_NAME).read_bytes(), original)
        self.assertEqual((destination / m.BACKUP_NAME).read_bytes(), original)

    def test_migration_cannot_commit_early_attach_or_rebind_environment(self):
        self.create()
        original = (self.source / m.DATABASE_NAME).read_bytes()
        for statement, code in (
            ("COMMIT", "MIGRATION_FAILED"),
            ("ATTACH DATABASE ':memory:' AS other", "MIGRATION_FAILED"),
            ("UPDATE runtime_metadata SET environment='CORP'", "MIGRATION_IDENTITY_CHANGED"),
        ):
            destination = self.base / ("rejected-" + str(len(list(self.base.iterdir()))))

            def migrate(connection):
                connection.execute("CREATE TABLE partial_change(value TEXT)")
                connection.execute(statement)

            with patch.object(m, "CURRENT_VERSION", 2), patch.dict(m.MIGRATIONS, {1: migrate}):
                self.error(code, m.migrate_copy, self.source, destination)
            with closing(sqlite3.connect(destination / m.DATABASE_NAME)) as connection, connection:
                self.assertIsNone(connection.execute("SELECT name FROM sqlite_schema WHERE name='partial_change'").fetchone())
                self.assertEqual(connection.execute("SELECT environment FROM runtime_metadata").fetchone()[0], "LOCAL_DEVELOPMENT")
            self.assertEqual((self.source / m.DATABASE_NAME).read_bytes(), original)

    def test_missing_migration_and_unverified_copy_never_run_a_step(self):
        self.create()
        destination = self.base / "missing-step"
        with patch.object(m, "CURRENT_VERSION", 2):
            self.error("MIGRATION_UNAVAILABLE", m.migrate_copy, self.source, destination)
        self.assertFalse(destination.exists())
        destination = self.base / "bad-copy"
        original_hash = m._hash_file

        def corrupt_hash(path):
            return "f" * 64 if path.name == m.BACKUP_NAME else original_hash(path)

        with patch.object(m, "_hash_file", side_effect=corrupt_hash):
            self.error("COPY_MISMATCH", m.migrate_copy, self.source, destination)
        self.assertFalse((destination / m.DATABASE_NAME).exists())

    def test_live_or_unreconciled_sidecars_are_rejected_not_recovered(self):
        self.create()
        path = self.source / m.DATABASE_NAME
        before = path.read_bytes()
        journal = self.source / (m.DATABASE_NAME + "-journal")
        journal.write_bytes(b"synthetic unresolved journal marker")
        self.error("STORE_BUSY", m.inspect_store, self.source)
        self.error("STORE_BUSY", m.migrate_copy, self.source, self.base / "busy-copy")
        self.assertEqual(path.read_bytes(), before)
        self.assertEqual(journal.read_bytes(), b"synthetic unresolved journal marker")

    def test_closed_wal_legacy_database_is_rejected_without_creating_sidecars(self):
        path = self.legacy_job()
        with closing(sqlite3.connect(path)) as connection, connection:
            self.assertEqual(connection.execute("PRAGMA journal_mode=WAL").fetchone()[0], "wal")
        before = path.read_bytes()
        names = sorted(item.name for item in self.legacy.iterdir())
        self.error("STORE_BUSY", m.legacy_reference, self.legacy)
        self.assertEqual(path.read_bytes(), before)
        self.assertEqual(sorted(item.name for item in self.legacy.iterdir()), names)

    def test_handled_automatic_rollback_never_stamps_an_upgraded_version(self):
        self.create()
        original = (self.source / m.DATABASE_NAME).read_bytes()
        destination = self.base / "automatic-rollback"

        def migrate(connection):
            connection.execute("CREATE TABLE partial_change(value TEXT UNIQUE)")
            connection.execute("INSERT INTO partial_change VALUES('duplicate')")
            try:
                connection.execute("INSERT OR ROLLBACK INTO partial_change VALUES('duplicate')")
            except sqlite3.IntegrityError:
                pass

        with patch.object(m, "CURRENT_VERSION", 2), patch.dict(m.MIGRATIONS, {1: migrate}):
            with self.assertRaises(c.ContractError):
                m.migrate_copy(self.source, destination)
        with closing(sqlite3.connect(destination / m.DATABASE_NAME)) as connection, connection:
            self.assertEqual(connection.execute("PRAGMA user_version").fetchone()[0], 1)
            self.assertIsNone(connection.execute("SELECT name FROM sqlite_schema WHERE name='partial_change'").fetchone())
        self.assertEqual((self.source / m.DATABASE_NAME).read_bytes(), original)
        self.assertEqual((destination / m.BACKUP_NAME).read_bytes(), original)


if __name__ == "__main__":
    unittest.main()
