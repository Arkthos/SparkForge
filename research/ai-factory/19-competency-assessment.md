# 19 - Competency Assessment and Answer Guidance

[Back to the index](README.md)

## How to use this

Answer without looking at the guidance first. Use diagrams, concrete failure cases, and evidence references. A correct vocabulary definition is useful, but the main test is whether you can make a defensible engineering decision.

This is a learning rubric, not a professional certification or a production authorization.

## Foundations

### 1. A team has a model API, a task runner, and five role prompts. Does it have a factory?

**Answer guidance:** not enough information. Ask about intake, contracts, environment, state, verification, ownership, release, and operations. A collection of components is not evidence of repeatable accepted delivery.

### 2. When is a workflow preferable to an agent?

**Answer guidance:** when the process is known and predetermined control improves reliability or cost. Compare against an agent on representative tasks rather than selecting autonomy by fashion.

### 3. Name three meanings of harness.

**Answer guidance:** agent execution, evaluation, and developer environment. Explain their different responsibilities. Mentioning Harness the commercial platform is useful disambiguation, not another generic mechanism.

### 4. Does updating a project playbook train the model?

**Answer guidance:** not ordinarily. It changes external context or application behavior. Parameter training is a different process. Future improvement depends on retrieval and use of the updated material.

## Context and tools

### 5. A model supports a huge context window. Why not load every document?

**Answer guidance:** relevance, effective information use, cost, latency, privacy, conflicting versions, and output reserve. Measure whether targeted retrieval performs better; do not assume one universal answer.

### 6. Why can a valid citation still be misleading?

**Answer guidance:** the source may not support the claim, may describe a different setting, may be outdated, or may report an unverified claim. Check claim scope and qualifiers, not only URL existence.

### 7. Is a skill the same as a subagent?

**Answer guidance:** a skill is procedural content and optional resources; a subagent is delegated execution. Loading a skill need not create a separate worker, identity, or context.

### 8. What does a JSON schema fail to validate?

**Answer guidance:** authority, correct target, current revision, business meaning, truth, and actual outcome. Shape validation is one layer.

### 9. What does MCP not guarantee?

**Answer guidance:** trustworthy servers, proper user consent, authorized data flow, safe side effects, factual correctness, or implementation compliance simply because the protocol is used.

### 10. An agent card advertises deployment capability. May we invoke it?

**Answer guidance:** only after establishing identity, delegated authority, target scope, data handling, cost, and approval requirements. Advertisement is not permission.

## Reliability

### 11. A write times out. Should the harness retry?

**Answer guidance:** first classify whether the effect may have occurred. Use operation status or a verified idempotency contract. If unresolved, reconcile or escalate; do not blindly create a new logical action.

### 12. Why is a checkpoint not an exactly-once guarantee?

**Answer guidance:** the remote service can commit an effect before the local result is durable. Exactly-once claims require a complete service and transaction model, not just local state.

### 13. Does a Git worktree isolate all agent activity?

**Answer guidance:** it separates working files, but may still share databases, ports, credentials, caches, budget, or external resources.

### 14. What happens when a worker's lease expires?

**Answer guidance:** the old worker must not be able to commit stale results after ownership changes. Explain fencing or equivalent version checks at the state-changing boundary.

### 15. Does cancellation undo work?

**Answer guidance:** no. It can stop admission or request interruption; completed effects may need compensation and some cannot be reversed.

## Verification

### 16. The builder wrote both the implementation and all tests. Is passing enough?

**Answer guidance:** it is useful evidence but can share the same mistaken assumption. Preserve independent acceptance, regression, policy, and outcome checks.

### 17. Why can two different model reviewers miss the same defect?

**Answer guidance:** correlated training, reasoning patterns, shared misleading context, incomplete criteria, and similar tool limitations. Different names do not prove independent errors.

### 18. How should a model judge be calibrated?

**Answer guidance:** compare criterion-level decisions against qualified reference judgments, inspect false acceptance/rejection, test order/verbosity sensitivity, and recheck after judge or rubric changes.

### 19. What is the difference between `pass@k` and consistent success across attempts?

**Answer guidance:** finding at least one successful attempt is different from succeeding reliably every time. The metric must match whether the product can select among attempts or must deliver dependable unattended behavior.

