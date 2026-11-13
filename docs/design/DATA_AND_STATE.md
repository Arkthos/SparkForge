# Data contracts, state and compatibility

**Implemented coordinated contracts:** intent/envelope (WP-110), task/attempt/agent-result/finding/failure (WP-111). Plan, event, controller-verdict and evidence-bundle bodies remain planned. Current implemented `sparkforge.spec.v1` and assisted journals retain their own meaning.

## WP-110 public contract API

Import `plugins.sparkforge.runtime.contracts` through Python namespace packages; no initialization side effects or unused schema copies are needed. `validate_intent(value, supported_component_kinds=(...))` returns a detached `IntentBaseline`. The caller supplies a nonempty, unique vocabulary from its selected profile; the validator does not invent platform kinds or certify that profile. `validate_envelope(value, intent=baseline)` returns a detached `ExecutionEnvelope` after structural validation and exact intent ID/digest matching.

`parse_json(str_or_utf8_bytes)` rejects duplicate keys, malformed UTF-8/JSON, nonfinite numbers and excessive nesting. Pass its result to the record validator. `canonical_json(normalized_record)` uses the existing v1 canonicalization convention (sorted keys, compact JSON, unescaped Unicode, no nonfinite numbers); `record_digest(normalized_record)` is SHA-256 of those UTF-8 bytes. Every field and list order is bound. Validation does not silently trim text, normalize Unicode prose or omit authority-sensitive fields. `ContractError` supplies `code`, `path` and a bounded diagnostic without echoing input values.

| Contract choice | Implemented semantics |
|---|---|
| Identity and text | Closed fields; IDs are 1-80 ASCII letters/digits/`._-`, starting alphanumeric; revisions 1-1,000,000. Text is nonblank, at most 12,000 characters; tab/CR/LF allowed, other control/format/surrogate characters rejected. |
| Collections and serialization | At most 128 entries per ordinary list, two MiB UTF-8 per record and 32 JSON nesting levels. Duplicate criteria/source/reference/list identifiers fail. List order remains meaningful. Empty non-goals/constraints explicitly mean none; acceptance and source assumptions are nonempty. |
| Sources | Each assumption has ID, `known`/`unknown`/`unavailable`, statement, reason and references. References have opaque IDs and nullable revision/digest. Unknown bytes do not require invented hashes; even known references do not assert freshness or permission. |
| Environment/routes | Exactly one `LOCAL_DEVELOPMENT`, `CORP` or `ACRO`; profile, host and provider are opaque ID/positive-revision references, not credential-bearing URLs. Tools/effects are finite identifier lists, possibly empty. No credential or approval fields are accepted. Free text is not a secret scanner; callers must keep credentials out of all input. |
| Roots/paths | Roots carry ID, explicit `windows` or `posix` flavor and an absolute path. Windows uses uppercase drive plus backslashes; POSIX uses one leading slash. Volume/filesystem roots, UNC/devices, traversal, repeated/trailing separators, reserved Windows names, ADS, wildcard/8.3 aliases, Git internals and environment-secret paths fail. NFC spelling is required for paths, never silently converted. Up to 32 workspace roots (at least one) and 32 data roots (possibly none); duplicate IDs and lexical root aliases fail. |
| Relative identifiers | `relative_path(value)` accepts only canonical slash-separated relative paths, independently of the executing OS. Windows roots are never passed through the host's POSIX parser. Path components use the same portable restrictions; actual symlink/hardlink/network checks belong to later workspace admission. |
| Bounds | Positive integers only: job wall time <=604,800s; per-agent timeout <=86,400s; check timeout <=3,600s; agent/check attempts <=20; check output <=16 MiB; token caps <=1,000,000,000; other job/call/replan counts <=1,000,000. Per-agent/check allowances must fit job bounds. Disallowed work is represented by missing effects/tools, not unlimited/zero caps. |
| Usage/expiry | `unknown_usage` is `stop` or `reserve_maximum`, never assume-zero. `expires_at` is a real calendar UTC `YYYY-MM-DDTHH:MM:SSZ`; revocation contains both timestamp/reason or two nulls. Validation preserves expired/revoked proposals for later policy inspection; it neither probes the clock nor admits effects. |

These are structural proposal contracts, not a permission grant, materiality decision, source acquisition, authenticated producer identity, path sandbox or execution engine. TC-103/104 are exercised in `tests/test_runtime_contracts.py`; later admission must independently establish profile support, current authority, freshness, environment/path availability and accumulated allowances.

## WP-111 worker contract API

`plugins.sparkforge.runtime.agent_contracts` contains the cohesive worker-record family, sharing the strict WP-110 JSON/text/path/error helpers. The five closed records are `sparkforge.task.v1`, `sparkforge.attempt.v1`, `sparkforge.agent-result.v1`, `sparkforge.finding.v1` and `sparkforge.failure.v1`. No agent is installed or invoked by their validation.

