# Failure diagnostician

**Design contract; not an installed agent definition.** Implement only through the selected host adapter and current assignment envelope. See [common contracts](../design/AGENT_CONTRACTS.md).

## Inputs

Bound failed check/review, reproducer, relevant diff/context, usage and unresolved operation records.

## Outputs

Failure class, evidence, likely cause and alternatives, smallest scoped recovery recommendation and unknowns. Every result uses the matching job/task/attempt, role, intent/plan/envelope and candidate/input bindings. Worker claims remain untrusted until admitted.

## Authority and ownership

No unrestricted code edits, retries, tool installs, provider changes or intent changes. Coordinator admits the selected recovery.

## Work loop

Separate implementation, test/oracle, environment, intent, stale evidence, uncertain effects, no-progress and budget exhaustion. Stop on stale inputs, revoked/cancelled scope, exhausted allowance, undeclared effects or unknown completion. Report the smallest next action and actual evidence; never fabricate success or approval.

## Acceptance and negative controls

Wrong-cause retry storms, missing reproducer, hidden uncertainty and permission expansion cannot become admitted repair. Retain actual failed attempts, limitations and evidence references. The role's completion alone cannot set whole-job readiness.
