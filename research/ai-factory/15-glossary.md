# 15 - Glossary and Important Distinctions

[Back to the index](README.md)

These are concise working definitions for this corpus. Some industry terms have multiple usages; protocol-specific meanings should be checked against the selected version.

## System architecture

| Term | Working meaning |
|---|---|
| AI factory | Managed, repeatable production of useful AI-enabled outcomes; specify which meaning is intended |
| Infrastructure AI factory | Coordinated infrastructure for training and serving AI workloads |
| Enterprise AI capability | Organizational system for selecting, delivering, governing, and operating AI use cases |
| Software factory | Delivery system that transforms requirements into accepted software changes |
| Content factory | Repeatable production of media or documents with appropriate editorial and publication controls |
| Model | Learned computational component that produces outputs from inputs |
| AI application | Software that combines a model with interfaces, data, logic, and operations |
| Workflow | Designed control flow across steps |
| Agent | Goal-directed system where a model selects actions using observations |
| Agent harness | Machinery for model context, actions, state, controls, and lifecycle |
| Evaluation harness | Infrastructure for running tasks, grading trials, and aggregating results |
| Developer harness | Repeatable local environment and feedback mechanisms |
| Runtime | Execution machinery: processes, workers, scheduling, and lifecycle |
| Framework | Reusable implementation abstractions |
| SDK | Libraries and interfaces for building against a platform |
| Orchestrator | Coordinator of steps or delegated workers |
| Control plane | Configuration, policy, scheduling, and authority decisions |
| Execution plane | Where work and tool actions run |
| Data plane | Workload information and its movement |
| Evidence plane | Records needed to substantiate and explain outcomes |
| Paved path | Supported, documented route for common work |
| Harness | Also a company/product name; not the generic harness concept |

## Context and knowledge

| Term | Working meaning |
|---|---|
| Prompt engineering | Designing instructions and examples for model behavior |
| Context engineering | Selecting and maintaining all information supplied for inference |
| Context window | The bounded input/output context a model can process under its interface |
| Context pollution | Irrelevant, misleading, or conflicting information that interferes with useful behavior |
| Compaction | Reducing conversation/state detail into a smaller working representation |
| Working memory | Information retained for the active task |
| Episodic memory | History of particular events or runs |
| Semantic memory | Retained facts or concepts |
| Procedural memory | Guidance about how to perform work |
| Persistent memory | Information retained beyond one execution context |
| Memory poisoning | Untrusted or incorrect information promoted into later trusted context |
| RAG | Generation augmented with retrieved external information |
| Embedding | Numerical representation used for tasks such as similarity search |
| Vector index | Data structure supporting retrieval over vectors |
| Hybrid retrieval | Combination of retrieval methods such as keyword and semantic search |
| Reranking | Reordering retrieved candidates using a relevance model or rule |
| Chunk | A unit of content prepared for indexing or retrieval |
| Provenance | Where information came from and how it was transformed |
| Groundedness | Whether an output's claims are supported by the relevant evidence |
| Citation fidelity | Whether a citation accurately supports its attached claim |
| Knowledge graph | Representation of entities and relationships |
| Source of truth | An explicitly designated authoritative record for a particular fact or state |
| Brain | Informal name for persistent project knowledge; not a precise storage architecture |

## Tools and delegation

| Term | Working meaning |
|---|---|
| Tool | Operation exposed through an interface |
| Tool call | Structured request to perform an operation |
| Tool schema | Description of accepted input/output structure |
| ACI | Agent-computer interface designed for how agents interact with an environment |
| Persona | Role or behavioral specialization |
| Skill | Reusable procedural guidance with optional resources or scripts |
| Subagent | Delegated execution with a separate context or lifecycle |
| Handoff | Transfer of task responsibility or control |
| MCP | Model Context Protocol for connecting AI applications with context and capabilities |
| MCP resource | Contextual information exposed by an MCP server |
| MCP prompt | Templated interaction content exposed through MCP |
| A2A | Agent2Agent protocol for interaction between independent agent systems |
| Agent card | A2A capability and service metadata |
| Progressive disclosure | Load concise discovery information before full details |
| Instruction file | Project-specific guidance such as AGENTS.md or a product-specific equivalent |
| Hook | Code invoked at a lifecycle event; enforcement depends on actual coverage and trust boundary |
| Task runner | Program for defining and invoking repeatable commands |

## State and reliability

| Term | Working meaning |
|---|---|
| Task | Requested unit of work with a contract |
| Run | One execution instance attempting work |
| Attempt | One try at an operation or task |
| Event | Recorded occurrence or state transition |
| Artifact | Produced or referenced work product |
| Checkpoint | Durable representation sufficient for a defined recovery boundary |
| Lease | Time-bounded ownership of work |
| Fencing token | Version-like authority used to reject an obsolete worker's writes |
| Idempotency | Repetition does not add unintended effects under the operation's contract |
| Deduplication | Detecting and handling repeated work or messages |
| Reconciliation | Determining the actual state after uncertainty |
| Retry | Reattempting an operation under a bounded policy |
| Backoff | Increasing or otherwise controlling delay between retries |
| Jitter | Variation in retry timing to reduce synchronized load |
| Backpressure | Limiting incoming work to protect capacity |
| Check-and-act race | State changes between validation and execution |
| Recovery | Continuing safely after a failure |
| Replay | Re-executing historical work or events |
| Compensation | An additional action that mitigates an earlier effect |
| Rollback | Returning a supported component or state to an earlier version |
| Cancellation | Request to stop work; not necessarily reversal of completed effects |
| Deterministic | Same specified inputs and conditions produce the same result |
| Repeatability | A process can be carried out consistently under defined conditions |
| Reproducibility | Conditions and evidence permit a result to be reconstructed or meaningfully re-evaluated |

