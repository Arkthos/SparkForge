# Frozen specification format

`scripts\factory.py` accepts the closed `sparkforge.spec.v1` contract below.
Use `validate-spec` before proposing a job. Schema validity does not prove
source truth, permission, meaningful acceptance, command safety or operator
approval. The returned digest binds the canonical JSON, not its formatting.

## Synthetic example: not an accepted brief

This example has **synthetic authority only** and is **not an accepted brief**.
All source references are deliberately invented `example.invalid` locators
with repeated hex revisions and digests. They are not hashes of real wiki
or repository content, not an inspected private baseline and not evidence
of current coverage. `SNAPSHOT_SCOPE` here exercises the schema; current
live coverage is `NOT_ASSESSED`. Do not reuse these citations for real work.

The check would execute actual local Python against a synthetic
`component.py`. An authorized exercise must still have its own genuine
operator decision and execution permission. This document supplies no
decision, implemented component or passing review.

```json
{
  "schema_version": "sparkforge.spec.v1",
  "id": "SFS-SYNTHETIC-DEMO",
  "title": "Synthetic classifier contract exercise",
  "problem": "A fictional classifier must distinguish three supported actions and reject unknown input.",
  "audience": "Synthetic exercise operator",
  "environment": "LOCAL_DEVELOPMENT",
  "builder_actor": "synthetic-builder",
  "non_goals": [
    "No real source access, model calls, installation, publication or deployment.",
    "No inferred human acceptance or fabricated independent review."
  ],
  "knowledge": {
    "wiki_revision": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
    "repository_revision": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
    "citations": [
      {
        "source": "wiki",
        "locator": "https://example.invalid/synthetic/wiki/classifier-guidance",
        "revision": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        "sha256": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
      },
      {
        "source": "repository",
        "locator": "https://example.invalid/synthetic/repository/classifier-contract",
        "revision": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
        "sha256": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
      }
    ],
    "coverage": "SNAPSHOT_SCOPE",
    "limitations": [
      "Schema-only synthetic citations and repeated placeholder digests; no actual source authenticity or permission is established.",
      "The fictional comparison is limited to this fixture; current live coverage is NOT_ASSESSED.",
      "This example is not an accepted brief."
    ]
  },
  "reuse": {
    "decision": "UPDATE_EXISTING",
    "target": "synthetic-classifier",
    "rationale": "Within the fictional scenario, improve the named classifier instead of adding a duplicate.",
    "inspected_candidates": [
      "synthetic-classifier-fixture-only"
    ]
  },
  "controlled_files": [
    "component.py"
  ],
  "acceptance": [
    {
      "id": "A1",
      "behavior": "The synthetic classifier maps reuse, update and new correctly and raises ValueError for unsupported input.",
      "checks": [
        "classifier-contract"
      ]
    }
  ],
  "checks": [
    {
      "id": "classifier-contract",
      "argv": [
        "python",
        "-B",
        "-c",
        "from component import classify\nassert classify('reuse') == 'REUSE'\nassert classify('update') == 'UPDATE_EXISTING'\nassert classify('new') == 'NEW_COMPONENT'\ntry:\n    classify('unsupported')\nexcept ValueError:\n    pass\nelse:\n    raise AssertionError('Unknown action was accepted')\nprint('SYNTHETIC-CLASSIFIER-OK')"
      ],
      "timeout_seconds": 5,
      "output_limit_bytes": 4096,
      "max_attempts": 2,
      "required_markers": [
        "SYNTHETIC-CLASSIFIER-OK"
      ],
      "retain_output": false
    }
  ],
  "required_reviewers": [
    "quality"
  ]
}
```

## Exact fields and bounds

No additional fields are accepted at the spec, knowledge, citation, reuse,
acceptance or check levels. In particular there is no spec-level `approved`
flag. Approval belongs to a later job decision on the frozen spec SHA.

| Field | Contract |
|---|---|
| `schema_version` | Exactly `sparkforge.spec.v1`. |
| `id`, `builder_actor` | Short identifiers: an alphanumeric first character, followed by at most 79 letters, digits, dots, underscores or hyphens. The actor is a label, not authentication. |
| `title`, `problem`, `audience` | Nonempty bounded text. |
| `environment` | Exactly `LOCAL_DEVELOPMENT`, `CORP` or `ACRO`; none grants environment access. |
| `non_goals` | Nonempty unique text entries. |
| `knowledge` | Exactly `wiki_revision`, `repository_revision`, `citations`, `coverage`, `limitations`. |
| `reuse` | Exactly `decision`, `target`, `rationale`, `inspected_candidates`. Decision is `REUSE`, `UPDATE_EXISTING` or `NEW_COMPONENT`. Target may be empty only for `NEW_COMPONENT`; rationale and inspected-candidate list are required. |
| `controlled_files` | 1–512 unique relative file paths; no traversal, case/separator aliases, Git internals or environment-secret files other than `.env.example`. The manifest normalizes separators. |
| `acceptance` | Nonempty unique criteria, each with exactly `id`, `behavior`, `checks`. Referenced checks must exist; every check must be referenced. |
| `checks` | 1–64 unique checks with exactly the seven fields shown above. |
| `required_reviewers` | 1–16 unique role identifiers. All must have current passing review records before local verification. |

