# Test and acceptance strategy

The [requirements](../PRODUCT_REQUIREMENTS.md) and
[acceptance matrix](ACCEPTANCE_MATRIX.csv) define **96 planned scenarios**
covering 31 requirements. A mapping is not an implemented feature, executed
test or pass. The native slice has executable synthetic/contract/integration
coverage; deployed-host and real user acceptance remain separate.

## Evidence classes

| Class | Can establish | Cannot substitute for |
|---|---|---|
| Documentation | Traceability, links and lifecycle consistency | Runtime behavior or genuine approval |
| Unit/contract | Deterministic behavior and rejection of negative fixtures | Authenticated identities or OS confinement |
| Integration | Real owned helpers/processes cooperating on synthetic inputs | Actual provider/model or deployment acceptance |
| Browser fixture | Specified interactions on synthetic tab-local data | A real domain user's acceptance |
| Native metadata | The selected client discovers exact package resources | A model-driven workflow or full installed lifecycle |
| Live-host evaluation | A specifically authorized selected-host observation | Another environment or organizational release |
| Manual release | Actual owner/reviewer decisions for the exact artifact | Unperformed submission or deployment |

Use the smallest relevant existing command, then escalate when shared behavior
or a failure requires it:

```powershell
$env:PYTHONPATH = (Resolve-Path 'research_tools\.validation-deps').Path
python -B -m unittest discover -s tests
node --test tests\test_preview_model.cjs tests\test_preview_assets.cjs
python -B scripts\validate_plan.py --base HEAD
```

The full suite includes the research utilities and their declared local
Markdown/image dependencies; see [tooling setup](../../research_tools/README.md).
The native package tests do not acquire those dependencies. Live collectors,
real source corpora and original checkpoints are not inputs to this suite.

The [operating model](DEVELOPMENT_OPERATING_MODEL.md) covers the initial root
commit's special documentation check. Actual command outcomes belong in
[validation history](../VALIDATION_HISTORY.md), not in this scenario inventory.

## Acceptance discipline

Define behavior, required checks, reviewers and finite resources before the
operation. Include real failure/repair cases, missing markers, malformed and
foreign evidence, stale revisions, changed candidates, rejected approval,
resource exhaustion, cancellation and uncertain outcomes.

Generated tests cannot alone accept their generator. Protect independent
criteria and review control-plane changes independently. Do not remove failures,
weaken expected outputs, change skip rules or refresh a review token to relabel
an older opinion.

The current helper's decisions and reviews are assertions. The native workflow
forbids workers from manufacturing them; actual authentication and isolation
remain host/operator responsibilities. `CANDIDATE_VERIFIED` is narrow local
inventory completeness and always retains its human/host/publication limits.

## Results and limitations

PASS requires the expected current evidence. FAIL means an executed check
observed a violation. BLOCKED means a known prerequisite or unresolved effect
prevents progress. NOT_ASSESSED means assessment/comparison has not occurred.
Skipped, partial, missing, timed-out or unexecuted cases are not passes.

Keep all relevant attempts and corrections. A passing process exit cannot hide
an incomplete reporter. A mock denial proves the fixture behavior, not real
host enforcement. Product budgets/SLOs are not inferred from short engineering
test bounds.

Tests use explicitly owned synthetic directories. Do not substitute real
records, inspect credentials, change privileges or silently move fixtures to a
different storage/profile. Unknown process scope preserves the affected fixture
for reconciliation rather than broad cleanup.

Private historical checks, source reads and reviewer tokens are not imported
as acceptance of the changed publication candidate. The published self-check
example uses synthetic references and still requires its own actual review.

The two metadata profiles, hosted research and GitHub publication do not close
live wiki, model-driven journeys, installed lifecycle, Corp/Acro qualification,
security assurance or governed learning promotion.
