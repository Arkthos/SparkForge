# Test and acceptance strategy

The active [scenario matrix](ACCEPTANCE_MATRIX.csv) defines **100 planned scenarios** across 50 work packages and 41 requirements. Scenario IDs TC-101 through TC-200 are planning identities, not a claim of 100 executed tests. Earlier TC-001 through TC-096 remain in the archived baseline for historical evidence.

## Progressive evidence

| Layer | Required evidence | Cannot establish |
|---|---|---|
| Planning/governance | Valid task graph, coverage, links, archive integrity and lifecycle updates | Product behavior, genuine approval or real platform fit |
| Contract/unit | Side-effect-free schemas, finite bounds, transition guards and known-bad inputs | Actual host mediation or OS confinement |
| Synthetic integration | Owned file edits/processes, fake-host task receipts, repair/drift/recovery cases | Model-selected code/repair or real reviewer independence |
| Installed host | Exact package discovery/relocation/lifecycle and observed dispatch/recovery | Another host/build/environment |
| Model-driven behavioral evaluation | Actual roles on representative tasks, protected rubric, retained failures and usage | Universal correctness, production release or a fabricated human decision |
| Domain/control acceptance | Actual accountable review of selected outputs and boundary probes | Unperformed transfer/submission or all possible adversarial cases |

## Test development rules

Protect the behavioral oracle and evaluate known-bad controls. Include missing/malformed/stale/foreign/duplicate/reordered results, candidate changes, same-byte check reruns, wrong-role results, cancelled/revoked scope, exhausted resources, no-progress repair, semantic drift, crashes and unknown effects. A green happy path is insufficient.

Generated tests must detect seeded defects and observe behavior. Avoid tests that simply mirror current implementation or check incidental internal names. Keep source-neutral test fixtures synthetic and owned. Do not invoke live collectors, inspect credentials, call a model or migrate real state as part of the standard suite.

Run focused checks during each change. Run full relevant regression before integration when shared/runtime behavior changes; planning/CI changes receive their own negative fixtures. Preserve v1 tests until a separately scoped compatibility change is justified. Removing the disconnected preview intentionally retires its 40 Node checks and browser harness; it does not weaken native factory acceptance.

## Commands and platform limits

Use [README setup](../../README.md#validate-locally) for Python 3.12+ and repo-local Markdown/image dependencies. Full command: `python -B -m unittest discover -s tests` with PYTHONPATH configured. Native-only: `python -B -m unittest discover -s tests -p 'test_native_*.py'`. Planning: `python -B scripts/validate_plan.py --base HEAD` before commit and `HEAD~` after commit. Whitespace: `git diff --check`.

CI runs Python checks on Linux and Windows to expose platform-specific cases; an unavailable PowerShell/symlink privilege stays an explicit skip. It does not run real corp/acro models or deployment. Local Linux review previously observed 30 platform-dependent skips; current results belong in the validation ledger, not hard-coded as an acceptance target.

## Outcome and gate semantics

PASS means the expected current evidence was observed. FAIL means an executed check found a violation. BLOCKED means a prerequisite/unknown effect prevents progress. NOT_ASSESSED means it was not evaluated. A skipped, pending, missing, truncated or timed-out required check is not a pass.

The coordinator requires the whole current check/reviewer/controller inventory before readiness. Evidence carries intent/plan/candidate/task/attempt/oracle/source bindings and real producer context where available. Different actor strings or test labels do not establish authentic origin.

Each milestone uses the [evaluation plan](EVALUATION_PLAN.md) and task-specific acceptance. Installed P6 journeys and independently accepted outputs are separate from synthetic P4 success. Learning promotion, optional parallelism and acro need their own later evidence.
