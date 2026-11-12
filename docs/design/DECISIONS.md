# Technical decisions

This source-neutral register separates implemented local choices from open
deployment decisions. It describes this project's design, not an organization's
private policies or a historical approval transcript.

## D-001: component output and collaboration scope

**Requirements:** SF-01, SF-05, SF-14, SF-19, SF-20.

Target supported SPARK components and scoped improvements, not arbitrary
application generation. Collaboration means reviewable specifications, code,
findings and evidence; a hosted multi-user service is not implied.

## D-002: authority separation

**Requirements:** SF-04, SF-08, SF-15, SF-18, SF-19, NFR-01, NFR-02.

Intent, execution permissions, technical readiness, organizational acceptance
and release are separate. A model, schema, successful command or private
repository cannot grant the other authorities.

## D-003: exact approved host

**Requirements:** SF-13, SF-16, NFR-01, NFR-05, NFR-06.

OPEN: select and qualify the actual host/build/profile for a real deployment.
Native metadata or an available executable is not that selection. Never
silently replace a host, identity, provider or endpoint.

## D-004: native composition and minimal control plane

**Status:** retained as assisted-v1 implementation history; superseded for target composition by D-026.

**Requirements:** SF-05, SF-11, SF-13, SF-20, NFR-07, NFR-09.

IMPLEMENTED LOCAL CHOICE: one agent/skill uses existing host reasoning and
tools; small Python helpers provide deterministic source/spec/check/state
mechanisms. No separate model SDK, hosted scheduler or redundant factory stack.

## D-005: supported component matrix

**Requirements:** SF-03, SF-05, SF-06, SF-14, SF-19, NFR-05, NFR-08.

The initial package targets native agent/skill workflows and scoped code changes.
Do not claim universal component, application or MCP-server generation.
Expand support only with explicit contracts and representative acceptance.

## D-006: actual enforcement feasibility

**Requirements:** SF-04, SF-09, SF-13, SF-15, SF-21, NFR-01, NFR-02, NFR-06.

OPEN: qualify real identity, permissions, isolation and protected acceptance.
The current mode is operator-mediated assistance. Prompts, paths and local
digests do not supply a security boundary or unattended enforcement.

## D-007: source and effect policy

**Requirements:** SF-01, SF-12, SF-13, SF-16, SF-18, SF-21, NFR-01, NFR-04, NFR-10.

The operator selects permitted sources, provider/storage routes, credentials
and effects. Acquired instructions are data. The publication excludes private
inputs/history rather than assuming permission to export them.

## D-008: durable local state

**Requirements:** SF-11, SF-18, SF-20, NFR-02, NFR-03, NFR-04.

IMPLEMENTED LOCAL CHOICE: a new explicit SQLite job directory, separate from
the controlled candidate, stores transactional state/events and operation
reservations. Production-store, synchronization and power-loss claims are open.

## D-009: immutable decisions and evidence

**Requirements:** SF-04, SF-07, SF-10, SF-11, SF-21, NFR-02, NFR-08.

Canonical specs, controlled-byte manifests, exact check commands and current
review context prevent accidental stale admission. Material changes require
new decisions/evidence. For the coordinated target, distinguish unchanged intent from technical plan revisions under D-027; v1 continues to bind its entire frozen spec. Same-privilege tampering and actor authentication remain
outside the helper's trust claims.

## D-010: ownership and concurrency

**Requirements:** SF-09, SF-20, NFR-01, NFR-03, NFR-06.

Use explicit ownership, disjoint writes and an integration owner. Serial work
is valid. Optional concurrency needs actual isolation and resources; a worktree
or a worker name is not proof of confinement.

## D-011: source-aware comparison

**Requirements:** SF-01, SF-02, SF-03, SF-12, NFR-04, NFR-07, NFR-10.

IMPLEMENTED LOCAL CHOICE: verified indexed snapshots and explicit selected
implementation files, not a new crawler/vector service. Lexical search is only
a candidate aid. Live freshness and authorization are not inferred from hashes.