`knowledge.citations` must include both `wiki` and `repository` entries,
each with exactly `source`, `locator`, `revision`, `sha256`. A source's
revision must equal its declared baseline. Digests are 64 lowercase hex
characters; duplicate source/locator pairs are refused.

`knowledge.coverage` accepts `SNAPSHOT_SCOPE` or `CURRENT_SCOPE`, not
`NOT_ASSESSED`. This is a requirement for an explicitly assessed spec scope,
not permission to invent one. Snapshot readers always report current live
coverage `NOT_ASSESSED`; preserve that limitation when proposing a legitimate
snapshot-scoped spec. The helper does not establish `CURRENT_SCOPE` merely
because a caller writes the string. If both required evidence surfaces are
unavailable, hold the proposal rather than manufacture citations.

Each check contains:

- `argv`: 1–128 strings. The executable is `python` (the current interpreter)
  or an explicit absolute executable. Execution uses an argument list,
  `shell=False`, and the candidate workspace as its working directory.
- `timeout_seconds`: a finite number greater than zero and at most 3600.
- `output_limit_bytes`: an integer from 1 through 16 MiB.
- `max_attempts`: an integer from 1 through 20, charged per check and exact
  spec SHA, including failures and interrupted reservations.
- `required_markers`: 1–32 unique, nonempty strings matched in captured
  combined stdout/stderr. These are substrings, not regular expressions.
- `retain_output`: an explicit boolean. False avoids storing raw output in
  the receipt, not all sensitive metadata or in-memory processing.

JSON input is bounded to 2 MiB. Duplicate keys and non-finite numeric
constants are refused. Each controlled file must be a plain, non-aliased
file no larger than 32 MiB when checked. Future candidate files may be
absent at job initialization; they must exist before a check can run.

## CLI and lifecycle

For a synthetic local exercise, set `$Factory` to the resolved package's
`scripts\factory.py`, `$Spec` to the explicit JSON file, `$Workspace` to
an existing absolute candidate directory, and `$Job` to a new absolute
sibling directory with an existing parent. Do not overlap workspace and
job state or adopt a pre-existing directory.

```powershell
python -B $Factory validate-spec $Spec
python -B $Factory init --spec $Spec --workspace $Workspace --job-dir $Job
python -B $Factory status --job-dir $Job
```

Check exit codes and returned states. `init` yields `AWAITING_APPROVAL`.
**STOP before implementation** and show the actual frozen SHA. Manual
`decide --job-dir ... --spec-sha ... --decision accept|reject|changes --actor
...` is **OPERATOR-OWNED**; a worker must not simulate the decision.

Only after that decision and separate execution authorization:

```powershell
python -B $Factory run-check --job-dir $Job --check classifier-contract --confirm-run
```

A check's exit status, required markers, elapsed time, output limit and
unchanged controlled bytes all matter. Successful shell launch is not a
pass. Check CLI exit codes are 0 for pass, 1 for an observed non-pass and
2 for a blocked/error operation. Other successful helper calls return 0,
which by itself does not mean the candidate is verified.

### Review the context you actually inspected

Capture `review_context` from `status` **before inspecting** the candidate
and check evidence, and submit the **same token**. It binds the job ID,
exact spec SHA, candidate SHA, check round and check-evidence sequence.
A re-run on unchanged bytes still changes the context. If anything changes,
re-review; never relabel an old verdict with a new token.

Illustrative synthetic-workflow syntax, with no supplied verdict:

```powershell
$ReviewStart = python -B $Factory status --job-dir $Job | ConvertFrom-Json
# The independent reviewer now inspects this bound work and chooses a decision.
python -B $Factory record-review --job-dir $Job --candidate-sha $ReviewStart.candidate_sha --review-context $ReviewStart.review_context --role quality --decision $ReviewDecision --actor $ReviewerActor --notes $ReviewNotes
```

All accepted checks must pass before review admission. The reviewer chooses
`pass`, `changes` or `incomplete`; their actor must differ from
`builder_actor`. The operator/host must establish actual independence.
The helper verifies bindings, not the truth of an assertion.

## Repair, recovery and handoff

Use `revise --job-dir ... --spec ...` for a genuinely changed proposal with
the same spec ID. It preserves history and invalidates the decision;
an unchanged spec cannot reset an attempt limit. Candidate edits likewise
require fresh checks and review, not relabeled evidence.

Use `cancel --job-dir ... --reason ...` to request cancellation and
`history --job-dir ...` to inspect durable events. If execution is active
or uncertain, do not replay it. Only the operator may reconcile the exact
run using `reconcile --job-dir ... --run-id ... --actor ... --reason ...
--confirm-stopped` after checking effects. Reconciliation neither creates
a pass nor refunds an attempt.

Checks inherit the caller's environment and are not an OS sandbox.
Controlled files are digest inputs, not an access boundary.
`CANDIDATE_VERIFIED` is a current local evidence state, not human acceptance,
host qualification or permission to publish. Deliver the local evidence and
limitations, followed by an inactive improvement proposal or explicit
no-change. Keep real source material and job journals out of Git.
