# Project status

**As of 2026-11-12.** WP-110 through WP-113 implement strict intent/envelope and worker-exchange contracts, pure workflow/replay guards and a separate-store coexistence boundary. The coordinated factory loop is **not implemented yet**. Current shipped product behavior and package inventory remain experimental assisted v1.

## Implemented foundation

- Native Copilot agent/skill with source-informed intake, reuse/spec/check/review/repair guidance.
- Verified selected local snapshot lookup with bounded source text/citations and explicit coverage limits.
- Strict v1 specification, separate transactional SQLite job journal, operation reservations, bounded real subprocess checks and current-candidate review binding.
- Structural corp/acro package assembly and synthetic integration/negative tests.
- Explicit-input research/source/checkpoint utilities and narrow host/storage preparation tools.
- Source-neutral typed intent/envelope proposals, strict bounded JSON, complete canonical digests, finite allowances and host-independent lexical path validation. These records do not authenticate authority or run anything.
- Typed assignments, attempts, results, findings and failures with current bindings, protected write scopes, separate worker usage claims/host observations and producer-context checks. No worker claim admits evidence or completes a job.
- Pure job/task/attempt projections, legal transitions, expected revisions, command/event bindings, no-op replay, current-evidence completion and explicit unknown-effect/cancellation recovery. No journal or scheduler is created by these functions.
- Explicit new coordinated store headers, read-only assisted-v1 references and verified copy-before-migration transactions. Only store version 1 is shipped; future upgrades are exercised with injected synthetic test steps, never real operator conversion or automatic activation.

These are reusable mechanisms. They do not yet supply agent task orchestration, an independent running intent controller, autonomous diagnosis/repair, job-wide model accounting, live connectors or installed environment qualification.

## Organization and current plan

The active [roadmap](ROADMAP.md) has P0-P8 milestones, [backlog](IMPLEMENTATION_BACKLOG.csv) has 50 work packages, and [matrix](engineering/ACCEPTANCE_MATRIX.csv) has 100 planned scenarios mapped to 41 requirements. New task identities begin WP-100; earlier IDs remain in the [historical archive](archive/README.md). Old private-corpus publication work is not an active development dependency.

The fictional disconnected browser preview and its Node suite were retired. Current native helpers/tests and public research/source inventories are retained. The [cleanup ledger](development/REPOSITORY_CLEANUP.md) explains each disposition and recovery path.

## Next development action

**Implement WP-114**, the host capability protocol and deterministic scripted fake, using the [Copilot handoff](development/COPILOT_HANDOFF.md) and detailed plan. WP-110 through WP-113 are complete. WP-115 protected evaluation and WP-120 coordinated journal are also dependency-ready; keep each slice independently evidenced. No private corp/acro access, actual model call or invented launcher is needed.

Do not interpret planning completion as runtime completion. Agent role documents are design contracts until actual adapter/package tasks ship them. The existing v1 exact-spec manual approval semantics remain unchanged; target materiality policy is future implementation.

## Evidence and limits

Fresh Windows/Python 3.12.10 validation: **471 collected, 469 passed and two skipped** (existing symlink-privilege cases). All 14 migration/coexistence cases pass. Independent inspection exposed read-only WAL sidecar creation and false version stamping after automatic rollback; both were reproduced and corrected. Earlier failures, fixture cleanup corrections and all independent inspections remain recorded. See [validation history](VALIDATION_HISTORY.md) and [WP-113 cycle](engineering/cycles/ENG-20261112-wp113-coexistence.json). These checks are not live/domain or power-failure acceptance.

Hosted [Linux/Windows CI](https://github.com/Arkthos/SparkForge/actions/runs/43293165473) passed on the earlier `8b8c167` baseline; it is not evidence for this change. Current-branch CI remains pending publication.

Real corp and acro host/build capability, installed lifecycle, actual model-driven journeys, independent domain/control acceptance, production release, external platform submission and governed learning promotion remain NOT_ASSESSED. corp/acro credentials, source snapshots, journals and model routes stay isolated and outside Git. No private material or new license/organizational policy is inferred.
