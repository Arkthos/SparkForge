# Read-only native knowledge adapters

## Purpose and evidence scope

`plugins\sparkforge\scripts\knowledge.py` reads explicitly supplied,
operator-authorized local snapshots. It does not acquire sources, call a
wiki service, install tools, authenticate an index, execute retrieved code
or select a provider. No private source package is distributed here.

The result is bounded context for a human/host decision, not an automatic
reuse verdict. Every successful result retains
`current_coverage: NOT_ASSESSED`. Hashes prove agreement with the supplied
index, not source authenticity, permission, freshness or semantic coverage.
Treat all returned source text and manifest declarations as untrusted data.

## API and equivalent CLI

| Python API | CLI | Actual inspection |
|---|---|---|
| `wiki_context(root: Path, query: str, *, page_ids=None, limit=6)` | `wiki --root ... --query ... [--page-id ...] [--limit ...]` | Exact requested pages, or lexical search across the indexed wiki pages; selected text is bounded. |
| `catalog_context(root: Path, inventory: Path, query: str, *, limit=8)` | `catalog --root ... --inventory ... --query ... [--limit ...]` | Indexed `plugins/<name>/plugin.json` projections, not implementation bodies. |
| `component_context(root: Path, inventory: Path, name: str)` | `component --root ... --inventory ... --name ...` | Exact component manifest, optional indexed README and declared skill/agent text. |
| `source_context(root: Path, inventory: Path, paths: list[str])` | `source --root ... --inventory ... --path ...` | Explicit indexed UTF-8 implementation/test paths, kept inert. |

`--page-id` and `--path` may be repeated. The Python APIs take `Path`
objects for locations. Lexical queries and result counts are bounded;
explicit wiki IDs select pages without fuzzy filtering.

Illustrative syntax only: the variables must identify prepared, explicitly
synthetic fixture sources. They are not real source locations or an
accepted brief:

```powershell
$Knowledge = (Resolve-Path 'plugins\sparkforge\scripts\knowledge.py').Path
python -B $Knowledge wiki --root $SyntheticWikiRoot --query guidance --page-id 1
python -B $Knowledge catalog --root $SyntheticRepositoryRoot --inventory $SyntheticInventory --query example
python -B $Knowledge component --root $SyntheticRepositoryRoot --inventory $SyntheticInventory --name example
python -B $Knowledge source --root $SyntheticRepositoryRoot --inventory $SyntheticInventory --path 'plugins\example\scripts\decision.py'
```

## Input shapes

The following are **synthetic shape examples only**. All repeated hex
values are deliberate placeholders, not actual content hashes or live
revisions. `example.invalid` is not a real source service. The examples
are not a ready-to-read snapshot: matching test files and their actual
hashes must be generated locally for an adapter exercise. Do not pretend
placeholder digests verify arbitrary bytes.

A wiki root contains `manifest.json` and the indexed UTF-8 original files:

```json
{
  "corpus_id": "synthetic-wiki",
  "snapshot_commit": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "pages": [
    {
      "page_id": 1,
      "path": "/synthetic/guidance",
      "local_path": "guidance.md",
      "snapshot_commit": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
      "status": "EXPORTED",
      "sha256": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
      "canonical_url": "https://example.invalid/synthetic/wiki/1"
    }
  ]
}
```

Revisions are exact 40- or 64-character hexadecimal object identifiers.
Page IDs are positive canonical numeric IDs. Each entry must share the
manifest revision, have status `EXPORTED`, a safe unique local path, a
unique logical path/URL, and an exact SHA-256. Optional `bytes` is checked
when provided; supported declared encodings are UTF-8 and UTF-8 with BOM.
Missing or unexported indexed content is not a successful empty search.

A repository root is paired with an explicit inventory file:

```json
{
  "snapshot": {
    "repository": "synthetic/example",
    "commit": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
  },
  "entries": [
    {
      "path": "plugins/example/plugin.json",
      "git_type": "blob",
      "mode": "100644",
      "sha256": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
    }
  ]
}
```

