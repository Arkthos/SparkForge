# Template - Harness and Task Contract

[Corpus index](../README.md) | [Harness engineering](../03-harness-engineering.md)

**Status:** UNFILLED TEMPLATE. No execution is authorized by this example.

## Task identity and requested outcome

| Field | Value |
|---|---|
| Task ID / contract revision | Not set |
| Requester / acceptance owner | Not set |
| Goal | Not set |
| In-scope behavior | Not set |
| Out-of-scope behavior | Not set |
| Required artifacts | Not set |
| Completion criteria | Not agreed |

## Inputs and provenance

For each input, identify source, owner, revision, effective date, permitted purpose, and access scope. State missing evidence explicitly.

## Execution configuration

| Component | Approved version/configuration |
|---|---|
| Model/provider | Not selected |
| Harness | Not selected |
| Prompts/skills | Not selected |
| Environment/dependencies | Not selected |
| Policy | Not selected |
| Evaluation suite | Not selected |

## Tool contract

| Operation | Identity and target | Side effect | Approval | Retry/reconciliation |
|---|---|---|---|---|
| Not specified | Not authorized | Unknown | Not defined | Not defined |

Define invalid-input handling, preconditions, result semantics, limits, and postcondition checks.

## State and recovery

- Authoritative task/run store: Not set.
- Checkpoint boundaries: Not set.
- Pending-operation representation: Not set.
- Operation identity and deduplication: Not set.
- Crash recovery: Not designed.
- Cancellation and in-flight work: Not designed.
- Restore procedure and evidence retention: Not designed.

## Resource limits

| Limit | Value | Enforcement point |
|---|---|---|
| Time/deadline | Not agreed | Not set |
| Model/tool usage | Not agreed | Not set |
| Shared monetary budget | Not agreed | Not set |
| Concurrency/delegation | Not agreed | Not set |
| Retry/rework attempts | Not agreed | Not set |

Include nested workers and in-flight reservations. Missing limits are not unlimited permission.

## Acceptance and authority

Specify who controls the evaluator, who may edit acceptance criteria, and who may accept or release the artifact.

**Required evidence:** Not defined.<br>
**Approval binding and expiration:** Not defined.<br>
**Escalation conditions:** Not defined.<br>
**Uncertain outcome handling:** Not defined.

## Boundary tests

- [ ] Unauthorized target is rejected.
- [ ] Stale approval is rejected.
- [ ] Invalid tool input does not execute.
- [ ] Unknown write outcome is reconciled.
- [ ] Budget exhaustion stops new work.
- [ ] Cancellation does not falsely imply rollback.
- [ ] Completion requires actual artifact evidence.

**Execution readiness:** Not assessed.
