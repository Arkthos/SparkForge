# Native factory slice contract

## Objective and status boundary

Provide a usable local evidence spine for a complete host-assisted
intent-to-candidate workflow. The host performs intake, source/code
inspection, focused clarification, reuse judgment, implementation and
independent review; owned helpers provide strict specs, durable state,
actual bounded checks and explicit recovery.

This is an implemented local software contract, not a claim that a native
host, provider or real operator task has been accepted. Corp and Acro are
independent unqualified deployment targets. Current live source coverage
remains `NOT_ASSESSED`. No private source recipes, historical jobs or
review receipts are part of this publication.

## Required behavior

1. **Evidence before architecture:** inspect authorized guidance, plausible
   existing components and relevant actual code/tests. Preserve source
   revisions, hashes, omissions and limits. Lexical matches are candidates,
   not semantic approval; unavailable comparison is not proof of absence.
2. **Explicit route:** justify `REUSE`, `UPDATE_EXISTING` or `NEW_COMPONENT`.
   Preserve existing behavior where reusing/updating. A reuse outcome must
   not force a duplicate implementation.
3. **Concrete frozen spec:** validate the closed `sparkforge.spec.v1`
   contract; bind source scope, controlled files, acceptance-to-check
   traceability, exact argument lists, finite limits and reviewer roles.
   Reject malformed, duplicate or foreign bindings.
4. **Stop for the operator:** initialize separate state and present the
   exact spec SHA. STOP before implementation for `accept`, `reject` or
   `changes`. `decide` is OPERATOR-OWNED. A worker cannot invent a decision.
5. **Real host implementation:** edit the accepted workspace using the
   host's existing authorized capabilities. The journal helper is not a
   code generator or permission service.
6. **Actual command evidence:** reserve the allowed attempt, execute the
   stored command, inspect exit/marker/limit results and bind the unchanged
   candidate. Refuse missing approval, unknown checks, unavailable files,
   active reservations and exhausted limits.
7. **Independent review:** require all accepted checks to pass first.
   The reviewer captures `review_context` before inspecting and submits
   the same token, bound to job ID, exact spec SHA, candidate SHA, check
   round and check-evidence sequence. Changed context requires re-review,
   never relabeling. Distinct actor labels do not establish independence.
8. **Bounded correction:** keep real failures visible. Repairs use
   remaining per-check/per-spec attempts. Changed candidate bytes need
   current checks and review; changed scope needs `revise` and a new
   operator decision. Do not replace jobs or toggle specs to evade limits.
9. **Unknown-effect recovery:** inspect existing `status` and `history`
   after interruption; never assume a disconnect means failure.
   `cancel` records a request. OPERATOR-OWNED `reconcile` records checked
   process/effect reconciliation without inventing success or refunding
   attempts.
10. **Local handoff:** `CANDIDATE_VERIFIED` requires current passing check
    and review records. It still reports human acceptance required and no
    publication authorization. Finish with limitations and the next human
    decision, plus an inactive improvement proposal or explicit no-change.

## Deliberate non-goals

- Authenticating actor strings or protecting a journal from a same-privilege
  writer.
- OS-level sandboxing, credential isolation, automatic network denial or
  proof that every descendant effect stopped.
- Live source acquisition, source permission verification or authoritative
  coverage from a supplied manifest.
- Hidden model calls, provider fallback, package/MCP installation,
  automatic publishing, deployment or lesson promotion.
- Treating the fictional browser preview as execution or approval evidence.

The runner inherits caller environment. Controlled files are digest inputs,
not a process access allowlist. One active check is supported per job;
independent concurrent work requires disjoint owned workspaces/job areas.
Use authorized persistent storage; filesystem checks are not cloud-storage
qualification.

## Verification surfaces

- `tests\test_native_factory.py`: strict spec/state contracts, actual local
  check processes, evidence binding, negative/stale review, finite repair,
  cancellation and reconciliation.
- `tests\test_native_knowledge.py`: indexed byte reads, query/selection
  bounds, citations, unsafe/missing/changed source rejection.
- `tests\test_native_integration.py`: synthetic source inspection through
  concrete spec, real check failure/repair, review binding and relocation.
- `tests\test_native_package.py`: fixed package inventory, profile
  transformations, structural integrity and executable instruction
  contracts, including pre-inspection review context.
- `tests\test_native_dogfood.py`: an expressly synthetic selfcheck decision
  does not fabricate a reviewer or human acceptance.

Tests and examples are local synthetic evidence when executed. Neither
their presence nor a passing local run qualifies a live host or provider.
Record actual command results separately in the project validation ledger.

## Shipped selfcheck

`specs\native-factory-selfcheck.json` retains ID `SFS-001-selfcheck`,
environment `LOCAL_DEVELOPMENT`, the `core-contracts` check and
`max_attempts: 2`. The check requires at least 43 core cases, all executed,
with no skips/expected failures and explicit completion markers.
Its candidate binds this contract document, the factory implementation and
the core test file.

Its knowledge locators, revisions and digests are synthetic schema
placeholders using `example.invalid` and repeated hex. They are not hashes
of real acquired sources or an accepted brief; current live coverage is
`NOT_ASSESSED`. Actual candidate/check bindings are computed at runtime.
The engineering harness may record its expressly labeled synthetic test
decision, but cannot export that as genuine operator acceptance. It stops
at review pending and records no automatic independent review.

See the [factory API](../engineering/NATIVE_FACTORY.md),
[spec format](../../plugins/sparkforge/references/SPEC_FORMAT.md) and
[authority contract](../../plugins/sparkforge/references/AUTHORITY.md).
