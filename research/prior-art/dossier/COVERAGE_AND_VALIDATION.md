# Coverage, integrity, and validation limits

**Historical source baseline:** 2026-11-05. **Public edition:** 2026-11-12.
This page distinguishes the old research corpus, the publication's retained
metadata and analysis, and checks actually run on the new publication bytes.
No source or framework reading is silently relabeled as fresh execution.

The public comparison portion of the original coverage document is retained.
Private archive inventories, personal paths, original machine-specific
commands, mixed-context receipt files, and raw source/media payloads are not
included.

## 1. Historical coverage and the publication denominator

| Historical measure | Count | What is retained here |
|---|---:|---|
| Public repository snapshots | 33 | Public identities, immutable commits, dates, tree identities, observed visibility/archival state, and license coordinates |
| Selected UTF-8 source files captured in the study | 136 | No captured source bytes; only relevant public bibliographic and inspection metadata |
| Registered inspections | 90 | All inspection IDs, kinds, exact public paths, inclusive ranges, and bounded review notes |
| Source files with registered semantic ranges | 88 | All registered coordinates; some inspections share a file |
| Captures without registered semantic ranges | 48 | Historical count and its limit; not silently upgraded to reviewed evidence |
| Repositories with selected implementation reading | 9 | Spec Kit, OpenSpec, BMad Loop, RSC, SSSF, Foreman, Waza, Promptfoo, Rigour |
| Distinct registered source lines | 10,471 | The deduplicated line-coordinate denominator, not redistributed lines or a security-audit count |
| Original Markdown document topics | 14 | Fourteen detailed counterparts with an explicit disposition for every source document |
| Registered ZazenCodes supplement | 1 | Historical review method, timestamps, public companion identity, and limitations |
| Supplied overview images retained by the historical study | 1 | Historical fact only; no image is redistributed |

The 14 source documents comprise twelve authored scope/topic/reference texts
and two generated reference views. This edition likewise separates authored
analysis from the rendered catalog/register.

The captured-file denominator is historical. It is not the number of files
available in this checkout or a percentage of any upstream repository.
Root and selected directory listings were not exhaustive tree inventories.
The 48 files without registered semantic ranges include separately classified
license material and capture-only files; "captured" does not mean audited.

The [existing source catalog](../sources.json) supports local recomputation of
33 repositories, 90 inspections, 88 distinct reviewed files, nine selected
implementation repositories, and 10,471 distinct coordinates. The publication
does not have the 136 source captures needed to revalidate their original
bytes.

## 2. Evidence levels

| Level | Meaning in this dossier |
|---|---|
| Discovery-only | A result or link was found; it was not vetted as a candidate |
| Documentation reviewed | The specified README, guide, or specification range was historically read |
| Skill contract reviewed | Declared instructions were examined; compliance and enforcement were not established |
| Selected implementation reviewed | The cited code/configuration path was read at the recorded revision |
| Test source reviewed | Assertions were inspected; tests were not executed by this study |
| Candidate runtime validated | **NOT_RUN** |
| Selected deployment or customized-host acceptance | **NOT_ASSESSED** |

Some source kinds have still narrower ceilings: Foreman's instructions
embedded in source are prompts, Attractor is a specification, and factor-12
text-only reading does not include its linked diagrams.

Acquired prompts, installers, hooks, examples, model requests, schedules, and
deployment instructions were untrusted data. The historical investigation did
not activate them, and the publication pass does not execute them.

## 3. What the historical integrity tool checked

The original local network-free verification checked:

- public-snapshot metadata and complete commit identities;
- each captured file's byte length, UTF-8 line count, SHA-256, and Git blob
  SHA-1;
- source URLs against repository, pin, and original path;
- absence of LFS-pointer substitutions among selected text captures;
- candidate/catalog reconciliation and actual recorded root-license grants;
- registered ranges and generated source views;
- video/source identity, declared caption coverage, and the supplied image's
  recorded bytes and digest; and
- required authored documents and their local links/Markdown anchors.

The full caption text was not retained, so the extraction fingerprint could
not be independently rehashed by the offline verifier. The sampled frames
were historical browser-review observations, not separately retained source
files. Those limits are not repaired by publishing their description.

Hashes detect drift against a baseline. They do not prove authorship,
cryptographic signatures, current URL availability, every inference's
correctness, complete license clearance, or application security. An actor
able to replace both content and its manifest is outside that guarantee.

## 4. Historical outcomes, not current acceptance

The original authored coverage record and its receipt reported the following
results on 2026-11-05. These are preserved as **historical observations**, not
checks rerun for this edition and not new validation of excluded artifacts.

| Historical check | Reported result | Evidence boundary |
|---|---|---|
| Research-utility synthetic tests | PASS, 16 tests | Utility behavior, including video identity/coverage gaps, companion revision, and image tampering; not candidate frameworks |
| Catalog/index generation | PASS, 33 repositories and 136 captures | Source-index and citation-view generation, not software execution |
| Working-dossier verification | PASS, 14 documents, 498 relative links, 321 Markdown anchors | Original dossier/source integrity; these are not the current publication's link counts |
| Original verification receipt | PASS at `2026-11-05T13:33:49.916532+00:00` | Historical report; original private-context receipt and document fingerprints are withheld |
| Candidate installation, test suites, live models | NOT_RUN | Deliberately outside the research execution scope |
| Actual target-host acceptance | NOT_ASSESSED | No deployment or live compatibility evidence |

