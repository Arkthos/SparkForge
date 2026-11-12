# Factory and harness patterns

**Historical public-source baseline:** 2026-11-05. **Edition:** 2026-11-12.
These are bounded source and documentation findings, not executed frameworks.
Private adapter and operating-process comparisons are excluded.

Small deterministic controllers, complete hosted products, natural-language
specifications, and alternative agent runtimes answer different questions.
Calling them all interchangeable "agent frameworks" obscures the decisions
that determine authority, reliability, cost, and integration work.

## 1. SSSF: deterministic control around bounded agent work

[Super Simple Software Factory](CATALOG.md#sssf) is an unusually readable
implementation reference. The selected main branch contains a skill and
implementation templates; the separate example branch was not inspected.

### Phase success versus product acceptance

The [runner](EVIDENCE.md#sssf-run-acceptance) exposes human, agent, and code
phases. A phase succeeds when its body completes normally. Final `finish`
acceptance separately requires a nonempty collection of successful phases
and the caller's acceptance condition, and records run status with its exit
result.

A test-running phase can therefore do its job correctly while executing a
failing test suite. The command ran; the product is not accepted. Collapsing
those facts into one "completed" status would lose the most important result.

The pattern is useful, but a caller still has to supply the correct acceptance
condition. A generic default cannot infer the product's requirements. Nor does
successful use of the phase primitive prove every workflow built with it.

### Typed envelopes, gates, corrections, and usage

The [agent-call implementation](EVIDENCE.md#sssf-agent-calls) resolves configured
agents, checks for their prompts, invokes a supported backend, parses an output
type, and applies declared claim gates. Invalid JSON and failed gates feed
bounded correction requests into the same session. Usage accumulates across
attempts instead of reporting only the final attempt.

| Responsibility | Distinct question it answers |
|---|---|
| Output schema | Is the communication well formed and complete enough to inspect? |
| Claim or domain gate | What does the returned evidence actually establish? |
| Retry budget | When must repair stop, defer, or escalate? |
| Whole-run acceptance | Is the requested outcome ready under its actual criteria? |
| Trace | What happened, including failed attempts and their cost? |

Typed JSON does not prove correct code. Meaningful gates need substantive
assertions and an expected inventory of required checks; otherwise a smaller
all-green subset can conceal missing evidence.

### Observability and actual limits

The [trace schema](EVIDENCE.md#sssf-tracing) records sessions, phases, events,
envelopes, gate results, process identity, and model usage using JSONL and a
SQLite mirror. Capturing what a gate checked is more useful than preserving
only its color. Process identity includes PID and command context, useful for
recognizing owned work during recovery.

This is observability, not tamper-proof audit storage. Prompts, arguments,
results, and errors may be confidential and need explicit retention, access,
and export policies.

Selected implementation limits materially affect adoption:

- Backend validation accepts **Pi only** at this pin.
- Write-permission checking happens after agent calls, before envelope
  acceptance. That does not prevent the write or a network side effect.
- The [Git helper](EVIDENCE.md#sssf-git) stages with `git add -A`, unsuitable
  as an automatic default in a dirty/shared workspace containing unrelated
  user work.

The contribution is the understandable control structure, not a drop-in
replacement for the operator-selected coding host.

## 2. BMad Loop: separate the CLI contract from transport

[BMad Loop](CATALOG.md#bmad-loop) documents selection, implementation,
verification, review, and commit with resumable state, bounded attempts,
single-writer board ownership, deferred work, and environment-fault handling.
This study inspected selected adapter/profile implementation and operating
documentation, not the whole engine.

The [adapter guide](EVIDENCE.md#bmad-loop-transport) distinguishes two seams:

- **Coding CLI:** executable, rendered prompt, hooks, transcript, usage, and
  completion semantics.
- **Transport:** session or pane creation, observation, attachment, and
  termination.

That distinction keeps host-specific machinery from disappearing inside a
generic loop. A supported CLI label does not establish compatibility with
every operating system, wrapper, or transport.

The guide distinguishes an ended session from a live but quiet one, and an
unknown transport observation from a confirmed absence. Losing a connection
or seeing no new output does not prove that work failed or justify launching
a duplicate operation.

### The bundled Copilot profile is concrete, not a policy recommendation

The [captured profile](EVIDENCE.md#bmad-loop-copilot) invokes `copilot` with a
particular interactive prompt shape, grants all tools/paths/URLs through broad
bypass flags, and records a specific CLI build observation on macOS. It also
distinguishes main-session completion from subagent stop events and allows a
short grace period for usage written after completion.

Older skill-discovery comments in that file are not authority over newer
official documentation or the actual selected host. The relevant contract
must be checked, not inferred from comments or a compatibility badge.

The [profile adapter](EVIDENCE.md#bmad-loop-permissions) rejects non-bypass mode
when the profile has no mapping or excludes the platform. The captured
Copilot TOML contains no non-bypass mapping. That is an integration blocker
where bypass is unacceptable, not permission to circumvent host policy.

The [configuration guide](EVIDENCE.md#bmad-loop-policy) raises additional
questions: some budgets are advisory; verification commands require explicit
configuration; review selection can depend on the implementer's recommendation;
and resume can reload current policy. Each affects the relationship between
accepted intent, current evidence, and enforceable limits.

Native Windows `psmux` transport is described as experimental. Worktree
separation and local merge-back also do not establish an authorized remote
delivery policy. The historical project is early beta, not a qualified
production dependency.

## 3. Foreman/eve: product stations and action-specific authority

[Foreman](CATALOG.md#eve-foreman) offers a recognizable end-to-end experience:
classify work, analyze the repository, implement at a separate station, review
against the work item, and prepare a draft PR. A shared factory brain carries
recurring project knowledge.

The [operating instructions](EVIDENCE.md#eve-pipeline-instructions) stop for
clarification, call for self-contained handoffs, route research before analysis
where needed, and bound revision cycles. The
[reviewer wrapper](EVIDENCE.md#eve-review-wrapper) invokes a separate station
with a required output schema, rather than automatically supplying the
orchestrator's entire conversation.

Separate context is useful, but independence is not absence of context. The
reviewer intentionally receives the work item, criteria, branch, and
implementer's report. It still must inspect the actual changed artifacts and
checks instead of merely endorsing that report.

### Instructions are not all code-enforced transitions

In the inspected source, station order and revision limits appear in
instructions. The study did not establish a complete code-enforced
cross-station state machine. In contrast, the
[approval predicates](EVIDENCE.md#eve-approval) are selected actual code,
with different outcomes for different identities and effects.

The distinctions include unattended service identity, trusted callers,
scheduled app identity, and ordinary requests:

- Unattended comments can be limited to the stamped intake issue.
- Unattended factory runs cannot mutate the shared brain.
- Trusted callers and scheduled app turns can update it without an approval
  card.
- Draft PR creation has a different approval condition from shipping work
  ready for review.
- Moving work to ready-for-review remains a separate human shipping step.

The [trust helpers](EVIDENCE.md#eve-trust) obtain authority from session
context rather than model prose. Full webhook and channel verification were
not traced. These observations therefore describe selected policy mechanisms,
not universal human approval or an end-to-end security certification.

### A local interface with hosted execution

The [sandbox implementation](EVIDENCE.md#eve-sandbox) selects hosted Vercel
Sandbox for local development as well as production. A local TUI does not
establish local computation or data retention. The README's deploy
configuration also calls for a public Blob store, a separate storage review
concern before considering restricted inputs.

The [brain-writing tool](EVIDENCE.md#eve-brain-write) derives a configured
repository key, evaluates policy, and overwrites a bounded shared document.
A current shared document and immutable decision/evidence history are useful
for different purposes. One should not be misrepresented as the other.

Stations, self-contained handoffs, and separate write authorities can be
borrowed conceptually without adopting the hosting backend, external
integrations, or upstream policy.

## 4. Attractor, Fabro, and Roast: different orchestration contributions

[Attractor](CATALOG.md#attractor) contains natural-language specifications,
not an executable runtime qualified in this study. The
[reviewed introduction](EVIDENCE.md#attractor-design) separates a declared
graph, pluggable handlers, state, human decision nodes, backend execution,
checkpoint/resume concepts, and a presentation layer consuming events.
Only the opening orchestration-specification range was semantically reviewed;
the companion specifications were not deeply inspected.

[Fabro](CATALOG.md#fabro) is a graph-oriented product whose README describes
human gates, model routing, a server/UI, durable outputs, checkpoints, and
cloud sandbox choices. It is useful for comparing visible graphs and
intervention points. Automatic provider fallback, Git checkpoint behavior,
and external sandbox choices need their own assessment. README promises of
quality or scale are not measured acceptance evidence.

[Roast](CATALOG.md#roast) is a Ruby DSL composing deterministic code/command
steps with model and agent steps, iteration, mapping, and reusable scopes.
It illustrates that a model need not decide every mechanical transition.
The reviewed agent providers are Pi and Claude; the additional Ruby runtime
and provider configuration do not establish another host's compatibility.

These projects share design concerns. This study does not claim they are
interchangeable, share an audited lineage, or can be stacked without duplicate
state ownership.

## 5. Alternative runtimes and factory comparisons

[Deep Agents](CATALOG.md#deepagents) documents a LangChain/LangGraph harness
with subagents, filesystem backends, context offloading, memory, skills, and
tool approval. Its explicit backend interfaces are useful design references.
The README locates security at the tool/sandbox boundary, not in model
self-restraint. Optional hosted tracing has a separate data boundary.

[OpenHands SDK](CATALOG.md#openhands-sdk) separates tools, conversations,
workspaces, events, typed clients, and an Agent Server. The SDK repository is
not the entire OpenHands product or automation service. Product or benchmark
claims do not qualify an unrelated selected host or workload.

[mini-SWE-agent](CATALOG.md#mini-swe-agent), reviewed as v2, provides a
minimality counterexample: a small linear loop with independent shell
execution can be useful for bounded coding work. A small tool count is not
small authority. A general shell has the capabilities of its process
identity; Bash-oriented execution and external adapters are not Windows or
custom-host acceptance.

The [Archon-based wrapper](CATALOG.md#archon-factory) contributes mission and
non-goals, user journeys, independent holdouts, deliberate-defect calibration,
scheduling, and staging-feedback ideas. No root reuse license was established,
and the underlying Archon implementation was not deeply inspected. Automatic
merge, deployment, and scheduled external operations are not permissions
granted by the research. Keep it a conceptual comparison until rights and
behavior are independently resolved.

## 6. Cross-cutting design lessons

| Retain | Do not substitute |
|---|---|
| Deterministic ownership of consequential transitions | One giant prompt saying to continue until done |
| Typed artifacts plus independent acceptance | Valid JSON or a success label as product proof |
| Bounded repair with failure classification | Automatic credential changes, widened tools, or endless retries |
| Durable state and explicit recovery identity | Re-execution merely because a connection disappeared |
| Separate review context and real artifact inspection | The builder's narrative as the entire review evidence |
| Owned workspaces, paths, and process identities | Broad staging or generic process-name termination |
| Proposal/evidence authority separated from effects | A model verdict as permission to merge or deploy |
| Small, comprehensible capability interfaces | Several overlapping frameworks installed by default |

Every mechanism still has to fit the selected source, host, and permission
contract. The private implementation comparisons that once accompanied this
table are not included and cannot be inferred from it.

## 7. ZazenCodes follow-up: the small factory evolves

The [detailed video review](VIDEO_ZAZEN_FACTORY.md) preserves a practical
example of constructing a small skill-led factory, encountering friction, and
adding worktrees for parallel jobs. Its original shared-board build prompt
is not its final state. The pinned later v1 companion has per-job state,
distinct artifact owners, absolute worktree paths, separate browser/port
identities, and a complete review-round barrier.

Those are valuable responsibility and handoff contracts, not demonstrated
deterministic permission enforcement. V1 permits model-authorized local
integration into `main` while explicitly forbidding push. It does not
demonstrate the required pre-code human brief gate. V2's separate README
describes script-backed state/check gates and PR delivery, but executable
implementation was not reviewed and model-authorized merging remains a
documented policy. Version distinctions and actual authority must remain
visible in any reuse decision.
