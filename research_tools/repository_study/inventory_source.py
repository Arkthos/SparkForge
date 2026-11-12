"""Inventory pinned local Git objects; never clone, checkout or execute source.

Source identities, object store and destination are explicit. Symlinks,
submodules, LFS pointers and unsupported filenames retain separate dispositions.
"""

import argparse
import csv
import hashlib
import io
import os
import re
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import PurePosixPath
from urllib.parse import quote, urlsplit

from .._common import (
    MAX_BYTES, atomic_bytes, child, read_bytes, read_json, root_path, safe_main,
    unique_records, write_json, write_text,
)


def git(git_dir, *args, input=None):
    git_dir = root_path(git_dir)
    if (git_dir / "objects" / "info" / "alternates").exists() or (git_dir / "commondir").exists():
        raise ValueError("Select a self-contained object store, without alternate directories")
    environment = dict(os.environ)
    environment.update(
        GIT_NO_LAZY_FETCH="1", GIT_TERMINAL_PROMPT="0", GIT_OPTIONAL_LOCKS="0",
        GIT_ALTERNATE_OBJECT_DIRECTORIES="",
    )
    return subprocess.run(
        ["git", "--no-replace-objects", f"--git-dir={git_dir}", *args],
        input=input, check=True, capture_output=True, env=environment, timeout=120,
    ).stdout


def safe_parts(path):
    parts = path.split("/")
    if not parts or PurePosixPath(path).is_absolute():
        return None
    for part in parts:
        if part in {"", ".", "..", ".git"} or re.search(r'[<>:"|?*\\]', part):
            return None
        if part.rstrip(" .") != part:
            return None
        if re.fullmatch(r"(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(?:\..*)?", part, re.I):
            return None
    return tuple(parts)


def surface(path):
    parts = PurePosixPath(path).parts
    if parts[0] == "plugins" and len(parts) > 1:
        return f"plugin:{parts[1]}"
    if parts[0] == ".github":
        return "repository-governance-and-distribution"
    return "root-documentation-and-configuration"


def tree_entries(raw, repository_url, commit):
    entries = []
    for record in raw.split(b"\0"):
        if not record:
            continue
        metadata, raw_path = record.split(b"\t", 1)
        mode, kind, oid, size = metadata.decode("ascii").split()
        if not re.fullmatch(r"[0-9a-f]{40}", oid) or kind not in {"blob", "tree", "commit"}:
            raise ValueError("Unexpected Git tree metadata")
        path = raw_path.decode("utf-8")
        entries.append({
            "path": path, "mode": mode, "git_type": kind, "git_object": oid,
            "size_bytes": None if size == "-" else int(size), "surface": surface(path),
            "extension": PurePosixPath(path).suffix.lower(),
            "content_kind": "tree" if kind == "tree" else "not_read",
            "line_count": None, "sha256": None, "materialization": "not_applicable",
            "baseline_depth": "inventoried",
            "source_url": (
                f"{repository_url}/blob/{commit}/{quote(path, safe='/')}" if kind == "blob" else None
            ),
        })
    unique_records(entries, "path")
    return entries


