"""Verify local source bindings, supplied notes, artifact hashes and navigation.

Read-only by default. --receipt writes a separate verification result, never an
approval. PNG decoding is optional and does not establish visual review.
"""

import argparse
import urllib.parse
from collections import Counter

from .._common import child, read_bytes, read_json, root_path, unique_records, write_json
from . import collect_wiki as collector
from .build_corpus import heading_slug


def verify(root, *, receipt=False, decode_images=False):
    root = root_path(root)
    source_result = collector.verify(root)
    manifest = read_json(child(root, "manifest.json"))
    note_document = read_json(child(root, "source-notes.json"))
    review_document = read_json(child(root, "attachment-review.json"))
    artifact_document = read_json(child(root, "artifact-index.json"))
    notes, reviews, artifacts = note_document["pages"], review_document["attachments"], artifact_document["artifacts"]
    pages = unique_records(manifest["pages"], "page_id")
    attachments = unique_records(manifest["attachments"], "key")
    unique_records(artifacts, "path")
    failures = [] if source_result["result"] == "PASS" else ["SOURCE_VERIFICATION"]
    if any(document["source_commit"] != manifest["snapshot_commit"] for document in (note_document, review_document, artifact_document)):
        failures.append("DERIVED_REVISION")
    if set(unique_records(notes, "page_id")) != set(pages):
        failures.append("SOURCE_NOTE_ACCOUNTING")
    for note in notes:
        page = pages[note["page_id"]]
        if note["source_sha256"] != page["sha256"] or note["snapshot_commit"] != manifest["snapshot_commit"]:
            failures.append("SOURCE_NOTE_REVISION_BINDING")
        if not child(root, note["primary_topic"]).is_file():
            failures.append("SOURCE_NOTE_TOPIC")
        if (note["review_kind"] == "EMPTY_SOURCE") != (page["bytes"] == 0):
            failures.append("EMPTY_PAGE_ACCOUNTING")
    if set(unique_records(reviews, "attachment_key")) != set(attachments):
        failures.append("ATTACHMENT_REVIEW_ACCOUNTING")
    for review in reviews:
        if review["source_sha256"] != attachments[review["attachment_key"]]["sha256"] or review["snapshot_commit"] != manifest["snapshot_commit"]:
            failures.append("ATTACHMENT_REVIEW_BINDING")
    for artifact in artifacts:
        path = child(root, artifact["path"])
        if not path.is_file() or path.stat().st_size != artifact["bytes"] or collector.sha256_file(root, path) != artifact["sha256"]:
            failures.append("DERIVED_ARTIFACT_INTEGRITY")
    parser = collector.markdown_parser().enable("table")
    authored = [child(root, artifact["path"]) for artifact in artifacts if artifact["path"].endswith(".md")]
    anchors, parsed_documents = {}, {}
    for path in authored:
        tokens = parser.parse(read_bytes(path).decode("utf-8"))
        parsed_documents[path] = tokens
        counts, values = Counter(), set()
        for index, token in enumerate(tokens):
            if token.type == "heading_open":
                slug = heading_slug(tokens[index + 1].content)
                values.add(slug if counts[slug] == 0 else f"{slug}-{counts[slug]}")
                counts[slug] += 1
        anchors[path] = values
    checked_links = external_links = 0
    page_citations = set()
    for path, tokens in parsed_documents.items():
        def check(token):
            nonlocal checked_links, external_links
            attribute = "href" if token.type == "link_open" else "src" if token.type == "image" else None
            if attribute:
                parts = urllib.parse.urlsplit(token.attrGet(attribute))
                if parts.scheme or parts.netloc:
                    external_links += 1
                else:
                    destination = (path.parent / urllib.parse.unquote(parts.path)).resolve() if parts.path else path
                    destination = collector.inside(root, destination)
                    if not destination.is_file():
                        failures.append("AUTHORED_LOCAL_LINK")
                    fragment = urllib.parse.unquote(parts.fragment)
                    if fragment and destination in anchors and fragment not in anchors[destination]:
                        failures.append("AUTHORED_LOCAL_ANCHOR")
                    if destination.name == "SOURCE_GUIDE.md" and fragment.startswith("page-"):
                        page_citations.add(int(fragment.removeprefix("page-")))
                    checked_links += 1
            for token_child in token.children or []:
                check(token_child)
        for token in tokens:
            check(token)
    html_links = 0
    html_paths = [child(root, artifact["path"]) for artifact in artifacts if artifact["path"].endswith(".html")]
    for path in html_paths:
        contents = read_bytes(path).decode("utf-8")
        document = collector.HtmlReferences()
        document.feed(contents)
        if "<script" in contents.lower() or "<iframe" in contents.lower():
            failures.append("ACTIVE_AUTHORED_HTML")
        for target in document.targets:
            parts = urllib.parse.urlsplit(target)
            if not parts.scheme and not parts.netloc:
                destination = (path.parent / urllib.parse.unquote(parts.path)).resolve() if parts.path else path
                destination = collector.inside(root, destination)
                if not destination.is_file():
                    failures.append("AUTHORED_HTML_LOCAL_LINK")
                elif parts.fragment and destination.suffix == ".html":
                    if f'id="{urllib.parse.unquote(parts.fragment)}"' not in read_bytes(destination).decode("utf-8"):
                        failures.append("AUTHORED_HTML_ANCHOR")
            html_links += 1
    png_checks = 0
    if decode_images:
        from PIL import Image
        for attachment in manifest["attachments"]:
            if attachment["git_path"].lower().endswith(".png"):
                with Image.open(child(root, attachment["local_path"])) as image:
                    image.verify()
                png_checks += 1
    if not page_citations.issubset(pages):
        failures.append("UNKNOWN_PAGE_CITATION")
    if manifest["synthesis"]["status"] != "ASSEMBLED_SUPPLIED_NOTES_REQUIRES_REVIEW":
        failures.append("SYNTHESIS_STATE")
    if list(root.rglob(".writing-*")) or list(root.rglob(".download-*")):
        failures.append("INCOMPLETE_LOCAL_WRITES")
    result = {
        "verified_at_utc": collector.utc_now(), "result": "FAIL" if failures else "PASS",
        "page_notes_verified": len(notes), "nonempty_pages_with_notes": sum(page["bytes"] > 0 for page in pages.values()),
        "empty_pages_accounted": sum(page["bytes"] == 0 for page in pages.values()),
        "attachment_dispositions_verified": len(reviews), "png_integrity_checks": png_checks,
        "png_decoding": "SELECTED" if decode_images else "NOT_RUN",
        "derived_artifacts_verified": len(artifacts), "authored_documents_checked": len(authored),
        "local_markdown_links_checked": checked_links, "authored_html_links_checked": html_links,
        "distinct_page_citations": len(page_citations), "external_links_not_requested": external_links,
        "source_export_coverage": manifest["coverage_status"], "semantic_accuracy": "NOT_ASSESSED",
        "publication_authorized": False, "network_requests": 0, "source_code_executed": False,
        "failure_counts": dict(Counter(failures)),
    }
    if receipt:
        write_json(root, child(root, "corpus-verification.json"), result)
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True)
    parser.add_argument("--receipt", action="store_true")
    parser.add_argument("--decode-images", action="store_true", help="Optional Pillow PNG integrity checks; not visual review.")
    args = parser.parse_args(argv)
    return verify(args.root, receipt=args.receipt, decode_images=args.decode_images)


if __name__ == "__main__":
    collector.run_cli(main)
