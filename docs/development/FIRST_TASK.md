# First implementation task: WP-110

## Outcome

Implement strict IntentBaseline and ExecutionEnvelope records and deterministic validation/digest behavior. This is the smallest executable foundation for separating user intent from bounded technical execution. Do not implement a scheduler, actual agent calls, materiality classifier or replacement v1 workflow in this task.

## Entry and owned paths

WP-100 provides the planning baseline. Read the [target data/state](../design/DATA_AND_STATE.md), [human-decision policy](../design/HUMAN_DECISIONS.md), existing `factory.py` validation/canonicalization and native schema tests.

Proposed writes: `plugins/sparkforge/runtime/contracts.py`, minimal package initialization needed by real imports, `plugins/sparkforge/runtime/schemas/` if schemas are actually consumed, `tests/test_runtime_contracts.py`, and the four living records/new cycle. Do not add unused JSON-schema copies or a dependency solely to validate these small records. Keep existing assisted helpers/tests unchanged.

## Contract design to implement

Use closed explicit field sets and clearly named typed records/validation functions. The exact Python representation may be dataclasses or validated dictionaries, but callers must receive a canonical normalized value and typed errors. Document the chosen public functions in the task record.

| Record | Required fields / semantics |
|---|---|
| IntentBaseline | Schema version `sparkforge.intent.v1`; stable ID and positive revision; problem/outcome; audience; supported component kind; nonempty acceptance list of unique criterion IDs and observable behavior; non-goals; material constraints; source assumptions/references with explicit unknowns; no embedded approval/authentication flag |
| ExecutionEnvelope | Schema version `sparkforge.envelope.v1`; stable ID and positive revision; referenced intent ID/digest; one explicit environment and profile reference/revision; permitted workspace/data roots and tools/effects; selected host/provider route references; finite job/agent/check bounds; explicit treatment of unavailable usage; expiry/revocation representation; no credential material or self-issued authority |

The record is a proposal/binding, not an authenticated permission grant. Approval/origin ingress arrives in later tasks. A LOCAL_DEVELOPMENT fictional profile is legitimate in tests; never manufacture real wiki hashes or permissions just to make these records valid.

Represent source assumptions as known, unknown or unavailable with a reason; a source reference alone is not a freshness/permission assertion. Preserve meaningful user strings, reject forbidden control characters/oversized fields deliberately, and document finite limits. Avoid silent trimming/truncation that changes intent.

For paths, use the explicit supported path representation and environment semantics rather than interpreting a Windows path through a Linux Path parser. Test canonical relative identifiers separately from host-specific roots. Do not introduce an OS-sandbox claim from validation.

## Canonicalization and errors

Produce stable UTF-8 canonical JSON and SHA-256 from the full normalized record; object key order must not affect the digest, while semantically meaningful list order must be preserved unless the contract explicitly declares a set. Reject duplicate JSON keys on raw JSON input, unknown fields/versions, nonfinite numbers and boolean values passed as numeric bounds. Never drop fields from the digest to preserve approval accidentally.

Return explicit typed error codes/messages suitable for later CLI/result handling. Validation must be side-effect free: no job/store creation, source acquisition, environment probing, credential inspection, model call or decision recording.

## Required checks

1. Valid synthetic baseline/envelope round-trip; canonical key order yields identical digest.
2. Changing behavior, non-goal, material constraint, environment/provider/effect or bound changes the appropriate digest.
3. Duplicate/missing criterion IDs, empty observable acceptance, unknown keys/versions and mismatched intent binding are rejected.
4. Zero/negative/unlimited/nonfinite/boolean allowances and oversized malformed text are rejected with useful errors.
5. Proposed `approved: true`, arbitrary role authority and embedded credentials cannot grant permission; unknown fields fail closed.
6. Invalid/escaping/alias paths follow documented semantics, including Windows path strings on non-Windows test hosts.
7. Validation performs no I/O effects, and all current native v1 tests remain unchanged/passing within environment skips.

Link concrete tests to TC-103 and TC-104. These scenario IDs are planned acceptance, not pre-existing tests. Use standard-library unittest and the repository's current import conventions. Avoid meaningless tests asserting dataclass defaults or duplicating the implementation's exact branches.

## Exit and next task

Run focused new tests, native regressions and the planning/whitespace checks. Update status, WP-110 state, roadmap checkpoint, validation history and one cycle with actual outcomes. If the contract is complete, the next default task is WP-111; WP-115 can be selected independently after WP-110 where ownership permits. Do not mark WP-111 or the overall factory complete based on these schemas.
