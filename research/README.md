# Public-source research library

**Publication edition:** 2026-11-12. **Research baselines:** 2026-11-04 and
2026-11-05, as identified by each collection.

This library contains original public-source synthesis, synthetic teaching
examples, and public bibliographic metadata. It is not an export of a private
knowledge system, a source-code mirror, or a record of live framework
qualification. It supplies no live wiki access.

## What is included

| Collection | Contents | Evidence boundary |
|---|---|---|
| [AI factory and harness engineering](ai-factory/README.md) | 21 chapters, one index, six unfilled templates, and 49 public source entries | Preserves the 2026-11-04 authored research; proposed labs and the worked scenario were not executed |
| [Prior-art mechanisms and detailed dossier](prior-art/dossier/README.md) | Fourteen detailed topical counterparts, introductory reference, all 33 pinned repositories and 90 inspections, primary-source/video analysis, and discovery leads | Explicit document-by-document exclusions; historical selected reading, not new installation, execution, whole-repository audit, or private-source publication |
| [Self-improvement](../docs/research/SELF_IMPROVEMENT.md) | Fresh account of the Eric Tech video and the separately supplied Fluent repository | Historical review scope is explicit; proposed learning is not measured improvement or self-approval |

Use the factory collection for concepts, tradeoffs, exercises, and source
literacy. Use prior art to locate existing mechanisms before inventing another
implementation. Use self-improvement to distinguish observations, inactive
proposals, evaluation, and independently authorized promotion.

The enclosing project's living records own current implementation status.
Phrases such as "our later design," "not implemented," and "no framework
selected" inside the dated factory collection describe its research baseline,
not the current state of SparkForge.

## Selection and editorial record

For the initial 2026-11-11 factory selection, all 28 original factory Markdown
files and its public source catalog were read. Their 29 content hashes matched the original manifest.
The six templates remain unfilled. No source article, raw transcript, frame,
image, archive, or executable resource was imported.

Sixteen of those 29 content files are unchanged byte-for-byte, including the
public source catalog. Four Markdown files have the following limited
publication annotations and portability edits:

| File | Change and reason |
|---|---|
| [Factory index](ai-factory/README.md) | Adds the publication notice; scopes implementation statements to the historical study; replaces collection-local storage and excluded-folder references with portable publication boundaries |
| [Security and governance](ai-factory/08-security-and-governance.md) | Replaces the original storage-folder example with an explicit warning against adding runtime data to the published documentation |
| [Reference architecture](ai-factory/12-reference-architecture-and-decisions.md) | Labels the proposed design's historical status and makes the Windows workspace paragraph portable |
| [Evidence map](ai-factory/17-evidence-map-and-open-questions.md) | Replaces a collection-specific excluded-wiki name with the general boundary: no private wiki ingestion or live access |

**Formatting-only correction, 2026-11-11:** integration identified 45
two-space Markdown hard breaks that violated the normal trailing-whitespace
check. Those breaks now use explicit `<br>` elements outside code fences.
Wording, line-break meaning, and authored CRLF line endings are preserved.
No whitespace rule was disabled or weakened.

| Factory file | Hard breaks replaced |
|---|---:|
| `16-sources-and-reading-guide.md` | 4 |
| `18-worked-factory-scenario.md` | 4 |
| `20-eric-risco-video-review.md` | 5 |
| `README.md` | 2 |
| `templates/architecture-decision-record.md` | 7 |
| `templates/evaluation-plan.md` | 5 |
| `templates/harness-and-task-contract.md` | 3 |
| `templates/incident-and-learning-review.md` | 9 |
| `templates/release-evidence-record.md` | 3 |
| `templates/use-case-charter.md` | 3 |

These ten formatting-only edits overlap the earlier factory-index edit, so
13 original Markdown files differ in this edition. The manifests distinguish
formatting from portability, preserve pre-correction hashes and earlier check
results, and bind the current bytes. Originals were not edited.

These are publication annotations and portability changes to reviewed
public-source writing, not declassification by removing names. The initial
prior-art reference used public identities, pins, license observations, and
bounded findings without copying the contextualized original dossier.

**Detailed prior-art expansion, 2026-11-12:** all 14 original document topics
now have [detailed publication counterparts](prior-art/dossier/README.md).
They preserve the public analysis and tradeoffs rather than replacing the
research with the introductory reference. The
[disposition ledger](prior-art/dossier/document-dispositions.json) accounts
for every original, names the retained public topics and precise categories
withheld, and binds each new counterpart's bytes.

