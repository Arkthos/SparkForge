"""Build or verify an explicitly selected public research corpus, entirely offline."""

import argparse
import hashlib
import re
from collections import defaultdict
from datetime import datetime, timezone
from urllib.parse import quote, unquote, urlsplit

from .._common import child, read_bytes, read_json, root_path, safe_main, write_json, write_text


REQUIRED_DOCS = (
    "README.md", "SCOPE.md", "SPECIFICATIONS_AND_INTAKE.md", "REUSE_MAP.md",
    "FACTORY_PATTERNS.md", "QUALITY_AND_EVALUATION.md",
    "KNOWLEDGE_AND_GOVERNANCE.md", "COMPATIBILITY_AND_LICENSING.md",
    "INDUSTRY_AND_THEORY.md", "DISCOVERY_APPENDIX.md",
    "COVERAGE_AND_VALIDATION.md", "CATALOG.md", "EVIDENCE.md",
)


def safe_child(root, relative):
    return child(root, relative)


def verify_record(root, metadata, record):
    data = read_bytes(safe_child(root, record["local_file"]))
    text = data.decode("utf-8")
    blob = hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()
    actual = (len(data), hashlib.sha256(data).hexdigest(), blob, len(text.splitlines()))
    expected = (record["bytes"], record["sha256"], record["git_blob"], record["lines"])
    if actual != expected:
        raise ValueError("Source byte/hash/line mismatch")
    if record["commit"] != metadata["commit"]:
        raise ValueError("Source revision mismatch")
    parsed = urlsplit(record["source_url"])
    expected_path = f"/{metadata['repository']}/blob/{metadata['commit']}/{record['path']}"
    if parsed.scheme != "https" or parsed.netloc != "github.com" or unquote(parsed.path) != expected_path:
        raise ValueError("Source URL is not the recorded immutable revision")
    if parsed.query or parsed.fragment or record["is_lfs_pointer"]:
        raise ValueError("Unsupported source representation")
    return text


def normalize_ranges(ranges, line_count):
    result = []
    for start, requested_end in ranges:
        if type(start) is not int or type(requested_end) is not int:
            raise ValueError("Invalid inspected line range")
        end = line_count if requested_end == -1 else min(requested_end, line_count)
        if start < 1 or start > end:
            raise ValueError("Invalid or empty inspected line range")
        result.append([start, end])
    return result


def merge_ranges(ranges):
    merged = []
    for start, end in sorted(ranges):
        if merged and start <= merged[-1][1] + 1:
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])
    return merged


def classify_license(text):
    value = " ".join(text.lower().split())
    if (
        "permission is hereby granted, free of charge" in value
        and "to deal in the software without restriction" in value
        and "copyright notice and this permission notice" in value
    ):
        return "MIT"
    if "apache license" in value and "version 2.0" in value:
        return "Apache-2.0"
    return "NOT_ESTABLISHED"


def verify_video_reference(root, reference, candidates):
    metadata_path = safe_child(root, reference["metadata_file"])
    metadata_bytes = read_bytes(metadata_path)
    metadata = read_json(metadata_path)
    video_id = metadata["video_id"]
    if metadata["schema_version"] != 1 or not re.fullmatch(r"[A-Za-z0-9_-]{11}", video_id):
        raise ValueError("Invalid video reference identity")
    if metadata["url"] != f"https://www.youtube.com/watch?v={video_id}":
        raise ValueError("Video URL does not match its identity")
    candidate = candidates[reference["candidate"]]
    linked = metadata["linked_source"]
    if (linked["repository"].casefold(), linked["commit"]) != (
        candidate["canonical_repository"].casefold(), candidate["commit"]
    ):
        raise ValueError("Video companion revision does not match the candidate pin")
    transcript = metadata["transcript"]
    count = transcript["unique_segments"]
    if type(count) is not int or count < 1 or transcript["raw_dom_rows"] < count:
        raise ValueError("Invalid transcript segment inventory")
    ranges = transcript["reviewed_index_ranges"]
    if any(type(start) is not int or type(end) is not int or not 0 <= start <= end < count for start, end in ranges):
        raise ValueError("Invalid transcript inspection range")
    if transcript["all_available_segments_reviewed"] and merge_ranges(ranges) != [[0, count - 1]]:
        raise ValueError("Claimed full transcript review has a coverage gap")
    if not re.fullmatch(r"[a-f0-9]{64}", transcript["sha256_at_review"]):
        raise ValueError("Invalid recorded transcript fingerprint")
    if transcript["full_text_stored"]:
        raise ValueError("Video references retain metadata, not full transcript text")
    image = metadata["user_image"]
    image_data = read_bytes(safe_child(root, image["path"]))
    if (
        not image_data.startswith(b"\x89PNG\r\n\x1a\n")
        or len(image_data) != image["bytes"]
        or hashlib.sha256(image_data).hexdigest() != image["sha256"]
    ):
        raise ValueError("User-provided image bytes do not match the evidence record")
    document = safe_child(root, reference["document"])
    if document.suffix.lower() != ".md" or not document.is_file():
        raise ValueError("Video review document is missing or unsupported")
    return {
        **reference, "metadata": metadata,
        "metadata_sha256": hashlib.sha256(metadata_bytes).hexdigest(),
        "user_image_digest_verified": True, "full_transcript_bytes_reverified": False,
    }


