# Project status

**As of 2026-11-13.** Corrected P1 and WP-120 are implemented: the coordinated SQLite journal now persists and reconstructs source-neutral job/task/attempt state. The serial coordinator and full engineering loop are not yet implemented. Current shipped package behavior remains assisted v1.

## Implemented foundation

- Native Copilot agent/skill with source-informed intake, reuse/spec/check/review/repair guidance.
- Verified selected local snapshot lookup with bounded source text/citations and explicit coverage limits.
- Strict v1 specification, separate transactional SQLite job journal, operation reservations, bounded real subprocess checks and current-candidate review binding.
- Structural corp/acro package assembly and synthetic integration/negative tests.
- Explicit-input research/source/checkpoint utilities and narrow host/storage preparation tools.
- Source-neutral typed intent/envelope proposals, strict bounded JSON, complete canonical digests, finite allowances and host-independent lexical path validation. These records do not authenticate authority or run anything.
- Typed assignments, attempts, results, findings and failures with current bindings, protected write scopes, separate worker usage claims/host observations and producer-context checks. No worker claim admits evidence or completes a job.
- Pure job/task/attempt projections, legal transitions, expected revisions, command/event bindings, no-op replay, current-evidence completion and explicit unknown-effect/cancellation recovery. No journal or scheduler is created by these functions.
- Coordinated schema-v2 initializer and explicit v1-header copy migration, verified backups, immutable records/commands/events, revision-guarded projections and uniquely owned reservations. Read-only reconstruction detects divergence; explicit SQLite recovery preserves unknown host effects. Assisted-v1 stores remain separate and unchanged.
- Source-neutral host capability/observation protocol and a scripted test fake with dispatch/cancel counters, lost-response reconciliation and explicit unknown usage. No native launcher or real worker/model execution is implemented.
- Version-bound protected routing evaluator outside candidate ownership: revision 3 has 19 behavioral cases and 12 seeded defects/drift variants. Normal-read payload whitespace is checked with absent and false audit flags; intent remains unchanged at revision 1. This evaluates trusted finite synthetic code, not arbitrary workers in an enforced sandbox.

These are reusable mechanisms. They do not yet supply agent task orchestration, an independent running intent controller, autonomous diagnosis/repair, job-wide model accounting, live connectors or installed environment qualification.

## Organization and current plan

The active [roadmap](ROADMAP.md) has P0-P8 milestones, [backlog](IMPLEMENTATION_BACKLOG.csv) has 50 work packages, and [matrix](engineering/ACCEPTANCE_MATRIX.csv) has 100 planned scenarios mapped to 41 requirements. New task identities begin WP-100; earlier IDs remain in the [historical archive](archive/README.md). Old private-corpus publication work is not an active development dependency.

The fictional disconnected browser preview and its Node suite were retired. Current native helpers/tests and public research/source inventories are retained. The [cleanup ledger](development/REPOSITORY_CLEANUP.md) explains each disposition and recovery path.

## Next development action

**Continue with WP-121**, the serial dependency scheduler/coordinator, using the completed [journal API](design/DATA_AND_STATE.md#implemented-wp-120-api-and-boundaries) on [PR #1](https://github.com/Arkthos/SparkForge/pull/1). WP-120 is complete; the remaining P2 tasks are not. Source-neutral fake observations are sufficient. Unknown external effects remain unresolved until observation-backed reconciliation; journal replay never invokes a host.

Do not interpret planning completion as runtime completion. Agent role documents are design contracts until actual adapter/package tasks ship them. The existing v1 exact-spec manual approval semantics remain unchanged; target materiality policy is future implementation.

## Evidence and limits

Fresh WP-120 Windows/Python 3.12.10 validation: **528 collected, 526 passed, two existing symlink-privilege skips**. All **75 affected tests** pass, including 18 journal tests and 17 migration tests. Owned process exits exercise rollback before commit and persistent replay after a lost commit reply. Distinct review found observation-version and parent-cancellation defects; both were reproduced and fixed. Initial cold-journal recovery failures and corrections remain in [validation history](VALIDATION_HISTORY.md) and the [WP-120 cycle](engineering/cycles/ENG-20261113-wp120-journal.json).

[The P1 pull request](https://github.com/Arkthos/SparkForge/pull/1) is open and unmerged, published through the native PR tool. Original P1 implementation head `9e8c7793f9045ceda3929d3fe7c14ff20abf6caa` and tree `1946fddc75f0b863ae196a83019ddc675b6d10c1` had [passing hosted CI](https://github.com/Arkthos/SparkForge/actions/runs/43362930589): Windows 497/497; Linux 468 passed/29 skipped. Those are historical results, not the current correction count. Earlier EMU denials and a corrected unpublished-head/base validation error remain recorded; no agent changed credentials, destination or visibility.

The [P1 publication](engineering/cycles/ENG-20261112-p1-publication.json), [correction](engineering/cycles/ENG-20261113-p1-review-corrections.json) and [preparation](engineering/cycles/ENG-20261113-wp120-preparation.json) cycles remain immutable. WP-120 began from verified clean local/upstream/PR head `f61a33ddc928fcb2dbf43abc02f4a25979089670`; its new hosted results await publication. A reported DNS/model-request interruption preceded this work and made no implementation delta. No route/credential changes, merge, Agent merge or deployment occurred.

Real corp and acro host/build capability, installed lifecycle, actual model-driven journeys, independent domain/control acceptance, production release, external platform submission and governed learning promotion remain NOT_ASSESSED. corp/acro credentials, source snapshots, journals and model routes stay isolated and outside Git. No private material or new license/organizational policy is inferred.
