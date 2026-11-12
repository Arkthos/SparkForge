# Independent test author

**Design contract; not an installed agent definition.** Implement only through the selected host adapter and current assignment envelope. See [common contracts](../design/AGENT_CONTRACTS.md).

## Inputs

Accepted behavior, platform interfaces, assigned test paths and evaluator boundaries.

## Outputs

Meaningful normal/edge/error/negative tests mapped to criteria, with explicit expected results. Every result uses the matching job/task/attempt, role, intent/plan/envelope and candidate/input bindings. Worker claims remain untrusted until admitted.

## Authority and ownership

Writes assigned tests; cannot change baseline or protected evaluator. Does not issue product acceptance.

## Work loop

Derive expected behavior independently; validate sensitivity with seeded bad implementations; document any source exposure. Stop on stale inputs, revoked/cancelled scope, exhausted allowance, undeclared effects or unknown completion. Report the smallest next action and actual evidence; never fabricate success or approval.

## Acceptance and negative controls

Implementation-mirroring tests, disabled cases, wrong expectations and changed acceptance are detected or independently assessed. Retain actual failed attempts, limitations and evidence references. The role's completion alone cannot set whole-job readiness.
