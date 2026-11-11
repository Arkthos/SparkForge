# 14 - Learning Path and Practical Labs

[Back to the index](README.md)

## Learning is demonstrated, not declared

The objective is to become capable of designing, evaluating, and operating a bounded factory. Reading the documents is preparation; explaining tradeoffs and producing evidence are the assessment.

These labs are **proposed exercises**. They have not been executed as part of this research corpus. They do not authorize spending, installing tools, connecting private systems, or publishing outputs.

Use public or synthetic inputs. Any model-assisted experiment should first establish an approved provider, data boundary, and budget.

## Prerequisites

Helpful foundations:

- basic software development and version control;
- command execution and exit statuses;
- HTTP/API concepts;
- testing and data formats;
- elementary measurement and experimental design;
- identity and access-control concepts.

If a prerequisite is missing, learn it while working through the corresponding lab. A sophisticated agent framework is not a prerequisite.

## Four learning stages

| Stage | Core reading | Demonstration |
|---|---|---|
| Explain | 01, 02, 03, 13, 20 | Draw the system and distinguish its responsibilities |
| Design | 04, 05, 06, 08, 12 | Specify contracts, state, trust boundaries, and failure behavior |
| Evaluate | 07, 10, 11, 17 | Build an evaluation plan and interpret uncertain evidence |
| Operate | 09, 10, 18, 19 | Exercise recovery, controls, and a release decision |

Proceed by demonstrated competency rather than a fixed promise of expertise in a certain number of weeks.

## Lab 1 - Classify the system

**Goal:** remove vocabulary confusion.

**Exercise:** classify twelve situations: a document classifier, a fixed extraction pipeline, a coding loop, a task runner, a terminal multiplexer, a skills folder, a vector search service, a model API, a multi-agent planner, a test runner, a release approval service, and an enterprise AI platform.

**Deliverable:** a concept map showing model, workflow, agent, harness, tool, environment, verification, and factory.

**Acceptance:** explain why at least three examples belong to more than one practical system but are not interchangeable concepts. Identify where authority resides.

**Failure to detect:** calling every automated component an agent or every collection of tools a factory.

## Lab 2 - Critique the supplied sources

**Goal:** distinguish useful ideas from unsupported generalizations.

**Exercise:** use the Allbright article and Risco video to extract ten claims. For each, record source location, evidence class, what it supports, what it does not support, and a testable local implication.

**Deliverable:** a claim/evidence table.

**Acceptance:** include the article's artifact-retention claim and the video's risk-routing and content-publication claims. Preserve the fact that the video describes manual final content review/upload.

**Failure to detect:** turning a creator's proof of concept into a verified production capability, or treating a source's popularity as evidence.

## Lab 3 - Design a repeatable command contract

**Goal:** understand the command registry before choosing a task runner.

**Exercise:** specify `verify`, `dev`, and `evidence` operations for a tiny synthetic project. Define inputs, directory, dependencies, outputs, failure status, cleanup, and supported environment.

**Deliverable:** command contracts and an execution-order diagram.

**Acceptance:** identify which checks can run concurrently and which must be sequential. Explain how a failed child command reaches the caller. Include a service-readiness check.

**Failure to detect:** assuming a pane that displays logs is a reliable machine-readable interface.

Implementation is optional later; this first exercise can be completed entirely on paper.

## Lab 4 - Specify a harness state machine

**Goal:** turn a conversational process into explicit lifecycle behavior.

**Exercise:** define task states, run states, permitted transitions, and completion conditions for a draft-only document worker. Use fake tool responses; no model is required.

**Deliverable:** state diagram and a transition table.

**Acceptance:** represent waiting for input, verification failure, cancellation, budget exhaustion, and an unknown operation outcome. Distinguish candidate-ready from accepted.

**Failure to detect:** a transition from "model says done" directly to "released."

## Lab 5 - Build a context and memory experiment

**Goal:** observe how information selection affects results.

**Exercise:** prepare a synthetic corpus with current instructions, an obsolete decision, a relevant exception, irrelevant logs, and a document containing an unauthorized instruction. Define five questions with known evidence.

**Deliverable:** retrieval choices, expected citations, and a memory-write policy.

**Acceptance:** the newer scoped decision wins only where it applies; the exception is preserved; unauthorized instructions remain data; missing evidence produces an explicit gap.

**Failure to detect:** copying a malicious source instruction into a trusted summary or long-term memory.

If an approved model is used later, compare preloading with targeted retrieval under the same questions and evidence.

## Lab 6 - Design a safe tool

**Goal:** distinguish schema validity from authority.