Historical archive checks and a separate shared-handoff link check are not
reproduced as evidence for this publication. They depended on excluded local
artifacts and say nothing about the new candidate. Their original archive
contents, inventory counts, locations, and resume records remain withheld.

### Failures and corrections remain visible

The first historical index attempt rejected Promptfoo's headerless MIT grant
because the classifier required an MIT title. The actual terms were inspected,
the classifier was corrected to recognize the grant, synthetic coverage was
extended, and tests/indexing passed. No upstream bytes were changed to make
the check pass.

The OpenAI harness-engineering fetch returned HTTP 403. The Foreman `src`
lookup failed and was corrected using the actual root inventory. These are
acquisition limits/corrections, not candidate test failures or evidence of
fallback credentials.

## 5. ZazenCodes follow-up coverage

The supplement added ten captured and registered companion files from one
repository. It distinguished the historical v1 build prompt, the video's
evolution, later v1 contracts, and separate v2 README/license.

The authored review records 778 unique available English auto-caption
segments deduplicated from 1,556 DOM rows, covering 00:00-27:47, and two
selected frame checks at 13:06 and 19:27. This is not continuous listening,
full visual coverage, or a repeat viewing by the publication worker.

Only v2's README and opening license text were read; executable code was not
audited or run. No standard root/v1 license was established. The scoped v2
GPLv3 grant does not license sibling material.

The supplied overview's original bytes were historically preserved and
checked, but are not in the publication. Captions, frames, raw browser
records, and their extraction fingerprints are also omitted. The
[video counterpart](VIDEO_ZAZEN_FACTORY.md) preserves the public analytical
content without implying rights to redistribute that media.

## 6. Reproduce the publication checks, not private-source validation

From this repository root, run the standard-library-only PowerShell recipe
in [the research library](../../README.md#local-validation). It reads the
[outer inventory](../../publication-manifest.json), checks current file
membership and byte hashes, parses JSON, verifies local Markdown file/anchor
links and source IDs, parses fenced JSON examples, and rejects trailing
spaces/tabs.

For normal Git whitespace validation of owned changes:

```powershell
git --no-pager diff --check -- research docs\research\SELF_IMPROVEMENT.md docs\research\self-improvement-sources.json
```

The recipe also checks the dossier's 14 dispositions and counterpart hashes,
33 candidate records, and all 90 rendered inspection anchors against the
preserved metadata. Link checks concern local files/anchors and pinned URL
structure, **not current external availability**.

The original private-source verification command is intentionally not offered
as a command that works on this publication. It requires excluded source
captures and records. Reindexing metadata would not constitute a new source
review even if those inputs were available.

The outer manifest preserves its earlier check objects unchanged and appends
dated evidence for this expansion. The previous manifest is separately
retained as an immutable publication-history snapshot. A historical PASS is
not overwritten or relabeled as a current result.

## 7. Publication checks on 2026-11-12

The following checks were actually executed locally for this expansion.
The outer inventory records the dated results separately from its immutable
2026-11-11 check objects. Inventory validation was also repeated after
recording the publication documentation and results.

| Actual command or check | Result | Scope |
|---|---|---|
| `python -B -`, executing the documented research-library PowerShell recipe | PASS | 54 inventoried files, 53 content hashes, 45 Markdown files, nine JSON files, 651 local links, two JSON examples, zero trailing-whitespace findings |
| Dossier checks within that recipe | PASS | All 14 dispositions/counterpart hashes, 33 candidates, 90 inspections, 88 source-coordinate files, 10,471 distinct line coordinates, 188 pinned dossier links, 21 Zazen timestamp topics and seven Risco ranges |
| `python -B -`, local original-topic/pin/range comparison | PASS | All 14 originals accounted for and unchanged against their existing receipt; all 33 public pins and 90 distinct range-coordinate sets retained |
| `python -B -`, finite publication-content indicators | PASS | 54 research/self-improvement files; no selected machine-path, excluded-context, credential-token, private-key, unexpected-file-type, or symlink findings |
| `git --no-pager diff --check -- research docs\research\SELF_IMPROVEMENT.md docs\research\self-improvement-sources.json` | PASS | Normal tracked-working-tree whitespace check without configuration overrides; the recipe additionally checks untracked publication text |
| Historical publication preservation checks | PASS | Prior manifest bytes and old check/correction objects unchanged; 33 other preexisting content files remain byte-identical |

This is bounded documentation and provenance verification, not exhaustive
semantic equivalence, a legal audit, or a guarantee that every possible
sensitive-content pattern was detected. Original-topic comparisons did not
read or execute the excluded upstream source captures. Product/runtime tests
were not rerun for this documentation-only increment; the coordinator owns
broader integration checks and any external publication.

## 8. What remains unestablished

- Current upstream content or availability at mutable web URLs.
- Candidate installation, tests, benchmarks, model trials, or measured
  quality/cost improvement.
- End-to-end host permissions, identity, sandboxing, or deployment acceptance.
- Every route through any reviewed framework.
- Complete source/dependency/media redistribution clearance.
- Revalidation of absent source captures, raw transcripts, images, or private
  checkpoint/archive material.
- Complete absence of sensitive material beyond the bounded editorial review
  and finite local indicator checks.
- Git staging, commits, remote publication, hosted CI, or product release by
  this research worker.

A documentation-integrity pass supports the stated local properties only.
Current product evidence and the coordinator's separately authorized
publication results belong in the project records, not retroactively in the
historical research.
