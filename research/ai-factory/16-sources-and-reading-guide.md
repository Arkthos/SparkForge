# 16 - Annotated Sources and Reading Guide

[Back to the index](README.md)

**Access baseline for every entry:** 2026-11-04.

The [machine-readable catalog](sources.json) records URLs, source classes, publication timing where established, and retrieval status. "Read" means the scope described below, not independent replication. Research abstracts are labeled as such. Living documentation is not pinned to a historical repository commit unless explicitly stated.

## Recommended first reading sequence

Start with S42 and S48 for the practical vision, S06 for workflow patterns, S07 for long-running work, S10 for evaluation, S22 for trust boundaries, and S23 for side-effect reliability. Then use S03, S25, and S40 to connect engineering to ownership, operations, and economics.

Use specifications and SDK documentation when making a concrete integration decision. Do not start by reading every product manual.

<a id="s01"></a>
## S01 - NVIDIA: AI Factories

[Original source](https://www.nvidia.com/en-us/solutions/ai-factories/)

**Class/access:** vendor architecture and product positioning; directly read relevant excerpts. **Timing:** living page; publication date not established.

Useful for distinguishing the infrastructure meaning of AI factory: coordinated compute, networking, storage, energy, models, and applications. It explains the importance of serving efficiency and system-level design. Vendor performance and business-impact statements are not independent evidence that our workload needs the same infrastructure.

<a id="s02"></a>
## S02 - Google Cloud: MLOps, Continuous Delivery and Automation Pipelines

[Original source](https://docs.cloud.google.com/architecture/mlops-continuous-delivery-and-automation-pipelines-in-machine-learning)

**Class/access:** official architecture guidance; relevant excerpts read. **Timing:** page identifies a 2024-08-28 review baseline.

Explains why production ML is a system of data, configuration, evaluation, deployment, and monitoring rather than a model alone. Its automation levels are useful context, but the article primarily addresses predictive ML. Do not import continuous training into an agent architecture that does not train models.

<a id="s03"></a>
## S03 - Microsoft: Establish an AI Center of Excellence

[Original source](https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/ai/center-of-excellence)

**Class/access:** official organizational guidance; page text read. **Timing:** observed metadata includes `ms.date` 2025-06-09 and an update timestamp in October 2026.

Useful for ownership, multidisciplinary roles, intake, reusable assets, governance, and transitioning from centralized expertise to supported delivery teams. It is an Azure-oriented adoption guide, not proof that every small project needs a separate center of excellence.

<a id="s04"></a>
## S04 - StrongDM: Software Factory

[Original source](https://factory.strongdm.ai/)

**Class/access:** primary practitioner/vendor account; page text read. **Timing:** publication date not established from the retrieved page.

Introduces specifications, behavioral scenarios, satisfaction, and a Digital Twin Universe as part of a non-interactive development approach. Particularly valuable for thinking about weak tests and evaluator gaming. Its no-human-code-review charter and spending heuristics are operating choices, not general safety or economic conclusions.

<a id="s05"></a>
## S05 - OpenAI: Harness Engineering

[Original source](https://openai.com/index/harness-engineering/)

**Class/access:** vendor engineering report; **indexed excerpts only**, because direct retrieval returned HTTP 403. **Timing:** February 11, 2026, visible in the original-page search result.

The accessible excerpts describe an agent-first internal product experiment, repository knowledge as a system of record, an instruction file as a map, and architectural/maintenance practices. Use for those limited claims. This corpus does not claim to have read or independently validated the entire report.

<a id="s06"></a>
## S06 - Anthropic: Building Effective Agents

[Original source](https://www.anthropic.com/research/building-effective-agents)

**Class/access:** vendor engineering guidance; relevant excerpts read. **Timing:** originally December 2024; the observed page contains a note directing readers to newer managed-agent material.

Foundational taxonomy of workflows, agents, chaining, routing, parallelization, orchestrator-workers, and evaluator-optimizer loops. Strong starting point for the principle of adding complexity only when needed. Its product references have evolved; use the patterns separately from current SDK selection.

<a id="s07"></a>
## S07 - Anthropic: Effective Harnesses for Long-Running Agents

[Original source](https://www.anthropic.com/research/effective-harnesses-for-long-running-agents)

**Class/access:** vendor engineering report; page text read. **Timing:** November 26, 2025.

Explains initializer/coding-session patterns, feature tracking, incremental progress, environment checks, and end-to-end testing. It explicitly describes limitations and open questions. The worked setting is full-stack web application development; do not generalize its exact file formats or agent topology without testing.

<a id="s08"></a>
## S08 - Anthropic: Effective Context Engineering for AI Agents

[Original source](https://www.anthropic.com/research/effective-context-engineering-for-ai-agents)

**Class/access:** vendor engineering guidance; substantial excerpts read. **Timing:** publication date not independently established in this review.

Connects prompt design, tools, evidence selection, just-in-time retrieval, compaction, and long-horizon work. Useful for treating context as a selected resource. Claims about particular models' long-context behavior should be evaluated on the intended workload rather than treated as universal.

<a id="s09"></a>
## S09 - Anthropic: Writing Tools for Agents

[Original source](https://www.anthropic.com/research/writing-tools-for-agents)

**Class/access:** vendor engineering guidance; relevant excerpts read. **Timing:** publication date not independently established.

Explains task-oriented tool design, clear boundaries, meaningful outputs, token efficiency, and tool evaluation. Useful alongside SWE-agent's ACI research. Recommendations from a vendor's own environment are starting hypotheses, not a replacement for our tool-contract tests.

<a id="s10"></a>
## S10 - Anthropic: Demystifying Evals for AI Agents

[Original source](https://www.anthropic.com/research/demystifying-evals-for-ai-agents)

**Class/access:** vendor engineering guidance; extensive excerpts read across evaluation structure and implementation guidance. **Timing:** publication date not independently established.

Defines task, trial, grader, trace, outcome, agent harness, and evaluation harness. Covers grader types, capability/regression suites, repeated trials, isolation, calibration, and maintenance. One of the most directly useful readings. Numerical benchmark anecdotes are not used here as current performance claims.

<a id="s11"></a>
## S11 - Anthropic: Managed Agents Architecture

[Original source](https://www.anthropic.com/research/managed-agents)

**Class/access:** vendor engineering report; page text read. **Timing:** publication date not independently established.

Describes separating the session, harness, and sandbox, with durable event history and credential boundaries. Also explains why model-specific harness workarounds can become obsolete. Reported operational gains belong to that deployment; the transferable lesson is interface and lifetime separation.

<a id="s12"></a>
## S12 - Claude Agent SDK Overview

[Original source](https://code.claude.com/docs/en/agent-sdk/overview)

**Class/access:** official SDK documentation; page text read. **Timing:** living documentation; redirected from the Claude Platform documentation location.

Useful for understanding the SDK's relationship to Claude Code, direct client SDKs, and managed agents, plus tools, hooks, permissions, sessions, and subagents. Product terms and authentication restrictions must be checked before adoption. A subscription or interactive login is not automatically an entitlement for every application use.

<a id="s13"></a>
## S13 - OpenAI Agents SDK

[Original source](https://openai.github.io/openai-agents-python/)

**Class/access:** official SDK documentation; relevant excerpts read. **Timing:** living documentation.

Describes agents, tools, handoffs, guardrails, sessions, tracing, and related execution capabilities. Helpful for distinguishing a direct API from a higher-level runtime. These are documented features, not proof that a particular configuration satisfies our durability, privacy, or release requirements.

<a id="s14"></a>
## S14 - LangGraph Persistence

[Original source](https://docs.langchain.com/oss/python/langgraph/persistence.md)

**Class/access:** official framework documentation; page text read. **Timing:** living documentation; the durable-execution URL redirected here.

Distinguishes checkpointers for thread state from stores for application-defined cross-thread data. Notes that in-memory persistence does not survive process restart. Useful for avoiding the assumption that an object named "memory" or "checkpointer" is automatically durable.

<a id="s15"></a>
## S15 - Model Context Protocol Specification, 2026-07-28

[Original source](https://modelcontextprotocol.io/specification/2026-07-28)

**Class/access:** protocol specification; overview page read. **Timing:** explicit specification version.

Defines the observed host/client/server and capability model, plus security and consent principles. The version is deliberately identified and is not claimed to be the latest. Implementation-level decisions require the relevant detailed sections, capability negotiation, and interoperability tests.

<a id="s16"></a>
## S16 - Agent2Agent Protocol Specification, 1.0.0

[Original source](https://a2a-protocol.org/v1.0.0/specification/)

**Class/access:** protocol specification; introduction and structural excerpts read. **Timing:** explicit version 1.0.0.

Explains agent discovery, tasks, messages, artifacts, and interactions between independent agent systems. Useful for separating remote-agent collaboration from local tool invocation. Compatibility does not establish trust, permission, task correctness, or operational reliability.

<a id="s17"></a>
## S17 - Agent Skills Overview

[Original source](https://agentskills.io/home.md)

**Class/access:** format documentation; page text read. **Timing:** living documentation; redirected from the introductory URL.

Defines a skill as a folder centered on `SKILL.md`, with optional scripts, references, and assets. Explains progressive disclosure. Useful for correcting the assumption that a skill is always a separate agent or process. Executable resources still need normal supply-chain and permission controls.

<a id="s18"></a>
## S18 - AGENTS.md

[Repository README](https://github.com/agentsmd/agents.md)

**Class/access:** maintainer documentation; README read through its raw source. **Timing:** repository default-branch observation.

Describes a simple open format for project guidance to coding agents. Useful for discoverable build, test, and contribution context. Runtime-specific discovery and precedence behavior still needs verification; an instruction file is not an enforcement mechanism.

<a id="s19"></a>
## S19 - NIST AI Risk Management Framework

[Original source](https://www.nist.gov/itl/ai-risk-management-framework)

**Class/access:** government framework overview; page text read. **Timing:** AI RMF 1.0 released January 26, 2023; overview also identifies the July 26, 2024 GenAI Profile and ongoing revision work.

Useful for risk ownership and lifecycle framing. The framework is voluntary; citing it is not certification or proof of compliance. This review read the overview, not a full legal mapping or every linked profile.

<a id="s20"></a>
## S20 - NIST AI RMF Playbook

[Original source](https://airc.nist.gov/airmf-resources/playbook/)

**Class/access:** government guidance; overview page read. **Timing:** living resource.

Organizes suggested actions under Govern, Map, Measure, and Manage. Explicitly states that it is not a checklist to apply in its entirety. Use it to structure questions and evidence appropriate to the use case.

<a id="s21"></a>
## S21 - OWASP Top 10 for LLM and Generative AI Applications, 2025

[Original source](https://genai.owasp.org/llm-top-10/)

**Class/access:** security-community guidance; relevant category list checked through the original page's indexed excerpt. **Timing:** 2025 edition.

Useful risk inventory: prompt injection, sensitive information disclosure, supply chain, poisoning, output handling, excessive agency, prompt leakage, vector/embedding weaknesses, misinformation, and unbounded consumption. The landing-page text extractor omitted the category content. Treat this as a risk inventory, not an exhaustive audit.

<a id="s22"></a>
## S22 - OWASP: Prompt Injection

[Original source](https://genai.owasp.org/llmrisk/llm01-prompt-injection/)

**Class/access:** defensive security guidance; relevant excerpts read directly. **Timing:** page associated with the 2025 risk framework.

Explains direct and indirect injection, consequences, and layered mitigations. Explicitly rejects the idea that retrieval or fine-tuning fully solves injection. Useful for understanding why external content remains untrusted and why least privilege matters.

<a id="s23"></a>
## S23 - AWS Builders' Library: Making Retries Safe with Idempotent APIs

[Original source](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/)

**Class/access:** primary engineering guidance; relevant excerpts read. **Timing:** publication date not established.

Explains idempotency contracts, stable request identity, and semantically equivalent responses. Essential background for agents that create external effects. It does not imply that every remote API supports idempotency or that local checkpointing creates exactly-once behavior.

<a id="s24"></a>
## S24 - OpenTelemetry GenAI Semantic Conventions

[Current repository](https://github.com/open-telemetry/semantic-conventions-genai)<br>
[Migration notice](https://opentelemetry.io/docs/specs/semconv/gen-ai/)

**Class/access:** maintainer documentation; migration notice and repository README read. **Timing:** living/default-branch observation.

The former documentation location now points to a dedicated GenAI repository covering spans, metrics, and events. Useful for planning interoperable telemetry. Exact schema URLs, attribute stability, and implementation support must be checked when adopting a version; they are not established by this overview reading.

<a id="s25"></a>
## S25 - Google SRE: Service Level Objectives

[Original source](https://sre.google/sre-book/service-level-objectives/)

**Class/access:** primary engineering reference; substantial excerpts read. **Timing:** book chapter; exact page revision not established.

Defines SLIs, SLOs, and SLAs and explains why measurement must reflect user-relevant behavior. Particularly useful for separating availability from correctness and avoiding misleading averages. The chapter's historical service examples are not current commitments.

<a id="s26"></a>
## S26 - ReAct: Synergizing Reasoning and Acting in Language Models

[Paper](https://arxiv.org/abs/2210.03629)

**Class/access:** research; abstract and bibliographic metadata read. **Timing:** initial preprint 2022; observed v3 metadata identifies the 2023 camera-ready version.

Influential example of interleaving model reasoning and environmental actions. Useful historical foundation for tool-using loops. Abstract-level review does not justify generalizing its benchmark improvements to current models or arbitrary factory workloads.

<a id="s27"></a>
## S27 - Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks

[Paper](https://arxiv.org/abs/2005.11401)

**Class/access:** research; abstract and metadata read. **Timing:** initial preprint May 22, 2020; accepted at NeurIPS 2020.

Foundational work combining parametric and non-parametric knowledge for generation. Useful for understanding the historical RAG concept. Modern application architectures use a broader range of retrieval mechanisms than the paper's particular model.

<a id="s28"></a>
## S28 - Lost in the Middle: How Language Models Use Long Contexts

[Paper](https://aclanthology.org/2024.tacl-1.9/)

**Class/access:** research publication; abstract and metadata read. **Timing:** TACL 2024.

Reports position-sensitive performance in multi-document question answering and key-value retrieval. Supports testing effective context use rather than relying on nominal window size. It is not a universal performance law for every later architecture or model.

<a id="s29"></a>
## S29 - SWE-agent: Agent-Computer Interfaces Enable Automated Software Engineering

[Paper](https://arxiv.org/abs/2405.15793)

**Class/access:** research; abstract and metadata read. **Timing:** 2024; observed v3.

Studies how interface design affects coding-agent behavior and performance. Useful for treating tools as agent-facing interfaces rather than only wrappers around human APIs. Historical benchmark scores are not used as current capability estimates.

<a id="s30"></a>
## S30 - Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena

[Paper](https://arxiv.org/abs/2306.05685)

**Class/access:** research; abstract and metadata read. **Timing:** 2023; observed v4.

Examines model-judge agreement and biases including position, verbosity, and self-enhancement. Useful for explaining why model grading needs calibration. Agreement reported in the study does not establish validity for our domain-specific acceptance decisions.

<a id="s31"></a>
## S31 - DSPy: Compiling Declarative Language Model Calls into Self-Improving Pipelines

[Paper](https://arxiv.org/abs/2310.03714)

**Class/access:** research; abstract and metadata read. **Timing:** initial preprint October 5, 2023.

Introduces a programmatic approach to composing and optimizing language-model pipelines against a metric. Useful conceptual counterpoint to manual prompt tinkering. Optimizing a metric does not ensure the metric represents the full user goal.

<a id="s32"></a>
## S32 - METR: Early-2025 AI and Experienced Developer Productivity

[Original study account](https://metr.org/blog/2025-07-10-early-2025-ai-experienced-os-dev-study/)

**Class/access:** independent empirical study account; methodology, results, and limitations read. **Timing:** July 10, 2025.

Reports a randomized study of 16 experienced developers and 246 tasks in their own open-source projects, finding tasks took 19% longer with the studied AI tooling. The source explicitly warns against broad generalization. Read with S33; this is a historical setting, not a current universal effect.

<a id="s33"></a>
## S33 - METR: Changing the Developer Productivity Experiment Design

[Original update](https://metr.org/blog/2026-02-24-uplift-update/)

**Class/access:** independent empirical-methodology update; page text read. **Timing:** February 24, 2026.

Explains why later data gives an unreliable signal of current productivity effects: participant and task selection, compensation changes, and difficulty measuring concurrent-agent work. Essential correction to simplistic reuse of the earlier result. Do not turn the newer raw estimates into a universal causal speedup.

<a id="s34"></a>
## S34 - Harness: Overview of Harness AI

[Original documentation](https://developer.harness.io/harness-platform/use-harness-ai/harness-ai)

**Class/access:** official product documentation; relevant excerpts read. **Timing:** living documentation.

Describes AI-assisted software-delivery features on the Harness platform. Included to disambiguate the company/product from generic harness engineering. No product evaluation, procurement recommendation, or verified integration is implied.

<a id="s35"></a>
## S35 - NVIDIA: Mastering LLM Techniques, Inference Optimization

[Original source](https://developer.nvidia.com/blog/mastering-llm-techniques-inference-optimization/)

**Class/access:** vendor technical guidance; relevant excerpts read. **Timing:** living article; exact current revision date not established.

Explains prefill, decode, KV caching, batching, memory, and parallelism. Useful infrastructure background. Concrete memory and throughput examples depend on architecture, precision, hardware, and workload; do not use them as a current sizing calculator.

<a id="s36"></a>
## S36 - Hidden Technical Debt in Machine Learning Systems

[Proceedings abstract](https://proceedings.neurips.cc/paper/2015/hash/86df7dcfd896fcaf2674f757a2463eba-Abstract.html)

**Class/access:** research publication; abstract read. **Timing:** NeurIPS 2015.

Identifies system-level debt including entanglement, data dependencies, hidden feedback loops, undeclared consumers, and configuration issues. Useful for understanding why a quick model-enabled result can create long-term operating obligations. This review did not reproduce or audit the full paper.

<a id="s37"></a>
## S37 - EleutherAI Language Model Evaluation Harness

[Repository](https://github.com/EleutherAI/lm-evaluation-harness)

**Class/access:** maintainer documentation; README excerpts read through raw source. **Timing:** default-branch observation.

A concrete example of infrastructure for evaluating generative language models across tasks. Included to distinguish evaluation harnesses from agent execution harnesses. Standard benchmark support does not replace domain-specific factory evaluation.

<a id="s38"></a>
## S38 - Model Cards for Model Reporting

[Paper](https://arxiv.org/abs/1810.03993)

**Class/access:** research/documentation proposal; abstract and metadata read. **Timing:** initial preprint 2018; FAT* 2019 publication.

Proposes documenting intended use, evaluation conditions, performance characteristics, and limitations. Useful template for transparent component reporting. A model card is evidence organization, not a warranty or a substitute for application-level evaluation.

<a id="s39"></a>
## S39 - Datasheets for Datasets

[Paper](https://arxiv.org/abs/1803.09010)

**Class/access:** research/documentation proposal; abstract and metadata read. **Timing:** initial preprint 2018; CACM publication in 2021.

Proposes documenting dataset motivation, composition, collection, and recommended uses. Useful for ingestion and evaluation data governance. Documentation does not by itself establish the rights to collect, use, or redistribute the data.

<a id="s40"></a>
## S40 - FinOps Foundation: AI Tools and Services Considerations

[Original source](https://www.finops.org/wg/finops-for-ai-tools-services-considerations/)

**Class/access:** practitioner guidance; lifecycle/tooling excerpts read, with use-case economics also surfaced in the source's indexed excerpt. **Timing:** publication date not independently established.

Useful for locating costs across training, adaptation, inference, retrieval, orchestration, and operations. Its workload-specific numerical examples and broad heuristics should not be imported as guarantees. The corpus uses its lifecycle framing, not a fixed vendor price or savings claim.

<a id="s41"></a>
## S41 - LangGraph Checkpointers

[Original source](https://docs.langchain.com/oss/python/langgraph/checkpointers)

**Class/access:** official framework documentation; relevant excerpts read. **Timing:** living documentation.

Explains threads, checkpoints, super-steps, pending writes, and distinctions between new input, resuming, and replaying. Especially important: an interrupted node can restart from its beginning. Checkpoint semantics need to be understood before wrapping side-effecting tools.

<a id="s42"></a>
## S42 - Andrew Allbright: From AI Harness to Software Factory

[Original article](https://andrewallbright.com/from-ai-harness-to-software-factory-a-practical-agentic-engineering-stack/)

**Class/access:** practitioner proposal; supplied article and directly retrieved page read. **Timing:** June 21, 2026, from the supplied article footer.

Practical anchor for shared task entry points, personas, developer sessions, work tracking, and artifact separation. Read [chapter 13](13-allbright-stack-analysis.md) alongside it: the article's terminology, retention assumptions, and interchangeability claim require qualification.

<a id="s43"></a>
## S43 - Andrew Allbright: Verification Engineering

[Original article](https://andrewallbright.com/verification-engineering/)

**Class/access:** practitioner concept note; page text read. **Timing:** publication date not established.

Frames deterministic verification as the agent's feedback sensor and identifies a shift from producing code toward determining correctness. Useful concise motivation. It is not a formal verification method or empirical proof of the claimed bottleneck shift.

<a id="s44"></a>
## S44 - Task Documentation

[Guide](https://taskfile.dev/docs/guide/)<br>
[Dependencies and task calls](https://taskfile.dev/docs/guide/dependencies)<br>
[Platforms and shells](https://taskfile.dev/docs/guide/platforms)

**Class/access:** official tool documentation; guide and relevant execution/platform sections read. **Timing:** living documentation.

Supports the article's command-registry idea and adds important semantics: dependencies can run concurrently; sequential task calls establish order; commands use an embedded shell; platform support does not make arbitrary scripts portable. No Task installation or configuration was performed.

<a id="s45"></a>
## S45 - Tmuxinator README

[Repository](https://github.com/tmuxinator/tmuxinator)

**Class/access:** maintainer documentation; README excerpts read. **Timing:** default-branch observation.

Describes management of tmux sessions and its Ruby/tmux environment assumptions. Useful for separating a convenient developer layout from process supervision or an agent runtime. It is one possible environment tool, not a requirement for our Windows setup.

<a id="s46"></a>
## S46 - pre-commit

[Official documentation](https://pre-commit.com/)

**Class/access:** official tool documentation; introductory/configuration excerpts read. **Timing:** living documentation.

Explains shared multi-language hooks and local quality feedback, with CI use also described. Useful for shifting simple checks earlier. Local hooks are not the sole release or security boundary.

<a id="s47"></a>
## S47 - Microsoft: Windows Terminal Panes

[Official documentation](https://learn.microsoft.com/en-us/windows/terminal/panes)

**Class/access:** official tool documentation; relevant excerpts read. **Timing:** observed document metadata dated November 2025.

Confirms a native Windows option for multiple visible command-line applications. Supports an environment alternative to tmux-based layouts, not an assertion that the two tools have identical lifecycle or persistence semantics.

<a id="s48"></a>
## S48 - Eric Risco: Software Factory Video

[Original video](https://www.youtube.com/watch?v=p6nnqerea7w)<br>
[Requested 14:18 section](https://www.youtube.com/watch?v=p6nnqerea7w&t=858s)

**Class/access:** practitioner video; original metadata, full Spanish auto-generated transcript, and selected frames reviewed. **Timing:** October 23, 2026.

Describes common intake, a project brain, specification writer, test-first builder, four reviewers, feedback consolidation, risk routing, and a content-production example. At 14:18 the discussion concerns video editing; final content review/upload remains manual. See [chapter 20](20-eric-risco-video-review.md) for precise review scope and caveats.

<a id="s49"></a>
## S49 - Eric Risco: RSC Harness README

[Repository](https://github.com/ericrisco/rsc-harness)

**Class/access:** maintainer/practitioner documentation; README excerpts read through raw source. **Timing:** current default-branch observation, not a snapshot of the video's exact implementation.

Describes project knowledge, skills, installation-plan approval, provider-specific hooks, memory, review, Git permissions, and synchronization behavior. Useful for examining the distance between instructions and enforcement. No installation, code audit, or behavioral verification was performed; automatic Git and data-sharing behavior would require review before adoption.

## How to continue reading

For a concrete implementation decision, move from these overview readings to the exact versioned API, permission model, deployment guide, and relevant tests. For a consequential empirical claim, read the full paper and its methodology before relying on its numbers.

The corpus intentionally leaves some questions open rather than presenting a collection of sources as a substitute for local evidence.
