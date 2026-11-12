# Repository cleanup and migration ledger

Baseline before reorganization: `f29eeb2e579f695ebf3c2ec522183ad23a555288`. The owner requested cleanup, a detailed coordinated-factory plan, GitHub publication and Copilot continuation. This is an organization/planning change, not implementation of the future runtime.

## Disposition decisions

| Material | Action | Reason / recovery |
|---|---|---|
| Existing native helpers, agent/skill, schemas and native tests | Retain paths and executable bytes | Useful tested foundation; changing imports/package inventories now would add risk without delivering coordination |
| Host/storage probes, review preparation and research utilities/tests | Retain | Reusable qualification/source tooling; use explicit inputs, no live invocation implied |
| Public research/dossiers/manifests | Retain byte-for-byte | Valuable evidence and inspiration; preserve hashes/dated inspection limits |
| Prior README/AGENTS/requirements/status/roadmap/backlog/plan/matrix/architecture/contracts/decisions | Snapshot under `docs/archive/2026-11-12/` | Preserve old decisions and IDs while replacing active planning |
| Publication scope, corpus coverage, private review preparation/completeness documents | Move into the same archive | Historical disclosure work should not dominate or gate current factory development |
| Fictional static preview, browser harness, two Node test files and preview guide | Remove from active tree | Disconnected prototype has no native runtime integration and is outside the current first-release scope; recover exact bytes from the baseline commit |
| Historical engineering cycles, receipts and validation history | Preserve original paths/bytes; append new outcomes only | Maintain evidence attribution and honest failures/skips |
| Runtime output ignore | Anchor `/runtime/` at repository root so future `plugins/sparkforge/runtime/` source is trackable | Prevent the old generic ignore from hiding the planned implementation |
| New coordinated runtime modules | Plan paths only; do not create placeholders | Implement in dependency-ready tasks with executable behavior |
| License/CODEOWNERS/organization policy | Do not invent | Real owner/terms decisions belong to the appropriate release boundary |

The [machine-readable disposition list](../archive/2026-11-12/dispositions.json) records every archived/moved/removed file and its original SHA-256. It deliberately does not hash itself. Historical cycle/evidence strings naming removed paths refer to those paths at their recorded commit; do not rewrite old receipts to pretend the retired preview is still tested now.

## Active identity migration

Earlier work-package IDs and TC-001 through TC-096 remain in archived CSVs. Active work uses WP-100 onward and TC-101 through TC-200, avoiding reused scenario meanings. The validator knows archived identities for historical references, but applies active dependency/state/coverage checks only to the active CSVs.

The earlier single-agent destination is superseded by D-026, and the future blanket full-spec approval design by D-027. Existing v1 exact-spec runtime behavior is deliberately unchanged. Private-corpus publication is outside the new critical path; no private source is copied or newly approved by this cleanup.

## Verification and rollback

Compare retained executable/research paths against the baseline object IDs; check the whole planned inventory and all Markdown local links outside the historical archive. Run the Python regression suite and planning validator. Verify the exact remote commit/tree after publication. A rollback is a new revert/corrective commit; do not rewrite the existing history or delete private originals.
