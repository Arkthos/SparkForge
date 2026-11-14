# Human decisions and delegated autonomy

**WP-122 structural policy is implemented alongside assisted v1.** Materiality comparison, exact decision bindings, envelope membership, expiry and revocation now run through the coordinated journal. Authentic ingress identity, semantic controller judgment and the full live factory remain separate qualification/implementation work. Assisted-v1 manual exact-spec semantics are unchanged.

## Implemented policy boundary

`runtime/policy.py` supplies `classify_change`, `decision_request`/`validate_request`, `decide`/`validate_decision`, `validate_binding`, `revocation`/`validate_revocation`, `envelope_membership` and `authorize`. These are deterministic record/scope operations, not a model reasoning service or an identity provider.

| Behavior | Implemented rule |
|---|---|
| Materiality | Compare complete proposed intent/envelope records with the accepted pair, not a worker-supplied diff or previous unaccepted proposal. Changed intent needs its owner; changed envelope needs its execution owner. Task criterion/protected-path/result-kind/role changes are control changes, not ordinary replans. Labels such as repair or refactor cannot hide those differences. |
| Ordinary continuation | Identical accepted intent/envelope with structurally in-scope task tactics yields `IN_SCOPE_STRUCTURAL` without a new decision. Scope/allowances are still checked; this does not certify semantic equivalence, approve a changed scheduler graph or integrate code. Unknown external effects yield `RECONCILE`. |
| Exact requests/responses | A request contains job, full target kind/ID/revision/digest, accepted-baseline digest, reason, alternatives and impact. A response binds the complete request digest and explicitly accepts/rejects/requests changes. Altering target, impact or accepted baseline makes an old response stale. |
| Separate authority owners | Intent and execution-envelope decisions require separate scoped ingress assertions (`intent_owner` / `execution_owner`). Response JSON cannot carry self-issued actor/approved/confidence fields. Ingress is separately supplied and constrained to host/operator assertions; explicit `synthetic_fixture` assertions are valid only for LOCAL_DEVELOPMENT tests. None of these labels authenticates its producer. |
| Accepted policy binding | A `sparkforge.policy-binding.v1` record chains the previous accepted binding and exact intent/envelope decisions. No resetting revision/history, stale baseline or rejected/revoked grant. An unchanged target can reuse its still-valid existing decision; changed scope requires a new exact acceptance. |
| Membership/time | Reuse P1 validation for environment/profile/provider, selected workspace/data roots, tools/effects, protected writes, criteria, finite allowances and task bindings. Journal admission checks current envelope expiry and task deadline, and cannot silently move the store workspace. |
| Revocation | Append an exact target/decision revocation with its scoped origin and reason. It blocks new effect and success admission, but does not delete decisions/observations, mark unknown effects unused or forbid factual reconciliation. A committed revocation remains effective despite later clock rollback. |

Journal `record_decision`, `bind_policy`, `revoke`, `classify` and `authority_status` provide working persistence/admission paths. New command-v3 writes assign `admitted_at` inside the writer transaction; callers cannot supply a backdated value. Records, decisions and replay outcomes remain immutable/idempotent. Clock regression blocks new work or authority/success admission, not cancellation, observation storage or non-authorizing reconciliation.

New reservations, dispatch and passing evidence/completion require both an accepted live policy binding and eligible parent/job state in the same transaction. Coordinator preflight only explains blockers; it is not the enforcement boundary. Unaccepted/expired/revoked/stale scope reports `POLICY_BLOCKED`. Existing v1/v2 command history remains replayable; it does not grant new command-v3 work permission. Old jobs without policy decisions can still be inspected/reconciled, but need explicit scoped acceptance before new work.

The active policy pair is separate from immutable initial job records. Updating accepted scope does not automatically rewrite assignments, adopt another schedule, reset allowance/consumption or migrate a workspace. Superseded assignments stop with `POLICY_BINDING_MISMATCH`; the later replanning/integration protocol must produce current work.

