# 17 - Evidence Map and Open Research Questions

[Back to the index](README.md)

## What this map does

This chapter makes important conclusions traceable and prevents recommendations from being mistaken for observed results. It complements the bibliography rather than replacing source reading.

**Supported** means the cited material supports the bounded statement. It does not mean independently reproduced here. **Synthesis** means a design recommendation developed in this corpus. **Not assessed** means the necessary local evidence does not exist yet.

## Consequential claims

| ID | Bounded claim | Evidence | Classification and limit |
|---|---|---|---|
| C01 | "AI factory" is used for infrastructure and for agentic software production | [S01](16-sources-and-reading-guide.md#s01), [S04](16-sources-and-reading-guide.md#s04), [S42](16-sources-and-reading-guide.md#s42), [S48](16-sources-and-reading-guide.md#s48) | Supported terminology observation; our three-part taxonomy is a synthesis |
| C02 | Workflows and agents can differ in who determines control flow | [S06](16-sources-and-reading-guide.md#s06) | Supported vendor taxonomy, not the only usage |
| C03 | Agent evaluation measures a model together with its harness and environment | [S10](16-sources-and-reading-guide.md#s10) | Supported engineering framing |
| C04 | Compaction alone did not solve the reported long-running coding problem | [S07](16-sources-and-reading-guide.md#s07) | Vendor observation in a specific setting |
| C05 | Initializers, explicit progress, and incremental testing are useful candidate patterns | [S07](16-sources-and-reading-guide.md#s07) | Reported pattern; local effectiveness not assessed |
| C06 | The same context capacity can be used more or less effectively depending on selection and placement | [S08](16-sources-and-reading-guide.md#s08), [S28](16-sources-and-reading-guide.md#s28) | Guidance plus bounded historical research |
| C07 | Agent-facing interface design can materially affect task performance | [S09](16-sources-and-reading-guide.md#s09), [S29](16-sources-and-reading-guide.md#s29) | Supported at guidance/abstract level; no local effect size |
| C08 | A skill can package instructions and resources without being a separate agent | [S17](16-sources-and-reading-guide.md#s17) | Supported format definition |
| C09 | MCP interoperability does not by itself enforce all consent and trust requirements | [S15](16-sources-and-reading-guide.md#s15) | Supported specification overview; version-scoped |
| C10 | A2A supports interaction between independent agent systems | [S16](16-sources-and-reading-guide.md#s16) | Supported specification overview; no implementation conformance tested |
| C11 | Checkpoint behavior and replay semantics must be understood before wrapping side effects | [S14](16-sources-and-reading-guide.md#s14), [S41](16-sources-and-reading-guide.md#s41) | Supported framework behavior plus reliability synthesis |
| C12 | Stable operation identity and a suitable service contract can make retries safer | [S23](16-sources-and-reading-guide.md#s23) | Supported engineering guidance; not universal exactly-once execution |
| C13 | Model graders can exhibit systematic biases | [S30](16-sources-and-reading-guide.md#s30), [S10](16-sources-and-reading-guide.md#s10) | Supported research/guidance; our domain judges remain uncalibrated |
| C14 | RAG and fine-tuning do not fully remove prompt-injection risk | [S22](16-sources-and-reading-guide.md#s22) | Supported defensive guidance |
| C15 | Persistent session state can be decoupled from harness and sandbox lifetime | [S11](16-sources-and-reading-guide.md#s11) | Reported architecture; our proposed deployment is unimplemented |
| C16 | Task dependencies are not an ordering mechanism | [S44](16-sources-and-reading-guide.md#s44) | Supported documented tool behavior |
| C17 | Terminal panes provide visibility, not automatically a durable agent execution system | [S45](16-sources-and-reading-guide.md#s45), [S47](16-sources-and-reading-guide.md#s47) | Tool capabilities plus architectural synthesis |
| C18 | StrongDM reports behavioral scenarios and service twins as part of its factory | [S04](16-sources-and-reading-guide.md#s04) | Primary self-report, not independent performance validation |
| C19 | The Risco video describes both software and content proof-of-concept workflows | [S48](16-sources-and-reading-guide.md#s48) | Transcript-based observation; no implementation reproduction |
| C20 | The video's content example retains manual review/upload | [S48](16-sources-and-reading-guide.md#s48) | Direct transcript support around 15:23 |
| C21 | Current RSC README behavior cannot be assumed identical to the video's implementation | [S49](16-sources-and-reading-guide.md#s49) | Source-version boundary; code not audited |
| C22 | Broad productivity claims require local measurement | [S32](16-sources-and-reading-guide.md#s32), [S33](16-sources-and-reading-guide.md#s33) | Supported methodological lesson; no universal speedup or slowdown |
| C23 | Production operation needs ownership beyond the model | [S02](16-sources-and-reading-guide.md#s02), [S03](16-sources-and-reading-guide.md#s03) | Supported guidance; our role map is a synthesis |
| C24 | Infrastructure availability and user-relevant correctness are different indicators | [S25](16-sources-and-reading-guide.md#s25) | Supported SRE framing |
| C25 | Useful cost analysis includes the whole AI lifecycle and the unit of business outcome | [S40](16-sources-and-reading-guide.md#s40) | Supported practitioner framing; example costs here are synthetic |
| C26 | Model and dataset documentation should preserve intended use and limitations | [S38](16-sources-and-reading-guide.md#s38), [S39](16-sources-and-reading-guide.md#s39) | Supported proposals; documentation is not certification |
| C27 | A no-human-review policy is not established as universally appropriate | [S04](16-sources-and-reading-guide.md#s04), [S42](16-sources-and-reading-guide.md#s42), [S48](16-sources-and-reading-guide.md#s48) | Sources describe different choices; our recommendation is risk-based synthesis |
| C28 | More agents, more tokens, or more generated code do not alone prove more value | [S10](16-sources-and-reading-guide.md#s10), [S33](16-sources-and-reading-guide.md#s33), [S40](16-sources-and-reading-guide.md#s40) | Measurement synthesis |

## Claims this corpus does not make

- That we have implemented an AI factory.
- That any named model or framework is best for our future use case.
- That the supplied sources prove safe unrestricted autonomy.
- That a particular token budget or reviewer count is optimal.
- That a system is secure because its design includes a sandbox or approval prompt.
- That the learning exercises have been executed.
- That a synthetic scenario demonstrates live provider acceptance.
- That reading the corpus makes someone an expert in every AI application domain.
- That private wiki material has been ingested or that this publication provides live access to any private knowledge source.

## Priority research questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Which first task class is worth automating? | Determines almost every later decision | Real workflow, bounded outcome, owner, baseline |
| What does acceptance mean? | Without an oracle, generation cannot be trusted | Domain-reviewed criteria and representative scenarios |
| Which data/provider/storage combination is approved? | Determines permitted execution | Explicit authorization and actual service permissions |
| Is a model call, workflow, or agent required? | Avoids unnecessary complexity | Baseline comparison on the task set |
| Does persistent memory improve this task? | Memory adds both value and risk | Retrieval/ablation results and stale-memory tests |
| Do specialized reviewers help? | They add latency, cost, and false positives | Defect detection and disagreement measurements |
| Which operations are safe to retry? | Prevents duplicate external effects | Tool/service contracts and failure-injection results |
| Which actions can be preauthorized? | Defines autonomy safely | Risk classification, controls, recovery, owner decision |
| How should evidence be retained? | Supports auditability without overcollection | Data classification, purpose, retention, access design |
| What is the actual cost per accepted result? | Prevents activity from masquerading as value | All-attempt cost and active human effort |
| How does the system fail under concurrency? | Parallelism exposes hidden shared state | Contention, lease, integration, and budget tests |
| Can maintainers still understand and repair the product? | Protects long-term ownership | Handoff and incident exercises with independent maintainers |

These are not unanswered ambiguities in the research assignment. They are decisions intentionally deferred until the future solution has a concrete use case.

## Proposed experiment sequence

### Experiment A - Simple baseline versus bounded agent

Use the same tasks and acceptance criteria. Compare manual/deterministic work with a bounded single agent. Record failures, active human time, cost, and elapsed time.

**Decision supported:** whether agentic execution adds value at all.

### Experiment B - Context and memory ablation

Compare a short project map, targeted retrieval, and a broader context strategy. Include stale and contradictory documents.

**Decision supported:** which context design improves the actual workload without increasing unauthorized exposure.

### Experiment C - Reviewer contribution

Compare the builder alone, deterministic checks, one independent reviewer, and a richer reviewer set.

**Decision supported:** whether each added reviewer improves accepted outcomes enough to justify cost and coordination.

### Experiment D - Recovery and side effects

Inject crashes and lost responses around a simulated external operation.

**Decision supported:** whether the design can continue without duplicate effects or false completion.

### Experiment E - Human approval calibration

Use a reviewed set of low-, high-, and uncertain-risk changes. Compare model recommendations against mandatory rules and qualified human decisions.

**Decision supported:** where a model can assist routing, not whether it should replace all authority.

### Experiment F - Handoff and maintainability

Give the produced artifact and evidence to a person who did not participate in the run. Ask them to explain, modify, and recover the system.

**Decision supported:** whether the factory preserves team ownership rather than merely producing output quickly.

## How to change our mind

For each recommendation, write down a disconfirming observation.

Examples:

- If memory adds stale facts more often than useful context, narrow or remove it.
- If extra reviewers mostly duplicate findings and create false alarms, simplify.
- If a fixed workflow matches an agent's quality with less cost and risk, use the workflow.
- If automatic promotion produces unacceptable escape rates, restore a stronger gate.
- If a task cannot be evaluated reliably, reduce scope or keep accountable human judgment.

A knowledge corpus should help us revise decisions when evidence changes, not merely defend the first architecture we found attractive.
