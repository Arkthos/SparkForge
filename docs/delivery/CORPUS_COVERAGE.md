# What the repository includes

**Updated:** 2026-11-12. **The additions below describe the local working
repository, not the current GitHub tree.** Commit `13e1501` is ready locally.
Its push was stopped because GitHub now reports public visibility, and no
changed-audience choice was obtained. Online `main` remains `ef54878`.

This is a completeness statement, not permission to
disclose excluded material. The owner requested all research, a scrubbed wiki
and all code; the original short publication did not include that full scope.

## Project-owned code and public research

| Material | Actual coverage |
|---|---|
| Main application, tests and preview | All 24 original tracked code files match the publication byte-for-byte |
| Native resources/specifications | The complete working native workflow is included with source-neutral guidance and synthetic examples |
| Public factory/harness corpus | All 28 authored chapters/index/templates and the public source catalog are included |
| Detailed prior-art dossier | All 14 original topic documents now have a detailed public-source edition and explicit inclusion/withholding dispositions; this replaces the summary-only coverage |
| Public source evidence | 33 public repository references and 90 historical inspections are retained as references, not unlicensed source mirrors or newly executed audits |
| Project-authored research/checkpoint utilities | All 19 original inputs are represented: 15 utility scripts, three synthetic test files and requirements metadata; nonidentical verifier versions retain separate entry points with shared stronger checks |
| Local review preparation | The generic full-corpus preparation tool and its synthetic tests are included; private outputs are not |

See the [research index](../../research/README.md), detailed
[dossier](../../research/prior-art/dossier/README.md), and
[tooling source map](../../research_tools/SOURCE_COVERAGE.json).
The tooling's 72 cases passed without skips; the full integrated Python run
passed 394 of 396 cases, with two existing Windows symlink-privilege skips.
See the [completeness specification](../specs/CORPUS_COMPLETENESS.md) and
validation history for scope and corrections. Local completion is not an
uploaded result until the exact remote commit is verified.

## Complete local review, not published wiki content

The separately authorized local workspace now retains a full review set:

| Collection | Verified originals | Full-text page candidates | Remaining condition |
|---|---|---|---|
| Wiki | 117 pages, 57 attachments, 27 ancillary files | 117, with 710 declared mechanical redaction spans | Semantic review, attachment review and exact source/data-owner release decision |
| Engineering study | All 14 authored documents | 14, with 181 declared mechanical redaction spans | Semantic review and exact release decision |

No excerpt truncation or model summary replaced these documents. Every original
byte/hash and every candidate's non-redacted content was checked. The opaque
attachments are original files, not scrubbed images. Mechanical matches can miss
confidential meaning, names and encoded values, and can remove harmless examples.

**The wiki and private engineering content are not on GitHub.** The local
candidate directory contains private originals and must not be uploaded as a
bundle. The [review guide](../engineering/CORPUS_REVIEW.md) explains the actual
mechanism and its `REVIEW_REQUIRED`/permission-false result.

## Other material intentionally separate

- The captured upstream repository contains 623 blobs and 223 directories.
  It is third-party/private source evidence, not SparkForge-authored application
  or research tooling. No source-copy redistribution is implied.
- Public source-code captures, full articles, transcripts and images retain
  their source-specific rights. References and collection tools are not a grant
  to publish every captured byte.
- Original private Git history, runtime journals, credentials and checkpoint
  archive contents remain local. Checkpoint-tool code is a separate category
  from its private archive outputs.

This repository is therefore not a complete private-workspace backup.
The remaining upload is explicitly blocked where review or rights are missing;
it is not silently replaced with a smaller corpus and labeled complete.
