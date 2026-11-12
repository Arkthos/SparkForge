# SparkForge native package

SparkForge is an experimental, operator-mediated workflow for turning an idea
into a concrete, source-informed specification and a checked local candidate.
The host performs reasoning, clarification, editing and independent review.
The owned Python helpers read indexed snapshots, freeze specifications, record
decisions, execute accepted checks and expose durable recovery state.

This package is not a template-only factory, an autonomous deployment service,
an authentication service or an OS sandbox. Corp and Acro are independent
requested deployment targets; neither is qualified by this publication.
Current live source coverage and native-host compatibility are `NOT_ASSESSED`.
No private source snapshots, earlier job journals or historical approval
receipts are distributed with it.

## Entry points

- `agents\sparkforge.agent.md`: native agent entry.
- `skills\sparkforge\SKILL.md`: the complete assisted workflow.
- `references\SPEC_FORMAT.md`: the exact `sparkforge.spec.v1` contract.
- `references\AUTHORITY.md`: operator, host, reviewer and publication boundaries.
- `scripts\knowledge.py`: read-only snapshot adapters.
- `scripts\factory.py`: spec, job, check and review helpers.

The entry files do not declare tools or MCP servers. The selected host must
provide already-authorized capabilities; missing capability is a blocker,
not permission to install or enable something.

## Full local workflow

1. Establish the desired outcome, audience, allowed inputs, environment,
   resource envelope and non-goals. Ask focused questions where an answer
   changes correctness, permission, scope or acceptance.
2. Read operator-selected authorized guidance with `wiki_context`; search
   indexed component manifests with `catalog_context`; inspect plausible
   components with `component_context`. Use `source_context` or an authorized
   host reader for the actual relevant implementation and tests. Preserve
   source revisions, content hashes, omissions and unresolved questions.
3. Justify `REUSE`, `UPDATE_EXISTING` or `NEW_COMPONENT` from that inspection.
   A lexical miss is not proof of absence. Missing comparison stays
   `NOT_ASSESSED`; do not manufacture citations to make a product spec pass.
4. Propose a concrete spec with controlled files, observable acceptance,
   exact check commands and limits, and independent reviewer roles.
   `validate-spec` checks consistency, not truth or acceptance. Initialize a
   separate job, present its exact spec SHA, and **STOP before implementation**.
5. The operator owns the `accept`, `reject` or `changes` decision. A worker
   cannot impersonate the operator or infer acceptance from silence.
   Only after genuine acceptance and separate execution permission may the
   host edit the agreed candidate and invoke `run-check --confirm-run`.
6. Run every accepted check against the actual candidate, then obtain actual
   independent review of the exact evidence. Repair within the accepted
   `max_attempts`; changed files require fresh checks and re-review.
   A changed brief uses `revise` and another operator decision.
7. Recover interrupted work using `status` and `history`, not blind retries.
   Manual `decide` and `reconcile` are **OPERATOR-OWNED**.
   Deliver a local handoff with limitations and the next human decision.
   `CANDIDATE_VERIFIED` is not human acceptance or publication authorization.
8. End with an inactive evidence-backed improvement proposal or explicit
   no-change. Do not silently change instructions, activate learning or
   promote a package.

## Helper syntax

These are illustrative commands for an explicitly synthetic exercise, not an
accepted brief or instructions to approve a real job. Start at the repository
root. The operator supplies `$Spec`, an existing `$Workspace`, and a fresh
absolute `$Job` whose parent exists and does not overlap that workspace.
For a fixture, use sibling candidate/job directories in an owned test area.
For a deployed package, resolve its actual relocated root instead.

```powershell
$PluginRoot = (Resolve-Path 'plugins\sparkforge').Path
$Factory = Join-Path $PluginRoot 'scripts\factory.py'
python -B $Factory validate-spec $Spec
python -B $Factory init --spec $Spec --workspace $Workspace --job-dir $Job
python -B $Factory status --job-dir $Job
```

Inspect each command's exit code and returned state. Initial state is
`AWAITING_APPROVAL`; missing future candidate files do not turn initialization
into approval. The operator, not the builder, records their decision with
`decide --job-dir ... --spec-sha ... --decision accept|reject|changes --actor ...`.
An accepted decision is an operator assertion, not an authenticated identity.

### Independent review must retain its starting context

The independent reviewer captures `review_context` from `status` **before
inspecting** the candidate and check evidence, then submits the **same token**.
It binds the job ID, exact spec SHA, candidate SHA, check round and
check-evidence sequence. Even a re-run on unchanged bytes changes the review
context. If any binding changes, stop and re-review; never relabel an old
verdict using a newly fetched token.

The following synthetic-workflow syntax assumes all required checks passed.
`$ReviewerActor`, `$ReviewDecision` and `$ReviewNotes` must come from the actual
independent reviewer; the example supplies no passing verdict:

```powershell
$ReviewStart = python -B $Factory status --job-dir $Job | ConvertFrom-Json
# Preserve ReviewStart while the independent reviewer inspects the bound work.
python -B $Factory record-review --job-dir $Job --candidate-sha $ReviewStart.candidate_sha --review-context $ReviewStart.review_context --role quality --decision $ReviewDecision --actor $ReviewerActor --notes $ReviewNotes
```

The role must be in the accepted spec. `pass`, `changes` and `incomplete` are
the only review decisions. The reviewer actor must differ from the builder,
but a different string alone does not establish independent judgment.

## Execution and evidence limits

Checks execute real processes with `shell=False`, in the candidate directory,
using the caller's environment. `python` resolves to the current interpreter.
The runner does not remove credentials, block network access or contain
descendants. Controlled-file hashing is not a filesystem access allowlist.
Timeouts, uncertain termination and interrupted reservations require operator
reconciliation before replay. See [authority](references/AUTHORITY.md).

Use authorized storage for jobs and source outputs. Records can contain paths,
commands, cited source information and optionally process output. Never commit
real runtime state, private captures or sensitive receipts to this repository.
Hash binding does not confer source permission, freshness or semantic coverage.

## Packaging and validation

From the repository root, `scripts\build_sparkforge_package.py --profile
corp|acro --output ...` creates a new local package from a fixed file inventory.
It does not install or invoke that package. The resulting
`PACKAGE_INVENTORY.json` reports `STRUCTURAL_ONLY` validation and
`compatibility: NOT_ASSESSED`. Do not reuse a pre-existing output directory.

For source-neutral synthetic regression, use:

```powershell
python -B -m unittest discover -s tests -p test_native_package.py
python -B -m unittest discover -s tests -p test_native_integration.py
```

These exercise owned contracts and fixture behavior, not a native model run,
live authorized sources, Corp/Acro qualification or operator acceptance.
The separate fictional browser preview was retired during the WP-100 cleanup.
The coordinated multi-agent target is described in the repository architecture;
this package still implements assisted v1 until that work is delivered.
