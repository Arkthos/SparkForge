"""Capture selected pinned public GitHub files without executing acquired code.

Network reads require --allow-network and an explicitly named token environment
variable. The command never logs in, changes accounts, clones or installs code.
"""

import argparse
import base64
import hashlib
import json
import os
import re
import subprocess
from datetime import datetime, timezone
from urllib.parse import quote

from .._common import child, read_bytes, read_json, root_path, safe_main, write_json, atomic_bytes


MAX_FILE_BYTES = 1_000_000


def api(endpoint, *, token_env, allow_network):
    if not allow_network:
        raise ValueError("Network access was not explicitly selected")
    if not re.fullmatch(r"repos/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+(?:/[^ \r\n]*)?", endpoint):
        raise ValueError("Only repository API paths are supported")
    token = os.environ.get(token_env, "") if token_env else ""
    if not token or "\r" in token or "\n" in token:
        raise ValueError("The explicitly selected token variable is unavailable")
    environment = dict(os.environ)
    environment["GH_TOKEN"] = token
    environment["GH_HOST"] = "github.com"
    environment["GH_PROMPT_DISABLED"] = "1"
    try:
        result = subprocess.run(
            ["gh", "api", "--hostname", "github.com", "--method", "GET", endpoint],
            check=True, capture_output=True, text=True, encoding="utf-8",
            timeout=90, env=environment,
        )
    except subprocess.CalledProcessError as error:
        status = re.search(r"HTTP \d{3}", error.stderr or "")
        raise RuntimeError("GitHub read failed" + (": " + status[0] if status else "")) from None
    return json.loads(result.stdout)


