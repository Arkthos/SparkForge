# Portable research utilities

This directory accounts for **all 19 selected project-authored source files**:
15 utility scripts, three synthetic test files and one requirements file.
It includes the previously separate public-repository, source-repository, wiki
and checkpoint tooling. It does **not** contain their acquired source corpora,
archives, private manifests, credentials, historical receipts or vendor caches.

[SOURCE_COVERAGE.json](SOURCE_COVERAGE.json) maps each authored filename to its
publication path and explains adaptations. The two historical checkpoint
verifiers were **not byte-identical**. Their separate entry points now share
the stronger verification implementation; this is explicit consolidation,
not a claim of exact duplication.

## Boundaries

- Run modules from this repository's root with Python 3.12 or newer. Imports
  and `--help` do not collect data, inspect credentials, scan corpora or write
  output. There is no implicit workspace or service.
- Roots, output locations, source identity and credentials must be explicitly
  selected by the operator. Inputs and tool output are untrusted data.
- Offline verification is read-only unless `--receipt` is selected. Index,
  render, catalog, build and reindex commands write their documented outputs
  inside the explicitly selected `--root`. Use an authorized working copy,
  not an original that must remain untouched.
- Collectors perform only authenticated GETs after explicit network selection.
  They never log in, discover/switch accounts, acquire/refresh tokens, run
  installers, invoke models, execute downloaded code or publish anything.
  No collector was run against a real service for this increment.
- Wiki collection, reading-packet and checkpoint CLI destinations cannot be
  inside this code repository. This prevents a common accidental import;
  it is not a storage sandbox or a complete data-loss-prevention control.
- Local path helpers reject traversal, symbolic links and junctions. Ordinary
  cloud-synchronized files are not treated as links merely because they carry
  a filesystem reparse attribute. Selecting storage does not certify its
  synchronization, organizational authorization or confidentiality.
- Pattern matching, hashes and synthetic tests are **not source/data clearance**.
  Private source text, derived notes, image content and operational observations
  need their own review and rights before any publication. Unknown comparison
  and semantic coverage remain `NOT_ASSESSED`.

## Utility map and safe offline invocations

In the examples below, `$corpus`, `$workspace`, `$objects`, `$plan`, `$notes`,
`$selection`, `$checkpoint` and `$output` mean **explicitly selected, authorized
local inputs or new outputs**. They are not defaults supplied by these tools.
Every Python command also supports `--help` without opening its inputs.

### Public repositories

| Utility | Purpose and offline invocation | Prerequisites and effects |
|---|---|---|
| `public_repositories\collect_github.py` | `python -B -m research_tools.public_repositories.collect_github --help` | Collection itself is not offline. Requires installed `gh`, a selected repository, `--output`, `--token-env NAME` and `--allow-network`. Uses only `github.com` with that token; no credential fallback. Every mode checks current public visibility. New snapshots pin a commit and capture the root listing, README and root license files. `files` captures selected files; `list` captures selected directory listings. No repository code is executed. |
| `public_repositories\study.py` | `python -B -m research_tools.public_repositories.study verify --root $corpus --workspace $workspace` | Requires a local `research.json`, pinned `sources` metadata/files and generated views. Rechecks exact UTF-8 bytes, Git blob IDs, revisions, licenses, registered line ranges, optional video metadata/image hashes, local links and anchors. `index` writes `source-index.json`, `CATALOG.md` and `EVIDENCE.md`; verification writes nothing without `--receipt`. |
| `public_repositories\test_study.py` | `python -B -m unittest research_tools.public_repositories.test_study` | All 16 original behavioral cases retained, with owned fixture directories and explicit mocked credential selection. No candidate framework is installed or evaluated. |

`research.json` retains the original candidate/inspection schema. An optional
`required_documents` array selects the documents to check; otherwise the
original source-neutral document names remain required. Runtime-specific
acceptance keys were replaced by `runtime_acceptance: NOT_ASSESSED`.
Video transcript coverage remains a registered observation; absent caption
bytes cannot be independently rehashed.

### Local source repositories

