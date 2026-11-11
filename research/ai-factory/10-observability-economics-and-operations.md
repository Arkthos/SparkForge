# 10 - Observability, Economics, and Operations

[Back to the index](README.md)

## Observability answers operational questions

The purpose is not to collect every token. It is to answer:

- What is running?
- What was the system trying to do?
- Which inputs, versions, identities, and permissions were involved?
- Where did time and money go?
- What actually changed?
- Why was the result accepted, rejected, or escalated?
- Can we stop and recover safely?

Allbright treats observability as an area to develop as the practice matures. Our recommendation is to establish a minimal structured record from the first experiment, because otherwise the experiment cannot be evaluated well. [S42](16-sources-and-reading-guide.md#s42)

## Three observation layers

| Layer | Examples | Principal consumer |
|---|---|---|
| Infrastructure | CPU, memory, queue depth, service availability | Platform and operations |
| Execution | Model calls, tools, retries, approvals, state transitions | Harness maintainers and investigators |
| Outcome | Accepted work, defect escape, user value, human effort | Product and accountable owners |

A system can have excellent uptime and consistently produce the wrong result. Infrastructure health and semantic quality must both be measured.

## A minimal trace vocabulary

Useful fields include:

- `task_id`, `run_id`, `attempt_id`, and parent identifiers;
- configuration and artifact revisions;
- operation name and target classification;
- start/end times and elapsed duration;
- outcome status and structured error category;
- policy and approval decision references;
- token and tool usage;
- budget changes;
- evidence references;
- cancellation and reconciliation state.

Keep high-cardinality identifiers out of metrics where they would make the system expensive or unusable; use traces or logs for individual runs.

Do not assume all vendors use identical field names. OpenTelemetry's GenAI conventions have moved to a dedicated repository, and implementation details should be checked and pinned before integration. [S24](16-sources-and-reading-guide.md#s24)

## Privacy-aware traces

Metadata, redacted content, and full content should have different handling.

Capture only what the evaluation or operating purpose requires. Restrict access to sensitive evidence. Avoid treating a telemetry vendor as an automatically authorized recipient of model inputs or customer records.

An investigator may need access to a private trace without that trace becoming available to every developer or agent. Record the path to evidence and the access decision, not just the evidence's existence.

## SLI, SLO, and SLA

Google's SRE guidance distinguishes:

- **SLI:** a measured indicator of service behavior.
- **SLO:** an objective for that indicator.
- **SLA:** an agreement with consequences associated with service commitments.

The guide also warns that aggregates can hide meaningful behavior. [S25](16-sources-and-reading-guide.md#s25)

For a factory, candidate indicators include:

| Indicator | Define carefully |
|---|---|
| Accepted-task rate | Eligible tasks, task mix, and what acceptance means |
| Time to accepted outcome | Include queue, execution, review, and rework |
| Human intervention | Count required decisions and active minutes, not just messages |
| Duplicate-action rate | Define the external effect and observation window |
| Recovery success | Which fault classes were exercised? |
| Evidence completeness | Which fields and checks are mandatory? |
| Escaped defect rate | How defects are linked to delivered work |
| Cost per accepted outcome | Include unsuccessful attempts and shared overhead |

Do not set a universal 99.9% target because it sounds professional. Select objectives based on users, consequences, baseline behavior, and feasible controls.

## Cost accounting

Include:

- input, output, cached, and other billable model usage under the actual provider contract;
- tool/API charges;
- evaluation and reviewer calls;
- compute and storage;
- indexing and retrieval;
- failed attempts and retries;
- human review, correction, and incident work;
- platform maintenance;
- idle reserved capacity where applicable.

A free-looking framework can still have significant operating cost. FinOps guidance emphasizes placing tools in the lifecycle and measuring the economics of the use case rather than only individual components. [S40](16-sources-and-reading-guide.md#s40)

## An illustrative comparison

The following values are invented for learning. They are not vendor prices, measured results, or a proposed budget.

Assume the same 100-task set and acceptance criteria, with human effort valued at an illustrative $60 per hour:

| Measure | Design A | Design B |
|---|---:|---:|
| Accepted outcomes | 80 | 95 |
| Model and tool cost across all attempts | $20 | $45 |
| Active human review and correction | 120 minutes | 30 minutes |
| Illustrative human effort cost | $120 | $30 |
| Combined cost | $140 | $75 |
| Combined cost per accepted outcome | $1.75 | approximately $0.79 |

Design B spends more on inference but has a lower combined cost in this hypothetical example. The example does not prove that more inference reduces human effort. That relationship must be measured.

Also distinguish **capacity value** from **cash savings**. Saving human minutes does not automatically reduce payroll or produce revenue. The freed capacity must be usable for valuable work.

If there are no accepted outcomes, cost per accepted outcome is undefined, not zero.

## Productivity measurement

Measure elapsed time and active human time separately. An agent may run for an hour while the operator does other work. Conversely, a fast model call may create substantial review effort.

Control for:

- task difficulty and novelty;
- familiarity with the codebase;
- quality requirements;
- task selection;
- developer experience;
- multiple concurrent agents;
- excluded or abandoned tasks;
- changes in scope.

METR's early-2025 study and February-2026 methodology update illustrate why self-reported productivity and simple before/after comparisons can mislead. The later update explicitly discusses selection and time-measurement difficulties. [S32](16-sources-and-reading-guide.md#s32) [S33](16-sources-and-reading-guide.md#s33)

Use local evidence rather than importing a headline as a universal productivity multiplier.

## Budget enforcement

A useful policy can include limits per request, run, task, user, tenant, and overall system.

Aggregate delegated work. An orchestrator should not give each child the entire remaining budget as if the children were independent accounts.

Distinguish:

- estimated cost before starting an operation;
- reserved allowance for in-flight work;
- observed usage;
- final reconciled billing.

Delayed billing and concurrent requests can cause a simple "check balance after completion" rule to overshoot. Reserve capacity where possible and define bounded overshoot behavior where exact real-time enforcement is unavailable.

Budget exhaustion should preserve state and stop new work. It should not trigger silent fallback to another account or provider.

## Operational dashboards

A small dashboard should show:

- active, waiting, failed, and unreconciled tasks;
- queue age and admission limits;
- acceptance and regression trends by task class;
- latency distribution;
- cost and human effort by outcome;
- recent model/harness/policy changes;
- safety and permission failures.

Avoid a dashboard dominated by tokens, number of agents, or generated lines of code. Those are activity measures, not success.

## Alert design

Alert on actionable conditions:

- unresolved consequential operations;
- unexpected writes or denied cross-scope access;
- sustained acceptance degradation;
- runaway retries;
- budget anomalies;
- stale approvals;
- inability to restore state;
- evidence-store failures.

Every alert needs an owner and a response. Too many low-quality alerts train people to ignore the system.

## Deployment and rollback

Promote a versioned bundle, not just a prompt string. Start with a limited exposure where appropriate, compare against the baseline, and keep a way to stop new work.

Rollback has limits:

- restoring old code does not unsend an email;
- changing a prompt does not undo a database write;
- reverting a model version does not erase leaked data;
- reverting a schema migration may be unsafe.

Plan containment, forward repair, and compensation as well as rollback.

## Incident handling

1. Contain new harmful or expensive work.
2. Preserve necessary evidence with access controls.
3. Identify affected tasks, artifacts, and external operations.
4. Reconcile uncertain outcomes.
5. Recover or compensate using authorized procedures.
6. Explain user impact and remaining uncertainty.
7. Convert the failure into a regression case or control improvement.
8. Re-evaluate the change before promotion.

An incident-triggered agent can prepare a diagnosis or patch. It should not automatically reinterpret the alert as authority to make unrestricted production changes.

## Continuous improvement

Group failures by cause: specification, retrieval, model judgment, tool interface, environment, policy, verification, or coordination.

Improve the responsible layer rather than adding prompt text indiscriminately. Then check whether the improvement generalizes and whether it introduced cost or safety regressions.

Operational maturity means the team can explain both successes and failures, not merely keep the agents running.
