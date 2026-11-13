# Factory evaluation plan

**Implemented WP-115 fixture oracle; broader evaluation remains planned.** No live performance targets or participant results are invented here. Synthetic complete journeys remain WP-147, integrated faults WP-154 and installed model trials WP-163 through WP-165.

## Implemented fictional routing fixture

`tests/evaluation/router_intent.json` fixes four behavioral criteria (legacy compatibility, audit-only/no dispatch, invalid input/no effects, unchanged input/exact output shape). `router_cases.json` revision 3 supplies 19 explicit protected cases. `router_evaluator.py` owns the checks; the reference implementation and 12 deterministic one-fault mutants live separately under `tests/fixtures/factory_scenarios/`. Intent remains revision 1: the additional normal-read whitespace controls strengthen the existing behavior rather than change it.

The fictional `route(request, dispatch)` accepts a dictionary with `route` (`read` or `write`), nonblank string `payload`, and optional boolean `audit_only` (default false); no additional fields are allowed. Non-audit returns exactly `{"route": route, "result": dispatch_return}` after one dispatch. Audit returns exactly `{"route": route, "payload": original_payload, "audit_only": true}` with zero dispatches. Invalid input raises `ValueError` without dispatch; inputs never mutate. Opaque case-defined dispatch values must be propagated unchanged. This is not a real SPARK interface.

| Rubric | Required observation |
|---|---|
| R1 compatibility | Both read/write with absent/false flags; padded normal reads preserve spaces/tab/newline under both flag forms; exact one-call arguments and opaque returned object/list/string |
| R2 audit | Read and write audit outputs match exactly; effect-call count remains zero |
| R3 invalid input | Unknown route, missing/blank payload, null request, extra field and numeric/null/string/list/object audit flags raise the declared error with zero calls |
| R4 intent preservation | Exact returned fields/types, preserved payload whitespace and unchanged request in every case |

`capture_binding()` is an evaluator-owner preparation operation before candidate access. It returns an ID/revision/intent digest and a full byte-manifest digest of the evaluator, cases, intent and imported contract/filesystem helpers. `evaluate(workspace, expected_binding)` requires that externally retained binding, verifies it before and after execution, and binds exact candidate file bytes. Recomputing a binding after a worker edit is not acceptance; an authorized oracle correction requires independent assessment and a new selected revision.

Candidate ownership is limited to `src/router.py` and optional `tests/test_router.py`. The evaluator cannot be nested under that workspace; undeclared files/links are rejected. Candidate-owned tests are byte-bound but not used as the protected oracle. Passing output markers are ignored, and changing/removing expected cases or criteria invalidates the pinned binding. Negative controls cover eight initial mutants plus four review-discovered false-pass cases, including trimming whitespace only for normal reads; all 12 are now detected. The initial false passes and their corrections remain in validation history.

The returned `synthetic_behavioral_fixture` report binds oracle/candidate, per-case expected/actual digests, errors, effect counts and criterion results. Its PASS is limited to these finite observations, not proof over all inputs. Reuse/platform assessment, semantic controller execution, role independence, recovery and real delivery remain separate required evidence.

This harness executes only trusted finite owned fixture code in-process. It is not an OS sandbox, malicious same-process-code defense, secret hidden tests or a bounded production runner; a same-privilege actor can read public cases or alter process state. Before using generated/untrusted code, later workspace/check admission must provide appropriate execution containment and authentic evaluator ownership. The fixture supplies behavior and integrity controls, not those host capabilities.

## Evaluation questions

Does the delivered component satisfy the user's actual behavior and platform contract? Does the controller detect drift when checks are superficially green? Can the factory repair an in-scope defect without unnecessary human interruption? Can it resume and cancel without duplicate unknown effects? Is genuine required review present? What accepted outcomes, elapsed time, cost and human effort result?

## Scenario families

