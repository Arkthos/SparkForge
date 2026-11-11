# Native assisted factory

## Implementation boundary

The native path is a complete **assisted** workflow, not an autonomous
service and not the browser preview. A selected host provides reasoning,
source/code inspection, focused clarification, editing and an actual
independent reviewer. `plugins\sparkforge\scripts\factory.py` supplies
deterministic local specification, job, execution and evidence operations.

The canonical agent and [skill](../../plugins/sparkforge/skills/sparkforge/SKILL.md)
describe intake → authorized inspection → justified `REUSE`,
`UPDATE_EXISTING` or `NEW_COMPONENT` → concrete spec → genuine operator
decision → host implementation → accepted commands → independent review →
bounded repair/recovery → local handoff → inactive learning or no-change.
There is a mandatory stop before implementation on a proposed brief.

This publication establishes no live host, model-provider or operator
acceptance result. Corp and Acro remain independent, unqualified targets.
The code does not bundle private sources or earlier execution journals.

## Core API and CLI

The helpers use Python's standard library. The exact spec contract is in
[SPEC_FORMAT](../../plugins/sparkforge/references/SPEC_FORMAT.md).

| Python operation | CLI | Effect |
|---|---|---|
| `validate_spec(value)` | `validate-spec SPEC` | Return a normalized valid spec; the CLI adds its digest and `approved: false`. |
| `init_job(spec, workspace, job_dir)` | `init --spec ... --workspace ... --job-dir ...` | Create a new job in `AWAITING_APPROVAL`; never adopt existing state. |
| `decide(job_dir, spec_sha, decision, actor)` | `decide --job-dir ... --spec-sha ... --decision ... --actor ...` | Record an OPERATOR-OWNED `accept`, `reject` or `changes` assertion on the exact spec. |
| `job_status(job_dir)` | `status --job-dir ...` | Re-evaluate current controlled bytes, applicable checks/reviews and recovery state. |
| `history(job_dir)` | `history --job-dir ...` | Read the ordered local event history. |
| `run_check(job_dir, check_id, *, confirm_run=False)` | `run-check --job-dir ... --check ... --confirm-run` | Reserve and execute one accepted, bounded command. |
| `record_review(job_dir, candidate_sha, role, decision, actor, notes, *, review_context=None)` | `record-review` with required candidate/context/role/decision/actor/notes flags | Admit a current independent review assertion; a missing API context is rejected. |
| `revise(job_dir, spec)` | `revise --job-dir ... --spec ...` | Keep the spec ID, retain history, clear approval and require a new decision on changed content. |
| `cancel(job_dir, reason)` | `cancel --job-dir ... --reason ...` | Record a cancellation request, not guaranteed effect termination. |
| `reconcile(job_dir, run_id, actor, reason, *, confirm_stopped=False)` | `reconcile --job-dir ... --run-id ... --actor ... --reason ... --confirm-stopped` | Record an OPERATOR-OWNED reconciliation of the active reservation. |

Actor and role labels are not identities authenticated by the helper.
`decide` and `reconcile` must not be used by a worker to manufacture human
consent. Real review cannot be supplied by the builder under another name.

## State and bindings

Each new job creates `job.sqlite3` with a current state row and ordered
events. Supported operations retain prior specs, attempts and reviews.
Transactions use `BEGIN IMMEDIATE` and do not queue concurrent writers
indefinitely. This is coordinated local state, not a signed audit ledger or
tamper-proof storage.

- Spec SHA: digest of canonical JSON with sorted object keys.
- Candidate SHA: digest of the declared relative-file manifest, including
  content hashes and byte counts.
- Check round: identity created when a different candidate is bound.
- Check-evidence sequence: incremented for each reserved check attempt.
- Review context: digest binding job ID, exact spec SHA, candidate SHA,
  check round and check-evidence sequence.

Capture `review_context` before inspecting the candidate/evidence and use
the same token in `record-review`. Changing the spec, candidate or check
evidence requires re-review, not relabeling an old verdict. A check re-run
on identical bytes still invalidates the previous review context.

Common statuses:

