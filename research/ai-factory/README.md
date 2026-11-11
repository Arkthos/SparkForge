# AI Factory and Harness Engineering: Knowledge Corpus

**Research baseline:** 2026-11-04<br>
**Purpose:** develop the understanding needed to design our own AI-enabled software factory later.<br>
**Status:** research and learning material, not an implemented factory or a production-readiness certification.

> **Publication edition, 2026-11-11:** this collection preserves the
> 2026-11-04 research baseline. Statements about future implementation,
> unselected components, and unexecuted labs describe that research, not the
> current SparkForge product. See the [publication notes](../README.md) for
> editorial changes, evidence boundaries, and local validation. No external
> source was refreshed or proposed lab executed for this edition.

## Start here

An AI model can generate a plausible answer. An agent can use tools to pursue a task. A harness makes that execution bounded, observable, resumable, and testable. A software factory organizes many such executions into a repeatable delivery system with explicit ownership, quality evidence, and release authority.

Our main interest is **agentic software engineering**: converting a well-defined need into a verified, maintainable software change. We also cover enterprise AI delivery and AI compute infrastructure because both are called "AI factories," but they solve different problems.

Andrew Allbright's **From AI Harness to Software Factory: A Practical Agentic Engineering Stack**, supplied as a reference for this project, is the practical anchor. Its command registry, agent roles, developer environment, and work queue are useful starting points. They are analyzed rather than adopted uncritically. See [the dedicated reading](13-allbright-stack-analysis.md).

Eric Risco's supplied video adds concrete software and content-production workflows. See [the video review](20-eric-risco-video-review.md), including the requested **14:18** segment, a timestamped guide, and a critical comparison with the article.

**The central principle:** generated output is a candidate; evidence supports acceptance; authorization permits consequential action. These are three different events.

## Reading routes

| Route | Read | Intended result |
|---|---|---|
| Orientation | 01, 02, 03, 13 | Explain what a factory and a harness actually do |
| Engineering core | 04 through 08 | Design context, tool, orchestration, evaluation, and security boundaries |
| Production and economics | 09, 10, 11 | Understand lifecycle, operating costs, and software delivery |
| Future solution design | 12, 18, templates | Produce a reviewable design without prematurely choosing a stack |
| Deliberate practice | 14, 19 | Demonstrate competence through exercises and scenario reasoning |
| Research scrutiny | 00, 16, 17 | Check provenance, evidence strength, and unresolved questions |

Read the orientation route first, not the entire bibliography. Then work through the engineering core with the synthetic scenario open beside it.

## Contents

| Document | Scope |
|---|---|
| [00 - Research method](00-research-method.md) | Scope, evidence classes, access limitations, freshness, and maintenance |
| [01 - Foundations and concept map](01-foundations-and-concept-map.md) | Models, agents, workflows, harnesses, factories, and common confusions |
| [02 - AI factory operating model](02-ai-factory-operating-model.md) | Value streams, ownership, artifacts, maturity, and feedback loops |
| [03 - Harness engineering](03-harness-engineering.md) | Execution lifecycle, state, policy, checkpoints, and completion contracts |
| [04 - Context, memory, and RAG](04-context-memory-and-rag.md) | Knowledge selection, retrieval, provenance, retention, and memory hygiene |
| [05 - Tools, skills, and protocols](05-tools-skills-and-protocols.md) | Tool contracts, MCP, A2A, instruction files, and procedural knowledge |
| [06 - Orchestration and reliability](06-orchestration-and-reliability.md) | Workflow patterns, delegation, retries, concurrency, and recovery |
| [07 - Evaluation and verification](07-evaluation-and-verification.md) | Graders, suites, holdouts, repeated trials, and release evidence |
| [08 - Security and governance](08-security-and-governance.md) | Trust boundaries, identity, approvals, privacy, and human control |
| [09 - Models, infrastructure, and MLOps](09-models-infrastructure-and-mlops.md) | Training versus inference, deployment, compute, adaptation, and lifecycle |
| [10 - Observability, economics, and operations](10-observability-economics-and-operations.md) | Traces, SLOs, unit economics, incidents, and improvement |
| [11 - Specification-driven software factories](11-spec-driven-software-factories.md) | Specifications, scenarios, feedback, code review, and delivery gates |
| [12 - Reference architecture and decisions](12-reference-architecture-and-decisions.md) | A provider-neutral reference design and build-versus-buy choices |
| [13 - Allbright stack analysis](13-allbright-stack-analysis.md) | Detailed critique of the supplied article and Windows adaptations |
| [14 - Learning path and labs](14-learning-path-and-labs.md) | Competency-based curriculum with concrete exercises and acceptance criteria |
| [15 - Glossary](15-glossary.md) | Compact definitions and distinctions |
| [16 - Sources and reading guide](16-sources-and-reading-guide.md) | Annotated primary sources, practitioner sources, and reading priorities |
| [17 - Evidence map and open questions](17-evidence-map-and-open-questions.md) | Consequential claims, support, limits, and experiments still needed |
| [18 - Worked factory scenario](18-worked-factory-scenario.md) | A synthetic software change from intake to recovery and release |
| [19 - Competency assessment](19-competency-assessment.md) | Questions, answer guidance, and a readiness rubric |
| [20 - Eric Risco video review](20-eric-risco-video-review.md) | Full-transcript review, selected visual checks, software/content pipelines, and critical lessons |

