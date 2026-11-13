# GitHub Copilot development handoff

## Mission and present state

The owner wants a coordinated SPARK software factory that takes ideas/content/existing code through clarification, platform fit, planning, implementation, testing, independent review, diagnosis, bounded repair/replanning and evidenced delivery. A distinct controller protects the user's intent. Humans decide material changes; ordinary in-scope engineering continues automatically.

The current package is assisted v1. Its strict spec/journal/check/review and snapshot mechanisms work under their tested limits. WP-110..114 implement contracts, pure workflow/replay, isolated-store coexistence and a host protocol/scripted fake alongside it; the coordinated execution loop is not implemented. **WP-115 is the next implementation task**. See the [WP-114 cycle](../engineering/cycles/ENG-20261112-wp114-fake-host.json) and [host protocol](../integration/HOST_ADAPTER.md).

## Read in this order

1. [AGENTS.md](../../AGENTS.md), [status](../PROJECT_STATUS.md), [roadmap](../ROADMAP.md) and [backlog](../IMPLEMENTATION_BACKLOG.csv).
2. [Architecture](../design/ARCHITECTURE.md), [split records/state](../design/DATA_AND_STATE.md), [material decisions](../design/HUMAN_DECISIONS.md).
3. [First task](FIRST_TASK.md) for the implemented foundation, then the next [implementation-plan section](../IMPLEMENTATION_PLAN.md#wp-115-establish-protected-behavioral-acceptance-and-evaluation-fixtures).
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

Continue this focused P1 branch, `kerodri-microsoft-sparkforge-coordinated-contracts`, based on `3decc8bc0326b51ac312b074bfadc396185f8d5c`, until its PR is integrated. Do not restart from older main and duplicate completed WP-110..114. The append-only cycles identify each introducing commit through Git history; use `git log -1 -- docs/engineering/cycles/ENG-20261112-wp114-fake-host.json` to resolve the exact latest implementation boundary. Publication/CI closure will record the observed head separately.

Next concrete task: read WP-115, `docs/specs/FIRST_FACTORY_SLICE.md` and `docs/engineering/EVALUATION_PLAN.md`. Implement the fictional routing interface, protected behavior/negative scenarios and rubric before seeded candidates. Bind evaluator revision outside coder-owned paths; demonstrate detection of implementation defects, semantic drift, changed tests, missing criteria, removed negatives and fabricated passing markers. Do not label scripted evaluation live controller/domain acceptance. Update the four living records and append a cycle; validate and commit before P2. WP-120 is dependency-ready but its journal is not already present in the WP-113 metadata header.

## Ready-to-use continuation prompt

```text
Continue development of Arkthos/SparkForge from the current default branch. Read AGENTS.md, .github/copilot-instructions.md, docs/PROJECT_STATUS.md, docs/development/COPILOT_HANDOFF.md, docs/development/FIRST_TASK.md, docs/design/ARCHITECTURE.md and the selected work-package sections of docs/IMPLEMENTATION_PLAN.md before changing code.

Build the coordinated multi-agent factory described there: a platform-aware brain, independent intent controller, scoped coder/test-author/reviewer/diagnostician roles, deterministic test execution and scheduling, bounded repair/replanning, durable recovery, and human decisions for material changes. The shipped native package is assisted v1; preserve its APIs/tests and do not claim the target runtime already exists.

Start with WP-110 unless the current backlog/evidence proves it is already complete, then select the next dependency-ready P1 task. Implement the exact intent-baseline/execution-envelope contract slice in FIRST_TASK.md with meaningful positive and negative tests. Do not build a scheduler, invent native Copilot commands, add an orchestration framework or require private corp/acro access for this step.

Proceed autonomously through ordinary in-scope coding, testing, diagnosis and correction. Complete and validate each coherent task before advancing; continue to dependency-ready work when the session permits. Ask only for a decision that materially changes user behavior, platform compatibility, authority/data routes, external effects or agreed resource limits. An unavailable future environment qualification must not block source-neutral work. Do not fabricate answers, approvals, independent reviews, model usage or test results.

For every completed slice: run the relevant existing/new tests, fix observed failures, run affected regressions, update docs/PROJECT_STATUS.md, docs/IMPLEMENTATION_BACKLOG.csv, docs/ROADMAP.md and docs/VALIDATION_HISTORY.md, and append a new engineering-cycle JSON. Use README dependency setup and run scripts/validate_plan.py against HEAD before commit and HEAD~ afterward, plus git diff --check. Record skips and actual failures/corrections. Keep historical cycles unchanged.

Use a focused development branch and the repository's normal PR workflow for implemented changes; publish commits/PR updates within this repository, without merging unrelated work or deploying. Include the required co-author trailer. Keep private sources, real profiles, credentials, journals and transcripts out of Git; keep corp and acro isolated. At every stopping point leave an exact checkpoint: commit/branch, completed task and evidence, remaining failures/blockers, next ready task, and precise continuation command/prompt. Do the implementation, not just another plan.
```

## Instruction support references

Repository-wide Copilot instructions are in `.github/copilot-instructions.md`; AGENTS.md remains the detailed contributor contract. GitHub documents client-dependent support, so verify the selected client actually includes the relevant instructions and explicitly attach the handoff when needed. No global precedence is assumed.

- https://docs.github.com/en/copilot/reference/custom-instructions-support
- https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/add-custom-instructions/add-repository-instructions

Reviewed 2026-11-12 for repository instruction placement only; not native multi-agent runtime qualification.