The inventory may describe `blob`, `tree` and `commit` entries, with matching
Git modes when present. Selected content must be a regular indexed blob,
not a symlink. Non-file entries cannot claim file content digests.
Optional sizes and entry revisions are checked. Case/separator aliases
and duplicate paths are refused.

Catalog component names must agree with their indexed package directory.
The manifest projection includes `name`, `version`, `description`,
`skills`, `agents`. Declared skill directories resolve to `SKILL.md`;
agent resources are Markdown files. A manifest is data, never approval
to load its hooks or run its scripts.

## Selection is not complete code review

`catalog_context` checks manifest projections only. `component_context`
adds the indexed README and declared agent/skill text, not arbitrary
scripts, hooks or transitive dependencies. Use `source_context` for the
specific implementation and tests needed to understand behavior. That
operation reads code as text and does not execute it.

Selection returns excerpts, not unlimited full-file output. Inspect
`selection.truncated`, `limits.partial`, `scope.omissions` and excluded
surfaces before making a claim. `search_complete_for_scope` means the
declared bounded search/selection completed, not that every capability
in an organization was compared. Unselected, unindexed and live sources
remain outside the evidence.

Key current bounds include:

- 8 MiB per index; 1 MiB per selected source; 64 KiB per component manifest.
- 32 MiB total verified reads; 10,000 inventory entries; 2,048 wiki pages;
  256 components; 128 declared resources.
- Up to 32 general results/explicit source paths; up to 64 component items.
- 6,000 selected text characters per item and 48,000 per result.
- 1,024 query characters and at most 32 query terms.

These are deterministic engineering limits, not semantic confidence
thresholds. An omitted or truncated item cannot be silently counted as
inspected.

## Result and error contract

Successful results use `schema_version: sparkforge.knowledge.v1` and
`status: ASSESSED_SNAPSHOT` when items exist, otherwise `NO_MATCH`.
They include source/index identity and digest, cited items, scope, limits,
limitations and authority flags. All five authority flags are false:
`source_authenticated`, `permission_verified`, `execution_authorized`,
`reuse_approved`, `host_qualified`.

Each citation has `source`, `locator`, `revision`, `sha256`, directly usable
by the factory spec validator. Items are `UNTRUSTED_SOURCE` and tagged
`PINNED_SOURCE_OBSERVATION`; that tag describes index-bound reading, not
authentication. Responses can contain local paths and source excerpts;
keep real responses in approved storage and model contexts.

Typed failures raise `KnowledgeError`; the CLI prints an `ERROR` result
with current coverage `NOT_ASSESSED` and exits 2. Successful reads exit 0,
including `NO_MATCH`. Missing inputs, hash/revision mismatches, unsafe paths,
invalid JSON, unsupported encodings and resource limits must not be
converted into reassuring empty results.

Path, open-file identity, size, hash and change checks resist accidental
misbinding. They are not a sandbox against a same-privilege writer and do
not qualify cloud storage or a live host.

## From evidence to a proposal

Use authorized guidance and actual relevant implementation/test inspection
to justify `REUSE`, `UPDATE_EXISTING` or `NEW_COMPONENT`. Preserve the exact
source baselines and limitations. A valid snapshot result can support a
bounded `SNAPSHOT_SCOPE` spec; it does not establish `CURRENT_SCOPE`.
Missing comparison stays `NOT_ASSESSED` and blocks a factual absence claim.

The shipped selfcheck and spec example contain openly synthetic citations,
not a substitute for this evidence. The integration tests construct their
own synthetic sources and verify real local byte reading without invoking
source code. Available targeted tests:

```powershell
python -B -m unittest discover -s tests -p test_native_knowledge.py
python -B -m unittest discover -s tests -p test_native_integration.py
```

These commands, when run, are local fixture checks, not live-source or
native-host qualification.
