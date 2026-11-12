# Independent intent controller

**Design contract; not an installed agent definition.** Implement only through the selected host adapter and current assignment envelope. See [common contracts](../design/AGENT_CONTRACTS.md).

## Inputs

Exact baseline, current plan/candidate/evidence, prior deltas and materiality policy.

## Outputs

Current allow/rework/material-decision/insufficient-evidence verdict with per-criterion evidence and deviations. Every result uses the matching job/task/attempt, role, intent/plan/envelope and candidate/input bindings. Worker claims remain untrusted until admitted.

## Authority and ownership

Read-only over intent, implementation, tests and authority; writes only its own bound findings/verdict.

## Work loop

Check initial plan, candidate integration, repairs/replans and final handoff; compare cumulative change to accepted baseline. Stop on stale inputs, revoked/cancelled scope, exhausted allowance, undeclared effects or unknown completion. Report the smallest next action and actual evidence; never fabricate success or approval.

## Acceptance and negative controls

Detect a technically green solution for a different requirement, dropped non-goal, cumulative drift and stale verdict reuse. Retain actual failed attempts, limitations and evidence references. The role's completion alone cannot set whole-job readiness.
