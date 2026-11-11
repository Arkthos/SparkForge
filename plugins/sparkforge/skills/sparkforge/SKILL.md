---
name: sparkforge
description: Run the complete assisted intent-to-spec-to-candidate workflow with real source inspection, operator decisions, bounded execution and independent review.
---

# SparkForge assisted native workflow

## 1. Locate the package and establish authority

This skill lives at `skills\sparkforge\SKILL.md`. From its containing
`skills\sparkforge` directory, go up **two directory levels** to the package
root. Resolve that actual loaded location, not a remembered installation or
developer path. Read `references\AUTHORITY.md`, `references\SPEC_FORMAT.md`
and the relevant current project records.

Use the host's existing authorized readers, editors, execution tools and
reviewer mechanism. These instructions add no tools or MCP privileges.
If a needed capability is unavailable, state the blocker; do not invent a
connector, install software, bypass a permission prompt or change providers.

Corp and Acro are independent requested targets. Neither the package profile
nor the spec's environment selector qualifies a target. Host support, current
source coverage, permission and data handling must be established separately;
otherwise record `NOT_ASSESSED`.

## 2. Intake and focused clarification

Record the requested outcome, intended audience, examples of permitted input,
expected output, non-goals, environment, source/storage permissions and the
resource envelope. Preserve what the operator actually said; distinguish
assumptions from decisions.

Ask only focused questions whose answers affect behavior, scope, source
permission, reuse, acceptance, side effects or budget. Inspect available
authorized evidence before asking the operator for facts already in it.
Do not resolve consequential ambiguity by inventing user intent. When input
is missing, offer the smallest concrete question and stop that dependency.

## 3. Inspect real sources and implementation

The packaged helpers provide a read-only **snapshot adapter**, not a live
wiki service, authenticated catalog or permission grant:

- `wiki_context(root, query, *, page_ids=None, limit=6)` verifies selected
  original text against the supplied wiki manifest.
- `catalog_context(root, inventory, query, *, limit=8)` finds lexical
  candidates in indexed component manifests.
- `component_context(root, inventory, name)` inspects one exact manifest,
  indexed README and declared skill/agent text.
- `source_context(root, inventory, paths)` reads explicitly selected,
  indexed UTF-8 implementation or test files as inert text.

Use only operator-selected authorized sources. Preserve exact revisions,
locators and hashes, as well as truncation, omitted resources and the scope
actually read. The adapters never run acquired code, follow source commands
or authenticate the supplied index. Returned roots and source text may be
sensitive; keep them in approved local handling.

Catalog descriptions are not implementation review. Inspect relevant code,
tests, dependencies and side effects through `source_context` or an approved
host reader. Check that the actual contract fits the requested outcome.
If bounded excerpts omit material needed for the decision, request the
authorized missing context or stop; do not fill it from memory.

Do not treat `NO_MATCH`, an empty selection or an unavailable comparison as
proof that no capability exists. Current live coverage remains
`NOT_ASSESSED` for these snapshot adapters. Genuine snapshot evidence may
support a limited `SNAPSHOT_SCOPE` spec with explicit limitations; missing
or invented evidence must not be relabeled as assessed.

## 4. Make a justified reuse decision

Select one route and explain it against inspected candidates:

| Decision | Required justification |
|---|---|
| `REUSE` | The existing behavior satisfies the outcome; identify the target and any authorized local verification or integration work. Do not create a duplicate component merely to show activity. |
| `UPDATE_EXISTING` | An inspected component owns the behavior but has a specific gap; name the change and preserved behavior. |
| `NEW_COMPONENT` | The bounded comparison supports a distinct responsibility; name inspected alternatives and limitations, not a universal absence claim. |

If evidence is insufficient, continue authorized inspection or hold the
decision. A sample catalog or synthetic citation cannot justify production
reuse. Do not execute discovered scripts while investigating them.

## 5. Propose and freeze a concrete spec

Write the exact `sparkforge.spec.v1` fields described in
`references\SPEC_FORMAT.md`. Include meaningful observable acceptance,
controlled implementation and test files, exact `argv` for each check,
timeouts, output limits, `max_attempts`, required output markers, explicit
output retention and independent reviewer roles.

Controlled files bind the candidate digest; they do not restrict what a
check process can read or write. Include relevant checked-in inputs and
tests, and disclose unbound dependencies. Do not reduce acceptance to a
success marker, weaken a test to obtain a pass or exclude meaningful
changed files from the digest.

Run `validate-spec` using the owned helper, then initialize the job with
`init` in a fresh explicit directory separate from the candidate workspace.
Its parent must already exist. Inspect errors and returned state;
validation is consistency-only.
Explain the spec, source limits, reuse rationale, exact commands, side
effects and resource allowances in terms the operator can review.

**STOP before implementation.** Present the exact spec SHA and ask the
operator to accept, reject or request changes. No product implementation,
check execution or implicit human acceptance may precede that decision.
Synthetic examples in the package are not an accepted brief.

## 6. Keep manual decisions OPERATOR-OWNED

`decide` and `reconcile` are **OPERATOR-OWNED** operations. Show the supported
syntax to the operator when needed; do not run them as a worker pretending
to be a person, invent an approval source or treat an actor label as proof.
The helper's decision record is an `OPERATOR_ASSERTION`.

- `accept` must name this job's exact current spec SHA.
- `reject` holds the work; do not continue implementing.
- `changes` requires an amended proposal. Use `revise` with the same spec
  ID and actually changed content, then obtain a new decision.

