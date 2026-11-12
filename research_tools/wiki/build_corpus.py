"""Assemble supplied, source-bound summaries and a selected taxonomy into local views.

No private taxonomy, page IDs, review findings or operational observations are
embedded. Assembly records supplied claims; it does not perform or authorize review.
"""

import argparse
import hashlib
import html
import os
import re
import urllib.parse
from collections import Counter
from pathlib import Path

from .._common import child, read_bytes, read_json, root_path, unique_records, write_json, write_text
from . import collect_wiki as collector


def primary_topic(page, plan):
    topic = plan["page_topics"][str(page["page_id"])]
    collector.require(topic in plan["topics"], "UNKNOWN_PRIMARY_TOPIC")
    return topic


def heading_slug(value):
    value = re.sub(r"<[^>]*>", "", value).strip().lower()
    value = re.sub(r"[^\w\s-]", "", value)
    return re.sub(r"\s+", "-", value)


def render_document(root, path, authored):
    parser = collector.markdown_parser().enable("table")
    parser.options["html"] = False
    tokens = parser.parse(read_bytes(path).decode("utf-8"))
    heading_counts = Counter()
    for index, token in enumerate(tokens):
        if token.type == "heading_open":
            slug = heading_slug(tokens[index + 1].content)
            count = heading_counts[slug]
            heading_counts[slug] += 1
            token.attrSet("id", slug if count == 0 else f"{slug}-{count}")

        def rewrite(current):
            attribute = "href" if current.type == "link_open" else "src" if current.type == "image" else None
            if attribute:
                target = current.attrGet(attribute)
                parts = urllib.parse.urlsplit(target)
                if not parts.scheme and not parts.netloc:
                    destination = (path.parent / urllib.parse.unquote(parts.path)).resolve() if parts.path else path
                    destination = collector.inside(root, destination)
                    if destination in authored:
                        destination = child(root, "knowledge/" + destination.stem + ".html")
                    relative = os.path.relpath(destination, child(root, "knowledge")).replace("\\", "/")
                    current.attrSet(attribute, urllib.parse.quote(relative, safe="/.-") + ("#" + parts.fragment if parts.fragment else ""))
            for token_child in current.children or []:
                rewrite(token_child)

        rewrite(token)
    body = parser.renderer.render(tokens, parser.options, {})
    title = next((token.content for token in tokens if token.type == "inline"), path.stem)
    body = '<p><a href="../index.html">Corpus home</a> | <a href="../source-index.html">Original source index</a></p>' + body
    write_text(root, child(root, "knowledge/" + path.stem + ".html"), collector.html_document(title, body))


