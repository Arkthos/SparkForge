# Public prior art: mechanisms and reuse reference

**Prepared:** 2026-11-11. **Underlying public repository observations:**
2026-11-05. This is a new, source-neutral synthesis of public evidence, not a
republication of a contextualized dossier.

The [source catalog](sources.json) records 33 public repositories, exact
commits, historical inspection ranges, and license qualifications. These are
references, not vendored dependencies. No upstream code, skill collection,
license document, image, or caption archive is redistributed here.

## How to read the evidence

- **Documentation or skill contract:** what the upstream author describes or
  instructs. It is not proof of enforcement.
- **Selected implementation:** bounded source reading at the catalog's pin.
  It is not a whole-runtime, caller-authorization, or sandbox audit.
- **Test source:** assertions were read, not executed.
- **Specification:** a proposed contract, not an installed implementation.

This publication verified public identities and pins against existing
public-source metadata, not against a newly fetched upstream revision. The
historical findings below remain bounded by their recorded inspection ranges.
No candidate framework was installed, run, benchmarked, or adopted here.

## Detailed per-topic publication edition

**Added 2026-11-12:** the [detailed dossier](dossier/README.md) now accounts
for all 14 original prior-art documents. This page remains the introductory
reference; it is no longer the only published treatment of those topics.

The expansion preserves the public analysis, not the original private
operating context. Its [document dispositions](dossier/document-dispositions.json)
identify what each counterpart retains and what stays withheld. Source-specific
private facts are not transplanted into anonymous examples. No upstream code,
raw captions, screenshot, frame, or full article is imported.

| Detailed topic | Reference |
|---|---|
| Product goals and full capability comparison | [Scope](dossier/SCOPE.md), [reuse map](dossier/REUSE_MAP.md) |
| Intake, gates, artifacts, and accepted plans | [Specifications and intake](dossier/SPECIFICATIONS_AND_INTAKE.md) |
| Controllers, products, and alternative runtimes | [Factory patterns](dossier/FACTORY_PATTERNS.md) |
| Tests, independent judging, and correction | [Quality and evaluation](dossier/QUALITY_AND_EVALUATION.md) |
| Knowledge, learning, recovery, and authority | [Knowledge and governance](dossier/KNOWLEDGE_AND_GOVERNANCE.md) |
| Host compatibility, egress, and scoped rights | [Compatibility and licensing](dossier/COMPATIBILITY_AND_LICENSING.md) |
| Industrial accounts and discovery limits | [Industry and theory](dossier/INDUSTRY_AND_THEORY.md), [discovery appendix](dossier/DISCOVERY_APPENDIX.md) |
| Full video-topic and version analysis | [ZazenCodes](dossier/VIDEO_ZAZEN_FACTORY.md) |
| Every candidate and historical source range | [33-candidate catalog](dossier/CATALOG.md), [90-inspection register](dossier/EVIDENCE.md) |
| Denominators and actual validation boundaries | [Coverage and validation](dossier/COVERAGE_AND_VALIDATION.md) |

The new publication did not refresh the upstream sources, run their tests, or
repeat the video reviews. Historical observations remain dated and bounded.

## 1. Shape intent before starting execution

**Spec Kit** provides a useful distinction between a workflow step and a
review gate. The selected gate source supports configured verdicts,
noninteractive pause, invalid-input failure, and explicit abort/retry/skip
semantics. Selected engine ranges preserve run identity and use atomic
per-file state persistence. That is not evidence that an entire multi-file
workflow is transactional.

**OpenSpec** separates proposed changes into artifacts and dependencies.
Selected types/schema code checks relative paths, bounded declarations,
duplicate IDs, prerequisite references, and parseable structure. A valid
artifact graph does not establish that the specification is correct or
approved. **Spec Kitty**, **BMad Method**, and **GSD Core** add useful documented
work-package, role, lane, and discuss/plan/execute/verify patterns; their
overview readings do not establish complete implementation behavior.

**Superpowers** and **Agent Skills** make discovery, consequential questions,
non-goals, design confirmation, test-first work, and fresh verification
explicit. The reusable mechanism is a focused intake and evidence contract,
not a blanket instruction to discard existing code or trust a confidence
score.

