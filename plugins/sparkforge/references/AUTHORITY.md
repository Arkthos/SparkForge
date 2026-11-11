# Authority and evidence boundaries

## Independent decisions

| Decision or observation | Owner and meaning |
|---|---|
| Source access and disclosure | The operator and applicable data owner select authorized sources, provider context and storage. A supplied manifest is not permission. |
| Intent and scope acceptance | The operator reviews a concrete spec and decides on its exact SHA. Manual `decide` is OPERATOR-OWNED. |
| Command execution | The selected host and operator authorize the actual command, environment, side effects and finite resources. `--confirm-run` is an explicit runner input, not a credential. |
| Implementation | The builder uses the host's existing editor within the accepted contract. The helpers do not write product code. |
| Independent review | An actual reviewer inspects the bound candidate and evidence and supplies their decision. An alternate actor string is not proof of independence. |
| Unknown-effect reconciliation | The operator checks the active operation and relevant effects before `reconcile --confirm-stopped`. This is OPERATOR-OWNED. |
| Acceptance, installation and publication | A separate authorized human decision. No local runner status grants it. |

The package declares no tool allowlist, MCP configuration, credential
requirements or privilege expansion. It uses only capabilities already
authorized in the selected host. Missing capability is a blocker, not
permission for fallback tooling, a different identity or a new provider.
Corp and Acro must be qualified independently; choosing an environment or
building a profile does not perform that qualification.

## What the helper can establish

The factory validates the closed specification schema; binds the accepted
spec, controlled file manifest and check round; reserves finite attempts;
runs the stored command; and records its observed exit, output markers,
limits and uncertainty. SQLite transactions coordinate its own state
updates. Previous specifications, attempts, reviews and events are retained
through supported operations.

The snapshot adapters verify selected bytes against caller-supplied indexes,
return bounded context and expose omissions. Their citations preserve
locators, revisions and content hashes, not authenticated source ownership.
They do not follow links, run acquired code or invoke a model.

## What it cannot establish

- Actor labels and `OPERATOR_ASSERTION` / `REVIEWER_ASSERTION` records do
  not authenticate people, permissions or actual independence.
- Local digests and journals are not signed attestations or tamper-proof
  storage against a same-privilege editor.
- Controlled-file digests cover only the declared files. They are not an
  execution access allowlist and do not bind every dependency or environment
  value a command might consume.
- The runner uses `shell=False` but executes real programs. It inherits the
  caller environment, including accessible credentials and network routes,
  and adds `PYTHONDONTWRITEBYTECODE=1`; it is not an OS sandbox.
- Killing the direct child does not prove all descendants or external
  effects stopped. Timeout, interruption, cancellation and uncertain
  output require reconciliation, not automatic retry.
- A hash match does not prove source authenticity, permission, freshness,
  semantic relevance or complete comparison. Current live coverage remains
  `NOT_ASSESSED` for snapshot reads.
- `CANDIDATE_VERIFIED` never means human acceptance, host qualification,
  installation, deployment or publication authorization.

## Review binding

Capture `review_context` from `status` before inspecting the candidate and
check evidence. Submit the same token; it binds job ID, exact spec SHA,
candidate SHA, check round and check-evidence sequence. A changed spec,
candidate or newly reserved check invalidates the old context. Re-review
the current evidence rather than relabel an earlier verdict.

The CLI requires `--candidate-sha` and `--review-context`. The Python
`record_review` API rejects a missing context as well. This prevents
accidental stale admission; the helper cannot prove when a human read the
files or whether the claimed review actually occurred.

## Data and recovery handling

Jobs contain specifications, actor assertions, workspace locations, command
arguments, candidate hashes and runner receipts. `retain_output: false`
avoids saving raw process text in the check result, but output is still
read in memory and other fields or error messages can be sensitive.
Knowledge responses can contain full local roots and selected source text.
Use operator-approved handling; do not commit runtime jobs or captured
private sources and do not infer export rights from a private repository.

Use `status` and `history` before resuming. Preserve unknown outcomes,
failure records and consumed attempts. Never delete or recreate a job to
evade a budget, turn an interrupted check into success or manufacture a
review. Reconciliation records an operator assertion about effects; it
does not undo them or refund attempts.

## Synthetic evidence and learning

All shipped source citations in documentation examples and the selfcheck
are explicitly synthetic. They use `example.invalid` and repeated hex
placeholders, not real source pins. They demonstrate schema shape and
bounded engineering behavior only, not an accepted brief or current
coverage. The engineering dogfood harness labels its decision synthetic
and leaves independent review pending.

End an assisted task with an inactive, evidence-linked improvement proposal
or explicit no-change. Learning activation, changed operating instructions
and external contribution each require a new scoped decision and relevant
validation; they are not consequences of a passing local check.
