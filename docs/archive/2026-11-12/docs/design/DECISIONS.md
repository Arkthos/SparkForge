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
new decisions/evidence. Same-privilege tampering and actor authentication remain
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
checks; Node.js is used only for the existing static preview tests. No runtime
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
