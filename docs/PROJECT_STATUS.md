# Project status

**As of 2026-11-13.** Corrected P1 plus WP-120/121 are implemented: a transactional coordinated journal and serial scripted-host coordinator now preserve task graph, dispatch and reconciliation state. This is not the full model-driven engineering loop. Current shipped package behavior remains assisted v1.

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
- Pinned serial DAG with mandatory coder/test-author/runner/reviewer/final-controller barriers, durable operation identities, restartable installation and structured result gates. Only scripted hosts and unchanged pinned candidates are supported at this stage; whole-job acceptance remains false until later gates exist.
- Version-bound protected routing evaluator outside candidate ownership: revision 3 has 19 behavioral cases and 12 seeded defects/drift variants. Normal-read payload whitespace is checked with absent and false audit flags; intent remains unchanged at revision 1. This evaluates trusted finite synthetic code, not arbitrary workers in an enforced sandbox.

These are reusable mechanisms. They do not yet supply agent task orchestration, an independent running intent controller, autonomous diagnosis/repair, job-wide model accounting, live connectors or installed environment qualification.

## Organization and current plan

The active [roadmap](ROADMAP.md) has P0-P8 milestones, [backlog](IMPLEMENTATION_BACKLOG.csv) has 50 work packages, and [matrix](engineering/ACCEPTANCE_MATRIX.csv) has 100 planned scenarios mapped to 41 requirements. New task identities begin WP-100; earlier IDs remain in the [historical archive](archive/README.md). Old private-corpus publication work is not an active development dependency.

The fictional disconnected browser preview and its Node suite were retired. Current native helpers/tests and public research/source inventories are retained. The [cleanup ledger](development/REPOSITORY_CLEANUP.md) explains each disposition and recovery path.

## Next development action

**Next: WP-122**, materiality classification and decision admission, using the completed [journal/coordinator APIs](design/DATA_AND_STATE.md#implemented-wp-121-serial-coordinator) on the existing PR branch. WP-120 and WP-121 are complete; the rest of P2 is not. Workspace integration, real result/effect mediation, aggregate accounting and final intent acceptance remain explicit later tasks.

Do not interpret planning completion as runtime completion. Agent role documents are design contracts until actual adapter/package tasks ship them. The existing v1 exact-spec manual approval semantics remain unchanged; target materiality policy is future implementation.

## Evidence and limits

Fresh WP-121 Windows/Python 3.12.10 validation: **547 collected, 545 passed, two existing symlink-privilege skips**. All **73 affected tests** pass, including 19 scheduler/coordinator cases. Distinct review exposed a stale-snapshot cancellation race, blocked reconciliation without cancel support, and cross-kind command-key collisions; each reproduced before correction. Additional job-context guards stop stale graph execution and prevent invalidation while descendant effects remain unresolved. See [validation history](VALIDATION_HISTORY.md) and [WP-121 cycle](engineering/cycles/ENG-20261113-wp121-coordinator.json).

[The P1 pull request](https://github.com/Arkthos/SparkForge/pull/1) is open and unmerged, published through the native PR tool. Original P1 implementation head `9e8c7793f9045ceda3929d3fe7c14ff20abf6caa` and tree `1946fddc75f0b863ae196a83019ddc675b6d10c1` had [passing hosted CI](https://github.com/Arkthos/SparkForge/actions/runs/43362930589): Windows 497/497; Linux 468 passed/29 skipped. Those are historical results, not the current correction count. Earlier EMU denials and a corrected unpublished-head/base validation error remain recorded; no agent changed credentials, destination or visibility.

WP-120 was committed/published as `1999ac26351488fbf42ed626e0a191bdc09f44bb`; [its hosted run](https://github.com/Arkthos/SparkForge/actions/runs/43526649270) passed Windows 528/528 and Linux 499 passed/29 skipped, including planning/whitespace. WP-121's hosted results await its publication. Historical cycles remain immutable. The earlier reported DNS/model interruption produced no implementation delta or route changes. No merge, Agent merge, deployment or actual model/tenant operation occurred.

Real corp and acro host/build capability, installed lifecycle, actual model-driven journeys, independent domain/control acceptance, production release, external platform submission and governed learning promotion remain NOT_ASSESSED. corp/acro credentials, source snapshots, journals and model routes stay isolated and outside Git. No private material or new license/organizational policy is inferred.