**Exercise:** specify a synthetic `prepare_change` and `commit_change` pair. Include tenant, target revision, operation ID, approval reference, and error semantics.

**Deliverable:** input/output examples and negative cases.

**Acceptance:** reject another tenant's target, stale revision, missing approval, and same operation ID with different intent. Represent a write timeout as uncertain when appropriate.

**Failure to detect:** a valid JSON request that changes the wrong resource.

## Lab 7 - Build a protected evaluation plan

**Goal:** learn what makes a score meaningful.

**Exercise:** define at least twelve cases spanning success, failure, abstention, permission denial, stale input, and valid alternative solutions. Separate development cases from protected cases.

**Deliverable:** [evaluation plan](templates/evaluation-plan.md), grader definitions, and known-good/known-bad examples.

**Acceptance:** every criterion has an appropriate grader; hard safety gates cannot be averaged away; missing grader output is not a pass; held-out cases test disclosed requirements.

**Failure to detect:** a builder that can edit its own entire acceptance suite.

The number of cases is a teaching minimum, not a production reliability guarantee.

## Lab 8 - Compare one worker with specialized reviewers

**Goal:** test whether complexity earns its cost.

**Exercise:** compare a single-worker baseline with a builder plus focused reviewers on the same permitted task set. Initially, the experiment can use scripted traces. Live model trials require explicit setup and budget.

**Deliverable:** an ablation report covering accepted outcomes, real defects found, false positives, total cost, latency, and human minutes.

**Acceptance:** report all attempts and use the same acceptance criteria. Discuss correlated failures and reviewer disagreement.

**Failure to detect:** declaring the multi-agent design better because it produces more comments or uses more tokens.

## Lab 9 - Recovery and duplicate-action drill

**Goal:** demonstrate safe behavior around the crash gap.

**Exercise:** use a local fake service that records operations. Inject failures before intent persistence, before execution, after execution but before response, and after response but before checkpoint.

**Deliverable:** a run table explaining observed state and the safe next action at each point.

**Acceptance:** a lost response does not create a second logical effect. An operation that cannot be reconciled remains explicitly unresolved.

**Failure to detect:** assuming "no response" means "nothing happened."

Do not use a real payment, email, publishing, or production API for this exercise.

## Lab 10 - Risk and approval tabletop

**Goal:** design human involvement based on consequences.

**Exercise:** classify changes to button color, legal text, authentication, pricing, a database migration, documentation, a dependency, and a production alert rule.

**Deliverable:** mandatory review rules plus a model-assisted recommendation policy.

**Acceptance:** explain why small diffs can be high risk; bind approvals to exact artifacts; handle uncertain classification conservatively; distinguish requester from approver.

**Failure to detect:** granting a model authority to waive the rule it is supposed to apply.

## Lab 11 - Economics and service objectives

**Goal:** evaluate the whole workflow.

**Exercise:** use the illustrative comparison in chapter 10, then vary acceptance rate, reviewer cost, human effort, and retry frequency.

**Deliverable:** a small cost table and a proposed set of task-level SLIs.

**Acceptance:** include failed attempts, separate active human time from elapsed time, and avoid dividing by zero accepted outcomes. Explain why capacity gains are not automatically cash savings.

**Failure to detect:** optimizing cost per token while increasing cost per accepted result.

## Lab 12 - Capstone factory design

**Goal:** integrate the concepts without overbuilding.

**Exercise:** choose one bounded software or content task. Complete the charter, harness contract, evaluation plan, one architecture decision, and a mock release review.

**Deliverable:** a design packet and a walkthrough of one success, one rejection, and one interrupted run.

**Acceptance:** a different person can explain the inputs, trust boundaries, evidence, costs, and recovery path without relying on the original designer's chat history.

For a content task, include rights, factual accuracy, editing integrity, and final publication authority. For software, include protected acceptance checks and integration evidence.

## Suggested reading practice

For each chapter:

1. Summarize the main idea without looking.
2. Draw one boundary or lifecycle.
3. Invent a failure the design must handle.
4. Identify a source that supports the idea and one limitation of that source.
5. Explain what you would measure before adopting the pattern.

Use [the assessment](19-competency-assessment.md) after completing the core labs.

## Evidence of growing expertise

Progress is visible when we can:

- choose a simpler design and defend the choice;
- identify an unsupported claim in a compelling demonstration;
- construct a valid negative test;
- explain why an operation's result is uncertain;
- distinguish a broken evaluator from a broken agent;
- make a bounded recommendation using incomplete evidence;
- operate and improve a system without losing its authority boundaries.

Expertise remains domain-specific. Understanding a software-change factory does not automatically qualify us to automate medical, legal, financial, or other high-consequence decisions.