The expansion includes the full 33-candidate analysis, all 90 historical
inspection coordinates and notes, industrial/standards sources, all six
registry results, seven additional leads, the Risco transcript-topic revisit,
and the detailed ZazenCodes timestamp/version/artifact analysis. It adds no
source capture, transcript, screenshot, private operating fact, or new
framework execution. Restricted comparisons are withheld, not transplanted
under different organization names. The complete mixed-context original is
therefore **not** published, and no private-content clearance is claimed.

The [factory manifest](ai-factory/corpus-manifest.json) records original and
published hashes, identifies changed files, and separates the original
2026-11-04 checks from publication checks. The
[publication inventory](publication-manifest.json) binds all files in this
research edition, including the two self-improvement documents. Each manifest
excludes itself from its own hash list; the outer inventory includes the
factory manifest.

The [prior manifest](publication-history/PUB-20261111-library.json) is
retained byte-for-byte as an immutable historical snapshot. Existing check
objects and formatting-correction records in the current inventory remain
unchanged; the new edition adds separately dated results instead of claiming
the earlier 36-file checks validated the larger library.

## What is excluded

- Private knowledge exports, restricted contextualized documents, and
  confidential derived comparisons.
- Private Git history, runtime journals, databases, checkpoints, model
  conversations, and operator session material.
- Third-party source-code copies, full article caches, raw captions, video,
  images, screenshots, and mixed archives.
- Dependency installations, model calls, framework runs, provider changes,
  automatic learning promotion, and external publication operations.

Public availability is not a redistribution license. The cited material
retains its own terms. Repository root-license observations do not cover every
file, dependency, asset, service, trademark, or model. This research does not
assign a license to the whole SparkForge project.

## Evidence and freshness

The prior-art catalog preserves observed public visibility and pinned commit
identities from existing public-source metadata. The publication pass checked
those identities against that metadata; it did not query GitHub again.
Historical review ranges identify what the earlier review inspected, not what
was newly executed or independently reproduced for this publication.

The video reviews preserve the original dates and access limitations. No raw
captions or frames accompany them. Documentation claims, source inspection,
test-source reading, actual execution, and production acceptance are different
levels of evidence.

No external URL availability, current upstream behavior, deployment
compatibility, benchmark result, source redistribution clearance, or real
learning gain was newly established. Refresh the relevant primary source and
qualify the selected version before an adoption decision.

## Local validation

The following standard-library-only PowerShell recipe checks this edition
from the repository root. It does not fetch URLs, run research examples, call
models, or execute source tools. It checks inventory membership and hashes,
JSON syntax, inline Markdown file/anchor links, JSON examples, source-ID
consistency, the complete dossier dispositions/catalog/register, and trailing
spaces/tabs. It is a bounded documentation check,
not a complete Markdown renderer, legal assessment, or secret scanner.

```powershell
@'
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import quote, unquote, urlsplit

root = Path.cwd().resolve()
inventory = root / "research" / "publication-manifest.json"
manifest_text = inventory.read_text(encoding="utf-8")
assert not re.search(r"[ \t]+$", manifest_text, re.M), "Manifest trailing whitespace"
manifest = json.loads(manifest_text)
records = manifest["files"]
expected = {entry["relative_path"] for entry in records}
assert len(expected) == len(records), "Duplicate inventory entry"
actual = {
    path.relative_to(root).as_posix()
    for path in (root / "research").rglob("*") if path.is_file()
}
actual.update({
    "docs/research/SELF_IMPROVEMENT.md",
    "docs/research/self-improvement-sources.json",
})
assert actual == expected | {"research/publication-manifest.json"}, "Inventory differs"
pages = {}
json_count = 1
for entry in records:
    path = root / entry["relative_path"]
    assert not path.is_symlink() and path.resolve().is_relative_to(root), entry
    raw = path.read_bytes()
    assert len(raw) == entry["bytes"], entry
    assert hashlib.sha256(raw).hexdigest() == entry["sha256"], entry
    text = raw.decode("utf-8").replace("\r\n", "\n")
    assert not re.search(r"[ \t]+$", text, re.M), (path, "Trailing whitespace")
    if path.suffix == ".json":
        json.loads(text)
        json_count += 1
    elif path.suffix == ".md":
        pages[path.resolve()] = text
    else:
        raise AssertionError(f"Unexpected file type: {path.name}")

def without_fences(text):
    return re.sub(r"(?ms)^```[^\n]*\n.*?^```[ \t]*$", "", text)

def anchors(text):
    text = without_fences(text)
    found = set(re.findall(r'<a\s+id="([^"]+)"', text))
    seen = {}
    for title in re.findall(r"^#{1,6}\s+(.+)$", text, re.M):
        title = re.sub(r"\[([^]]+)\]\([^)]+\)", r"\1", title)
        slug = re.sub(r"[^\w -]", "", title.lower()).replace(" ", "-")
        n = seen.get(slug, 0)
        seen[slug] = n + 1
        found.add(slug if n == 0 else f"{slug}-{n}")
    return found

local_links = 0
examples = 0
for path, text in pages.items():
    assert len(re.findall(r"^```", text, re.M)) % 2 == 0, path
    for body in re.findall(r"(?ms)^```json[ \t]*\n(.*?)^```[ \t]*$", text):
        json.loads(body)
        examples += 1
    for link in re.findall(r"\[[^]]+\]\(([^)]+)\)", without_fences(text)):
        parsed = urlsplit(link)
        if parsed.scheme or parsed.netloc:
            continue
        target = (path.parent / unquote(parsed.path)).resolve() if parsed.path else path
        assert target.is_relative_to(root) and target.is_file(), (path, link)
        if parsed.fragment:
            assert target in pages and unquote(parsed.fragment) in anchors(pages[target]), (path, link)
        local_links += 1

