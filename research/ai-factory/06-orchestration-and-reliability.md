# 06 - Orchestration, Concurrency, and Reliable Execution

[Back to the index](README.md)

## Orchestration is coordination, not intelligence

An orchestrator decides which work may run, in what order, under which constraints, and how results are combined. It can be ordinary code, a graph, a queue-driven service, a model-driven planner, or a combination.

The right question is not "How many agents can we spawn?" It is "Which decomposition improves the outcome enough to justify its coordination cost?"

Anthropic's workflow taxonomy provides a useful starting set: chaining, routing, parallelization, orchestrator-workers, and evaluator-optimizer patterns. [S06](16-sources-and-reading-guide.md#s06)

## Pattern catalog

| Pattern | Appropriate situation | Main risk | Necessary control |
|---|---|---|---|
| Single call | Bounded transformation | Output looks valid but is wrong | Domain validation |
| Fixed chain | Stable sequence of stages | Errors propagate downstream | Stage-specific acceptance checks |
| Routing | Distinct task categories | Misrouting to a weak or unauthorized path | Measured classifier and safe fallback |
| Parallel independent work | Separable research or checks | Shared-state interference and cost growth | Isolation and aggregate limits |
| Orchestrator-workers | Subtasks depend on the input | Poor decomposition or missing integration | Explicit contracts and integration owner |
| Evaluator-optimizer | A rubric can guide useful revision | Endless iteration or metric gaming | Attempt limit and protected evaluator |
| Human approval workflow | Consequential decision needs authority | Approval fatigue or stale approval | Clear evidence and revision binding |
| Event-driven factory | Work enters from external events | Duplicate events and feedback storms | Deduplication, admission control, causal links |

A richer pattern is not automatically more capable. A fixed workflow can be easier to test and operate than an agent when the business process is already known.

## Decompose by contracts

A useful subtask has:

- a bounded objective;
- authorized inputs and tools;
- a named output artifact;
- acceptance criteria;
- dependencies;
- a budget;
- a stop condition;
- an escalation route.

"Act as a senior architect and improve the system" is a role prompt, not a sufficient work contract.

Prefer decomposition along stable artifact boundaries: extract evidence, propose a patch, verify a property, assemble a report. Splitting one tightly coupled code change among many writers can create more integration work than it saves.

## Parallel review

