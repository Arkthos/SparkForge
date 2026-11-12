# Specifications, intake, and accepted intent

**Public-source analysis from the 2026-11-05 baseline; publication edition
2026-11-12.** Source references below identify historical selected reading,
not newly run software. Private-system comparisons in the original topic are
not reproduced.

Intake is not simply turning a sentence into code. The useful work is to make
the intended outcome, existing options, change boundary, permitted inputs,
acceptance evidence, and non-goals explicit. Domain experts should not need
to design an implementation interface before receiving help.

## 1. Interview skills: structured discovery without false precision

[Agent Skills' interview contract](EVIDENCE.md#addy-intake) asks one question
at a time, records a hypothesis, distinguishes an actual desired outcome from
a conventional solution label, and concludes with intent and non-goals. It
requires a responsive user: ambiguity in an unattended request is a blocker,
not permission to claim confirmation.

This is useful when a person can describe a playbook, investigation, or
workflow but not a data model or interface. Focused questions reduce cognitive
load. Stating what the proposal will *not* do can expose a mismatch earlier
than a long implementation plan.

Two qualifications are essential:

- The approximate confidence percentages in the skill are heuristics, not
  calibrated probabilities. A useful brief distinguishes established facts,
  unresolved choices, and supporting evidence. A model saying it is "95%
  certain" does not measure understanding or confer consent.
- The contract's strict confirmation convention is a user-experience choice,
  not an authentication protocol. The selected host's real user action and the
  exact accepted artifact must define the consequential boundary.

[Superpowers brainstorming](EVIDENCE.md#superpowers-intake) reinforces a
complementary practice: read the supplied context and relevant existing system
before asking. Repeatedly asking a user to reconstruct facts already present
in accessible, authorized sources wastes time and can introduce mistakes.
Unavailable evidence should be exposed rather than filled in.

The reusable sequence is to understand the problem, present relevant options
and tradeoffs, make the proposed behavior concrete, and obtain the required
decision. It does not require activating either entire skill collection.

## 2. Spec Kit is a workflow substrate, not only a prompt pack

The [reviewed Spec Kit](CATALOG.md#spec-kit) includes integrations, presets,
extensions, workflows, step plugins, bundles, catalogs, and persistent runs
alongside specification artifacts. A comparison that treats this pin only as
a fixed linear template collection misses mechanisms present in the source.

### Gate behavior and its trust boundary

The [selected GateStep implementation](EVIDENCE.md#spec-kit-gate) validates
configured options and rejection policy at execution time. It can consume a
workflow-input verdict; otherwise an interactive terminal is prompted.
Noninteractive execution returns `PAUSED` rather than inventing an answer.
Abort, retry/pause, and skip are distinct outcomes.

These are actual code mechanisms, unlike an instruction that merely tells a
model to ask permission. They still do not supply a complete approval service.
An upstream caller can provide a verdict, and the general-purpose rejection
policy can allow a rejected step to be skipped.

Neither feature is intrinsically a defect in a generic workflow engine. But
if a product requires accepted intent before implementation, it must prove
that the surrounding host supplies an authorized human decision for the
current artifact and prevents implementation after rejection. Supplying the
word `approve` in a model-controlled field is not that proof. Nor should
reject-to-skip be inherited as the mandatory gate's default.

### Persistent state and failure handling

The [reviewed RunState ranges](EVIDENCE.md#spec-kit-state) validate run IDs,
retain run/step/input state, and write through a temporary file followed by
atomic replacement. A failed save poisons the in-memory instance, preventing
later writes from treating an unhealthy checkpoint as sound.

That is valuable recovery prior art. It establishes selected per-file
persistence behavior, not a transaction across every artifact, subprocess, or
external operation. A lost response after an effect still requires
reconciliation: restoring a state file does not prove that the effect never
occurred.

### Offline and restricted packaging

The [offline guide](EVIDENCE.md#spec-kit-offline) is useful because it describes
limits rather than treating "offline" as a single feature flag. Dependency
wheels can be OS- and Python-specific. Windows scaffolding has a documented
PowerShell requirement. Integration adapters can require both catalog and
archive availability. A transferred bundle manifest need not contain all
named dependencies.

The adoption question is therefore the complete reviewed dependency closure
for the chosen operation and platform. This reading did not install Spec Kit,
verify an offline deployment, or establish approval for a restricted host.

## 3. OpenSpec: artifacts for changes to existing software

[OpenSpec](CATALOG.md#openspec) organizes proposed changes around artifacts
instead of treating every request as a new project. Proposals, specifications,
design, tasks, application, and archival distinguish the current contract from
a candidate change. This fits both maintenance work and changes to a factory's
earlier outputs.

The [artifact types](EVIDENCE.md#openspec-artifacts) declare dependencies and
generated files, bound the number of artifacts, and constrain relative paths.
The reviewed path rules consider Windows and POSIX forms and reject parent
traversal and absolute paths.

The [schema loader](EVIDENCE.md#openspec-validation) parses structure, checks
duplicate identifiers, validates dependency references and apply prerequisites,
and invokes cycle validation. These checks ask useful structural questions:

| Structural question | What still needs another source of evidence |
|---|---|
| Does each dependency name an existing artifact? | Whether that dependency is the right engineering prerequisite |
| Is the graph structurally valid? | Whether its contents satisfy the user's actual need |
| Is a generated path in the expected relative namespace? | Whether every runtime write path is constrained |
| Are prerequisites present? | Whether the artifacts are semantically complete and accepted |

File existence and schema validity are not human approval. A valid graph can
still encode the wrong behavior or contain vacuous tests.

OpenSpec's lighter, change-oriented workflow and Spec Kit's richer engine are
alternatives to compare, not automatically two layers to install together.
Without a clear owner for the canonical brief and change state, stacking both
can create competing sources of truth. The catalog also preserves OpenSpec's
historical shared-specification-store beta qualification.

## 4. Richer lifecycle and generation alternatives

[Spec Kitty](CATALOG.md#spec-kitty) documents work packages, lifecycle lanes,
worktrees, review, acceptance, merge, and retrospectives. Visible progress and
bounded work-package ownership are useful ideas for work that crosses multiple
sessions. The reviewed main branch was a 4.x release-candidate line with stable
launch acceptance pending. The study read the selected README, not the entire
governance implementation. Its merge/push workflow must be assessed separately
from the target product's actual delivery permissions.

[BMad Method](CATALOG.md#bmad-method) provides a role- and artifact-rich
methodology. [BMad Builder](CATALOG.md#bmad-builder) is particularly relevant
when the output is a reusable agent, skill, workflow, or module rather than an
ordinary application. Generated capabilities need structure, dependency
information, validation, and documentation, not only a prompt.

The historical main branch of BMad Method was v7 preview alpha; stable v6 was
a different baseline. Related modules have their own configuration and sibling
resource contracts. Do not combine claims or interfaces across those branches.
The builder's module-generation implementation was not deeply traced.

A reusable intake artifact, a validation convention, or a testing-knowledge
fragment may offer more value than importing a complete methodology. A product
for domain experts should keep consequential decisions visible while avoiding
unnecessary ceremony.

## 5. RSC: explicit selection and revision-bound application

[RSC Harness](CATALOG.md#rsc-harness) records selected, deferred, and excluded
capabilities and the evidence that could justify reconsidering a deferral.
That is more informative than a binary list of installed tools.

The [application implementation](EVIDENCE.md#rsc-acceptance) validates plan
identity, records accepted-plan provenance, inventories governed paths, and
checks artifact digests. It also supplies receipts and backup-related
provenance. This makes an onboarding decision reproducible at the artifact
level.

The [reviewed test source](EVIDENCE.md#rsc-acceptance-tests) includes assertions
for a no-write preview, rejection of the wrong acceptance ID, and receipt
persistence. These assertions were read, not executed.

The useful principle is revision binding. It does not authenticate a person.
An implementation agent able to read an ID can echo it; a trustworthy channel
must supply the decision and the surrounding host must enforce its authority.
Content identity and human consent must not be conflated.

RSC's public source is also distinct from the separately discussed Risco
factory video. Shared authorship is not proof that this repository implements
the entire demonstrated product.

## 6. Questions an actionable brief should answer

These questions are research-derived design criteria, not a newly selected
schema or an executed acceptance suite.

| Question | Why it matters |
|---|---|
| What domain outcome is desired? | Prevents implementing a familiar solution shape that misses the problem |
| What existing capability was actually considered? | Makes reuse-first work observable and separates missing comparison from absence |
| Is the work reuse, an update, or a new component? | Makes ownership and change scope explicit |
| Which sources, tools, and data destinations are permitted? | Keeps intent separate from access and execution permission |
| What behavior and non-goals are accepted? | Gives later review a stable scope boundary |
| What demonstrates success and meaningful failure? | Gives tests an oracle other than the builder's own output |
| Which revision was accepted, and through what real decision channel? | Prevents stale or model-manufactured approval |
| What remains unknown or untested? | Stops a missing source or unqualified host from becoming invented certainty |

The public mechanisms help make these answers explicit. They do not supply
the target's private implementation facts or actual permission contract.
Those comparisons remain withheld or `NOT_ASSESSED` in this publication.
