"""Assemble the small native SparkForge package without installing or invoking it."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
import sys
from pathlib import Path, PureWindowsPath


NAME = "sparkforge"
VERSION = "0.1.0"
PROFILES = ("corp", "acro")
INVENTORY_FILE = "PACKAGE_INVENTORY.json"
MAX_RESOURCE_BYTES = 2 * 1024 * 1024
SOURCE_FILES = (
    "plugin.json",
    "agency.json",
    "agents/sparkforge.agent.md",
    "skills/sparkforge/SKILL.md",
    "README.md",
    "references/SPEC_FORMAT.md",
    "references/AUTHORITY.md",
    "scripts/factory.py",
    "scripts/knowledge.py",
)
_SKILLS = ["skills/sparkforge"]
_AGENTS = ["agents/sparkforge.agent.md"]
_DIGEST = re.compile(r"[0-9a-f]{64}\Z")
_DEVICE = re.compile(r"(?:CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(?:\.|$)", re.I)
_INVENTORY_KEYS = {
    "schema_version", "name", "version", "profile", "validation_scope",
    "compatibility", "files", "source_files", "source_sha256",
    "source_manifest_sha256", "package_sha256",
}


class PackageError(ValueError):
    """Invalid or unsafe package input; no compatibility or authority is implied."""


def _profile(profile: str) -> None:
    if type(profile) is not str or profile not in PROFILES:
        raise PackageError("profile must be exactly 'corp' or 'acro'")


def _part(part: str) -> None:
    if (
        not part or part in (".", "..") or part.endswith((" ", "."))
        or any(ord(char) < 32 or char in '<>:"|?*' for char in part)
        or _DEVICE.match(part)
    ):
        raise PackageError("unsafe or noncanonical path component")


def _relative(value: str) -> str:
    if type(value) is not str or "\\" in value or PureWindowsPath(value).drive:
        raise PackageError("resource paths must be canonical relative '/' paths")
    for part in value.split("/"):
        _part(part)
    return value


def _local_path(value: str | os.PathLike, label: str) -> Path:
    try:
        raw = os.fspath(value)
    except TypeError as exc:
        raise PackageError(f"{label} must be an explicit local path") from exc
    if not isinstance(raw, str) or not raw or raw != raw.strip():
        raise PackageError(f"{label} must be a nonempty unpadded path")
    windows = PureWindowsPath(raw)
    if os.name == "nt":
        if (
            windows.drive.startswith("\\\\")
            or bool(windows.drive) != bool(windows.root)
        ):
            raise PackageError(f"{label}: UNC, device and drive-relative paths are unsupported")
    elif "\\" in raw or windows.drive:
        raise PackageError(f"{label}: non-native path syntax is unsupported")
    path = Path(raw)
    suffix = raw[len(path.anchor):]
    if suffix:
        for part in suffix.replace("\\", "/").split("/"):
            _part(part)
    elif not path.anchor:
        raise PackageError(f"{label}: empty path")
    return path.absolute()


def _safe_stat(info: os.stat_result, label: str, *, directory: bool) -> None:
    if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & 0x400:
        raise PackageError(f"{label}: symlinks and reparse points are not allowed")
    if directory:
        if not stat.S_ISDIR(info.st_mode):
            raise PackageError(f"{label}: expected a directory")
    elif not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
        raise PackageError(f"{label}: expected a regular, non-hard-linked file")


def _existing(path: Path, label: str, *, directory: bool) -> os.stat_result:
    for ancestor in reversed((path, *path.parents)):
        try:
            info = ancestor.lstat()
        except OSError as exc:
            raise PackageError(f"{label}: missing or unreadable path ({type(exc).__name__})") from exc
        _safe_stat(info, label, directory=ancestor != path or directory)
    return info


def _stamp(info: os.stat_result) -> tuple:
    # Windows path/handle APIs can disagree on ctime without a content change.
    return info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns


def _read_resource(root: Path, relative: str) -> bytes:
    _relative(relative)
    path = root
    for part in relative.split("/"):
        _existing(path, relative, directory=True)
        try:
            names = os.listdir(path)
        except OSError as exc:
            raise PackageError(f"{relative}: unreadable resource directory") from exc
        if part not in names or sum(name.casefold() == part.casefold() for name in names) != 1:
            raise PackageError(f"{relative}: missing resource or noncanonical/ambiguous casing")
        path = path / part
    before = _existing(path, relative, directory=False)
    try:
        with path.open("rb") as stream:
            opened = os.fstat(stream.fileno())
            _safe_stat(opened, relative, directory=False)
            data = stream.read(MAX_RESOURCE_BYTES + 1)
            after_read = os.fstat(stream.fileno())
    except OSError as exc:
        raise PackageError(f"{relative}: unreadable resource") from exc
    after_path = _existing(path, relative, directory=False)
    if not (_stamp(before) == _stamp(opened) == _stamp(after_read) == _stamp(after_path)):
        raise PackageError(f"{relative}: resource changed during inspection")
    if not data or len(data) > MAX_RESOURCE_BYTES or len(data) != before.st_size:
        raise PackageError(f"{relative}: resource must contain 1..{MAX_RESOURCE_BYTES} bytes")
    return data


def _pairs(pairs: list) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise PackageError("duplicate JSON object key")
        result[key] = value
    return result


def _constant(value: str) -> None:
    raise PackageError(f"non-JSON numeric constant: {value}")


def _json(data: bytes, label: str) -> dict:
    try:
        result = json.loads(data.decode("utf-8"), object_pairs_hook=_pairs, parse_constant=_constant)
    except (ValueError, UnicodeError) as exc:
        raise PackageError(f"{label}: invalid JSON ({exc})") from exc
    if type(result) is not dict:
        raise PackageError(f"{label}: expected a JSON object")
    return result


def _nonempty_text(value: object, label: str) -> None:
    if type(value) is not str or not value.strip() or value != value.strip():
        raise PackageError(f"{label}: expected nonempty unpadded text")
    try:
        value.encode("utf-8")
    except UnicodeError as exc:
        raise PackageError(f"{label}: invalid Unicode") from exc


def _manifest(data: bytes, profile: str) -> dict:
    manifest = _json(data, "plugin.json")
    fields = {"name", "description", "version", "skills", "agents"}
    if profile == "acro":
        fields.add("engines")
    if set(manifest) != fields:
        raise PackageError("plugin.json: missing or unexpected fields for the selected profile")
    if manifest["name"] != NAME or manifest["version"] != VERSION:
        raise PackageError("plugin.json: expected sparkforge experimental version 0.1.0")
    _nonempty_text(manifest["description"], "plugin.json description")
    for key, expected in (("skills", _SKILLS), ("agents", _AGENTS)):
        declarations = manifest[key]
        if type(declarations) is not list:
            raise PackageError(f"plugin.json {key}: expected a resource list")
        for declaration in declarations:
            _relative(declaration)
        if declarations != expected:
            raise PackageError(f"plugin.json {key}: declarations must match the owned inventory exactly")
    if profile == "acro" and manifest["engines"] != ["copilot"]:
        raise PackageError("plugin.json: Acro engines must be exactly ['copilot']")
    return manifest


def _frontmatter(data: bytes, label: str) -> None:
    try:
        lines = data.decode("utf-8").splitlines()
        end = lines.index("---", 1)
    except (UnicodeError, ValueError) as exc:
        raise PackageError(f"{label}: missing minimal frontmatter") from exc
    if not lines or lines[0] != "---" or not any(line.strip() for line in lines[end + 1:]):
        raise PackageError(f"{label}: frontmatter and body are required")
    fields = {}
    for line in lines[1:end]:
        key, separator, value = line.partition(": ")
        if not separator or key in fields or key not in ("name", "description"):
            raise PackageError(f"{label}: only single-line name and description frontmatter is supported")
        _nonempty_text(value, f"{label} {key}")
        fields[key] = value
    if set(fields) != {"name", "description"} or fields["name"] != NAME:
        raise PackageError(f"{label}: frontmatter must identify the single sparkforge entry")


def _contents(payloads: dict[str, bytes], profile: str) -> dict:
    manifest = _manifest(payloads["plugin.json"], profile)
    if profile == "corp":
        agency = _json(payloads["agency.json"], "agency.json")
        if agency != {"engines": ["copilot"], "platforms": ["windows"]}:
            raise PackageError("agency.json: expected only copilot and windows declarations")
    for relative, data in payloads.items():
        try:
            text = data.decode("utf-8")
        except UnicodeError as exc:
            raise PackageError(f"{relative}: expected UTF-8 text") from exc
        if not text.strip():
            raise PackageError(f"{relative}: empty resource")
        if relative.endswith(".py"):
            try:
                compile(text, relative, "exec", dont_inherit=True)
            except (SyntaxError, ValueError) as exc:
                raise PackageError(f"{relative}: invalid Python syntax") from exc
    _frontmatter(payloads[_AGENTS[0]], _AGENTS[0])
    _frontmatter(payloads["skills/sparkforge/SKILL.md"], "skills/sparkforge/SKILL.md")
    return manifest


def _hash(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _canonical(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _formatted(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=True, indent=2) + "\n").encode("utf-8")


def _entries(payloads: dict[str, bytes]) -> list[dict]:
    return [
        {"path": path, "size_bytes": len(data), "sha256": _hash(data)}
        for path, data in sorted(payloads.items())
    ]


def _files(profile: str) -> tuple[str, ...]:
    return tuple(path for path in SOURCE_FILES if profile == "corp" or path != "agency.json")


def _directories(files: tuple[str, ...]) -> set[str]:
    result = set()
    for relative in files:
        parts = relative.split("/")[:-1]
        result.update("/".join(parts[:index]) for index in range(1, len(parts) + 1))
    return result


def _inventory_entries(value: object, expected: tuple[str, ...], label: str) -> None:
    if type(value) is not list or len(value) != len(expected):
        raise PackageError(f"{label}: incomplete or unexpected inventory")
    paths = []
    for entry in value:
        if type(entry) is not dict or set(entry) != {"path", "size_bytes", "sha256"}:
            raise PackageError(f"{label}: invalid file entry")
        paths.append(_relative(entry["path"]))
        if type(entry["size_bytes"]) is not int or not 1 <= entry["size_bytes"] <= MAX_RESOURCE_BYTES:
            raise PackageError(f"{label}: invalid byte size")
        if type(entry["sha256"]) is not str or not _DIGEST.fullmatch(entry["sha256"]):
            raise PackageError(f"{label}: invalid SHA-256")
    if paths != sorted(expected):
        raise PackageError(f"{label}: paths must match the sorted owned inventory exactly")


def _scan_package(root: Path, files: tuple[str, ...]) -> None:
    expected_files = set(files) | {INVENTORY_FILE}
    expected_dirs = _directories(files)
    seen_files, seen_dirs = set(), set()

    def visit(directory: Path, prefix: str = "") -> None:
        _existing(directory, "package directory", directory=True)
        try:
            children = list(directory.iterdir())
        except OSError as exc:
            raise PackageError("unreadable package directory") from exc
        for child in children:
            relative = f"{prefix}{child.name}"
            _relative(relative)
            try:
                info = child.lstat()
            except OSError as exc:
                raise PackageError("package changed during inspection") from exc
            is_directory = stat.S_ISDIR(info.st_mode)
            _safe_stat(info, relative, directory=is_directory)
            if is_directory:
                if relative not in expected_dirs:
                    raise PackageError(f"{relative}: undeclared package directory")
                seen_dirs.add(relative)
                visit(child, f"{relative}/")
            else:
                if relative not in expected_files:
                    raise PackageError(f"{relative}: undeclared package file")
                seen_files.add(relative)

    visit(root)
    if seen_files != expected_files or seen_dirs != expected_dirs:
        raise PackageError("package is missing required resources or directories")


def validate_package(package: str | os.PathLike, profile: str) -> dict:
    """Return a structural receipt, or raise PackageError. Never invokes a host."""
    _profile(profile)
    root = _local_path(package, "package")
    _existing(root, "package", directory=True)
    files = _files(profile)
    _scan_package(root, files)
    inventory = _json(_read_resource(root, INVENTORY_FILE), INVENTORY_FILE)
    expected = {
        "schema_version": "sparkforge.package.v1",
        "name": NAME,
        "version": VERSION,
        "profile": profile,
        "validation_scope": "STRUCTURAL_ONLY",
        "compatibility": "NOT_ASSESSED",
    }
    if set(inventory) != _INVENTORY_KEYS or any(inventory.get(key) != value for key, value in expected.items()):
        raise PackageError("inventory metadata does not match the selected experimental profile")
    _inventory_entries(inventory["files"], files, "files")
    _inventory_entries(inventory["source_files"], SOURCE_FILES, "source_files")
    for key in ("source_sha256", "source_manifest_sha256", "package_sha256"):
        if type(inventory[key]) is not str or not _DIGEST.fullmatch(inventory[key]):
            raise PackageError(f"inventory: invalid {key}")
    if inventory["source_sha256"] != _hash(_canonical(inventory["source_files"])):
        raise PackageError("source inventory digest mismatch")
    if inventory["package_sha256"] != _hash(_canonical({"profile": profile, "files": inventory["files"]})):
        raise PackageError("package inventory digest mismatch")

    payloads = {relative: _read_resource(root, relative) for relative in files}
    manifest = _contents(payloads, profile)
    if inventory["files"] != _entries(payloads):
        raise PackageError("package bytes do not match the digest inventory")
    source_entries = {entry["path"]: entry for entry in inventory["source_files"]}
    for entry in inventory["files"]:
        if entry["path"] == "plugin.json" and profile == "acro":
            continue
        if entry != source_entries[entry["path"]]:
            raise PackageError("untransformed resource differs from the recorded source")
    if profile == "acro":
        manifest = {key: value for key, value in manifest.items() if key != "engines"}
    if inventory["source_manifest_sha256"] != _hash(_canonical(manifest)):
        raise PackageError("profile manifest differs from the recorded source manifest")
    return {"valid": True, **inventory}


def build_package(profile: str, output: str | os.PathLike, source: str | os.PathLike | None = None) -> dict:
    """Export the canonical Corp source into a new local directory; no installs."""
    _profile(profile)
    if source is None:
        source = Path(__file__).absolute().parent.parent / "plugins" / NAME
    root = _local_path(source, "source")
    destination = _local_path(output, "output")
    _existing(root, "source", directory=True)
    _existing(destination.parent, "output parent", directory=True)
    try:
        physical_source = root.resolve(strict=True)
        physical_output = destination.parent.resolve(strict=True) / destination.name
    except OSError as exc:
        raise PackageError("cannot establish physical source/output locations") from exc
    if physical_source.is_relative_to(physical_output) or physical_output.is_relative_to(physical_source):
        raise PackageError("output and source must not overlap in either direction")
    if os.path.lexists(destination):
        raise PackageError("output already exists; choose a new directory")

    originals = {relative: _read_resource(root, relative) for relative in SOURCE_FILES}
    manifest = _contents(originals, "corp")
    payloads = {relative: originals[relative] for relative in _files(profile)}
    if profile == "acro":
        payloads["plugin.json"] = _formatted({**manifest, "engines": ["copilot"]})
    files = _entries(payloads)
    source_files = _entries(originals)
    inventory = {
        "schema_version": "sparkforge.package.v1",
        "name": NAME,
        "version": VERSION,
        "profile": profile,
        "validation_scope": "STRUCTURAL_ONLY",
        "compatibility": "NOT_ASSESSED",
        "files": files,
        "source_files": source_files,
        "source_sha256": _hash(_canonical(source_files)),
        "source_manifest_sha256": _hash(_canonical(manifest)),
        "package_sha256": _hash(_canonical({"profile": profile, "files": files})),
    }
    _existing(destination.parent, "output parent", directory=True)
    try:
        destination.mkdir()
    except OSError as exc:
        raise PackageError("could not exclusively create new output directory") from exc
    owner = _existing(destination, "output", directory=True)

    def check_owner() -> None:
        current = _existing(destination, "output", directory=True)
        if (owner.st_dev, owner.st_ino) != (current.st_dev, current.st_ino):
            raise PackageError("output directory changed during assembly")

    try:
        for relative in sorted(_directories(_files(profile)), key=lambda name: (name.count("/"), name)):
            check_owner()
            directory = destination.joinpath(*relative.split("/"))
            _existing(directory.parent, "output parent", directory=True)
            directory.mkdir()
        # Publish the inventory last; interrupted output is never silently reused.
        for relative, data in [*payloads.items(), (INVENTORY_FILE, _formatted(inventory))]:
            check_owner()
            target = destination.joinpath(*relative.split("/"))
            _existing(target.parent, "output parent", directory=True)
            with target.open("xb") as stream:
                stream.write(data)
    except OSError as exc:
        raise PackageError("assembly failed; partial output retained for operator inspection") from exc
    check_owner()
    return validate_package(destination, profile)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", required=True, choices=PROFILES)
    parser.add_argument("--output", required=True, help="new directory under an existing local parent")
    args = parser.parse_args(argv)
    try:
        result = build_package(args.profile, args.output)
    except PackageError as exc:
        print(json.dumps({
            "valid": False, "error": str(exc),
            "validation_scope": "STRUCTURAL_ONLY", "compatibility": "NOT_ASSESSED",
        }), file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