def inventory(root, git_dir, commit, tree, repository_url, *, max_bytes=MAX_BYTES):
    root, git_dir = root_path(root, must_exist=False), root_path(git_dir)
    if root.is_relative_to(git_dir):
        raise ValueError("Output must not be inside the selected Git object store")
    if not all(re.fullmatch(r"[0-9a-f]{40}", value) for value in (commit, tree)):
        raise ValueError("Select full immutable SHA-1 commit and tree IDs")
    url = urlsplit(repository_url)
    if url.scheme != "https" or not url.netloc or url.username or url.password or url.query or url.fragment:
        raise ValueError("Select a credential-free repository HTTPS URL")
    repository_url = repository_url.rstrip("/")
    if git(git_dir, "rev-parse", f"{commit}^{{tree}}").decode().strip() != tree:
        raise ValueError("Unexpected pinned tree")
    entries = tree_entries(
        git(git_dir, "ls-tree", "-r", "-t", "-z", "--long", commit), repository_url, commit,
    )
    blobs = [entry for entry in entries if entry["git_type"] == "blob"]
    if max_bytes < 1 or sum(entry["size_bytes"] for entry in blobs) > max_bytes:
        raise ValueError("Selected blobs exceed the explicit total byte bound")
    batch = git(
        git_dir, "cat-file", "--batch",
        input="".join(entry["git_object"] + "\n" for entry in blobs).encode(),
    )
    stream = io.BytesIO(batch)
    materialized = set()
    for entry in blobs:
        oid, kind, size = stream.readline().decode("ascii").strip().split()
        size = int(size)
        if size != entry["size_bytes"] or size < 0:
            raise ValueError("Git object size differs from tree metadata")
        data = stream.read(size)
        if (
            len(data) != size or stream.read(1) != b"\n"
            or oid != entry["git_object"] or kind != "blob"
        ):
            raise ValueError("Invalid Git object batch")
        if hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest() != oid:
            raise ValueError("Object integrity failure")
        entry["sha256"] = hashlib.sha256(data).hexdigest()
        if entry["mode"] == "120000":
            entry.update(content_kind="symlink_target", materialization="not_followed")
            continue
        try:
            text = data.decode("utf-8-sig")
        except UnicodeDecodeError:
            entry["content_kind"] = "binary_or_non_utf8"
        else:
            entry["content_kind"] = "binary_or_non_utf8" if "\0" in text else "utf8_text"
            if "\0" not in text:
                entry["line_count"] = len(text.splitlines())
            if data.startswith(b"version https://git-lfs.github.com/spec/v1"):
                entry["content_kind"] = "git_lfs_pointer"
        if safe_parts(entry["path"]) is None:
            entry["materialization"] = "unsupported_windows_path"
            continue
        folded = entry["path"].casefold()
        if folded in materialized:
            raise ValueError("Case-insensitive output collision")
        materialized.add(folded)
        target = child(root, "source/" + entry["path"])
        if target.exists() and read_bytes(target, limit=max_bytes) != data:
            raise ValueError("Refusing to overwrite changed source")
        if not target.exists():
            atomic_bytes(root, target, data)
        entry["materialization"] = "exact_blob_bytes"
    if stream.read():
        raise ValueError("Unexpected trailing bytes in Git object batch")
    for entry in entries:
        if entry["mode"] == "160000":
            entry.update(content_kind="submodule_gitlink", materialization="not_fetched")
    leaves = [entry for entry in entries if entry["git_type"] != "tree"]
    summary = {
        "schema_version": 1, "repository_url": repository_url, "commit": commit, "tree": tree,
        "branch_observed": "NOT_ASSESSED", "observed_visibility": "NOT_ASSESSED",
        "collected_at_utc": datetime.now(timezone.utc).isoformat(), "snapshot_root": "source",
        "acquisition": "Explicit local object reads; no checkout, hooks, filters, submodules or LFS download.",
        "tracked_leaf_count": len(leaves), "directory_count": len(entries) - len(leaves),
        "blob_bytes": sum(entry["size_bytes"] for entry in blobs),
        **{
            name: dict(sorted(Counter(entry[field] for entry in leaves).items()))
            for name, field in (
                ("content_kinds", "content_kind"), ("surfaces", "surface"),
                ("extensions", "extension"), ("materialization", "materialization"),
            )
        },
        "breadth_claim": "Every returned pinned local tree entry is inventoried; every blob hash is verified.",
        "depth_claim": "Structural metadata only; no semantic review or runtime validation.",
        "network_requests": 0,
    }
    write_json(root, child(root, "evidence/inventory.json"), {"snapshot": summary, "entries": entries})
    write_json(root, child(root, "evidence/snapshot.json"), summary)
    csv_text = io.StringIO(newline="")
    columns = list(entries[0]) if entries else ["path", "git_type", "git_object"]
    writer = csv.DictWriter(csv_text, fieldnames=columns)
    writer.writeheader()
    writer.writerows(entries)
    write_text(root, child(root, "evidence/inventory.csv"), csv_text.getvalue())
    return {"status": "INVENTORIED", "files": len(leaves), "network_requests": 0}


def load_inventory(root):
    root = root_path(root)
    document = read_json(child(root, "evidence/inventory.json"))
    source = child(root, document["snapshot"]["snapshot_root"])
    entries = unique_records(document["entries"], "path")
    return document, source, entries


def source_bytes(source, entry):
    if entry["materialization"] != "exact_blob_bytes":
        raise ValueError("Source was not materialized as an ordinary file")
    data = read_bytes(child(source, entry["path"]))
    if len(data) != entry["size_bytes"] or hashlib.sha256(data).hexdigest() != entry["sha256"]:
        raise ValueError("Source byte/hash mismatch")
    if hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest() != entry["git_object"]:
        raise ValueError("Source Git blob mismatch")
    return data


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, help="Explicit local output corpus root.")
    parser.add_argument("--git-dir", required=True, help="Existing self-contained local object store; never fetched.")
    parser.add_argument("--commit", required=True)
    parser.add_argument("--tree", required=True)
    parser.add_argument("--repository-url", required=True)
    parser.add_argument("--max-bytes", type=int, default=MAX_BYTES, help="Maximum total selected blob bytes.")
    args = parser.parse_args(argv)
    return inventory(args.root, args.git_dir, args.commit, args.tree, args.repository_url, max_bytes=args.max_bytes)


if __name__ == "__main__":
    try:
        safe_main(main)
    except subprocess.SubprocessError:
        print('{"status":"FAIL","error_type":"LOCAL_GIT_READ_FAILED"}')
        raise SystemExit(1) from None