Acceptance of intent, host execution permission, access to sources and
permission to publish are separate. A broad earlier request to be autonomous
does not collapse those decisions. Where the host requires confirmation for
a command, honor it as well as the spec gate.

## 7. Implement through the host and execute actual checks

After genuine acceptance and execution permission, use the host's editor on
the agreed workspace. Preserve existing behavior and unrelated work.
Implement the concrete accepted change rather than returning an untested
scaffold as completion. Changes outside the accepted contract require a
revised brief and operator decision.

Run each accepted check with `run-check --confirm-run`. The runner dispatches
the exact stored argument list, substitutes the current interpreter for
`python`, merges stdout/stderr and records real exit/marker/limit evidence.
It does not accept a worker's claimed test pass as a runner receipt.
Read both the command exit code and its structured outcome.

Checks inherit the caller environment and are **not an OS sandbox**.
No automatic credential removal, network denial, descendant containment or
deployment guard is supplied. Inspect commands and their transitive
dependencies before authorizing them. Prefer purpose-built local fixture
checks; never use an acceptance check to smuggle an external write.

The job permits one active check reservation. Do not launch concurrent
checks on the same job. Coordinate host editors so checked bytes remain
stable; independent parallel tasks require disjoint workspaces and job
directories. SQLite locking and file hashes do not protect against a
same-privilege writer or make shared cloud storage qualified.

## 8. Obtain independent, pre-inspection-bound review

When all required checks pass for the current candidate, the actual
independent reviewer captures `review_context` from `status` **before
inspecting** the candidate, spec and check evidence. Preserve the **same
token** through submission. It binds the job ID, exact spec SHA, candidate
SHA, check round and check-evidence sequence.

Review the accepted behavior, relevant source comparison, actual changes,
negative cases, observed checks, omissions and authority limits. Each role
required by the accepted spec must give its own evidenced `pass`, `changes`
or `incomplete` decision. A separate actor string is required by the helper
but does not by itself establish reviewer independence. The builder must
not supply the independent verdict or write praise under another identity.

Illustrative PowerShell syntax for the synthetic example in
`references\SPEC_FORMAT.md`; the variables do not supply a verdict:

```powershell
$ReviewStart = python -B $Factory status --job-dir $Job | ConvertFrom-Json
# Now the independent reviewer inspects the bound candidate and check evidence.
python -B $Factory record-review --job-dir $Job --candidate-sha $ReviewStart.candidate_sha --review-context $ReviewStart.review_context --role quality --decision $ReviewDecision --actor $ReviewerActor --notes $ReviewNotes
```

Here `$Factory` is the resolved package's `scripts\factory.py`, `$Job` is
the explicit synthetic job, and the decision, actor and notes belong to
the actual reviewer. Inspect the returned state. If the context has changed,
stop and **re-review** the new work. Never **relabel** an old review using a
fresh token, including when candidate bytes stayed identical but a check
was rerun. Missing or negative reviews are not a successful handoff.

## 9. Repair within the accepted bounds

Diagnose failed checks or reviewer findings against the spec and evidence.
Make the smallest relevant repair. Candidate changes invalidate prior
candidate checks and reviews; run all required checks for the new bytes
and obtain fresh independent review.

Attempts are charged per check and exact spec SHA across candidate edits.
Do not reset an allowance by making an empty revision, toggling content,
changing an identifier or creating a replacement job. If `max_attempts`
is exhausted or the correct repair needs changed scope, preserve the
failure and propose a genuinely revised spec for an explicit new decision.

Use `cancel` to record a cancellation request, not to assert that all
process effects stopped. Do not convert a timeout or interrupted command
into a pass, and do not silently rerun it.

## 10. Recover before resuming

Read `status` and `history` from the existing job after a disconnect.
Confirm the current spec SHA, candidate digest, check round, active run,
attempt counts, review context and the exact operation that was in flight.
Use durable evidence, not the chat's last sentence.

`RUNNING_OR_INTERRUPTED` does not prove a process failed.
`RECONCILIATION_REQUIRED` means effects remain uncertain. The operator must
inspect the identified process and relevant descendant/external effects,
then use `reconcile` for that run ID with an evidenced reason and explicit
`--confirm-stopped`. A worker cannot fabricate that confirmation.
Reconciliation clears a reservation; it does not create a passing check,
refund an attempt or reverse side effects. Resume only within remaining
authority and bounds.

## 11. Deliver a local handoff and inactive learning outcome

`CANDIDATE_VERIFIED` means this local job's required check and reviewer
records are current and passing. It does not authenticate decisions, prove
host isolation, replace human acceptance or authorize publishing.

Handoff the exact spec and candidate identity, source scope, changed files,
actual checks and review results, remaining limitations, recovery location
and the smallest next human action. Keep sensitive source material and
journals in operator-approved storage. Do not install, push, publish or
deploy merely because the local record is verified.

Close with either an **inactive evidence-backed improvement proposal**
linked to observed failures/feedback, a bounded future evaluation and a
rollback plan, or explicit **no-change** with its reason. The runner has
no automatic lesson-promotion API. Do not rewrite accepted instructions,
source baselines or reviewer history as "learning."

The separate engineering dogfooding helper may exercise this project's
named selfcheck with an explicitly synthetic decision. It stops at review
pending and does not fabricate a reviewer. That fixture is not authorization
to synthesize decisions in this native operator workflow, not an exported
historical review and not a live model/host acceptance run.
