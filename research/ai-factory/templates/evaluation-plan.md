# Template - Evaluation Plan

[Corpus index](../README.md) | [Evaluation chapter](../07-evaluation-and-verification.md)

**Status:** UNFILLED TEMPLATE. No results have been observed.

## Question and decision

**Question being evaluated:** Not set.<br>
**Decision this evaluation will support:** Not set.<br>
**Claim it will not support:** Not set.

## System under test

Record exact application, model, prompt, skill, harness, tool, policy, environment, and retrieval versions. Identify mutable provider aliases or other reproducibility limits.

## Baseline and candidates

| Variant | Description | What differs |
|---|---|---|
| Baseline | Not defined | Not defined |
| Candidate | Not defined | Not defined |

Keep comparison conditions equivalent where needed. Explain unavoidable differences.

## Task population

- Intended users and task classes: Not set.
- Dataset sources and authorization: Not established.
- Development/validation/holdout split: Not defined.
- Known gaps and underrepresented cases: Not assessed.
- Leakage and contamination controls: Not designed.
- State reset/isolation: Not designed.

## Case schema

| Field | Required content |
|---|---|
| Case ID | Stable identity |
| Input and starting state | Versioned, permitted material |
| User-visible requirement | Explicit and unambiguous |
| Expected outcome | Verifiable result or legitimate abstention |
| Mandatory constraints | Policy and process invariants |
| Graders | Appropriate deterministic/model/human checks |
| Reference examples | Known-good and known-bad artifacts |

## Grading

| Criterion | Grader | Calibration evidence | Threshold |
|---|---|---|---|
| Not defined | Not selected | Not available | Not agreed |

Specify hard gates separately. Define `unknown`, missing evidence, evaluator failure, partial credit, and disagreement handling.

## Experimental design

- Tasks and trial count rationale: Not set.
- Randomization or ordering: Not defined.
- Shared-state and correlated-failure handling: Not defined.
- Exclusion policy: Not defined.
- Cost and latency collection: Not defined.
- Human-effort measurement: Not defined.
- Uncertainty reporting: Not defined.

Do not remove inconvenient failures after seeing the results.

## Planned failure cases

- [ ] Missing or contradictory input.
- [ ] Unauthorized operation.
- [ ] Tool outage and uncertain write.
- [ ] Stale approval or artifact.
- [ ] Prompt injection in source material.
- [ ] Budget exhaustion and cancellation.
- [ ] Valid alternative solution.
- [ ] Known evaluator bypass or invalid success.

## Results

**Execution status:** Not run.<br>
**Observed results:** None.<br>
**Skipped checks:** All, until execution.<br>
**Decision:** Not made.

Populate results from actual evidence; never copy expectations into the observed-result fields.
