# Target contracts and implemented subset

The coordinated extensions are C-017 through C-024. C-001 through C-016 remain useful logical contracts; where the old frozen-brief/manual workflow is described, it is the current assisted-v1 subset, not the target materiality policy.

These are project-authored logical contracts, not copied organizational policy
or a promise that every interface already exists. The exact implemented schema
is `sparkforge.spec.v1` and the helper APIs described by
[SFS-001](../specs/NATIVE_FACTORY_SLICE.md). Future trust, transport and release
mechanisms must satisfy the remaining obligations without inventing authority.

## C-001: common envelope and evidence origin

**Requirements:** SF-11, SF-20, NFR-02, NFR-03, NFR-04.
**Decisions:** D-008, D-009, D-023.

Records need an explicit version, kind, applicable scope, revision, producing
operation and evidence class. Pre-job environment facts must not fabricate a job.
Unknown versions, conflicting identities and malformed records fail explicitly.
Origin labels distinguish observations, fixtures and assertions; a worker-written
label is not authentication. The local journal supplies consistency, not a
cryptographically protected record store.

## C-002: host profile and execution authorization

**Requirements:** SF-13, SF-16, SF-18, NFR-01, NFR-05, NFR-06.
**Decisions:** D-003, D-006, D-007, D-008, D-013, D-021, D-022.

Bind any real effect to the actual selected host, identity, data/provider/storage
route, tools, resources and permitted action. An installed executable, accepted
configuration shape or available credential does not select or qualify a profile.
The host-record checker always leaves host qualification/execution authority
false. Authenticate and enforce the real boundary externally before claiming
unattended operation.

## C-003: intake, source and reuse assessment

**Requirements:** SF-01, SF-02, SF-03, SF-12, NFR-01, NFR-07, NFR-09, NFR-10.
**Decisions:** D-005, D-007, D-011, D-018.

Preserve input provenance, applicable source rights, revision, scope, coverage,
limitations and conflicting facts. Treat acquired instructions as data.
Assess actual component behavior and selected code before REUSE, UPDATE_EXISTING
or NEW_COMPONENT. A snapshot hash does not establish current truth; absent
comparison stays `NOT_ASSESSED`, not proof of no existing capability.
Returned excerpts expose truncation and omissions instead of implying full review.

## C-004: immutable build brief and expected inventories

**Requirements:** SF-02, SF-03, SF-04, SF-05, SF-06, SF-08, NFR-02, NFR-08, NFR-09.
**Decisions:** D-002, D-005, D-009, D-011, D-012.

Freeze intended behavior, audience, non-goals, source/reuse rationale, controlled
files, acceptance, exact check commands/limits and the reviewer inventory.
Reject missing or unknown fields rather than accepting an approval flag embedded
in content. Canonical serialization provides the spec digest.
Changing material scope or required evidence needs a new revision and decision.
An example is not an accepted brief.

## C-005: trusted approval and revocation

**Requirements:** SF-04, SF-10, SF-15, NFR-01, NFR-02.
**Decisions:** D-002, D-006, D-009, D-023.

Real approval must name the exact current object and originate from its actual
decision owner. Reject stale, foreign or fabricated authority. Intent acceptance
does not grant every source, command, provider, publication or deployment effect.
The implemented manual command records an operator assertion; the native worker
must not use it to approve itself. A future trusted ingress and revocation
mechanism require independently qualified identity and effect mediation.

## C-006: job lifecycle and atomic commands

**Requirements:** SF-04, SF-09, SF-10, SF-11, SF-20, NFR-02, NFR-03, NFR-06, NFR-09.
**Decisions:** D-004, D-008, D-009, D-014.

Persist preconditions and event/state transitions atomically. Preserve active
operations, attempts, revisions, cancellations and failures. Missing candidate
files remain implementation work, not empty passing evidence.
Current helper states distinguish approval, pending/failed checks, stale bytes,
pending/negative review, cancellation and reconciliation. The status projection
cannot itself approve an action. Invalid or conflicting state stops admission.

## C-007: work package and worker exchange

**Requirements:** SF-05, SF-06, SF-07, SF-08, SF-09, SF-20, NFR-01, NFR-06, NFR-08.
**Decisions:** D-004, D-010, D-012.

Before delegation identify objective, accepted baseline, owned paths, exclusions,
dependencies, allowed effects/resources, acceptance, failure/stop conditions and
integration owner. Independent work needs disjoint writes and deliberate
integration. Returned output reports changed artifacts, actual outcomes and
limitations. A handoff is not dispatch, approval or proof of isolation.
The current package directs host workers; it does not implement a scheduler.

