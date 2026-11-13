# Detailed implementation plan

This is the execution companion to the [roadmap](ROADMAP.md), [active backlog](IMPLEMENTATION_BACKLOG.csv), [architecture](design/ARCHITECTURE.md) and [scenario matrix](engineering/ACCEPTANCE_MATRIX.csv). It contains 50 work packages and 100 planned acceptance scenarios. The CSV owns state; this document owns implementation instructions. Paths under a future `runtime/` tree are proposed destinations, not existing modules or working commands.

## Rules for every work package

Read actual code first. Prefer existing helpers and the smallest complete behavior. Use closed versioned records, explicit dependencies, finite allowances, synthetic fixtures and genuine evidence. Do not create placeholder modules merely to check off file names. If a better local module boundary is justified, record it in the task/cycle and update dependent paths without changing behavior or scope.

Define allowed writes before dispatch; protect baseline/oracle/control-plane resources. Preserve unrelated work. Add meaningful positive and negative tests; report unexecuted live scenarios honestly. Run the relevant checks, diagnose failures and correct them before broadening. Keep current and historical evidence separate.

A task is done when its deliverables work, its acceptance is observed, required review is real, relevant regressions pass, documentation is current and continuation records identify the next task. If a genuine prerequisite is unavailable, leave it blocked/not-started and select independent ready work; do not fabricate host capability or approval.

For source-neutral development, use the existing repo-local Python dependencies and deterministic fake-host tests. Do not call models or real services merely to develop schemas. Full installed/model-driven environment claims require their separate P6 evidence.

The owner has authorized this organization/planning/GitHub publication task. Future Copilot development follows the supplied handoff; it does not authorize private source upload, arbitrary paid inference, new providers or production deployment.

## P0: Organized baseline

Milestone exit: Current architecture, traceability, cleanup, Copilot entry point and regression evidence.

### WP-100: Reconcile architecture and organize the development baseline

**Entry:** None. **Owner role:** Integration maintainer. **State:** consult the CSV.
**Requirements:** SF-11, SF-19, SF-20, SF-22, SF-25, SF-26, SF-31, NFR-07, NFR-08, NFR-10. **Scenarios:** TC-101, TC-102.

**Goal:** Make the current implementation, target design, task order, evidence and continuation instructions unambiguous.

**Implementation:** Archive prior planning and publication material; retire the fictional preview; preserve runtime/research bytes; introduce this roadmap and Copilot entry point; validate links, dependency graph, history, and regression checks.

**Owned/proposed paths:** `README.md`; `AGENTS.md`; `.github/`; `docs/`; `scripts/validate_plan.py`; `tests/test_validate_plan.py`. Inspect shared helpers first; coordinate shared-file changes explicitly.

**Positive acceptance:** A fresh contributor can identify the first task, current product limitations, milestone exits and exact checks without private chat context.

**Required negative controls:** Archived decisions cannot silently override the current target; retired preview files are absent and historical cycles remain unchanged.

**Validation and exit:** implement the concrete behavior/negative cases behind the linked scenarios; execute the relevant suites against exact artifacts; inspect results and retain failures/skips; run affected existing v1 regressions. Record actual evidence in VALIDATION_HISTORY and a new cycle, update the task state and next ready task. For live-host work, unit mocks supplement but do not replace the named host/environment observations.

**Stop/recovery:** preserve original state and unrelated changes on failure; classify cause, stale evidence and uncertain effects before retry; do not widen scope, weaken the oracle or reset allowances. Ordinary in-scope corrections continue. Material changes follow HUMAN_DECISIONS.

## P1: Executable contracts and evaluator

Milestone exit: Validated baseline/envelope/task/result schemas, transitions, v1 migration policy, fake host and protected behavioral fixtures.

### WP-110: Define intent baseline and delegated execution envelope

**Entry:** WP-100. **Owner role:** Contracts maintainer. **State:** consult the CSV.
**Requirements:** SF-02, SF-04, SF-10, SF-25, SF-26, NFR-01, NFR-02. **Scenarios:** TC-103, TC-104.

**Goal:** Separate user-owned behavior from revisable technical tactics and permission/resource limits.

**Implementation:** Implement closed versioned IntentBaseline and ExecutionEnvelope records; canonical digests; stable criterion IDs; explicit non-goals, environment, permitted effects and finite bounds; deterministic validation and safe JSON round-trip.

**Owned/proposed paths:** `plugins/sparkforge/runtime/contracts.py`; `plugins/sparkforge/runtime/schemas/`; `tests/test_runtime_contracts.py`. Inspect shared helpers first; coordinate shared-file changes explicitly.

**Positive acceptance:** A technical plan can reference one unchanged intent/envelope; intent or envelope changes yield different bindings and require the appropriate decision.

**Required negative controls:** Reject unknown keys/versions, duplicate criteria, boolean-as-number bounds, unlimited allowances, forged approval fields and missing behavioral acceptance.

**Validation and exit:** implement the concrete behavior/negative cases behind the linked scenarios; execute the relevant suites against exact artifacts; inspect results and retain failures/skips; run affected existing v1 regressions. Record actual evidence in VALIDATION_HISTORY and a new cycle, update the task state and next ready task. For live-host work, unit mocks supplement but do not replace the named host/environment observations.

**Stop/recovery:** preserve original state and unrelated changes on failure; classify cause, stale evidence and uncertain effects before retry; do not widen scope, weaken the oracle or reset allowances. Ordinary in-scope corrections continue. Material changes follow HUMAN_DECISIONS.

### WP-111: Define agent tasks results findings and role contracts

**Entry:** WP-110. **Owner role:** Contracts maintainer. **State:** consult the CSV.
**Requirements:** SF-06, SF-08, SF-20, SF-22, SF-27, SF-28, NFR-02, NFR-08. **Scenarios:** TC-105, TC-106.

**Goal:** Give every worker an explicit assignment and an admissible, typed result.

**Implementation:** Define TaskAssignment, AgentAttempt, AgentResult, Finding and Failure records; bind task/role/intent/plan/candidate/input digests; allowed paths/effects, acceptance IDs, deadline, allowance, evidence references and uncertainty; implement producer-role validation.

