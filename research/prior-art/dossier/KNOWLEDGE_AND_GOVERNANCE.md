# Project knowledge, feedback, and governance

**Historical public-source analysis:** 2026-11-05. **Edition:** 2026-11-12.
This counterpart retains the public mechanisms and reasoning, not private
wiki content, source discrepancies, checkpoint identities, or transfer routes.

A project brain is not simply a large prompt or vector database. It contains
different kinds of information with different authority: policy, implementation
facts, accepted intent, execution state, candidate lessons, and verified
learning. Retrieval does not make those categories interchangeable.

## 1. Preserve the kind and authority of knowledge

| Kind | General example | Required distinction |
|---|---|---|
| Authoritative policy | A contributor or approval rule from its actual owner | Record owner, source revision, scope, and precedence |
| Observed implementation fact | A manifest or adapter's selected source behavior | Cite exact code and review depth; do not call it live enforcement |
| Accepted intent | The requester-approved brief and non-goals | Bind the decision to the accepted revision |
| Current execution state | Job, phase, attempt, artifacts, outstanding checks | Persist recoverable state rather than depend on chat memory |
| Candidate lesson | A suspected recurring failure pattern | Retain evidence, uncertainty, and proposed applicability without promoting it |
| Verified lesson | A reviewed invariant supported by actual outcomes | Keep it scoped, discoverable, revisable, and retireable |
| Untrusted acquired content | Issue text, documents, examples, tool outputs | Treat it as data, not instructions that can redefine authority |

A policy description, observed code behavior, and proven runtime control are
different statements. A knowledge system should preserve that distinction,
not flatten every retrieved sentence into an instruction.

This table is a general design model. It does not assert that a private
policy, repository, or live implementation in the original context has any
particular content.

## 2. Retrieve relevant context instead of dumping everything

