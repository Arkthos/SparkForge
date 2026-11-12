# Product questions and public research scope

**Publication edition:** 2026-11-12. **Historical comparison baseline:**
2026-11-05. This page preserves the public research lens and general
user-requested product goals. It does not reproduce a private operating brief.

The historical source mixed those goals with restricted source inventories,
specific organizational routing, and a then-current permission boundary.
Those facts are withheld. The comparison questions here are not assertions
that an unnamed organization has a particular policy, repository, deployment,
or existing implementation. Current authority remains with the
[project records](../../../docs/PROJECT_STATUS.md) and the operator's actual
permissions.

## Purpose and intended users

The requested factory helps domain experts turn ideas, existing code,
playbooks, and knowledge into maintainable components. A person can be expert
in an operational problem without being expert in programming. Useful intake
therefore explains outcomes, options, non-goals, constraints, and acceptance
evidence in understandable language.

This is not equivalent to an unrestricted application generator. The output
must fit the selected component and host contracts. Both a change to an
existing component and a later change to a previously generated component
belong in the product model. Reuse discovery precedes a decision to invent
another implementation.

Public sources can help design that experience. They cannot answer which
private materials the operator may read, what an inaccessible component does,
or what a target environment has actually accepted.

## Comparison questions

The `PA-R` labels below are local research-navigation IDs, **not** replacements
for the current project's requirement IDs or evidence that a feature is done.
The first fifteen retain the general capability questions of the original
study. The last three describe public adoption/handling questions; the
source-specific rollout and permission mapping is deliberately not reproduced.

| ID | Product or adoption question | Qualification that must survive reuse |
|---|---|---|
| PA-R01 | Can intake accept ideas, code, playbooks, and knowledge? | Ask for the actual source and permitted access; possession of an idea is not authorization to read another system |
| PA-R02 | Can the factory clarify behavior, constraints, requirements, and acceptance with a domain expert? | Read supplied, authorized context first; do not make the person reconstruct facts that the available evidence already answers |
| PA-R03 | Does it inspect existing capabilities before proposing new work? | Record reuse, update, or new work and the comparison coverage; unavailable evidence means `NOT_ASSESSED`, not absence |
| PA-R04 | Is the proposed brief accepted by the requester before implementation? | Bind the actual behavior, change boundary, and criteria to the accepted revision; an AI verdict is not a human decision |
| PA-R05 | Can it create or modify the selected kind of component? | Fit real manifests, interfaces, dependencies, and ownership instead of generating an unrelated generic app |
| PA-R06 | Can it write appropriate tests? | Test generation is a capability, not a commitment to one dedicated agent or a fixed test framework |
| PA-R07 | Can it execute checks and analyze the actual results? | Separate command execution, assertion results, missing infrastructure, and evidence of intended behavior |
| PA-R08 | Can it review software quality and relevant risks? | Use engineering practice and applicable deterministic checks; a model reviewer cannot confer external authority |
| PA-R09 | Can it correct failures and handle errors? | Explicit budgets, failure classification, cancellation, escalation, and reconciliation are design work, not infinite self-healing |
| PA-R10 | Can it accept changes, bug reports, and feedback? | A changed requirement may need a newly accepted revision; feedback is not invisible scope expansion |
| PA-R11 | Does it retain documentation, decisions, logs, failures, and evidence from the start? | Preserve useful recovery facts with appropriate access and retention; do not export raw confidential logs |
| PA-R12 | Can project knowledge be revisited and maintained? | A frozen reference is not continuing operational truth; preserve source owner, revision, precedence, and freshness |
| PA-R13 | Does the integration use the operator-selected coding host? | Verify executable, version, protocol, identity, permission behavior, plugins, and cancellation rather than silently selecting a bundled alternative |
| PA-R14 | Is local readiness demonstrated before broader submission? | Translate "working" into component-specific acceptance; parsing a manifest or passing mocks is insufficient |
| PA-R15 | Can it prepare reviewable branch/PR delivery? | Readiness, intent approval, external-write permission, maintainer acceptance, and distribution remain separate |
| PA-R16 | Can deployment profiles be qualified independently? | A profile name or state folder is not evidence of process isolation or another environment's acceptance |
| PA-R17 | Can a permitted engineering handoff be reproduced elsewhere? | Dependency closure, rights, rationale, limits, and target-local evidence must accompany any approved transfer |
| PA-R18 | Is research/publication handling explicit? | Local checks do not install candidates, grant access, approve new providers, or clear excluded content for a repository |