def build(root, plan, summaries):
    root = root_path(root)
    manifest, snapshot = read_json(child(root, "manifest.json")), read_json(child(root, "snapshot.json"))
    collector.verify_sources(root, manifest, snapshot)
    pages = unique_records(manifest["pages"], "page_id")
    commit = snapshot["commit"]
    collector.require(plan["schema_version"] == summaries["schema_version"] == 1, "UNSUPPORTED_BUILD_INPUT")
    collector.require(plan["source_commit"] == summaries["source_commit"] == commit, "BUILD_REVISION_MISMATCH")
    summary_records = summaries["pages"]
    expected = {str(page["page_id"]) for page in pages.values() if page["bytes"] > 0}
    collector.require(set(summary_records) == expected, "SOURCE_SUMMARY_ACCOUNTING_MISMATCH")
    collector.require(set(plan["page_topics"]) == {str(key) for key in pages}, "PAGE_TOPIC_ACCOUNTING_MISMATCH")
    topics = plan["topics"]
    collector.require(topics and len(topics) == len(set(topics)), "INVALID_TOPIC_SET")
    for topic in topics:
        collector.require(re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9_-]*", topic) is not None, "INVALID_TOPIC_NAME")
    generated_names = ["SOURCE_GUIDE.md", "COVERAGE.md", "ATTACHMENTS.md"]
    authored_names = list(plan.get("authored_documents", [])) + ["topics/" + topic + ".md" for topic in topics]
    collector.require(len(authored_names) == len(set(authored_names)), "DUPLICATE_AUTHORED_DOCUMENT")
    authored = [child(root, name) for name in generated_names + authored_names]
    collector.require(len({path.stem.casefold() for path in authored}) == len(authored), "FLAT_RENDER_FILENAME_COLLISION")
    for name in authored_names:
        path = child(root, name)
        collector.require(path.suffix == ".md" and path.is_file(), "AUTHORED_DOCUMENT_MISSING")
    supplied_reviews = plan.get("attachment_reviews", {})
    attachments = unique_records(manifest["attachments"], "key")
    collector.require(set(supplied_reviews).issubset(attachments), "UNKNOWN_ATTACHMENT_REVIEW")
    for key, review in supplied_reviews.items():
        collector.require(review["source_sha256"] == attachments[key]["sha256"], "ATTACHMENT_REVIEW_HASH_MISMATCH")
        collector.require(isinstance(review.get("review_status"), str) and review["review_status"], "MISSING_REVIEW_STATUS")
    source_notes, guide = [], [
        "# Source guide and page coverage", "", f"Frozen source commit: `{commit}`.",
        "Summaries below are supplied source-bound paraphrases, not independent validation.",
        "Empty pages receive no invented substantive guidance.", "",
    ]
    for page in pages.values():
        page_id, topic = page["page_id"], primary_topic(page, plan)
        if page["bytes"] == 0:
            kind, summary = "EMPTY_SOURCE", "Empty page at the frozen revision; its hierarchy role is retained."
        else:
            entry = summary_records[str(page_id)]
            collector.require(entry["source_sha256"] == page["sha256"], "SOURCE_SUMMARY_HASH_MISMATCH")
            collector.require(isinstance(entry.get("summary"), str) and entry["summary"].strip(), "EMPTY_SOURCE_SUMMARY")
            kind, summary = entry.get("review_kind", "SUPPLIED_CONTENT_SUMMARY"), entry["summary"]
            collector.require(kind != "EMPTY_SOURCE", "NONEMPTY_SOURCE_MARKED_EMPTY")
        source_notes.append({
            "page_id": page_id, "source_key": page["key"], "source_path": page["path"],
            "source_sha256": page["sha256"], "source_blob_id": page["source_blob_id"],
            "snapshot_commit": commit, "source_retrieved_at_utc": page.get("retrieved_at_utc"),
            "canonical_url": page.get("canonical_url"), "review_kind": kind,
            "summary_type": "SUPPLIED_PARAPHRASE_NOT_INDEPENDENTLY_VERIFIED",
            "summary": summary, "primary_topic": "topics/" + topic + ".md",
            "original_view": "views/" + page["key"] + ".html",
        })
        guide.extend([
            f"## Page {page_id}", "", "**" + collector.escape_markdown(page["path"]) + "**",
            f"**Disposition:** `{kind}`. [Original snapshot](views/{page['key']}.html) | [Topic](topics/{topic}.md)", "",
            summary, "",
        ])
    review_entries, attachment_lines = [], [
        "# Attachment inventory and supplied review", "",
        "Every attachment is accounted for. Missing review inputs remain NOT_REVIEWED.",
        "This builder does not inspect images, execute code or infer review from file type.", "",
        "| Item | Source pages | Recorded review | Original bytes |", "|---|---|---|---|",
    ]
    for key, attachment in attachments.items():
        review = supplied_reviews.get(key, {})
        page_ids = [page["page_id"] for page in pages.values() if page["key"] in attachment["source_page_keys"]]
        status = review.get("review_status", "NOT_REVIEWED")
        review_entries.append({
            "attachment_key": key, "source_page_ids": page_ids, "source_sha256": attachment["sha256"],
            "snapshot_commit": commit, "review_status": status, "notes": review.get("notes", ""),
            "review_input_supplied": key in supplied_reviews, "source_code_executed_by_builder": False,
        })
        sources = ", ".join(f"[Page {page_id}](SOURCE_GUIDE.md#page-{page_id})" for page_id in page_ids)
        attachment_lines.append(
            f"| {collector.escape_markdown(key)} | {sources} | `{collector.escape_markdown(status)}` | [Original]({collector.href(attachment['local_path'])}) |"
        )
    media = [child(root, name) for name in plan.get("media_files", [])]
    for path in media:
        collector.require(path.is_file(), "MEDIA_FILE_MISSING")
    review_kinds = dict(Counter(note["review_kind"] for note in source_notes))
    synthesis = {
        "status": "ASSEMBLED_SUPPLIED_NOTES_REQUIRES_REVIEW", "source_commit": commit,
        "assembled_at_utc": collector.utc_now(), "pages_accounted": len(source_notes),
        "content_pages_synthesized": len(summary_records), "empty_pages_accounted": len(pages) - len(summary_records),
        "review_kinds": review_kinds, "topical_chapters": len(topics),
        "attachment_review_counts": dict(Counter(row["review_status"] for row in review_entries)),
        "independent_human_review": "NOT_ASSESSED", "live_solution_validation": "NOT_PERFORMED",
        "model_requests": 0, "publication_authorized": False,
    }
    write_json(root, child(root, "source-notes.json"), {
        "schema_version": 1, "source_commit": commit, "pages": source_notes,
        "review_method": "Assembly of explicit, hash-bound input notes; no new substantive review performed.",
    })
    write_json(root, child(root, "attachment-review.json"), {"schema_version": 1, "source_commit": commit, "attachments": review_entries})
    write_text(root, child(root, "SOURCE_GUIDE.md"), "\n".join(guide))
    write_text(root, child(root, "ATTACHMENTS.md"), "\n".join(attachment_lines) + "\n")
    coverage = [
        "# Coverage and provenance", "", f"Frozen source commit: `{commit}`.",
        f"Scoped export: **{manifest['coverage_status']}**. Semantic conclusions remain supplied, not independently verified.", "",
        "| Measure | Count |", "|---|---:|",
        f"| Page nodes accounted | {len(pages)} |", f"| Nonempty pages with supplied summaries | {len(summary_records)} |",
        f"| Empty nodes accounted | {len(pages) - len(summary_records)} |", f"| Attachments retained | {len(attachments)} |",
        f"| Supplied attachment reviews | {len(supplied_reviews)} |", f"| Attachments without supplied review | {len(attachments) - len(supplied_reviews)} |",
        "", "Hash equality is not source accuracy, permission, release acceptance or semantic coverage.",
        "External references are not crawled; original restrictions also apply to derived notes.", "",
    ]
    write_text(root, child(root, "COVERAGE.md"), "\n".join(coverage))
    for path in authored:
        render_document(root, path, set(authored))
    source_rows = [
        f'<li><a href="views/{collector.href(page["key"])}.html">{html.escape(page["path"])}</a></li>' for page in pages.values()
    ]
    write_text(root, child(root, "source-index.html"), collector.html_document(
        "Original source hierarchy",
        '<h1>Original source hierarchy</h1><p><a href="index.html">Corpus home</a></p><ol>' + "".join(source_rows) + "</ol>",
    ))
    topic_rows = [f'<li><a href="knowledge/{collector.href(topic)}.html">{html.escape(topic)}</a></li>' for topic in topics]
    write_text(root, child(root, "index.html"), collector.html_document(
        "Local knowledge corpus",
        "<h1>Local knowledge corpus</h1><p>Supplied notes require review; no publication or operational acceptance is implied.</p>"
        f"<p>{len(pages)} page nodes accounted; {len(summary_records)} supplied summaries; {len(attachments)} attachments retained.</p>"
        '<p><a href="knowledge/SOURCE_GUIDE.html">Source guide</a> | <a href="source-index.html">Original hierarchy</a> | '
        '<a href="knowledge/ATTACHMENTS.html">Attachments</a> | <a href="knowledge/COVERAGE.html">Coverage</a></p><ol>'
        + "".join(topic_rows) + "</ol>",
    ))
    write_json(root, child(root, "corpus.json"), {
        "schema_version": 1, "source_commit": commit, "entry_points": ["index.html"],
        "topics": ["topics/" + topic + ".md" for topic in topics],
        "source_notes": "source-notes.json", "attachment_review": "attachment-review.json",
        "export_coverage": manifest["coverage_status"], "synthesis": synthesis,
    })
    artifacts = authored + [child(root, "knowledge/" + path.stem + ".html") for path in authored] + [
        child(root, name) for name in ("index.html", "source-index.html", "source-notes.json", "attachment-review.json", "corpus.json")
    ] + media
    collector.require(len(set(artifacts)) == len(artifacts), "DUPLICATE_DERIVED_ARTIFACT")
    write_json(root, child(root, "artifact-index.json"), {
        "schema_version": 1, "source_commit": commit, "created_at_utc": collector.utc_now(),
        "artifacts": [
            {"path": path.relative_to(root).as_posix(), "bytes": path.stat().st_size, "sha256": hashlib.sha256(read_bytes(path)).hexdigest()}
            for path in artifacts
        ],
    })
    manifest["synthesis"], manifest["validation"] = synthesis, {"status": "PENDING", "report": "corpus-verification.json"}
    collector.checkpoint(root, manifest)
    return {
        "result": "PASS", "status": synthesis["status"], "page_notes": len(source_notes),
        "supplied_summaries": len(summary_records), "artifacts": len(artifacts), "network_requests": 0,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, help="Explicit input/output corpus; original source files are never rewritten.")
    parser.add_argument("--plan", required=True, help="Explicit source-bound taxonomy/review input JSON.")
    parser.add_argument("--summaries", required=True, help="Explicit source-bound per-page notes JSON.")
    args = parser.parse_args(argv)
    return build(args.root, read_json(Path(args.plan)), read_json(Path(args.summaries)))


if __name__ == "__main__":
    collector.run_cli(main)
