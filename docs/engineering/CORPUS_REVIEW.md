# Complete local corpus review preparation

`scripts\prepare_wiki_review.py` prepares full, hash-bound local copies of an
indexed wiki for human review. It does not summarize the pages, approve export,
scrub images or publish anything. The
[completeness specification](../specs/CORPUS_COMPLETENESS.md) defines the work.

## Inputs and explicit destination

Use an existing authorized source export with `manifest.json`. It must contain
`snapshot_commit` and all three arrays: `pages`, `attachments` and
`ancillary_items`. Each item needs a unique key/path, `status: EXPORTED`, the
same snapshot revision, a byte count and SHA-256.

The source may be a retained wiki or an explicitly constructed index of
project-authored documents using this shape. If an index names the subject
repository's revision rather than a document Git revision, label that
distinction. Hashing an index does not authenticate its source assertions.

Choose a **new** authorized local output directory with an existing parent.
The tool refuses existing outputs, source/output overlap, its own code tree
and output beneath a Git repository. It never chooses a temporary directory,
changes synchronization, deletes an old run or configures a remote.

```powershell
python -B scripts\prepare_wiki_review.py --root '<authorized-export>' --output '<new-local-review-directory-outside-git>' --policy '<local-policy.json>' --confirm-local-review
```

Library calls also require explicit confirmation:

```python
from pathlib import Path
from scripts.prepare_wiki_review import prepare_review

report = prepare_review(
    Path(r"C:\approved\source-export"),
    Path(r"C:\approved\review-output"),
    {"schema_version": "sparkforge.wiki-redaction-policy.v1",
     "literals": ["SyntheticExampleOrganization"]},
    confirm_local_review=True,
)
```

The paths and literal above are illustrative, not permission for those
locations. A real policy can contain private names; keep it outside Git.
The optional policy accepts literal strings only, never executable regex/code.
Without one, only the documented built-in mechanical patterns are applied.

## Output and completeness

The output directory contains:

- `source-manifest.private.json`, copied verbatim from the supplied index.
- `redaction-policy.private.json`, with the actual local literal policy.
- `originals\pages`, `originals\attachments` and `originals\ancillary_items`,
  containing every indexed original with verified byte counts/hashes.
- `candidates`, containing every UTF-8 page in full except declared redaction
  spans, including empty pages rather than silently omitting them.
- `review-manifest.private.json`, binding original/candidate identities,
  counts, redactions, policy and implementation hashes, and review limits.
- `README.txt`, explaining why this directory is not a publication payload.

Original inputs are not changed. Candidate positions refer to decoded Unicode
character offsets in the original text; each replacement is recorded. The
concatenation of unchanged segments and recorded replacements reconstructs
the candidate exactly. There is no excerpt limit or generated summary.

Non-page items are copied as opaque bytes and remain `NOT_REVIEWED`. Their
presence is not evidence of image, attachment or active-content scrubbing.
Referenced external resources outside the supplied index are not fetched.
The index itself, including its original reference inventory, is retained locally.

## What the mechanical pass removes

Built-in patterns identify common private-key blocks, authorization headers,
selected token formats, URLs, email addresses, Windows paths, UUIDs and
40/64-character hexadecimal fingerprints. Explicit literal matches supplement
them. Overlapping spans are merged while retaining their rule names/counts.

This pass **can miss sensitive values, personal names, encoded content and
confidential operational meaning**. It can also redact harmless examples.
It is not a semantic sanitizer, secret detector certification or declassification
process. Review both the retained text and every removal.

The result always keeps:

```json
{
  "status": "REVIEW_REQUIRED",
  "publication_authorized": false,
  "semantic_review_completed": false,
  "attachment_review_completed": false
}
```

A successful command means complete local preparation under the declared index,
not a safe-to-publish wiki or permission to upload internal-derived content.

## Failure, ownership and bounds

All source hashes and declared sizes are checked before creating the output.
Duplicate/unsafe paths, missing or incomplete records, mixed revisions,
non-UTF-8 pages and resource violations fail instead of being skipped.
Symlinks, redirecting reparse components and multiply linked files are refused.
Ordinary nonredirecting cloud metadata does not itself qualify storage.

The engineering bounds are 4 MiB for the manifest, 16 MiB per source file,
64 MiB total declared source bytes and 10,000 indexed items. They limit this
helper, not product SLOs. Windows network/mapped/non-local drives are refused;
the operator still owns actual backing-store and storage permission decisions.

Files are created exclusively in the new owned output. A write failure leaves
an `INCOMPLETE.json` marker and any already written private originals intact.
No recursive cleanup is attempted. Reconcile that exact directory; do not
retry into it or delete unknown contents. A missing final review manifest also
means preparation is incomplete.

Path/identity checks are defensive procedure, not a hostile-filesystem sandbox.
Keep roots stable and avoid concurrent mutation. The CLI reports categories and
counts rather than raw source text, exception paths or redacted values.
Library callers must handle failures explicitly and must not publish private
manifest objects by accident.

## Validation and release

```powershell
python -B -m unittest discover -s tests -p test_prepare_wiki_review.py
```

The synthetic suite covers full-length preservation, opaque-file accounting,
redaction reconstruction, missing/altered/incomplete sources, collision
preservation, resource limits, write failure and refusal to use repository
outputs. Positive unit fixtures isolate the repository-location check to keep
test files under `tests`; a separate case exercises the actual refusal.
The actual local corpus run separately exercises an outside-repository destination.

Before any release, a responsible reviewer must assess every candidate and
attachment, identify remaining restricted material, confirm applicable source/
data-owner permission for the exact destination and bind that decision to the
reviewed bytes. This helper has no approve/upload switch. A generic instruction
to continue autonomously or a private repository does not supply that evidence.

Review output is not a drop-in native knowledge index. Redacted bytes must not
reuse original source hashes or be represented as unchanged source excerpts.
An approved publication edition needs its own revision/index and explicit
provenance/permission mapping before a runtime adapter can consume it.
