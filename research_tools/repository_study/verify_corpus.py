"""Verify a selected local source study without running its business code.

This command is read-only unless --receipt is selected. Optional comparison
roots and recorded-check expectations must be supplied, never inferred.
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
from urllib.parse import unquote, urlsplit

from .._common import child, read_bytes, read_json, root_path, safe_main, unique_records, write_json
from .inventory_source import git, load_inventory, source_bytes, tree_entries


def anchors(path):
    result, duplicates, fenced = set(), {}, False
    for line in read_bytes(path).decode("utf-8").splitlines():
        if line.startswith("```"):
            fenced = not fenced
        if fenced or not re.match(r"^#{1,6}\s", line):
            continue
        heading = re.sub(r"^#{1,6}\s+", "", line).strip().lower()
        slug = re.sub(r"[^\w -]", "", heading).replace(" ", "-")
        count = duplicates.get(slug, 0)
        duplicates[slug] = count + 1
        result.add(f"{slug}-{count}" if count else slug)
    return result


def compare_host(host_root, expected_head):
    host_root = root_path(host_root)
    if not re.fullmatch(r"[0-9a-f]{40}", expected_head):
        raise ValueError("Host comparison needs an immutable commit")
    environment = {
        **os.environ, "GIT_OPTIONAL_LOCKS": "0", "GIT_NO_LAZY_FETCH": "1",
        "GIT_TERMINAL_PROMPT": "0",
    }

    def query(*arguments):
        return subprocess.run(
            ["git", "--no-replace-objects", "-c", "core.fsmonitor=false", *arguments],
            cwd=host_root, check=True, capture_output=True, env=environment, timeout=30,
        ).stdout

    if query("rev-parse", "HEAD").decode("ascii").strip() != expected_head:
        return "REQUIRES_INSPECTION"
    expected = {}
    for row in query("ls-tree", "-r", "-z", expected_head).split(b"\0"):
        if row:
            metadata, raw_path = row.split(b"\t", 1)
            mode, kind, oid = metadata.decode("ascii").split()
            if kind != "blob" or mode not in {"100644", "100755"}:
                return "NOT_ASSESSED_UNSUPPORTED_TRACKED_ENTRY"
            expected[raw_path.decode("utf-8")] = (mode, oid)
    indexed = {}
    for row in query("ls-files", "--stage", "-z").split(b"\0"):
        if row:
            metadata, raw_path = row.split(b"\t", 1)
            mode, oid, stage = metadata.decode("ascii").split()
            if stage != "0":
                return "REQUIRES_INSPECTION"
            indexed[raw_path.decode("utf-8")] = (mode, oid)
    if indexed != expected or query("ls-files", "--others", "--exclude-standard", "-z"):
        return "REQUIRES_INSPECTION"
    # Avoid git status/diff: clean filters and filesystem-monitor hooks can run code.
    for relative, (_, oid) in expected.items():
        path = child(host_root, relative)
        if not path.is_file():
            return "REQUIRES_INSPECTION"
        data = read_bytes(path)
        if hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest() != oid:
            return "REQUIRES_INSPECTION"
    return "CLEAN_UNCHANGED_EXACT_BYTES"


def verify(root, git_dir, *, context_root=None, host_root=None, host_head=None, receipt=False):
    root, git_dir = root_path(root), root_path(git_dir)
    inventory, source, entries = load_inventory(root)
    snapshot, failures = inventory["snapshot"], []
    commit = snapshot["commit"]
    if not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise ValueError("Invalid pinned source revision")
    leaves = {path: row for path, row in entries.items() if row["git_type"] != "tree"}

    def load(name):
        return read_json(child(root, "evidence/" + name))

    catalog = load("catalog.json")
    references = load("resolved-references.json")
    refs = references["references"]
    study = read_json(child(root, "study.json"))
    actual_entries = unique_records(tree_entries(
        git(git_dir, "ls-tree", "-r", "-t", "-z", "--long", commit), snapshot["repository_url"], commit,
    ), "path")
    if set(actual_entries) != set(entries):
        failures.append("PINNED_TREE_ACCOUNTING")
    if git(git_dir, "rev-parse", f"{commit}^{{tree}}").decode().strip() != snapshot["tree"]:
        failures.append("PINNED_TREE_IDENTITY")
    for path, row in entries.items():
        actual = actual_entries.get(path, {})
        if any(actual.get(key) != row[key] for key in ("mode", "git_type", "git_object", "size_bytes")):
            failures.append("GIT_METADATA")
    expected_files = {path for path, row in leaves.items() if row["materialization"] == "exact_blob_bytes"}
    observed_files = set()
    if source.exists():
        for path in source.rglob("*"):
            checked = child(source, path.relative_to(source).as_posix())
            if checked.is_file():
                observed_files.add(checked.relative_to(source).as_posix())
    if observed_files != expected_files:
        failures.append("MATERIALIZED_FILE_ACCOUNTING")
    for path in expected_files:
        source_bytes(source, leaves[path])
    for ref in refs:
        entry = entries[ref["path"]]
        if not 1 <= ref["start"] <= ref["end"] <= entry["line_count"]:
            failures.append("REFERENCE_RANGE")
        if ref["url"] != entry["source_url"] + f"#L{ref['start']}-L{ref['end']}":
            failures.append("REFERENCE_REVISION")
    if any(value != commit for value in (
        study["primary_source"]["commit"], catalog["commit"], references["commit"],
    )):
        failures.append("MIXED_SOURCE_REVISIONS")
    resource_count = hook_count = 0
    for plugin in catalog["plugins"]:
        prefix = f"plugins/{plugin['name']}"
        manifest = read_json(child(source, prefix + "/plugin.json"))
        for kind in ("skills", "agents"):
            for item in manifest.get(kind, []):
                path = prefix + "/" + item.removeprefix("./") + ("/SKILL.md" if kind == "skills" else "")
                child(source, path)
                if path not in expected_files:
                    failures.append("DECLARED_RESOURCE")
                resource_count += 1
        for hook_file in plugin["hook_files"]:
            hook_path = child(source, hook_file)
            for hook in read_json(hook_path)["hooks"]:
                relative = hook_path.parent.relative_to(source).as_posix() + "/" + hook["script"]
                target = child(source, relative)
                if not target.is_file() or target.relative_to(source).as_posix() not in expected_files:
                    failures.append("HOOK_SCRIPT_REFERENCE")
                hook_count += 1
    repository = urlsplit(snapshot["repository_url"])
    marker = repository.path.rstrip("/") + f"/blob/{commit}/"
    local_links = pinned_links = 0
    markdown_files = sorted(root.glob("*.md"))
    for document in markdown_files:
        text = read_bytes(child(root, document.name)).decode("utf-8")
        text = re.sub(r"```.*?```", "", text, flags=re.S)
        for target in re.findall(r"(?<!!)\[[^\]\n]*\]\(([^)]+)\)", text):
            parsed = urlsplit(target)
            if parsed.scheme or parsed.netloc:
                if parsed.netloc == repository.netloc and parsed.path.startswith(marker):
                    path = unquote(parsed.path[len(marker):])
                    entry = leaves.get(path)
                    if entry is None:
                        failures.append("PINNED_SOURCE_LINK")
                    elif parsed.fragment:
                        match = re.fullmatch(r"L(\d+)(?:-L(\d+))?", parsed.fragment)
                        if not match or not 1 <= int(match[1]) <= int(match[2] or match[1]) <= entry["line_count"]:
                            failures.append("SOURCE_LINK_RANGE")
                    pinned_links += 1
                elif parsed.netloc == repository.netloc and parsed.path.startswith(repository.path.rstrip("/") + "/blob/"):
                    failures.append("UNEXPECTED_SOURCE_REVISION")
                continue
            destination = (document.parent / unquote(parsed.path)).resolve() if parsed.path else document
            if not destination.is_relative_to(root):
                raise ValueError("Documentation link escapes the explicit root")
            destination = child(root, destination.relative_to(root).as_posix())
            if not destination.exists():
                failures.append("LOCAL_LINK")
            elif parsed.fragment and destination.suffix == ".md" and unquote(parsed.fragment) not in anchors(destination):
                failures.append("LOCAL_ANCHOR")
            local_links += 1

    def csv_rows(name):
        return list(csv.DictReader(io.StringIO(read_bytes(child(root, "evidence/" + name)).decode("utf-8-sig"))))

    coverage = csv_rows("coverage.csv")
    if set(unique_records(coverage, "path")) != set(leaves):
        failures.append("PER_FILE_COVERAGE")
    summary = load("coverage-summary.json")
    if summary["commit"] != commit or summary["exclusive_depth_counts"] != dict(Counter(row["depth"] for row in coverage)):
        failures.append("DEPTH_ACCOUNTING")
    for name, category in [
        ("skills.csv", "skills"), ("agents.csv", "agents"),
        ("executable-surfaces.csv", "scripts"), ("queries.csv", "queries"),
    ]:
        if set(unique_records(csv_rows(name), "path")) != {row["path"] for row in catalog[category]}:
            failures.append("CATALOG_CSV")
    context_pages = study.get("context_source", {}).get("pages", [])
    if context_pages and context_root is None:
        raise ValueError("Recorded context requires an explicit --context-root")
    if context_root is not None:
        context_root = root_path(context_root)
    for page in context_pages:
        if hashlib.sha256(read_bytes(child(context_root, page["local_path"]))).hexdigest() != page["sha256"]:
            failures.append("CONTEXT_HASH")
    recorded_checks = study.get("recorded_checks", [])
    for check in recorded_checks:
        data = read_bytes(child(root, check["path"]))
        if hashlib.sha256(data).hexdigest() != check["sha256"]:
            failures.append("RECORDED_CHECK_HASH")
        if any(token not in data.decode("utf-8-sig") for token in check.get("required_text", [])):
            failures.append("RECORDED_CHECK_EXPECTATION")
    parse_doc = load("static-checks.json")
    expected_parses = {
        (path, "json_parse" if path.endswith(".json") else "python_ast_parse")
        for path in expected_files if path.endswith((".json", ".py"))
    }
    parsed = parse_doc["checks"]
    if (
        parse_doc["commit"] != commit or len(parsed) != len(expected_parses)
        or {(row["path"], row["check"]) for row in parsed} != expected_parses
        or any(row["status"] != "PASS" for row in parsed)
    ):
        failures.append("STATIC_PARSE_SCOPE")
    powershell_paths = {path for path in expected_files if path.endswith(".ps1")}
    ps_checks = []
    if powershell_paths:
        ps_doc = load("powershell-static-checks.json")
        ps_checks = ps_doc["checks"]
        if ps_doc["commit"] != commit or set(unique_records(ps_checks, "path")) != powershell_paths or any(
            row["status"] != "PASS" for row in ps_checks
        ):
            failures.append("POWERSHELL_PARSE_SCOPE")
    host_status = "NOT_ASSESSED"
    if bool(host_root) != bool(host_head):
        raise ValueError("Host comparison needs both --host-root and --host-head")
    if host_root:
        host_status = compare_host(host_root, host_head)
        if host_status != "CLEAN_UNCHANGED_EXACT_BYTES":
            failures.append("HOST_BASELINE")
    files = []
    for path in sorted(root.rglob("*")):
        checked = child(root, path.relative_to(root).as_posix())
        if checked.is_file() and checked.name not in {"verification.json", "corpus-files.json"}:
            if checked.suffix == ".json":
                read_json(checked)
            data = read_bytes(checked)
            files.append({"path": checked.relative_to(root).as_posix(), "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)})
    result = {
        "schema_version": 1, "result": "FAIL" if failures else "PASS",
        "verified_at_utc": datetime.now(timezone.utc).isoformat(), "commit": commit,
        "materialized_blobs_rechecked": len(expected_files), "tree_entries_reconciled": len(entries),
        "unmaterialized_leaves": len(leaves) - len(expected_files), "focused_source_references": len(refs),
        "declared_resources": resource_count, "hook_script_references": hook_count,
        "markdown_files": len(markdown_files), "local_links_checked": local_links, "pinned_links_checked": pinned_links,
        "context_hashes_checked": len(context_pages), "recorded_check_receipts_checked": len(recorded_checks),
        "source_static_parses": len(parsed) + len(ps_checks), "host_worktree": host_status,
        "live_runtime": "NOT_RUN", "network_requests": 0, "failure_counts": dict(Counter(failures)),
    }
    if receipt:
        write_json(root, child(root, "evidence/corpus-files.json"), files)
        write_json(root, child(root, "evidence/verification.json"), result)
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True)
    parser.add_argument("--git-dir", required=True)
    parser.add_argument("--context-root")
    parser.add_argument("--host-root")
    parser.add_argument("--host-head")
    parser.add_argument("--receipt", action="store_true")
    args = parser.parse_args(argv)
    return verify(args.root, args.git_dir, context_root=args.context_root, host_root=args.host_root, host_head=args.host_head, receipt=args.receipt)


if __name__ == "__main__":
    try:
        safe_main(main)
    except subprocess.SubprocessError:
        print('{"result":"FAIL","error_type":"LOCAL_GIT_READ_FAILED"}')
        raise SystemExit(1) from None