## C-008: revision/run/attempt binding

**Requirements:** SF-04, SF-07, SF-10, SF-11, NFR-02, NFR-07, NFR-08.
**Decisions:** D-008, D-009, D-010, D-012.

Do not conflate job/spec/candidate/check/run/attempt/round identities. Credit only
consistent results for the current accepted spec and actual controlled bytes.
Bind check sequence to persisted attempt history so a counter rollback cannot
resurrect an earlier review. A runner label/digest is consistency metadata,
not proof that an adversarial same-privilege writer cannot forge the store.
Material input or acceptance changes invalidate affected evidence.

## C-009: checks and reviewer results

**Requirements:** SF-06, SF-07, SF-08, SF-09, NFR-02, NFR-08.
**Decisions:** D-009, D-012, D-019.

Checks need actual completion, expected shape/markers, exit/output observations,
limits and current producer/binding metadata. Missing, truncated, timed-out,
foreign or inconsistent evidence cannot pass. Preserve all attempts.
Reviewers capture context before inspection and submit the same token; changes
require re-review, not relabeling an old opinion. Missing/negative required
reviews block readiness. Independent review remains an assertion whose genuine
origin is the host/operator's responsibility.

## C-010: artifacts, evidence and readiness

**Requirements:** SF-07, SF-08, SF-11, SF-14, SF-19, NFR-02, NFR-04, NFR-08.
**Decisions:** D-006, D-008, D-009, D-012.

The declared expected inventory, current artifact bytes and admissible check/
review results determine scoped readiness. No missing item is an implicit pass.
The implemented `CANDIDATE_VERIFIED` state means local inventory completeness,
not genuine human acceptance, host security or publication authorization.
Keep permitted summaries separate from raw runtime state; match any packaged
artifact to the exact source/resources that were assessed.

## C-011: feedback and rework

**Requirements:** SF-02, SF-09, SF-10, SF-11, SF-12, SF-21, NFR-09.
**Decisions:** D-002, D-009, D-012, D-014, D-025.

Link feedback to the job/component and source revision. Distinguish an in-scope
defect from changed intent, data authority or acceptance. Repair reruns affected
checks; material change creates a revision and a new decision. Preserve earlier
outcomes and explain the current blocker in plain language.
Learning observations are inactive proposals or an explicit no-change result,
not an automatic instruction to edit or execute.

## C-012: errors and resource outcomes

**Requirements:** SF-09, SF-10, NFR-03, NFR-04, NFR-06.
**Decisions:** D-006, D-007, D-013, D-014.

Expose typed failure, unavailable prerequisites, exhausted resources and unknown
effects without sensitive payloads or success-shaped defaults. Finite timeout,
output and attempt limits belong in the accepted operation. Do not retry under
a different provider, invent unlimited budgets or change criteria to remove
a failure. Distinguish engineering limits from unapproved product SLOs.

## C-013: cancellation, recovery and uncertain effects

**Requirements:** SF-09, SF-10, SF-11, SF-20, NFR-03, NFR-04, NFR-06.
**Decisions:** D-008, D-010, D-013, D-014.

Reserve durable operation identity before dispatch. A lost session or response
requires inspection/reconciliation, not duplicate execution. Cancellation stops
new admission and preserves residual-effect uncertainty.
The helper stops only its owned direct process; descendants and kernel calls
are not a sandbox/hard-deadline guarantee. Manual reconciliation requires
actual evidence that the relevant operation stopped and its effects were
assessed. A recorded PID alone is not durable kill authority.

## C-014: submission intent and receipt

**Requirements:** SF-14, SF-15, SF-18, SF-19, NFR-01, NFR-03, NFR-10.
**Decisions:** D-002, D-014, D-016, D-020.

Any external action needs an explicit destination, exact payload/ref, identity,
permissions and requested effect. Local readiness and a preview do not submit
anything. Changed payload/target requires its appropriate decision; uncertain
outcomes require read-only reconciliation before retry.
Record the actual resulting remote identity. A private repository does not
clear restricted data, and repository publication is not a production release.

## C-015: package and adaptation manifests

**Requirements:** SF-05, SF-13, SF-14, SF-16, SF-17, SF-19, NFR-05, NFR-07, NFR-10.
**Decisions:** D-005, D-015, D-017, D-020, D-024.

