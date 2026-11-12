# Quality, testing, evaluation, and correction

**Research baseline:** 2026-11-05. **Public edition:** 2026-11-12.
The historical study read selected documentation, code, and test source; it
did not install candidates or execute their tests or models.

Test writing, execution, result analysis, review, and feedback are distinct
capabilities. They need not be separate agents, and deterministic work should
not become model work merely to make the diagram symmetrical. A known test
command, schema validator, or selected scanner can run as ordinary code.

## Evidence is layered

| Layer | What the evidence can support | What it cannot establish alone |
|---|---|---|
| Package/schema validation | Required fields, references, paths, declared structure | Useful behavior or correct domain logic |
| Static checking | Selected syntax, types, style, patterns, secret-like strings | Complete security or runtime correctness |
| Unit tests | Bounded behavior under the exercised conditions | Integration of every component |
| Integration/component tests | Contracts between exercised pieces | Real service acceptance when all external surfaces are mocked |
| Behavioral evaluations | Skill/agent behavior on the selected cases and rubrics | Universal reliability or external approval |
| Independent review | Additional defects, missing evidence, scope drift | A substitute for meaningful executed checks |
| User acceptance | Whether the outcome solves the accepted need | Permission to bypass maintainers or distribution decisions |

The [factory evaluation chapter](../../ai-factory/07-evaluation-and-verification.md)
provides the foundations. The mechanisms below add implementation-level and
route-specific distinctions.

## 1. Test design and an explicit evidence oracle