def build_index(root):
    root = root_path(root)
    research = read_json(child(root, "research.json"))
    if research["schema_version"] != 1 or research["candidate_execution"] != "NOT_RUN":
        raise ValueError("Unexpected research scope")
    candidates = research["candidates"]
    ids = [candidate["id"] for candidate in candidates]
    if not ids or len(set(ids)) != len(ids) or any(
        not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", value) for value in ids
    ):
        raise ValueError("Invalid, empty or duplicate candidate identifiers")
    captured = {}
    for directory_entry in sorted(child(root, "sources").iterdir()):
        directory = child(root, directory_entry.relative_to(root).as_posix())
        metadata = read_json(child(directory, "metadata.json"))
        if metadata["visibility"] != "public" or not re.fullmatch(r"[0-9a-f]{40}", metadata["commit"]):
            raise ValueError("Source is not a public immutable snapshot")
        key = metadata["repository"].casefold()
        if key in captured:
            raise ValueError("Duplicate canonical repository")
        files = read_json(child(directory, "files.json"))
        texts = {}
        for path, record in files.items():
            if path != record["path"]:
                raise ValueError("Source index key/path mismatch")
            texts[path] = verify_record(root, metadata, record)
        captured[key] = (directory, metadata, files, texts)
    candidate_data = {}
    for candidate in candidates:
        directory, metadata, files, texts = captured[candidate["repository"].casefold()]
        licenses = [
            {"path": path, "classification": classify_license(text)}
            for path, text in texts.items()
            if re.fullmatch(r"(license|licence|copying)(\.(md|txt|rst))?", path, re.I)
        ]
        observed = {item["classification"] for item in licenses} or {"NOT_ESTABLISHED"}
        if candidate["root_license"] not in observed:
            raise ValueError("License classification disagrees with captured text")
        candidate_data[candidate["id"]] = {
            **candidate, "canonical_repository": metadata["repository"],
            "commit": metadata["commit"], "commit_date": metadata["commit_date"],
            "observed_at_utc": metadata["observed_at_utc"], "archived": metadata["archived"],
            "url": metadata["url"],
            "metadata_file": (directory / "metadata.json").relative_to(root).as_posix(),
            "license_evidence": licenses, "files": files,
        }
    if len(candidate_data) != len(captured):
        raise ValueError("Candidate catalog and captured repositories do not reconcile")
    inspections = [
        {
            "id": candidate["id"] + "-overview", "candidate": candidate["id"],
            "path": candidate.get("primary_document", "README.md"), "kind": "documentation",
            "ranges": [candidate["overview"]],
            "focus": "Screening observations remain upstream claims unless separately traced.",
        }
        for candidate in candidates
    ] + research["inspections"]
    if len({item["id"] for item in inspections}) != len(inspections):
        raise ValueError("Duplicate inspection identifiers")
    reviewed = defaultdict(list)
    for item in inspections:
        record = candidate_data[item["candidate"]]["files"][item["path"]]
        item["requested_ranges"] = item["ranges"]
        item["ranges"] = normalize_ranges(item["ranges"], record["lines"])
        item["source_url"] = record["source_url"]
        item["local_file"] = record["local_file"]
        item["source_sha256"] = record["sha256"]
        reviewed[(item["candidate"], item["path"])].extend(item["ranges"])
    file_count = 0
    for candidate in candidate_data.values():
        for path, record in candidate["files"].items():
            record["registered_review_ranges"] = merge_ranges(reviewed.get((candidate["id"], path), []))
            file_count += 1
    videos = [verify_video_reference(root, ref, candidate_data) for ref in research.get("video_reviews", [])]
    if len({item["id"] for item in videos}) != len(videos):
        raise ValueError("Duplicate video review identifiers")
    return {
        "schema_version": 1, "boundary": research["purpose"], "candidate_execution": "NOT_RUN",
        "runtime_acceptance": "NOT_ASSESSED",
        "counts": {
            "repositories": len(candidates), "captured_text_files": file_count,
            "registered_inspections": len(inspections),
            "files_with_registered_semantic_ranges": len(reviewed),
            "files_without_registered_semantic_ranges": file_count - len(reviewed),
            "repositories_with_selected_implementation_review": len({
                item["candidate"] for item in inspections if item["kind"] == "implementation"
            }),
            "unique_registered_lines": sum(
                end - start + 1 for ranges in reviewed.values() for start, end in merge_ranges(ranges)
            ),
            "registered_video_reviews": len(videos), "verified_user_images": len(videos),
        },
        "candidates": list(candidate_data.values()), "inspections": inspections, "video_reviews": videos,
    }


