# Offline user preview

## What this surface does

`preview\index.html` is a self-contained, tab-local prototype of the user
journey. It uses fictional examples, simple word matching and deterministic
text templates. It is separate from the [native assisted factory](NATIVE_FACTORY.md):
it does not run the Python helpers, inspect a repository/wiki, call a model,
execute acceptance checks, install a package or publish a result.

Its purpose is to make the intent → scope → decision → tangible draft →
feedback loop reviewable without pretending a factory run occurred.
Use non-sensitive fictional input only. Any platform labels in the UI
describe unassessed targets, not a confidential platform contract.

## Open and explore

From the repository root, open `preview\index.html` in a modern browser.
No server, package installation or external resource is required.
For example:

```powershell
Start-Process (Resolve-Path 'preview\index.html').Path
```

Use the fictional incident-handoff or weekly-brief example, or enter
non-sensitive synthetic text. This is a preview demonstration, not an
accepted native brief.

1. **Describe:** enter a title, desired outcome, audience and optional
   supplied input notes.
2. **Assess fit:** inspect the small fictional catalog, choose reuse,
   adapt or a new draft, and state the rationale, non-goals and observable
   acceptance checklist.
3. **Review brief:** inspect that exact revision. Approve only the local
   preview, keep it unapproved, or edit it. This decision grants no real
   source access, coding, execution or publication authority.
4. **Preview and feedback:** assemble in-tab documents, inspect/select
   their text, request a revision, and optionally capture an inactive idea
   linked to recorded feedback.

The summary checks cover completeness and current preview approval, not
the behavior of any generated component. A missing fictional match says
nothing about capabilities in the operator's real environment.

## Documents and revision behavior

- **Reuse** produces a `REUSE_PLAN.md`, not a new skill.
- **Adapt** includes a `CHANGE_PLAN.md` and a proposed skill template.
- **New draft** includes a proposed skill template without a sample target.
- All routes include a `REVIEW_CHECKLIST.md` and `PREVIEW_RECORD.json`.

These are strings held in the tab, not files written to disk. The UI can
select text; it supplies no installer or automatic download. Checkboxes
remain a proposed checklist, never passing test evidence.

Approval is bound to the displayed preview revision and snapshot.
Changing an approved brief withdraws approval and invalidates artifacts.
Feedback records the inspected revision and artifact names, then opens a
new draft; it does not silently implement the requested change.
An improvement idea references feedback and remains `PROPOSED` with
`active: false`. No learning evaluation or promotion occurs.

## Privacy and trust limits

The preview calls no model or company service and has no automatic saving
or storage API. Refreshing or resetting clears its tab-local state.
The page's content policy blocks connections, and its own scripts use
local assets. That does not establish browser/extension/OS-level data
isolation or secure erasure; do not enter sensitive information.

Preview approvals and history are ordinary mutable browser state, not
authenticated decisions or an authoritative ledger. Exporting selected
text manually is a separate user action with its own data obligations.
The preview's record reports `LOCAL_PREVIEW_ONLY`,
`realCoverage: NOT_ASSESSED`, and false host/execution/runtime/learning
flags. It is not the native `sparkforge.spec.v1` schema and cannot be
treated as an accepted job by changing a label.

## Available browser checks and next boundary

`preview\browser-checks.html` is the shipped local browser harness.
It can be opened locally to exercise the prototype's model/UI behavior;
its results describe that browser session only. This document contains no
claim that browser checks or a real host were run during publication.

For real work, return to the native workflow: authorized actual source and
code inspection, a concrete spec, genuine operator decision, host editing,
real accepted-command checks and independent review. Corp and Acro must
be assessed independently. Do not carry a preview approval, fictional
catalog match or deterministic checklist across that boundary as evidence.
