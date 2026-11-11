# 09 - Models, Infrastructure, and the AI Lifecycle

[Back to the index](README.md)

## Why this belongs in a software-factory corpus

Our factory can use hosted models without owning GPU infrastructure. We still need to understand the lifecycle and economics of the services it depends on.

An infrastructure AI factory and a software factory meet at a service boundary: the software factory consumes inference capability; the infrastructure factory operates the compute, model-serving, and related systems. NVIDIA's definition emphasizes coordinated infrastructure across energy, chips, infrastructure, models, and applications. [S01](16-sources-and-reading-guide.md#s01)

Do not confuse "building our own AI factory" with "training our own foundation model."

## The model lifecycle

| Activity | What changes | Main evidence needed |
|---|---|---|
| Pretraining | Broad model parameters learned from large datasets | Data legitimacy, training quality, broad evaluation |
| Post-training or adaptation | Behavior or task capability | Suitable data, comparative evaluation, safety effects |
| Fine-tuning | Parameters adapted for a narrower purpose | Holdout performance and regression analysis |
| Retrieval/indexing | External knowledge available at inference | Source quality, permissions, retrieval evaluation |
| Prompt or harness revision | How the model is used | System-level regression and operational evaluation |
| Inference | A model processes an input | Correct routing, usage accounting, bounded execution |
| Deployment | A configuration becomes available to users | Promotion evidence, monitoring, recovery |
| Retirement | A model/configuration stops being used | Dependency migration and retention decisions |

These are separate activities. Re-indexing a document corpus is not the same as training a foundation model. Editing a system prompt is not fine-tuning.

## Model selection is workload selection

Evaluate candidates on the actual task classes:

- tool selection and argument correctness;
- instruction following under realistic context;
- ability to use the required modalities;
- supported context length and effective retrieval;
- artifact quality and regression rate;
- latency and throughput;
- total usage and cost;
- privacy, contractual, regional, and operational constraints;
- availability of a supported integration;
- failure behavior.

A model that is excellent at open-ended prose may not be the best fit for a strict extraction tool. A smaller model can be sufficient for a narrow task, but only measured evidence can establish that sufficiency.

The model names assigned to reviewers in the supplied video are examples of one creator's choices, not a benchmark-derived recommendation for our system. [S48](16-sources-and-reading-guide.md#s48)

## Hosted versus self-hosted

| Approach | Advantages | Responsibilities and tradeoffs |
|---|---|---|
| Hosted API | Fast access, managed serving, less infrastructure work | Provider terms, data boundary, quotas, version changes, recurring usage |
| Managed private deployment | More deployment and access options | Contract and configuration complexity, cost, platform dependence |
| Self-hosted model | Greater infrastructure control and customization | Hardware, patching, scaling, security, availability, model licensing |
| Hybrid | Fit different approved workloads to different environments | More operational and evaluation complexity |

Self-hosting is not automatically cheaper or more private in practice. A poorly operated local deployment can expose data; a low-utilization GPU can be expensive. Conversely, a hosted service may be unsuitable for a particular data classification or operating requirement.

Open weights do not automatically mean unrestricted open-source rights. Check the actual license and intended use.

## Inference concepts

### Prefill

The model processes the input context and prepares internal states used for generation. Long prompts can increase this work and affect time to first token.

### Decode

An autoregressive model generates subsequent tokens using prior context and generated output. Sequential generation creates different performance characteristics from input processing.

### KV cache

The serving system can retain attention-related key/value states to avoid recomputing them at each generation step. This improves efficiency but consumes memory. It is not the same as application memory or a database of past answers.

### Batching

Serving multiple requests together can improve hardware utilization. Continuous or in-flight batching handles requests whose generation lengths differ, rather than forcing every request to wait for the longest member of a static batch.

### Quantization

Lower-precision representations can reduce memory and sometimes improve performance. Quality and latency effects depend on the model, implementation, hardware, and workload; evaluate them rather than assuming no loss.