def local_link(path):
    return quote(path.replace("\\", "/"), safe="/.-")


def render_catalog(index):
    lines = [
        "# Pinned candidate catalog", "",
        "Source-review findings are not installed components or runtime acceptance.",
        "Root-license classification is not redistribution clearance.", "",
        "| Candidate | Family | Review depth | Research disposition |", "|---|---|---|---|",
    ]
    for candidate in index["candidates"]:
        lines.append(
            f"| [{candidate['canonical_repository']}](#{candidate['id']}) | {candidate['category']} | "
            f"{candidate['depth']} | {candidate['fit']} |"
        )
    for candidate in index["candidates"]:
        record = candidate["files"][candidate.get("primary_document", "README.md")]
        lines.extend([
            "", f"## {candidate['id']}", "",
            f"**Repository:** [{candidate['canonical_repository']}]({candidate['url']}/tree/{candidate['commit']})  ",
            f"**Pin:** `{candidate['commit']}`; committed {candidate['commit_date']}  ",
            f"**Root license:** {candidate['root_license']}; **archived:** {str(candidate['archived']).lower()}  ",
            f"**Depth:** {candidate['depth']}; **disposition:** {candidate['fit']}", "",
            candidate["summary"], "", "**Reusable contribution:** " + candidate["reuse"], "",
            "**Conditions and exclusions:** " + candidate["conditions"], "",
        ])
        if candidate.get("license_note"):
            lines.extend(["**License qualification:** " + candidate["license_note"], ""])
        lines.append(
            f"[Pinned overview]({record['source_url']}) | "
            f"[Recorded source metadata]({local_link(candidate['metadata_file'])}) | "
            f"[Inspection record](EVIDENCE.md#{candidate['id']}-overview)"
        )
    return "\n".join(lines) + "\n"


def render_evidence(index):
    lines = [
        "# Source inspection register", "",
        "Registered inclusive ranges are clipped at EOF and are not a whole-file or security review.",
        "Cached text and test-source inspection do not establish execution or semantic acceptance.", "",
    ]
    for item in index["inspections"]:
        links = [f"[L{start}-L{end}]({item['source_url']}#L{start}-L{end})" for start, end in item["ranges"]]
        lines.extend([
            f"## {item['id']}", "",
            f"**Candidate:** [{item['candidate']}](CATALOG.md#{item['candidate']}); **kind:** {item['kind']}  ",
            f"**Original path:** `{item['path']}`  ", "**Pinned ranges:** " + ", ".join(links) + "  ",
            f"**Local source:** [Inert captured text]({local_link(item['local_file'])})", "", item["focus"], "",
        ])
    for item in index["video_reviews"]:
        metadata = item["metadata"]
        lines.extend([
            f"## {item['id']}", "", f"**Video:** [{metadata['title']}]({metadata['url']})  ",
            f"**Review:** [{item['document']}]({local_link(item['document'])})  ",
            f"**Source record:** [Metadata and coverage]({local_link(item['metadata_file'])})  ",
            f"**User image:** [Preserved PNG]({local_link(metadata['user_image']['path'])})", "",
            "The image digest is checked. Registered caption coverage cannot be rehashed without retained caption bytes.", "",
        ])
    return "\n".join(lines)


