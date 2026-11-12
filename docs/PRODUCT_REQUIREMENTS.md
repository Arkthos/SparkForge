# Product requirements

**Planning baseline: 2026-11-12.** This revision adopts the owner's explicit coordinated multi-agent objective. It supersedes the earlier single-agent target and blanket full-spec reapproval as future design choices. It does not change the existing assisted-v1 runtime semantics.

## Product goal

Convert a user's rough idea, content or existing implementation into an evidenced solution that fits the selected SPARK platform. Keep the human responsible for intent and material decisions while the factory handles ordinary planning, coding, testing, diagnosis, correction, review and recovery inside an agreed envelope.

The initial delivery is a local native-host component factory. Supported component kinds must come from an actual profile, with synthetic agent/skill or small component examples used until private platform interfaces are available. Universal application generation, a hosted multi-user SaaS, production auto-deployment and automatic corp/acro synchronization are outside the first release.

## Functional requirements

| ID | Requirement | Acceptance boundary |
|---|---|---|
| SF-01 | Accept ideas, existing code, playbooks and content | Preserve provenance and use only inputs available within the selected environment. |
| SF-02 | Clarify outcome, audience and observable acceptance | Reuse supplied/source-backed facts; ask only consequential missing questions. |
| SF-03 | Assess platform fit and reuse before generation | Inspect relevant implementation; lexical matches and missing hits are insufficient. |
| SF-04 | Bind user intent and material decisions to exact current objects | Routine technical work inside an accepted envelope can proceed; changed behavior or authority needs its decision owner. |
| SF-05 | Create or improve supported SPARK components | A selected platform profile defines supported kinds; do not invent private framework behavior. |
| SF-06 | Author meaningful independent behavioral tests | Protect acceptance and test negative/edge behavior rather than mirroring generated code. |
| SF-07 | Execute checks and evaluate actual evidence | Completion, a zero exit and demonstrated acceptance are different facts. |
| SF-08 | Review quality, security and platform fit independently | Required review must be current and genuinely separate from the builder context. |
| SF-09 | Diagnose failures and repair within finite allowances | Preserve failed attempts, unknown effects and no-progress/budget stops. |
| SF-10 | Route feedback, defects and changed intent | Equivalent repair stays in scope; changed goals create explicit baseline deltas. |
| SF-11 | Maintain decisions, docs, state and useful evidence | Keep runtime/private data outside Git and evidence bound to exact revisions. |
| SF-12 | Refresh authorized platform knowledge when needed | Keep permission, freshness, integrity and semantic coverage separate. |
| SF-13 | Use the selected native Copilot host through an explicit adapter | Qualify actual capabilities; no invented API, account or provider fallback. |
| SF-14 | Produce an evidenced working local candidate | A worker turn, template, mock or package metadata alone cannot establish readiness. |
| SF-15 | Prepare and perform contribution through a selected route | External write/deployment effects have an exact target/payload scope. |
| SF-16 | Qualify corp using corp-local context and observations | A label or source-neutral test does not establish actual environment support. |
| SF-17 | Support independent acro adaptation and qualification | No shared credentials, runtime memory bridge or inherited corp acceptance. |
| SF-18 | Bind external effects to explicit scope and reconcile outcomes | Local readiness is not export authority; lost responses require inspection before replay. |
| SF-19 | Deliver useful user, operator and contributor guidance | Document actual supported behavior, limitations, recovery and accountable support. |
| SF-20 | Use versioned contracts and controlled engineering | Deterministic admission guards, owned changes, traceability and regression evidence. |
| SF-21 | Support governed learning after the core factory works | Inactive proposals first; independent evaluation and exact promotion/withdrawal later. |
| SF-22 | Coordinate distinct brain, controller, coding, testing, review and diagnosis roles | Separate logical responsibility and context; parallelism is optional. |
| SF-23 | Maintain a platform-aware brain for planning and replanning | Bind plans to environment, supported interfaces, source revisions and accepted intent. |
| SF-24 | Enforce independent intent-control checkpoints | Detect semantic drift at planning, integration, repair, replan and final handoff. |
| SF-25 | Separate intent baseline, execution plan and evidence | A technical revision cannot silently rewrite the user outcome or inherit stale results. |
| SF-26 | Require human decisions when materially necessary | Classify behavior/authority/resource deltas explicitly; ordinary bounded corrections continue. |
| SF-27 | Dispatch durable tasks with role, ownership and dependency contracts | Validate results and full barriers; do not equate model prose with completion. |
| SF-28 | Route implementation, oracle, environment, intent and uncertain-effect failures differently | Use evidence-backed diagnosis and the smallest valid recovery route. |
| SF-29 | Account for job-wide agent and execution resources | Preserve totals across retries/replans; unreported usage is unknown, not zero. |
| SF-30 | Resume jobs without duplicating unknown operations | Persist operation identity before effects and reconcile cancellation/interruption. |
| SF-31 | Keep development resumable by GitHub Copilot | Maintain a clear first task, exact evidence, next actions and dependency-ordered instructions. |

## Nonfunctional requirements

| ID | Requirement | Acceptance boundary |
|---|---|---|
| NFR-01 | Least authority and explicit effect/data boundaries | Prompts/hashes/actor strings are not isolation or authenticated consent. |
| NFR-02 | Revision-bound evidence and decisions | Separate source, intent, plan, candidate, task, run, attempt and review context. |
| NFR-03 | Durable recovery and reconciled effects | Atomic reservations and explicit unknown states; no blind retries. |
| NFR-04 | Privacy-preserving diagnostics and retention | Use bounded summaries; keep secrets, private sources and raw traces out of Git. |
| NFR-05 | Portability within observed host support | Qualify package/resources/lifecycle separately in each target. |
| NFR-06 | Finite resources and cancellable work | Bound whole jobs and agent/check attempts; report termination uncertainty. |
| NFR-07 | Maintainability and reproducibility | Small complete changes, existing helpers, explicit dependencies and migrations. |
| NFR-08 | Meaningful independent validation | Positive and known-bad controls; synthetic and live acceptance remain separate. |
| NFR-09 | Understandable operation | Explain current state, next action, questions, costs and material decisions. |
| NFR-10 | Supply-chain and distribution discipline | Path-specific terms, owned inventory and exact contribution payloads. |

## Required product journeys

1. Clarify an idea with relevant platform context and explain reuse/update/new alternatives.
2. Establish the intent baseline and delegated envelope; expose unresolved material decisions before implementation.
3. Brain produces a task plan; independent controller checks intent alignment; deterministic runtime admits work.
4. Coder and test roles produce scoped artifacts; runner executes checks; reviewer and controller evaluate exact current results.
5. Diagnostician routes a defect to bounded repair; equivalent technical replanning proceeds without unnecessary user approval.
6. Drift, exhausted resources, new permission/data routes or uncertain effects produce the appropriate decision or reconciliation state.
7. Restart preserves work and avoids duplicate unknown effects; feedback resumes repair or creates a new intent revision.
8. Deliver code, evidence summaries, documentation and remaining limits; external submission remains a distinct scoped effect.

## First-release scope and later extensions

Required: serial multi-agent coordination, protected criteria, explicit host adapter, useful new and brownfield component journeys, bounded repair/replanning, status, cancellation/recovery, independent review, first-environment installed acceptance and reviewable delivery.

Later: acro-local adaptation on its own evidence, measured parallel execution and governed learning promotion. None is a hidden prerequisite to the first-environment qualified local release. Environment-specific facts, organization policy, identities, budgets and license terms remain unresolved until actually supplied or observed.