### 20. The evaluation reports no failures in a small set. What can we claim?

**Answer guidance:** only the observed result under that set and configuration, with uncertainty. Do not infer zero failure probability or broad production reliability.

### 21. When should a trajectory be graded instead of just the final artifact?

**Answer guidance:** for necessary process or safety invariants such as data access, forbidden operations, budget, and approvals. Avoid forcing one exact strategy where multiple safe outcomes are valid.

### 22. A candidate changed after the tests. Can the old results authorize it?

**Answer guidance:** not without an explicit valid evidence-reuse policy and appropriate rechecking. The default is to bind evidence to the exact artifact and invalidate stale acceptance.

## Authority and operations

### 23. Can a risk-classification agent waive a mandatory human-review rule?

**Answer guidance:** no. It can inform routing within an approved policy. It must not grant itself or another worker broader authority.

### 24. Why can a one-line legal notice edit be riskier than a large refactor?

**Answer guidance:** consequences, not line count, determine risk. Legal commitments, consent, pricing, or accessibility can be affected by tiny changes.

### 25. What belongs in an approval request?

**Answer guidance:** exact action, target/account/environment, artifact revision, evidence, known limitations, effects, and validity constraints. Explain what happens if inputs change.

### 26. Which costs belong in cost per accepted outcome?

**Answer guidance:** all relevant attempts, reviewers, tools, infrastructure, retrieval, human effort, rework, and operating overhead. No accepted outcomes means the ratio is undefined, not free.

### 27. What is the difference between uptime and useful reliability?

**Answer guidance:** a service can respond successfully while producing incorrect or unauthorized results. Measure semantic quality, accepted outcomes, and operational safety separately from infrastructure availability.

### 28. Why should the factory's own improvements pass through review?

**Answer guidance:** self-modified prompts, skills, policies, or evaluators can introduce regressions or promote poisoned context. Separate execution feedback from controlled engineering changes.

## Reading the supplied references

### 29. What needs qualification in Allbright's artifact separation?

**Answer guidance:** stable versus volatile and control versus data do not align perfectly with main repo versus sub-repo. Some generated artifacts are durable evidence; deleting them can destroy reproducibility. Sensitive material may not belong in Git at all.

### 30. What specifically occurs around 14:18 in the Risco video?

**Answer guidance:** the content-factory example concerns AI-assisted editing. The surrounding process includes cleanup, assembly, design/transitions, and thumbnail work. The creator says final review/upload remains manual. This is not evidence of fully autonomous publishing.

## Design defense

Choose a bounded use case and defend these decisions:

- why AI is necessary;
- why the proposed autonomy level is appropriate;
- where authoritative state lives;
- which actions are allowed;
- how output is independently checked;
- what happens after a lost response;
- how costs and human effort are measured;
- which component would be removed first if it did not earn its complexity.

An answer should name evidence that could change the decision.

## Competency rubric

| Dimension | Emerging | Working competence | Strong competence |
|---|---|---|---|
| Conceptual precision | Repeats labels | Distinguishes responsibilities | Explains ambiguous terminology and tradeoffs |
| Architecture | Draws components | Defines contracts and ownership | Justifies minimal boundaries and replacement paths |
| Verification | Lists tests | Designs suitable graders and negative cases | Diagnoses evaluator flaws and uncertainty |
| Reliability | Describes retries | Handles idempotency and recovery | Explains crash gaps, concurrency, and unresolved state |
| Authority | Adds a warning prompt | Separates identity, permission, and approval | Demonstrates enforceable boundaries and revocation |
| Economics | Counts tokens | Measures whole-workflow cost and effort | Designs comparisons and explains causal limitations |
| Operations | Assumes success | Defines monitoring and response | Can hand off, contain, recover, and learn from incidents |
| Evidence literacy | Trusts compelling examples | Preserves source scope and limits | Identifies contradictory evidence and updates conclusions |

Do not average away a critical weakness in authority or recovery because the architecture explanation is polished.

## Readiness boundary

We are ready to design a first experiment when we can produce a bounded charter, a defensible architecture, and an evaluation plan.

We are ready to operate that experiment only after its controls and recovery behavior have been exercised in the chosen environment.

Production readiness requires additional evidence and explicit authority. This corpus supplies a foundation for that work, not a shortcut around it.