**Owned/implemented paths:** `plugins/sparkforge/runtime/agent_contracts.py`; shared helpers in `runtime/contracts.py`; `tests/test_agent_envelopes.py`; shared synthetic `tests/runtime_fixtures.py`. WP-111 keeps worker records in a cohesive sibling module instead of enlarging the intent/envelope module; no unused schema copies. See the [record API](design/DATA_AND_STATE.md#wp-111-worker-contract-api).

**Positive acceptance:** Every planned role can exchange a bounded result whose claims are distinct from host observations and accepted evidence.

**Required negative controls:** Reject wrong-task/wrong-role/stale candidate results, malformed findings, arbitrary filesystem paths and self-issued permissions.

**Validation and exit:** implement the concrete behavior/negative cases behind the linked scenarios; execute the relevant suites against exact artifacts; inspect results and retain failures/skips; run affected existing v1 regressions. Record actual evidence in VALIDATION_HISTORY and a new cycle, update the task state and next ready task. For live-host work, unit mocks supplement but do not replace the named host/environment observations.

**Stop/recovery:** preserve original state and unrelated changes on failure; classify cause, stale evidence and uncertain effects before retry; do not widen scope, weaken the oracle or reset allowances. Ordinary in-scope corrections continue. Material changes follow HUMAN_DECISIONS.

### WP-112: Specify workflow events transitions and idempotency

**Entry:** WP-111. **Owner role:** Runtime maintainer. **State:** consult the CSV.
**Requirements:** SF-09, SF-11, SF-20, SF-27, SF-30, NFR-02, NFR-03. **Scenarios:** TC-107, TC-108.

**Goal:** Make legal workflow progression independent of model prose.

**Implementation:** Implement pure transition guards for planned job/task/attempt states; expected revision checks; command idempotency keys and payload digests; event IDs; stale-result rules; distinguish blocked, failed, unknown and completed.

**Owned/proposed paths:** `plugins/sparkforge/runtime/transitions.py`; `tests/test_workflow_transitions.py`; `docs/design/DATA_AND_STATE.md`. Inspect shared helpers first; coordinate shared-file changes explicitly.

**Positive acceptance:** The same admitted command is replayable without duplicate work; conflicting replay is explicit; completion requires the expected evidence inventory.

**Required negative controls:** Reject impossible transitions, result-before-dispatch, reused key with different payload and completion while an operation is unresolved.

**Validation and exit:** implement the concrete behavior/negative cases behind the linked scenarios; execute the relevant suites against exact artifacts; inspect results and retain failures/skips; run affected existing v1 regressions. Record actual evidence in VALIDATION_HISTORY and a new cycle, update the task state and next ready task. For live-host work, unit mocks supplement but do not replace the named host/environment observations.

**Stop/recovery:** preserve original state and unrelated changes on failure; classify cause, stale evidence and uncertain effects before retry; do not widen scope, weaken the oracle or reset allowances. Ordinary in-scope corrections continue. Material changes follow HUMAN_DECISIONS.

### WP-113: Specify assisted-v1 coexistence and schema migrations

**Entry:** WP-112. **Owner role:** Runtime maintainer. **State:** consult the CSV.
**Requirements:** SF-11, SF-20, SF-25, NFR-02, NFR-03, NFR-05, NFR-07. **Scenarios:** TC-109, TC-110.

**Goal:** Introduce orchestration without rewriting or silently approving existing assisted journals.

**Implementation:** Keep factory.py v1 API and stores separate; define explicit new-store creation and read-only legacy references; reserve schema versioning; test backup-before-migration and transactional rollback for future versioned stores.

**Owned/proposed paths:** `plugins/sparkforge/runtime/migrations.py`; `tests/test_runtime_migrations.py`; `docs/design/DATA_AND_STATE.md`. Inspect shared helpers first; coordinate shared-file changes explicitly.

**Positive acceptance:** Existing v1 fixtures still pass; a v1 journal is neither adopted as a coordinated job nor granted inherited approval.

**Required negative controls:** Unknown future versions and interrupted migration leave originals intact; no in-place conversion of real operator state.

**Validation and exit:** implement the concrete behavior/negative cases behind the linked scenarios; execute the relevant suites against exact artifacts; inspect results and retain failures/skips; run affected existing v1 regressions. Record actual evidence in VALIDATION_HISTORY and a new cycle, update the task state and next ready task. For live-host work, unit mocks supplement but do not replace the named host/environment observations.

**Stop/recovery:** preserve original state and unrelated changes on failure; classify cause, stale evidence and uncertain effects before retry; do not widen scope, weaken the oracle or reset allowances. Ordinary in-scope corrections continue. Material changes follow HUMAN_DECISIONS.

### WP-114: Define host adapter capabilities and deterministic fake host

**Entry:** WP-111. **Owner role:** Host integration maintainer. **State:** consult the CSV.
**Requirements:** SF-13, SF-16, SF-17, SF-22, NFR-01, NFR-05, NFR-06. **Scenarios:** TC-111, TC-112.

**Goal:** Develop coordination without inventing native Copilot APIs or requiring sensitive sources.

**Implementation:** Define capability discovery, dispatch, poll, cancel, reconcile, identity context and usage receipt protocols; implement a scripted fake with deterministic failures and call counters; capability absence returns unsupported before effects.

**Owned/proposed paths:** `plugins/sparkforge/runtime/host.py`; `tests/fakes/fake_host.py`; `tests/test_host_adapter.py`. Inspect shared helpers first; coordinate shared-file changes explicitly.

**Positive acceptance:** Tests can drive all workflow states offline and distinguish dispatch acceptance from completed work.

**Required negative controls:** Reject missing required capabilities, cross-environment receipts, unobserved cancellation claims and unknown usage presented as zero.

**Validation and exit:** implement the concrete behavior/negative cases behind the linked scenarios; execute the relevant suites against exact artifacts; inspect results and retain failures/skips; run affected existing v1 regressions. Record actual evidence in VALIDATION_HISTORY and a new cycle, update the task state and next ready task. For live-host work, unit mocks supplement but do not replace the named host/environment observations.

**Stop/recovery:** preserve original state and unrelated changes on failure; classify cause, stale evidence and uncertain effects before retry; do not widen scope, weaken the oracle or reset allowances. Ordinary in-scope corrections continue. Material changes follow HUMAN_DECISIONS.

### WP-115: Establish protected behavioral acceptance and evaluation fixtures

**Entry:** WP-110. **Owner role:** Independent evaluation maintainer. **State:** consult the CSV.
**Requirements:** SF-06, SF-07, SF-08, SF-24, NFR-02, NFR-08. **Scenarios:** TC-113, TC-114.

**Goal:** Define success and known-bad controls before building the loop.

**Implementation:** Create synthetic component interface, accepted behaviors, hidden/independent scenario definitions, drift examples, seeded implementation defects and a rubric; bind evaluator revision outside coder-owned paths.

**Owned/proposed paths:** `tests/fixtures/factory_scenarios/`; `tests/evaluation/`; `docs/engineering/EVALUATION_PLAN.md`. Inspect shared helpers first; coordinate shared-file changes explicitly.

**Positive acceptance:** The evaluation harness detects each seeded defect and semantic deviation, even when a worker reports success.

**Required negative controls:** A coder-modified test, missing criterion, removed negative case or fabricated passing marker cannot satisfy protected acceptance.

**Validation and exit:** implement the concrete behavior/negative cases behind the linked scenarios; execute the relevant suites against exact artifacts; inspect results and retain failures/skips; run affected existing v1 regressions. Record actual evidence in VALIDATION_HISTORY and a new cycle, update the task state and next ready task. For live-host work, unit mocks supplement but do not replace the named host/environment observations.

**Stop/recovery:** preserve original state and unrelated changes on failure; classify cause, stale evidence and uncertain effects before retry; do not widen scope, weaken the oracle or reset allowances. Ordinary in-scope corrections continue. Material changes follow HUMAN_DECISIONS.

## P2: Deterministic coordination

Milestone exit: Transactional store, serial graph scheduler, materiality admission, job budgets, workspace ownership, check bridge and result admission.

### WP-120: Implement coordinated journal and atomic event storage

**Entry:** WP-112, WP-113. **Owner role:** Runtime maintainer. **State:** consult the CSV.
**Requirements:** SF-11, SF-20, SF-27, SF-30, NFR-02, NFR-03, NFR-04. **Scenarios:** TC-115, TC-116.

**Goal:** Persist intent, plans, tasks, attempts, evidence and operation reservations transactionally.

**Implementation:** Use SQLite with explicit schema/version and optimistic revision guards; atomically commit event plus projection; reserve dispatch before calling a host; retain prior plans and failures; offer read-only status reconstruction.

**Implemented execution contract (WP-120):** The [atomic storage and recovery definition](design/DATA_AND_STATE.md#wp-120-prepared-storage-and-recovery-contract) is now implemented from corrected P1 head `f61a33ddc928fcb2dbf43abc02f4a25979089670`. It supplies one job per coordinated store, immutable records/initial snapshots, persistent command receipts/events, revision-guarded projections and uniquely owned reservations. Each command and all record/event/projection/reservation writes commit together. Durable idempotency is checked before stale-revision rejection; replay cannot restore old state or repeat effects. See the [API/limits](design/DATA_AND_STATE.md#implemented-wp-120-api-and-boundaries).

Coordinated schema v2 and the tested v1-header copy upgrade are implemented without converting assisted stores. Read-only reconstruction is distinct from explicit SQLite recovery. Pending dispatch/lost response/cancel acknowledgement remains unresolved until observation-backed reconciliation; no blind redispatch or assumed-zero consumption. Concrete write-boundary, writer-conflict, owned-process crash, observation-version and parent-cancellation tests exercise these boundaries; real host/power-loss acceptance remains unassessed.

**Owned/proposed paths:** `plugins/sparkforge/runtime/store.py`; the directly dependent schema/version implementation in `runtime/migrations.py`; `tests/test_runtime_store.py`; affected migration/transition tests and living records. Do not create empty modules during preparation. Inspect shared helpers first; coordinate shared-file changes explicitly.

**Positive acceptance:** Restart reconstructs the same state and pending reservations; rejected updates do not partially persist.

**Required negative controls:** Inject transaction failures, concurrent writers, corrupt records and duplicate event IDs; no silent overwrite or success-shaped recovery.

**Validation and exit:** implement the concrete behavior/negative cases behind the linked scenarios; execute the relevant suites against exact artifacts; inspect results and retain failures/skips; run affected existing v1 regressions. Record actual evidence in VALIDATION_HISTORY and a new cycle, update the task state and next ready task. For live-host work, unit mocks supplement but do not replace the named host/environment observations.

**Stop/recovery:** preserve original state and unrelated changes on failure; classify cause, stale evidence and uncertain effects before retry; do not widen scope, weaken the oracle or reset allowances. Ordinary in-scope corrections continue. Material changes follow HUMAN_DECISIONS.

### WP-121: Implement serial dependency scheduler and coordinator

**Entry:** WP-120, WP-111. **Owner role:** Orchestration maintainer. **State:** consult the CSV.
**Requirements:** SF-20, SF-22, SF-27, NFR-03, NFR-06, NFR-07. **Scenarios:** TC-117, TC-118.

**Goal:** Run a deterministic task graph with one active worker initially.

**Implementation:** Validate acyclic task dependencies and required role barriers; admit ready tasks; persist selected task and attempt identity; dispatch through host protocol; distinguish task success from job readiness; stop on cancellation or unresolved reservations.

**Implemented boundary:** See [the serial coordinator API](design/DATA_AND_STATE.md#implemented-wp-121-serial-coordinator). A closed pinned schedule is persisted as an immutable record with capability/job-context bindings. Restartable registration and serial ticks use WP-120's operation ownership and command replay. This initial profile only accepts scripted hosts and unchanged pinned candidates; candidate integration, policy/accounting, dynamic replanning and actual host/whole-job acceptance remain explicit later tasks. Required code/test/runner/reviewer/final-controller barriers cannot be removed to finish early. Unsupported host cancellation still permits read-only outcome reconciliation.

**Owned/proposed paths:** `plugins/sparkforge/runtime/coordinator.py`; `plugins/sparkforge/runtime/scheduler.py`; `tests/test_scheduler.py`. Inspect shared helpers first; coordinate shared-file changes explicitly.

**Positive acceptance:** Repeated scheduler ticks produce one dispatch per admitted operation and never skip required dependency or review work.

**Required negative controls:** Reject graph cycles, missing tasks, overlapping active ownership, duplicate dispatch and job completion after only a worker completion.

**Validation and exit:** implement the concrete behavior/negative cases behind the linked scenarios; execute the relevant suites against exact artifacts; inspect results and retain failures/skips; run affected existing v1 regressions. Record actual evidence in VALIDATION_HISTORY and a new cycle, update the task state and next ready task. For live-host work, unit mocks supplement but do not replace the named host/environment observations.

**Stop/recovery:** preserve original state and unrelated changes on failure; classify cause, stale evidence and uncertain effects before retry; do not widen scope, weaken the oracle or reset allowances. Ordinary in-scope corrections continue. Material changes follow HUMAN_DECISIONS.

### WP-122: Implement materiality classification and decision admission

**Entry:** WP-121, WP-110. **Owner role:** Control-plane maintainer. **State:** consult the CSV.
**Requirements:** SF-04, SF-10, SF-24, SF-25, SF-26, NFR-01, NFR-02. **Scenarios:** TC-119, TC-120.

**Goal:** Allow ordinary bounded work while escalating actual changes to intent or authority.

**Implementation:** Implement materiality rules, decision requests, current-object binding, revocation and envelope membership; independently verify proposed deltas; keep human decisions as host ingress assertions until authentic origin is qualified.

**Owned/proposed paths:** `plugins/sparkforge/runtime/policy.py`; `tests/test_materiality_policy.py`; `docs/design/HUMAN_DECISIONS.md`. Inspect shared helpers first; coordinate shared-file changes explicitly.

**Positive acceptance:** An in-scope repair or internal plan adjustment continues without another intent approval; a changed acceptance condition or permission envelope cannot.

**Required negative controls:** Worker confidence, silence, label changes, cumulative small scope expansions and stale decisions never bypass the decision boundary.

**Validation and exit:** implement the concrete behavior/negative cases behind the linked scenarios; execute the relevant suites against exact artifacts; inspect results and retain failures/skips; run affected existing v1 regressions. Record actual evidence in VALIDATION_HISTORY and a new cycle, update the task state and next ready task. For live-host work, unit mocks supplement but do not replace the named host/environment observations.

**Stop/recovery:** preserve original state and unrelated changes on failure; classify cause, stale evidence and uncertain effects before retry; do not widen scope, weaken the oracle or reset allowances. Ordinary in-scope corrections continue. Material changes follow HUMAN_DECISIONS.

### WP-123: Implement job and agent resource accounting

**Entry:** WP-122. **Owner role:** Runtime maintainer. **State:** consult the CSV.
**Requirements:** SF-09, SF-29, NFR-03, NFR-06. **Scenarios:** TC-121, TC-122.

**Goal:** Bound the whole factory loop rather than only individual check processes.

**Implementation:** Reserve attempt/time/model-call allowances before dispatch; track reported tokens/cost only when host exposes reliable usage; preserve unknown usage; maintain job-wide totals across repairs and replans; separate optional extensions from remaining budget.

**Owned/proposed paths:** `plugins/sparkforge/runtime/budgets.py`; `tests/test_runtime_budgets.py`. Inspect shared helpers first; coordinate shared-file changes explicitly.

**Positive acceptance:** Exhausted allowance stops new admission with a clear reason; changing agents, tasks or plans does not reset job totals.

**Required negative controls:** Reject negative/overflow/nonfinite values, retry storms, hidden provider substitution and unknown cost treated as free.

**Validation and exit:** implement the concrete behavior/negative cases behind the linked scenarios; execute the relevant suites against exact artifacts; inspect results and retain failures/skips; run affected existing v1 regressions. Record actual evidence in VALIDATION_HISTORY and a new cycle, update the task state and next ready task. For live-host work, unit mocks supplement but do not replace the named host/environment observations.

**Stop/recovery:** preserve original state and unrelated changes on failure; classify cause, stale evidence and uncertain effects before retry; do not widen scope, weaken the oracle or reset allowances. Ordinary in-scope corrections continue. Material changes follow HUMAN_DECISIONS.

### WP-124: Implement candidate ownership and workspace adapter

**Entry:** WP-121. **Owner role:** Workspace maintainer. **State:** consult the CSV.
**Requirements:** SF-05, SF-20, SF-27, NFR-01, NFR-02, NFR-07. **Scenarios:** TC-123, TC-124.

**Goal:** Track exactly what each worker may change and what belongs in the candidate.

**Implementation:** Inspect dirty state without reset; allocate owned paths; capture full candidate manifest including declared dependency/config files; compare actual changes; preserve unrelated content; define integration ownership and worktree lifecycle.

**Owned/proposed paths:** `plugins/sparkforge/runtime/workspace.py`; `tests/test_workspace_ownership.py`. Inspect shared helpers first; coordinate shared-file changes explicitly.

**Positive acceptance:** A valid result identifies its exact diff and content digests; undeclared changes block integration and remain visible.

**Required negative controls:** Reject escaping paths, symlink aliases, changing protected acceptance files, overwriting user changes and assuming worktrees are OS sandboxes.

**Validation and exit:** implement the concrete behavior/negative cases behind the linked scenarios; execute the relevant suites against exact artifacts; inspect results and retain failures/skips; run affected existing v1 regressions. Record actual evidence in VALIDATION_HISTORY and a new cycle, update the task state and next ready task. For live-host work, unit mocks supplement but do not replace the named host/environment observations.

**Stop/recovery:** preserve original state and unrelated changes on failure; classify cause, stale evidence and uncertain effects before retry; do not widen scope, weaken the oracle or reset allowances. Ordinary in-scope corrections continue. Material changes follow HUMAN_DECISIONS.

### WP-125: Bridge declared checks and current evidence to the assisted runner

**Entry:** WP-120, WP-115. **Owner role:** Execution maintainer. **State:** consult the CSV.
**Requirements:** SF-07, SF-08, SF-20, NFR-02, NFR-06, NFR-08. **Scenarios:** TC-125, TC-126.

**Goal:** Reuse bounded execution and stale-evidence rules through an explicit compatibility boundary.

**Implementation:** Map coordinated check requests onto existing runner semantics; identify what is shared versus wrapped; bind coordinated intent/plan/task and legacy runner receipts; require current candidate and protected check inventory; leave v1 behavior unchanged unless a separately tested API extraction is justified.

**Owned/proposed paths:** `plugins/sparkforge/runtime/checks.py`; `tests/test_check_bridge.py`; `plugins/sparkforge/scripts/factory.py`. Inspect shared helpers first; coordinate shared-file changes explicitly.

**Positive acceptance:** Current checks produce admissible evidence and changed candidates invalidate affected checks and reviews in both layers.

**Required negative controls:** Reject imported synthetic assertions as real results, mismatched runner receipts, incomplete output and fabricated approved v1 decisions.

**Validation and exit:** implement the concrete behavior/negative cases behind the linked scenarios; execute the relevant suites against exact artifacts; inspect results and retain failures/skips; run affected existing v1 regressions. Record actual evidence in VALIDATION_HISTORY and a new cycle, update the task state and next ready task. For live-host work, unit mocks supplement but do not replace the named host/environment observations.

**Stop/recovery:** preserve original state and unrelated changes on failure; classify cause, stale evidence and uncertain effects before retry; do not widen scope, weaken the oracle or reset allowances. Ordinary in-scope corrections continue. Material changes follow HUMAN_DECISIONS.

### WP-126: Implement agent dispatch result admission and cancellation protocol

**Entry:** WP-121, WP-114. **Owner role:** Host integration maintainer. **State:** consult the CSV.
**Requirements:** SF-13, SF-22, SF-27, SF-30, NFR-01, NFR-02, NFR-03. **Scenarios:** TC-127, TC-128.

**Goal:** Connect the coordinator to real or fake worker execution without trusting completion prose.

**Implementation:** Persist operation keys; dispatch versioned assignments; poll boundedly; validate result schemas, actor/role and evidence bindings; record usage and pending/unknown completion; reject late revoked results; make cancellations requests until observed stopped.

**Owned/proposed paths:** `plugins/sparkforge/runtime/dispatch.py`; `tests/test_dispatch_admission.py`. Inspect shared helpers first; coordinate shared-file changes explicitly.

**Positive acceptance:** A completed worker turn becomes a task result only after all admission guards pass.

**Required negative controls:** A lost response cannot trigger another effectful call; duplicate, out-of-order, wrong producer and stale plan results remain uncredited.

**Validation and exit:** implement the concrete behavior/negative cases behind the linked scenarios; execute the relevant suites against exact artifacts; inspect results and retain failures/skips; run affected existing v1 regressions. Record actual evidence in VALIDATION_HISTORY and a new cycle, update the task state and next ready task. For live-host work, unit mocks supplement but do not replace the named host/environment observations.

**Stop/recovery:** preserve original state and unrelated changes on failure; classify cause, stale evidence and uncertain effects before retry; do not widen scope, weaken the oracle or reset allowances. Ordinary in-scope corrections continue. Material changes follow HUMAN_DECISIONS.

## P3: Platform brain and intent control

Milestone exit: Profile/context/intake/reuse pipeline, brain task planner and independent drift checkpoints.

### WP-130: Define platform and environment capability profiles

**Entry:** WP-110. **Owner role:** Platform integration maintainer. **State:** consult the CSV.
**Requirements:** SF-03, SF-12, SF-16, SF-17, SF-23, NFR-01, NFR-05, NFR-10. **Scenarios:** TC-129, TC-130.

**Goal:** Give the brain explicit supported component contracts and environment-local facts.

**Implementation:** Define component kinds, interfaces, packaging rules, tools, data routes, source revisions and unknowns; create a clearly fictional synthetic profile; let real corp/acro profiles be supplied outside Git; bind every run to one profile.

**Owned/proposed paths:** `plugins/sparkforge/runtime/platform.py`; `tests/fixtures/platform/`; `tests/test_platform_profiles.py`. Inspect shared helpers first; coordinate shared-file changes explicitly.

**Positive acceptance:** A request can be checked against a selected profile and unsupported outputs explained without guessing private SPARK behavior.

**Required negative controls:** Reject cross-environment references, unauthenticated permission flags and unknown capabilities silently assumed supported.

**Validation and exit:** implement the concrete behavior/negative cases behind the linked scenarios; execute the relevant suites against exact artifacts; inspect results and retain failures/skips; run affected existing v1 regressions. Record actual evidence in VALIDATION_HISTORY and a new cycle, update the task state and next ready task. For live-host work, unit mocks supplement but do not replace the named host/environment observations.

**Stop/recovery:** preserve original state and unrelated changes on failure; classify cause, stale evidence and uncertain effects before retry; do not widen scope, weaken the oracle or reset allowances. Ordinary in-scope corrections continue. Material changes follow HUMAN_DECISIONS.

### WP-131: Integrate source snapshots context selection and freshness

**Entry:** WP-130. **Owner role:** Knowledge maintainer. **State:** consult the CSV.
**Requirements:** SF-01, SF-03, SF-12, SF-23, NFR-02, NFR-04, NFR-07. **Scenarios:** TC-131, TC-132.

**Goal:** Reuse verified source reading with task-specific context and visible gaps.

**Implementation:** Wrap knowledge.py rather than replacing its integrity checks; bind selected excerpts and original locators; record freshness/permission evidence separately; expose truncation, conflicting guidance, cache invalidation and missing comparison; support fake/local profiles first.

**Owned/proposed paths:** `plugins/sparkforge/runtime/context.py`; `plugins/sparkforge/scripts/knowledge.py`; `tests/test_context_selection.py`. Inspect shared helpers first; coordinate shared-file changes explicitly.

**Positive acceptance:** Every platform/reuse decision can cite the exact relevant original implementation and applicable guidance.

**Required negative controls:** A lexical miss, stale index, omitted excerpt or injected source instruction cannot become evidence of absence or executable policy.

**Validation and exit:** implement the concrete behavior/negative cases behind the linked scenarios; execute the relevant suites against exact artifacts; inspect results and retain failures/skips; run affected existing v1 regressions. Record actual evidence in VALIDATION_HISTORY and a new cycle, update the task state and next ready task. For live-host work, unit mocks supplement but do not replace the named host/environment observations.

**Stop/recovery:** preserve original state and unrelated changes on failure; classify cause, stale evidence and uncertain effects before retry; do not widen scope, weaken the oracle or reset allowances. Ordinary in-scope corrections continue. Material changes follow HUMAN_DECISIONS.

### WP-132: Implement focused intake and decision questions

**Entry:** WP-131, WP-110. **Owner role:** Interaction maintainer. **State:** consult the CSV.
**Requirements:** SF-01, SF-02, SF-04, SF-25, NFR-09. **Scenarios:** TC-133, TC-134.

**Goal:** Turn rough ideas and existing content into a bounded problem without repeatedly asking known facts.

**Implementation:** Extract outcome/audience/inputs/non-goals; resolve facts from selected context; rank consequential ambiguities; ask only questions affecting behavior, fit or authority; preserve user wording and pending decisions; bind resulting criteria to the intent baseline.

**Owned/proposed paths:** `plugins/sparkforge/runtime/intake.py`; `tests/test_intake_flow.py`. Inspect shared helpers first; coordinate shared-file changes explicitly.

**Positive acceptance:** Equivalent supplied facts are reused and a material unresolved ambiguity is presented as a focused question.

**Required negative controls:** Reject fabricated answers, question loops, hidden assumptions about sensitive sources and coding before a usable accepted intent.

**Validation and exit:** implement the concrete behavior/negative cases behind the linked scenarios; execute the relevant suites against exact artifacts; inspect results and retain failures/skips; run affected existing v1 regressions. Record actual evidence in VALIDATION_HISTORY and a new cycle, update the task state and next ready task. For live-host work, unit mocks supplement but do not replace the named host/environment observations.

**Stop/recovery:** preserve original state and unrelated changes on failure; classify cause, stale evidence and uncertain effects before retry; do not widen scope, weaken the oracle or reset allowances. Ordinary in-scope corrections continue. Material changes follow HUMAN_DECISIONS.

### WP-133: Implement evidence-backed reuse update or new assessment

**Entry:** WP-132. **Owner role:** Platform brain maintainer. **State:** consult the CSV.
**Requirements:** SF-03, SF-05, SF-12, SF-23, NFR-07, NFR-08. **Scenarios:** TC-135, TC-136.

**Goal:** Fit solutions to existing platform capabilities before generating new components.

**Implementation:** Inspect candidate manifests plus relevant source/tests; assess compatibility, ownership and delta size; distinguish direct reuse, adaptation and new component; record reasons and alternatives; route missing source comparison explicitly.

**Owned/proposed paths:** `plugins/sparkforge/runtime/reuse.py`; `tests/test_reuse_assessment.py`. Inspect shared helpers first; coordinate shared-file changes explicitly.

**Positive acceptance:** Brownfield tasks preserve relevant existing contracts and explain why the chosen change is the smallest suitable option.

**Required negative controls:** Component-name matches alone, absent search hits and unverifiable platform capabilities cannot justify the decision.

**Validation and exit:** implement the concrete behavior/negative cases behind the linked scenarios; execute the relevant suites against exact artifacts; inspect results and retain failures/skips; run affected existing v1 regressions. Record actual evidence in VALIDATION_HISTORY and a new cycle, update the task state and next ready task. For live-host work, unit mocks supplement but do not replace the named host/environment observations.

**Stop/recovery:** preserve original state and unrelated changes on failure; classify cause, stale evidence and uncertain effects before retry; do not widen scope, weaken the oracle or reset allowances. Ordinary in-scope corrections continue. Material changes follow HUMAN_DECISIONS.

### WP-134: Implement the platform brain and task planner

**Entry:** WP-133, WP-111. **Owner role:** Brain maintainer. **State:** consult the CSV.
**Requirements:** SF-05, SF-20, SF-22, SF-23, SF-27, NFR-06, NFR-07. **Scenarios:** TC-137, TC-138.

**Goal:** Translate accepted intent and platform constraints into a bounded engineering task graph.

**Implementation:** Produce versioned ExecutionPlan with role assignments, criterion coverage, dependency order, owned paths, tests, review barriers and allowances; justify architecture/reuse; identify unavailable capabilities without inventing launchers.

**Owned/proposed paths:** `plugins/sparkforge/runtime/planning.py`; `docs/roles/brain.md`; `tests/test_brain_planning.py`. Inspect shared helpers first; coordinate shared-file changes explicitly.

**Positive acceptance:** Every criterion has an implementation/evaluation route and the graph can be admitted by the deterministic scheduler.

**Required negative controls:** Reject missing roles, uncovered criteria, circular tasks, unbounded repairs and plans that expand the accepted envelope.

**Validation and exit:** implement the concrete behavior/negative cases behind the linked scenarios; execute the relevant suites against exact artifacts; inspect results and retain failures/skips; run affected existing v1 regressions. Record actual evidence in VALIDATION_HISTORY and a new cycle, update the task state and next ready task. For live-host work, unit mocks supplement but do not replace the named host/environment observations.

**Stop/recovery:** preserve original state and unrelated changes on failure; classify cause, stale evidence and uncertain effects before retry; do not widen scope, weaken the oracle or reset allowances. Ordinary in-scope corrections continue. Material changes follow HUMAN_DECISIONS.

### WP-135: Implement independent intent-control checkpoints

**Entry:** WP-134, WP-115, WP-122. **Owner role:** Intent controller maintainer. **State:** consult the CSV.
**Requirements:** SF-04, SF-08, SF-10, SF-22, SF-24, SF-26, NFR-02, NFR-08. **Scenarios:** TC-139, TC-140.

**Goal:** Detect semantic drift before planning, integration, repair and handoff can advance.

**Implementation:** Compare baseline, proposed plan/delta and behavioral evidence; return allow/rework/material-decision/insufficient-evidence with cited deviations; require current controller verdict at transition barriers; keep controller read-only over intent, oracle and implementation.

**Owned/proposed paths:** `plugins/sparkforge/runtime/intent_control.py`; `docs/roles/intent-controller.md`; `tests/test_intent_controller.py`. Inspect shared helpers first; coordinate shared-file changes explicitly.

**Positive acceptance:** A technically passing but behaviorally different solution is blocked and ordinary equivalent implementation changes remain allowed.

**Required negative controls:** Brain cannot overwrite controller verdicts, rewrite acceptance to pass, swap reviewer or refresh an old opinion onto a new candidate.

**Validation and exit:** implement the concrete behavior/negative cases behind the linked scenarios; execute the relevant suites against exact artifacts; inspect results and retain failures/skips; run affected existing v1 regressions. Record actual evidence in VALIDATION_HISTORY and a new cycle, update the task state and next ready task. For live-host work, unit mocks supplement but do not replace the named host/environment observations.

**Stop/recovery:** preserve original state and unrelated changes on failure; classify cause, stale evidence and uncertain effects before retry; do not widen scope, weaken the oracle or reset allowances. Ordinary in-scope corrections continue. Material changes follow HUMAN_DECISIONS.

## P4: Complete multi-agent engineering loop

Milestone exit: Coder, independent test author, runner, reviewer, diagnosis, bounded repair/replanning and first full synthetic journey.

### WP-140: Implement scoped coder agent execution

**Entry:** WP-134, WP-124, WP-126. **Owner role:** Coder integration maintainer. **State:** consult the CSV.
**Requirements:** SF-05, SF-20, SF-22, SF-27, NFR-01, NFR-07. **Scenarios:** TC-141, TC-142.

**Goal:** Create or adapt only the assigned component using the selected host.

**Implementation:** Build coder context from current plan and relevant source; dispatch bounded work; admit declared diff and rationale; preserve user edits; report partial/unavailable work and exact artifact references; never let coder write intent/oracle/control policy.

**Owned/proposed paths:** `plugins/sparkforge/runtime/roles/coder.py`; `docs/roles/coder.md`; `tests/test_coder_role.py`. Inspect shared helpers first; coordinate shared-file changes explicitly.

**Positive acceptance:** Both a new synthetic component and a brownfield delta can be integrated under explicit ownership.

**Required negative controls:** Reject out-of-scope files, missing implementations, unrequested dependencies and changed acceptance disguised as a repair.

**Validation and exit:** implement the concrete behavior/negative cases behind the linked scenarios; execute the relevant suites against exact artifacts; inspect results and retain failures/skips; run affected existing v1 regressions. Record actual evidence in VALIDATION_HISTORY and a new cycle, update the task state and next ready task. For live-host work, unit mocks supplement but do not replace the named host/environment observations.

**Stop/recovery:** preserve original state and unrelated changes on failure; classify cause, stale evidence and uncertain effects before retry; do not widen scope, weaken the oracle or reset allowances. Ordinary in-scope corrections continue. Material changes follow HUMAN_DECISIONS.

### WP-141: Implement independent test-author agent execution

**Entry:** WP-115, WP-126. **Owner role:** Test integration maintainer. **State:** consult the CSV.
**Requirements:** SF-06, SF-22, SF-24, NFR-02, NFR-08. **Scenarios:** TC-143, TC-144.

**Goal:** Generate useful tests from behavior independently of coder self-assessment.

**Implementation:** Supply baseline/platform contracts and approved oracle but limit solution anchoring; require normal, edge, error and negative cases; preserve stable criterion mapping; validate generated tests detect seeded defects before credit.

**Owned/proposed paths:** `plugins/sparkforge/runtime/roles/test_author.py`; `docs/roles/test-author.md`; `tests/test_test_author_role.py`. Inspect shared helpers first; coordinate shared-file changes explicitly.

**Positive acceptance:** Tests assess externally observable behavior and complement protected evaluator cases.

**Required negative controls:** Reject implementation-mirroring assertions, disabled tests, weakened expectations and self-reported coverage without executed results.

**Validation and exit:** implement the concrete behavior/negative cases behind the linked scenarios; execute the relevant suites against exact artifacts; inspect results and retain failures/skips; run affected existing v1 regressions. Record actual evidence in VALIDATION_HISTORY and a new cycle, update the task state and next ready task. For live-host work, unit mocks supplement but do not replace the named host/environment observations.

**Stop/recovery:** preserve original state and unrelated changes on failure; classify cause, stale evidence and uncertain effects before retry; do not widen scope, weaken the oracle or reset allowances. Ordinary in-scope corrections continue. Material changes follow HUMAN_DECISIONS.

### WP-142: Implement deterministic test-runner role

**Entry:** WP-125, WP-141. **Owner role:** Execution maintainer. **State:** consult the CSV.
**Requirements:** SF-07, SF-22, SF-29, NFR-02, NFR-06, NFR-08. **Scenarios:** TC-145, TC-146.

**Goal:** Execute the complete declared suite and retain usable evidence for diagnosis.

**Implementation:** Resolve exact approved commands; reserve checks and allowance; collect exit/completion/output bindings; detect missing cases/reporters, timeouts and truncation; produce structured failures and rerun affected plus mandatory regression checks.

**Owned/proposed paths:** `plugins/sparkforge/runtime/roles/test_runner.py`; `docs/roles/test-runner.md`; `tests/test_test_runner_role.py`. Inspect shared helpers first; coordinate shared-file changes explicitly.

**Positive acceptance:** All required checks are accounted for on the current candidate; skips and unavailable checks remain explicit.

**Required negative controls:** Reject zero-exit with incomplete results, a single green test substituting for the inventory and retries that erase failures.

**Validation and exit:** implement the concrete behavior/negative cases behind the linked scenarios; execute the relevant suites against exact artifacts; inspect results and retain failures/skips; run affected existing v1 regressions. Record actual evidence in VALIDATION_HISTORY and a new cycle, update the task state and next ready task. For live-host work, unit mocks supplement but do not replace the named host/environment observations.

**Stop/recovery:** preserve original state and unrelated changes on failure; classify cause, stale evidence and uncertain effects before retry; do not widen scope, weaken the oracle or reset allowances. Ordinary in-scope corrections continue. Material changes follow HUMAN_DECISIONS.

### WP-143: Implement independent quality and security review

**Entry:** WP-135, WP-142. **Owner role:** Review integration maintainer. **State:** consult the CSV.
**Requirements:** SF-08, SF-14, SF-22, SF-24, NFR-01, NFR-02, NFR-08. **Scenarios:** TC-147, TC-148.

**Goal:** Review current code, behavioral evidence, platform fit and relevant security concerns independently.

**Implementation:** Capture review context before inspection; use selected host reviewer capability; issue severity-tagged findings and criterion references; require all configured reviewer roles; invalidate on changed code/evidence; report unavailable genuine independence.

**Owned/proposed paths:** `plugins/sparkforge/runtime/roles/reviewer.py`; `docs/roles/reviewer.md`; `tests/test_review_barrier.py`. Inspect shared helpers first; coordinate shared-file changes explicitly.

**Positive acceptance:** Readiness requires complete current checks, controller alignment and required independent review.

**Required negative controls:** Reject builder self-review under a new label, stale-token refresh, missing reviewers, ignored blocking findings and fabricated security assurance.

**Validation and exit:** implement the concrete behavior/negative cases behind the linked scenarios; execute the relevant suites against exact artifacts; inspect results and retain failures/skips; run affected existing v1 regressions. Record actual evidence in VALIDATION_HISTORY and a new cycle, update the task state and next ready task. For live-host work, unit mocks supplement but do not replace the named host/environment observations.

**Stop/recovery:** preserve original state and unrelated changes on failure; classify cause, stale evidence and uncertain effects before retry; do not widen scope, weaken the oracle or reset allowances. Ordinary in-scope corrections continue. Material changes follow HUMAN_DECISIONS.

### WP-144: Implement error diagnosis and failure classification

**Entry:** WP-142, WP-111. **Owner role:** Diagnosis maintainer. **State:** consult the CSV.
**Requirements:** SF-07, SF-09, SF-22, SF-28, NFR-03, NFR-09. **Scenarios:** TC-149, TC-150.

**Goal:** Explain the failing behavior before selecting a recovery action.

**Implementation:** Consume bound failures, logs within retention limits, reproducer and current diff; classify implementation/test/environment/intent/stale/uncertain/budget causes; return evidence, likely cause, alternatives and smallest next action; use unknown when evidence is insufficient.

**Owned/proposed paths:** `plugins/sparkforge/runtime/roles/diagnostician.py`; `docs/roles/diagnostician.md`; `tests/test_failure_classification.py`. Inspect shared helpers first; coordinate shared-file changes explicitly.

**Positive acceptance:** Seeded failures route to the right class with reproducible evidence and no direct uncontrolled retry.

**Required negative controls:** Reject diagnosis that changes requirements, hides uncertainty, changes provider or treats infrastructure denial as a coding defect.

**Validation and exit:** implement the concrete behavior/negative cases behind the linked scenarios; execute the relevant suites against exact artifacts; inspect results and retain failures/skips; run affected existing v1 regressions. Record actual evidence in VALIDATION_HISTORY and a new cycle, update the task state and next ready task. For live-host work, unit mocks supplement but do not replace the named host/environment observations.

**Stop/recovery:** preserve original state and unrelated changes on failure; classify cause, stale evidence and uncertain effects before retry; do not widen scope, weaken the oracle or reset allowances. Ordinary in-scope corrections continue. Material changes follow HUMAN_DECISIONS.

### WP-145: Implement bounded repair routing and progress detection

**Entry:** WP-140, WP-143, WP-144, WP-123. **Owner role:** Orchestration maintainer. **State:** consult the CSV.
**Requirements:** SF-09, SF-10, SF-22, SF-26, SF-28, SF-29, NFR-03, NFR-06, NFR-08. **Scenarios:** TC-151, TC-152.

**Goal:** Automatically correct in-scope defects and rerun evidence without unnecessary human approval.

**Implementation:** Route diagnoses to coder/test-author/environment handler; preserve the baseline and protected oracle; invalidate affected evidence; measure repeated failure signatures and unchanged candidates; enforce job-wide bounds; obtain controller recheck and independent review after repair.

**Owned/proposed paths:** `plugins/sparkforge/runtime/repair.py`; `tests/test_repair_loop.py`. Inspect shared helpers first; coordinate shared-file changes explicitly.

**Positive acceptance:** A seeded defect is repaired within the original envelope without user intervention and all relevant evidence is refreshed.

**Required negative controls:** Stop repeated no-progress fixes, exhausted resources, scope changes, weakened tests and unresolved external effects.

**Validation and exit:** implement the concrete behavior/negative cases behind the linked scenarios; execute the relevant suites against exact artifacts; inspect results and retain failures/skips; run affected existing v1 regressions. Record actual evidence in VALIDATION_HISTORY and a new cycle, update the task state and next ready task. For live-host work, unit mocks supplement but do not replace the named host/environment observations.

**Stop/recovery:** preserve original state and unrelated changes on failure; classify cause, stale evidence and uncertain effects before retry; do not widen scope, weaken the oracle or reset allowances. Ordinary in-scope corrections continue. Material changes follow HUMAN_DECISIONS.

### WP-146: Implement technical replanning under controller review

**Entry:** WP-145, WP-135. **Owner role:** Brain maintainer. **State:** consult the CSV.
**Requirements:** SF-10, SF-23, SF-24, SF-25, SF-26, SF-27, SF-29, NFR-02, NFR-06. **Scenarios:** TC-153, TC-154.

**Goal:** Change engineering tactics when a repair strategy fails while preserving user intent.

**Implementation:** Create explicit plan revisions and supersession links; cancel/reconcile affected work; retain unchanged evidence only under an explicit dependency-impact rule; obtain controller verdict; update task graph without resetting budgets or accepting stale results.

**Owned/proposed paths:** `plugins/sparkforge/runtime/replanning.py`; `tests/test_replanning.py`. Inspect shared helpers first; coordinate shared-file changes explicitly.

**Positive acceptance:** An equivalent alternative strategy proceeds automatically inside the envelope; altered behavior generates a material decision request.

**Required negative controls:** Reject cumulative scope creep, dropped criteria, silently reduced check inventory and late completion from a superseded plan.

**Validation and exit:** implement the concrete behavior/negative cases behind the linked scenarios; execute the relevant suites against exact artifacts; inspect results and retain failures/skips; run affected existing v1 regressions. Record actual evidence in VALIDATION_HISTORY and a new cycle, update the task state and next ready task. For live-host work, unit mocks supplement but do not replace the named host/environment observations.

**Stop/recovery:** preserve original state and unrelated changes on failure; classify cause, stale evidence and uncertain effects before retry; do not widen scope, weaken the oracle or reset allowances. Ordinary in-scope corrections continue. Material changes follow HUMAN_DECISIONS.

### WP-147: Demonstrate the complete coordinated factory slice

**Entry:** WP-146, WP-143. **Owner role:** Integration maintainer. **State:** consult the CSV.
**Requirements:** SF-01, SF-02, SF-03, SF-05, SF-06, SF-07, SF-08, SF-09, SF-11, SF-22, SF-23, SF-24, SF-25, SF-26, SF-27, SF-28, SF-29, NFR-08, NFR-09. **Scenarios:** TC-155, TC-156.

**Goal:** Prove cooperation across roles on a useful synthetic platform component change.

**Implementation:** Run intake/reuse/brain/controller/coder/test/review/handoff through the coordinator and fake host; inject code defect, passing-but-drifting solution and budget exhaustion; collect exact artifacts and agent attempt counts; keep fixture-scripted behavior labeled.

**Owned/proposed paths:** `tests/test_factory_journeys.py`; `tests/fixtures/factory_scenarios/`; `docs/specs/FIRST_FACTORY_SLICE.md`. Inspect shared helpers first; coordinate shared-file changes explicitly.

**Positive acceptance:** The accepted result, repair and drift barriers satisfy FIRST_FACTORY_SLICE; local fixture success is distinguished from live model success.

**Required negative controls:** No mocked repair or invented reviewer can be reported as actual model-driven acceptance; incomplete roles or artifacts prevent handoff.

**Validation and exit:** implement the concrete behavior/negative cases behind the linked scenarios; execute the relevant suites against exact artifacts; inspect results and retain failures/skips; run affected existing v1 regressions. Record actual evidence in VALIDATION_HISTORY and a new cycle, update the task state and next ready task. For live-host work, unit mocks supplement but do not replace the named host/environment observations.

**Stop/recovery:** preserve original state and unrelated changes on failure; classify cause, stale evidence and uncertain effects before retry; do not widen scope, weaken the oracle or reset allowances. Ordinary in-scope corrections continue. Material changes follow HUMAN_DECISIONS.

## P5: Recovery feedback and usability

Milestone exit: Restart/cancel/revocation, feedback, readable status, combined faults and material-approval usability.

### WP-150: Implement restart recovery and operation reconciliation

**Entry:** WP-147, WP-120. **Owner role:** Recovery maintainer. **State:** consult the CSV.
**Requirements:** SF-09, SF-11, SF-30, NFR-02, NFR-03, NFR-04. **Scenarios:** TC-157, TC-158.

**Goal:** Resume durable jobs after process loss without replaying unknown effects.

**Implementation:** Inspect pending dispatch/check/effect reservations; query host by operation identity; credit only current completed evidence; preserve unknown outcomes; require explicit reconciliation where observability cannot establish completion; test crash points before/after reservation, dispatch and result persistence.

**Owned/proposed paths:** `plugins/sparkforge/runtime/recovery.py`; `tests/test_restart_recovery.py`. Inspect shared helpers first; coordinate shared-file changes explicitly.

**Positive acceptance:** Each crash point has an explicit recovery path and no duplicate effect under tested host capabilities.

**Required negative controls:** Do not infer not-started from no response, use PIDs as permanent identities or recover unknown usage as zero.

**Validation and exit:** implement the concrete behavior/negative cases behind the linked scenarios; execute the relevant suites against exact artifacts; inspect results and retain failures/skips; run affected existing v1 regressions. Record actual evidence in VALIDATION_HISTORY and a new cycle, update the task state and next ready task. For live-host work, unit mocks supplement but do not replace the named host/environment observations.

**Stop/recovery:** preserve original state and unrelated changes on failure; classify cause, stale evidence and uncertain effects before retry; do not widen scope, weaken the oracle or reset allowances. Ordinary in-scope corrections continue. Material changes follow HUMAN_DECISIONS.

### WP-151: Implement cancellation revocation and late-result handling

**Entry:** WP-150, WP-122. **Owner role:** Control-plane maintainer. **State:** consult the CSV.
**Requirements:** SF-04, SF-09, SF-10, SF-30, NFR-01, NFR-03, NFR-06. **Scenarios:** TC-159, TC-160.

**Goal:** Stop new admission immediately while accurately reporting already-started effects.

**Implementation:** Persist cancel/revocation events; request owned host stops; revoke stale task authority; distinguish requested/stopped/unknown; quarantine late results; reconcile external effects under the actual envelope.

**Owned/proposed paths:** `plugins/sparkforge/runtime/cancellation.py`; `tests/test_cancel_revocation.py`. Inspect shared helpers first; coordinate shared-file changes explicitly.

**Positive acceptance:** No new work begins after cancellation or revoked intent/envelope; unresolved descendants remain visible.

**Required negative controls:** A cancel acknowledgement alone cannot become proof all side effects stopped; late success cannot resurrect a cancelled job.

**Validation and exit:** implement the concrete behavior/negative cases behind the linked scenarios; execute the relevant suites against exact artifacts; inspect results and retain failures/skips; run affected existing v1 regressions. Record actual evidence in VALIDATION_HISTORY and a new cycle, update the task state and next ready task. For live-host work, unit mocks supplement but do not replace the named host/environment observations.

**Stop/recovery:** preserve original state and unrelated changes on failure; classify cause, stale evidence and uncertain effects before retry; do not widen scope, weaken the oracle or reset allowances. Ordinary in-scope corrections continue. Material changes follow HUMAN_DECISIONS.

### WP-152: Implement feedback defect and intent-change routing

**Entry:** WP-147, WP-135. **Owner role:** Interaction maintainer. **State:** consult the CSV.
**Requirements:** SF-02, SF-04, SF-10, SF-24, SF-26, NFR-02, NFR-09. **Scenarios:** TC-161, TC-162.

**Goal:** Continue development from user feedback without losing the accepted baseline or historical evidence.

**Implementation:** Bind feedback to delivered candidate; deduplicate equivalent submissions; classify bug/clarification/new requirement; repair bugs within allowance; create explicit new intent revision for changed goals; preserve attribution and previous outcome.

**Owned/proposed paths:** `plugins/sparkforge/runtime/feedback.py`; `tests/test_feedback_routing.py`. Inspect shared helpers first; coordinate shared-file changes explicitly.

**Positive acceptance:** A bug enters bounded repair; a new feature creates a reviewable delta and correct decision request.

**Required negative controls:** Reject stale feedback applied to another component, duplicated jobs and scope expansion disguised as a bug.

**Validation and exit:** implement the concrete behavior/negative cases behind the linked scenarios; execute the relevant suites against exact artifacts; inspect results and retain failures/skips; run affected existing v1 regressions. Record actual evidence in VALIDATION_HISTORY and a new cycle, update the task state and next ready task. For live-host work, unit mocks supplement but do not replace the named host/environment observations.

**Stop/recovery:** preserve original state and unrelated changes on failure; classify cause, stale evidence and uncertain effects before retry; do not widen scope, weaken the oracle or reset allowances. Ordinary in-scope corrections continue. Material changes follow HUMAN_DECISIONS.

### WP-153: Implement readable status evidence summary and local metrics

**Entry:** WP-120, WP-147. **Owner role:** Observability maintainer. **State:** consult the CSV.
**Requirements:** SF-11, SF-19, SF-29, SF-31, NFR-04, NFR-09. **Scenarios:** TC-163, TC-164.

**Goal:** Show what is happening, why it stopped and what action is actually needed.

**Implementation:** Project milestones/tasks/roles/current candidate/checks/reviews/budget and blockers read-only; emit selected local metrics; distinguish known/unknown usage; redact configured sensitive fields; provide bounded export and retention policy hooks.

**Owned/proposed paths:** `plugins/sparkforge/runtime/status.py`; `tests/test_status_projection.py`; `docs/engineering/OPERATIONS.md`. Inspect shared helpers first; coordinate shared-file changes explicitly.

**Positive acceptance:** A user can locate the next decision and a maintainer can trace a result to exact evidence without reading raw model transcripts.

**Required negative controls:** Status cannot approve or dispatch; secrets, unrestricted source text and synthetic metrics cannot be presented as observed product telemetry.

**Validation and exit:** implement the concrete behavior/negative cases behind the linked scenarios; execute the relevant suites against exact artifacts; inspect results and retain failures/skips; run affected existing v1 regressions. Record actual evidence in VALIDATION_HISTORY and a new cycle, update the task state and next ready task. For live-host work, unit mocks supplement but do not replace the named host/environment observations.

**Stop/recovery:** preserve original state and unrelated changes on failure; classify cause, stale evidence and uncertain effects before retry; do not widen scope, weaken the oracle or reset allowances. Ordinary in-scope corrections continue. Material changes follow HUMAN_DECISIONS.

### WP-154: Run integrated fault negative and recovery campaign

**Entry:** WP-150, WP-151, WP-152, WP-153. **Owner role:** Independent evaluation maintainer. **State:** consult the CSV.
**Requirements:** SF-07, SF-08, SF-09, SF-24, SF-30, NFR-01, NFR-02, NFR-03, NFR-08. **Scenarios:** TC-165, TC-166.

**Goal:** Demonstrate that the coordinated system rejects known-bad behavior under combined failures.

**Implementation:** Exercise stale/reordered/foreign/duplicate results, crashes, token-budget exhaustion, changed oracle, same-byte check reruns, source injection and cumulative drift; retain failure receipts and rerun affected scenarios after fixes.

**Owned/proposed paths:** `tests/evaluation/`; `tests/test_factory_faults.py`; `docs/engineering/EVALUATION_PLAN.md`. Inspect shared helpers first; coordinate shared-file changes explicitly.

**Positive acceptance:** Every mandatory negative scenario has observed rejection and no unresolved correctness-critical defect remains.

**Required negative controls:** A green happy path, mocked permission denial or skipped fault is not substitute evidence for the missing case.

**Validation and exit:** implement the concrete behavior/negative cases behind the linked scenarios; execute the relevant suites against exact artifacts; inspect results and retain failures/skips; run affected existing v1 regressions. Record actual evidence in VALIDATION_HISTORY and a new cycle, update the task state and next ready task. For live-host work, unit mocks supplement but do not replace the named host/environment observations.

**Stop/recovery:** preserve original state and unrelated changes on failure; classify cause, stale evidence and uncertain effects before retry; do not widen scope, weaken the oracle or reset allowances. Ordinary in-scope corrections continue. Material changes follow HUMAN_DECISIONS.

### WP-155: Review usability and material approval frequency

**Entry:** WP-154. **Owner role:** Domain acceptance maintainer. **State:** consult the CSV.
**Requirements:** SF-02, SF-19, SF-26, SF-31, NFR-08, NFR-09. **Scenarios:** TC-167, TC-168.

**Goal:** Make ordinary development proceed smoothly and material decisions understandable.

**Implementation:** Exercise unfamiliar-user instructions and decision examples; measure unnecessary interruptions in synthetic journeys; explain alternatives, cost/scope and exact object for actual decisions; record participant-based evaluation separately when available.

**Owned/proposed paths:** `docs/engineering/OPERATIONS.md`; `docs/engineering/EVALUATION_PLAN.md`; `tests/test_decision_explanations.py`. Inspect shared helpers first; coordinate shared-file changes explicitly.

**Positive acceptance:** Ordinary in-scope repair requests no extra intent approval; material changes explain the precise decision and consequence.

**Required negative controls:** Do not invent participant feedback, make elapsed silence approval or hide a blocking decision in a status log.

**Validation and exit:** implement the concrete behavior/negative cases behind the linked scenarios; execute the relevant suites against exact artifacts; inspect results and retain failures/skips; run affected existing v1 regressions. Record actual evidence in VALIDATION_HISTORY and a new cycle, update the task state and next ready task. For live-host work, unit mocks supplement but do not replace the named host/environment observations.

**Stop/recovery:** preserve original state and unrelated changes on failure; classify cause, stale evidence and uncertain effects before retry; do not widen scope, weaken the oracle or reset allowances. Ordinary in-scope corrections continue. Material changes follow HUMAN_DECISIONS.

## P6: Installed host and first-environment acceptance

Milestone exit: Actual native adapter/role discovery/lifecycle, corp-local model-driven journeys, independent acceptance and measured operating limits.

### WP-160: Qualify the selected native host capability adapter

**Entry:** WP-114, WP-147. **Owner role:** Native host maintainer. **State:** consult the CSV.
**Requirements:** SF-13, SF-16, SF-17, SF-22, NFR-01, NFR-05, NFR-06. **Scenarios:** TC-169, TC-170.

**Goal:** Connect the abstract protocol to capabilities actually available in one chosen Copilot host/build.

**Implementation:** Record host version, agent invocation/session support, tool boundary, identity/reviewer separation, cancellation/recovery and usage visibility; implement only documented/observed mechanisms; list unsupported capabilities and narrower assisted fallback explicitly.

**Owned/proposed paths:** `plugins/sparkforge/runtime/hosts/`; `docs/integration/HOST_ADAPTER.md`; `tests/test_native_host_contract.py`. Inspect shared helpers first; coordinate shared-file changes explicitly.

**Positive acceptance:** A disposable authorized probe demonstrates dispatch, completion binding and recovery for the claimed capability set.

**Required negative controls:** Do not invent a CLI launcher, assume SDK access from a subscription, substitute a provider or silently call manual operation autonomous.

**Validation and exit:** implement the concrete behavior/negative cases behind the linked scenarios; execute the relevant suites against exact artifacts; inspect results and retain failures/skips; run affected existing v1 regressions. Record actual evidence in VALIDATION_HISTORY and a new cycle, update the task state and next ready task. For live-host work, unit mocks supplement but do not replace the named host/environment observations.

**Stop/recovery:** preserve original state and unrelated changes on failure; classify cause, stale evidence and uncertain effects before retry; do not widen scope, weaken the oracle or reset allowances. Ordinary in-scope corrections continue. Material changes follow HUMAN_DECISIONS.

### WP-161: Package and discover actual role definitions

**Entry:** WP-160, WP-135, WP-143. **Owner role:** Package maintainer. **State:** consult the CSV.
**Requirements:** SF-05, SF-13, SF-22, SF-23, SF-24, NFR-05, NFR-10. **Scenarios:** TC-171, TC-172.

**Goal:** Ship the coordinated roles using the selected host supported composition.

**Implementation:** Translate docs/roles contracts into actual supported prompts/tool restrictions; add owned inventory closure; distinguish entry brain/controller/workers and deterministic runner; verify relocation and installed-resource resolution.

**Owned/proposed paths:** `plugins/sparkforge/agents/`; `plugins/sparkforge/skills/`; `plugins/sparkforge/plugin.json`; `scripts/build_sparkforge_package.py`; `tests/test_native_package.py`. Inspect shared helpers first; coordinate shared-file changes explicitly.

**Positive acceptance:** The selected host discovers the intended role resources and no role silently inherits excessive tools or undeclared files.

**Required negative controls:** More agent files or a metadata pass alone do not establish delegation, independent judgment or an execution boundary.

**Validation and exit:** implement the concrete behavior/negative cases behind the linked scenarios; execute the relevant suites against exact artifacts; inspect results and retain failures/skips; run affected existing v1 regressions. Record actual evidence in VALIDATION_HISTORY and a new cycle, update the task state and next ready task. For live-host work, unit mocks supplement but do not replace the named host/environment observations.

**Stop/recovery:** preserve original state and unrelated changes on failure; classify cause, stale evidence and uncertain effects before retry; do not widen scope, weaken the oracle or reset allowances. Ordinary in-scope corrections continue. Material changes follow HUMAN_DECISIONS.

### WP-162: Qualify fresh installation upgrade and removal

**Entry:** WP-161, WP-150, WP-151. **Owner role:** Package maintainer. **State:** consult the CSV.
**Requirements:** SF-05, SF-14, SF-19, NFR-03, NFR-05, NFR-07, NFR-10. **Scenarios:** TC-173, TC-174.

**Goal:** Verify the exact installed package works without a developer checkout.

**Implementation:** Build reproducible owned inventory; install into an explicitly selected disposable host profile; exercise new job, resume, upgrade and uninstall; preserve operator jobs/config; check partial failure and rollback; record exact package digest.

**Owned/proposed paths:** `scripts/build_sparkforge_package.py`; `tests/test_package_lifecycle.py`; `docs/engineering/OPERATIONS.md`. Inspect shared helpers first; coordinate shared-file changes explicitly.

**Positive acceptance:** Installed-source commands resolve shipped resources and lifecycle operations preserve unrelated user content.

**Required negative controls:** A checkout test, fabricated installer, shadow import or removal of operator data cannot qualify the lifecycle.

**Validation and exit:** implement the concrete behavior/negative cases behind the linked scenarios; execute the relevant suites against exact artifacts; inspect results and retain failures/skips; run affected existing v1 regressions. Record actual evidence in VALIDATION_HISTORY and a new cycle, update the task state and next ready task. For live-host work, unit mocks supplement but do not replace the named host/environment observations.

**Stop/recovery:** preserve original state and unrelated changes on failure; classify cause, stale evidence and uncertain effects before retry; do not widen scope, weaken the oracle or reset allowances. Ordinary in-scope corrections continue. Material changes follow HUMAN_DECISIONS.

### WP-163: Run authorized corp model-driven new and brownfield journeys

**Entry:** WP-162, WP-131, WP-154. **Owner role:** Corp operator and evaluator. **State:** consult the CSV.
**Requirements:** SF-01, SF-03, SF-05, SF-07, SF-14, SF-16, SF-22, SF-23, SF-24, NFR-04, NFR-05, NFR-08. **Scenarios:** TC-175, TC-176.

**Goal:** Demonstrate actual model-driven cooperation on representative permitted platform tasks.

**Implementation:** Select finite trials, source/profile versions and independent rubric; run new/reuse/update cases plus real diagnosis/repair, drift and interruption; record failures, manual interventions and actual usage locally; publish only cleared aggregate evidence.

**Owned/proposed paths:** `docs/engineering/ENVIRONMENT_ACCEPTANCE.md`; `environment-local evidence outside Git`. Inspect shared helpers first; coordinate shared-file changes explicitly.

**Positive acceptance:** The actual installed corp host satisfies the declared journeys; model decisions and repairs are observed rather than fixture-authored.

**Required negative controls:** Offline tests, synthetic sources, host metadata and another environment result cannot be relabeled corp acceptance.

**Validation and exit:** implement the concrete behavior/negative cases behind the linked scenarios; execute the relevant suites against exact artifacts; inspect results and retain failures/skips; run affected existing v1 regressions. Record actual evidence in VALIDATION_HISTORY and a new cycle, update the task state and next ready task. For live-host work, unit mocks supplement but do not replace the named host/environment observations.

**Stop/recovery:** preserve original state and unrelated changes on failure; classify cause, stale evidence and uncertain effects before retry; do not widen scope, weaken the oracle or reset allowances. Ordinary in-scope corrections continue. Material changes follow HUMAN_DECISIONS.

### WP-164: Obtain independent domain and security acceptance

**Entry:** WP-163, WP-155. **Owner role:** Domain and independent review owners. **State:** consult the CSV.
**Requirements:** SF-08, SF-14, SF-19, SF-24, NFR-01, NFR-08, NFR-09. **Scenarios:** TC-177, TC-178.

**Goal:** Confirm the factory delivers useful supported outcomes under its real claimed limits.

**Implementation:** Review representative outputs and platform fit with actual participants; examine control-plane threat cases, source isolation, acceptance protection and residual manual steps; record genuine accept/changes with scope and exact package binding.

**Owned/proposed paths:** `docs/engineering/ENVIRONMENT_ACCEPTANCE.md`; `environment-local review records`. Inspect shared helpers first; coordinate shared-file changes explicitly.

**Positive acceptance:** Blocking findings are resolved or support claims are narrowed with an explicit accountable decision.

**Required negative controls:** An AI-authored approval, confident summary, worker label or aggregate score cannot stand in for actual required decisions.

**Validation and exit:** implement the concrete behavior/negative cases behind the linked scenarios; execute the relevant suites against exact artifacts; inspect results and retain failures/skips; run affected existing v1 regressions. Record actual evidence in VALIDATION_HISTORY and a new cycle, update the task state and next ready task. For live-host work, unit mocks supplement but do not replace the named host/environment observations.

**Stop/recovery:** preserve original state and unrelated changes on failure; classify cause, stale evidence and uncertain effects before retry; do not widen scope, weaken the oracle or reset allowances. Ordinary in-scope corrections continue. Material changes follow HUMAN_DECISIONS.

### WP-165: Measure reliability latency and cost against selected targets

**Entry:** WP-164, WP-123. **Owner role:** Evaluation and operations maintainer. **State:** consult the CSV.
**Requirements:** SF-07, SF-29, NFR-06, NFR-08, NFR-09. **Scenarios:** TC-179, TC-180.

**Goal:** Choose operating limits from observed accepted outcomes and human effort.

**Implementation:** Compare manual/assisted baseline with factory trials; measure accepted-task rate, false acceptance, drift detection, repair effectiveness, recovery, approval burden, elapsed time and reported cost; preserve denominators and unknowns; select support SLOs from evidence.

**Owned/proposed paths:** `docs/engineering/EVALUATION_PLAN.md`; `environment-local measurements`. Inspect shared helpers first; coordinate shared-file changes explicitly.

**Positive acceptance:** The release records task mix, trial count, variability and observed limitations rather than invented universal thresholds.

**Required negative controls:** Synthetic speed, test counts, tokens alone or excluding failed runs cannot establish product reliability or economics.

**Validation and exit:** implement the concrete behavior/negative cases behind the linked scenarios; execute the relevant suites against exact artifacts; inspect results and retain failures/skips; run affected existing v1 regressions. Record actual evidence in VALIDATION_HISTORY and a new cycle, update the task state and next ready task. For live-host work, unit mocks supplement but do not replace the named host/environment observations.

**Stop/recovery:** preserve original state and unrelated changes on failure; classify cause, stale evidence and uncertain effects before retry; do not widen scope, weaken the oracle or reset allowances. Ordinary in-scope corrections continue. Material changes follow HUMAN_DECISIONS.

## P7: Qualified local release and contribution preparation

Milestone exit: Verified docs, exact-effect boundary, contribution bundle and local release candidate; actual submission separately scoped.

### WP-170: Complete user operator contributor and support guides

**Entry:** WP-155, WP-162. **Owner role:** Documentation maintainer. **State:** consult the CSV.
**Requirements:** SF-11, SF-19, SF-31, NFR-07, NFR-09. **Scenarios:** TC-181, TC-182.

**Goal:** Make the tested release usable and maintainable without prior conversations.

**Implementation:** Write supported journeys, setup, approval decisions, failure/status explanations, recovery, retention, package lifecycle and contributor checks from actual behavior; include owner/support responsibilities only when genuine; verify examples in the installed source.

**Owned/proposed paths:** `docs/engineering/OPERATIONS.md`; `docs/delivery/WIKI_AND_SUBMISSION.md`; `CONTRIBUTING.md`. Inspect shared helpers first; coordinate shared-file changes explicitly.

**Positive acceptance:** A new operator can follow the documented supported path and identify the next action when blocked.

**Required negative controls:** Unimplemented CLI examples, fictional contacts or stale source links cannot appear as working support instructions.

**Validation and exit:** implement the concrete behavior/negative cases behind the linked scenarios; execute the relevant suites against exact artifacts; inspect results and retain failures/skips; run affected existing v1 regressions. Record actual evidence in VALIDATION_HISTORY and a new cycle, update the task state and next ready task. For live-host work, unit mocks supplement but do not replace the named host/environment observations.

**Stop/recovery:** preserve original state and unrelated changes on failure; classify cause, stale evidence and uncertain effects before retry; do not widen scope, weaken the oracle or reset allowances. Ordinary in-scope corrections continue. Material changes follow HUMAN_DECISIONS.

### WP-171: Implement exact external-effect intents and reconciliation

**Entry:** WP-151, WP-122. **Owner role:** Control-plane maintainer. **State:** consult the CSV.
**Requirements:** SF-15, SF-18, SF-26, SF-30, NFR-01, NFR-02, NFR-03, NFR-10. **Scenarios:** TC-183, TC-184.

**Goal:** Keep contribution or deployment effects inside explicit destinations and payload scope.

**Implementation:** Define effect preview, destination/payload/identity binding, decision admission, operation key and read-after-write reconciliation; implement fake destination first; preserve denied/unknown outcomes; prevent changed-payload replay.

**Owned/proposed paths:** `plugins/sparkforge/runtime/effects.py`; `tests/test_external_effects.py`. Inspect shared helpers first; coordinate shared-file changes explicitly.

**Positive acceptance:** Local readiness alone never performs an external write and an authorized write is observable and reconcilable.

**Required negative controls:** Reject stale decisions, different repository/branch, private data in a public payload and blind replay after a lost response.

**Validation and exit:** implement the concrete behavior/negative cases behind the linked scenarios; execute the relevant suites against exact artifacts; inspect results and retain failures/skips; run affected existing v1 regressions. Record actual evidence in VALIDATION_HISTORY and a new cycle, update the task state and next ready task. For live-host work, unit mocks supplement but do not replace the named host/environment observations.

**Stop/recovery:** preserve original state and unrelated changes on failure; classify cause, stale evidence and uncertain effects before retry; do not widen scope, weaken the oracle or reset allowances. Ordinary in-scope corrections continue. Material changes follow HUMAN_DECISIONS.

### WP-172: Prepare reviewable contribution and documentation bundles

**Entry:** WP-171, WP-170. **Owner role:** Delivery maintainer. **State:** consult the CSV.
**Requirements:** SF-11, SF-14, SF-15, SF-18, SF-19, NFR-04, NFR-10. **Scenarios:** TC-185, TC-186.

**Goal:** Assemble exact code, evidence summaries and docs for the approved platform contribution route.

**Implementation:** Produce local diff/branch/PR/wiki payload previews without publishing; bind tested package/source/evidence versions; check owned file inventory and exclusions; include remaining limitations and explicit requested stage.

**Owned/proposed paths:** `plugins/sparkforge/runtime/delivery.py`; `tests/test_delivery_bundle.py`; `docs/delivery/WIKI_AND_SUBMISSION.md`. Inspect shared helpers first; coordinate shared-file changes explicitly.

**Positive acceptance:** A reviewer can inspect the complete candidate and contribution payload before any external submission.

**Required negative controls:** Reject mixed runtime/private data, missing evidence, untested artifact substitutions and automatic production modification.

**Validation and exit:** implement the concrete behavior/negative cases behind the linked scenarios; execute the relevant suites against exact artifacts; inspect results and retain failures/skips; run affected existing v1 regressions. Record actual evidence in VALIDATION_HISTORY and a new cycle, update the task state and next ready task. For live-host work, unit mocks supplement but do not replace the named host/environment observations.

**Stop/recovery:** preserve original state and unrelated changes on failure; classify cause, stale evidence and uncertain effects before retry; do not widen scope, weaken the oracle or reset allowances. Ordinary in-scope corrections continue. Material changes follow HUMAN_DECISIONS.

### WP-173: Assemble the release candidate and continuation checkpoint

**Entry:** WP-164, WP-165, WP-172. **Owner role:** Release coordinator. **State:** consult the CSV.
**Requirements:** SF-11, SF-14, SF-15, SF-19, SF-20, SF-31, NFR-02, NFR-05, NFR-08, NFR-10. **Scenarios:** TC-187, TC-188.

**Goal:** Finish the qualified first-environment release with honest support and reproducibility.

**Implementation:** Check milestone evidence completeness, exact source/package, open risks, genuine ownership/terms and selected support scope; rerun affected checks; produce operator handoff and recovery checkpoint; record external submission as separate work.

**Owned/proposed paths:** `docs/PROJECT_STATUS.md`; `docs/VALIDATION_HISTORY.md`; `docs/engineering/cycles/`; `release-local bundle`. Inspect shared helpers first; coordinate shared-file changes explicitly.

**Positive acceptance:** Every claimed capability has current evidence and the qualified local release is review-ready without waiting for optional learning/parallelism/acro.

**Required negative controls:** A push, documentation pass, unresolved blocker or invented approval cannot complete release qualification.

**Validation and exit:** implement the concrete behavior/negative cases behind the linked scenarios; execute the relevant suites against exact artifacts; inspect results and retain failures/skips; run affected existing v1 regressions. Record actual evidence in VALIDATION_HISTORY and a new cycle, update the task state and next ready task. For live-host work, unit mocks supplement but do not replace the named host/environment observations.

**Stop/recovery:** preserve original state and unrelated changes on failure; classify cause, stale evidence and uncertain effects before retry; do not widen scope, weaken the oracle or reset allowances. Ordinary in-scope corrections continue. Material changes follow HUMAN_DECISIONS.

### WP-174: Submit only through the actual selected platform route

**Entry:** WP-173. **Owner role:** Authorized contributor. **State:** consult the CSV.
**Requirements:** SF-15, SF-18, SF-19, NFR-01, NFR-03, NFR-10. **Scenarios:** TC-189, TC-190.

**Goal:** Perform a separately scoped platform contribution when the destination and authority exist.

**Implementation:** Review exact cleared payload and destination; invoke the selected effect adapter; verify actual remote identity; route received feedback as defects or changed intent; retain uncertainty before retry.

**Owned/proposed paths:** `environment-local submission records`; `docs/delivery/WIKI_AND_SUBMISSION.md`. Inspect shared helpers first; coordinate shared-file changes explicitly.

**Positive acceptance:** The requested submission exists at the verified destination and no unsupported organizational acceptance is claimed.

**Required negative controls:** Do not infer production deployment or platform approval from development-repository publication.

**Validation and exit:** implement the concrete behavior/negative cases behind the linked scenarios; execute the relevant suites against exact artifacts; inspect results and retain failures/skips; run affected existing v1 regressions. Record actual evidence in VALIDATION_HISTORY and a new cycle, update the task state and next ready task. For live-host work, unit mocks supplement but do not replace the named host/environment observations.

**Stop/recovery:** preserve original state and unrelated changes on failure; classify cause, stale evidence and uncertain effects before retry; do not widen scope, weaken the oracle or reset allowances. Ordinary in-scope corrections continue. Material changes follow HUMAN_DECISIONS.

## P8: Independent adaptations and optional improvements

Milestone exit: Acro-local qualification, measured parallelism and evaluated learning lifecycle.

### WP-180: Adapt the factory independently inside acro

**Entry:** WP-162. **Owner role:** Acro operator and maintainer. **State:** consult the CSV.
**Requirements:** SF-13, SF-16, SF-17, SF-23, NFR-01, NFR-04, NFR-05, NFR-10. **Scenarios:** TC-191, TC-192.

**Goal:** Use shared reviewed source with independent target-local knowledge and authority.

**Implementation:** Inventory acro host/capabilities/sources/storage/tools; obtain permitted shared-code distribution as needed; build target package; keep credentials, snapshots, journals and model routes local; do not require exporting corp data.

**Owned/proposed paths:** `environment-local acro profile`; `docs/engineering/ENVIRONMENT_ACCEPTANCE.md`. Inspect shared helpers first; coordinate shared-file changes explicitly.

**Positive acceptance:** Acro can operate independently under its own profile; unavailable corp sources do not become a fabricated dependency.

**Required negative controls:** Reject shared credentials, live environment bridges, inherited permissions and imported corp runtime state.

**Validation and exit:** implement the concrete behavior/negative cases behind the linked scenarios; execute the relevant suites against exact artifacts; inspect results and retain failures/skips; run affected existing v1 regressions. Record actual evidence in VALIDATION_HISTORY and a new cycle, update the task state and next ready task. For live-host work, unit mocks supplement but do not replace the named host/environment observations.

**Stop/recovery:** preserve original state and unrelated changes on failure; classify cause, stale evidence and uncertain effects before retry; do not widen scope, weaken the oracle or reset allowances. Ordinary in-scope corrections continue. Material changes follow HUMAN_DECISIONS.

### WP-181: Qualify acro journeys and package lifecycle independently

**Entry:** WP-180, WP-154. **Owner role:** Acro operator and evaluator. **State:** consult the CSV.
**Requirements:** SF-07, SF-08, SF-14, SF-17, SF-22, NFR-05, NFR-08. **Scenarios:** TC-193, TC-194.

**Goal:** Establish actual acro support rather than copying corp acceptance.

**Implementation:** Repeat selected installed new/brownfield/repair/drift/recovery and lifecycle scenarios with target-local sources and rubric; record actual usage, failures, participants and support limits.

**Owned/proposed paths:** `environment-local acro evidence`; `docs/engineering/ENVIRONMENT_ACCEPTANCE.md`. Inspect shared helpers first; coordinate shared-file changes explicitly.

**Positive acceptance:** Each acro claim is supported by acro observations and exact source/package/profile bindings.

**Required negative controls:** A structural acro package or corp success is not acro acceptance.

**Validation and exit:** implement the concrete behavior/negative cases behind the linked scenarios; execute the relevant suites against exact artifacts; inspect results and retain failures/skips; run affected existing v1 regressions. Record actual evidence in VALIDATION_HISTORY and a new cycle, update the task state and next ready task. For live-host work, unit mocks supplement but do not replace the named host/environment observations.

**Stop/recovery:** preserve original state and unrelated changes on failure; classify cause, stale evidence and uncertain effects before retry; do not widen scope, weaken the oracle or reset allowances. Ordinary in-scope corrections continue. Material changes follow HUMAN_DECISIONS.

### WP-182: Add bounded parallel scheduling only when justified

**Entry:** WP-173, WP-124. **Owner role:** Orchestration and workspace maintainers. **State:** consult the CSV.
**Requirements:** SF-20, SF-22, SF-27, SF-29, NFR-01, NFR-03, NFR-06. **Scenarios:** TC-195, TC-196.

**Goal:** Improve measured throughput without weakening isolation or review barriers.

**Implementation:** Select disjoint tasks, concurrency limit and resource partitioning; qualify host isolation; retain one integration owner; prevent shared cache/workspace collisions; compare accepted-task latency/cost with serial baseline.

**Owned/proposed paths:** `plugins/sparkforge/runtime/scheduler.py`; `tests/test_parallel_scheduler.py`. Inspect shared helpers first; coordinate shared-file changes explicitly.

**Positive acceptance:** Parallel work preserves the same invariants and demonstrates a measured benefit for the selected task mix.

**Required negative controls:** No parallel writers to overlapping paths, budget multiplication, missing joins or assumed worktree confinement.

**Validation and exit:** implement the concrete behavior/negative cases behind the linked scenarios; execute the relevant suites against exact artifacts; inspect results and retain failures/skips; run affected existing v1 regressions. Record actual evidence in VALIDATION_HISTORY and a new cycle, update the task state and next ready task. For live-host work, unit mocks supplement but do not replace the named host/environment observations.

**Stop/recovery:** preserve original state and unrelated changes on failure; classify cause, stale evidence and uncertain effects before retry; do not widen scope, weaken the oracle or reset allowances. Ordinary in-scope corrections continue. Material changes follow HUMAN_DECISIONS.

### WP-183: Collect evidence-backed inactive learning proposals

**Entry:** WP-173, WP-153. **Owner role:** Learning maintainer. **State:** consult the CSV.
**Requirements:** SF-10, SF-11, SF-21, NFR-02, NFR-04, NFR-07, NFR-08. **Scenarios:** TC-197, TC-198.

**Goal:** Learn from permitted outcomes without changing active behavior automatically.

**Implementation:** Bind observations to task/evidence and retention scope; distinguish recurring problem from one-off failure; propose falsifiable changes or explicit no-change; keep proposals inactive and environment-local.

**Owned/proposed paths:** `plugins/sparkforge/runtime/learning.py`; `tests/test_learning_proposals.py`. Inspect shared helpers first; coordinate shared-file changes explicitly.

**Positive acceptance:** A proposal is traceable, scoped and evaluable; creating it does not dispatch work or modify policy.

**Required negative controls:** Reject invented lessons, unapproved transcript collection, cross-environment memory and self-activation.

**Validation and exit:** implement the concrete behavior/negative cases behind the linked scenarios; execute the relevant suites against exact artifacts; inspect results and retain failures/skips; run affected existing v1 regressions. Record actual evidence in VALIDATION_HISTORY and a new cycle, update the task state and next ready task. For live-host work, unit mocks supplement but do not replace the named host/environment observations.

**Stop/recovery:** preserve original state and unrelated changes on failure; classify cause, stale evidence and uncertain effects before retry; do not widen scope, weaken the oracle or reset allowances. Ordinary in-scope corrections continue. Material changes follow HUMAN_DECISIONS.

### WP-184: Evaluate promote monitor and withdraw learning changes

**Entry:** WP-183, WP-171. **Owner role:** Independent evaluator and promotion owner. **State:** consult the CSV.
**Requirements:** SF-04, SF-08, SF-09, SF-21, NFR-01, NFR-02, NFR-03, NFR-06, NFR-08. **Scenarios:** TC-199, TC-200.

**Goal:** Promote useful changes only after independent comparison and an exact decision.

**Implementation:** Evaluate baseline/candidate on held-out cases; preserve negative results; require separately allowed evaluation resources and promotion; monitor exact active version; implement withdrawal/rollback without restoring revoked data.

**Owned/proposed paths:** `plugins/sparkforge/runtime/learning.py`; `tests/test_learning_promotion.py`. Inspect shared helpers first; coordinate shared-file changes explicitly.

**Positive acceptance:** Only the evaluated approved version becomes active and failures can be safely withdrawn.

**Required negative controls:** Learner cannot edit its evaluator, criterion, authority, provider or budget; score-only promotion is rejected.

**Validation and exit:** implement the concrete behavior/negative cases behind the linked scenarios; execute the relevant suites against exact artifacts; inspect results and retain failures/skips; run affected existing v1 regressions. Record actual evidence in VALIDATION_HISTORY and a new cycle, update the task state and next ready task. For live-host work, unit mocks supplement but do not replace the named host/environment observations.

**Stop/recovery:** preserve original state and unrelated changes on failure; classify cause, stale evidence and uncertain effects before retry; do not widen scope, weaken the oracle or reset allowances. Ordinary in-scope corrections continue. Material changes follow HUMAN_DECISIONS.

## Historical work and numbering

Earlier work IDs and 96 earlier scenarios are preserved in the [archived baseline](archive/README.md). They are not active prerequisites. Active work begins at WP-100 and active scenario IDs run TC-101 through TC-200, preserving distinct identities rather than recycling old scenario meanings. Old cycles remain attributable to their original baseline.

Existing delivered mechanisms are reused: snapshot verification, assisted v1 job/check/review lifecycle, package assembly, host-record checks, storage probes and research tooling. Do not treat a not-yet-complete coordinated task as a request to erase those mechanisms.
