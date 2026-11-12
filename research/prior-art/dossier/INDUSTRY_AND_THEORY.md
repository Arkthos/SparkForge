# Industry evidence and engineering principles

**Historical reading:** 2026-11-05. **Publication edition:** 2026-11-12.
Practitioner accounts explain why the same mechanisms recur. Their production
statistics remain self-reported and workload-specific. This edition neither
refreshes the articles nor reproduces their results.

The primary URLs and historical access status are also recorded in
[public context sources](public-context-sources.json). Full article bodies
are not redistributed. Private workload comparisons from the original topic
are withheld.

## 1. Stripe Minions: deterministic blueprints and bounded agent work

Both primary articles were read in the historical study:

- [Minions: Stripe's one-shot, end-to-end coding agents](https://stripe.dev/blog/minions-stripes-one-shot-end-to-end-coding-agents),
  published 2026-02-09.
- [Minions, Part 2](https://stripe.dev/blog/minions-stripes-one-shot-end-to-end-coding-agents-part-2),
  published 2026-02-19.

Stripe describes deterministic blueprint steps surrounding agent steps.
Known context gathering, common mechanical operations, and verification need
not all be negotiated with a model. Agent reasoning is used where reasoning
and implementation are valuable; ordinary code supplies predictable structure
around them.

Additional transferable ideas are:

- a curated tool set instead of an indiscriminate catalog;
- relevant, directory-scoped context instead of a giant universal prompt;
- inexpensive local feedback before costly CI iterations;
- bounded attempts to repair CI rather than endless self-correction; and
- PR delivery with human review.

The distinction between workflow structure and agent work matters more than
the names of individual roles. A deterministic preflight or test runner does
not need its own model turn to be a first-class factory capability.

Stripe's isolation also depends on standardized quarantined development
environments. A local worktree is not equivalent to that boundary. A reader
must qualify the actual execution and data environment rather than transplant
an industrial diagram into an unrestricted workstation.

Minions is an internal Stripe system, not a ready-to-install public package
audited here. The articles mention a fork of Goose. That source tree was not
captured or qualified by this study; [Goose](DISCOVERY_APPENDIX.md#additional-leads)
remains a separate lead. An industrial description is not evidence that its
implementation is available for reuse.

## 2. Uber: optimize useful outcomes under quality constraints

Primary source, historically read across two fetch ranges:
[Building an efficient software factory](https://www.uber.com/gp/en/blog/efficient-software-factory/),
published 2026-08-27.

Uber emphasizes workload-specific benchmarks, quality/reliability constraints,
model selection, context engineering, and spend visibility. The meaningful
objective is a useful accepted outcome at an acceptable total cost, not the
cheapest individual call.

| Public lesson | Design question for a component factory |
|---|---|
| Benchmark the actual workload | Are cases representative of the selected skill, adapter, query, or component rather than a generic coding leaderboard? |
| Ground work in relevant context | Can authorized retrieval and reuse search avoid a long investigation in the wrong direction? |
| Avoid unused tool schemas | Can progressive discovery reduce both context cost and selection confusion? |
| Move predictable sequences into code | Which collection and validation operations can run deterministically without a model turn per step? |
| Observe resources and failures | Are actual usage and failed attempts recorded, rather than assuming an upstream budget or price? |
| Learn from recurring inefficient behavior | Is each proposed improvement supported by permitted traces and measured outcomes? |

Uber's large context graph, organization-wide gateways, spend tiers, and
analytics are scale-specific implementation choices. They are not reasons
to add a large graph database or automatic cross-session transcript collector
to a small first implementation.

Productivity and cost numbers in a practitioner account are not forecasts
for this project. No comparable measurements on a selected coding host or
factory workload were performed here.

## 3. Long-running harnesses: leave reliable state for the next session

Historically read primary source:
[Anthropic: effective harnesses for long-running agents](https://www.anthropic.com/research/effective-harnesses-for-long-running-agents).
The engineering URL redirected to this research URL during retrieval.

The account separates initialization from later incremental coding sessions.
Feature records, progress artifacts, Git history, and end-to-end tests help
address two failures: attempting too much in one context and declaring the
whole task complete after only partial progress.

The transferable lesson is recoverable work plus verification of the actual
feature, including a user journey where appropriate. It is not a requirement
to adopt Claude, copy the example application, or use one particular
multi-agent topology.

The article explicitly leaves open whether a single general-purpose agent
or specialization is best for all workloads. Different capability labels in
a product specification therefore do not justify one agent per label.

Strong prompts about preserving tests are not security controls. Acceptance
artifacts and evidence still need whatever host/controller protections are
required by the selected authority model. The described process is useful
evidence about design, not proof that every shortcut is impossible.

## 4. 12-Factor Agents: own the consequential loop

The [pinned public resource](CATALOG.md#twelve-factor) contributes
practitioner principles that connect to the concrete controllers:

- own relevant context and prompts instead of surrendering them to opaque
  defaults;
- treat structured tool calls as proposals executed by ordinary code;
- retain meaningful business/execution state;
- expose pause/resume interfaces;
- contact people when intent or authority is missing; and
- provide useful error context with bounded recovery and escalation.

The [control-flow discussion](EVIDENCE.md#factor-control) identifies the
boundary between a proposed action and execution. A system able to pause
only after an effect cannot use that pause as pre-action permission.
The [launch/pause/resume section](EVIDENCE.md#factor-pause) also favors durable
continuation over an in-memory wait that disappears with the process.

The [error section](EVIDENCE.md#factor-errors) supplies conceptual guidance
and illustrative pseudocode, not audited production code to execute unchanged.
The [factor-12 text](EVIDENCE.md#factor-reducer-heading) is largely a heading
and diagram links. Those diagrams were not fetched or visually inspected and
do not establish an implemented reducer.

Its Apache-2.0 code grant and README-declared CC-BY-SA-4.0 written content are
different license scopes. This original analysis cites the ideas without
copying the manual or its illustrations.

## 5. Standards support portability, not universal enforcement

The [Agent Skills specification](https://agentskills.io/specification)
describes a `SKILL.md` entry point with optional scripts, references, assets,
metadata, and progressive disclosure. A focused entry point can load deeper
material when relevant instead of filling every task's context with it.

That is useful for both a factory's own skills and the components it
generates. A format standard does not mean every host honors the same
commands, hooks, tool permissions, or filesystem policy. The experimental
`allowed-tools` field explicitly varies by implementation.

The historically read
[GitHub Copilot CLI plugin reference](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-plugin-reference)
adds concrete packaging distinctions: legacy versus Agent Plugins manifests,
recognized schemas, component paths, repository versus managed configuration,
and updates. These are documentation observations, not a test of a
customized host. The mutable web pages were not newly fetched in this
publication pass.

## 6. Risco remains product inspiration, not authority

The [scope counterpart](SCOPE.md#the-risco-example-inspiration-not-an-approval-protocol)
retains all topic timestamps from the second historical transcript review.
The [earlier critical review](../../ai-factory/20-eric-risco-video-review.md)
remains separate, including its visual/access limits.

The common intake, project knowledge, builder, reviewers, rework, and human
routing are useful conceptual product decomposition. A model called an
"approver" is not the requester accepting the brief and is not a maintainer
accepting a release. The video does not demonstrate a universal pre-code
human specification gate.

The public [RSC Harness](CATALOG.md#rsc-harness) was studied independently.
The historical public author-repository listing did not locate a separately
named complete implementation of the demonstrated factory. That is a bounded
search result, not proof that such an implementation does not exist.

The [ZazenCodes supplement](VIDEO_ZAZEN_FACTORY.md) adds a complementary
view of a smaller factory evolving through real workflow friction. Its
different versions and authority choices should not be merged into one
imaginary implementation.

## 7. Connect to foundations without inflating coverage

The [AI factory collection](../../ai-factory/README.md) already provides
agent-loop, context/memory/RAG, tools/protocols, orchestration, evaluation,
security, economics, operations, and reference-architecture foundations.
Its [source guide](../../ai-factory/16-sources-and-reading-guide.md)
distinguishes primary reading, excerpts, and less-direct evidence.

This dossier adds detailed mechanism-level reuse comparisons rather than
replacing that foundation. The learning labs and worked scenario remain
unexecuted teaching material.

An [OpenAI harness-engineering page](https://openai.com/index/harness-engineering/)
was identified, but direct historical retrieval returned HTTP 403. It is
preserved as an inaccessible lead in the
[discovery appendix](DISCOVERY_APPENDIX.md#additional-leads), not used as
a newly read authority or silently replaced with secondary claims.