**Limits:** classification is structural, not proof that arbitrary prose/code preserves intent. Control-policy/oracle/reviewer changes remain material and are not auto-approved by the intent/envelope decision API. Host/operator assertions remain `authenticated: false`; genuine ingress authentication is outside this slice. Aggregate resource accounting is WP-123. Native effects, actual code integration and full model-driven acceptance remain later work. Tests seed only explicitly labeled fictional decisions; no real approval is manufactured.

## Establish the initial envelope

Before real factory implementation, make the intended outcome/acceptance/non-goals and bounded execution scope reviewable. Existing instructions or an established operating profile may already authorize the needed scope; do not ask the same question again. If behavior or authority is missing or materially ambiguous, ask the relevant owner for the exact decision. Never treat silence, time elapsed, a generated field or a worker label as consent.

For development of SparkForge itself, the current owner has requested repository organization, planning, cleanup, validation and GitHub publication. Synthetic implementation/testing after the supplied Copilot handoff can proceed under that development scope. That does not supply real corp/acro access, unlimited model spending or production deployment permission.

## Materiality table

| Proposed action/change | Default route | Required evidence |
|---|---|---|
| Fix code failing an unchanged accepted behavior | Continue automatically within allowance | Bound diagnosis, owned diff, fresh affected checks and review |
| Refactor internal code preserving public behavior | Continue after plan/controller checks | Compatibility/regression evidence and ownership |
| Change technical task order/strategy inside envelope | New plan revision; no fresh intent decision | Dependency impact, controller alignment, unchanged budget totals |
| Add supplemental tests for unchanged behavior | Continue with independent test checks | Criterion mapping; existing mandatory oracle unchanged |
| Correct a genuinely erroneous expected result | Independent oracle assessment; decision if accepted behavior changes | Original failure retained, rationale and owner of affected criterion |
| Change user outcome, supported audience, acceptance or non-goals | Ask user/domain owner | Exact intent delta, alternatives and impact |
| Introduce new dependency/tool/provider/account/data route | Check existing envelope; ask actual authority if outside it | Exact capability/effect/resource delta; no silent substitution |
| Exceed agreed attempts/model calls/time/cost limit | Stop new work and request extension or narrower outcome | Used/remaining/unknown usage, cause and concrete options |
| Select a different environment or transfer restricted content | Target-local authority and applicable disclosure decision | Exact files/destination/data route; no inherited corp permission |
| Publish, merge, install or deploy | Execute only within the current specifically authorized effect scope | Exact target/payload; current evidence and reconciliation path |
| Unknown outcome after timeout/lost response | Reconcile before retry | Host/destination observation under durable operation key |
| Promote a learning proposal or change evaluator/control rules | Independent evaluation and exact promotion/change decision | Baseline comparison, regressions, version and rollback |

These defaults apply to actual scope, not action names. An innocuous-sounding refactor can change behavior; an already-authorized publication does not require another redundant confirmation. Batch related decisions into a concrete reviewable proposal when useful.

## Decision request contents

State the exact blocked action/object, why the existing envelope does not cover it, relevant evidence, alternatives, behavioral/data/resource consequences, recommended option and what continues independently. Ask a focused question. Do not bury the decision in a long log or ask the user to approve an unseen specification.

Bind the response to the current intent/envelope/effect object and record its genuine origin. A stale answer cannot authorize a changed payload. Revocation prevents new admission and requires in-flight reconciliation. Authority origin remains the host/operator responsibility until an actual trusted ingress is implemented and qualified.

## Controller versus deterministic policy

The controller evaluates semantic alignment and proposes a materiality verdict with cited differences. Deterministic admission independently checks environment, allowed effects/tools/paths, explicit criterion changes, resource totals and current decision bindings. A controller confidence score does not override those checks. Unknown materiality remains unresolved, not auto-approved.

Cumulative small changes are assessed against the accepted intent/envelope, not only the immediately preceding revision. This prevents many individually small adjustments from turning into a different product.

## Existing assisted-v1 behavior

The shipped `sparkforge.spec.v1` freezes behavior, commands, files and bounds in one record. Its manual `decide` binds the exact digest, and `revise` clears approval. Those remain unchanged. WP-122 now implements coordinated structural policy, not a bypass of v1 decisions or completion of the WP-125 check bridge. Full policy/host/engineering-loop acceptance still requires its relevant integration evidence.
