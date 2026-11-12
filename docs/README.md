# Documentation map

Read only the context needed for the current task, using this ownership map. Current owner direction can change any plan; record the resulting decision and affected work rather than silently following stale prose.

| Question | Canonical record |
|---|---|
| What works now and what is next? | [Project status](PROJECT_STATUS.md) |
| What are we building and what is excluded? | [Requirements](PRODUCT_REQUIREMENTS.md) |
| Which milestone and dependencies come first? | [Roadmap](ROADMAP.md) and [active backlog](IMPLEMENTATION_BACKLOG.csv) |
| Exactly how should a work package be implemented and accepted? | [Detailed implementation plan](IMPLEMENTATION_PLAN.md) |
| How do the agents and deterministic runtime cooperate? | [Architecture](design/ARCHITECTURE.md), [agent contracts](design/AGENT_CONTRACTS.md), [data/state](design/DATA_AND_STATE.md) |
| When does a human need to decide? | [Human decisions](design/HUMAN_DECISIONS.md) |
| Which interfaces and design decisions are authoritative? | [Contracts](design/CONTRACTS.md), [decision register](design/DECISIONS.md) |
| How does Copilot start and continue? | [Handoff](development/COPILOT_HANDOFF.md), [first task](development/FIRST_TASK.md), [contributor guide](../CONTRIBUTING.md) |
| How do we prove a milestone? | [Test strategy](engineering/TEST_STRATEGY.md), [scenario matrix](engineering/ACCEPTANCE_MATRIX.csv), [evaluation plan](engineering/EVALUATION_PLAN.md) |
| What was actually tested? | [Validation history](VALIDATION_HISTORY.md) and [append-only cycles](engineering/cycles/) |
| What should the first complete factory journey do? | [First factory slice](specs/FIRST_FACTORY_SLICE.md) |
| What capabilities must a native host supply? | [Host adapter](integration/HOST_ADAPTER.md) |
| What does the current v1 package actually do? | [Native factory guide](engineering/NATIVE_FACTORY.md), [native knowledge guide](engineering/NATIVE_KNOWLEDGE.md), [v1 slice](specs/NATIVE_FACTORY_SLICE.md) |
| What must be checked in corp and acro? | [Environment acceptance](engineering/ENVIRONMENT_ACCEPTANCE.md) |
| What research can inform implementation? | [Research index](../research/README.md), [reuse choices](development/PRIOR_ART_APPLICATION.md), [provenance](RESEARCH_PROVENANCE.md) |
| What changed in the cleanup? | [Cleanup ledger](development/REPOSITORY_CLEANUP.md) and [archive](archive/README.md) |

Requirements own desired behavior; the backlog owns task state; the plan owns task execution instructions; code and actual check receipts establish observed behavior. A planned acceptance scenario is not an executed test. Role documents are design contracts until actual packaging and host-dispatch work ships them.
