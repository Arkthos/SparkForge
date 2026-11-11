# 03 - Agent Harness Engineering

[Back to the index](README.md)

## What we are engineering

The harness is the application machinery that makes a model useful as an agent. It decides what the model can see, how proposed actions are interpreted, which actions may execute, how state is retained, and what happens when the run finishes or fails.

Anthropic's evaluation guide defines an agent harness as the system around the model that processes inputs, orchestrates tools, and returns results. Its long-running-agent report shows why a model plus a loop and compaction can still fail to make coherent progress. [S10](16-sources-and-reading-guide.md#s10) [S07](16-sources-and-reading-guide.md#s07)

This chapter proposes a provider-neutral design vocabulary. Not every system needs a large framework, separate services, or all mechanisms on day one.

## Minimum responsibilities

| Responsibility | Question the harness must answer |
|---|---|
| Task admission | Is the request valid, in scope, and authorized? |
| Context assembly | Which instructions, state, and evidence belong in the next request? |
| Model invocation | Which approved model/configuration should be used? |
| Action interpretation | Is the model requesting a tool, a clarification, or completion? |
| Policy enforcement | Is this action permitted for this identity, target, and state? |
| Tool execution | How is the operation executed, timed out, and observed? |
| State management | What is durable, and what can be reconstructed? |
| Resource control | How are time, cost, turns, and delegated work bounded? |
| Verification | What evidence establishes the requested outcome? |
| Recovery | What happens after a crash, disconnect, or uncertain tool result? |
| Completion | How is an honest final status produced? |

The model may help decide a next step. It should not be the only mechanism enforcing these responsibilities.

## A lifecycle with explicit states

An illustrative task lifecycle:

```text
RECEIVED -> QUALIFIED -> READY -> RUNNING -> VERIFYING
                                  |             |
                                  v             v
                              WAITING       CANDIDATE_READY
                                  |             |
                                  +-> RUNNING   v
                                           ACCEPTED -> RELEASED
```

Additional terminal or exceptional states include `REJECTED`, `FAILED`, `CANCELLED`, `BUDGET_EXHAUSTED`, and `NEEDS_RECONCILIATION`.

Important distinctions:

- `WAITING` can mean awaiting information or approval, not a failed task.
- `CANDIDATE_READY` means an artifact exists, not that it is accepted.
- `ACCEPTED` means specified verification and review requirements were satisfied.
- `RELEASED` means an authorized promotion actually happened.
- `NEEDS_RECONCILIATION` means a side effect may have occurred but its outcome is uncertain.

A **task** can span multiple **runs**. A run can contain multiple model turns and tool attempts. Keep these identities separate so a retry is not confused with new work.

## A conceptual execution loop

The following is design pseudocode, not a ready-to-run implementation:

```text
admit task under a specific identity and approved scope
load the exact task, policy, environment, and input revisions
restore durable state and reconcile unresolved operations

while task is runnable:
    check cancellation, deadline, and remaining shared budget
    assemble bounded context from authorized state and evidence
    request the next model response using an approved configuration
    record usage and the observable response
    validate the response structure

    if the response proposes an action:
        validate target, parameters, permissions, and preconditions
        obtain a revision-bound approval if required
        persist an operation intent and stable operation identifier
        execute through the controlled tool boundary
        persist the result or mark the outcome uncertain
        update task state from observed facts

    if the response proposes completion:
        verify the required artifacts and acceptance criteria
        finish only if the task contract is satisfied
        otherwise return actionable failures or escalate within limits

write a final status that distinguishes outcome, evidence, and limitations
```

A durable operation intent improves recovery, but cannot by itself make a remote service transactional. The external service's idempotency and lookup capabilities still determine what can be safely retried.

## State: what belongs where

| State type | Examples | Appropriate properties |
|---|---|---|
| Task contract | Goal, scope, acceptance criteria, risk class | Versioned and reviewable |
| Run state | Current phase, pending actions, attempts, budget | Durable enough for required recovery |
| Event history | Tool request/result, approval, cancellation | Ordered, attributable, retention-controlled |
| Working context | Selected messages and evidence for the next call | Reconstructable and bounded |
| Artifacts | Patch, report, test output, generated file | Revisioned with provenance |
| Knowledge | Reviewed reusable lessons | Owned, scoped, correctable |
| Secrets | Service credentials | Outside model-visible and untrusted execution state |

**A summary is a view, not the record.** If the summary says "deployment failed" but the service accepted the deployment before a connection broke, the summary must not trigger a duplicate deployment.

Anthropic's Managed Agents account describes separating session history, harness execution, and sandbox resources. The general lesson is useful beyond that product: state and execution lifetimes do not have to be identical. [S11](16-sources-and-reading-guide.md#s11)

## Checkpoint design

A useful checkpoint identifies:

- task and run identifiers;
- the exact task contract and policy revisions;
- code or artifact revision;
- the last durably observed events;
- completed and unresolved operations;
- budgets consumed and reserved;
- approval decisions and their validity constraints;
- environment recipe and relevant dependency versions;
- where permitted evidence can be retrieved.