## Reusable design templates

These are **unfilled planning aids**, not approved configurations or executable policies.

- [Use-case charter](templates/use-case-charter.md)
- [Harness and task contract](templates/harness-and-task-contract.md)
- [Evaluation plan](templates/evaluation-plan.md)
- [Architecture decision record](templates/architecture-decision-record.md)
- [Release evidence record](templates/release-evidence-record.md)
- [Incident and learning review](templates/incident-and-learning-review.md)

The [source catalog](sources.json) provides machine-readable source IDs, URLs, source classes, and retrieval status. It is not a cache of the original articles.

The generated [corpus manifest](corpus-manifest.json) inventories the documents and their content hashes for later ingestion and change detection. It does not certify external source claims or make the proposed labs executed.

## What we should be able to explain

By applying the material, we should be able to:

1. Select the least complex approach that solves a use case: deterministic software, a model call, a workflow, or an agent.
2. Draw the boundary between the model's proposals and the system's authority.
3. Design a harness that stops, resumes, and reports uncertainty without duplicating external actions.
4. Define success independently of the agent's own description of its work.
5. Distinguish tool access, procedural knowledge, persistent memory, and orchestration.
6. Measure accepted outcomes, total cost, operational risk, and human effort rather than token volume or code volume.
7. Explain when a practitioner pattern is useful and what evidence is missing before generalizing it.
8. Produce a small, testable factory design whose components can be replaced without losing accountability.

Reading alone does not demonstrate expertise. The labs and assessment turn these goals into observable work products.

## Ten durable lessons

1. A better model does not remove the need for clear goals, permissions, and outcome verification.
2. The harness is part of the evaluated system, not an interchangeable footnote to a model benchmark.
3. Documentation helps agents find information; it does not enforce security.
4. A context summary is not the authoritative record of what happened.
5. A timeout does not prove that an external operation failed.
6. More agents add coordination and failure modes as well as potential capacity.
7. Test passing is evidence about tested properties, not proof of complete correctness.
8. Human review must have a defined object, authority, and point in the lifecycle.
9. Cost per accepted outcome is more meaningful than cost per token alone.
10. A factory is successful when it repeatedly delivers useful, safe, maintainable outcomes, not when it maximizes autonomy.

## Boundaries of this corpus

This is an original synthesis of public material and the article supplied by the user. It does not contain private project records, credentials, copied article archives, live agent transcripts, or private wiki exports.

At the research baseline, no product or provider was selected and no frameworks, hooks, background services, connectors, or model endpoints were installed or configured by the study. Exercises are proposed work, not reported experiments. Numerical examples are explicitly illustrative.

This repository edition contains the reviewed public-source synthesis and bibliographic metadata only. Its publication does not authorize storing confidential datasets, credentials, or runtime records alongside it.

## Using this corpus in a future knowledge system

Use the chapter title, section heading, source IDs, and research date as retrieval metadata. Preserve the difference between **documented fact**, **reported experience**, and **proposed design** when chunking the documents. Do not turn recommendations or synthetic examples into claims about an implemented system.

Before a later design commitment, refresh the relevant source pages and create an architecture decision record. Before a production claim, execute the corresponding tests and record the exact revision and evidence.