## D-012: complete evidence and independent review

**Requirements:** SF-06, SF-07, SF-08, SF-09, SF-14, SF-20, SF-21, NFR-08.

Require the accepted check/reviewer inventory. Capture review context before
inspection and submit the same token; any change requires re-review. A
different actor string alone does not establish independence.

## D-013: finite resources and stopping

**Requirements:** SF-09, SF-13, SF-20, SF-21, NFR-03, NFR-04, NFR-06.

Checks declare timeout, output and attempt limits. An unchanged spec cannot
reset attempts. Actual model budgets and product SLOs remain operator decisions.
Direct-child termination does not prove all descendant effects stopped.

## D-014: reconciliation before retry

**Requirements:** SF-09, SF-10, SF-11, SF-15, SF-21, NFR-03.

Reserve intent before dispatch and preserve uncertain state. A timeout,
disconnection or missing response cannot justify blind replay. Reconciliation
records a real assessment, not an automatic retry token.

## D-015: owned packaging and discovery

**Requirements:** SF-05, SF-13, SF-14, NFR-05, NFR-10.

IMPLEMENTED LOCAL CHOICE: fixed owned resources, new output directories and
digest inventories for two experimental metadata profiles. Structural assembly
does not qualify an installed host or supply an authorized installer.

## D-016: contribution and documentation delivery

**Requirements:** SF-14, SF-15, SF-18, SF-19, NFR-10.

Prepare code, evidence and documentation locally; execute a contribution only
under its exact destination/payload authority. Development repository
publication is distinct from program submission, distribution or deployment.

## D-017: independent target adaptation

**Requirements:** SF-16, SF-17, NFR-01, NFR-05.

Corp and Acro are independent requested targets. No credential/state bridge,
automatic data transfer or inherited acceptance is designed. Qualify target-local
requirements and approved sources separately.

## D-018: public prior art and adoption

**Requirements:** SF-03, SF-13, SF-20, SF-21, NFR-07, NFR-10.

Use public research to choose bounded mechanisms, not install every framework.
Preserve path-specific license, platform, review-depth and execution limits.
A repository-level badge is not complete dependency or redistribution clearance.

## D-019: engineering dogfooding and self-hosting

**Requirements:** SF-20, SF-21, SF-11, NFR-07, NFR-08.

The engineering harness may run the factory's own tests with explicitly
synthetic decisions. It must not manufacture reviewers or human acceptance.
Changed publication bytes need their own evidence; private historical tokens
are not imported. Autonomous self-hosting remains separate.

## D-020: ownership, terms and support

**Requirements:** SF-14, SF-19, NFR-07, NFR-10.

OPEN: confirm real maintainers, applicable support duties and distribution terms
at the requested stage. Do not invent identities, code-owner decisions or a
public license. Public-source research retains upstream terms.

## D-021: live acceptance targets

**Requirements:** SF-07, SF-08, SF-14, SF-16, SF-21, NFR-04, NFR-08.

OPEN: define representative tasks, baselines, independent rubrics, allowed data
and finite resources before live trials. Synthetic helper tests cannot be
relabeled as an actual user or deployed-provider evaluation.

## D-022: helper language and dependencies

**Requirements:** SF-13, NFR-05, NFR-07, NFR-10.

IMPLEMENTED LOCAL CHOICE: Python 3.10+ standard library. Git supports project
checks. The fictional static preview and its Node tests were retired in the WP-100 reorganization; Node is no longer required. No runtime
framework, dependency acquisition or model service is automatically installed.

## D-023: genuine decision origin

**Requirements:** SF-04, SF-10, SF-21, NFR-01, NFR-02, NFR-09.

The manual decision/reconciliation interface is operator-owned. Worker content,
silence and editable actor labels are not authenticated consent. A future
trusted ingress needs actual host support, display/binding and revocation proof.