| Utility | Purpose and offline invocation | Prerequisites and effects |
|---|---|---|
| `repository_study\inventory_source.py` | `python -B -m research_tools.repository_study.inventory_source --help` | An actual inventory additionally requires `--root`, `--git-dir`, full `--commit` and `--tree`, and `--repository-url`. Reads a self-contained **existing local** Git object store only. Lazy fetching and terminal prompts are disabled; alternate object stores are rejected. Writes inert `source` files and `evidence\inventory.json`, `inventory.csv`, `snapshot.json`. Symlinks, submodules, unsafe filenames and LFS pointers retain explicit dispositions. `--max-bytes` bounds selected blob bytes. |
| `repository_study\catalog_source.py` | `python -B -m research_tools.repository_study.catalog_source --root $corpus` | Requires the inventory, matching source bytes, plugin marketplace/CODEOWNERS, per-plugin `plugin.json` and `agency.json`. Extracts skills, agents, hooks, script definitions and query headers; parses Python/JSON without imports or execution. Writes the catalog, static checks and four CSV views under `evidence`. Unsupported ownership syntax fails for review rather than inventing an owner. |
| `repository_study\build_reference_views.py` | `python -B -m research_tools.repository_study.build_reference_views --root $corpus` | Requires `evidence\references.json`, `skill-summaries.json`, `asset-classification.json` and the catalog/inventory. Ranges and notes are explicit input, not built-in findings. Writes `SOURCES.md`, `SKILLS.md`, resolved references and per-file coverage. Counts are computed from inputs. |
| `repository_study\parse_powershell.ps1` | `pwsh -NoProfile -NonInteractive -File research_tools\repository_study\parse_powershell.ps1 -Help` | PowerShell 7. Actual parsing requires `-SourceRoot`, `-Inventory` and `-Output`; the output parent must exist. Rechecks source sizes and SHA-256, then calls the PowerShell parser on text. Does **not** invoke source scripts, hooks, profiles or power actions. Output cannot overwrite the inventory or source tree. |
| `repository_study\verify_corpus.py` | `python -B -m research_tools.repository_study.verify_corpus --root $corpus --git-dir $objects` | Reconciles the pinned tree, materialized blobs, references, declarations, hooks, CSV coverage, static checks and local links. Optional `--context-root` is required when context records exist; optional host comparison requires **both** `--host-root` and `--host-head`. Neither is inferred. `--receipt` writes the corpus file index and verification result. |

Source inventories now store `snapshot_root: source` relative to the explicit
corpus and record `repository_url`, not a private repository constant or an
absolute object-store path. Verification therefore receives `--git-dir`
separately. Visibility and observed branch stay `NOT_ASSESSED`.

Source-study `study.json` requires `primary_source.commit`. Optional
`context_source.pages` entries contain `local_path` and `sha256`, relative to
`--context-root`. Optional `recorded_checks` contain `path`, `sha256` and
`required_text`; they verify supplied receipts without executing their tests.
The old fixed test-failure strings, source counts and host baseline were removed.
Optional host comparison reads the commit, index and exact working bytes,
with filesystem monitoring disabled. It does not invoke `git status`, clean
filters or hooks. A checkout using line-ending/clean transformations may require
inspection even if Git would otherwise call it clean; submodules and tracked
symlinks remain unassessed by this exact-byte comparison.

### Wiki evidence and supplied knowledge

| Utility | Purpose and offline invocation | Prerequisites and effects |
|---|---|---|
| `wiki\collect_wiki.py` | `python -B -m research_tools.wiki.collect_wiki verify --root $corpus` | Rechecks frozen sources, hierarchy, backing objects, attachment accounting, local navigation and counts. `render` writes escaped offline views and local indexes. `verify` writes only when `--receipt` is selected. Network `prepare`/`collect` are separate phases described below. |
| `wiki\reindex_local.py` | `python -B -m research_tools.wiki.reindex_local --root $corpus` | Rechecks downloaded bytes and reparses Markdown/HTML references. A newly discovered attachment requires a separate collection; it is never fetched here. Saves the prior reference index, then updates the selected manifest and local views. Does not modify authorization fields. |
| `wiki\prepare_review.py` | `python -B -m research_tools.wiki.prepare_review --root $corpus --output $output` | New, separate local output required. Verifies every source and prepares bounded text packets, splitting long pages into indexed character ranges. Preserves source files and manifest. Attachment inventory remains `NOT_REVIEWED`; binary files are not copied or interpreted. Optional `--compact-urls` records mechanical readability changes. **This is not the publication scrubber or semantic clearance.** |
| `wiki\build_corpus.py` | `python -B -m research_tools.wiki.build_corpus --root $corpus --plan $plan --summaries $notes` | Assembles supplied, commit/hash-bound notes and taxonomy; never calls a model. Writes page/attachment coverage, source notes, a source index, knowledge views, `corpus.json` and artifact digests. Updates only assembly/validation metadata in the selected manifest, never authorization. Missing image review is not inferred from image type. |
| `wiki\verify_corpus.py` | `python -B -m research_tools.wiki.verify_corpus --root $corpus` | Rechecks source/summary/attachment bindings, generated artifact digests, Markdown/HTML links and anchors. Optional `--decode-images` performs Pillow PNG integrity checks, **not visual review**. Optional `--receipt` writes only `corpus-verification.json`; it does not approve or promote the corpus. |
| `wiki\test_collect_wiki.py` | `python -B -m unittest research_tools.wiki.test_collect_wiki` | All 17 original reference-parser cases retained with synthetic service aliases/page IDs. Requires the declared Markdown parser; no real export is read. |
| `wiki\requirements.txt` | Metadata only; no action on import/help. | Original pinned `markdown-it-py`, `mdurl` and Pillow requirements retained. Markdown parsing/rendering needs the first two. Pillow is used only for selected PNG verification. No `_deps` or vendor source is published. |