def capture_file(root, directory, metadata, document, request):
    if document["type"] != "file":
        raise ValueError("Requested source is not a regular file")
    if document["size"] > MAX_FILE_BYTES:
        raise ValueError("Source exceeds the research size bound")
    if document.get("encoding") != "base64":
        document = request(f"repos/{metadata['repository']}/git/blobs/{document['sha']}") | {
            "path": document["path"], "html_url": document.get("html_url"),
        }
    content = "".join(document["content"].split())
    if len(content) > 4 * ((MAX_FILE_BYTES + 2) // 3):
        raise ValueError("Encoded source exceeds the research size bound")
    data = base64.b64decode(content, validate=True)
    if len(data) > MAX_FILE_BYTES:
        raise ValueError("Decoded source exceeds the research size bound")
    blob_id = hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()
    if blob_id != document["sha"]:
        raise ValueError("Git blob identity mismatch")
    text = data.decode("utf-8")
    source_path = document["path"]
    child(root, source_path)
    name = hashlib.sha256(source_path.encode("utf-8")).hexdigest() + ".txt"
    target = child(directory, "files/" + name)
    if target.exists() and read_bytes(target) != data:
        raise ValueError("Pinned source cache changed")
    atomic_bytes(root, target, data)
    index_path = child(directory, "files.json")
    index = read_json(index_path) if index_path.exists() else {}
    record = {
        "path": source_path, "commit": metadata["commit"], "git_blob": blob_id,
        "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data),
        "lines": len(text.splitlines()), "local_file": target.relative_to(root).as_posix(),
        "source_url": (
            f"https://github.com/{metadata['repository']}/blob/"
            f"{metadata['commit']}/{quote(source_path, safe='/')}"
        ),
        "is_lfs_pointer": text.startswith("version https://git-lfs.github.com/spec/v1"),
    }
    index[source_path] = record
    write_json(root, index_path, index)
    return record


def contents(metadata, path, request):
    if path:
        parts = path.replace("\\", "/").split("/")
        if any(part in {"", ".", ".."} for part in parts) or path.startswith("/"):
            raise ValueError("Use a repository-relative source path")
    encoded = quote(path, safe="/")
    return request(f"repos/{metadata['repository']}/contents/{encoded}?ref={metadata['commit']}")


def snapshot(root, requested, directory, request):
    repository = request(f"repos/{requested}")
    if repository.get("private") or repository.get("visibility") != "public":
        raise ValueError("Public-source study refuses a non-public repository")
    canonical = repository["full_name"]
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", canonical):
        raise ValueError("Invalid canonical repository identity")
    existing = child(directory, "metadata.json")
    if existing.exists():
        metadata = read_json(existing)
        if (
            metadata["requested_repository"].casefold() != requested.casefold()
            or metadata["repository"].casefold() != canonical.casefold()
            or metadata["visibility"] != "public"
            or not re.fullmatch(r"[0-9a-f]{40}", metadata["commit"])
        ):
            raise ValueError("Existing snapshot identity does not match the request")
    else:
        branch = repository["default_branch"]
        head = request(f"repos/{canonical}/commits/{quote(branch, safe='')}")
        if not re.fullmatch(r"[0-9a-f]{40}", head["sha"]):
            raise ValueError("Invalid immutable source revision")
        metadata = {
            "requested_repository": requested, "repository": canonical,
            "url": f"https://github.com/{canonical}", "description": repository.get("description"),
            "visibility": "public", "default_branch": branch, "commit": head["sha"],
            "tree": head["commit"]["tree"]["sha"],
            "commit_date": head["commit"]["committer"]["date"],
            "observed_at_utc": datetime.now(timezone.utc).isoformat(),
            "pushed_at": repository.get("pushed_at"), "created_at": repository.get("created_at"),
            "archived": repository["archived"], "disabled": repository["disabled"],
            "fork": repository["fork"], "stars_observed": repository["stargazers_count"],
            "license_spdx_detected": (repository.get("license") or {}).get("spdx_id"),
            "license_detection_is_not_legal_clearance": True,
            "read_scope": "Selected files; a root listing is not a whole-tree audit.",
            "execution": "No source code, hooks, installers or models executed.",
        }
        write_json(root, existing, metadata)
    root_entries = contents(metadata, "", request)
    if not isinstance(root_entries, list):
        raise ValueError("Expected a root directory listing")
    write_json(root, child(directory, "root.json"), [
        {key: entry.get(key) for key in ("name", "path", "type", "size", "sha", "html_url")}
        for entry in root_entries
    ])
    for entry in root_entries:
        if entry["type"] == "file" and (
            entry["name"].lower() in {"readme.md", "readme.rst", "readme"}
            or re.fullmatch(r"(license|licence|copying)(\.(md|txt|rst))?", entry["name"], re.I)
        ):
            capture_file(root, directory, metadata, contents(metadata, entry["path"], request), request)
    index = child(directory, "files.json")
    if not index.exists():
        write_json(root, index, {})
    return metadata


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=["snapshot", "files", "list"])
    parser.add_argument("repository")
    parser.add_argument("paths", nargs="*")
    parser.add_argument("--output", required=True, help="Explicit local capture root.")
    parser.add_argument("--token-env", required=True, help="Name, never value, of the selected GitHub token variable.")
    parser.add_argument("--allow-network", action="store_true")
    args = parser.parse_args(argv)
    if not args.allow_network:
        parser.error("--allow-network is required; no collection was attempted")
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", args.repository):
        parser.error("use an owner/repository identifier")
    if args.mode in {"files", "list"} and not args.paths:
        parser.error("this mode needs at least one source path")
    root = root_path(args.output, must_exist=False)
    directory = child(root, "sources/" + args.repository.replace("/", "--"))

    def request(endpoint):
        return api(endpoint, token_env=args.token_env, allow_network=args.allow_network)

    metadata = snapshot(root, args.repository, directory, request)
    captures = listings = 0
    for path in args.paths:
        document = contents(metadata, path, request)
        if args.mode == "list":
            if not isinstance(document, list):
                raise ValueError("Requested source is not a directory")
            entries = [
                {key: entry.get(key) for key in ("name", "path", "type", "size", "sha")}
                for entry in document
            ]
            name = hashlib.sha256(path.encode("utf-8")).hexdigest() + ".json"
            write_json(root, child(directory, "listings/" + name), entries)
            listings += 1
        else:
            capture_file(root, directory, metadata, document, request)
            captures += 1
    return {"status": "CAPTURED", "selected_files": captures, "directory_listings": listings}


if __name__ == "__main__":
    try:
        safe_main(main)
    except (RuntimeError, subprocess.SubprocessError):
        print(json.dumps({"status": "FAIL", "error_type": "GITHUB_READ_FAILED"}))
        raise SystemExit(1) from None
