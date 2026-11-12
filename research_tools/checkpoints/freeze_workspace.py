"""Freeze only explicitly selected local files and directories into a new checkpoint.

No implicit workspace, historical manifest, source archive, helper execution,
account or remote backup is selected. Inputs and outputs retain their source
restrictions; a checkpoint is not permission to publish its contents.
"""

import argparse
import hashlib
import json
import os
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from .._common import child, linked, read_bytes, read_json, root_path, safe_main
from . import verify_checkpoint


EXCLUDED_DIRECTORIES = {".git", "__pycache__", "_deps", "node_modules"}


def verifier():
    # Only this owned package is imported; never a script from an input checkpoint.
    return verify_checkpoint


def verifier_digest(stream, limit=verify_checkpoint.MAX_ARCHIVE_BYTES):
    return verify_checkpoint.digest(stream, limit)


def file_hash(path, limit=verify_checkpoint.MAX_ARCHIVE_BYTES):
    with path.open("rb") as stream:
        return verifier_digest(stream, limit)


def write_new_json(path, value):
    path = child(path.parent, path.name)
    if path.exists():
        raise ValueError("Refusing to overwrite a checkpoint artifact")
    try:
        with path.open("x", encoding="utf-8", newline="\n") as stream:
            json.dump(value, stream, indent=2, ensure_ascii=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
    except FileExistsError:
        raise ValueError("Refusing to overwrite a checkpoint artifact") from None


def category(relative, categories):
    matches = [prefix for prefix in categories if relative == prefix or relative.startswith(prefix.rstrip("/") + "/")]
    return categories[max(matches, key=len)] if matches else "selected_source"


def select_files(workspace, selection, previous=None, *, max_files=verify_checkpoint.MAX_FILES, max_bytes=verify_checkpoint.MAX_ARCHIVE_BYTES):
    workspace = root_path(workspace)
    selected, changed = {}, []
    allowed_changes = set(selection.get("expected_working_updates", []))
    if previous:
        for record in previous["files"]:
            relative = record["path"]
            path = verify_checkpoint.safe_path(workspace, relative)
            if not path.is_file():
                raise ValueError("Previously preserved file is missing")
            if file_hash(path, max_bytes) != record["sha256"]:
                if relative not in allowed_changes:
                    raise ValueError("Unexpected change to the previous baseline")
                changed.append(relative)
            selected[relative] = path
    for relative in selection.get("files", []):
        path = verify_checkpoint.safe_path(workspace, relative)
        if not path.is_file():
            raise ValueError("Explicitly selected file is missing")
        selected[relative] = path
    for relative in selection.get("directories", []):
        directory = verify_checkpoint.safe_path(workspace, relative)
        if not directory.is_dir() or directory.name in EXCLUDED_DIRECTORIES:
            raise ValueError("Unsupported selected directory")
        for current, directories, files in os.walk(directory, followlinks=False):
            directories[:] = sorted(name for name in directories if name not in EXCLUDED_DIRECTORIES)
            for name in directories:
                if linked(Path(current) / name):
                    raise ValueError("Linked source directory is not followed")
            for name in sorted(files):
                path = Path(current) / name
                if path.suffix in {".pyc", ".pyo"}:
                    continue
                if name.endswith((".partial", ".tmp")) or name.startswith(".writing-"):
                    raise ValueError("Unsettled source artifact")
                key = path.relative_to(workspace).as_posix()
                selected[key] = verify_checkpoint.safe_path(workspace, key)
                if len(selected) > max_files:
                    raise ValueError("Selected file-count bound exceeded")
    if not selected or len(selected) > max_files:
        raise ValueError("Empty or oversized explicit selection")
    if len({name.casefold() for name in selected}) != len(selected):
        raise ValueError("Case-colliding selected files")
    if sum(path.stat().st_size for path in selected.values()) > max_bytes:
        raise ValueError("Selected byte bound exceeded")
    for name in selected:
        if set(name.split("/")) & EXCLUDED_DIRECTORIES:
            raise ValueError("Dependency caches and Git stores are excluded")
    return dict(sorted(selected.items())), sorted(changed)


def freeze(workspace, output, checkpoint_id, selection, *, previous_root=None, max_files=verify_checkpoint.MAX_FILES, max_bytes=verify_checkpoint.MAX_ARCHIVE_BYTES):
    workspace, output = root_path(workspace), root_path(output, must_exist=False)
    if not re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9_.-]{0,100}", checkpoint_id):
        raise ValueError("Invalid checkpoint identifier")
    if selection["schema_version"] != 1 or max_files < 1 or max_bytes < 1:
        raise ValueError("Unsupported checkpoint selection or bounds")
    if output.exists() or workspace.is_relative_to(output):
        raise ValueError("Checkpoint output must be new and cannot contain its input workspace")
    previous, prior_result = None, None
    if previous_root is not None:
        previous_root = root_path(previous_root)
        previous = read_json(child(previous_root, "manifest.json"))
        prior_result = verify_checkpoint.verify(previous, previous_root, max_files=max_files, max_bytes=max_bytes)
    for receipt in selection.get("required_receipts", []):
        path = verify_checkpoint.safe_path(workspace, receipt["path"])
        if file_hash(path, max_bytes) != receipt["sha256"]:
            raise ValueError("Required receipt digest differs")
        document = read_json(path)
        if document.get(receipt.get("status_key", "status")) != receipt.get("expected_status", "PASS"):
            raise ValueError("Required receipt does not have the selected status")
        for relative, expected in receipt.get("source_sha256", {}).items():
            if file_hash(verify_checkpoint.safe_path(workspace, relative), max_bytes) != expected:
                raise ValueError("Required receipt source binding is stale")
    selected, changed = select_files(workspace, selection, previous, max_files=max_files, max_bytes=max_bytes)
    if any(path.is_relative_to(output) for path in selected.values()):
        raise ValueError("Checkpoint output must not be in the selected input set")
    categories = selection.get("categories", {})
    for relative, label in categories.items():
        verify_checkpoint.safe_path(workspace, relative)
        if not isinstance(label, str) or not label:
            raise ValueError("Invalid explicit category")
    output.mkdir(parents=True, exist_ok=False)
    pending = child(output, ".snapshot.partial")
    records = []
    with pending.open("xb") as stream:
        with ZipFile(stream, "w", compression=ZIP_DEFLATED, compresslevel=6) as archive:
            total = 0
            for relative, path in selected.items():
                data = read_bytes(path, limit=max_bytes)
                total += len(data)
                if total > max_bytes:
                    raise ValueError("Source changed beyond the selected byte bound")
                records.append({
                    "path": relative, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest(),
                    "category": category(relative, categories),
                })
                archive.writestr(relative, data)
        stream.flush()
        os.fsync(stream.fileno())
    manifest = {
        "schema_version": 1, "checkpoint_id": checkpoint_id, "state": "FROZEN_VERIFIED",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "handling": "Operator-selected local storage; source restrictions remain; no publication authorization.",
        "workspace_resolution": "Explicit --workspace only; no path inference.",
        "archive": {"file": ".snapshot.partial", "bytes": pending.stat().st_size, "sha256": file_hash(pending, max_bytes), "format": "ZIP_DEFLATED"},
        "counts": {
            "files": len(records), "bytes": sum(row["bytes"] for row in records),
            "categories": dict(sorted(Counter(row["category"] for row in records).items())),
        },
        "required_receipts_checked": len(selection.get("required_receipts", [])),
        "previous_checkpoint": None if not previous else {
            "id": previous["checkpoint_id"], "archive_sha256": previous["archive"]["sha256"],
            "archive_automatically_included": False, "verification": prior_result,
            "intentional_working_updates": changed,
        },
        "known_limits": [
            "Selected artifacts only; not an atomic filesystem or machine backup.",
            "Sources are reread before sealing; later working edits do not alter the frozen archive.",
            "Hash equality does not establish rights, encryption, external authenticity or remote synchronization.",
            "No source code, checkpoint-local helper, installer, model or power command was executed.",
        ],
        "publication_authorized": False, "files": records,
    }
    result = verify_checkpoint.verify(manifest, output, workspace, True, max_files=max_files, max_bytes=max_bytes)
    if result["status"] != "PASS":
        raise ValueError("Working files changed during the freeze; preserve the partial output")
    pending.rename(child(output, "snapshot.zip"))
    manifest["archive"]["file"] = "snapshot.zip"
    write_new_json(child(output, "manifest.json"), manifest)
    result["verified_at_utc"] = datetime.now(timezone.utc).isoformat()
    write_new_json(child(output, "verification.json"), result)
    return {
        "status": "FROZEN_VERIFIED", "files": len(records), "bytes": manifest["counts"]["bytes"],
        "previous_working_updates": len(changed), "publication_authorized": False, "network_requests": 0,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", required=True)
    parser.add_argument("--output", required=True, help="New local checkpoint directory; no existing output is adopted.")
    parser.add_argument("--checkpoint-id", required=True)
    parser.add_argument("--selection", required=True, help="Explicit file/directory/receipt selection JSON.")
    parser.add_argument("--previous-root", help="Optional explicitly selected previous checkpoint; never inferred or auto-included.")
    parser.add_argument("--max-files", type=int, default=verify_checkpoint.MAX_FILES)
    parser.add_argument("--max-bytes", type=int, default=verify_checkpoint.MAX_ARCHIVE_BYTES)
    args = parser.parse_args(argv)
    output = root_path(args.output, must_exist=False)
    if output.is_relative_to(Path(__file__).resolve().parents[2]):
        raise ValueError("Runtime checkpoints must be outside the publication code repository")
    return freeze(
        args.workspace, output, args.checkpoint_id, read_json(Path(args.selection)),
        previous_root=args.previous_root, max_files=args.max_files, max_bytes=args.max_bytes,
    )


if __name__ == "__main__":
    safe_main(main)
