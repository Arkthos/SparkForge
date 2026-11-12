"""Small local I/O helpers shared by the portable research commands."""

from __future__ import annotations

import hashlib
import json
import os
import re
from pathlib import Path
from uuid import uuid4


MAX_BYTES = 64 * 1024 * 1024


def linked(path):
    return path.is_symlink() or getattr(path, "is_junction", lambda: False)()


def root_path(value, *, must_exist=True):
    if value is None:
        raise ValueError("An explicit root is required")
    path = Path(value).absolute()
    for component in (path, *path.parents):
        if linked(component):
            raise ValueError("Linked roots are not supported")
    if must_exist and not path.is_dir():
        raise ValueError("The selected root must be an existing directory")
    return path.resolve()


def child(root, relative):
    root = root_path(root, must_exist=False)
    if not isinstance(relative, str) or not relative or "\0" in relative:
        raise ValueError("Invalid relative path")
    parts = relative.replace("\\", "/").split("/")
    for part in parts:
        if (
            part in {"", ".", ".."}
            or re.search(r'[<>:"|?*]', part)
            or part.rstrip(" .") != part
            or re.fullmatch(r"(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(?:\..*)?", part, re.I)
        ):
            raise ValueError("Unsafe relative path")
    path = root
    for part in parts:
        path = path / part
        if linked(path):
            raise ValueError("Linked local paths are not supported")
    if not path.resolve().is_relative_to(root):
        raise ValueError("Local path leaves the selected root")
    return path


def inside(root, path):
    root = root_path(root, must_exist=False)
    path = Path(path).absolute()
    try:
        relative = path.relative_to(root).as_posix()
    except ValueError:
        raise ValueError("Local path leaves the selected root") from None
    return child(root, relative)


def read_bytes(path, *, limit=MAX_BYTES):
    if not isinstance(limit, int) or limit < 1:
        raise ValueError("Invalid byte limit")
    if linked(Path(path)):
        raise ValueError("Linked files are not supported")
    with Path(path).open("rb") as stream:
        data = stream.read(limit + 1)
    if len(data) > limit:
        raise ValueError("Local file exceeds the explicit byte bound")
    return data


def read_json(path):
    return json.loads(read_bytes(path).decode("utf-8-sig"))


def atomic_bytes(root, path, value):
    path = inside(root, path)
    path.parent.mkdir(parents=True, exist_ok=True)
    pending = child(path.parent, ".writing-" + uuid4().hex)
    created = False
    try:
        with pending.open("xb") as stream:
            created = True
            stream.write(value)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(pending, path)
    finally:
        if created and pending.exists():
            pending.unlink()


def write_json(root, path, value):
    atomic_bytes(root, path, (json.dumps(value, indent=2, ensure_ascii=True) + "\n").encode())


def write_text(root, path, value):
    atomic_bytes(root, path, value.encode("utf-8"))


def verified_bytes(root, record, *, path_key="local_path", limit=MAX_BYTES):
    data = read_bytes(child(root, record[path_key]), limit=limit)
    if len(data) != record["bytes"] or hashlib.sha256(data).hexdigest() != record["sha256"]:
        raise ValueError("Recorded source byte/hash mismatch")
    if record.get("source_blob_id"):
        actual = hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()
        if actual != record["source_blob_id"]:
            raise ValueError("Recorded Git blob mismatch")
    return data


def unique_records(records, key):
    result = {}
    for record in records:
        value = record[key]
        if value in result:
            raise ValueError("Duplicate source record")
        result[value] = record
    return result


def safe_main(main):
    try:
        result = main()
    except (OSError, ValueError, KeyError, TypeError, UnicodeError) as error:
        # Source-bearing exception messages must not be printed by a CLI.
        print(json.dumps({"status": "FAIL", "error_type": type(error).__name__}))
        raise SystemExit(1) from None
    if isinstance(result, dict):
        print(json.dumps(result, indent=2))
        if result.get("result", result.get("status")) == "FAIL":
            raise SystemExit(1)
