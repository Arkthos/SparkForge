# Contributing

Read [AGENTS.md](AGENTS.md), [current status](docs/PROJECT_STATUS.md) and the [Copilot handoff](docs/development/COPILOT_HANDOFF.md). Choose the first ready task in the active backlog whose prerequisites are done. The detailed plan defines scope, proposed paths, positive acceptance and negative controls.

## Work loop

1. Inspect branch, HEAD, dirty files and pending operations. Preserve unrelated work.
2. State the selected work package, intended behavior, owned paths, required evidence and any material unknown.
3. Implement one complete slice with behavior/negative tests. Reuse actual code; do not add empty future modules.
4. Run focused tests, inspect real failures, fix them and rerun affected evidence. Run shared regressions before integration.
5. Obtain actual independent review when the task/gate requires it. If unavailable, say so; do not invent a reviewer or complete the gated acceptance.
6. Update current status, backlog, roadmap and validation history; append a new cycle from the template. Include failed attempts, fixes, skipped/unexecuted checks and the exact next task.
7. Validate the whole change boundary and staged payload, commit with the required trailer, and publish through the owner's selected branch/PR scope. Do not force push or deploy.

Use the [README setup](README.md#validate-locally). Before committing run `python -B scripts/validate_plan.py --base HEAD` and `git diff --check`; afterward compare to `HEAD~`. Do not claim a clean-tree HEAD check establishes lifecycle completeness for the prior commit.

## Compatibility and data

The coordinated runtime is planned alongside assisted v1. Existing `factory.py`/`knowledge.py` interfaces and tests remain supported until a separately scoped migration. Private corp/acro sources, credentials, real profiles, journals and raw transcripts stay outside Git. Preserve research byte inventories. Do not select a public license or invent CODEOWNERS/organization policy.

## Definition of done

Deliverables work; accepted behavior and negative controls have observed evidence; required checks/reviews are current; no unresolved required failure or effect is concealed; docs and continuation state match code; the next unblocked task is explicit. Planned scenarios, mocks and metadata keep their own evidence class.
