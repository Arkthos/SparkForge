# Project status

**As of 2026-11-12.** WP-110 through WP-112 implement strict intent/envelope and worker-exchange contracts plus pure workflow/replay guards. The coordinated factory loop is **not implemented yet**. Current shipped product behavior remains experimental assisted v1.

## Implemented foundation

- Native Copilot agent/skill with source-informed intake, reuse/spec/check/review/repair guidance.
- Verified selected local snapshot lookup with bounded source text/citations and explicit coverage limits.
- Strict v1 specification, separate transactional SQLite job journal, operation reservations, bounded real subprocess checks and current-candidate review binding.
- Structural corp/acro package assembly and synthetic integration/negative tests.
- Explicit-input research/source/checkpoint utilities and narrow host/storage preparation tools.
- Source-neutral typed intent/envelope proposals, strict bounded JSON, complete canonical digests, finite allowances and host-independent lexical path validation. These records do not authenticate authority or run anything.
- Typed assignments, attempts, results, findings and failures with current bindings, protected write scopes, separate worker usage claims/host observations and producer-context checks. No worker claim admits evidence or completes a job.
- Pure job/task/attempt projections, legal transitions, expected revisions, command/event bindings, no-op replay, current-evidence completion and explicit unknown-effect/cancellation recovery. No journal or scheduler is created by these functions.

These are reusable mechanisms. They do not yet supply agent task orchestration, an independent running intent controller, autonomous diagnosis/repair, job-wide model accounting, live connectors or installed environment qualification.

## Organization and current plan

The active [roadmap](ROADMAP.md) has P0-P8 milestones, [backlog](IMPLEMENTATION_BACKLOG.csv) has 50 work packages, and [matrix](engineering/ACCEPTANCE_MATRIX.csv) has 100 planned scenarios mapped to 41 requirements. New task identities begin WP-100; earlier IDs remain in the [historical archive](archive/README.md). Old private-corpus publication work is not an active development dependency.

The fictional disconnected browser preview and its Node suite were retired. Current native helpers/tests and public research/source inventories are retained. The [cleanup ledger](development/REPOSITORY_CLEANUP.md) explains each disposition and recovery path.

## Next development action

**Implement WP-113**, the separate-store/v1 coexistence and safe-migration boundary, using the [Copilot handoff](development/COPILOT_HANDOFF.md) and detailed plan. WP-110 through WP-112 are complete. No private corp/acro access, actual model call or new orchestration framework is needed.

Do not interpret planning completion as runtime completion. Agent role documents are design contracts until actual adapter/package tasks ship them. The existing v1 exact-spec manual approval semantics remain unchanged; target materiality policy is future implementation.

## Evidence and limits

Fresh Windows/Python 3.12.10 validation: **457 collected, 455 passed and two skipped** (existing symlink-privilege cases). All 16 transition cases pass. Independent implementation inspection found stranded reconciled work and discarded causes; both were reproduced and corrected without another dispatch or relaxed evidence gates. Earlier dependency/depth/producer fixes remain recorded. See [validation history](VALIDATION_HISTORY.md) and [WP-112 cycle](engineering/cycles/ENG-20261112-wp112-transitions.json). These checks are not live/domain acceptance.

Hosted [Linux/Windows CI](https://github.com/Arkthos/SparkForge/actions/runs/43293165473) passed on the earlier `8b8c167` baseline; it is not evidence for this change. Current-branch CI remains pending publication.

Real corp and acro host/build capability, installed lifecycle, actual model-driven journeys, independent domain/control acceptance, production release, external platform submission and governed learning promotion remain NOT_ASSESSED. corp/acro credentials, source snapshots, journals and model routes stay isolated and outside Git. No private material or new license/organizational policy is inferred.
