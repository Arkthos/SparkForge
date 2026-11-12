"""Reconcile references in an explicitly selected local corpus; never fetch new items."""

import argparse
import time

from .._common import child, read_json, root_path, unique_records, write_json
from . import collect_wiki as collector


def reindex(root):
    root = root_path(root)
    manifest, snapshot = read_json(child(root, "manifest.json")), read_json(child(root, "snapshot.json"))
    collector.verify_sources(root, manifest, snapshot)
    backing = unique_records(read_json(child(root, "backing-items.json"))["items"], "path")
    parser = collector.markdown_parser()
    previous_references = manifest["references"]
    attachments = unique_records(manifest["attachments"], "git_path")
    manifest["references"], manifest["unparsed_attachment_markers"] = [], []
    for page in manifest["pages"]:
        text, _ = collector.source_text(root, child(root, page["local_path"]))
        references, unresolved = collector.extract_references(text, parser)
        for reference in references:
            target = reference["target"]
            reference.update(
                source_page_key=page["key"], source_page_id=page["page_id"],
                key=collector.identifier("reference", page["key"] + "\0" + target),
            )
            try:
                reference.update(collector.classify_reference(target, page, snapshot, manifest["pages"], backing))
            except ValueError:
                reference.update(kind="INVALID_REFERENCE", status="NOT_FETCHED")
            if reference["kind"] == "WIKI_ATTACHMENT":
                collector.require(reference["git_path"] in attachments, "NEW_ATTACHMENT_REQUIRES_SEPARATE_COLLECTION")
                attachment = attachments[reference["git_path"]]
                reference.update(attachment_key=attachment["key"], status=attachment["status"])
            manifest["references"].append(reference)
        for marker in unresolved:
            marker["source_page_key"] = page["key"]
        manifest["unparsed_attachment_markers"].extend(unresolved)
        page.update(reference_count=len(references), reference_scan_status="PARSED")
    for attachment in manifest["attachments"]:
        references = [ref for ref in manifest["references"] if ref.get("attachment_key") == attachment["key"]]
        collector.require(references, "ATTACHMENT_WITHOUT_REFERENCE")
        attachment["reference_keys"] = [ref["key"] for ref in references]
        attachment["source_page_keys"] = sorted({ref["source_page_key"] for ref in references})
    manifest["local_reference_refinement"] = {
        "performed_at_utc": collector.utc_now(), "network_requests": 0,
        "method": "Reparse verified local source with the current reference classifier; no source refresh.",
    }
    manifest["coverage_status"] = collector.coverage_status(manifest)
    write_json(root, child(root, f"attempts/reference-index-{time.time_ns()}.json"), {"references": previous_references})
    collector.checkpoint(root, manifest)
    collector.render_corpus(root, manifest, snapshot)
    return {"result": "PASS", "reference_reindex": "PASS", "counts": manifest["counts"], "network_requests": 0}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, help="Explicit input/output corpus; manifest and local views are regenerated.")
    return reindex(parser.parse_args(argv).root)


if __name__ == "__main__":
    collector.run_cli(main)
