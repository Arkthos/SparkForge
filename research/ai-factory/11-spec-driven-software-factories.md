# 11 - Specification-Driven Software Factories

[Back to the index](README.md)

## The specification is an engineering interface

A specification turns intent into an inspectable contract. It should say what changes, what must remain true, what constraints apply, and how the result will be judged.

Specification-driven development does not mean producing the longest possible document. It means making the consequential decisions explicit enough that implementation and verification can proceed without guessing.

The supplied video separates a specification writer from a builder. StrongDM describes a more aggressive software factory driven by specifications and scenarios. Allbright describes a shared operational stack and team playbooks. These approaches overlap, but they are not the same methodology. [S48](16-sources-and-reading-guide.md#s48) [S04](16-sources-and-reading-guide.md#s04) [S42](16-sources-and-reading-guide.md#s42)

## Four specification layers

| Layer | Question | Example |
|---|---|---|
| User outcome | What should the user be able to do? | Export the filtered list they are currently viewing |
| Domain invariants | What must always remain true? | Export never includes another tenant's rows |
| Engineering constraints | What boundaries must implementation respect? | Preserve the public API and supported file format |
| Acceptance evidence | How will we know? | Filter, tenant, encoding, and regression scenarios |

A model can draft these layers. The relevant owner still needs to confirm consequential business decisions and unresolved ambiguity.

## What belongs in a task specification

- Goal and user context.
- In-scope and out-of-scope behavior.
- Current behavior and evidence of the problem.
- Affected interfaces and dependencies.
- Data and permission boundaries.
- Acceptance criteria, including negative cases.
- Nonfunctional requirements such as latency or accessibility when relevant.
- Migration and compatibility requirements.
- Verification plan.
- Rollout and recovery considerations.
- Explicit open decisions.

Do not hide unresolved questions behind a polished architecture paragraph.

## Executable specifications

Some requirements can become automated checks:

- input/output examples;
- invariants and property-based tests;
- API contract tests;
- database-state assertions;
- accessibility checks;
- performance bounds;
- allowed-operation policies.

Others require judgment: whether the interaction is understandable, whether the change solves the right problem, or whether the proposed risk is acceptable.

The goal is not to force every requirement into one test framework. It is to make each requirement's verification method explicit.

## Test-driven development

The test-first sequence is useful:

1. Express a required behavior.
2. Confirm that the current implementation fails for the intended reason.
3. Implement the smallest suitable change.
4. Confirm the new behavior and relevant regressions.
5. Refactor while preserving the contract.

A failing test caused by a broken environment does not establish a product defect. A passing test that checks only the implementation's own assumptions does not establish user acceptance.

The video's builder follows a test-first pattern. The missing question to add is who owns independent acceptance coverage. [S48](16-sources-and-reading-guide.md#s48)

## Scenarios and the test oracle problem

A **scenario** describes a meaningful situation and expected behavior. A **test oracle** is the mechanism that determines whether the result is correct.

An oracle may be:

- an exact state assertion;
- a reference implementation;
- a domain invariant;
- a property that must remain true under a transformation;
- a rubric applied by a qualified reviewer;
- a calibrated model judge.

The oracle is often the hardest part of a factory. Generating code is not enough if no one can reliably distinguish a correct solution from a convincing shortcut.

## StrongDM's factory: useful ideas and limits

StrongDM reports non-interactive development driven by specifications and scenarios, with behavioral clones of third-party services called a Digital Twin Universe. It also describes an intentionally provocative operating charter that excludes human code writing and code review. [S04](16-sources-and-reading-guide.md#s04)

Transferable ideas:

- evaluate user-visible behavior rather than only superficial test completion;
- protect evaluation material from easy modification by the builder;
- simulate important external-service behavior;
- expand failure coverage beyond convenient happy paths;
- inspect whether agents are exploiting weak acceptance criteria.

Do not adopt the following as established conclusions:

- that human code review is unnecessary for every workload;
- that a twin fully represents production;
- that an LLM satisfaction score is objective truth;
- that high token expenditure is itself progress;
- that the reported approach has independently demonstrated universal economics.

The distinction between development tests and held-out behavioral scenarios is useful. Renaming a weak test "scenario" does not make it strong.

## Repository legibility

Agents and humans need to find:

- the architecture;
- supported commands;
- current requirements;
- module ownership;
- important invariants;
- tests and fixtures;
- previous decisions;
- known limitations.

The indexed portions of OpenAI's harness-engineering report describe repository knowledge as a system of record and a short instruction file as a map to deeper documentation. Direct access to the full article was blocked during this review, so this is a limited source-backed observation, not a full reconstruction of its method. [S05](16-sources-and-reading-guide.md#s05)

A useful repository is not one with the largest instruction file. It is one where reliable information is discoverable and maintained.

## Enforcement levels

| Mechanism | Strength | Limitation |
|---|---|---|
| Prompt or playbook | Explains desired behavior | Can be ignored or misunderstood |
| Local formatter/linter | Fast deterministic feedback | Covers only configured properties |
| Pre-commit hook | Catches common issues early | Local coverage and execution can vary |
| CI gate | Consistent checks on submitted revisions | Can be misconfigured or incomplete |
| Protected evaluator | Independent acceptance evidence | Depends on coverage and integrity |
| Release control | Restricts promotion authority | Needs correct identity and revision binding |
| Runtime monitoring | Detects real-world failures | Often detects after some impact |

Use these as complementary layers. The pre-commit project documents a practical framework for shared hooks, and also describes CI usage. [S46](16-sources-and-reading-guide.md#s46)

## Code review in an agentic factory

Separate review purposes:

- correctness;
- architecture and maintainability;
- security and privacy;
- usability and accessibility;
- operational readiness;
- compliance with the agreed scope.

Some checks should be automated deterministically. Some benefit from AI-assisted analysis. Some require an accountable human.

The decision to reduce manual code review should follow evidence about the task class, verifier coverage, failure costs, and operational recovery. It should not be a philosophical requirement of having a factory.

Human involvement can move earlier toward specification and system design while remaining necessary at certain release boundaries.

## Integration is its own stage

Two changes can pass independently and fail together. A reviewer can approve a patch whose base has changed. A migration can conflict with a concurrent deployment.

Before promotion:

- establish the exact integrated revision;
- rerun required checks in that context;
- resolve dependency and schema compatibility;
- invalidate stale approvals when needed;
- preserve a rollback or forward-recovery plan.

An agent's isolated branch is a candidate workspace, not proof of integration.

## A disciplined change packet

A useful output packet contains:

1. The requested outcome and scope.
2. The exact change.
3. Why the implementation fits the architecture.
4. Evidence for each acceptance criterion.
5. Known limitations and skipped checks.
6. Data, security, and operational implications.
7. A promotion decision or explicit pending approval.

This packet can be produced largely by automation, but its assertions must be grounded in actual results.

## Preventing factory-generated technical debt

Watch for:

- duplicated utilities created because context was not retrieved;
- unnecessary abstraction added to satisfy vague requests;
- test weakening to make a task pass;
- copied obsolete patterns;
- dependencies added without operational justification;
- repeated local fixes that hide a systemic problem;
- stale generated documentation;
- unowned background services and workflows.

Use bounded cleanup and architecture checks, but evaluate those changes like any other change. A cleanup agent should not be exempt from scope or release controls.

## The product is not the factory

An agentic factory can build ordinary deterministic software. An AI-enabled product can be built with a mostly conventional development process. The two dimensions are independent.

This matters for evaluation: we may need to evaluate the factory that builds the application and separately evaluate an agent inside the application.

## Design lesson

Invest in a precise specification, a suitable environment, and trustworthy verification before maximizing unattended execution. Those investments benefit human engineers too; they are not merely accommodations for weak models.
