# SparkForge architecture

## Current implementation

SparkForge is a native agent/skill plus small Python standard-library helpers.
The host provides reasoning, editing, tool permissions and interaction. There is
no embedded alternative model runtime, hosted scheduler or shared credential store.

```text
Operator-approved host
  -> native agent and skill
  -> authorized source adapter -> cited comparison
  -> concrete specification -> genuine operator decision
  -> host implementation -> accepted check runner
  -> independent current-context review -> bounded repair or handoff
```

| Surface | Owned behavior | Important limit |
|---|---|---|
| `plugins/sparkforge/agents` and `skills` | Full native development procedure | Instructions do not enforce OS permissions |
| `scripts/knowledge.py` in the package | Bounded indexed snapshot reads, hashes, citations and source-file lookup | Does not authenticate sources or establish live coverage |
| `scripts/factory.py` in the package | Strict specs, local state/events, decisions, checks, review context and recovery | Editable local records are not a trusted identity service |
| Repository package builder | Allowlisted profile export and byte inventory | Structural validity is not deployed compatibility |
| Engineering preparation tools | Host-record consistency and disposable storage observations | Qualification flags remain false |
| `preview` | Fictional tab-local UX prototype | No real knowledge lookup, model work or durable authority |
| Public research | Original synthesis, provenance and design references | Reading is not implementation or framework adoption |

The [native slice specification](../specs/NATIVE_FACTORY_SLICE.md) is the
executable implementation scope. The [contract catalog](CONTRACTS.md) records
wider target obligations, not a claim that every logical interface is implemented.

## Sources and specifications

The snapshot adapter consumes caller-selected existing indexes and original
files. It verifies declared byte hashes, identities, paths, sizes and bounded
UTF-8 text. It never follows source instructions into execution or fetches a
replacement source/provider automatically.

The agent compares actual selected implementation resources before proposing
reuse, update or a new component. Lexical matches are candidates, not judgments.
Missing required knowledge or current policy blocks an unqualified conclusion.

A specification declares observable acceptance, non-goals, source scope, reuse
rationale, controlled files, exact argv, finite check limits and required review
roles. The executable schema is documented in the shipped
[specification reference](../../plugins/sparkforge/references/SPEC_FORMAT.md).
An exact-spec manual decision is necessary for the assisted workflow, but the
caller remains responsible for authentic authority and safe execution.

## State and evidence

The local job directory is explicitly selected, newly owned and separate from
the candidate workspace. SQLite transactions bind state and events; check intent
is reserved before dispatch. An unfinished reservation remains visible and must
be reconciled rather than blindly replayed.

Candidate manifests bind actual controlled bytes. A check records its command,
attempt, runner identity metadata, exit, output digest/count, required markers
and uncertainty. A passing exit is insufficient when evidence is incomplete.
Changing candidate bytes or check evidence invalidates dependent review context.

Before inspection, a reviewer captures the context for the job/spec/candidate/
round/evidence sequence. Submission must use that same context. The mechanism
detects stale assertions; it does not prove a person performed the review.

`CANDIDATE_VERIFIED` means the declared local check and review inventory is
complete for those bytes. Human acceptance, host security, current source rights
and external publication remain outside that result.

## Processes and resources

Checks use exact argv without a shell. `python` resolves to the current helper
interpreter; other executable paths are explicit. Each check has timeout,
output and attempt bounds. The caller must review the code loaded by a command,
not only its shape.

The child inherits the caller's environment. Filesystem/network confinement,
credential isolation, process-tree stopping and hard kernel deadlines are not
provided by this helper. Use a properly restricted operator-approved context.
Unknown effects or an unconfirmed stop remain a blocker.

## Packaging and deployment

Both metadata profiles derive from the same owned resources and exclude the
research corpus, runtime state and source captures. Profile names represent
requested targets, not evidence of access or compatibility. Installed discovery,
upgrade/uninstall, approved connectors and representative user journeys require
their own exact-host checks.

The publication is a standalone software checkout. Private platform operating
material is intentionally absent. Operators supply approved source inputs or
integration facts through their own authorized environment; no sibling private
directory is a software/test dependency.

## Feedback, learning and release

Feedback may lead to an in-scope repair or a revised specification and new
decision. A learning proposal is inactive until its hypothesis, source rights,
independent evaluation, exact promotion and rollback conditions are satisfied.
No-change is legitimate; recording a follow-up is not dispatch authority.

Local handoff, repository publication, platform contribution, installation and
production release are separate stages. None may silently inherit another
stage's approval, credentials, data scope or successful test result.
