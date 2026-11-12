# Deterministic test runner

**Design contract; not an installed agent definition.** Implement only through the selected host adapter and current assignment envelope. See [common contracts](../design/AGENT_CONTRACTS.md).

## Inputs

Current candidate, declared commands, required inventory and remaining allowance.

## Outputs

Actual completion/exit/output/limit receipts, exact bindings, case counts when supported and structured failure evidence. Every result uses the matching job/task/attempt, role, intent/plan/envelope and candidate/input bindings. Worker claims remain untrusted until admitted.

## Authority and ownership

Executes admitted checks in selected context; cannot change tests or reinterpret failures as success. No model is required for execution.

## Work loop

Reserve before dispatch, run boundedly, preserve failures and uncertainty, identify incomplete reporters and refresh evidence after change. Stop on stale inputs, revoked/cancelled scope, exhausted allowance, undeclared effects or unknown completion. Report the smallest next action and actual evidence; never fabricate success or approval.

## Acceptance and negative controls

Zero exit with missing required behavior, truncation, timeout, stale candidate and one test substituting for a suite cannot pass. Retain actual failed attempts, limitations and evidence references. The role's completion alone cannot set whole-job readiness.