The requirements do not select a language, database, framework stack, model
routing policy, agent count, or one-role-per-agent topology. Different
responsibilities can be implemented by ordinary code, tools, a serial agent,
or appropriately bounded independent work. Naming responsibilities is not a
reason to spawn more agents.

## Separate the approval authorities

There are at least three distinct decisions:

1. **Intent:** the requester accepts what should be built and how success will
   be recognized, before implementation starts.
2. **Readiness:** tests, analyzers, and reviewers provide evidence and recommend
   correction or delivery within that accepted scope.
3. **External acceptance:** the relevant owner or maintainer decides whether
   a change may be submitted, merged, distributed, or otherwise acted upon.

Actual tool execution permission is also necessary. Acceptance of a feature
does not authorize arbitrary source reads, new credentials, model providers,
or external writes. Passing a readiness gate does not impersonate the
requester, authenticate a reviewer, or approve a release.

The prior art illustrates why this separation is necessary. Spec Kit can
consume a verdict from workflow input. RSC can verify a plan digest. Foreman
uses different predicates for different callers and actions. ZazenCodes v1
uses a model's approval to authorize a local merge. Those are different
mechanisms with different authority assumptions, not equivalent forms of
"human in the loop."

## Public sources and missing comparison

The [AI factory learning collection](../../ai-factory/README.md) supplies
conceptual foundations and proposed exercises. Its labs and synthetic worked
scenario were not executed by this study.

The [pinned repository catalog](CATALOG.md) supplies public selected-source
findings. The [inspection register](EVIDENCE.md) identifies the exact
documentation, configuration, implementation, or test-source ranges behind
those findings. No framework's complete execution behavior was qualified.

The private source inventories, original source pins, organizational practices,
and actual implementation comparisons from the contextualized brief are not
included. An adoption decision requiring that evidence remains
`NOT_ASSESSED` here. The reader must obtain an appropriately authorized
comparison source rather than infer that an existing capability does not
exist.

## The Risco example: inspiration, not an approval protocol

The original study revisited the supplied
[Eric Risco video](https://www.youtube.com/watch?v=p6nnqerea7w) using all
477 unique available Spanish automatic-caption segments, spanning
00:00-17:20. The earlier
[critical review](../../ai-factory/20-eric-risco-video-review.md) remains a
separate record with its own visual limitations.

| Historical timestamp range | Public topic retained | Interpretation |
|---|---|---|
| 04:00-05:29 | Persistent project knowledge | Knowledge is an explicit product capability, not merely context retained in chat |
| 06:34-08:11 | Common intake, grounded specifications, isolated work, test-driven builder | Useful workflow decomposition; no target-host qualification follows |
| 08:12-10:13 | Focused review roles | Review dimensions can be separate without requiring that topology for every component |
| 10:14-10:52 | A model consolidates feedback and requests rework | "Approver" names a model responsibility here, not human authority |
| 11:03-12:31 | Separate risk/human routing and supporting hooks/code | The walkthrough does not establish that every action is covered by an enforced gate |
| 12:32-13:50 | Identifiable parallel jobs and non-programmer users | The user experience and recovery identities are useful design concerns |
| 14:32-15:29 | Human review and upload in a content example | Do not generalize automatic promotion to every demonstrated workflow |

The video does not establish a universal human pre-code specification gate.
That gate is a project requirement, not a rule attributed to the video. The
creator characterizes the systems as proofs of concept, not comprehensive
production-control evidence.

The second historical pass added no new frame-level claim: advertising
interrupted fresh frame inspection. It did not erase or upgrade the earlier
qualified visual observations. This publication pass did not reopen the
player, copy captions, or acquire images.

## Research scope is not implementation authority

The historical task considered public projects, skills, products, proofs of
concept, theory, and documentation for reusable mechanisms. Inert source
collection and selected reading did not install or execute any of them.
Public queries used generic capability descriptions rather than private
source content.

This edition performs a narrower operation: publishing original public-source
analysis and bibliographic coordinates. It does not rerun the acquisition,
activate a captured prompt or installer, change providers, run paid
evaluations, create a repository, or deploy a component. Current project work
may have progressed since the historical study; that does not retroactively
turn the study into an implementation acceptance record.

Use the [reuse map](REUSE_MAP.md) to evaluate useful mechanisms and the
[compatibility chapter](COMPATIBILITY_AND_LICENSING.md) to identify what
still requires explicit evidence. A source-backed recommendation is a
starting point, not a selected architecture, security certification, or
permission to publish the original mixed-context dossier.
