# Self-improvement: public mechanisms and evidence boundaries

**Publication edition:** 2026-11-11. **Underlying review:** 2026-11-05.
**Scope:** research input for bounded learning, including SF-21.

This is a fresh public-source-only account, not a private project comparison,
a dependency installation, a model-training plan, or an implementation
completion report. The [source record](self-improvement-sources.json)
preserves identities, pins, dates, and review limits. Current product status
belongs to the project's living records, not this research page.

## Three loops that should not be confused

| Loop | Useful outcome | Boundary |
|---|---|---|
| Current-job correction | Repair a failed check within accepted scope | Bounded attempts; no new intent or authority |
| Product improvement | Turn permitted signals into proposed future work | An observation or ticket is not execution permission |
| Factory/project learning | Improve reusable expertise, a skill, or workflow | Inactive proposal, actual evaluation, independent review, authorized promotion |

More tickets, longer prompts, or a model's confidence do not establish
learning. A legitimate assessment may conclude that no reusable change is
needed. That is different from hiding a mandatory assessment failure.

## The Eric Tech video

[I Built a Self-Improving Software Factory](https://www.youtube.com/watch?v=aggJvNZxfKA)
is by Eric Tech / EricWTech, with a reported publication date of 2026-10-06.
It is a different video from the
[Eric Risco factory review](../../research/ai-factory/20-eric-risco-video-review.md).
Its description links to
[EricTechPro/super-board](https://github.com/EricTechPro/super-board), **not
Fluent**. The linked Super Board source was not audited.

The earlier review covered 382 unique available English auto-caption
segments, from 00:00 through 12:15, and one selected frame at 08:59. The player
duration was reported as 756.961 seconds. This is a recorded historical review
scope, not a new audiovisual review during publication. Auto-captions can
garble terminology. No raw captions, image, or video accompanies this account.

| Time | Described mechanism | Qualification |
|---|---|---|
| [00:08](https://www.youtube.com/watch?v=aggJvNZxfKA&t=8s) and [02:29](https://www.youtube.com/watch?v=aggJvNZxfKA&t=149s) | Collect signals into tickets and a project board | Source access, scheduling, and external issue writes need their own authorization |
| [02:58](https://www.youtube.com/watch?v=aggJvNZxfKA&t=178s) | Separate build, QA, review, and human-required work | Stage separation is useful; no reliability rate follows from a demonstration |
| [04:34](https://www.youtube.com/watch?v=aggJvNZxfKA&t=274s) | Check whether behavior is needed or already provided by code, a platform, or dependencies | Reuse-first investigation should precede new implementation |
| [05:33](https://www.youtube.com/watch?v=aggJvNZxfKA&t=333s) | Consult current dependency documentation | Reading guidance does not authorize connector or dependency installation |
| [07:05](https://www.youtube.com/watch?v=aggJvNZxfKA&t=425s) | QA checks actual ticket completion | Use appropriate unit, contract, integration, and end-to-end evidence |
| [08:59](https://www.youtube.com/watch?v=aggJvNZxfKA&t=539s) | Turn new signals and ideas into backlog work | Primarily a product-improvement loop, not demonstrated model-weight training |
| [09:22](https://www.youtube.com/watch?v=aggJvNZxfKA&t=562s) | Diagnose, refine, and reevaluate UI changes | Reuse the bounded critique/repair/evaluate pattern, not a UI-only requirement |
| [10:46](https://www.youtube.com/watch?v=aggJvNZxfKA&t=646s) | Claims about hooks, secret protection, skill evaluation, and documentation | Presentation claims, not independently audited control behavior |

The video supplies an accessible operating model. It does not establish
quantified improvement, universal model/host compatibility, safe production
telemetry collection, or permission to automate publication.

## Fluent is a separate reference

[mrinalwadhwa/fluent](https://github.com/mrinalwadhwa/fluent) was observed public
at commit `0871f94c95306230ad3729d736fbd8abc9e572bb`, dated 2026-11-01.
The historical review read its
[pinned README](https://github.com/mrinalwadhwa/fluent/blob/0871f94c95306230ad3729d736fbd8abc9e572bb/README.md)
in full. Its documented distinctions are useful independently of installing
the runtime:

- **Observations are not actions.** Record a signal without assuming enough
  evidence or authority to act.
- **Human attention and compute are separate queues.** One unanswered
  question need not halt unrelated ready work.
- **Shaping has layers.** Brief, Behavior Specifications, Technical Approach,
  and Implementation Plan separate different kinds of decisions.
- **Behavior diffs make changes inspectable.** Describe added, changed, and
  removed behavior, with explicit requirements and planned verification.
- **Creating a Work Item does not run or queue it.** Recording a handoff and
  spending execution resources are different events.
- **Independent review and the final Tester are distinct.** Worker reports,
  reviewer judgments, and actual command results are not interchangeable.
- **Learning follows reviewed and tested work.** Reusable Expertise may
  change; it may also legitimately remain unchanged.
- **Follow-ups are additional work.** The default `propose` posture waits for
  authorization; opt-in `execute` has a configured chain bound.
- **Landing is another decision.** A ready Merge Candidate does not itself
  change the target branch. Automatic landing is a separate opt-in policy.

The README's optional post-merge and corrective paths are documented features,
not authorizations for this project.

## Selected learning-handoff implementation

The earlier reading of
[`src/learner.rs`](https://github.com/mrinalwadhwa/fluent/blob/0871f94c95306230ad3729d736fbd8abc9e572bb/src/learner.rs)
covered production handoff functions through `load_verified_handoff` and the
opening test source. It did not cover the whole runtime or establish caller,
sandbox, promotion, or deployment correctness. Tests were read, not executed.

| Mechanism | Bounded source finding | Transferable lesson |
|---|---|---|
| Draft versus authoritative handoff | `stamp_handoff` supplies Work Item, Attempt, and Merge Candidate identities from caller context | The learner must not invent its own trusted provenance; caller authority still needs enforcement |
| Learning versus follow-ups | The handoff separates learning summary, expertise references, and follow-ups | Knowledge proposals and new work requests have different lifecycles |
| Inert output | Producing the handoff does not itself create observations, work items, or queue entries | Proposal creation is not execution authority |
| Conservative normalization | Incomplete corrective metadata can become observation-only; duplicate follow-up IDs are rejected | Normalization must not increase authority or hide mandatory failures |
| Content binding | Canonical JSON, SHA-256 references, and verification on load | Detect changed bytes before a consumer acts; hashes do not authenticate the actor |
| Optional no-change path | An absent optional draft can yield zero follow-ups | No-op can be valid, but not a substitute for a failed required assessment |
| Atomic writing | The module calls an atomic handoff writer | Atomicity alone does not establish write-once immutability or permission |

Normalization returns notes, but the inspected `stamp_handoff` binds them as
`_normalizations`. That function alone is not evidence that every correction
is surfaced operationally. Material invalid metadata and allowed downgrades
should be visible to a consumer rather than interpreted as automatic validity.

## Licensing and platform limits

Fluent's
[pinned root license](https://github.com/mrinalwadhwa/fluent/blob/0871f94c95306230ad3729d736fbd8abc9e572bb/LICENSE)
was identified as Apache-2.0 from the opening license text and metadata.
This is not a complete license, trademark, dependency, or distribution audit.
No Fluent source or license text is copied into this repository.

The README at that pin advertised installation as **macOS only**. Interactive
skill and autonomous coder profiles are separate choices; examples discuss
Codex, Claude, and Pi. Native Windows and a selected custom host were not
qualified. AWS Fargate execution introduces a separate runtime/data boundary,
not an automatic fallback.

The justified use here is **design reference**, not runtime adoption.
Compatibility, selected-file terms, dependencies, credentials, data
destinations, and operational behavior need their own review before reuse.

## A bounded design to evaluate

The following is original design synthesis, not a claim that the references
or this publication implemented and passed these controls:

1. Accept only permitted feedback and scoped job/check/review evidence.
   Do not sweep unrelated personal histories or production logs.
2. Bind observations to host-supplied origin, project/environment scope, and
   exact source revisions. A user-provided actor label is not authentication.
3. Record an explicit `NO_CHANGE` or an **inactive** candidate with a
   falsifiable hypothesis, baseline, target, risks, and verification plan.
4. Keep follow-up work proposals inert until the applicable intent and
   execution authorization exist.
5. Actually compare baseline and candidate using protected regression,
   negative controls, and held-out acceptance where applicable. Record failed,
   skipped, incomplete, and adverse results, not just apparent improvements.
6. Require independent review, including semantic conflicts with policy.
   Protected-file hashes alone do not establish that a new rule is safe.
7. Promote only the exact independently accepted version to an authorized
   target. Keep the active version identifiable, monitor it, and support
   qualified withdrawal or rollback.
8. Never let the learner grant itself permissions, rewrite approval rules,
   weaken protected acceptance, change providers, or reset budgets.

Proposal-only follow-ups are the conservative starting point. Automatically
executed chains, new telemetry connectors, scheduled collection, issue
creation, and deployment require separately approved policies and evidence.

Useful acceptance cases include missing or unauthorized inputs, invented
provenance, a sound no-change outcome, missing mandatory evaluation,
regression rejection, stale promotion, attempted self-approval, inert
follow-ups, cross-scope isolation, and withdrawal of a previously useful
lesson. These are proposed tests, not passing results.

Success is an improvement supported by actual comparative evidence and
independent authorization, or a justified decision to reject, withdraw, or
make no change. It is not a requirement that every run invent a new lesson.