| Function / record | Binding and semantics |
|---|---|
| `validate_task(value, intent=..., envelope=..., plan_sha=..., candidate_sha=...)` / `TaskAssignment` | Job/task/attempt/role plus intent/envelope/plan/candidate/input digests; input inventory digest recomputed. One matching environment/profile/host/provider, workspace ID and data-root subset; criteria exist in the baseline. Exact candidate writes cannot overlap protected path prefixes; no aliases/globs/absolute paths. Effects/tools/allowances cannot expand the envelope; deadline cannot exceed expiry. |
| Task result kinds | `intake: baseline_proposal`, `brain: plan_proposal`, `controller: controller_verdict`, `coder: candidate`, `test_author: tests`, `test_runner: check_report`, `reviewer: review`, `diagnostician: diagnosis`, `delivery: delivery_bundle`, `coordinator: coordination`. Only coder/test-author/delivery tasks may list candidate writes, with explicit `workspace_write`. Other role outputs use opaque artifact references, not arbitrary output filesystem paths. |
| `validate_attempt(value, task=...)` / `AgentAttempt` | Exact assignment digest/binding, durable operation key, bounded ordinal, separate host producer/observation, timestamps and observed usage. Reserved work cannot claim dispatch; accepted/running/cancel-requested are not completion. Unknown state preserves missing observation and usage rather than assuming no effects. |
| `validate_result(value, task=..., attempt=..., current_candidate_sha=..., prior_producers=(...))` / `AgentResult` | Exact assignment and current input-candidate binding, observed producer match, role-specific result kind, outcome, opaque artifact/evidence digests, claimed changed paths/output candidate, findings/failures, worker usage claim, uncertainty and next action. Host turn completion is necessary but never admits the claim as completed job evidence. Failed/cancelled/unknown host observations cannot become successful worker results. |
| Producer separation | Controller/test-author/reviewer results require caller-supplied relevant prior producer observations. Reusing the same stable host ID/context fails even if actor/session labels or host configuration revision change. These consistency checks cannot authenticate observations or establish that the caller supplied a complete prior-producer set; qualified host ingress remains mandatory. |
| `validate_finding` / `Finding` | Severity, failure category, bounded message/recommendation, optional canonical relative location, acceptance IDs and evidence refs. Enclosing result checks criterion membership and exact evidence identity/digest. Findings cannot grant approval. |
| `validate_failure` / `Failure` | Implementation/oracle/environment/intent/authority/stale/budget/unknown-effects/unknown cause; evidence or an explicit limitation; bounded correction suggestion. Unknown effects must suggest reconcile/stop, never an unobserved safe retry. A failed/blocked result must include a structured cause. |
| Usage | Host `observed_usage` and worker `usage_claim` remain distinct. Known values are nonnegative integers <=10^12; observed overruns are retained, not rejected or replaced by lower worker claims. Unknown values must all be null with a reason, never zero. Accounting/admission is WP-123. |

Arrays/text/identifiers use WP-110 limits; exact candidate path lists allow up to 512 entries. The functions normalize and revalidate supplied task/attempt structures, but only `validate_task` compares the complete intent/envelope/current-plan context. Callers must supply current authoritative observations, not let a worker substitute the comparison inputs. Actual graph membership, protected-control inventory, candidate bytes, authentic producer separation, current expiry/revocation and effect permission are later deterministic admission responsibilities. TC-105/106 are exercised by `tests/test_agent_envelopes.py`.

## Record ownership and binding

| Record | Required substance | Binding / owner |
|---|---|---|
| IntentBaseline | Outcome, audience, component kind, criterion IDs and behavior, non-goals, material constraints, source assumptions | Canonical digest and explicit user decision; user owns changes |
| ExecutionEnvelope | One environment/profile, permitted roots/tools/data/provider/effects, timeout/attempt/call limits, usage-unknown policy, expiry/revocation | Separate digest and actual operator/authority ingress |
| ExecutionPlan | Intent/envelope refs, task graph, role assignments, criterion coverage, controlled files/dependencies, check/reviewer inventory, plan rationale | Monotonic plan revision and previous-plan link; brain proposes, controller checks |
| TaskAssignment | Objective, role, dependencies, inputs, scope, acceptance, allowance, stop conditions | Job/task/attempt + intent/plan/envelope/input digests |
| AgentAttempt | Dispatch reservation, operation key, producer context, start/completion, observed usage | Host receipt + durable event identity; not a worker-supplied authority string |
| CandidateManifest | Controlled implementation/test/config/dependency file list, sizes/hashes and ownership | Exact candidate digest; include behaviorally relevant dependencies |
| CheckReceipt | Command, check/criterion IDs, exit/completion, output digest/limits, duration, uncertainty | Current candidate, task/attempt/check sequence and runner origin |
| Review/ControllerVerdict | Object reviewed, pre-inspection context, findings, criterion assessment and verdict | Current candidate/plan/evidence sequence; actual producer relationship |
| DecisionRequest/Decision | Material delta, alternatives, impact, exact object, responder/origin, time/revocation | Current target digest; editable JSON cannot authenticate its own origin |
| EffectIntent/Receipt | Destination, payload digest, requested effect, permitted identity, observed remote result | Durable operation key; unknown outcomes reconcile before retry |
| EvidenceBundle | Required inventory and admitted references, failures, skips, limitations, package binding | Completeness of current evidence only; not an independent grant of authority |