def heading_ids(text):
    result = set(re.findall(r'<a\s+(?:id|name)="([^"]+)"', text))
    occurrences = defaultdict(int)
    for heading in re.findall(r"^#{1,6}\s+(.+?)\s*#*\s*$", text, re.M):
        slug = re.sub(r"[^\w\- ]", "", heading.lower()).replace(" ", "-")
        occurrence = occurrences[slug]
        occurrences[slug] += 1
        result.add(f"{slug}-{occurrence}" if occurrence else slug)
    return result


def verify_links(documents, workspace):
    workspace = root_path(workspace)
    checked = anchors = 0
    for document in documents:
        text = re.sub(r"```.*?```", "", read_bytes(document).decode("utf-8"), flags=re.S)
        for target in re.findall(r"!?\[[^\]]*\]\(([^)]+)\)", text):
            parsed = urlsplit(target.strip("<>"))
            if parsed.scheme or parsed.netloc:
                continue
            destination = (document.parent / unquote(parsed.path)).absolute() if parsed.path else document
            try:
                relative = destination.resolve().relative_to(workspace).as_posix()
            except ValueError:
                raise ValueError("Out-of-workspace documentation link") from None
            destination = child(workspace, relative)
            if not destination.exists():
                raise ValueError("Broken local documentation link")
            checked += 1
            if parsed.fragment and destination.suffix.lower() == ".md":
                if unquote(parsed.fragment) not in heading_ids(read_bytes(destination).decode("utf-8")):
                    raise ValueError("Broken Markdown anchor")
                anchors += 1
    return checked, anchors


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=["index", "verify"])
    parser.add_argument("--root", required=True, help="Corpus root; index writes only its documented generated files.")
    parser.add_argument("--workspace", required=True, help="Explicit boundary for local documentation links.")
    parser.add_argument("--receipt", action="store_true", help="Write verification.json after a successful verification.")
    args = parser.parse_args(argv)
    root, workspace = root_path(args.root), root_path(args.workspace)
    if not root.is_relative_to(workspace):
        raise ValueError("The corpus is outside the selected documentation workspace")
    index = build_index(root)
    generated = {"CATALOG.md": render_catalog(index), "EVIDENCE.md": render_evidence(index)}
    if args.mode == "index":
        write_json(root, child(root, "source-index.json"), index)
        for name, text in generated.items():
            write_text(root, child(root, name), text)
        return {"status": "INDEXED", "counts": index["counts"], "network_requests": 0}
    if read_json(child(root, "source-index.json")) != index:
        raise ValueError("Generated source index is stale")
    for name, text in generated.items():
        if read_bytes(child(root, name)).decode("utf-8") != text:
            raise ValueError("Generated document is stale")
    research = read_json(child(root, "research.json"))
    documents = [child(root, name) for name in research.get("required_documents", REQUIRED_DOCS)]
    documents.extend(child(root, item["document"]) for item in index["video_reviews"])
    if len(set(documents)) != len(documents):
        raise ValueError("Duplicate research document declarations")
    for path in documents:
        if not path.is_file():
            raise ValueError("Required research document is missing")
    checked, anchors = verify_links(documents, workspace)
    result = {
        "status": "PASS", "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "counts": index["counts"], "documents": len(documents), "local_links_checked": checked,
        "markdown_anchors_checked": anchors, "source_bytes_and_git_blob_ids_verified": True,
        "generated_views_match_canonical_records": True, "full_video_transcript_bytes_reverified": False,
        "candidate_software_or_evaluations_executed": False, "network_requests": 0,
        "document_sha256": {path.name: hashlib.sha256(read_bytes(path)).hexdigest() for path in documents},
        "limits": ["Selected evidence only; no live compatibility, legal clearance or whole-repository review."],
    }
    if args.receipt:
        write_json(root, child(root, "verification.json"), result)
    return result


if __name__ == "__main__":
    safe_main(main)