Wiki network phases require all of `--service-config`, `--token-env NAME`,
`--root` and `--allow-network`. The token must already exist in the selected
environment variable; this tool never invokes Azure CLI or requests a token.
The configured principal label is a consistency binding, **not authenticated
proof of identity or authorization**. Service aliases must be enumerated
explicitly; the tool does not infer an organization, project or alternative host.

Example **synthetic configuration shape**, not a live service:

```json
{
  "base_url": "https://service.example/Project/_apis",
  "service_urls": ["https://service.example/Project"],
  "source_url": "https://service.example/Project/_wiki/wikis/Example.wiki/1",
  "project_name": "Project",
  "wiki_id": "Example.wiki",
  "root_page_id": 1,
  "principal_label": "operator-selected-principal"
}
```

`prepare` requires an empty initial destination. `--resume` explicitly
continues a compatible incomplete frozen operation. The default is one GET
attempt; `--max-attempts 2` or `3` explicitly selects recorded transient-read
retries. No credential switching occurs. `--branch-metadata` explicitly
selects bracketed branch metadata with pinned Git reconciliation, not an
automatic fallback after failure. Content downloads require a matching Git
blob ID before being retained. HTTP redirects are not followed.

Builder inputs no longer contain a private taxonomy, page membership, image
review decisions, approval statements or completed-work counts. Both input
JSON documents require `schema_version: 1` and `source_commit` matching the
corpus. The plan supplies:

- `topics`: safe filename stems whose `topics\<stem>.md` files already exist;
- `page_topics`: every page ID, as a string, mapped to one declared topic;
- optional `authored_documents` and `media_files`, relative to the corpus;
- optional `attachment_reviews`, keyed by attachment key, containing
  `source_sha256`, `review_status` and optional `notes`.

The summaries document supplies `pages`, keyed by each **nonempty** page ID.
Each entry has `source_sha256`, nonempty `summary` and optional `review_kind`.
Empty pages are accounted for without invented summaries. Duplicate or
colliding flattened HTML filenames fail. The resulting state is
`ASSEMBLED_SUPPLIED_NOTES_REQUIRES_REVIEW`, not independent acceptance.

### Checkpoints

| Utility | Purpose and offline invocation | Prerequisites and effects |
|---|---|---|
| `checkpoints\freeze_workspace.py` | `python -B -m research_tools.checkpoints.freeze_workspace --help` | Actual creation requires explicit `--workspace`, new `--output`, `--checkpoint-id` and `--selection`. Only selected files/directories are archived. Optional `--previous-root` verifies the selected predecessor; its archive/helpers are **not automatically included or executed**. Writes a ZIP, manifest and receipt after read-back and working-file comparison. No restore, machine scan, power action or remote backup is implemented. |
| `checkpoints\verify_checkpoint.py` | `python -B -m research_tools.checkpoints.verify_checkpoint --checkpoint $checkpoint` | Later verifier entry point. Rechecks archive/member size, digest, path, duplicate and type invariants without extracting anything. Working comparison requires `--working --workspace $workspace`. Read-only; no receipt write. |
| `checkpoints\verify_checkpoint_legacy.py` | `python -B -m research_tools.checkpoints.verify_checkpoint_legacy --checkpoint $checkpoint` | Earlier verifier entry point, sharing the stronger checks above. Preserves archive-only and explicit working-comparison modes, including distinct missing/size/content differences. No historical defaults or script loading. |
| `checkpoints\test_checkpoint.py` | `python -B -m unittest research_tools.checkpoints.test_checkpoint` | All ten original checkpoint tests retained with newly created owned synthetic archives. No real checkpoint manifest or archive was read during this work. |

