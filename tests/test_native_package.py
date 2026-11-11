"""Synthetic structural package checks; no host, model, install or live helper."""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import unittest
import uuid
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from scripts import build_sparkforge_package as package


ROOT = Path(__file__).absolute().parent.parent
CANONICAL = ROOT / "plugins" / "sparkforge"
BUILDER = ROOT / "scripts" / "build_sparkforge_package.py"
HELPERS = {"scripts/factory.py", "scripts/knowledge.py"}
SYNTHETIC_FACTORY = (
    "from knowledge import fixture_identity\n"
    "if __name__ == '__main__':\n"
    "    print(fixture_identity())\n"
)
SYNTHETIC_KNOWLEDGE = (
    "def fixture_identity():\n"
    "    return 'SYNTHETIC_PACKAGE_FIXTURE_ONLY'\n"
)


def canonical_digest(value: object) -> str:
    data = json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":"))
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


class NativePackageCase(unittest.TestCase):
    def setUp(self) -> None:
        # All ephemeral fixtures stay under this project's tests, never system temp.
        self.case = ROOT / "tests" / f".native-package-case-{uuid.uuid4().hex}"
        self.case.mkdir()
        self.addCleanup(shutil.rmtree, self.case)
        self.repository = self.case / "synthetic repository"
        self.source = self.repository / "plugins" / "sparkforge"
        self.source.mkdir(parents=True)
        for relative in package.SOURCE_FILES:
            target = self.source.joinpath(*relative.split("/"))
            target.parent.mkdir(parents=True, exist_ok=True)
            if relative == "scripts/factory.py":
                target.write_text(SYNTHETIC_FACTORY, encoding="utf-8")
            elif relative == "scripts/knowledge.py":
                target.write_text(SYNTHETIC_KNOWLEDGE, encoding="utf-8")
            else:
                shutil.copyfile(CANONICAL.joinpath(*relative.split("/")), target)
        self.output = self.case / "new package with spaces"

    def write_json(self, path: Path, value: object) -> None:
        path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")

    def manifest(self) -> dict:
        return json.loads((self.source / "plugin.json").read_text(encoding="utf-8"))

    def inventory(self, output: Path | None = None) -> dict:
        return json.loads(((output or self.output) / package.INVENTORY_FILE).read_text(encoding="utf-8"))

    def build(self, profile: str = "corp", output: Path | None = None) -> dict:
        return package.build_package(profile, output or self.output, self.source)

    def denied(self, profile: str = "corp", *, output: Path | str | None = None) -> None:
        target = self.output if output is None else output
        with self.assertRaises(package.PackageError):
            package.build_package(profile, target, self.source)
        self.assertFalse(self.output.exists(), "a preflight failure created output")

    def test_corp_and_acro_profiles_match_the_exact_inventory(self) -> None:
        for profile in package.PROFILES:
            with self.subTest(profile=profile):
                output = self.case / profile
                report = self.build(profile, output)
                self.assertEqual(report, package.validate_package(output, profile))
                self.assertTrue(report["valid"])
                self.assertEqual(report["compatibility"], "NOT_ASSESSED")
                self.assertEqual(report["validation_scope"], "STRUCTURAL_ONLY")
                self.assertEqual(report["name"], "sparkforge")
                self.assertEqual(report["version"], "0.1.0")
                expected = set(package.SOURCE_FILES)
                manifest = json.loads((output / "plugin.json").read_text(encoding="utf-8"))
                if profile == "corp":
                    self.assertNotIn("engines", manifest)
                    self.assertEqual(
                        json.loads((output / "agency.json").read_text(encoding="utf-8")),
                        {"engines": ["copilot"], "platforms": ["windows"]},
                    )
                else:
                    expected.remove("agency.json")
                    self.assertEqual(manifest["engines"], ["copilot"])
                    self.assertFalse((output / "agency.json").exists())
                actual = {file.relative_to(output).as_posix() for file in output.rglob("*") if file.is_file()}
                self.assertEqual(actual, expected | {package.INVENTORY_FILE})
                self.assertEqual(manifest["skills"], ["skills/sparkforge"])
                self.assertEqual(manifest["agents"], ["agents/sparkforge.agent.md"])
                self.assertEqual([entry["path"] for entry in report["files"]], sorted(expected))
                for entry in report["files"]:
                    data = output.joinpath(*entry["path"].split("/")).read_bytes()
                    self.assertEqual(entry["size_bytes"], len(data))
                    self.assertEqual(entry["sha256"], hashlib.sha256(data).hexdigest())

    def test_digest_inventory_is_deterministic_portable_and_profile_bound(self) -> None:
        before = {relative: self.source.joinpath(*relative.split("/")).read_bytes() for relative in package.SOURCE_FILES}
        first = self.build("corp", self.case / "first")
        second = self.build("corp", self.case / "second")
        acro = self.build("acro", self.case / "acro")
        self.assertEqual(first, second)
        self.assertNotEqual(first["package_sha256"], acro["package_sha256"])
        self.assertEqual(first["source_sha256"], acro["source_sha256"])
        self.assertEqual(first["source_manifest_sha256"], canonical_digest(self.manifest()))
        encoded = json.dumps(first)
        self.assertNotIn(str(self.case), encoded)
        self.assertNotIn(str(self.case).replace("\\", "\\\\"), encoded)
        self.assertNotIn("timestamp", encoded)
        for entry in first["files"] + first["source_files"]:
            self.assertFalse(Path(entry["path"]).is_absolute())
            self.assertNotIn("\\", entry["path"])
        self.assertEqual(before, {
            relative: self.source.joinpath(*relative.split("/")).read_bytes()
            for relative in package.SOURCE_FILES
        })

    def test_both_profiles_relocate_without_original_source_or_cwd_dependency(self) -> None:
        locations = {}
        for profile in package.PROFILES:
            original = self.case / f"original-{profile}"
            expected = self.build(profile, original)
            moved = self.case / f"relocated {profile} deployment"
            shutil.move(str(original), moved)
            locations[profile] = (moved, expected)
        shutil.rmtree(self.repository)
        unrelated = self.case / "unrelated working directory"
        unrelated.mkdir()
        for profile, (moved, expected) in locations.items():
            with self.subTest(profile=profile):
                self.assertEqual(package.validate_package(moved, profile), expected)
                result = subprocess.run(
                    [sys.executable, "-B", str(moved / "scripts" / "factory.py")],
                    cwd=unrelated, capture_output=True, text=True, timeout=30,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stdout.strip(), "SYNTHETIC_PACKAGE_FIXTURE_ONLY")
                self.assertEqual(package.validate_package(moved, profile), expected)

    def test_unlisted_source_files_are_never_copied(self) -> None:
        extras = {
            ".env": "SYNTHETIC_SECRET_DO_NOT_EXPORT",
            "runtime/job.sqlite": "SYNTHETIC_STATE",
            "raw-wiki/page.md": "SYNTHETIC_RAW_WIKI",
            "scripts/unowned.py": "raise RuntimeError('must not execute')\n",
            "agents/other.agent.md": "unlisted agent",
            package.INVENTORY_FILE: '{"stale": true}',
        }
        for relative, content in extras.items():
            path = self.source.joinpath(*relative.split("/"))
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
        report = self.build()
        for relative in extras:
            if relative != package.INVENTORY_FILE:
                self.assertFalse(self.output.joinpath(*relative.split("/")).exists())
        self.assertNotIn("SYNTHETIC_SECRET", json.dumps(report))
        self.assertNotIn("stale", self.inventory())

    def test_every_source_resource_is_required_even_for_acro(self) -> None:
        for profile in package.PROFILES:
            for relative in package.SOURCE_FILES:
                with self.subTest(profile=profile, missing=relative):
                    target = self.source.joinpath(*relative.split("/"))
                    data = target.read_bytes()
                    target.unlink()
                    try:
                        self.denied(profile)
                    finally:
                        target.write_bytes(data)

    def test_unexpected_profiles_are_not_normalized(self) -> None:
        for profile in ("CORP", " corp", "acro ", "other", "", None, True, 1, []):
            with self.subTest(profile=profile):
                self.denied(profile)
                with self.assertRaises(package.PackageError):
                    package.validate_package(self.source, profile)

    def test_preexisting_directory_is_untouched(self) -> None:
        self.output.mkdir()
        sentinel = self.output / "do-not-touch.txt"
        sentinel.write_text("existing owner data", encoding="utf-8")
        with self.assertRaisesRegex(package.PackageError, "already exists"):
            self.build()
        self.assertEqual(sentinel.read_text(encoding="utf-8"), "existing owner data")
        self.assertEqual(list(self.output.iterdir()), [sentinel])

    def test_preexisting_file_and_empty_directory_are_rejected(self) -> None:
        self.output.write_bytes(b"existing file")
        with self.assertRaises(package.PackageError):
            self.build()
        self.assertEqual(self.output.read_bytes(), b"existing file")
        self.output.unlink()
        self.output.mkdir()
        with self.assertRaises(package.PackageError):
            self.build()
        self.assertEqual(list(self.output.iterdir()), [])

    def test_interrupted_assembly_retains_partial_output_without_reusing_it(self) -> None:
        original = Path.open
        target = self.output / "scripts" / "factory.py"

        def fail_write(path: Path, mode="r", *args, **kwargs):
            if path == target and mode == "xb":
                raise OSError("synthetic interrupted write")
            return original(path, mode, *args, **kwargs)

        with patch.object(Path, "open", fail_write):
            with self.assertRaisesRegex(package.PackageError, "partial output retained"):
                self.build()
        self.assertTrue(self.output.is_dir())
        self.assertFalse((self.output / package.INVENTORY_FILE).exists())
        with self.assertRaises(package.PackageError):
            package.validate_package(self.output, "corp")
        with self.assertRaisesRegex(package.PackageError, "already exists"):
            self.build()
        self.assertTrue((self.source / "scripts" / "factory.py").is_file())

    def test_source_output_overlap_is_rejected_in_both_directions(self) -> None:
        for output in (self.source, self.source / "build", self.source.parent, self.repository):
            with self.subTest(output=output):
                with self.assertRaisesRegex(package.PackageError, "overlap"):
                    self.build(output=output)
        self.assertTrue((self.source / "plugin.json").is_file())
        self.assertFalse((self.source / "build").exists())

    def test_missing_output_parent_and_source_are_rejected_without_creation(self) -> None:
        self.denied(output=self.case / "missing parent" / "new")
        self.assertFalse((self.case / "missing parent").exists())
        with self.assertRaises(package.PackageError):
            package.build_package("corp", self.output, self.case / "missing-source")
        self.assertFalse(self.output.exists())

    def test_noncanonical_filesystem_paths_are_not_normalized(self) -> None:
        separator = os.sep
        bad = [
            f"{self.case}{separator}child{separator}..{separator}new",
            f"{self.case}{separator}.{separator}new",
            f"{self.case}{separator}{separator}new",
            f"{self.case}{separator}new{separator}",
            f"{self.case}{separator}new.",
            f"{self.case}{separator}new ",
            f"{self.case}{separator}NUL",
            f"{self.case}{separator}payload:stream",
            "C:drive-relative",
            "\\\\server\\share\\new",
        ]
        for target in bad:
            with self.subTest(target=target):
                self.denied(output=target)
        with self.assertRaises(package.PackageError):
            package.build_package("corp", self.output, f"{self.source}{separator}..{separator}sparkforge")

    def test_declared_traversal_absolute_alias_and_windows_paths_fail(self) -> None:
        original = self.manifest()
        bad = (
            "../escape", "/absolute", "skills/../sparkforge", "skills/./sparkforge",
            "skills//sparkforge", "skills/sparkforge/", "skills\\sparkforge",
            "C:/outside", "C:outside", "\\\\server\\share",
            "Skills/sparkforge", "skills/sparkforge.", "skills/NUL",
            "skills/sparkforge:stream", "", None, True,
        )
        for declaration in bad:
            with self.subTest(declaration=declaration):
                manifest = {**original, "skills": [declaration]}
                self.write_json(self.source / "plugin.json", manifest)
                self.denied()
        self.write_json(self.source / "plugin.json", original)

    def test_manifest_and_owned_resource_declarations_must_agree(self) -> None:
        original = self.manifest()
        changes = (
            {"name": "another-name"},
            {"version": "0.2.0"},
            {"description": ""},
            {"description": None},
            {"skills": []},
            {"agents": []},
            {"skills": "skills/sparkforge"},
            {"skills": ["skills/sparkforge", "skills/another"]},
            {"agents": ["agents/another.agent.md"]},
            {"engines": ["copilot"]},
            {"mcpServers": {"unapproved": {"command": "never-run"}}},
        )
        for change in changes:
            with self.subTest(change=change):
                self.write_json(self.source / "plugin.json", {**original, **change})
                self.denied()

    def test_agency_support_cannot_be_broadened_or_moved_silently(self) -> None:
        bad = (
            {"engines": ["copilot"], "platforms": ["windows", "linux"]},
            {"engines": ["claude", "copilot"], "platforms": ["windows"]},
            {"engines": ["copilot"]},
            {"engines": ["copilot"], "platforms": ["windows"], "dependencies": ["other"]},
        )
        for value in bad:
            with self.subTest(value=value):
                self.write_json(self.source / "agency.json", value)
                self.denied("acro")

    def test_duplicate_keys_non_json_values_and_non_objects_fail(self) -> None:
        path = self.source / "plugin.json"
        original = path.read_text(encoding="utf-8")
        invalid = (
            original.replace('"name":', '"name": "other", "name":', 1),
            original.replace('"description":', '"unapproved": NaN, "description":', 1),
            "[]", "true", "{", "\ufeff" + original,
        )
        for text in invalid:
            with self.subTest(text=text[:60]):
                path.write_text(text, encoding="utf-8")
                self.denied()

    def test_agent_and_skill_frontmatter_cannot_widen_permissions(self) -> None:
        for relative in ("agents/sparkforge.agent.md", "skills/sparkforge/SKILL.md"):
            path = self.source.joinpath(*relative.split("/"))
            original = path.read_text(encoding="utf-8")
            for replacement in (
                original.replace("name: sparkforge", "name: different", 1),
                original.replace("name: sparkforge", "name: sparkforge\ntools: all", 1),
                original.replace("name: sparkforge", "name: sparkforge\nmcpServers: auto-start", 1),
                original.replace("name: sparkforge", "name: sparkforge\nname: sparkforge", 1),
                "# no frontmatter\n",
                "---\nname: sparkforge\ndescription: fixture\n---\n",
            ):
                with self.subTest(relative=relative, replacement=replacement[:70]):
                    path.write_text(replacement, encoding="utf-8")
                    self.denied()
            path.write_text(original, encoding="utf-8")

    def test_helpers_are_syntax_checked_but_not_executed(self) -> None:
        path = self.source / "scripts" / "factory.py"
        path.write_text("raise RuntimeError('must never execute while building')\n", encoding="utf-8")
        self.build()
        path.write_text("def broken(:\n", encoding="utf-8")
        with self.assertRaisesRegex(package.PackageError, "Python syntax"):
            self.build(output=self.case / "invalid-helper")
        self.assertFalse((self.case / "invalid-helper").exists())

    def test_empty_oversized_and_non_utf8_resources_fail_preflight(self) -> None:
        path = self.source / "README.md"
        for data in (b"", b" " * 3, b"x" * (package.MAX_RESOURCE_BYTES + 1), b"\xff"):
            with self.subTest(length=len(data)):
                path.write_bytes(data)
                self.denied()

    def test_file_cannot_replace_a_required_directory(self) -> None:
        shutil.rmtree(self.source / "skills")
        (self.source / "skills").write_text("not a directory", encoding="utf-8")
        self.denied()

    def test_actual_resource_casing_must_match_the_manifest_inventory(self) -> None:
        original = self.source / "skills" / "sparkforge" / "SKILL.md"
        original.rename(original.with_name("skill.MD"))
        with self.assertRaisesRegex(package.PackageError, "casing"):
            self.build()
        self.assertFalse(self.output.exists())

    def test_reparse_sources_resources_and_output_ancestors_are_rejected(self) -> None:
        original = Path.lstat
        for target in (
            self.source, self.source.parent, self.source / "scripts",
            self.source / "scripts" / "factory.py", self.case,
        ):
            def reparse(path: Path, *args, **kwargs):
                info = original(path, *args, **kwargs)
                if path == target:
                    return SimpleNamespace(st_mode=info.st_mode, st_file_attributes=0x400)
                return info

            with self.subTest(target=target), patch.object(Path, "lstat", reparse):
                with self.assertRaisesRegex(package.PackageError, "reparse"):
                    self.build()
            self.assertFalse(self.output.exists())

    def test_symlink_mode_is_rejected_without_following_it(self) -> None:
        original = Path.lstat
        target = self.source / "scripts" / "factory.py"

        def link_stat(path: Path, *args, **kwargs):
            if path == target:
                return SimpleNamespace(st_mode=stat.S_IFLNK | 0o777, st_file_attributes=0)
            return original(path, *args, **kwargs)

        with patch.object(Path, "lstat", link_stat):
            with self.assertRaisesRegex(package.PackageError, "symlinks"):
                self.build()
        self.assertFalse(self.output.exists())

    def test_hardlinked_resource_is_rejected(self) -> None:
        source = self.source / "scripts" / "knowledge.py"
        link = self.case / "synthetic hardlink.py"
        try:
            os.link(source, link)
        except OSError as exc:
            self.skipTest(f"host cannot create an owned hardlink fixture: {type(exc).__name__}")
        with self.assertRaisesRegex(package.PackageError, "hard-linked"):
            self.build()
        self.assertFalse(self.output.exists())

    def test_windows_path_handle_ctime_disagreement_does_not_change_content_binding(self) -> None:
        original = os.fstat

        def metadata_only(fd: int):
            info = original(fd)
            return SimpleNamespace(
                st_mode=info.st_mode, st_nlink=info.st_nlink,
                st_dev=info.st_dev, st_ino=info.st_ino, st_size=info.st_size,
                st_mtime_ns=info.st_mtime_ns, st_ctime_ns=info.st_ctime_ns + 1,
                st_file_attributes=getattr(info, "st_file_attributes", 0),
            )

        with patch.object(os, "fstat", metadata_only):
            report = self.build()
        self.assertEqual(package.validate_package(self.output, "corp"), report)

    def test_content_stat_change_during_read_is_rejected(self) -> None:
        original = Path.lstat
        target = self.source / "plugin.json"
        visits = 0

        def changed(path: Path, *args, **kwargs):
            nonlocal visits
            info = original(path, *args, **kwargs)
            if path == target:
                visits += 1
                if visits >= 2:
                    return SimpleNamespace(
                        st_mode=info.st_mode, st_nlink=info.st_nlink,
                        st_dev=info.st_dev, st_ino=info.st_ino, st_size=info.st_size,
                        st_mtime_ns=info.st_mtime_ns + 1, st_ctime_ns=info.st_ctime_ns,
                        st_file_attributes=getattr(info, "st_file_attributes", 0),
                    )
            return info

        with patch.object(Path, "lstat", changed):
            with self.assertRaisesRegex(package.PackageError, "changed during inspection"):
                self.build()
        self.assertFalse(self.output.exists())

    def test_wrong_profile_cannot_validate_another_profile(self) -> None:
        for built, claimed in (("corp", "acro"), ("acro", "corp")):
            with self.subTest(built=built, claimed=claimed):
                output = self.case / built
                self.build(built, output)
                with self.assertRaises(package.PackageError):
                    package.validate_package(output, claimed)

    def test_validation_detects_missing_or_changed_files(self) -> None:
        for index, relative in enumerate((*package.SOURCE_FILES, package.INVENTORY_FILE)):
            with self.subTest(relative=relative):
                output = self.case / f"missing-{index}"
                self.build(output=output)
                output.joinpath(*relative.split("/")).unlink()
                with self.assertRaises(package.PackageError):
                    package.validate_package(output, "corp")
        self.build()
        (self.output / "README.md").write_text("changed bytes", encoding="utf-8")
        with self.assertRaisesRegex(package.PackageError, "digest inventory"):
            package.validate_package(self.output, "corp")

    def test_validation_rejects_unexpected_files_and_empty_directories(self) -> None:
        for index, (relative, is_directory) in enumerate((
            ("raw-wiki", True), ("state.sqlite", False), ("scripts/unowned.py", False),
        )):
            with self.subTest(relative=relative):
                output = self.case / f"extra-{index}"
                self.build(output=output)
                path = output.joinpath(*relative.split("/"))
                if is_directory:
                    path.mkdir()
                else:
                    path.write_text("not part of the package", encoding="utf-8")
                with self.assertRaisesRegex(package.PackageError, "undeclared"):
                    package.validate_package(output, "corp")

    def test_inventory_path_injection_is_rejected_before_resource_read(self) -> None:
        self.build()
        original = self.inventory()
        for value in ("../outside", "/absolute", "C:/outside", "scripts\\factory.py", "README.md."):
            with self.subTest(value=value):
                record = json.loads(json.dumps(original))
                record["files"][0]["path"] = value
                self.write_json(self.output / package.INVENTORY_FILE, record)
                with self.assertRaises(package.PackageError):
                    package.validate_package(self.output, "corp")

    def test_inventory_schema_digests_and_sizes_are_checked(self) -> None:
        self.build()
        original = self.inventory()
        changes = (
            ("schema_version", "other"),
            ("profile", "acro"),
            ("compatibility", "SUPPORTED"),
            ("validation_scope", "LIVE"),
            ("source_sha256", "0" * 64),
            ("package_sha256", "0" * 64),
            ("source_manifest_sha256", "0" * 64),
            ("source_files", []),
            ("files", []),
        )
        for key, value in changes:
            with self.subTest(key=key):
                record = {**original, key: value}
                self.write_json(self.output / package.INVENTORY_FILE, record)
                with self.assertRaises(package.PackageError):
                    package.validate_package(self.output, "corp")
        for key, value in (("size_bytes", True), ("sha256", "BAD"), ("extra", "not permitted")):
            with self.subTest(key=key):
                record = json.loads(json.dumps(original))
                record["files"][0][key] = value
                self.write_json(self.output / package.INVENTORY_FILE, record)
                with self.assertRaises(package.PackageError):
                    package.validate_package(self.output, "corp")

    def test_recorded_source_must_match_untransformed_payloads(self) -> None:
        self.build("acro")
        record = self.inventory()
        for entry in record["source_files"]:
            if entry["path"] == "README.md":
                entry["sha256"] = "0" * 64
        record["source_sha256"] = canonical_digest(record["source_files"])
        self.write_json(self.output / package.INVENTORY_FILE, record)
        with self.assertRaisesRegex(package.PackageError, "recorded source"):
            package.validate_package(self.output, "acro")

    def test_rewritten_acro_manifest_cannot_silently_change_source_semantics(self) -> None:
        self.build("acro")
        manifest_path = self.output / "plugin.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["description"] = "A changed description"
        self.write_json(manifest_path, manifest)
        record = self.inventory()
        for entry in record["files"]:
            if entry["path"] == "plugin.json":
                entry["sha256"] = hashlib.sha256(manifest_path.read_bytes()).hexdigest()
                entry["size_bytes"] = manifest_path.stat().st_size
        record["package_sha256"] = canonical_digest({"profile": "acro", "files": record["files"]})
        self.write_json(self.output / package.INVENTORY_FILE, record)
        with self.assertRaisesRegex(package.PackageError, "source manifest"):
            package.validate_package(self.output, "acro")

    def test_output_reparse_resource_fails_validation(self) -> None:
        self.build()
        original = Path.lstat
        target = self.output / "skills"

        def reparse(path: Path, *args, **kwargs):
            info = original(path, *args, **kwargs)
            if path == target:
                return SimpleNamespace(st_mode=info.st_mode, st_file_attributes=0x400)
            return info

        with patch.object(Path, "lstat", reparse):
            with self.assertRaisesRegex(package.PackageError, "reparse"):
                package.validate_package(self.output, "corp")

    def test_cli_default_source_is_relative_to_builder_not_cwd(self) -> None:
        scripts = self.repository / "scripts"
        scripts.mkdir()
        script = scripts / BUILDER.name
        shutil.copyfile(BUILDER, script)
        unrelated = self.case / "unrelated cwd"
        unrelated.mkdir()
        for profile in package.PROFILES:
            output = self.case / f"cli-{profile}"
            result = subprocess.run(
                [sys.executable, "-B", str(script), "--profile", profile, "--output", str(output)],
                cwd=unrelated, capture_output=True, text=True, timeout=30,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(result.stdout)
            self.assertEqual(report, package.validate_package(output, profile))
        result = subprocess.run(
            [sys.executable, "-B", str(script), "--profile", "corp", "--output", str(output)],
            cwd=unrelated, capture_output=True, text=True, timeout=30,
        )
        self.assertEqual(result.returncode, 2)
        self.assertFalse(json.loads(result.stderr)["valid"])
        self.assertEqual(result.stdout, "")

    def test_cli_does_not_normalize_profile_spelling(self) -> None:
        result = subprocess.run(
            [sys.executable, "-B", str(BUILDER), "--profile", "CORP", "--output", str(self.output)],
            cwd=ROOT, capture_output=True, text=True, timeout=30,
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("invalid choice", result.stderr)
        self.assertFalse(self.output.exists())

    def test_native_instructions_include_full_loop_and_manual_authority(self) -> None:
        agent = (CANONICAL / "agents" / "sparkforge.agent.md").read_text(encoding="utf-8")
        skill = (CANONICAL / "skills" / "sparkforge" / "SKILL.md").read_text(encoding="utf-8")
        prose = " ".join(skill.split())
        self.assertIn("skills\\sparkforge\\SKILL.md", agent)
        self.assertIn("two directory levels", skill)
        for phrase in (
            "wiki_context", "catalog_context", "component_context",
            "REUSE", "UPDATE_EXISTING", "NEW_COMPONENT", "validate-spec",
            "OPERATOR-OWNED", "STOP before implementation",
            "run-check", "record-review", "candidate digest", "max_attempts",
            "revise", "cancel", "reconcile", "CANDIDATE_VERIFIED",
            "inactive evidence-backed improvement proposal", "no-change",
            "engineering dogfooding", "concurrent", "disjoint",
            "snapshot adapter", "NOT_ASSESSED", "Corp and Acro",
        ):
            with self.subTest(phrase=phrase):
                self.assertTrue(phrase.casefold() in prose.casefold(), f"Native workflow is missing {phrase!r}")
        for text in (agent, skill):
            header = text.split("---", 2)[1]
            self.assertNotIn("tools:", header)
            self.assertNotIn("mcpServers:", header)
            self.assertNotIn("allowed-tools:", header)
            self.assertNotIn(str(ROOT), text)

    def test_documented_spec_uses_frozen_fields_and_labels_synthetic_authority(self) -> None:
        guide = (CANONICAL / "references" / "SPEC_FORMAT.md").read_text(encoding="utf-8")
        example = json.loads(guide.split("```json\n", 1)[1].split("\n```", 1)[0])
        self.assertEqual(set(example), {
            "schema_version", "id", "title", "problem", "audience", "environment",
            "builder_actor", "non_goals", "knowledge", "reuse", "controlled_files",
            "acceptance", "checks", "required_reviewers",
        })
        self.assertEqual(example["schema_version"], "sparkforge.spec.v1")
        self.assertEqual(example["knowledge"]["coverage"], "SNAPSHOT_SCOPE")
        self.assertIn("synthetic", example["builder_actor"])
        self.assertNotIn("approved", example)
        for check in example["checks"]:
            self.assertEqual(set(check), {
                "id", "argv", "timeout_seconds", "output_limit_bytes",
                "max_attempts", "required_markers", "retain_output",
            })
        self.assertIn("not an accepted brief", guide)

    def test_review_examples_bind_the_preinspection_context_without_relabeling(self) -> None:
        for relative in (
            "README.md", "references/SPEC_FORMAT.md", "skills/sparkforge/SKILL.md",
        ):
            text = CANONICAL.joinpath(*relative.split("/")).read_text(encoding="utf-8")
            prose = " ".join(text.split()).casefold()
            with self.subTest(relative=relative):
                commands = re.findall(
                    r"(?:FACTORY|\$Factory) record-review\b[^\n]*(?:\n--[^\n]*)*",
                    text,
                )
                self.assertTrue(commands, f"{relative}: missing record-review example")
                for command in commands:
                    self.assertIn("--candidate-sha", command)
                    self.assertIn("--review-context", command)
                for phrase in (
                    "review_context", "before inspecting", "same token",
                    "job ID", "exact spec SHA", "candidate SHA",
                    "check round", "check-evidence sequence", "re-review", "relabel",
                ):
                    self.assertTrue(
                        phrase.casefold() in prose,
                        f"{relative}: missing review-context safeguard {phrase!r}",
                    )


if __name__ == "__main__":
    unittest.main()
