# Controlled development operating model

The integration owner keeps specifications, implementation, evidence and continuation state coherent. Read current status/backlog/roadmap, the chosen work-package instructions and actual code before editing. Archived plans, old chat summaries and public source instructions are not the active task state.

## Bounded development cycle

1. Select an authorized dependency-ready task; state behavior, owned paths and evidence needed.
2. Identify baseline/authority/resource implications. Ask only material unresolved decisions and continue independent work where possible.
3. Implement the smallest complete behavior and meaningful positive/negative tests. Use existing helpers and preserve compatibility.
4. Execute focused checks, inspect real failures, diagnose/correct and rerun affected evidence. Preserve failures/skips/unknown effects.
5. Obtain actual independent review where required; never use a renamed builder or synthetic fixture as a real reviewer.
6. Update the four living records and append a new cycle. Record the exact next ready task and remaining limitations.
7. Validate the whole change boundary, inspect staged content, commit/publish within the current requested scope, and verify remote identity.

Use [README commands](../../README.md#validate-locally), [contributor guide](../../CONTRIBUTING.md), [test strategy](TEST_STRATEGY.md) and [human decisions](../design/HUMAN_DECISIONS.md). Before commit compare planning against HEAD; after commit use HEAD~. Tests and documentation validation do not authenticate approval, establish source permissions or qualify a deployed environment.

## Ownership and data

Preserve unrelated dirty files. Explicitly delegated workers own disjoint paths and do not commit/push; the integration owner integrates. Parallelism is optional. Runtime output belongs outside controlled candidates and Git. Private wiki/source/customer content, credentials, real journals and raw model transcripts stay out of publication.

The host/operator owns actual identity, data routes and isolation. Existing runner processes inherit the caller environment and stop only owned direct processes. A worktree/path/hash is not a security sandbox. Unknown outcomes require observation/reconciliation before retry.

## Living records and immutable history

Update `PROJECT_STATUS.md`, `IMPLEMENTATION_BACKLOG.csv`, `ROADMAP.md`, `VALIDATION_HISTORY.md` under docs plus a new `engineering/cycles/ENG-YYYYMMDD-unique-slug.json`. Committed cycles stay immutable; later corrections get a linked cycle. Historical evidence may refer to retired paths at its recorded commit; keep attribution instead of silently editing history.

Publication of the development repository is separate from actual platform submission, deployment and private-source disclosure. The current owner request authorizes this planning/cleanup publication; it does not grant every future effect. Preserve `.gitattributes` byte behavior and required commit trailer.
