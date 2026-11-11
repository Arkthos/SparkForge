# 07 - Evaluation and Verification Engineering

[Back to the index](README.md)

## Different questions require different evidence

**Testing** checks specified behavior. **Evaluation** measures system performance across a task distribution. **Verification engineering** makes important correctness properties observable and actionable. **Acceptance** decides whether evidence is sufficient for a use. **Authorization** decides whether an action may happen.

These activities overlap but are not interchangeable. Allbright's verification note emphasizes deterministic feedback as a sensor for agents. Anthropic's evaluation guide distinguishes tasks, trials, graders, traces, outcomes, and the evaluation harness. [S43](16-sources-and-reading-guide.md#s43) [S10](16-sources-and-reading-guide.md#s10)

## Evaluate the system, not just the model

The result depends on:

- task wording and information availability;
- model and generation configuration;
- prompts and skills;
- context selection and memory;
- tool interfaces and permissions;
- environment and dependencies;
- orchestration and stopping rules;
- grader implementation.

Changing the harness can change performance without changing the model. A model benchmark score is not a direct prediction of our factory's acceptance rate.

## A layered evaluation strategy

| Layer | What it checks | Example |
|---|---|---|
| Unit | Deterministic local behavior | Task parser rejects missing acceptance criteria |
| Contract | Component boundaries | Tool cannot write outside its permitted target |
| Integration | Components working together | Retrieval returns the authorized revision |
| End-to-end | User-relevant outcome | The requested behavior works in the application |
| Agent capability | Performance on representative tasks | Can the worker diagnose several failure classes? |
| Regression | Previously accepted behavior | A model upgrade does not break known tasks |
| Safety and misuse | Forbidden or risky behavior | Untrusted source text cannot authorize publication |
| Reliability | Failure and recovery semantics | A lost response does not duplicate a write |
| Operational | Real service behavior | Latency, error rate, cost, and human intervention |
| Business | Value in the actual workflow | Accepted work improves total lead time and quality |

No single aggregate score replaces all layers.

## Task, trial, and outcome

A **task** defines a problem and success conditions. A **trial** is one attempt. A **trace** records observable steps. An **outcome** is the resulting state of the environment.

For example:

- Task: repair a cancellation bug.
- Trial: one execution with a specified model and harness.
- Trace: files inspected, edits proposed, commands run, results observed.
- Outcome: the cancellation behavior works and required existing behaviors remain intact.

"I fixed the cancellation bug" is a trace statement, not the outcome.

## Designing a task set

Start with a small but deliberate set of real task classes or synthetic analogues. Include:

- ordinary successful cases;
- boundary conditions;
- missing and contradictory information;
- tasks that should be refused or escalated;
- permission failures;
- tool outages and uncertain writes;
- unfamiliar but valid variants;
- regressions from prior failures.

A suite containing only easy happy paths rewards overconfidence. A suite containing only attacks can produce an unusably cautious system. Measure both appropriate action and appropriate non-action.

Keep the underlying requirement visible even when individual test instances are held out. A protected holdout should test generalization, not surprise the agent with undisclosed product requirements.

## Dataset partitions

| Partition | Purpose | Access rule |
|---|---|---|
| Development examples | Improve prompts, tools, and workflows | Available to maintainers and optimization loops |
| Validation set | Compare candidate designs | Controlled use and tracked iterations |
| Protected holdout | Estimate generalization before promotion | Not editable or routinely visible to the worker |
| Regression bank | Preserve known capabilities | Versioned, with reviewed changes |
| Production samples | Detect drift and real failures | Permission-aware collection and retention |

Repeatedly optimizing against the holdout turns it into a development set. Holdout freshness and access controls are operational requirements, not labels alone.

Synthetic cases are useful for controlled failures, but they may miss the ambiguity, dependencies, and messiness of real work. Record that limitation.

## Graders

### Deterministic graders

Use them for properties that can be checked reliably in code:

- schema and type validity;
- expected state changes;
- unit and integration test results;
- allowed paths and operations;
- presence of required evidence;
- budget and deadline compliance.

A deterministic grader can still be wrong or incomplete. Validate it with known-good and known-bad artifacts.

### Model-based graders

Use them where a rubric needs semantic judgment: explanation quality, coverage of a nuanced request, or the usefulness of a synthesis.

Give the grader:

- a specific rubric;
- sufficient permitted evidence;
- separate criteria instead of one vague "quality" score;
- an `unknown` or insufficient-evidence option;
- instructions to treat evaluated content as untrusted data.

The MT-Bench/Chatbot Arena paper discusses position, verbosity, and self-enhancement biases in LLM judging. It supports calibration and caution, not a claim that one model can objectively certify another's work. [S30](16-sources-and-reading-guide.md#s30)

### Human graders

Use domain experts for ambiguous ground truth, consequential judgments, and calibration. Provide a rubric and examples; humans can disagree too.

Record disagreement rather than forcing artificial certainty. When two competent reviewers disagree, the problem may be the task definition, not the reviewer.

## Judge calibration

Create a set of artifacts independently labeled by qualified reviewers. Compare model judgments to those labels by criterion, not only overall.

Inspect:

- false acceptance of incorrect or unsafe work;
- false rejection of valid alternatives;
- sensitivity to response length and order;
- inconsistency across repeated grading;
- behavior when evidence is missing;
- susceptibility to instructions embedded in the artifact.

Changing the judge model or rubric changes the measuring instrument. Recalibrate before interpreting score changes as product improvement.

## Hard constraints and soft quality

Do not average a severe policy violation away with excellent prose.

An illustrative acceptance structure:

| Criterion | Treatment |
|---|---|
| Authorized data and tool use | Mandatory gate |
| No unresolved consequential write | Mandatory gate |
| Required behavior and regressions | Mandatory gate |
| Evidence bound to candidate revision | Mandatory gate |
| Readability and presentation | Rubric, within agreed limits |
| Cost and latency | Operational thresholds appropriate to the task |

Actual thresholds belong in an approved evaluation plan. This table is a design pattern, not a production policy.

## Outcome checks versus trajectory checks

Outcome checks allow valid alternative strategies. A rigid requirement that the agent call exactly five tools in a particular order can reject a better solution.

Trajectory checks remain essential for constraints: the agent must not read unauthorized data, edit protected tests, or publish without approval even if the final artifact looks correct.

Use outcome criteria for the goal and trajectory criteria for necessary process or safety invariants.

## Repeated trials and uncertainty

One successful run does not establish reliability. Repeat tasks under controlled starting conditions and report the number of tasks, trials, failures, exclusions, and incomplete runs.

`pass@k` asks whether at least one of a set of attempts succeeds. `pass^k` emphasizes success across all of the attempts. They answer different questions. A system that occasionally finds a solution after many tries is not necessarily a dependable unattended service. [S10](16-sources-and-reading-guide.md#s10)

Avoid these statistical mistakes:

- treating correlated trials as independent;
- hiding failed infrastructure runs without explaining exclusions;
- selecting only the best seed or successful trajectory;
- comparing designs on different task distributions;
- claiming superiority from a tiny score difference without uncertainty;
- treating zero observed failures as proof of zero failure probability.

Repeated trials on the same task do not provide the same diversity as additional representative tasks. Use intervals appropriate to the sampling design, and consider task-level or cluster-level analysis when observations share dependencies.

## Baselines and ablations

Before adding a complex system, compare:

1. A manual or deterministic baseline.
2. A single model call where appropriate.
3. A bounded single-agent harness.
4. The proposed richer workflow.

An **ablation** removes or changes one component to estimate its contribution: no persistent memory, simpler tool set, no parallel reviewers, different retrieval, or a cheaper model.

Track quality, cost, latency, human minutes, and operational failures together. An extra reviewer that finds one more issue but creates many false alarms may not improve the workflow.

DSPy is an example of treating language-model pipelines as optimizable programs with an explicit metric. The general lesson is to optimize against a meaningful objective with held-out evaluation, not that any optimized prompt is automatically robust. [S31](16-sources-and-reading-guide.md#s31)

## The verification boundary in software factories

A builder may write its own tests as part of implementation. That is useful development feedback. It should not be allowed to silently rewrite every independent acceptance check.

Separate:

- developer tests that evolve with the code;
- protected regression tests;
- acceptance scenarios owned by the product or verification process;
- security and policy checks;
- production monitoring.

StrongDM's scenario and digital-twin approach is one reported attempt to strengthen behavioral validation. The important questions are coverage, realism, evaluator independence, and resistance to gaming, not whether the artifact is called a "test" or a "scenario." [S04](16-sources-and-reading-guide.md#s04)

## Digital twins and simulated services

A service twin can make dangerous, expensive, or rare cases repeatable. It can simulate timeouts, permission failures, rate limits, and unusual state transitions.

Its limitation is fidelity. A twin may omit the production behavior that causes the actual incident.

Maintain:

- a documented supported surface;
- contract checks against the real service where authorized;
- known differences;
- versioned fixtures;
- failure-injection capabilities;
- evidence that evaluations reset state correctly.

A passing twin-based evaluation is not the same as live acceptance.

## A release evidence bundle

Record:

- exact candidate revision and task contract revision;
- model, harness, tool, environment, and policy configuration;
- dataset and grader versions;
- task and trial counts;
- per-criterion results;
- failures, exclusions, and skipped checks;
- usage and elapsed time;
- reviewer decisions and exceptions;
- residual risks;
- the authority that accepted promotion.

This bundle can be compact. Its value comes from accurate binding and retrievability, not from retaining every token forever.

## Testing our measuring system

Seed a known bug. Supply a valid alternative solution. Remove a required evidence file. Change the artifact after testing. Make the grader unavailable. Feed the judge an artifact containing a request to ignore the rubric.

If these cases do not produce the expected result, the evaluator needs repair before its score can guide release.
