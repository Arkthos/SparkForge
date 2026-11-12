# Capability-to-resource and reuse map

**Edition:** 2026-11-12, preserving the public comparison from the
2026-11-05 study. The `PA-R` labels refer to the
[publication scope](SCOPE.md#comparison-questions), not the current
implementation backlog. The table is a research comparison, not a dependency
selection or a claim that each capability has been built.

The source-specific organization, inventory, packaging, and rollout columns
of the original map are withheld. The questions below concern general
product requirements and publicly observed mechanism limits; they do not
assert hidden facts about a substitute organization.

## Complete capability comparison

| Question | Public prior art | Mechanism worth preserving | Evidence or adaptation still required |
|---|---|---|---|
| PA-R01: heterogeneous intake | [Agent Skills](CATALOG.md#addy-skills), [Foreman](CATALOG.md#eve-foreman), [BMad Method](CATALOG.md#bmad-method) | Intent extraction, work classification, clarification before action | Establish permitted source formats, locations, accounts, sensitivity, and connectors; an idea does not grant source access |
| PA-R02: understandable requirements | [Superpowers](CATALOG.md#superpowers), [Spec Kit](CATALOG.md#spec-kit), [OpenSpec](CATALOG.md#openspec) | Context-first questions, desired outcomes, non-goals, structured artifacts | Produce a domain-friendly brief and component-specific criteria without asking the user to act as a software architect |
| PA-R03: reuse before creation | [RSC](CATALOG.md#rsc-harness), [Agent OS](CATALOG.md#agent-os), [Compound Engineering](CATALOG.md#compound-engineering) | Evidence-backed selection, relevant standards, prior-learning lookup | Search an actually authorized current inventory; record reuse/update/new reasoning and unavailable evidence separately |
| PA-R04: accepted brief | [RSC acceptance](EVIDENCE.md#rsc-acceptance), [Spec Kit gate](EVIDENCE.md#spec-kit-gate), [Superpowers intake](EVIDENCE.md#superpowers-intake) | Exact artifact binding, pause/resume, explicit rejection | Authenticate the decision and bind it to the current brief; a readable digest or model-supplied verdict is not consent |
| PA-R05: component creation and updates | [BMad Builder](CATALOG.md#bmad-builder), [Agent Skills packaging](EVIDENCE.md#addy-copilot), [engineering plugin](CATALOG.md#engineering-plugin) | Structured packages, skills, commands, references, dependency-aware generation | Match the selected target's actual extension points and manifest contract rather than another marketplace's format |
| PA-R06: test writing | [TEA](CATALOG.md#bmad-tea), [Superpowers TDD](EVIDENCE.md#superpowers-tdd) | Risk-based design, meaningful red tests, test-quality review | Preserve accepted behavior as the oracle; do not let the builder weaken it or delete legitimate existing work |
| PA-R07: test execution and analysis | [Pester](CATALOG.md#pester), [Waza](CATALOG.md#waza), [SSSF acceptance](EVIDENCE.md#sssf-run-acceptance) | Deterministic runners, recorded assertions, acceptance distinct from execution | Bind checks to the candidate; distinguish product defects, unavailable infrastructure, skipped checks, and missing evidence |
| PA-R08: quality and risk review | [Agent Skills](CATALOG.md#addy-skills), [Rigour](CATALOG.md#rigour), [Gitleaks](CATALOG.md#gitleaks), [Foreman reviewer](EVIDENCE.md#eve-review-wrapper) | Focused review, deterministic analysis, separate review context | Define actual trust boundaries, permitted tools, protected criteria, and escalation; no model review or clean scan is a complete safety proof |
| PA-R09: repair and error handling | [SSSF calls](EVIDENCE.md#sssf-agent-calls), [BMad Loop](CATALOG.md#bmad-loop), [12-Factor errors](EVIDENCE.md#factor-errors) | Typed outcomes, bounded corrections, persistent state, deferral and escalation | Keep malformed output, failed tests, environment faults, denied authority, cancellation, and uncertain external completion distinct |
| PA-R10: changes and feedback | [Foreman](CATALOG.md#eve-foreman), [BMad Loop](CATALOG.md#bmad-loop), [Compound Engineering](CATALOG.md#compound-engineering) | Common intake, deferred-work ledger, reviewed learning | Route changed requirements through a new decision when needed; retain prior scope and outcomes |
| PA-R11: documentation and logs | [SSSF tracing](EVIDENCE.md#sssf-tracing), [RSC receipts](EVIDENCE.md#rsc-acceptance), [GSD Core](CATALOG.md#gsd-core) | Task/run/phase identities, decisions, handoffs, durable current state | Keep confidential logs out of the publication; preserve useful, qualified evidence and an explicit retention policy |
| PA-R12: continuing project knowledge | [Agent OS](CATALOG.md#agent-os), [RSC](CATALOG.md#rsc-harness), [Rigour lessons](EVIDENCE.md#rigour-lessons) | Relevant retrieval, provenance, candidate versus verified lessons, retirement | Establish authorized refresh and source precedence; a frozen snapshot or repeated inference is not permanent authority |
| PA-R13: selected host integration | [Copilot SDK](CATALOG.md#copilot-sdk), [BMad profile](EVIDENCE.md#bmad-loop-copilot), [Waza CLI](EVIDENCE.md#waza-cli) | Explicit adapter/connection boundaries, lifecycle events, configured executable selection | Qualify the exact executable/version, protocol, authentication, permissions, discovery, and cancellation; do not substitute a bundled host silently |
| PA-R14: meaningful local readiness | [SSSF](CATALOG.md#sssf), [TEA](CATALOG.md#bmad-tea), [Waza](CATALOG.md#waza) | Whole-run acceptance, realistic fixtures, behavioral regressions | Define the complete selected acceptance boundary; a dry run, mock, or manifest parse does not establish a working user journey |
| PA-R15: reviewable delivery | [Foreman policies](EVIDENCE.md#eve-approval), [GitHub Agentic Workflows](CATALOG.md#gh-aw) | Reasoning separated from privileged effects, separate shipping decision | Use the actual selected branch/PR and permission contract; public patterns do not authorize automatic merge, deployment, or data export |
| PA-R16: independent profile qualification | [Rigour profiles](EVIDENCE.md#rigour-profiles), [SDK connection](EVIDENCE.md#sdk-local-cli) | Explicit identity/configuration and scoped state | Prove actual environment boundaries; configuration separation neither creates a transfer bridge nor establishes process isolation |
| PA-R17: reproducible permitted handoff | [Spec Kit offline](EVIDENCE.md#spec-kit-offline), [RSC provenance](EVIDENCE.md#rsc-acceptance) | Reviewed dependency payloads, exact revisions, rationale, receipts | Resolve transfer rights, target-platform dependencies, host differences, and target-local acceptance separately |
| PA-R18: explicit research handling | [Compatibility boundaries](COMPATIBILITY_AND_LICENSING.md), [coverage](COVERAGE_AND_VALIDATION.md) | Distinct source reading, execution permission, artifact retention, and publication decisions | A study does not authorize an installer's telemetry, a scheduler, a provider, an external write, or release of excluded records |

The [ZazenCodes follow-up](VIDEO_ZAZEN_FACTORY.md) adds specific lessons across
this map: one intended owner per artifact, an expected complete review set,
per-job identities, worktrees and ports, bounded resumptions, human-facing
blockers, and visible integration friction. It supplements the mechanisms;
its model-approved local merge does not replace the accepted-brief or
external-action boundary.

## Reuse is not one decision

### Reuse an existing capability

First determine whether an available, authorized component already owns the
required behavior. Check its current contract, side effects, dependencies,
permissions, and maintenance ownership. A public framework shortlist is not a
substitute for that search. Where the comparison source is missing, state the
coverage limit rather than claiming that a new implementation is necessary.

### Adapt a small module or skill

Source reuse can be appropriate when the chosen file's license permits it,
required notices are preserved, the dependency closure is understood, and the
instructions fit the actual host and approved operating model. A single
`SKILL.md` may rely on scripts, sibling references, hooks, or conversion logic.

The reuse record must identify what was adapted and from which exact upstream
revision. Host-specific tool names, permission declarations, command discovery,
and implicit state locations require deliberate work. A familiar Markdown
format is not evidence that runtime behavior is portable.

### Reuse a design or test pattern

Sometimes importing a runtime creates more cost or risk than it removes.
SSSF's phase-versus-acceptance distinction, OpenSpec's artifact dependencies,
RSC's revision binding, and Waza's refusal of missing verdicts are useful
without importing the full respective frameworks.

This is not an excuse to recreate a library uncritically. Identify the small
contract actually needed and preserve its failure behavior. A simplified
design that drops rejection, attribution, or bounded correction has lost the
important part of the prior art.

### Use a product as a comparison only

Foreman is valuable for understanding classification, analysis, construction,
review, project knowledge, and draft-PR delivery. Its actual hosted sandbox
also illustrates why the product is not automatically the correct local
runtime. Fabro, Deep Agents, OpenHands, Roast, and the Archon wrapper raise
different provider, hosting, dependency, licensing, and authority questions.

"Useful reference," "permitted source adaptation," "installed dependency,"
and "accepted deployment" are separate dispositions. A shortlist should never
silently turn one into another.

## What was not established by the public landscape

The bounded study did not demonstrate a ready-made package combining:

- accessible domain-expert intake;
- an authorized, current comparison against the selected component inventory;
- exact host, identity, permission, and lifecycle compatibility;
- component-specific generation, packaging, testing, and review;
- revision-bound human intent and independent readiness evidence; and
- separately qualified deployment and permitted transfer.

This is a statement about the reviewed evidence, not proof that no such
product exists. It is also not a reason to rebuild every stage. The detailed
matrix identifies substantial existing work for each part while keeping
missing integration evidence visible.

## Distinctions to test in an adoption decision

| Do not conflate | Practical consequence |
|---|---|
| A specification exists / the specification is accepted | Artifact creation is not approval |
| A digest matches / the decision is authenticated | A model can echo a hash it is able to read |
| A tool was invoked / intended behavior was demonstrated | Commands can fail, return partial data, or check the wrong candidate |
| An agent reports success / the whole job is accepted | Self-report is one evidence input, not the verdict |
| A reviewer has a fresh context / review is fully independent | Mutable tests, common assumptions, tools, and implementer summaries can still bias it |
| A worktree is separate / the process is sandboxed | Filesystem, network, credentials, processes, and ports need their own boundaries |
| A local executable / local inference and storage | A local process may transmit all chosen inputs to a configured service |
| A compatible file format / compatible host behavior | Hooks, commands, paths, manifests, and permissions vary with implementation and version |
| One profile's evidence / another target's evidence | Acceptance does not transfer merely because the same source is installed |
| Ready for submission / approved for release | External acceptance and distribution remain independently authorized actions |

These distinctions are decision criteria, not an executed acceptance suite or
a development schedule. Current implementation evidence belongs in the
project's living records, not retroactively in this historical comparison.
