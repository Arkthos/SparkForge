# Public-source research library

**Publication edition:** 2026-11-11. **Research baselines:** 2026-11-04 and
2026-11-05, as identified by each collection.

This library contains original public-source synthesis, synthetic teaching
examples, and public bibliographic metadata. It is not an export of a private
knowledge system, a source-code mirror, or a record of live framework
qualification. It supplies no live wiki access.

## What is included

| Collection | Contents | Evidence boundary |
|---|---|---|
| [AI factory and harness engineering](ai-factory/README.md) | 21 chapters, one index, six unfilled templates, and 49 public source entries | Preserves the 2026-11-04 authored research; proposed labs and the worked scenario were not executed |
| [Prior-art mechanisms and reuse reference](prior-art/README.md) | Fresh source-neutral synthesis and 33 pinned public repository references | Historical documentation and selected source-reading findings; not installation, execution, or a whole-repository audit |
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

All 28 original factory Markdown files and its public source catalog were
read before selection. Their 29 content hashes matched the original manifest.
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
public-source writing, not declassification by removing names. The
contextualized prior-art dossier was **not copied or redacted into this
repository**. Its public repository identities, pins, license observations,
and bounded public-source findings were used to write a new reference.
Private comparisons and historical local artifact paths are not evidence here.

The [factory manifest](ai-factory/corpus-manifest.json) records original and
published hashes, identifies changed files, and separates the original
2026-11-04 checks from publication checks. The
[publication inventory](publication-manifest.json) binds all files in this
research edition, including the two self-improvement documents. Each manifest
excludes itself from its own hash list; the outer inventory includes the
factory manifest.

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
consistency, and trailing spaces/tabs. It is a bounded documentation check,
not a complete Markdown renderer, legal assessment, or secret scanner.

```powershell
@'
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import unquote, urlsplit

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
print(json.dumps({
    "result": "PASS", "published_files": len(actual),
    "hashed_content_files": len(records), "markdown_files": len(pages),
    "json_files": json_count, "local_links": local_links,
    "json_examples": examples, "factory_source_citations": citations,
    "trailing_whitespace_findings": 0,
}, sort_keys=True))
'@ | python -B -
```

The inventory records the observed publication checks. Its historical checks
are not silently relabeled as new results. Passing this recipe establishes
only the enumerated local properties; it does not certify external sources,
proposed laboratories, product behavior, host acceptance, or publication on
GitHub.