## Evaluation and quality

| Term | Working meaning |
|---|---|
| Eval | Structured assessment of AI-system behavior |
| Trial | One attempt at an evaluation task |
| Grader | Mechanism that scores a property |
| Rubric | Explicit criteria and scoring guidance |
| Test oracle | Basis for deciding whether behavior is correct |
| Outcome | Actual resulting state, not just the system's report |
| Trace or trajectory | Observable sequence of a trial's interactions |
| Capability evaluation | Measures what the system can accomplish |
| Regression evaluation | Checks that previously accepted behavior remains |
| Holdout | Evaluation material kept separate from routine optimization |
| Leakage | Information crosses a boundary that invalidates evaluation or privacy |
| Contamination | Prior exposure compromises an evaluation's intended independence |
| LLM-as-judge | Using a model to apply a rubric |
| Judge calibration | Comparing grading behavior against qualified reference judgments |
| False acceptance | Accepting a result that should fail |
| False rejection | Rejecting a valid result |
| Ablation | Removing or changing a component to study its contribution |
| `pass@k` | Whether at least one of multiple attempts succeeds |
| `pass^k` | Consistency measure emphasizing success across all repeated attempts |
| Evaluation saturation | A suite no longer distinguishes improvements because it is too easy |
| Reward hacking | Satisfying the measured objective without achieving the intended goal |
| Digital twin | Model or replica of a system's relevant behavior; fidelity is bounded |
| Acceptance | Decision that evidence meets the defined use requirements |
| Verification engineering | Making important correctness properties observable and actionable |

## Security and governance

| Term | Working meaning |
|---|---|
| Authentication | Establishing an identity |
| Authorization | Determining permitted actions in context |
| Least privilege | Granting only the authority needed |
| Principal | Identity under which an action is evaluated |
| Tenant | Isolation/account boundary in a shared system |
| Blast radius | Scope of possible impact |
| Prompt injection | Input content steers the model contrary to intended behavior |
| Indirect injection | Injection arriving through external content rather than the direct request |
| Confused deputy | A component misuses its authority on behalf of a less-privileged requester |
| Sandbox | Restricted execution environment with specific, testable boundaries |
| Egress control | Restriction on outbound data or network access |
| Credential broker | Component that supplies or uses credentials without broadly exposing them |
| Human in the loop | An explicit human decision is part of the execution path |
| Human on the loop | Human monitoring with an intervention capability |
| Risk-based review | Review intensity determined by consequences and uncertainty |
| Approval binding | Linking authorization to the exact action, target, and revision |
| Retention | Rules governing how long information is kept |
| Data minimization | Processing and retaining only what the purpose requires |
| Governance | Ownership, policy, decisions, oversight, and evidence for responsible operation |

## Models, operations, and economics

| Term | Working meaning |
|---|---|
| Pretraining | Broad parameter learning from training data |
| Fine-tuning | Parameter adaptation for a narrower purpose |
| Distillation | Training a model using another model's behavior as part of the learning signal |
| PEFT | Parameter-efficient fine-tuning methods |
| LoRA | Adapter-based low-rank parameter adaptation |
| Inference | Applying a trained model to an input |
| Prefill | Processing the input context before generation |
| Decode | Producing output tokens autoregressively |
| KV cache | Stored attention-related state used to reduce repeated inference computation |
| Quantization | Lower-precision representation of model data or computation |
| Continuous batching | Serving requests with dynamic admission/completion within batches |
| Model routing | Selecting a model or processing path for a request |
| MLOps | Engineering and operations practices for ML lifecycles |
| LLMOps | Operational practices emphasizing language-model applications |
| AgentOps | Operational practices emphasizing stateful agents and tool actions |
| Drift | Change that reduces the validity of prior behavior or evaluation |
| Model card | Documentation of model intended use, evaluation, and limitations |
| Dataset datasheet | Documentation of dataset motivation, composition, collection, and use |
| SLI | Service level indicator |
| SLO | Objective for an SLI |
| SLA | Service agreement with associated commitments or consequences |
| TTFT | Time to first token |
| Tail latency | Behavior near the slow end of a latency distribution |
| Unit economics | Cost and value per meaningful unit of work |
| Cost per accepted outcome | Total relevant cost divided across accepted work, including failed-attempt cost |
| TCO | Total cost of ownership, including operation and human effort |
| FinOps for AI | Managing cost and value of AI workloads |
| AI for FinOps | Using AI to perform financial/operational management tasks |

## False friends to remember

**Memory is not truth. A skill is not a worker. A schema is not permission. A trace is not proof. A passing test is not complete correctness. A ticket is not a durable queue. A sandbox is not unlimited safety. A model reviewer is not release authority. A factory is not a swarm.**