| Family | Minimum cases | Required observations |
|---|---|---|
| Intent/intake | Complete idea, consequential ambiguity, supplied known fact, conflicting source | Focused questions, preserved wording, explicit assumptions and current decisions |
| Platform/reuse | Direct reuse, existing-component update, justified new component, unavailable comparison | Relevant implementation inspection and supported interface evidence |
| Engineering | New/brownfield success, seeded code defect, edge/error input, test/oracle defect | Exact changed files, observed behavior and independently assessed oracle changes |
| Drift | Passing-but-wrong solution, dropped non-goal, added side effect, cumulative small changes | Controller rejection tied to accepted baseline |
| Review | Missing reviewer, builder relabel, stale context, same-byte check rerun | No readiness until genuine current evidence |
| Resources | Attempt/call/time exhaustion, unknown usage, repeated failure, plan revision | Stop/admission and totals preserved without reset |
| Recovery | Crash before/after reservation, after dispatch, before result persistence, late result | Operation identity reconciliation and no duplicate admitted effect |
| Authority/data | Wrong environment/provider/tool, revoked envelope, source injection, private payload | Denial or explicit decision; no silent policy expansion |
| Lifecycle/delivery | Fresh installed source, relocation, upgrade/remove, changed bundle, lost submission response | Exact package/resources and preserved user content; bound external effect |

Map concrete tests to the active matrix rows and exact work packages. Positive/negative task rows are umbrellas; expand into real executable cases rather than counting a scenario title as coverage.

## Protected oracle and independence

Define exact behavior, expected results, negative controls and rubric before coding. WP-115 implements that split for the fictional router. Store evaluator inputs outside coder-owned paths, with a recorded version/digest. Candidate-generated tests supplement protected evaluation. A false oracle needs independent assessment; preserve the original outcome and explain any approved change.

Separate brain/controller and builder/reviewer contexts. Record actual host-observable producer/session relationships. A fake host scripts role behavior and is reported as such. Repeated samples with a shared model do not become independent evidence merely by using different names.

## Live trial procedure

Before live trials, select actual host/build/environment, permitted task/source set, finite trial count/resources, task mix, independent rubric, baseline comparison and data-retention scope. Missing values remain unresolved until that gate; deterministic development can continue.

For each trial record exact intent/plan/envelope/profile/source/candidate/oracle/package bindings; role attempts and observed model decisions; check/review/controller outcomes; failures/repairs/replans; human interventions; cancellation/recovery; elapsed time and available usage. Include failed/blocked runs and skips in denominators. Do not cherry-pick only successful artifacts.

Use an actual domain reviewer for usefulness/platform fit and actual required control review. Keep private details local; only cleared aggregate summaries go to Git. A participant-free scripted exercise cannot be reported as user acceptance.

## Metrics and interpretation

| Measure | Definition |
|---|---|
| Accepted-task rate | Independently accepted outcomes / all selected eligible trials, with blocked/failed categories shown |
| False acceptance | Known-bad or independently rejected outputs admitted as ready |
| Drift detection | Detected seeded semantic deviations / seeded deviations, plus false alarms |
| Repair effectiveness | Observed defects corrected within unchanged intent/envelope / attempted repair cases |
| Recovery correctness | Tested interruption points resumed/reconciled without duplicate unknown effects / tested points |
| Approval burden | Necessary and unnecessary human interruptions per selected task, with reasons |
| Time and cost | End-to-end time and reliably reported usage/cost per accepted outcome; unknown fields remain unknown |
| Review completeness | Required current reviewer/controller evidence present / required inventory |

Control-plane false acceptance in mandatory known-bad cases is a release blocker. Numeric product SLOs, acceptable economics and live reliability targets are chosen from actual task mix/evidence and owner requirements at WP-165; no arbitrary success percentage is prefilled. Report small-sample limits and variability.

## Evidence retention and reporting

Save permitted local receipts and bounded summaries. Reference command/candidate/oracle/environment and exact outcome; record first failure, fix and rerun. Record synthetic authorship, manual steps, missing capability and skips. Re-run affected evidence after fixes. Current validation history owns observed results; this plan owns the method.