factory = root / "research" / "ai-factory"
sources = json.loads((factory / "sources.json").read_text(encoding="utf-8"))
ids = [entry["id"] for entry in sources["sources"]]
assert len(ids) == len(set(ids)) == 49
guide = pages[(factory / "16-sources-and-reading-guide.md").resolve()]
assert {value.lower() for value in ids} <= anchors(guide)
citations = 0
for path, text in pages.items():
    if path.is_relative_to(factory):
        refs = re.findall(r"\[(S\d{2})\]\(", text)
        assert set(refs) <= set(ids), path
        citations += len(refs)

dossier = root / "research" / "prior-art" / "dossier"
dispositions = json.loads((dossier / "document-dispositions.json").read_text(encoding="utf-8"))
original_names = {
    "README.md", "SCOPE.md", "REUSE_MAP.md", "SPECIFICATIONS_AND_INTAKE.md",
    "FACTORY_PATTERNS.md", "QUALITY_AND_EVALUATION.md",
    "KNOWLEDGE_AND_GOVERNANCE.md", "COMPATIBILITY_AND_LICENSING.md",
    "INDUSTRY_AND_THEORY.md", "DISCOVERY_APPENDIX.md",
    "COVERAGE_AND_VALIDATION.md", "CATALOG.md", "EVIDENCE.md",
    "VIDEO_ZAZEN_FACTORY.md",
}
documents = dispositions["documents"]
assert len(documents) == 14
assert {d["source_document"] for d in documents} == original_names
assert {d["publication_document"] for d in documents} == original_names
assert {p.name for p in dossier.glob("*.md")} == original_names
for doc in documents:
    path = dossier / doc["publication_document"]
    raw = path.read_bytes()
    assert len(raw) == doc["publication_bytes"], doc
    assert hashlib.sha256(raw).hexdigest() == doc["publication_sha256"], doc
    assert doc["retained_public_topics"] and doc["withheld_material"], doc
assert dispositions["complete_original_dossier_reproduced"] is False
assert dispositions["private_content_publication_permission_established"] is False
assert dispositions["upstream_source_captures_included"] is False
assert dispositions["raw_transcripts_images_or_session_records_included"] is False

public = json.loads((dossier.parent / "sources.json").read_text(encoding="utf-8"))
analysis = json.loads((dossier / "catalog-analysis.json").read_text(encoding="utf-8"))
repositories = public["repositories"]
repository_ids = {r["id"] for r in repositories}
candidate_ids = {c["id"] for c in analysis["candidates"]}
assert len(repositories) == len(repository_ids) == len(analysis["candidates"]) == 33
assert candidate_ids == repository_ids
inspection_ids = set()
focused_ids = set()
reviewed_lines = {}
catalog = pages[(dossier / "CATALOG.md").resolve()]
register = pages[(dossier / "EVIDENCE.md").resolve()]
assert set(re.findall(r"^## (.+)$", catalog, re.M)) == repository_ids
for repo in repositories:
    assert repo["visibility_at_observation"] == "public", repo["id"]
    assert re.fullmatch(r"[0-9a-f]{40}", repo["commit"]), repo["id"]
    for entry in repo["historical_inspections"]:
        assert entry["id"] not in inspection_ids, entry["id"]
        inspection_ids.add(entry["id"])
        if entry["id"] != repo["id"] + "-overview":
            focused_ids.add(entry["id"])
        expected_url = f'https://github.com/{repo["repository"]}/blob/{repo["commit"]}/{quote(entry["path"], safe="/")}'
        assert entry["source_url"] == expected_url, entry["id"]
        assert re.fullmatch(r"[0-9a-f]{64}", entry["source_sha256_at_historical_review"])
        assert re.fullmatch(r"[0-9a-f]{40}", entry["git_blob"])
        key = (repo["id"], entry["path"])
        reviewed_lines.setdefault(key, set())
        for start, end in entry["historical_reviewed_line_ranges"]:
            assert 1 <= start <= end, entry["id"]
            reviewed_lines[key].update(range(start, end + 1))
            assert f'{entry["source_url"]}#L{start}-L{end}' in register, entry["id"]
