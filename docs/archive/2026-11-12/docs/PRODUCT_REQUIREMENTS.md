# SparkForge product requirements

**Baseline:** publication-safe requirements, 2026-11-11.

These are the owner's product goals and project-authored engineering
requirements. They do not quote or establish a private platform's policies.
The implemented local slice is narrower than the complete target product.

## Purpose and roles

Help people turn permitted ideas, code, playbooks and knowledge into supported
SPARK components or compatible changes to existing components. The user owns
intent and domain acceptance. Maintainers own code review; operators own the
actual host, permissions, data routes and resources. Applicable release and
organization decisions remain with their real owners.

Responsibilities do not require one agent or account per role. No hosted
multi-user service, shared credential store, automatic cross-machine state
synchronization or unrestricted application generator is implied.

## Functional requirements

| ID | Requirement | Required distinction |
|---|---|---|
| SF-01 | Accept ideas, code, playbooks and knowledge | An input reference is not access or disclosure permission |
| SF-02 | Clarify requirements and acceptance in plain language | Use known authorized evidence before repeating questions |
| SF-03 | Assess existing platform/wiki capabilities first | Explain reuse/update/new and comparison limits |
| SF-04 | Obtain exact-brief approval before implementation | A title, silence or generated approval field is insufficient |
| SF-05 | Create or improve supported SPARK components | Do not relabel an unrelated application as a supported component |
| SF-06 | Author meaningful tests | A separate agent per test role is not required |
| SF-07 | Execute tests and analyze actual results | Check execution, a pass and demonstrated behavior differ |
| SF-08 | Review quality and security | Findings do not grant user or organizational authority |
| SF-09 | Correct failures and handle errors | Preserve failures and stop at accepted limits |
| SF-10 | Route feedback, defects and changed intent | Material changes invalidate affected approvals/evidence |
| SF-11 | Maintain docs, decisions and useful evidence | Do not commit sensitive runtime data |
| SF-12 | Revisit approved source knowledge when needed | Preserve provenance, permission and freshness limits |
| SF-13 | Use the operator-approved native Copilot host | Do not silently substitute a provider, launcher or account |
| SF-14 | Produce a working local candidate before submission | A mock, template or successful worker turn is not acceptance |
| SF-15 | Prepare delivery through an approved contribution route | No automatic production modification or review bypass |
| SF-16 | Qualify the initial Corp target independently | An environment label does not establish its permissions |
| SF-17 | Support later authorized Acro adaptation | No shared credentials, live bridge or inherited acceptance |
| SF-18 | Require explicit scope for repository/external effects | Local creation and source access do not grant export rights |
| SF-19 | Deliver useful user/operator/contributor documentation | Prepared material is not a published or accepted release |
| SF-20 | Use versioned specifications and controlled development | Bound workers, artifacts, tests and independent evidence |
| SF-21 | Include governed learning | Proposals cannot change their own policy, evaluator or authority |

## Nonfunctional requirements

| ID | Requirement | Qualification |
|---|---|---|
| NFR-01 | Least authority and explicit data/effect boundaries | Separate procedural guidance from actual enforcement |
| NFR-02 | Revision-bound evidence and decisions | Do not conflate source, spec, candidate, run and attempt |
| NFR-03 | Durable recovery and reconciled effects | A timeout is not proof an effect did not happen |
| NFR-04 | Privacy-preserving observability and retention | Keep useful diagnostics without secrets or raw traces |
| NFR-05 | Portability within declared support | Qualify the exact host, package, paths and dependencies |
| NFR-06 | Finite resources and cancellation | Missing authorization never means unlimited resources |
| NFR-07 | Maintainability and reproducibility | Prefer small reversible changes and explicit dependencies |
| NFR-08 | Meaningful repeatable validation | Include negative controls and independent acceptance |
| NFR-09 | Understandable operation | Explain questions, state, failures and next actions |
| NFR-10 | Supply-chain and distribution discipline | Resolve source terms, ownership and delivery provenance |

## Observable journeys

1. The user supplies an idea; the factory inspects permitted knowledge and
   existing code, clarifies gaps and proposes a reviewable specification.
2. The operator accepts, rejects or requests changes to that exact specification.
   Missing approval stops implementation; it is not interpreted as consent.
3. The host implements an accepted delta. Declared commands produce actual check
   evidence, and a separate reviewer examines the same candidate and context.
4. An in-scope failure enters a bounded repair loop. Changed intent returns to a
   new decision; the original failure and attempts remain recorded.
5. A stopped or interrupted run is reconciled before resuming. No invisible
   inference retry or duplicate external write follows from a lost connection.
6. A reviewed local candidate is handed to the user. Publication, installation,
   deployment and organizational acceptance remain distinct effects.
7. Permitted outcomes may produce an inactive improvement proposal or an honest
   no-change assessment. Evaluation and promotion remain independently governed.

## Current slice and open decisions

The native package implements an operator-assisted workflow and deterministic
snapshot/spec/check/review helpers. Actor strings are assertions, not identity
proof. The host/operator retains authority, isolation and source-data controls.
Python and SQLite are local implementation choices, not production-store or
environment qualifications.

The preview remains fictional and tab-local. Governed promotion/rollback,
actual model-driven acceptance, live connectors and installed-host lifecycle
are still target work. Numeric product SLOs, live budgets and deployment
profiles must be approved rather than inferred from engineering test limits.

The public [learning study](research/SELF_IMPROVEMENT.md) informs SF-21 without
installing another framework or claiming that source research is an executed
learning mechanism.