[TEA](CATALOG.md#bmad-tea) distinguishes risk-based planning, generation,
test-quality review, nonfunctional evidence, behavioral evaluation, and
requirements traceability. Its documented red mode is different from merely
expanding coverage of existing behavior.

The [trace skill](EVIDENCE.md#tea-trace) makes its oracle choices visible:
formal requirements, contract/spec artifacts, permitted external pointers,
and optionally synthetic journeys inferred from source. It also declares
scope-bound output files and depends on sibling knowledge/contracts and
BMad configuration.

Inferred journeys can expose missing requirements; they must not silently
replace the requester-accepted brief. A generated test that simply confirms
what the current implementation happens to do has no independent authority
over the intended behavior. Similarly, a waiver needs a real authorized
decision and reason, not a convenient model output that turns a gate green.

[Superpowers TDD](EVIDENCE.md#superpowers-tdd) emphasizes observing a
meaningful failure before the fix and checking why the failure occurred.
That is useful discipline. Its blanket delete-code-written-before-tests rule
should not be imported into maintenance of legitimate user-owned work.
Red/green/refactor does not require discarding an existing component.

## 2. Executing a check is not accepting the product

The [SSSF runner](EVIDENCE.md#sssf-run-acceptance) is a concrete source example:
phase completion and the caller's whole-run acceptance condition are distinct.
A runner can successfully execute tests that report failed assertions.

A truthful report distinguishes:

- a command ran and its selected assertions passed;
- a command ran and assertions failed;
- a required dependency, host, or connector prevented execution;
- a check was intentionally omitted or skipped;
- evidence is missing, stale, from another revision, or attributed to another
  job; and
- completion of an external operation is uncertain.

A repair agent needs that classification. An access denial is not a product
defect to fix by editing code, and it does not authorize another account.
Missing infrastructure must not silently reduce the required check inventory.

[Pester](CATALOG.md#pester) offers deterministic PowerShell assertions,
mocking, coverage, and machine-readable integration. Mocks can keep a unit
test from affecting a real service, and also limit what it proves. Installed
Windows versions, the source pin, and release packages are distinct artifacts.
No Pester installation or candidate test execution occurred in the study.

## 3. Waza: assess each route separately

[Waza](CATALOG.md#waza) targets skills, agents, workflows, repository/CLI/MCP
scenarios, trials, graders, and evidence. The selected paths do not collapse
into a single "supports Copilot" guarantee.

### Ordinary CLI selection

The [client connection code](EVIDENCE.md#waza-cli) uses an explicit usable
`COPILOT_CLI_PATH` override. Otherwise it selects the embedded CLI and refuses
a silent fallback to an arbitrary executable on `PATH`.

Explicit selection is useful. Accepting a path still does not prove that the
selected wrapper or binary supports the expected protocol, permissions,
identity, plugins, lifecycle, and cancellation semantics.

### Isolated evidence judging

The [evidence grader](EVIDENCE.md#waza-judge) requires frozen evidence and an
isolated executor rather than the actor's own context. It records evidence and
delivery identities, labels the delivered material as untrusted evidence
rather than instructions, and constrains the judge to verdict tools.

It also rejects invalid or duplicate callbacks, execution errors, policy
denials, cancellation, and missing verdicts. Absence of a verdict does not
become approval. This is materially stronger than accepting any favorable
prose from another model.

The boundary remains limited: an isolated judge can be wrong, the rubric can
be poor, and evidence selection can omit the relevant failure. Identity and
callback checks do not establish semantic correctness by themselves.

### The judge runtime is narrower than the ordinary override

The [judge runtime resolver](EVIDENCE.md#waza-judge-runtime) requires an
absolute native executable and verifies that an override refers to the same
tested installation as the pinned embedded runtime. A matching version string
or arbitrary custom wrapper is not enough. Owned-transport cleanup is also
part of that selected implementation.

That route's restriction should neither be ignored nor generalized to all
Waza execution. Where the approved host cannot satisfy it, the evidence
judge route is unqualified; silently switching runtimes is not a solution.

### Attribution and platform-specific assertions

The [reviewed test source](EVIDENCE.md#waza-evidence-tests) checks foreign
evaluation/task/run/attempt identities, digest tampering, and preservation of
the original result file. It also expects preserved evidence-snapshot help to
describe Linux/macOS support.

These are assertions that were read, not passing tests observed during the
study. The help assertion concerns a particular snapshot route, not every
Waza feature on Windows.

### Text-only execution has a smaller capability envelope

The [text-only runner contract](EVIDENCE.md#waza-text-route) specifies explicit
execution consent and model selection, disabled tools/skills/discovery, and
owned transport cleanup. Fixtures, file inputs, MCP, and agent definitions
are excluded from that route.

A successful text-only trial would therefore not qualify a tool-using
factory, live connector, or component installation. Cancellation, synthetic
process tests, and live model behavior remain different evidence levels.

| Hypothetical result | Honest interpretation |
|---|---|
| Mock executor passes | The selected mock path and checks worked |
| Synthetic stdio/control check passes | The exercised process/protocol contract behaved as expected |
| Live text-only trial passes | That constrained text route worked for those cases and the selected model |
| Live skill/component trial passes | The exercised host and capability set worked for the selected cases |
| A release binary works | That binary worked, not necessarily another source revision, image, or extension |

These are interpretation rules, **not results obtained here**.

## 4. Promptfoo: useful evaluation structure, distinct data routes

[Promptfoo](CATALOG.md#promptfoo) contributes configurable test matrices,
rubrics, assertions, provider comparisons, regressions, and adversarial
evaluation. Its [data-handling guide](EVIDENCE.md#promptfoo-privacy) is needed
to interpret broad privacy statements in the README.

The guide separates target calls, test generation, and grading, and also
describes hosted fallbacks, remote-only plugins/strategies, telemetry, sharing,
and Cloud-backed setup. The [selection implementation](EVIDENCE.md#promptfoo-remote)
uses explicit-disable precedence, configured remote endpoints, cloud login,
and available local credentials in remote-generation decisions.

Disabling remote generation is not network isolation. It does not turn an
external target model into local inference, disable all hosted functionality,
or grant permission for a separately configured grading provider. Each
selected data destination needs review.

The best reuse might be the evaluation structure or a deliberately constrained
integration, rather than the default red-team workflow. No scans,
attack-generation workloads, or provider evaluations were run in this study.

## 5. Deterministic checks and review quality

[Gitleaks](CATALOG.md#gitleaks) illustrates credential-pattern scanning with
redacted, machine-readable evidence. Its captured README says feature
development ended and future releases focus on security patches, pointing to
a successor that was not vetted here. That historical maintenance claim must
not automatically install the successor or qualify a current version.

A clean scan is not proof that all confidential content is absent. Candidate
secrets should not be printed in reports. Tool selection, maintenance, rules,
and the actual scan scope remain important.

[Rigour's goal guide](EVIDENCE.md#rigour-goal) documents path and selected
file/symbol checks, with semantic intent outside their reach. A missing PR
description can mean the optional goal check does not run. A local pre-PR job
cannot rely on that behavior as its only scope gate.

[Superpowers verification](EVIDENCE.md#superpowers-verification) supplies a
useful procedural rule: identify evidence for a claim, run the relevant
command, inspect its result, and only then claim completion. The controller or
host still has to capture a real result; an instruction does not prove
compliance.

## 6. Evaluate the feedback loop, not only the artifact

These are research-derived scenarios for a later, explicitly scoped
evaluation. They are not a suite that this publication ran.

| Scenario | A trustworthy result distinguishes |
|---|---|
| A builder changes tests to match broken behavior | Passing edited tests from satisfying the accepted requirement |
| A relevant deliberate defect is placed in an owned disposable fixture | A meaningful detecting test from a vacuous assertion |
| Evidence is reused for a different job or revision | Valid attribution from stale or foreign evidence |
| A judge times out or emits no verdict | Unassessed/failed judging from approval |
| A required check is omitted | Missing evidence from an all-green subset |
| An approved dependency or connector is unavailable | Environment/access blockage from a product defect |
| Repeated repair makes no progress | Bounded escalation from endless resource consumption |
| The requester changes the requirement | A newly accepted revision from silent scope drift |
| A remote request times out after dispatch | Unknown effect needing reconciliation from safely repeatable work |
| A mock passes but the actual host was never exercised | Fixture validation from live acceptance |

Checks, reviewers, and error handling should improve evidence. They must not
weaken the requirement or erase failed attempts until a dashboard appears
green. Private acceptance criteria or live integration findings from the
original context are not present in this edition.