### Parallelism

Models or workloads can be distributed across devices. The choices affect memory, communication overhead, capacity, and operational complexity.

NVIDIA's inference-optimization article explains prefill, decode, batching, caching, and model parallelism. Its concrete examples are technical context, not a current sizing guarantee for our future deployment. [S35](16-sources-and-reading-guide.md#s35)

## Measure the right serving behavior

| Measure | What it reveals | Limitation |
|---|---|---|
| Time to first token | Delay before output begins | Not total task completion time |
| Inter-token latency | Generation responsiveness | Does not capture tool or review delays |
| End-to-end latency | User-visible completion time | Must define where the task starts and ends |
| Throughput | Work handled per unit time | Can improve while individual latency worsens |
| Queue delay | Capacity pressure | May be hidden by server-only metrics |
| Memory utilization | Capacity constraints | High utilization alone does not mean useful work |
| Tokens per cost or energy unit | Serving efficiency | Not equivalent to accepted business outcomes |

Different tokenizers make raw token counts imperfect cross-model comparisons. A software factory should ultimately measure completed, accepted work as well as infrastructure efficiency.

## Caching is not one mechanism

- **Prompt caching:** reuse computation for eligible repeated input prefixes or segments under a provider's contract.
- **KV caching:** lower-level reuse of inference state.
- **Exact result caching:** return a previous answer for an equivalent request.
- **Semantic caching:** reuse an answer for an approximately similar request.
- **Tool-result caching:** reuse an external observation for a defined validity period.

Each needs scope and invalidation. A cached answer must not cross tenant permissions. A cached account balance can become wrong. A semantic match is not proof that two legal or financial questions have the same answer.

## MLOps, LLMOps, and AgentOps

MLOps applies software-engineering and operational disciplines to ML systems: data validation, training, model evaluation, deployment, and monitoring. Google's guide describes increasing levels of automation for predictive ML pipelines. [S02](16-sources-and-reading-guide.md#s02)

LLMOps usually expands attention to prompts, retrieval, model providers, generated output, and token economics. AgentOps adds tool actions, stateful trajectories, delegation, permission boundaries, and recovery.

These names are useful areas of emphasis, not universally standardized product categories. Do not copy a predictive-ML continuous-training architecture when the problem is a hosted-model agent with no training pipeline.

## Version the deployed system

The relevant version is a bundle:

- application code;
- model identifier and available revision information;
- prompt and skill revisions;
- harness configuration;
- tool schemas and adapters;
- retrieval index and source versions;
- policy;
- evaluators;
- dependencies and environment.

Temperature settings and a model name do not guarantee deterministic reproduction. Hosted implementations can change, and external services evolve. Record reproducibility limits honestly.

## Data and model documentation

Model Cards propose documenting intended uses, evaluation conditions, performance characteristics, and limitations. Datasheets for Datasets propose documenting dataset motivation, composition, collection, and recommended uses. [S38](16-sources-and-reading-guide.md#s38) [S39](16-sources-and-reading-guide.md#s39)

For our factory, adapt the idea into system documentation: what work is supported, what is prohibited, what evidence exists, and what is not assessed.

Documentation is especially important when a component is reused outside its original context.

## Drift and technical debt

The system can degrade when:

- users ask different kinds of questions;
- source documents change;
- an API changes its behavior;
- a model version changes;
- a skill or prompt accumulates contradictory exceptions;
- evaluators become stale or saturated;
- hidden dependencies proliferate.

The Hidden Technical Debt paper identifies system-level risks such as entanglement, data dependencies, hidden feedback loops, and undeclared consumers. Its general warning applies here: quick model-enabled wins can carry substantial ongoing maintenance obligations. [S36](16-sources-and-reading-guide.md#s36)

## Initial implication for our project

A first software-factory experiment should consume an approved existing model and focus on task contracts, verification, and recovery. Training infrastructure, distributed inference, and multi-provider routing should remain deferred unless the task and evidence justify them.
