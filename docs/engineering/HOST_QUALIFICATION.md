# Host qualification: record consistency is not acceptance

## Current boundary

`scripts\validate_host_qualification.py` validates a proposed host record.
It does not contact a host, authenticate evidence, verify permissions,
install a package or authorize execution. Its report always has
`scope: record_consistency_only`, `host_qualified: false` and
`execution_authorized: false`, including for a structurally valid record
containing `OBSERVED` capabilities.

Corp and Acro are independent requested deployment targets. Their actual
client selection, capabilities and end-to-end native acceptance remain
unqualified by this publication. An environment name, package manifest,
synthetic fixture or earlier result from another client is not a substitute.
No confidential platform configuration or operating recipe is included.

## Closed record contract

The top-level fields are exactly:

- `schema_version`: `sparkforge-host-qualification.v1`.
- `scope_type`: `ENVIRONMENT`.
- `environment_id`, `record_revision`: nonempty, unpadded strings.
- `selection`: exactly `status`, `reason`, `client`.
- `capabilities`: an array of capability records.

Selection status is `UNSELECTED` or `SELECTED`. An unselected client must be
null. A selected client has exactly these nonempty string fields:
`product`, `distribution`, `launcher`, `build`, `profile_id`,
`profile_revision`, `config_revision`, `os`, `architecture`.
They bind the proposed record to a specific configuration; the validator
does not launch or resolve the strings.

Each capability has exactly `id`, `status`, `reason`, `evidence`. IDs must be
unique. A capability's status controls the permissible evidence class:

| Capability status | Evidence class |
|---|---|
| `NOT_ASSESSED` | `evidence` must be null. |
| `DOCUMENTED` | `DOCUMENTATION_CLAIM` or `PINNED_SOURCE_OBSERVATION`. |
| `SYNTHETIC_ONLY` | `SYNTHETIC_RESULT`. |
| `OBSERVED` | `LIVE_HOST_RESULT`. |
| `UNSUPPORTED` | `DOCUMENTATION_CLAIM`, `PINNED_SOURCE_OBSERVATION` or `LIVE_HOST_RESULT`. |

Non-null evidence has exactly `class`, `reference`, `revision`, `binding`.
Its binding has exactly `environment_id`, `record_revision`,
`capability_id`, `client`, matching the containing record and selection.
A `LIVE_HOST_RESULT` requires a selected client. Reusing an evidence
reference with a conflicting class or revision is invalid.

The evidence reference remains inert text. A caller can write a plausible
claim without performing a test; passing this checker does not make that
claim genuine. An empty capability inventory can be structurally valid
but adds `CAPABILITY_INVENTORY_NOT_ASSESSED`.

## Synthetic validation

From the repository root, this command checks an explicitly fictional,
unselected-client fixture:

```powershell
python -B scripts\validate_host_qualification.py tests\fixtures\host_qualification\unselected.json
```

Exit 0 means the record is consistent; exit 1 means invalid input. Even a
valid report retains `RECORD_ORIGIN_NOT_AUTHENTICATED`,
`HOST_QUALIFICATION_NOT_ESTABLISHED` and
`EXECUTION_AUTHORIZATION_NOT_ESTABLISHED`. Unselected and unobserved
capabilities add further blockers.

The shipped `selected.json` is also wholly synthetic. Its
`LIVE_HOST_RESULT` field is a fixture claim for schema tests, not evidence
that a real host was contacted. Neither fixture is an accepted operator
brief, native run receipt or permission to access a system.

## Operator qualification procedure

This is a product-level checklist, not a platform-specific deployment
recipe. Perform it only in the operator-selected authorized environment:

1. Select the exact client/distribution/build, launcher, configuration,
   profile, OS and architecture. Identify the source, provider and storage
   permissions separately; do not infer them from a machine or account name.
2. Identify the capabilities this particular workflow needs: loading the
   intended package, authorized reading and editing, genuine decision
   ingress, bounded command execution, independent review, cancellation,
   recovery and local evidence handling. Do not equate an incomplete
   capability list with complete qualification.
3. Use a pre-authorized synthetic trial first. Observe actual behavior and
   negative cases, including no decision, stale spec/review context, failed
   commands and uncertain interruption. Record what was not exercised.
4. Bind each permitted observation to that exact client, configuration and
   evidence revision. Keep sensitive receipts in approved storage, not in
   this repository. A documentation claim remains documentation evidence.
5. Obtain the appropriate human decision for the next scoped use. Source
   access, execution, acceptance and external publication are distinct.
   The record validator itself never grants that decision.

Reassess affected capabilities when client, configuration, permissions,
provider, storage or package behavior changes. Do not transfer a Corp result
to Acro, a development result to production, or a record from another build
to the current one. Unknown coverage stays `NOT_ASSESSED`.

See [native workflow](NATIVE_FACTORY.md),
[storage limits](STORAGE_QUALIFICATION.md) and
[authority](../../plugins/sparkforge/references/AUTHORITY.md).