Checkpoint selections are JSON, for example:

```json
{
  "schema_version": 1,
  "files": ["notes.txt"],
  "directories": ["selected-documents"],
  "categories": {"selected-documents": "selected_documentation"},
  "expected_working_updates": [],
  "required_receipts": []
}
```

Directory traversal is bounded to explicit selections; Git stores and
dependency/bytecode caches are excluded. Default bounds are 10,000 files and
512 MiB for both recorded content and the archive (`--max-files`,
`--max-bytes`). Required receipt entries may contain `path`, `sha256`,
`status_key`, `expected_status` and a `source_sha256` map. A predecessor's
working-file changes must be explicitly named in `expected_working_updates`.
Failed/partial output is not adopted or automatically deleted; inspect it and
select a new output boundary. A verified ZIP is not an atomic filesystem
backup, remote-sync receipt, encryption or authenticity signature.

## Validation and dependencies

From the publication root:

```powershell
$env:PYTHONPATH = (Resolve-Path 'research_tools\.validation-deps').Path
python -B -m unittest discover -s tests -p test_research_tools.py
```

The integration file loads the three preserved suites plus focused portability
and regression cases. All fixtures are created under explicitly owned test
directories and removed afterward. Local Git object reads and network stages
are mocked; the real PowerShell parser runs only on a newly authored synthetic
script. No application/native tests are modified.

If the declared packages are missing, install only into an owned location.
Do not install globally or import a captured vendor cache:

```powershell
New-Item -ItemType Directory -Force 'research_tools\.validation-work' | Out-Null
$env:TEMP = (Resolve-Path 'research_tools\.validation-work').Path
$env:TMP = $env:TEMP
$env:TMPDIR = $env:TEMP
python -B -m pip install --quiet --disable-pip-version-check --no-cache-dir --no-compile --only-binary=:all: --target 'research_tools\.validation-deps' -r 'research_tools\wiki\requirements.txt'
```

These dependency/scratch directories are ignored, not publication content.
The dependency restore above occurred only after the preserved wiki tests
failed because `markdown_it` was unavailable. No global package changes were made.

Actual validation in this increment:

- Initial preserved-suite run: 33 cases, five missing-parser errors. After the
  scoped dependency restore, all 33 passed.
- First expanded run: 66 cases, one portability failure. The PowerShell
  path guard incorrectly classified ordinary synchronized files as links;
  it now rejects actual symbolic links/junctions, matching the Python helpers.
- Final focused run: **72 passed, zero skips**. This includes all 43 preserved
  cases and 29 focused regressions: passive imports/help, explicit roots and
  credential selection, mocked wiki enumeration/collection, source bindings,
  bounded reading packets, supplied-note assembly, static extraction,
  PowerShell parsing, public visibility rechecks, safe raw host comparison and
  synthetic archive creation/verification.
- All 24 authored Python files, including the integration test, compiled
  in memory without bytecode writes. PowerShell `-Help` passed.
- Specific removed-default pattern checks found no matches. These were
  supplemental checks, **not a clearance or proof that unknown private facts
  cannot exist**.
- Installation scratch cleanup initially hit a read-only-directory error.
  After verifying that the owned directory was empty and not a link,
  `Remove-Item -Force` removed it. No permissions or source files were changed.
  The ignored validation dependencies remain available for coordinator checks.

Not exercised against real inputs/services: actual GitHub or Azure DevOps
collection, authentication acceptance, HTTP retry timing/pagination on a live
service, large corpus/ZIP limits, real checkpoint freeze/restore, real host comparison,
or source-specific review and publication. One generated PNG was integrity
checked; that is not image-content review. Full application checks, project
records/cycles, final publication scanning and Git operations belong to the
integration coordinator. No hosted CI or deployment acceptance is claimed.