**Design implication:** represent the requested outcome, non-goals, open
decisions, acceptance criteria, and approved revision separately from
execution permission. A recorded work item must not automatically become
queued work.

Pinned examples:
[Spec Kit gate](https://github.com/github/spec-kit/blob/ec9a6f3b94c0aa856f77e550785a1ddde1993de1/src/specify_cli/workflows/step/gate/__init__.py),
[OpenSpec schema](https://github.com/Fission-AI/OpenSpec/blob/3e4d5f0769e2857c8eb54f149cbf5e4f703fa04c/src/core/artifact-graph/schema.ts),
[Superpowers discovery](https://github.com/obra/superpowers/blob/22f0b463e7a5e579904dd6211a520321035526f7/skills/brainstorming/SKILL.md).

## 2. Make context and component adoption reviewable

**RSC Harness** is useful for distinguishing a project knowledge map from
automatic component installation. The selected onboarding source binds an
apply operation to an exact plan and governed artifact digests, with
provenance, backups, and receipts. Its test source includes no-write preview,
wrong-plan rejection, and receipt persistence; those tests were not run.

Its historical host table also illustrates why compatibility must be
feature-specific: Copilot output surfaces did not imply supported Copilot
session memory. **Agent OS** contributes a documented standards-discovery and
indexing pattern. **BMad Builder** and the **engineering plugin** supply
component/workflow design references, not permission to install every
connector or copy a single skill without its required resources.

**Design implication:** inventory what a component adds, reads, changes,
executes, and transmits. Keep selected, deferred, and excluded capabilities
explicit. A skill name, hook declaration, or byte digest is not enforcement,
authenticated approval, or a portable dependency closure.

Pinned example:
[RSC onboarding apply](https://github.com/ericrisco/rsc-harness/blob/726aaf3ba87c584329fc821f243a7ce5e62450fd/scripts/lib/onboarding-apply.js).

## 3. Separate deterministic coordination from model work

**Super Simple Software Factory** demonstrates a useful architectural split:
Python owns phases and acceptance while agents return typed envelopes.
Selected runner code distinguishes phase completion from whole-run
acceptance; trace code records identities in JSONL with a SQLite mirror.
Selected agent-call code handles bounded corrections and accumulated usage.
The reviewed path is Pi-specific, and its Git helper uses broad staging.
Neither that staging behavior nor post-call write checks should be adopted as
a universal safety boundary.

**BMad Loop** documents story selection, implementation, independent review,
verification, durable state, and bounded attempts. Selected profile code
distinguishes bypass and non-bypass launch modes. Its bundled Copilot profile
uses broad permission flags, and a particular macOS/CLI hook observation does
not qualify native Windows. Advisory budgets and enforced limits must be
identified separately.

**Foreman/eve** separates classifier, analyst, implementer, and reviewer
stations. Some ordering and bounded-rework rules are instructions in a prompt;
they are not all established as deterministic enforcement. Selected source
also separates caller trust, review output shape, brain updates, and approval
policies. Its inspected sandbox implementation uses hosted Vercel Sandbox
even for local development. A local interface therefore does not prove local
execution or local data retention.

**Design implication:** preserve task/run/attempt identities, explicit
ownership, observed results, finite repair limits, and a real acceptance gate.
Treat a model verdict as evidence rather than human authorization. Keep
consequential effects and publication separate from candidate production.

Pinned examples:
[SSSF runner](https://github.com/disler/super-simple-software-factory/blob/de31374882e7a4e3e5b7bb9bd09e69dc2f779356/.claude/skills/sssf/templates/adws/adw_modules/runner.py),
[BMad profile adapter](https://github.com/bmad-code-org/bmad-loop/blob/49eb8a3f15b1cab9758948b5b341516de9c044df/src/bmad_loop/adapters/profile.py),
[Foreman sandbox](https://github.com/vercel-labs/eve-software-factory-template/blob/6bc5febab95de4c05fa08b164f544650f6aa11aa/agent/sandbox.ts).

### The ZazenCodes example has distinct versions

The public [video](https://www.youtube.com/watch?v=ctoaIC4LHmI) and repository
are related references, not interchangeable revisions.

The original v1 build prompt describes shared board state. The selected
current v1 skill/role documents instead use per-job state, worktrees,
distinct artifact owners, a complete review-round barrier, and bounded
builder resumptions: two resumptions across three review rounds. Those are
useful coordination contracts. They remain agent instructions, not a verified
process sandbox.

The v1 approver can authorize a local main-branch merge through a model
verdict, while the orchestrator says not to push. That is a boundary to
question, not a substitute for a human intent or integration decision.
The separately documented v2 describes an issue-driven successor with
script/state gates and PR delivery. Only its README and opening license text
were reviewed; its executable implementation was not.

Do not attribute v2 properties to the earlier video, infer that a changed
state-file convention proves recovery, or inherit demonstrated permission
bypass. Root/v1 reuse licensing was not established. The v2 license is scoped
to that subtree, as described below.

Pinned example:
[v1 orchestration contract](https://github.com/zazencodes/zazencodes-season-3/blob/6c2b66b0f38fc883f773fe098214c0cef4ea7654/src/software-factory-claude-code/.claude/skills/factory/SKILL.md).

## 4. Evaluate the result and the measuring system

**Waza** contributes concrete evidence-binding mechanisms: frozen evidence,
an isolated judge executor, constrained verdict tools, and failure on missing
or invalid callbacks in selected source. Its read test source covers foreign
run/task/attempt identifiers and changed digests. Reading those assertions is
not observing their execution.

Its paths also have different contracts: an explicit CLI override, bundled
runtime behavior, opt-in text-only execution, an isolated judge, and snapshot
handling cannot be reduced to one "Copilot compatible" label. The pinned
judge code has a specific native-runtime restriction.

**BMad TEA** connects risk-based test design, requirements, nonfunctional
evidence, behavioral evaluation, and traceability. **Promptfoo** supports
provider comparison and configurable assertions, but its privacy documentation
separates target calls, generation, grading, telemetry, sharing, and hosted
features. Disabling remote generation is not network isolation; selected
source also shows remote-routing/fallback conditions.

**Pester** and **Gitleaks** are references for deterministic checks where
appropriate. Neither was installed or run for this study. A scanner result
would still not prove absence of all confidential material.

**Design implication:** bind criteria, input evidence, grader configuration,
and results to exact candidate revisions. Include known-bad artifacts,
missing-result handling, protected acceptance, negative cases, and all failed
attempts. Do not equate typed output, a model's self-report, or a workflow exit
with successful user-visible behavior.

Pinned examples:
[Waza evidence grader](https://github.com/microsoft/waza/blob/f5789f75fa00924411734d07fd4012ba80e2154c/internal/graders/evidence_prompt_grader.go),
[Promptfoo data handling](https://github.com/promptfoo/promptfoo/blob/e3e2bb871540ae153a630878ecb17e56cfb487e3/site/docs/red-team/troubleshooting/data-handling.md).

## 5. Treat learning as an evaluated proposal

**Rigour's** selected lesson logic distinguishes decision precedence,
counterevidence, withdrawal, human-origin recurrence, and bot-only evidence.
This is a useful antidote to promoting every generated suggestion into policy.
Its documented profiles organize identity/state; they do not prove OS-level
isolation. Its goal checks also distinguish checkable paths/symbols from
semantic criteria that remain unassessed.

**Compound Engineering** connects work and review to durable learning. The
guidance emphasizes useful, non-obvious, material lessons and the cheapest
suitable representation. It also exposes a privacy question: broad discovery
of histories across agent installations requires explicit permission; a
request to improve one project does not authorize unrelated transcript access.

The separate [self-improvement study](../../docs/research/SELF_IMPROVEMENT.md)
adds Fluent's inert learning handoff, host-supplied provenance, independent
review, no-change path, and separation of follow-ups from execution.

**Design implication:** observations can yield `NO_CHANGE`, an inactive
candidate, or a separate work proposal. Evaluation, protected regression
checks, independent review, version-bound promotion, monitoring, and
withdrawal remain distinct. A mandatory evaluation failure is not a successful
no-op, and the learner must not grant itself approval or new permissions.

Pinned examples:
[Rigour lesson logic](https://github.com/rigour-labs/rigour/blob/7e0ef7f4e4ef614d55d83d2958e2603f65f019e7/packages/rigour-core/src/review-learning/lessons.ts),
[Compound learning guide](https://github.com/EveryInc/compound-engineering-plugin/blob/799ac9aeb97bf1c51238c38122915470413c26c5/docs/guides/ce-compound.md).

## Reference map

Complete immutable pins and historical review ranges are in
[sources.json](sources.json). The short descriptions below identify reading
leads, not comparative performance findings.

| Public repository | Useful reference | Historical review depth |
|---|---|---|
| [github/spec-kit](https://github.com/github/spec-kit) | Workflow gates, run state, specification lifecycle | Selected implementation and documentation |
| [Fission-AI/OpenSpec](https://github.com/Fission-AI/OpenSpec) | Artifact graph, prerequisites, change lifecycle | Selected implementation and documentation |
| [spec-kitty/spec-kitty](https://github.com/spec-kitty/spec-kitty) | Work packages, lifecycle lanes, worktrees | Selected README |
| [bmad-code-org/BMAD-METHOD](https://github.com/bmad-code-org/BMAD-METHOD) | Requirements, roles, delivery artifacts | README and license |
| [bmad-code-org/bmad-builder](https://github.com/bmad-code-org/bmad-builder) | Reusable skill/workflow/module design | README and license |
| [bmad-code-org/bmad-method-test-architecture-enterprise](https://github.com/bmad-code-org/bmad-method-test-architecture-enterprise) | Test strategy and requirement traceability | README, license, selected skill contract |
| [bmad-code-org/bmad-loop](https://github.com/bmad-code-org/bmad-loop) | Deterministic CLI coordination and bounded attempts | Selected adapter, profile, documentation |
| [obra/superpowers](https://github.com/obra/superpowers) | Discovery, TDD, diagnosis, verification | Selected README and skills |
| [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) | Focused intent discovery and engineering practice | Selected README, intake skill, host guide |
| [ericrisco/rsc-harness](https://github.com/ericrisco/rsc-harness) | Exact-plan onboarding and project knowledge | Selected implementation, test source, README |
| [buildermethods/agent-os](https://github.com/buildermethods/agent-os) | Discoverable project standards | README |
| [disler/super-simple-software-factory](https://github.com/disler/super-simple-software-factory) | Phase/run acceptance, typed envelopes, traces | Selected implementation and README |
| [strongdm/attractor](https://github.com/strongdm/attractor) | Graph/state/handler and human-node contracts | README and selected specification; not execution |
| [fabro-sh/fabro](https://github.com/fabro-sh/fabro) | Graph routing, checkpoints, human gates | README; cloud and fallback choices need review |
| [Shopify/roast](https://github.com/Shopify/roast) | Ruby workflow composition and reusable scopes | Selected README |
| [langchain-ai/deepagents](https://github.com/langchain-ai/deepagents) | Context, memory, skills, filesystem backends | README; alternative runtime, not a drop-in adoption |
| [OpenHands/software-agent-sdk](https://github.com/OpenHands/software-agent-sdk) | Tools, conversations, workspaces, events | Selected README |
| [SWE-agent/mini-swe-agent](https://github.com/SWE-agent/mini-swe-agent) | Small linear trajectory and shell loop | Selected README |
| [github/copilot-sdk](https://github.com/github/copilot-sdk) | Explicit CLI connection and pre-tool hooks | README and selected official SDK documentation |
| [github/gh-aw](https://github.com/github/gh-aw) | Read-oriented agent jobs and separate validated writes | Selected README; runs through GitHub Actions |
| [vercel-labs/eve-software-factory-template](https://github.com/vercel-labs/eve-software-factory-template) | Station handoffs, review wrapper, approval distinctions | Selected implementation, instructions, README |
| [coleam00/ai-software-factory](https://github.com/coleam00/ai-software-factory) | Release intent, journeys, holdouts, scheduling | Selected README/root inventory; license unresolved |
| [microsoft/waza](https://github.com/microsoft/waza) | Trials, evidence-bound grading, runtime distinctions | Selected implementation, test source, documentation |
| [promptfoo/promptfoo](https://github.com/promptfoo/promptfoo) | Comparative evaluation and explicit data routes | README, selected implementation, privacy guide |
| [rigour-labs/rigour](https://github.com/rigour-labs/rigour) | Evidence-backed lessons, counterevidence, withdrawal | Selected implementation and documentation |
| [EveryInc/compound-engineering-plugin](https://github.com/EveryInc/compound-engineering-plugin) | Work/review/learning continuity | Selected workflow guides |
| [open-gsd/gsd-core](https://github.com/open-gsd/gsd-core) | Durable phase artifacts and bounded context handoffs | README |
| [gsd-build/get-shit-done](https://github.com/gsd-build/get-shit-done) | Historical pointer to GSD Core | README/metadata; archived at observation |
| [anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins) | Engineering review/debug/test/documentation workflows | Selected engineering-package README and manifest |
| [gitleaks/gitleaks](https://github.com/gitleaks/gitleaks) | Deterministic credential-pattern scanning | Selected README |
| [Pester/Pester](https://github.com/Pester/Pester) | PowerShell assertions, mocks, coverage | Selected README and actual license |
| [humanlayer/12-factor-agents](https://github.com/humanlayer/12-factor-agents) | Owned control flow, pause/resume, bounded recovery | Selected README/factor text; linked diagrams not reviewed |
| [zazencodes/zazencodes-season-3](https://github.com/zazencodes/zazencodes-season-3) | Artifact ownership and a complete review-round barrier | Selected v1 contracts; v2 README/license only |

## Licensing is scoped evidence, not blanket clearance

The catalog's root-license classifications come from the earlier recorded
license review, not merely an API badge. Most roots were classified MIT.
Important exceptions and limits:

- BMad repositories and Pester had API `NOASSERTION` observations, but the
  recorded grant review classified BMad as MIT and Pester as Apache-2.0.
  BMad trademark notices remain a separate concern.
- Attractor and the engineering-plugin repository have Apache-2.0 roots.
- 12-Factor Agents separates its Apache-2.0 code grant from the README's
  CC-BY-SA-4.0 declaration for written content. Do not treat prose as code.
- Promptfoo's grant was classified MIT from its terms despite the absence of
  an MIT title.
- No root reuse license was established for the Archon-based factory wrapper
  or ZazenCodes root/v1 material. These remain reference-only; an informal
  invitation to copy is not a complete redistribution assessment.
- The ZazenCodes **v2 subtree** has a GPLv3 license. It does not license sibling
  directories retroactively and is not a noncommercial-only restriction.
  Applicability to a concrete reuse/distribution needs its own review.

This is not legal advice or a transitive license audit. Reusing an idea in
original words differs from copying code or adapting instructional text.
Any approved source reuse needs exact upstream paths and pins, applicable
copyright/license/notice handling, modification records, dependency review,
and the selected files' terms. This reference grants no new rights.

## Portability and adoption checks still open

Qualify the exact host, binary/version, shell, identity, plugins, lifecycle,
permission hooks, cancellation, and data destinations. A custom CLI override
does not prove protocol compatibility; SDKs can bundle their own standard
runtime. A Linux or macOS observation is not native Windows acceptance.
An offline bundle must contain the reviewed target-platform dependencies,
not just a manifest.

Do not silently substitute providers or adopt broad permission flags, cloud
sandboxes, telemetry, transcript discovery, automatic merge, or deployment.
Git worktrees separate working files, not all processes, credentials, data,
ports, or side effects. Hashes bind bytes, not authority.

The next evidence needed for any adoption is narrow: inspect the chosen
version and terms, define its allowed data/actions and failure behavior, then
run authorized local contract and recovery checks on the actual target.
Until that happens, compatibility and effectiveness remain `NOT_ASSESSED`.
