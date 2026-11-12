# Agent and deterministic role contracts

**Planned contracts.** These roles are not installed by this document. Actual host integration and role packaging belong to P6. A role is a bounded responsibility/context, not necessarily another account, model, process or simultaneous worker.

## Role map

| Role | Main inputs | Main output | Writes / forbidden authority |
|---|---|---|---|
| Intake/context | User idea, selected sources, profile, unresolved questions | Clarified facts, focused questions, baseline proposal | Proposed records only; cannot invent answers or accept intent |
| Platform brain | Accepted baseline/envelope, profile, sources, prior findings | Versioned task plan or justified technical replan | Plans and assignments; cannot change accepted criteria, authority or controller verdict |
| Intent controller | Baseline, plan/diff/evidence, materiality rules | Current allow/rework/material-decision/insufficient-evidence verdict | Verdict/findings only; cannot edit implementation or redefine success |
| Coder | Scoped task, relevant source/contracts, allowed paths | Candidate diff, rationale, limitations, evidence pointers | Assigned implementation/docs only; no protected oracle/control records |
| Test author | Behavioral criteria, platform interfaces, protected rubric | Tests and criterion mapping | Assigned test paths; no baseline, hidden evaluator or permission changes |
| Test runner | Current candidate, declared exact commands, allowance | Observed check receipts and structured failures | Owned execution artifacts only; no interpretation that weakens expected behavior |
| Reviewer | Pre-inspection context, exact candidate and checks | Severity-tagged findings and pass/changes/incomplete | Review records only; cannot self-review builder work under another label |
| Diagnostician | Bound failure, reproducer, relevant diff/source | Failure class, causal evidence, smallest repair/recovery proposal | Diagnosis only; cannot dispatch unlimited retries or widen scope |
| Documentation/delivery | Current accepted candidate and evidence | Accurate guides and local contribution bundle | Assigned docs/bundle; no unapproved submission or private-data export |
| Coordinator | Durable state, policy, budgets, graph, valid results | Admitted transitions and task dispatch | Runtime store/owned task controls; cannot manufacture identity/consent |

## Required assignment envelope

Every task includes schema version, job/task/attempt IDs, role, current intent/plan/envelope digests, environment/profile revision, objective, criterion IDs, input references/digests, allowed write paths, excluded/protected paths, dependencies, allowed effects/tools, finite allowance, required result shape and stop conditions.

Provide only relevant selected source context. All retrieved text remains untrusted. A source instruction cannot change the worker's role or authorization. Result JSON is also untrusted until validated.

## Required result envelope

A result reports schema version, matching identities/digests, producer/session references exposed by the host, outcome (completed/failed/blocked/unknown/cancelled), artifact references/content hashes, actual changed paths, evidence references, findings, usage observations with known/unknown distinction, uncertainty and suggested next action.

A worker may claim completion. The coordinator independently checks identity/role/bindings, declared versus actual changes, current graph state, allowance, required evidence and unresolved effects. A completed host turn alone never sets job readiness.

## Independent controller checkpoints

Require a current verdict before initial plan admission, candidate integration, repair plan admission where it changes tactics, replan adoption and final handoff. The controller compares meaning as well as structure: intended users/outcome, criteria, non-goals, platform constraints, added side effects and whether evidence demonstrates the actual request.

Verdicts identify the reviewed object/digests, checkpoint, per-criterion observations, deviations, materiality, evidence limitations and next action. Missing evidence is insufficient-evidence, not automatic approval. A new candidate or changed plan cannot adopt a stale verdict.

## Separation and review

Brain and controller have separate role contexts. Builder and reviewer have genuinely separate review execution, not just different actor strings. Test author derives behavior from the baseline and platform contract; protected evaluation remains outside builder ownership. Test-author independence does not require hiding all source forever; any source exposure and review context must be explicit.

Host APIs may not offer enforceable per-role tools. In that case record the narrower assisted trust model; do not claim the prompt enforces OS isolation. Changes to the control plane, schema, oracle or reviewer policy need independent inspection and their own regression cases.

## Stop conditions

Workers stop and report when the task no longer matches current digests, they need undeclared effects or files, platform facts are unavailable, budget is exhausted, input is contradictory, cancellation/revocation is observed or effects cannot be determined. The coordinator classifies the next step. Focused human questions are for material decisions; ordinary in-scope defects go through repair.