## D-024: bounded schema evolution

**Requirements:** SF-12, SF-17, SF-20, NFR-05, NFR-07.

Reject unknown versions/fields rather than silently accepting changed meaning.
Review migrations and evidence invalidation before extending persisted records.
Future adapters must retain permissions, scope and explicit failure semantics.

## D-025: governed improvement lifecycle

**Requirements:** SF-21, SF-04, SF-08, SF-09, SF-10, SF-11, SF-20, NFR-01, NFR-02, NFR-03, NFR-06, NFR-08, NFR-10.

REQUIRED TARGET: permitted observations, inactive proposals, independent
evaluation, exact promotion, monitoring and safe withdrawal. No-change is valid.
The learner cannot change its own authority, protected acceptance, provider or
budget. The current workflow does not claim promotion/rollback is implemented.

## D-026: coordinated roles with a deterministic control plane

**Requirements:** SF-20, SF-22, SF-23, SF-24, SF-27, NFR-07.

ACCEPTED TARGET: distinct brain, intent controller, coder, test author, reviewer and diagnostician responsibilities, with deterministic test execution and coordination. Supersedes D-004 as destination; the old package remains assisted. Sequential agents first; concurrency is optional.

## D-027: material decisions and split artifacts

**Requirements:** SF-04, SF-10, SF-25, SF-26, NFR-01, NFR-02.

ACCEPTED TARGET: separate intent, execution envelope, technical plan and evidence. Ordinary bounded repairs/replans preserve intent approval after controller/admission checks. Material behavior/authority/resource changes need their decision owner. Do not bypass current v1 manual decisions while implementing this target.

## D-028: explicit host protocol before native wiring

**Requirements:** SF-13, SF-22, SF-27, SF-30, NFR-03, NFR-05.

ACCEPTED TARGET: a small capability-based adapter plus deterministic fake. No model SDK/framework choice or native launcher is implied. Actual host/build capability selection remains OPEN at P6; absent features narrow support rather than silently changing providers.

## D-029: job-wide resource and recovery invariants

**Requirements:** SF-09, SF-28, SF-29, SF-30, NFR-03, NFR-06.

ACCEPTED TARGET: operation reservations, idempotency, typed failures, no-progress detection and aggregate budgets survive task/plan/agent changes. Unknown usage/effects stay unknown. Existing per-check v1 bounds are reused, not mistaken for complete job accounting.

## D-030: environment-local knowledge and independent target evidence

**Requirements:** SF-03, SF-12, SF-16, SF-17, SF-23, NFR-01, NFR-04, NFR-05.

ACCEPTED TARGET: each run uses one selected platform/environment profile. corp and acro keep separate credentials, sources, journals and model routes. Shared reviewed code does not require a live bridge or export of corp runtime knowledge.

## D-031: protected oracle and progressive evidence

**Requirements:** SF-06, SF-07, SF-08, SF-14, SF-24, NFR-08.

ACCEPTED TARGET: define known-good/known-bad behavioral fixtures first, then fake-host integrations, fault/recovery cases and actual installed model journeys. Do not relabel fixture-authored repairs, worker prose, metadata or historical receipts as live acceptance.

## D-032: one active roadmap and explicit history

**Requirements:** SF-11, SF-19, SF-20, SF-31, NFR-07.

IMPLEMENTED PLANNING CHOICE: active work begins WP-100; old IDs/scenarios remain in a byte-preserved archive for old cycles. Remove the disconnected fictional preview; preserve runtime tests and research/source bytes. Publication/private-corpus history no longer dominates active milestones.

## D-033: core factory before optional expansion

**Requirements:** SF-14, SF-17, SF-21, SF-31, NFR-07, NFR-09.

ACCEPTED DELIVERY ORDER: core serial factory, recovery and first-environment installed qualification precede optional measured parallelism and learning promotion. Acro remains an independent target with its own priority/context, not a hidden prerequisite for the first local release.
