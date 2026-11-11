# 02 - The AI Factory Operating Model

[Back to the index](README.md)

## From a demonstration to a capability

A demonstration shows that one task can work. A capability means a team knows which tasks are suitable, how work enters the system, what controls apply, how failures are handled, and how useful outcomes are delivered repeatedly.

The factory is therefore a **sociotechnical system**: software, data, people, roles, incentives, review mechanisms, and operating practices. Google MLOps guidance emphasizes the surrounding production system rather than just a model. Microsoft's AI Center of Excellence guidance emphasizes multidisciplinary ownership, reusable assets, intake, governance, and measured outcomes. [S02](16-sources-and-reading-guide.md#s02) [S03](16-sources-and-reading-guide.md#s03)

The operating model below is our synthesis for a software-oriented factory.

## The value stream

| Stage | Principal question | Durable output | Typical owner |
|---|---|---|---|
| Discover | Is this a worthwhile problem? | Use-case charter and baseline | Product or domain owner |
| Qualify | Can the work be safely delegated? | Scope, risk class, data permissions | Domain owner and control owners |
| Specify | What counts as an acceptable result? | Versioned task and acceptance criteria | Product and engineering |
| Prepare | Is the environment ready? | Workspace and dependency manifest | Platform or engineering |
| Execute | Can the bounded work be performed? | Candidate artifact and run record | Worker under harness control |
| Verify | Does the evidence support acceptance? | Grader results and review decisions | Verification owners |
| Promote | May this exact artifact be released? | Revision-bound approval | Authorized release owner |
| Operate | Does it remain useful and safe? | Monitoring and incident records | Service owner |
| Improve | What should change next? | Evaluated changes to the system | Cross-functional owners |
| Retire | Should this capability continue? | Decommission and retention decision | Product and service owners |

A run can stop at any stage. Rejection, abstention, and escalation can be correct outcomes.

## The factory's real product

For software work, the product is not just generated code. It is a package of:

- the change itself;
- its relationship to an agreed need;
- verification for the exact artifact;
- known limitations and remaining risks;
- installation, migration, and recovery information where relevant;
- ownership after delivery.

For a research or analysis factory, replace code with a report or decision-support artifact, but preserve evidence, provenance, permission, and acceptance.

This changes capacity planning. If code generation becomes faster while integration and review remain constrained, the factory can accumulate more unaccepted work rather than deliver more value.

## Ownership cannot be delegated to a prompt

| Accountability | Responsible human role | Automation can help with |
|---|---|---|
| Business value | Product or domain owner | Candidate prioritization and impact analysis |
| Correctness criteria | Domain and engineering owners | Draft tests and scenario expansion |
| Runtime reliability | Service/platform owner | Health checks, bounded recovery, diagnostics |
| Data permissions | Data owner and applicable governance roles | Classification and policy evaluation |
| Release authorization | Designated approver | Evidence assembly and policy checks |
| Incident response | On-call/service owner | Detection, containment proposals, evidence gathering |
| Cost | Budget owner | Attribution, forecasts, enforced limits |

A small team may combine roles. It should not combine incompatible authorities invisibly: the same autonomous worker that changes the product should not silently redefine the acceptance criteria and approve its own release.

## Work intake

A useful intake contract answers:

1. Who wants the result, and who can accept it?
2. What is the smallest valuable outcome?
3. What is outside scope?
4. Which sources, repositories, tenants, and environments are allowed?
5. Which actions are read-only, reversible, or consequential?
6. What evidence is needed?
7. What time, compute, and money limits apply?
8. What happens when inputs are missing or contradictory?

Do not treat every ticket as agent-ready. A ticket may describe a wish rather than a bounded task. A human or an authorized intake process must resolve consequential ambiguity before execution.

## Reuse and the paved path

A **paved path** is a supported, documented way of performing common work. It reduces the need for each team or agent to reinvent operational decisions.

Reusable assets can include:

- task entry points and environment recipes;
- tool contracts and permission profiles;
- approved model configurations;
- evaluation fixtures and protected holdouts;
- standard artifact and evidence schemas;
- release and incident procedures;
- domain-specific skills;
- source and data documentation.

Reuse should preserve context. A refund policy from one product is not automatically valid for another. A data-access adapter is reusable only when its identity and authorization remain correct.

## Maturity without autonomy worship

The following is a **local planning model**, not an industry certification.

| Stage | Observable ability | Exit evidence |
|---|---|---|
| Experimental | Complete isolated examples manually | A documented problem and a reproducible baseline |
| Repeatable | Run a bounded task with stable inputs and output contracts | Repeat trials and explain failures |
| Controlled | Enforce scope, budget, identity, and approvals outside prompts | Negative tests prove forbidden actions are blocked |
| Recoverable | Resume work and reconcile uncertain external outcomes | Failure-injection and restoration exercises |
| Operated | Monitor quality, reliability, cost, and human effort | SLOs, runbooks, owners, incident evidence |
| Scaled | Add workloads without losing boundaries or economics | Measured performance under realistic load and tenant separation |

Autonomy can remain low at a high maturity level. A reliable draft-generation system with strong human review may be more mature than an unrestricted agent with impressive demos.

## Three feedback loops

### Execution loop

The current worker receives tool results and corrects its approach within a task. This loop should not be allowed to change global policy.

### Engineering loop

Maintainers inspect failures, revise the harness or tools, run regression evaluations, and promote improvements. A "self-improving" agent should usually propose changes into this loop rather than overwrite its own protected evaluators.

### Business loop

The organization determines whether the capability improves the real workflow. A faster model response may not reduce a user's total time or improve the delivered result.

Separating these loops prevents local optimization from becoming uncontrolled system change.

## Knowledge lifecycle

A useful lesson moves through several states:

```text
Observation -> candidate explanation -> checked finding
            -> reviewed guidance -> published knowledge
            -> monitored use -> correction or retirement
```

A single failed trial should not immediately become a universal policy. Store the observation and its conditions first. When a lesson is promoted into team guidance, link the supporting evidence and identify an owner.

Conversely, do not keep rediscovering verified lessons in chat histories. Put stable knowledge in an accessible, versioned system with clear navigation. Allbright's shared playbooks and OpenAI's indexed account of repository knowledge both illustrate this direction. [S42](16-sources-and-reading-guide.md#s42) [S05](16-sources-and-reading-guide.md#s05)

## Measures that reveal the operating model

Use a balanced set:

- accepted outcomes per unit of time;
- total elapsed time from intake to accepted delivery;
- active human minutes, including supervision and rework;
- cost per accepted outcome, including failed attempts;
- escaped defects and incident severity;
- percentage of work rejected or escalated, with reasons;
- recovery success and duplicate-action incidents;
- policy violations and attempted unauthorized actions;
- adoption and user-perceived value.

Do not interpret a low escalation rate as automatically good. It may mean the system is confidently proceeding when it should stop.

## Portfolio selection

Good early candidates tend to have bounded scope, accessible evidence, reversible outputs, an available reference or reviewer, and a meaningful baseline.

Poor first candidates combine unclear goals, hidden business context, broad write permissions, hard-to-observe outcomes, and high-impact irreversible actions.

An early factory task could prepare a proposed documentation correction or a small software patch with tests. A poor initial task would grant an agent unsupervised control over a production estate and ask it to "make everything better."

## Questions before scaling

Can a new operator reproduce a run? Can an auditor identify which inputs and permissions were used? Can a user understand what was accepted and what remains uncertain? Can the service owner stop new work without losing existing evidence? Can the budget owner explain the marginal cost of one additional useful outcome?

If these questions cannot be answered, adding more workers scales ambiguity as well as throughput.