Declare owned resources, profile, dependencies, version, byte inventory,
support scope and evidence class. Resolve installed resources from the actual
package, not an undeclared sibling checkout. Refuse collisions and unsafe paths.
Both local profile exports are structural templates; each actual target needs
its own discovery, installation/lifecycle, permissions and acceptance.
An authorized adaptation never carries credentials, journals or unapproved data.

## C-016: governed self-improvement

**Requirements:** SF-21, SF-04, SF-08, SF-09, SF-10, SF-11, SF-20, NFR-01, NFR-02, NFR-03, NFR-06, NFR-08, NFR-10.
**Decisions:** D-002, D-006, D-009, D-012, D-013, D-014, D-018, D-019, D-025.

Use permitted observations with origin/scope and an explicit hypothesis. An
inactive candidate must face independent evaluation, regressions and retained
negative results before exact authorized promotion. Monitor and withdraw only
within a separately approved resource/data envelope; never restore revoked data.
The learner cannot alter its own policy, oracle, provider, reviewer or budget.
No-change is legitimate. The current native workflow supports proposal/no-change
discipline, not a completed automatic promotion/rollback implementation.

## C-017: intent plan and envelope separation

**Requirements:** SF-04, SF-10, SF-25, SF-26, NFR-01, NFR-02.
**Decisions:** D-026, D-027.

IntentBaseline captures behavior/non-goals; ExecutionEnvelope captures one environment and finite permissions/resources; ExecutionPlan captures technical tasks. Equivalent technical changes require current controller/admission checks, not blanket intent reapproval. Existing v1 exact-spec semantics remain unchanged until an explicit bridge/migration is implemented.

## C-018: agent role assignment and result admission

**Requirements:** SF-20, SF-22, SF-27, NFR-01, NFR-02, NFR-08.
**Decisions:** D-026, D-028.

Every assignment/result binds job, task, attempt, role, intent/plan/envelope, candidate/inputs, ownership and allowance. Host completion and worker claims are untrusted until current deterministic admission. Roles communicate through explicit artifacts; independence requires observed host producer/context separation.

## C-019: platform brain and semantic intent controller

**Requirements:** SF-02, SF-03, SF-23, SF-24, SF-26, NFR-08, NFR-09.
**Decisions:** D-026, D-027, D-030.

Brain plans/replans from profile and cited sources. Controller independently checks cumulative intent alignment at plan/integration/repair/replan/handoff. Neither may rewrite the baseline/oracle to accept a deviation; insufficient evidence remains explicit.

## C-020: diagnosis repair and technical replanning

**Requirements:** SF-07, SF-09, SF-10, SF-28, SF-29, NFR-03, NFR-06, NFR-08.
**Decisions:** D-027, D-029.

Classify code/oracle/environment/intent/stale/unknown/budget failures. Route the smallest in-scope repair, refresh affected evidence and retain failed attempts. Replanning keeps criterion coverage and job-wide totals. No-progress or exhausted allowance stops new work.

## C-021: durable scheduling and operation identity

**Requirements:** SF-20, SF-27, SF-30, NFR-02, NFR-03.
**Decisions:** D-028, D-029.

Validate graph and role barriers, reserve before effects, bind command keys to payloads, and persist event/projection atomically. Same operation replay cannot duplicate admitted work. Unknown completion, cancellation and late results require explicit observed reconciliation.

## C-022: host adapter and environment-local profiles

**Requirements:** SF-13, SF-16, SF-17, SF-22, SF-23, NFR-01, NFR-05.
**Decisions:** D-028, D-030.

Host supplies only documented/observed capabilities for dispatch, poll, stop, reconcile, producer context and usage. Fake adapters are labeled. Each run has one profile and isolated sources/credentials/state; no assumed native launcher or corp/acro bridge.

## C-023: aggregate budgets and independent evaluator

**Requirements:** SF-06, SF-08, SF-24, SF-29, NFR-06, NFR-08.
**Decisions:** D-029, D-031.

Reserve finite job/agent/check resources before dispatch and retain totals across repairs/replans. Unreported usage is unknown. Protected behavioral evaluation stays outside coder ownership and rejects known-bad controls even when worker checks report success.

## C-024: resumable contributor handoff

**Requirements:** SF-11, SF-19, SF-20, SF-31, NFR-07, NFR-09.
**Decisions:** D-032, D-033.

Maintain one current backlog, detailed implementation plan, exact validation record, append-only cycle and concrete next task. Archived planning and historical IDs remain attributable but cannot gate active source-neutral work. Copilot can continue without private chat context.