| Status | Meaning / next action |
|---|---|
| `AWAITING_APPROVAL` | Present the exact current spec and wait for the operator. |
| `REJECTED` | No implementation or checks under that decision. |
| `IMPLEMENTATION_REQUIRED` | The accepted controlled-file set is not yet available. |
| `CHECKS_PENDING` | Required checks lack current results. |
| `CHECKS_FAILED` | At least one applicable check is non-passing. Inspect evidence before repair. |
| `STALE_CANDIDATE` | Declared bytes changed after the recorded candidate; obtain fresh check evidence. |
| `REVIEW_PENDING` | Checks pass but required independent review is missing. |
| `CHANGES_REQUIRED` | A current review requested changes or is incomplete. |
| `RUNNING_OR_INTERRUPTED` | An active reservation exists; determine whether it is still running. |
| `RECONCILIATION_REQUIRED` | Effects remain uncertain; the operator must reconcile before replay. |
| `CANCELLED` | Cancellation is recorded; do not infer every effect stopped. |
| `CANDIDATE_VERIFIED` | Current check/review records satisfy this local contract, not human acceptance or publication authority. |

Status precedence exposes active/uncertain operations before less urgent
states. Returning JSON or CLI exit 0 does not make every status successful.

## Actual command execution and finite repair

A check requires accepted current spec authority, explicit confirmation,
available controlled files and an unspent per-check/per-spec attempt.
Reservation happens before dispatch. The runner executes the stored `argv`
in the candidate workspace with `shell=False`; `python` resolves to the
running interpreter. It inherits the caller environment and adds
`PYTHONDONTWRITEBYTECODE=1`.

Combined stdout/stderr is bounded and hashed. A pass requires exit zero,
all required markers, elapsed/output bounds, no uncertain effect outcome
and the same controlled bytes afterward. Receipts include the runner's
implementation digest and Python version. `retain_output` controls whether
captured text is also stored; it does not sanitize metadata.

These are real processes, **not an OS sandbox**. Controlled-file hashing
is not an access allowlist. Commands can consume unbound dependencies and
caller credentials or affect external systems unless the host prevents it.
Stopping a parent process does not prove descendants or external effects
stopped. Unknown outcomes remain blocked for operator reconciliation.

Only one check reservation is active per job. Coordinate host edits; use
disjoint candidate/job areas for independent concurrent tasks. Repairs
must preserve accepted scope and use remaining `max_attempts`. A changed
candidate needs all required checks and independent review again. Attempts
are not refunded by candidate changes, cancellation or reconciliation.
Do not toggle specs or replace jobs to evade limits.

## Recovery, handoff and improvement

On reconnect, inspect the existing job's `status` and `history`; confirm
its spec, current candidate, active run, counts and source assumptions
before any action. Silence is not a failed run. The operator owns process
and side-effect reconciliation and its exact run ID.

Deliver an evidence-linked local handoff with spec/candidate identities,
changed files, actual check and review results, unknowns, recovery
location and the next human decision. Keep source captures and journals
in authorized storage. No status authorizes installation, publishing,
deployment, provider substitution or paid inference.

The final learning outcome is an inactive evidence-backed improvement
proposal, with a bounded future evaluation and rollback, or explicit
no-change. No automatic promotion API is implemented.

## Synthetic engineering checks

Available targeted regressions:

```powershell
python -B -m unittest discover -s tests -p test_native_factory.py
python -B -m unittest discover -s tests -p test_native_integration.py
python -B -m unittest discover -s tests -p test_native_dogfood.py
```

`specs\native-factory-selfcheck.json` is the named `SFS-001-selfcheck`
fixture. Its `core-contracts` command requires at least 43 core cases,
no skips or expected failures, a successful unittest result and explicit
completion markers. Its `max_attempts` is 2. Knowledge citations are
schema-only synthetic placeholders; current live coverage is
`NOT_ASSESSED`, and the fixture is not an accepted brief.

`scripts\dogfood_native_factory.py --job-dir ... --confirm-engineering-test`
can execute that fixture against the project's actual controlled bytes,
using an explicitly synthetic decision. It requires a new job outside the
candidate repository and stops at `REVIEW_PENDING` when checks pass.
It never auto-records a reviewer. Its report labels human acceptance
`NOT_ASSESSED` and native model workflow execution false. Unit tests use
owned synthetic repositories and sibling jobs under `tests`; a schema
check is not evidence that this engineering run or a native host ran.