A checkpoint should not be a memory dump containing every secret or private source. Minimize it while retaining what recovery needs.

Checkpoint frequency trades durability against overhead. Checkpoint around meaningful boundaries: before a consequential operation, after its observed result, after verified progress, and before handing work to another execution context.

For framework-specific behavior, inspect the actual checkpoint semantics. LangGraph distinguishes thread state, checkpoints, and stores; its documentation notes that a resumed interrupted node can restart from its beginning. Code before the interruption must therefore be designed with re-execution in mind. [S14](16-sources-and-reading-guide.md#s14) [S41](16-sources-and-reading-guide.md#s41)

## Long-running work

Anthropic's reported pattern separates an initializer from subsequent incremental coding sessions. The initializer establishes an environment, a feature list, and progress artifacts; later sessions inspect that state, make bounded progress, and verify behavior. [S07](16-sources-and-reading-guide.md#s07)

Transferable ideas:

1. Make unfinished work explicit rather than relying on conversational memory.
2. Check the starting environment before adding new work.
3. Keep changes small enough to verify and recover.
4. Record what was actually checked.
5. Leave a useful next-action pointer.

Important adaptations:

- An initializer must not invent consequential scope and treat it as approved.
- A feature list is not an immutable oracle if the requirements themselves are wrong; changes need controlled review.
- The source's preference for JSON over Markdown was an experimental observation, not a universal data-format law.
- A clean Git commit is useful but does not prove that the correct behavior was tested.
- Long-running execution still needs limits, cancellation, and a human escalation path.

## Completion is a contract

Weak completion:

> The agent produced a confident final message.

Stronger completion:

> The requested artifact exists at the recorded revision; required checks have results bound to it; unresolved criteria are explicitly listed; necessary acceptance or release authority has been exercised.

A completion contract should say which checks are mandatory, what may be skipped, who may approve an exception, and how partial outcomes are represented.

Do not treat "no error returned" as success when the output is missing. Do not treat skipped tests as passed. Do not reuse evidence from an earlier artifact after making an unverified edit.

## Permissions and the execution boundary

Place consequential enforcement in code or infrastructure that the worker cannot casually rewrite:

- tool allowlists and target scopes;
- data-access enforcement;
- credential brokering;
- filesystem and network restrictions;
- resource limits;
- approval validity checks;
- protected verification and release controls.

Prompt instructions remain useful for behavior, but they are not a security boundary. A sandbox also has a specific boundary: a process or container with broad mounts, credentials, or unrestricted egress may offer little protection against the actions that matter.

## Observability without indiscriminate recording

Useful records include observable model outputs, selected tool requests, tool results, timestamps, state transitions, policy outcomes, token usage, and artifact references.

Do not make observability depend on access to hidden model reasoning. A concise action rationale can be helpful, but it is not guaranteed to faithfully explain the model's internal process. Review the external behavior and evidence.

Do not log secrets or entire private documents by default. Some evidence may need a restricted store, a redacted view, or only an authorized reference. The trace reader's access must not exceed the source reader's access accidentally.

## What the harness should not do

- Retry paid or consequential operations without a bounded, authorized policy.
- Select an unrelated provider when the configured one fails.
- Treat retrieved instructions as higher authority than the task and policy.
- Allow the worker to edit protected acceptance criteria to make itself pass.
- Report a synthetic test as production acceptance.
- Let delegated workers acquire broader permissions than the parent.
- Keep running indefinitely because the model requests more time.
- Declare a task complete when a critical operation remains uncertain.

## Testing the harness itself

| Test | Expected property |
|---|---|
| Tool-call arguments violate the schema | No execution; explicit validation result |
| Tool target belongs to another tenant | Access denied before data is returned |
| Model repeatedly asks for the same failing action | Bounded attempts and a useful stop reason |
| Process crashes after recording intent | Recovery checks whether execution occurred |
| Remote write succeeds but response is lost | Reconciliation avoids blind duplication |
| Approval arrives after artifact changes | Approval is rejected as stale |
| Cancellation arrives during tool execution | No new work starts; in-flight outcome is reconciled |
| Context compaction loses a summary detail | Durable evidence remains available |
| Child workers exhaust shared budget | Aggregate limits stop additional work |
| Model claims success without an artifact | Completion is rejected |
| Evaluation result belongs to an older revision | It cannot authorize the new artifact |
| A tool returns an instruction to expand privileges | Treated as untrusted content, not authority |

These are behavior tests of our proposed design, not results from an implemented system.

## Simplicity and change

Start with a small explicit loop if that satisfies the task. Add graph execution, distributed workers, elaborate memory, or multi-agent coordination only when a measured requirement justifies them.

Some harness logic compensates for a particular model weakness. As models change, that logic can become unnecessary or counterproductive. Anthropic's Managed Agents report describes such an example involving context-reset behavior. Keep the ability to evaluate the model-and-harness pair, and remove complexity when evidence supports doing so. [S11](16-sources-and-reading-guide.md#s11)