Use deterministic UTF-8 canonical JSON, stable field ordering and explicit finite numeric handling. Reject duplicate keys, unknown fields/versions, invalid enums, alias paths, missing required values and nonfinite numbers. A hash covers the full canonical record, not a selectively omitted constraint. Keep a clear distinction between user text and identifiers.

## Proposed job states

```mermaid
stateDiagram-v2
  [*] --> Intake
  Intake --> NeedsDecision: Material ambiguity
  NeedsDecision --> Planning: Current decision
  Intake --> Planning: Baseline and envelope accepted
  Planning --> Ready: Controller aligned
  Planning --> NeedsDecision: Material delta
  Ready --> Running: Reserved dispatch
  Running --> Checking: Admitted artifacts
  Checking --> Reviewing: Current checks pass
  Checking --> Diagnosing: Failure
  Reviewing --> Diagnosing: Blocking findings
  Diagnosing --> Repairing: In scope and allowance
  Repairing --> Checking: New candidate
  Diagnosing --> Planning: Technical replan
  Diagnosing --> NeedsDecision: Changed intent or allowance
  Reviewing --> Verified: Final controller and all evidence
  Running --> Reconciling: Unknown completion
  Reconciling --> Ready: Observed safe resumption
  Verified --> Delivered: Local handoff
  Ready --> Cancelled: Cancellation
  Running --> Cancelling: Cancellation
  Cancelling --> Cancelled: Effects reconciled
  Cancelling --> Reconciling: Unknown effects
```

This diagram is conceptual; WP-112 defines the exact executable enum and transition table. Blocked and failed task projections preserve their cause without conflating terminal job failure, a retryable defect and unresolved effects. Cancellation/revocation stops new admission in every nonterminal state even where the diagram omits repetitive edges.

## Store and command requirements

- Persist expected revision, command idempotency key, payload digest, event and projection atomically. Same key/same payload returns prior result; same key/different payload is a conflict.
- Reserve dispatch/check/external effects before calling the adapter. A reservation with no completion is unresolved, not automatically unused. Record observed usage once under the operation identity.
- Derive pending tasks from the validated graph, not model-selected arbitrary task IDs. One active task initially; no indefinite writer waits.
- Append historical attempts, plans, findings and decisions. A changed projection does not rewrite earlier evidence. A local SQLite journal remains same-privilege mutable; do not claim tamper-proof audit.
- Store role/session/producer receipts as observations. Authentication and per-role privilege enforcement depend on actual host capabilities.

## Invalidation and replay

| Change | Required effect |
|---|---|
| User behavior/non-goal/accepted constraint | New intent revision and decision; affected plan/results become stale |
| Envelope authority, environment, provider or data route | New envelope/authority; stop affected admissions and reassess in-flight work |
| Equivalent technical plan | New plan revision, controller verdict and dependency-impact analysis; preserve allowance totals |
| Controlled candidate/dependency bytes | Invalidate affected checks/reviews/controller outcome; recompute mandatory regression evidence |
| Check rerun on identical bytes | Advance evidence sequence; old review context cannot certify new evidence |
| Source/profile revision | Reassess decisions depending on those sources; no assumed freshness inheritance |
| Revocation/cancel | Stop new work; late results cannot resurrect superseded authority |
| Lost response/restart | Inspect reservation by operation key; reconcile, do not blindly replay |

Only explicitly proven-independent evidence can survive a plan revision. Default to invalidating affected evidence; do not optimize by attaching old findings to a newly fetched token. Hidden dependencies require a fuller candidate inventory or narrower claim.

## v1 coexistence and migrations

Do not import `job.sqlite3` as a coordinated job or fabricate acceptance for it. Coordinated stores have their own schema/version and root. A v1 journal may be referenced read-only with a clearly scoped evidence class. It does not inherit accepted intent, envelope or host independence.

WP-125 must reuse the runner's mechanics without calling v1 `decide` as a fake operator. Options are a tested explicit adapter to genuinely accepted v1 jobs or a narrow shared execution extraction with both old and new admission front ends. Keep v1 public behavior and all applicable regression tests unchanged. Record the extraction decision before implementation.

Future store upgrades need explicit version detection, a verified backup/copy, a transaction or new-store migration, validation and rollback. Reject unknown versions without modifying originals. No automatic migration of real operator state in synthetic tests.

## Observability and retention

Local runtime stores may contain source locators, paths, prompts and output. Default summaries should contain only the data needed to explain state/evidence. Retain raw output only under the selected envelope. Never commit real jobs, private profiles, model transcripts or mixed archives. Recovery backups and retention permissions remain target-local; Git is not the runtime store.
