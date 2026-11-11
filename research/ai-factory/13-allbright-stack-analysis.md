# 13 - Critical Reading of the Allbright Stack

[Back to the index](README.md)

## Source

Andrew Allbright, **From AI Harness to Software Factory: A Practical Agentic Engineering Stack**, published June 21, 2026 according to the supplied article. The original page was also retrieved. [S42](16-sources-and-reading-guide.md#s42)

This is a practitioner architecture, not a standardized reference architecture or a comparative study. Its main value is showing how familiar tools can be composed into a shared way of working.

## The argument in our own words

An individual can gain capability from an AI assistant. A team needs more: common entry points, repeatable environments, explicit roles, documented conventions, work tracking, and observable results.

The proposed stack uses:

- Taskfile for discoverable operations;
- Claude or another agent platform for execution;
- role-based agents or skills for specialized work;
- tmuxinator for a shared terminal/process layout;
- Jira or an equivalent tracker for assigning work;
- separate repositories for some generated artifacts.

The transferable insight is **shared operating contracts**, not allegiance to these exact tools.

## Claim-by-claim analysis

| Article idea | What is useful | Qualification needed |
|---|---|---|
| A factory adds repeatability, auditability, and team ownership | Correctly widens the problem beyond model capability | A mature harness can already implement some of these; the terms are not universally standardized |
| Taskfile is a control-plane contract | A discoverable command registry reduces hidden knowledge | A task runner alone is not authorization, durable scheduling, or audit infrastructure |
| Personas encode team practices | Role-specific context can focus work | Persona, skill, tool, and subagent are different mechanisms |
| A linter persona enforces style | Automated style checks reduce review burden | Prefer the deterministic linter for enforcement; a model can interpret or repair its findings |
| Tmuxinator gives common runtime signals | Reproducible process startup improves feedback | A visible pane is not automatically visible to an agent through its tools |
| A ticket system is the job queue | Work has a common origin and ownership | Reliable execution additionally needs leases, deduplication, attempts, and recovery |
| Main repo and sub-repo separate control and data | Separate lifecycles can reduce clutter | Repo boundaries do not automatically enforce trust, permission, or retention |
| Volatile artifacts can be garbage-collected without affecting reproducibility | Some scratch data is disposable | Deleting inputs, evidence, or referenced artifacts can destroy reproducibility |
| Knowledge compounds across invocations | Reviewed lessons can improve later work | This requires deliberate storage, retrieval, freshness, and evaluation; it is not automatic training |
| Humans and agents become interchangeable | Shared interfaces can make collaboration easier | Accountability, judgment, rights, and failure characteristics are not interchangeable |

These are refinements of the proposal, not reasons to discard it.

## Taskfile as an entry-point registry

Task's official documentation describes command tasks, dependencies, sequential calls, environment handling, platform-specific steps, and output modes. [S44](16-sources-and-reading-guide.md#s44)

A useful command registry might expose these **conceptual contracts**:

| Operation | Contract |
|---|---|
| `task help` | Show supported operations and prerequisites |
| `task verify` | Run defined checks and return a non-success status when required checks fail |
| `task dev` | Start a documented local environment and expose readiness |
| `task evidence` | Assemble results for the current candidate revision |
| `task review` | Produce review findings without changing the candidate |

These names are illustrative; no Taskfile has been created.

Two details matter:

1. Task dependencies can run concurrently. Listing `build` before `test` in `deps` does not establish order. Use sequential task calls when one stage must finish first.
2. Task uses an embedded shell, not necessarily the user's interactive shell. Separate command entries do not automatically share changed directory or environment state.

Those details can turn an apparently repeatable command into a subtly incorrect workflow if ignored.

## What makes a command a real contract

Record:

- working directory;
- input and environment requirements;
- supported platforms;
- dependencies and their versions;
- side effects;
- expected outputs;
- exit-status semantics;
- timeout and cancellation behavior;
- cleanup ownership;
- where evidence is written.

A command that prints "all good" while suppressing a failed child process is not a quality gate.

The same contract should be used locally and in CI where practical, while allowing environment-specific setup.

## Personas versus machinery

The article's roles are useful work categories: architect, debugger, documentation maintainer, and reviewer.

Implement each role with the least complex mechanism:

- A formatter is usually an ordinary program.
- A test runner is usually an ordinary program.
- A debugging agent can choose which observations to gather.
- A documentation skill can guide a worker without creating another agent.
- An independent review may justify a separate read-only context.

Do not pay for an LLM to perform a deterministic check that a mature tool already handles reliably.

Business rules should not live only in persona prompts. Rules that govern authority, data access, or release need enforceable representations.

## The developer environment

Tmuxinator manages tmux sessions using configuration. Its README assumes tmux and a Ruby environment. It is not a universal process supervisor or a native-Windows requirement. [S45](16-sources-and-reading-guide.md#s45)

The principle to preserve is:

> Make the environment easy to start, inspect, and reproduce, and give both humans and agents access to actionable feedback.

For our Windows context:

| Need | Native Windows possibility | Optional alternative |
|---|---|---|
| Multiple visible terminals | Windows Terminal panes | tmux/tmuxinator in an intentionally selected Unix-like environment |
| Repeatable commands | Existing package/build tools, Task, or explicit PowerShell scripts | Equivalent commands in WSL or a container |
| Test feedback | Structured runner output and captured exit status | Watchers with machine-readable events |
| Service readiness | Explicit health probe and process identity | Container health checks or supervised remote service |
| Workspace isolation | Separate working directories/worktrees | Dedicated container or VM |

Windows Terminal documents support for panes, but panes alone do not provide durable execution or automatic recovery. [S47](16-sources-and-reading-guide.md#s47)

No environment option has been selected or installed.

## Work tracking versus execution state

A ticket is a good place for human intent, priority, and ownership. It is usually not enough to represent:

- all tool attempts;
- the current lease holder;
- an uncertain external write;
- aggregate budget consumption;
- a paused approval;
- exact environment state.

Link the ticket to a durable run record rather than filling the ticket with every transient event. Keep the two synchronized through explicit transitions.

A ticket comment saying "done" should not override failed acceptance checks.

## Artifact separation and retention

Classify artifacts by purpose rather than by whether AI generated them:

| Artifact | Likely treatment |
|---|---|
| Accepted architecture decision | Reviewed project knowledge |
| Candidate architecture sketch | Draft with provenance |
| Temporary tool output | Short-lived working data if not needed as evidence |
| Release test results | Retained evidence tied to the release |
| Private source dataset | Authorized data store with access and retention controls |
| Agent transcript | Restricted retention based on purpose and sensitivity |
| Secret | Secret-management system, not a document repository |

A decision record may be stable control knowledge even if an agent drafted it. A human-written log can still be transient. "AI-generated" is not a useful retention class.

Garbage collection should respect references and evidence obligations. If a release decision points to a deleted artifact, auditability has been weakened.

## Observability from the start

Task names are good labels for measurement, but measurement still needs implementation.

Capture a run ID, timestamps, artifact revision, exit status, usage where applicable, and acceptance result. Later, add richer traces as needed.

Likewise, a rule in CLAUDE.md can be reviewed as text, but auditing compliance requires evidence that executions followed it.

## A revised version of the stack

Our synthesis:

1. **Shared operations:** a task registry with explicit contracts.
2. **Execution:** bounded agents and deterministic tools in an intentional environment.
3. **Knowledge:** versioned project information with ownership and provenance.
4. **Work state:** task identities, dependencies, attempts, and recovery.
5. **Verification:** independent checks and clear acceptance criteria.
6. **Authority:** identity, permissions, approvals, and protected promotion.
7. **Evidence and learning:** structured records, retention, and evaluated improvements.

This preserves the article's practical simplicity while making the missing boundaries explicit.

## What to borrow first

Borrow the shared command vocabulary and a small, well-indexed knowledge base. Make one workflow reproducible and verifiable. Do not begin by installing every suggested tool or creating a persona for every team role.

The article is an excellent orientation source when read alongside protocol documentation, evaluation guidance, and the reliability material in this corpus.