The supplied video demonstrates security, UX, UI, and code-consistency review in parallel. [S48](16-sources-and-reading-guide.md#s48)

A careful implementation would:

1. Freeze the candidate revision being reviewed.
2. Give each reviewer the relevant scope and evidence.
3. Keep reviewers read-only where possible.
4. Require concrete findings rather than general opinions.
5. Deduplicate findings.
6. Resolve contradictory findings against the actual artifact.
7. Recheck affected properties after fixes.

Fresh contexts are useful separation, not proof of independent error distributions. A second model can share the same blind spot or the same misleading source.

## Concurrency has several scopes

| Shared resource | Failure example | Mitigation |
|---|---|---|
| Files | Two workers overwrite the same file | Separate workspaces or controlled ownership |
| Git branch | Review refers to an earlier head | Revision binding and integration checks |
| Database | One trial changes another trial's fixture | Isolated test databases or namespaces |
| Service ports | Workers connect to the wrong server | Allocated ports and explicit endpoint identity |
| Credentials | A child inherits excessive privileges | Scoped delegation and credential brokering |
| Budget | Each worker spends as if it owns the whole allowance | Shared accounting and reservation |
| Knowledge store | Conflicting lessons overwrite each other | Versioned proposals and conflict resolution |
| Release queue | Individually valid patches conflict after merge | Reverification on the integrated revision |

A Git worktree isolates working files, not necessarily every process, database, network resource, or secret.

## Work queues and delivery semantics

A work tracker such as Jira or GitHub Issues expresses business work. A reliable execution queue additionally needs machine-facing properties:

- stable work identifiers;
- delivery and acknowledgment semantics;
- ownership or leases;
- retry policy;
- cancellation;
- timeout handling;
- dependency state;
- deduplication;
- auditability.

Do not assume that changing a ticket label atomically assigns work to exactly one worker. If two workers can observe the same ready item, the admission mechanism must handle contention.

A lease should not let an old worker continue committing results after a new worker takes ownership. Systems that need this guarantee can use a fencing token or equivalent version check at the state-changing boundary.

## Idempotency and retries

An operation is idempotent when repeating it under its contract does not create additional unintended effects. This property belongs to the operation, not to the retry loop.

AWS's guidance explains why stable caller-provided request identifiers and semantically equivalent responses can make retries safer. [S23](16-sources-and-reading-guide.md#s23)

For a consequential operation, consider:

1. Generate a stable operation ID for the logical intent.
2. Bind it to the caller, target, and intended payload.
3. Persist that intent.
4. Invoke a service that supports a suitable idempotency contract, if available.
5. Record the observed result.
6. On uncertainty, inspect status before deciding to retry.

The same key with changed intent should not be silently accepted. A retry of "create one report" is not a request to create a different report.

## The crash gap

Suppose the service creates an external ticket, then the harness crashes before recording the response.

On restart, the local log may show an uncompleted operation. That does not mean the ticket was not created.

Possible responses:

- Query by the stable operation ID if the service supports it.
- Retry with the same idempotency key under a verified service contract.
- Search for a uniquely attributable result, if that method is reliable enough.
- Mark the outcome unresolved and require reconciliation.

What is not safe is automatically issuing a fresh creation request with a new identifier.

A checkpoint alone cannot give exactly-once behavior across arbitrary remote services. Avoid that claim unless the full transaction and delivery model has actually been established.

## Classify failure before retrying

| Failure | Typical response |
|---|---|
| Invalid input | Correct the input; do not blindly retry |
| Permission denied | Stop or obtain proper authorization; do not switch identities |
| Missing required source | Report the gap or use an explicitly approved alternate source |
| Transient read failure | Bounded retry may be appropriate |
| Rate limit | Respect backoff and shared capacity |
| Write timeout | Reconcile the possible effect before retrying |
| Verification failure | Produce bounded rework or escalate |
| Budget exhaustion | Stop new work and preserve state |
| Cancellation | Stop admission; handle in-flight outcomes explicitly |
| Provider unavailable | Use only a preapproved fallback policy or stop |

Retry budgets should include nested retries in SDKs, tools, workers, and orchestration. Three layers each retrying can multiply total attempts unexpectedly.

## Backpressure

When incoming work exceeds processing capacity, adding agents can worsen the problem by increasing API contention, shared-resource pressure, and verification backlog.

Apply controls at admission:

- maximum active tasks;
- per-user or per-tenant limits;
- priority and fairness rules;
- queue age and expiry;
- capacity reserved for recovery;
- a policy for dropping or deferring obsolete work.

A software factory should be able to say "queued," "rejected," or "deferred" honestly. Pretending to accept unlimited work creates hidden latency and cost.

## Cancellation is not rollback

Cancellation can mean:

- stop scheduling additional work;
- ask a worker to stop;
- terminate a local process;
- request cancellation from a remote service.

None of these necessarily reverses effects already committed. A refund, publication, or external notification may need a separate compensating action, and some effects cannot be fully undone.

Represent cancellation state separately from outcome state. "Cancelled after publication" is materially different from "cancelled before any write."

## Recovery versus replay

**Recovery** continues from known durable state after a failure. **Replay** re-executes some historical work. **Reproduction** attempts to reconstruct the conditions of an earlier result.

These are different operations. Replay of a read-only model task may simply incur extra cost. Replay of a side-effecting tool may duplicate a real-world action.

Before replaying:

- identify which events are observations and which are actions;
- use a safe simulated environment where possible;
- preserve original inputs and versions as permitted;
- disable production side effects unless explicitly authorized;
- record the replay as a new run rather than rewriting the original.

## Useful reliability experiments

Kill a worker before and after a tool call. Deliver the same event twice. Change an artifact after approval. Revoke a credential mid-run. Delay one reviewer. Run two tasks against the same target. Exhaust the shared budget. Make a service return a successful HTTP response with an application-level failure.

A design is not recoverable because it has a `resume` button. It is recoverable when these experiments produce controlled, explainable outcomes.