assert len(inspection_ids) == 90 and len(reviewed_lines) == 88
assert sum(map(len, reviewed_lines.values())) == 10471
assert focused_ids == set(analysis["focused_inspection_notes"])
assert set(re.findall(r"^## (.+)$", register, re.M)) == inspection_ids | {"zazen-video"}
for text in analysis["focused_inspection_notes"].values():
    assert text in register
for candidate in analysis["candidates"]:
    assert candidate["description"] in catalog, candidate["id"]
    assert candidate["reusable_contribution"] in catalog, candidate["id"]
    assert all(value in catalog for value in candidate["conditions"]), candidate["id"]

context = json.loads((dossier / "public-context-sources.json").read_text(encoding="utf-8"))
assert len(context["primary_sources"]) == 6
assert len(context["registry_discovery"]["results"]) == 6
assert len(context["additional_leads"]) == 7
videos = {v["id"]: v for v in context["videos"]}
assert len(videos) == len(context["videos"]) == 2
video_page = pages[(dossier / "VIDEO_ZAZEN_FACTORY.md").resolve()]
video_times = {int(v) for v in re.findall(r"\?v=ctoaIC4LHmI&t=(\d+)s", video_page)}
assert video_times == {v["seconds"] for v in videos["ctoaIC4LHmI"]["timestamp_topics"]}
assert len(video_times) == 21
scope_page = pages[(dossier / "SCOPE.md").resolve()]
assert len(videos["p6nnqerea7w"]["timestamp_topics"]) == 7
assert all(v["range"] in scope_page for v in videos["p6nnqerea7w"]["timestamp_topics"])
assert all(v["raw_captions_frames_or_media_included"] is False for v in videos.values())
discovery_urls = {r["url"] for r in context["registry_discovery"]["results"]}
by_repository = {r["repository"].lower(): r for r in repositories}
pinned_links = 0
for path, text in pages.items():
    if not path.is_relative_to(dossier):
        continue
    for url in re.findall(r"\[[^]]+\]\((https://github\.com/[^)]+)\)", text):
        if url in discovery_urls:
            continue
        parts = urlsplit(url).path.strip("/").split("/")
        if len(parts) >= 4 and parts[2] in {"blob", "tree", "commit"}:
            repo = by_repository["/".join(parts[:2]).lower()]
            assert parts[3] == repo["commit"], (path, url)
            pinned_links += 1

previous = root / "research" / "publication-history" / "PUB-20261111-library.json"
assert hashlib.sha256(previous.read_bytes()).hexdigest() == "d9f1d2c4be76836d1791068d5bf1f7abcbaea6367474ec767a87cbb0ec2940dd"
historical = json.loads(previous.read_text(encoding="utf-8"))
for key in ("checks", "validation_history", "publication_corrections"):
    assert manifest[key] == historical[key], ("Historical record altered", key)
print(json.dumps({
    "result": "PASS", "published_files": len(actual),
    "hashed_content_files": len(records), "markdown_files": len(pages),
    "json_files": json_count, "local_links": local_links,
    "json_examples": examples, "factory_source_citations": citations,
    "dossier_documents": len(documents), "prior_art_candidates": len(repository_ids),
    "prior_art_inspections": len(inspection_ids), "dossier_pinned_links": pinned_links,
    "discovery_results": 6, "additional_leads": 7,
    "video_timestamp_topics": len(video_times),
    "historical_check_records_preserved": True,
    "trailing_whitespace_findings": 0,
}, sort_keys=True))
'@ | python -B -
```

The inventory records the observed publication checks. Its historical checks
are not silently relabeled as new results. Passing this recipe establishes
only the enumerated local properties; it does not certify external sources,
proposed laboratories, product behavior, host acceptance, or publication on
GitHub.