[Agent OS](CATALOG.md#agent-os) describes discovering, indexing, and injecting
project standards relevant to the task. [RSC Harness](CATALOG.md#rsc-harness)
keeps knowledge, tools, skills, and working rules discoverable while explicitly
deferring or excluding unnecessary capabilities.

For a component change, relevant context may include the applicable package
contract, source ownership, existing alternatives, and contribution
requirements. Loading every unrelated document and tool schema can increase
cost and obscure the facts that matter.

Standards inferred from existing code need review before promotion. Repetition
does not prove that a pattern is intentional or desirable. A model should not
convert an accidental implementation convention into an authoritative rule.

Retrieval must retain provenance and uncertainty. If a source is unavailable,
the result is incomplete coverage, not "no existing solution." If a document
and selected source code disagree, identify the discrepancy and the relevant
authority instead of silently picking whichever is easiest to satisfy.
Actual private discrepancies are deliberately not included in this edition.

## 3. Current views and durable decision history serve different purposes

[RSC's application code](EVIDENCE.md#rsc-acceptance) inventories governed
artifacts, binds a selected plan, checks digests, and records provenance.
Its selected/deferred/excluded model makes the reason for not installing a
capability part of the knowledge record.

A factory needs both:

- a concise **current view** that makes the next action and present state
  discoverable; and
- an **evidence history** explaining earlier decisions, accepted revisions,
  failures, corrections, and changes.

Updating a current document does not justify rewriting which revision was
previously accepted or tested. Conversely, an append-only archive alone does
not tell the next worker what to do now. A useful maintained index connects
the two without turning an old result into current validation.

The digest guarantees content binding relative to the recorded baseline, not
who accepted it. State and receipts also need an authority and storage model;
they are not automatically tamper-proof because they are durable files.

## 4. Rigour: candidate lessons, decisions, and counterevidence

The [selected lesson-state implementation](EVIDENCE.md#rigour-lessons)
models accepted, rejected, dropped, and candidate states, precedence of
recorded human decisions, withdrawal and demotion, counterevidence blocking
promotion, and rejection of bot-only agreement as sufficient evidence.
Recurrence is evaluated across human-origin review observations.

That is useful feedback-governance prior art because it makes disagreement and
retirement part of the model. A learning store should not only accumulate
positive examples and forget contradictions.

The qualification matters: human-origin recurrence can promote a lesson
without a fresh explicit approval of that exact lesson. "Verified" in that
logic does not mean every promotion involved a new human click. An adoption
must decide which changes can be suggested, which can be promoted under an
already approved rule, and which require a new owner decision.

Multiple agents repeating an error should not turn the error into a standard.
A later fix or revert may supply evidence, but is not automatic causal proof
that a proposed lesson was responsible for an outcome.

[Rigour profiles](EVIDENCE.md#rigour-profiles) document scoped configuration,
identity, and state. That organization is useful; it does not prove operating
system isolation or make a repository name an authorization grant. Model
review, synchronization, setup hooks, and any added components also have
their own service and permission boundaries.

## 5. Compound Engineering: store the cheapest durable lesson

The [learning guide](EVIDENCE.md#compound-learning) asks whether a lesson is
non-obvious, durable, and material. When a test or lint rule can prevent
recurrence, that can be more useful than another narrative. An appropriate
standard or concise learning document can preserve reasoning that otherwise
would be lost.

Useful learning records retain:

- the root cause and evidence supporting it;
- failed approaches, not just the final successful story;
- the working solution and the circumstances where it applies;
- checks or outcomes that justify confidence; and
- a retirement condition, especially for an upstream-dependent workaround.

This counters a growing folder of duplicate or contradictory lessons that
nobody reads. It also makes "no useful new lesson" a legitimate outcome rather
than an incentive to invent one.

The same guide describes automatic discovery of histories across several
agent installations. That is a separate privacy decision. Permission to
maintain one project's knowledge does not imply access to unrelated personal,
customer, credential-bearing, or cross-project transcripts.

The [execution guide](EVIDENCE.md#compound-work) keeps verification,
canonical commits, and delivery with the host even when work is delegated.
Delegating implementation does not delegate away responsibility for evidence
or external-action authority.

## 6. Foreman: shared context mutation is a distinct effect

The [brain-writing tool](EVIDENCE.md#eve-brain-write) derives its storage key
from configured repository context rather than arbitrary model input. It
uses a specific policy and overwrites a bounded shared document, with an
explicit error result.

The [selected policy](EVIDENCE.md#eve-approval) denies shared-brain mutation
by unattended factory runs, permits trusted callers and scheduled app turns
without a card, and requires approval for other callers. This is not a
universal human-review gate.

Persistent shared context can affect many later jobs, so updating it is a
different authority from editing one work item. The public pattern is useful;
the exact upstream policy is not automatically appropriate elsewhere. Issue
content or tool output must not become trusted shared knowledge solely
because an agent copied it.

An editable brain document and an immutable history of why it changed are
complementary. A bounded overwrite does not by itself retain prior decisions,
withdrawals, or the evidence needed to undo a bad lesson.

## 7. Recovery is an explicit engineering contract

[12-Factor Agents](EVIDENCE.md#factor-pause) emphasizes launching, pausing,
resuming, and stopping work. Its [control-flow discussion](EVIDENCE.md#factor-control)
locates an important interruption point between selecting a tool and invoking
it. A pause after an irreversible effect cannot serve as pre-effect approval.

[SSSF traces](EVIDENCE.md#sssf-tracing) and
[Spec Kit state](EVIDENCE.md#spec-kit-state) provide selected concrete storage
mechanisms. [GSD Core](CATALOG.md#gsd-core) documents durable phase/context
artifacts across fresh sessions. These are useful inputs to recovery design,
not proof of one complete distributed transaction system.

| Recovery question | Failure it helps prevent |
|---|---|
| Which job and accepted brief are being resumed? | Mixing tasks or acting under stale intent |
| Which code, source, and configuration revisions apply? | Reusing checks for a different state |
| What completed, failed, paused, or remains uncertain? | Duplicate work and false completion |
| Which process or external operation is actually owned? | Interference with unrelated work |
| Which evidence is still valid? | Treating an earlier review as acceptance of a changed candidate |
| What decision is needed from a person? | Hiding missing intent, permission, or authority |

Connection loss is not evidence of job failure. When an external effect may
have occurred, automatic retry can duplicate it. Reconciliation against
durable receipts and actual state is more valuable than reconstructing a
confident story from the last chat message.

## 8. Knowledge transfer is not unrestricted data transfer

A permitted engineering handoff can include owned plugin material, dependency
identities, requirements, rationale, qualified test evidence, instructions,
known limits, and adaptation questions. It does not automatically include
every source record, raw prompt, model result, personal history, credential,
or log. Derived summaries may still be confidential.

A hash identifies bytes; it does not make the bytes or their metadata safe
to publish. A portable package must still be qualified with the receiving
host's permissions, sources, dependencies, and local evidence. No actual
cross-environment route from the original dossier is reproduced here.

The separate [self-improvement research](../../../docs/research/SELF_IMPROVEMENT.md)
adds public analysis of inactive proposals, no-change outcomes, evaluation,
and independent promotion. Neither that study nor this one demonstrates
measured learning improvement or grants a learner authority to promote itself.
