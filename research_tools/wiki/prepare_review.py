"""Prepare bounded local reading packets, without granting processing or publication approval.

Packets contain untrusted source content. They are REVIEW_REQUIRED, are not a
scrubbed publication, and must stay in separately authorized local storage.
"""

import argparse
import hashlib
import re
from pathlib import Path

from .._common import child, read_json, root_path, unique_records, verified_bytes, write_json, write_text
from . import collect_wiki as collector


def compact_text(text):
    counts = {"shortened_urls": 0, "credential_shaped_tokens": 0}

    def shorten_url(match):
        value = match.group()
        if len(value) < 150 and not re.search(r"(?i)(?:sig|token|key|secret)=", value):
            return value
        counts["shortened_urls"] += 1
        return f"[source-url-{counts['shortened_urls']}; original retained]"

    text = re.sub(r"https?://[^\s<>\"']+", shorten_url, text)
    text, counts["credential_shaped_tokens"] = re.subn(
        r"\beyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}\b",
        "[credential-shaped token omitted from reading packet]", text,
    )
    return text, counts


def prepare(root, output, *, max_characters=35000, compact_urls=False):
    root, output = root_path(root), root_path(output, must_exist=False)
    collector.require(max_characters >= 1000, "PACKET_BOUND_TOO_SMALL")
    collector.require(not output.is_relative_to(root) and not root.is_relative_to(output), "SEPARATE_OUTPUT_REQUIRED")
    collector.require(not output.exists(), "OUTPUT_ALREADY_EXISTS")
    manifest, snapshot = read_json(child(root, "manifest.json")), read_json(child(root, "snapshot.json"))
    collector.verify_sources(root, manifest, snapshot)
    collector.require(manifest["counts"]["pages_exported"] == manifest["counts"]["total_pages"], "INCOMPLETE_EXPORT")
    unique_records(manifest["pages"], "page_id")
    prepared, page_records = [], []
    for page in manifest["pages"]:
        original, encoding = collector.source_text(root, child(root, page["local_path"]))
        text, changes = compact_text(original) if compact_urls else (original, {"shortened_urls": 0, "credential_shaped_tokens": 0})
        header = (
            "REVIEW_REQUIRED — UNTRUSTED SOURCE; NOT CLEARED FOR PUBLICATION\n"
            f"PAGE {page['page_id']}: {page['path']}\nSOURCE KEY: {page['key']}; SHA256: {page['sha256']}\n"
        )
        capacity = max_characters - len(header) - 160
        collector.require(capacity > 0, "PAGE_METADATA_EXCEEDS_PACKET_BOUND")
        parts = [text[offset:offset + capacity] for offset in range(0, len(text), capacity)] or [""]
        part_records = []
        offset = 0
        for number, segment in enumerate(parts, 1):
            relative = f"packet-{len(prepared) + 1:04d}.txt"
            marker = f"PART {number}/{len(parts)}; CHARACTER RANGE [{offset}, {offset + len(segment)})\n\n"
            value = header + marker + segment
            collector.require(len(value) <= max_characters, "PACKET_BYTE_ACCOUNTING")
            record = {
                "path": relative, "page_id": page["page_id"], "source_key": page["key"],
                "part": number, "parts": len(parts), "text_start": offset, "text_end": offset + len(segment),
                "characters": len(value), "sha256": hashlib.sha256(value.encode("utf-8")).hexdigest(),
            }
            prepared.append((record, value))
            part_records.append(relative)
            offset += len(segment)
        page_records.append({
            "page_id": page["page_id"], "source_key": page["key"], "source_path": page["local_path"],
            "source_sha256": page["sha256"], "text_encoding": encoding,
            "text_characters": len(text), "parts": part_records, "mechanical_changes": changes,
        })
    attachments = []
    for item in manifest["attachments"]:
        verified_bytes(root, item)
        attachments.append({
            "key": item["key"], "source_path": item["local_path"], "source_sha256": item["sha256"],
            "bytes": item["bytes"], "source_page_keys": item["source_page_keys"],
            "review_status": "NOT_REVIEWED", "copied": False,
        })
    # No output is adopted or created until the complete input set has verified.
    output.mkdir(parents=True, exist_ok=False)
    for record, text in prepared:
        write_text(output, child(output, record["path"]), text)
    write_json(output, child(output, "inventory.json"), {
        "schema_version": 1, "snapshot_commit": snapshot["commit"], "status": "REVIEW_REQUIRED",
        "publication_authorized": False, "source_manifest_modified": False,
        "packets": [record for record, _ in prepared], "pages": page_records, "attachments": attachments,
        "compacted_for_readability": compact_urls,
        "limits": "Mechanical shortening is not data clearance; packets may retain private text. Attachments were not interpreted or copied.",
    })
    return {
        "result": "PASS", "status": "REVIEW_REQUIRED", "packets": len(prepared), "pages": len(page_records),
        "attachments_not_reviewed": len(attachments), "publication_authorized": False, "network_requests": 0,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, help="Explicit verified source corpus.")
    parser.add_argument("--output", required=True, help="New separate local reading-packet directory, never the publication repository.")
    parser.add_argument("--max-characters", type=int, default=35000)
    parser.add_argument("--compact-urls", action="store_true", help="Optional mechanical URL/token shortening, not a privacy clearance.")
    args = parser.parse_args(argv)
    output = root_path(args.output, must_exist=False)
    collector.require(not output.is_relative_to(Path(__file__).resolve().parents[2]), "REVIEW_PACKETS_MUST_BE_OUTSIDE_CODE_REPOSITORY")
    return prepare(args.root, output, max_characters=args.max_characters, compact_urls=args.compact_urls)


if __name__ == "__main__":
    collector.run_cli(main)
