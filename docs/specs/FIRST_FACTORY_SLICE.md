# First coordinated factory slice

**Target integration gate: WP-147.** This is a planned synthetic scenario with real owned file edits/check processes driven through the coordinator and a labeled deterministic fake host. Actual model-driven replication is WP-163. Existing v1 synthetic repair tests remain a separate earlier capability.

## User outcome and fictional platform

A fictional platform supports small Python components and declares an existing request-routing component with a stable input/output interface. The user wants to add an audit-only routing option while preserving current routes and rejecting unknown values. This is a fixture contract, not a claim about real SPARK APIs.

The component accepts a supported routing request and returns the declared result without sending network traffic or mutating unrelated files. Existing routes and error behavior remain compatible. Audit-only must not dispatch the underlying action. Scope excludes a new web UI, new provider, background service, actual tenant access and automatic deployment.

## Acceptance criteria

| Criterion | Observable behavior | Evidence |
|---|---|---|
| Existing compatibility | Every existing route retains its declared result/error behavior | Executed regression checks on exact candidate |
| New behavior | Audit-only returns the expected record and never calls the effect stub | Positive case plus effect-call counter |
| Invalid input | Unknown/malformed request is rejected with the declared error | Negative/edge cases |
| Platform fit/reuse | Existing component is inspected and updated for a justified minimal delta | Source/profile bindings and reuse assessment |
| Intent preservation | No new output/effect/UI appears beyond accepted criteria | Controller checkpoints and diff/evidence inspection |
| Independence | Builder cannot change protected criteria or satisfy its own required review | Ownership tests and host producer/context observations at the appropriate evidence class |
| Recoverability | Restart/lost response cannot duplicate an effectful operation | Durable operation key and fake-host call counter |
| Honest handoff | Complete current checks/reviews/controller evidence and scoped limitations | Exact local bundle and readable status |

The evaluator defines exact inputs/outputs/errors before implementation. These fixture details belong to WP-115; the coder cannot choose an easier oracle after seeing a failure.

## Expected coordinated journey

1. Intake reads the supplied idea and synthetic platform/source context. It asks only if a behaviorally consequential fact is absent.
2. Brain proposes UPDATE_EXISTING with relevant source inspection, a task graph and finite allowance. Controller checks that audit-only cannot execute the action.
3. Coordinator admits tasks; coder makes the scoped change; independent test author derives tests from the baseline.
4. Runner executes actual declared commands. The seeded first implementation incorrectly dispatches the action in audit-only mode and fails the effect-count criterion.
5. Diagnostician identifies the implementation defect from the actual bound failure; repair routes back to coder without another user intent approval inside allowance.
6. Runner reruns affected checks and required regressions; reviewer inspects exact current code/evidence and controller confirms semantics.
7. Local handoff includes implementation, tests, evidence references, plan/source/profile bindings, remaining limitations and no release claim.

The fake host scripts role outputs and edits for deterministic integration tests. Report them as scripted cooperation, never as a model choosing a repair. WP-163 repeats selected cases with actual model-driven roles and real host observations.

## Required negative journeys

- A green implementation ignores audit-only and returns a superficially similar record: controller/protected oracle rejects semantic drift.
- A worker edits the protected evaluator or removes the failing check: ownership/acceptance barrier rejects it.
- A second equivalent repair keeps the same failure and candidate: no-progress/allowance handling stops the loop.
- A plan drops old-route compatibility or requests another provider: materiality/admission prevents silent scope expansion.
- A delayed result names a superseded plan/candidate: result stays uncredited.
- A response is lost after dispatch: restart inspects the operation key; it does not dispatch again.
- Cancellation or decision revocation arrives while work runs: no new work is admitted; unknown effects remain visible.
- A required reviewer is missing or builder is relabeled: readiness is blocked.
- A check reruns on identical bytes: fresh review context is required.

## Exit evidence

The scenario is complete only when actual file/process receipts, fake-host operation counters, current role/result bindings and positive/negative outcomes are inspectable. Report all failed attempts, skipped cases and fixture authorship. This gate does not qualify a real host, independent human acceptance, corp/acro support or production release.
