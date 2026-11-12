# Project status

**As of 2026-11-12.** WP-100 reorganizes the repository around the coordinated multi-agent factory and a dependency-ordered Copilot implementation plan. The target runtime is **not implemented yet**. Current executable product behavior remains experimental assisted v1.

## Implemented foundation

- Native Copilot agent/skill with source-informed intake, reuse/spec/check/review/repair guidance.
- Verified selected local snapshot lookup with bounded source text/citations and explicit coverage limits.
- Strict v1 specification, separate transactional SQLite job journal, operation reservations, bounded real subprocess checks and current-candidate review binding.
- Structural corp/acro package assembly and synthetic integration/negative tests.
- Explicit-input research/source/checkpoint utilities and narrow host/storage preparation tools.

These are reusable mechanisms. They do not yet supply agent task orchestration, an independent running intent controller, autonomous diagnosis/repair, job-wide model accounting, live connectors or installed environment qualification.

## Organization and current plan

The active [roadmap](ROADMAP.md) has P0-P8 milestones, [backlog](IMPLEMENTATION_BACKLOG.csv) has 50 work packages, and [matrix](engineering/ACCEPTANCE_MATRIX.csv) has 100 planned scenarios mapped to 41 requirements. New task identities begin WP-100; earlier IDs remain in the [historical archive](archive/README.md). Old private-corpus publication work is not an active development dependency.

The fictional disconnected browser preview and its Node suite were retired. Current native helpers/tests and public research/source inventories are retained. The [cleanup ledger](development/REPOSITORY_CLEANUP.md) explains each disposition and recovery path.

## Next development action

**Implement WP-110**, the strict intent-baseline/execution-envelope contracts, following [FIRST_TASK](development/FIRST_TASK.md). Then select the next dependency-ready P1 task. Use the [Copilot handoff](development/COPILOT_HANDOFF.md) and detailed plan. No private corp/acro access, actual model call or new orchestration framework is needed for this first slice.

Do not interpret planning completion as runtime completion. Agent role documents are design contracts until actual adapter/package tasks ship them. The existing v1 exact-spec manual approval semantics remain unchanged; target materiality policy is future implementation.

## Evidence and limits

Fresh local validation: **412 Python cases collected, 382 passed and 30 skipped** (29 Windows-only cases and one PowerShell integration case). No failures/errors remain. Planning validation covers 96 active Markdown files, archive integrity and the 50-task dependency graph. Retained-byte comparison verified 107 existing source/test/research files and all seven historical cycles. See [validation history](VALIDATION_HISTORY.md) and the [reorganization receipt](engineering/evidence/REORGANIZATION_20261112.json). Hosted [Linux/Windows CI](https://github.com/Arkthos/SparkForge/actions/runs/43293165473) passed on `8b8c167`: Linux 383 passed/29 Windows-only skips; Windows all 412 passed with zero skips. The 195-file remote tree exactly matched the staged tree. Historical Node/browser receipts retain their original scope, not current acceptance.

Real corp and acro host/build capability, installed lifecycle, actual model-driven journeys, independent domain/control acceptance, production release, external platform submission and governed learning promotion remain NOT_ASSESSED. corp/acro credentials, source snapshots, journals and model routes stay isolated and outside Git. No private material or new license/organizational policy is inferred.
