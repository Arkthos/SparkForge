"""Verify an explicitly selected sealed checkpoint, without extracting any entry.

Consolidates the two historical authored verifiers. Archive checks do not read
working files unless --working and --workspace are explicitly selected.
"""

import argparse
import hashlib
import re
import stat
from zipfile import BadZipFile, ZipFile

from .._common import child, read_json, root_path, safe_main


MAX_ARCHIVE_BYTES = 512 * 1024 * 1024
MAX_FILES = 10000


def digest(stream, limit=MAX_ARCHIVE_BYTES):
    result, length = hashlib.sha256(), 0
    while block := stream.read(min(1024 * 1024, limit - length + 1)):
        length += len(block)
        if length > limit:
            raise ValueError("Checkpoint byte bound exceeded")
        result.update(block)
    return result.hexdigest()


def safe_path(root, relative):
    if not isinstance(relative, str) or "\\" in relative:
        raise ValueError("Invalid manifest path")
    return child(root, relative)


def verify(manifest, checkpoint, workspace=None, working=False, *, max_bytes=MAX_ARCHIVE_BYTES, max_files=MAX_FILES):
    checkpoint = root_path(checkpoint)
    if working and workspace is None:
        raise ValueError("Working comparison requires an explicit workspace")
    if workspace is not None:
        workspace = root_path(workspace)
    if max_bytes < 1 or max_files < 1:
        raise ValueError("Invalid checkpoint bounds")
    if manifest["schema_version"] != 1 or manifest["state"] != "FROZEN_VERIFIED":
        raise ValueError("Unsupported or unsealed checkpoint")
    records = manifest["files"]
    if not records or len(records) > max_files:
        raise ValueError("Empty or oversized file inventory")
    expected = {record["path"]: record for record in records}
    if len(expected) != len(records):
        raise ValueError("Empty or duplicated file inventory")
    if len({path.casefold() for path in expected}) != len(expected):
        raise ValueError("Case-colliding archive paths")
    if manifest["counts"]["files"] != len(records):
        raise ValueError("File count does not reconcile")
    total = 0
    for relative, record in expected.items():
        safe_path(workspace if working else checkpoint, relative)
        if type(record["bytes"]) is not int or record["bytes"] < 0:
            raise ValueError("Invalid recorded size")
        total += record["bytes"]
        if total > max_bytes:
            raise ValueError("Uncompressed checkpoint byte bound exceeded")
        if not re.fullmatch(r"[a-f0-9]{64}", record["sha256"]):
            raise ValueError("Invalid recorded digest")
    if manifest["counts"]["bytes"] != total:
        raise ValueError("Byte count does not reconcile")
    archive_record = manifest["archive"]
    archive = safe_path(checkpoint, archive_record["file"])
    if not archive.is_file() or archive.stat().st_size != archive_record["bytes"]:
        raise ValueError("Snapshot archive is missing or its size differs")
    if type(archive_record["bytes"]) is not int or archive_record["bytes"] > max_bytes:
        raise ValueError("Archive byte bound exceeded")
    with archive.open("rb") as stream:
        if digest(stream, max_bytes) != archive_record["sha256"]:
            raise ValueError("Snapshot archive SHA-256 differs")
    with ZipFile(archive, "r") as bundle:
        entries = bundle.infolist()
        if len(entries) != len(expected) or {entry.filename for entry in entries} != set(expected):
            raise ValueError("Archive entries do not match the manifest")
        for entry in entries:
            record = expected[entry.filename]
            mode = entry.external_attr >> 16
            if entry.is_dir() or stat.S_ISLNK(mode) or entry.flag_bits & 1 or entry.file_size != record["bytes"]:
                raise ValueError("Archive entry size/type differs")
            with bundle.open(entry, "r") as stream:
                if digest(stream, record["bytes"]) != record["sha256"]:
                    raise ValueError("Archive entry digest differs")
    differences = []
    if working:
        for relative, record in expected.items():
            path = safe_path(workspace, relative)
            if not path.is_file():
                differences.append({"path": relative, "reason": "missing"})
            elif path.stat().st_size != record["bytes"]:
                differences.append({"path": relative, "reason": "size_changed"})
            else:
                with path.open("rb") as stream:
                    if digest(stream, record["bytes"]) != record["sha256"]:
                        differences.append({"path": relative, "reason": "content_changed"})
    return {
        "status": "FAIL" if differences else "PASS", "checkpoint": manifest["checkpoint_id"],
        "archive_sha256": archive_record["sha256"], "archive_files_verified": len(expected),
        "working_files_checked": len(expected) if working else 0,
        "working_comparison_scope": "Recorded files only; newly added files are not rejected.",
        "differences": differences, "network_requests": 0, "files_modified": 0,
        "publication_authorized": False,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkpoint", required=True)
    parser.add_argument("--workspace")
    parser.add_argument("--working", action="store_true")
    parser.add_argument("--max-bytes", type=int, default=MAX_ARCHIVE_BYTES)
    parser.add_argument("--max-files", type=int, default=MAX_FILES)
    args = parser.parse_args(argv)
    if args.working and not args.workspace:
        parser.error("--working requires --workspace")
    checkpoint = root_path(args.checkpoint)
    return verify(
        read_json(child(checkpoint, "manifest.json")), checkpoint, args.workspace, args.working,
        max_bytes=args.max_bytes, max_files=args.max_files,
    )


if __name__ == "__main__":
    try:
        safe_main(main)
    except BadZipFile:
        print('{"status":"FAIL","error_type":"INVALID_CHECKPOINT_ARCHIVE"}')
        raise SystemExit(1) from None
