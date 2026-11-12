# Research and tooling completeness increment

**Scope:** the owner requested the full research, a scrubbed wiki and all code,
not only the previously published summary. This specification separates
project-owned/public material that can be added now from restricted inputs
that must remain in authorized local storage pending an actual release decision.

## Required outputs

| ID | Observable result | Evidence boundary |
|---|---|---|
| RC-01 | Every original tracked application/test/preview code file is compared with the publication | Byte comparison, not an assumption from directory names |
| RC-02 | Previously omitted project-authored research utilities and their tests are reviewed and included in portable form where safe | No private endpoints, fixed identities, captured credentials or implicit network execution |
| RC-03 | Detailed public prior-art topics are preserved in a full publication edition, not replaced by one short summary | Per-document disposition; private comparisons and unlicensed captured third-party content remain excluded |
| RC-04 | A local-only review preparation tool accounts for every indexed wiki page and attachment without silent omission | Validated source hashes, bounded reads, explicit unsupported/missing cases and preserved originals |
| RC-05 | Every text page's candidate preserves original content/order except declared mechanical redactions | A redaction candidate is not semantic review, permission or a safe-to-publish verdict |
| RC-06 | Missing files, altered hashes, unsafe paths, collisions and incomplete source records stop preparation explicitly | No adoption of existing outputs, automatic recovery deletion or successful-empty fallback |
| RC-07 | Runtime/private content never enters the publication repository merely because a scrubber ran | The tool requires a separate explicit destination, refuses the code repository and never publishes |
| RC-08 | All claims identify published, locally prepared, withheld and unassessed material separately | A new completeness ledger and actual results; no declaration that every private source was exported |

## Handling rules

The current authorization supports local preparation in the operator-selected
workspace and publishing reviewed project-owned/public-source material. The
unavailable scope clarification does not clear corporate or confidential derived
content for a personal GitHub destination. Removing names or matching credential
patterns does not grant that clearance.

Preserve the original working history and source captures. Do not republish
raw transcripts, archives, vendor dependencies, captured third-party code or
private records without their separate rights and authorization. Public
repository references and licensed mechanisms are distinct from source copies.

Research tools must have explicit input/output and service selection. Read-only
imports, help and offline fixtures must not invoke a network service, collect
credentials or run acquired code. Existing network collection commands remain
separately authorized operations, not part of this increment's execution.

The local wiki preparation is a review aid. It must label outputs
`REVIEW_REQUIRED`, retain a local source/candidate map and redaction counts,
and keep publication permission false. Non-text attachments remain
`NOT_REVIEWED`; copying their exact local bytes cannot scrub images or binaries.
Never replace an unreviewed attachment with an invented description.

## Integration and acceptance

Use disjoint owned work for detailed public research and research utilities.
The coordinator owns this specification, local wiki preparation, integration,
living records, cycles and Git operations. Do not touch the already reviewed
native factory candidate or rewrite historical cycles.

Run focused new-tool tests, existing relevant tests, the project validator,
complete publication-content checks and exact outgoing/remote byte comparisons.
Record any remaining source/data-owner decision as a blocker for the affected
upload, not for unrelated safe code/documentation work.
