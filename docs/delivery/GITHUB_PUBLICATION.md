# Clean repository publication

**Destination:** [Arkthos/SparkForge](https://github.com/Arkthos/SparkForge).
**Current state:** initial publication verified; the later corpus/tooling
increment is local and blocked on an audience decision. GitHub now reports
public visibility instead of the initially verified private visibility.

On 2026-11-12 the pre-push guard stopped before `git push`: repository ID and
owner still matched, but `private` was false. A separate read confirmed
`visibility: public`, metadata update time `2026-11-12T16:07:29Z`, and online
`main` still at `ef54878d1330e3d83089c87fcf799d2a88672a2e`.
No inference is made about who changed the setting. The audience question
received no selection, so no retry or visibility edit was performed.

The expanded, tested local commit is
`13e15010ffc80546fc0cb8ef3ea58fbcc43c3886`. It contains the detailed public
dossier, all inventoried authored research tools and local review-preparation
code, not the private wiki/study contents. A decision to publish those safe
additions publicly would still not approve the separate restricted-corpus upload.

The initial snapshot is commit
[`a30cdba0df37ae032388e89ad7725c5b20a895c2`](https://github.com/Arkthos/SparkForge/commit/a30cdba0df37ae032388e89ad7725c5b20a895c2),
with tree `c5b8250841c3277e51405205fb52f05fcac56db2`. At
`2026-11-11T23:29:09.300328+00:00`, the GitHub `main` ref, private visibility,
empty root-commit parent list and all 100 file objects matched the checked
local snapshot. Documentation-only closure follows in a separate cycle.

The owner requested repository publication and autonomous completion. The
implemented approach uses a new clean history for non-sensitive project-owned
software, source-neutral documentation and reviewed public research. It does
not upload restricted material based on an unanswered clarification.

## Included

- Original project-owned helper, package-builder and preview code.
- Synthetic tests/fixtures and a synthetic self-check specification.
- Usable native agent/skill resources and their exact interface guidance.
- Source-neutral requirements, contracts, decisions, roadmap and acceptance plan.
- Reviewed original public-source synthesis, bibliographic metadata and
  source-only prior-art/learning references with their limits.
- Fresh sanitized validation and publication receipts for this candidate.

## Excluded

- Private corporate wiki pages, proprietary repository captures and attachments.
- Source-specific internal procedures, actual private source pins/identifiers
  and restricted contextual research.
- Original private Git objects/history and its operational/reviewer receipts.
- Runtime databases, journals, model prompts/results, session state and archives.
- Credentials, tokens, private keys, environment files and raw transcripts.
- Generated package/build outputs; reproduce these from the cleared source.

The originals are retained separately, not deleted or history-rewritten.
Omission does not claim that they were unnecessary, publicly licensed or
authorized for another destination. Private visibility is not data-owner
permission.

## Verification before publication

The procedure below also applies to future updates; it is not permission to
expand the cleared content scope.

Run the existing software/documentation checks in this independent checkout.
Verify that tests do not depend on private sibling directories. Review the
complete staged file list and all reachable outgoing commits, not only the
last diff. Check credential/private-source indicators without printing matches
and inspect any finding rather than treating a clean scan as absolute proof.

Verify the repository identity and private visibility immediately before the
push. Push only the prepared branch, without importing private refs or using
force. Inspect the resulting remote commit and privacy afterward. A lost
response requires read-only reconciliation before retry.

The first publication commit has no Git parent: use the documentation
validator without a Git base and inspect mandatory living records/cycle
explicitly. Later implementation/governance commits use the normal lifecycle.

The repository's `.gitattributes` preserves authored bytes, including line
endings, so source and public-research inventories remain verifiable after a
fresh checkout. No global Git configuration was changed.

## Scope of success

Success here means the exact clean software/research snapshot is stored in the
requested private repository. It is not a full workspace backup, a public
license grant, a platform submission, an installed package or a production
release. It does not qualify private data export, a new provider, cross-environment
transfer or automatic learning promotion.

No hosted CI is configured by this operation. Local checks and actual remote
publication are reported separately in [validation history](../VALIDATION_HISTORY.md)
and the append-only cycle.
