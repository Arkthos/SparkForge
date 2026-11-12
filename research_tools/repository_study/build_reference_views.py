"""Generate source references, skill navigation and explicit per-file review depth."""

import argparse
from collections import Counter

from .._common import child, read_json, root_path, safe_main, unique_records, write_json, write_text
from .catalog_source import write_csv
from .inventory_source import load_inventory


def cell(value):
    return str(value).replace("|", "\\|").replace("\n", " ")


def build(root):
    root = root_path(root)
    inventory, _, entries = load_inventory(root)

    def load(name):
        return read_json(child(root, "evidence/" + name))

    catalog, references = load("catalog.json"), load("references.json")
    notes = load("skill-summaries.json")["skills"]
    commit = inventory["snapshot"]["commit"]
    if commit != references["commit"] or commit != catalog["commit"]:
        raise ValueError("Mixed source revisions")
    unique_records(references["references"], "id")
    expected_notes = {f"{row['plugin']}/{row['name']}" for row in catalog["skills"]}
    if set(notes) != expected_notes:
        raise ValueError("Skill notes differ from declarations")
    lines = [
        "# Immutable source references", "",
        f"Primary references bind to `{commit}` in the explicitly selected repository.",
        "Access restrictions still apply. Registered ranges do not establish full semantic review or execution.", "",
    ]
    reviewed, resolved = {}, []
    for ref in references["references"]:
        entry = entries[ref["path"]]
        start, end = ref["start"], entry["line_count"] if ref["end"] is None else ref["end"]
        if type(start) is not int or type(end) is not int or not 1 <= start <= end <= entry["line_count"]:
            raise ValueError("Invalid source range")
        url = entry["source_url"] + f"#L{start}-L{end}"
        lines += [
            f"## {ref['id']}", "", f"**{ref['title']}**", f"Evidence class: {ref['kind']}.", "",
            f"[`{ref['path']}:L{start}-L{end}`]({url})", "",
        ]
        reviewed.setdefault(ref["path"], []).append(f"{start}-{end}")
        resolved.append({**ref, "end": end, "url": url})
    source_document = "\n".join(lines)
    lines = [
        "# Complete declared skill catalog", "",
        f"**{len(catalog['skills'])} declared skills at `{commit}`.**",
        "Input hints and intended outputs are declarations or supplied notes, not tested runtime contracts.", "",
    ]
    for plugin in catalog["plugins"]:
        selected = [row for row in catalog["skills"] if row["plugin"] == plugin["name"]]
        lines += [
            f"## {plugin['name']}", "", f"Version `{plugin['version']}`; {len(selected)} declared skills.", "",
        ]
        if not selected:
            lines += ["No skills are declared by this package.", ""]
            continue
        lines += ["| Skill and pinned contract | Purpose | Declared input hint | Intended output |", "|---|---|---|---|"]
        for skill in selected:
            purpose, output = notes[f"{skill['plugin']}/{skill['name']}"]
            hint = skill["declared_inputs"] or "No frontmatter input hint."
            lines.append(
                f"| [`{skill['name']}`]({skill['source']['url']}) | {cell(purpose)} | {cell(hint)} | {cell(output)} |"
            )
        lines.append("")
    structural = {row["path"] for group in ("skills", "agents", "scripts", "queries") for row in catalog[group]}
    structural |= {row["path"] for row in entries.values() if row["git_type"] == "blob" and row["extension"] == ".json"}
    assets = load("asset-classification.json")["assets"]
    unique_records(assets, "path")
    if any(row["path"] not in entries for row in assets):
        raise ValueError("Unknown asset classification")
    binary = {row["path"] for row in assets if row["inspection"] == "container_or_header_only"}
    coverage = []
    for row in entries.values():
        if row["git_type"] == "tree":
            continue
        path = row["path"]
        depth = (
            "selected_range_semantic_review" if path in reviewed else
            "container_or_header_only" if path in binary else
            "structural_only" if path in structural else "inventory_only"
        )
        coverage.append({
            "path": path, "surface": row["surface"], "depth": depth,
            "structural_extraction": path in structural,
            "reviewed_ranges": ";".join(reviewed.get(path, [])), "sha256": row["sha256"],
        })
    summary = {
        "commit": commit, "total_inventoried_files": len(coverage),
        "structurally_extracted_files_overlapping_review": len(structural),
        "selected_range_reviewed_files": len(reviewed), "source_reference_count": len(resolved),
        "exclusive_depth_counts": dict(sorted(Counter(row["depth"] for row in coverage).items())),
        "caution": "Registered notes and selected ranges are not independent review or live validation.",
    }
    write_text(root, child(root, "SOURCES.md"), source_document)
    write_text(root, child(root, "SKILLS.md"), "\n".join(lines))
    write_json(root, child(root, "evidence/resolved-references.json"), {"commit": commit, "references": resolved})
    write_csv(root, "coverage.csv", coverage, ["path", "surface", "depth", "structural_extraction", "reviewed_ranges", "sha256"])
    write_json(root, child(root, "evidence/coverage-summary.json"), summary)
    return {"status": "BUILT", "files_accounted": len(coverage), "references": len(resolved), "network_requests": 0}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, help="Explicit corpus input/output root.")
    return build(parser.parse_args(argv).root)


if __name__ == "__main__":
    safe_main(main)
