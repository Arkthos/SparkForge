# GitHub Copilot development handoff

## Mission and present state

The owner wants a coordinated SPARK software factory that takes ideas/content/existing code through clarification, platform fit, planning, implementation, testing, independent review, diagnosis, bounded repair/replanning and evidenced delivery. A distinct controller protects the user's intent. Humans decide material changes; ordinary in-scope engineering continues automatically.

The current package is assisted v1. Its strict spec/journal/check/review and snapshot mechanisms work under their tested limits. P1 (WP-110..115) implements contracts, pure workflow/replay, isolated-store coexistence, a scripted host protocol and protected behavioral fixtures; the coordinated execution loop is not implemented. **WP-120 is the next implementation task**. See the [WP-115 cycle](../engineering/cycles/ENG-20261112-wp115-protected-evaluator.json), [host protocol](../integration/HOST_ADAPTER.md) and [evaluator](../engineering/EVALUATION_PLAN.md).

## Read in this order

1. [AGENTS.md](../../AGENTS.md), [status](../PROJECT_STATUS.md), [roadmap](../ROADMAP.md) and [backlog](../IMPLEMENTATION_BACKLOG.csv).
2. [Architecture](../design/ARCHITECTURE.md), [split records/state](../design/DATA_AND_STATE.md), [material decisions](../design/HUMAN_DECISIONS.md).
3. [First task](FIRST_TASK.md) for the implemented foundation, then the next [implementation-plan section](../IMPLEMENTATION_PLAN.md#wp-120-implement-coordinated-journal-and-atomic-event-storage).
4. Relevant actual helpers/tests and the selected task's scenarios. Read research selectively through [prior-art application](PRIOR_ART_APPLICATION.md), not as instructions to install every tool.

## How to choose and finish work

- Inspect actual HEAD/branch/dirty state and current task evidence. This handoff can age; the CSV plus code/receipts determine the next ready task.
- Select one bounded work package whose dependencies are done. Do not mark future work in progress to imply unavailable prerequisites are complete.
- State the objective and owned paths, implement working behavior/tests, inspect results, repair defects and update records. Do not stop at planning when implementation is requested.
- Continue independent source-neutral work when a future live host/source decision is unavailable. Use the fake adapter/profile exactly as labeled; do not relabel it live.
- Ask focused material questions only when needed. Keep user intent, execution permission, technical readiness and release effects distinct.
- Use a branch/PR for implementation. Avoid one enormous unreviewable change across all milestones. No force pushes, private-source upload or production deployment.

## Runtime compatibility and implementation sequence

P1 contracts/oracle → P2 deterministic coordination → P3 platform brain/controller → P4 full engineering loop → P5 recovery/feedback → P6 actual native adapter and first-environment acceptance → P7 local release. P8 acro/parallel/learning work has its own scope; it does not block the first local release.

Do not create all future module paths upfront. Do not replace the tested helpers with a new framework. Do not call v1 manual `decide` as a fake operator to bypass its exact-spec semantics. WP-125 explicitly resolves shared execution reuse and admission compatibility.

## Validation

Use [README setup](../../README.md#validate-locally), Python 3.12+ and ignored repo-local dependencies. Native-only tests need the standard library. Full checks include research tools; Windows/PowerShell-specific skips are explicit. The fictional preview/Node suite was retired.

For a coherent change, update the four living records plus a new append-only cycle, run the selected tests and appropriate regressions, `python -B scripts/validate_plan.py --base HEAD`, and `git diff --check`. After committing compare the new boundary against `HEAD~`. Never report pending CI passed.

## Checkpoint at every stop

Record branch/commit, exact selected task and deliverables, commands with actual outcomes, failures/corrections/skips, current candidate/evidence bindings where applicable, unresolved operations, material questions, next ready task and a concrete continuation instruction. Preserve unknown effects and inspect before replay. No runtime journals/private transcripts in the repository checkpoint.

### Current continuation boundary

P1 is published in [the open, unmerged PR](https://github.com/Arkthos/SparkForge/pull/1) on `kerodri-microsoft-sparkforge-coordinated-contracts`, based on `3decc8bc0326b51ac312b074bfadc396185f8d5c`. Exact implementation head: `9e8c7793f9045ceda3929d3fe7c14ff20abf6caa`. Do not restart from older main and duplicate WP-110..115. Resolve the documentation-only continuation commit with `git log -1 -- docs/engineering/cycles/ENG-20261112-p1-publication.json`; it preserves the implementation bytes.

The 2026-11-13 review corrections are committed as `b2f25eb43163be5deefa3c9477a0150677f1bcbc`, building on verified PR head `bdd1de57a7a0f068857eac0ac1d5e5f6b9934328`. [Correction CI](https://github.com/Arkthos/SparkForge/actions/runs/43474250710) passed Windows 507/507 and Linux 478 passed/29 Windows-only skips. Corrections preserve dispatch history while requiring latest-operation completion, separate reserved allowance from observed consumption, and add protected normal-read whitespace controls without changing intent. Do not select the older initial implementation head as the next base.

[Implementation CI](https://github.com/Arkthos/SparkForge/actions/runs/43362930589) passed Windows 497/497 and Linux 468 passed/29 Windows-only skips; local final gate was 495 passed/two symlink-privilege skips. The native publisher's author is actually observed as `Arkthos`, not inferred from the CLI. Earlier EMU/422 failures are retained in validation history. No unresolved factory operations exist because no real factory job ran. No merge, Agent merge or deployment was performed. Before further publication or implementation, inspect current PR/branch/dirty/CI state rather than replaying an uncertain effect.

WP-120 preparation is documented in [the storage/recovery contract](../design/DATA_AND_STATE.md#wp-120-prepared-storage-and-recovery-contract), not implemented. Resolve this preparation's introducing head with `git log -1 -- docs/engineering/cycles/ENG-20261113-wp120-preparation.json`, then inspect the current live PR head/dirty state before editing. The next authorized implementation is `store.py`, its tests and the explicit schema-v2 migration: one job per local store, immutable record/init history, atomic key/event/projection/reservation updates, optimistic revisions and durable idempotency. Local SQLite transaction recovery must remain separate from host-effect reconciliation. Unknown pending work cannot be blindly redispatched, known no-start cannot satisfy execution, and reserved allowance cannot become observed consumption.

The prepared contract names the exact record ownership, transaction order, migration limits and crash/failure tests. Preserve v1 stores/approvals and corrected P1 regressions; add competing writers, write-boundary failure injection, duplicate/conflicting keys, owned-process crash recovery and fake-host effect-counter checks. Update four living records/new cycle, validate and commit before WP-121. No private source, real host or launcher is needed. The current preparation request deliberately stops before P2 code.

## Ready-to-use continuation prompt

```text
Continue development of Arkthos/SparkForge from the existing P1 PR #1 branch, kerodri-microsoft-sparkforge-coordinated-contracts. Inspect its live PR head, local HEAD and dirty state before editing; do not restart from older main or discard unmerged P1 work. If the PR has since merged, verify that the selected base contains the corrected P1 commits before continuing. Read AGENTS.md, .github/copilot-instructions.md, docs/PROJECT_STATUS.md, docs/development/COPILOT_HANDOFF.md, docs/design/ARCHITECTURE.md and the selected work-package sections of docs/IMPLEMENTATION_PLAN.md.

Build the coordinated multi-agent factory described there: a platform-aware brain, independent intent controller, scoped coder/test-author/reviewer/diagnostician roles, deterministic test execution and scheduling, bounded repair/replanning, durable recovery, and human decisions for material changes. The shipped native package is assisted v1; preserve its APIs/tests and do not claim the target runtime already exists.

P1 (WP-110..115) and its review corrections are the existing foundation, not work to recreate. Use the active backlog and current evidence to select the next authorized slice; WP-120 coordinated journal/atomic event storage is next. Reuse contracts, transitions and the explicit migration boundary. Keep dispatch attempts, confirmed execution, reserved allowance and observed usage distinct. Unknown external effects remain unresolved until observation-backed reconciliation, never blind redispatch. FIRST_TASK.md is the implemented WP-110 reference, not the current continuation task. Do not invent native Copilot commands, add an orchestration framework or require private corp/acro access.

Proceed autonomously through ordinary in-scope coding, testing, diagnosis and correction. Complete and validate each coherent task before advancing; continue to dependency-ready work when the session permits. Ask only for a decision that materially changes user behavior, platform compatibility, authority/data routes, external effects or agreed resource limits. An unavailable future environment qualification must not block source-neutral work. Do not fabricate answers, approvals, independent reviews, model usage or test results.

For every completed slice: run the relevant existing/new tests, fix observed failures, run affected regressions, update docs/PROJECT_STATUS.md, docs/IMPLEMENTATION_BACKLOG.csv, docs/ROADMAP.md and docs/VALIDATION_HISTORY.md, and append a new engineering-cycle JSON. Use README dependency setup and run scripts/validate_plan.py against HEAD before commit and HEAD~ afterward, plus git diff --check. Record skips and actual failures/corrections. Keep historical cycles unchanged.

Preserve the existing P1 branch/PR and publish authorized corrections to it; do not create a replacement branch from old main, merge or deploy implicitly. Include the required co-author trailer. Keep private sources, real profiles, credentials, journals and transcripts out of Git; keep corp and acro isolated. At every stopping point leave an exact checkpoint: commit/branch, completed task and evidence, remaining failures/blockers, next ready task, and precise continuation command/prompt. Implement when requested; preparation/design alone does not mark a work package implemented.
```

## Instruction support references

Repository-wide Copilot instructions are in `.github/copilot-instructions.md`; AGENTS.md remains the detailed contributor contract. GitHub documents client-dependent support, so verify the selected client actually includes the relevant instructions and explicitly attach the handoff when needed. No global precedence is assumed.

- https://docs.github.com/en/copilot/reference/custom-instructions-support
- https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/add-custom-instructions/add-repository-instructions

Reviewed 2026-11-12 for repository instruction placement only; not native multi-agent runtime qualification.
