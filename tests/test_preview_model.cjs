"use strict";

const test = require("node:test");
const assert = require("node:assert/strict");
const preview = require("../preview/model.js");

function displayed(state) {
  return { revision: state.revision, snapshotKey: preview.snapshotKey(state) };
}

function approvedExample(id = "incident") {
  const state = preview.createExample(id);
  return preview.approvePreview(state, displayed(state));
}

function expectCode(action, code) {
  assert.throws(action, (error) => error instanceof preview.PreviewError && error.code === code);
}

test("a fresh preview has no implicit selection, approval or authority", () => {
  const state = preview.initialState();
  assert.equal(state.revision, 1);
  assert.equal(state.approval, null);
  assert.equal(state.artifacts, null);
  assert.equal(state.draft.decision, "");
  const report = preview.readiness(state);
  assert.equal(report.realCoverage, "NOT_ASSESSED");
  for (const flag of ["hostQualified", "executionAuthorized", "runtimeReady", "learningActivated"]) {
    assert.equal(report[flag], false);
  }
});

test("examples are fictional, complete, distinct, and unapproved", () => {
  for (const id of Object.keys(preview.EXAMPLES)) {
    const state = preview.createExample(id);
    assert.deepEqual(preview.validateDraft(state.draft), {});
    assert.equal(state.approval, null);
    assert.equal(preview.assessSamples(state.draft).realCoverage, "NOT_ASSESSED");
  }
  assert.notEqual(preview.createExample("incident").draft.title, preview.createExample("weekly").draft.title);
  expectCode(() => preview.createExample("__proto__"), "UNKNOWN_EXAMPLE");
});

test("editing an example never mutates the catalog, fixture or prior state", () => {
  const state = preview.createExample("incident");
  const saved = JSON.stringify(state);
  const next = preview.setField(state, "goal", "Different preview goal");
  assert.equal(JSON.stringify(state), saved);
  assert.notEqual(next.draft.goal, preview.EXAMPLES.incident.goal);
  assert.ok(Object.isFrozen(preview.CATALOG[0]));
});

test("field updates reject unknown fields and non-text values", () => {
  const state = preview.initialState();
  for (const field of ["__proto__", "hostQualified", "approval"]) {
    expectCode(() => preview.setField(state, field, "yes"), "UNKNOWN_FIELD");
  }
  for (const value of [null, true, 42, {}, []]) {
    expectCode(() => preview.setField(state, "goal", value), "INVALID_FIELD_TYPE");
  }
});

test("incomplete intake produces actionable errors, not a ready state", () => {
  const errors = preview.validateDraft(preview.initialState().draft, "intake");
  assert.ok(errors.title && errors.goal && errors.audience);
  assert.equal(errors.criteria, undefined);
  expectCode(() => preview.validateDraft({}, "unknown"), "UNKNOWN_STAGE");
});

test("a later scope-field error does not trap the user on the intake step", () => {
  const state = preview.setField(preview.createExample("incident"), "rationale", "x".repeat(1601));
  assert.deepEqual(preview.validateDraft(state.draft, "intake"), {});
  assert.ok(preview.validateDraft(state.draft, "scope").rationale);
});

test("length limits reject rather than silently truncate input", () => {
  for (const [field, limit] of Object.entries(preview.LIMITS)) {
    const state = preview.setField(preview.createExample("incident"), field, "x".repeat(limit + 1));
    assert.equal(state.draft[field].length, limit + 1);
    assert.ok(preview.validateDraft(state.draft)[field]);
  }
});

test("empty criteria, non-goals and unsafe names cannot be approved", () => {
  for (const [field, value] of [["criteria", "\n \n"], ["nonGoals", ""], ["title", "../.."]]) {
    const state = preview.setField(preview.createExample("incident"), field, value);
    expectCode(() => preview.approvePreview(state, displayed(state)), "BRIEF_INCOMPLETE");
  }
  assert.equal(preview.slug("A name / with spaces"), "a-name-with-spaces");
  assert.equal(preview.slug("../../"), "");
});

test("sample matching explains words and never claims real coverage", () => {
  const assessment = preview.assessSamples(preview.createExample("incident").draft);
  assert.equal(assessment.matches[0].id, "sample-incident-summary");
  assert.ok(assessment.matches[0].matchedWords.includes("incident"));
  assert.equal(assessment.realCoverage, "NOT_ASSESSED");
  assert.equal(assessment.catalogVersion, "fictional-catalog-v1");
});

test("an empty sample match is not proof no real component exists", () => {
  const state = preview.setField(preview.initialState(), "goal", "zyxwvu");
  const result = preview.assessSamples(state.draft);
  assert.deepEqual(result.matches, []);
  assert.equal(result.realCoverage, "NOT_ASSESSED");
});

test("reuse and adaptation require a known fictional target and reason", () => {
  for (const decision of ["reuse", "adapt"]) {
    let state = preview.setField(preview.createExample("incident"), "decision", decision);
    state = preview.setField(state, "targetId", "unread-real-component");
    assert.ok(preview.validateDraft(state.draft).targetId);
    state = preview.setField(state, "rationale", "");
    assert.ok(preview.validateDraft(state.draft).rationale);
  }
});

test("choosing a new draft clears an old sample association", () => {
  const state = preview.setField(preview.createExample("incident"), "decision", "new");
  assert.equal(state.draft.targetId, "");
  assert.deepEqual(preview.validateDraft(state.draft), {});
});

test("unknown decisions and contradictory new-draft associations are rejected", () => {
  let state = preview.setField(preview.createExample("incident"), "decision", "deploy");
  assert.ok(preview.validateDraft(state.draft).decision);
  state = preview.setField(state, "decision", "new");
  state = preview.setField(state, "targetId", "sample-weekly-brief");
  assert.ok(preview.validateDraft(state.draft).targetId);
});

test("a complete draft cannot assemble documents without preview approval", () => {
  expectCode(() => preview.assemblePreview(preview.createExample("incident")), "APPROVAL_REQUIRED");
});

test("approval binds the exact displayed content, not only a revision number", () => {
  const state = preview.createExample("incident");
  const oldDisplay = displayed(state);
  const edited = preview.setField(state, "goal", "A changed desired outcome.");
  assert.equal(edited.revision, state.revision);
  expectCode(() => preview.approvePreview(edited, oldDisplay), "STALE_REVIEW");
});

test("approval requires an actual displayed snapshot", () => {
  const state = preview.createExample("incident");
  for (const view of [null, {}, { revision: 0, snapshotKey: preview.snapshotKey(state) }]) {
    expectCode(() => preview.approvePreview(state, view), "STALE_REVIEW");
  }
});

test("repeated approval and assembly are idempotent", () => {
  const state = approvedExample();
  assert.equal(preview.approvePreview(state, displayed(state)), state);
  const assembled = preview.assemblePreview(state);
  assert.equal(preview.assemblePreview(assembled), assembled);
});

test("rejecting a preview cannot assemble documents or confer approval", () => {
  const state = preview.declinePreview(preview.createExample("incident"));
  assert.equal(state.reviewStatus, "REJECTED");
  assert.equal(state.approval, null);
  expectCode(() => preview.assemblePreview(state), "APPROVAL_REQUIRED");
  const edited = preview.setField(state, "goal", "Revised outcome");
  assert.equal(edited.reviewStatus, "DRAFT");
});

test("withdrawing a prior preview approval invalidates its artifacts", () => {
  const state = preview.declinePreview(preview.assemblePreview(approvedExample()));
  assert.equal(state.revision, 2);
  assert.equal(state.artifacts, null);
  assert.equal(state.approval, null);
  assert.equal(preview.readiness(state).executionAuthorized, false);
});

test("every brief field invalidates prior approval and document previews", () => {
  for (const field of preview.FIELDS) {
    const original = preview.assemblePreview(approvedExample());
    const next = preview.setField(original, field, original.draft[field] + " changed");
    assert.equal(next.revision, 2, field);
    assert.equal(next.approval, null, field);
    assert.equal(next.artifacts, null, field);
    assert.equal(original.revision, 1, field);
    assert.equal(preview.approvalCurrent(next), false, field);
  }
});

test("further edits share the new draft revision; a no-op edit changes nothing", () => {
  const approved = approvedExample();
  assert.equal(preview.setField(approved, "title", approved.draft.title), approved);
  const next = preview.setField(approved, "goal", "First change.");
  const again = preview.setField(next, "audience", "Another reader");
  assert.equal(again.revision, 2);
});

test("a directly changed draft cannot reuse a stale approval", () => {
  const state = approvedExample();
  const tampered = { ...state, draft: { ...state.draft, goal: "Changed outside the UI." } };
  assert.equal(preview.approvalCurrent(tampered), false);
  expectCode(() => preview.assemblePreview(tampered), "APPROVAL_REQUIRED");
});

test("adaptation produces a change plan, skill template and unexecuted checklist", () => {
  const state = preview.assemblePreview(approvedExample());
  const names = state.artifacts.files.map((file) => file.name);
  assert.ok(names.includes("CHANGE_PLAN.md"));
  assert.ok(names.some((name) => name.endsWith("\\SKILL.md")));
  assert.ok(names.includes("REVIEW_CHECKLIST.md"));
  assert.ok(state.artifacts.files.every((file) => typeof file.content === "string"));
  const record = JSON.parse(state.artifacts.files.find((file) => file.name === "PREVIEW_RECORD.json").content);
  assert.equal(record.previewApproved, true);
  assert.equal(record.executionAuthorized, false);
  assert.equal(record.realCoverage, "NOT_ASSESSED");
});

test("reuse does not quietly generate a new skill", () => {
  let state = preview.setField(preview.createExample("weekly"), "decision", "reuse");
  state = preview.assemblePreview(preview.approvePreview(state, displayed(state)));
  assert.ok(state.artifacts.files.some((file) => file.name === "REUSE_PLAN.md"));
  assert.ok(state.artifacts.files.every((file) => !file.name.endsWith("SKILL.md")));
});

test("new-draft output is a template without a fictional change baseline", () => {
  let state = preview.setField(preview.createExample("incident"), "decision", "new");
  state = preview.assemblePreview(preview.approvePreview(state, displayed(state)));
  assert.ok(state.artifacts.files.some((file) => file.name.endsWith("\\SKILL.md")));
  assert.ok(state.artifacts.files.every((file) => file.name !== "CHANGE_PLAN.md"));
  assert.match(state.artifacts.files[0].content, /deterministic template/);
});

test("feedback remains linked to the old preview and requires a new approval", () => {
  const original = preview.assemblePreview(approvedExample());
  const next = preview.requestChanges(original, "Put open questions before the timeline.");
  assert.equal(next.feedback[0].revision, 1);
  assert.ok(next.feedback[0].artifactNames.length);
  assert.equal(next.revision, 2);
  assert.equal(next.approval, null);
  assert.equal(next.artifacts, null);
  assert.equal(next.draft.goal, original.draft.goal);
  expectCode(() => preview.assemblePreview(next), "APPROVAL_REQUIRED");
});

test("feedback cannot manufacture an observation before a current preview", () => {
  expectCode(() => preview.requestChanges(preview.createExample("incident"), "Change this"), "PREVIEW_REQUIRED");
  expectCode(() => preview.requestChanges(preview.assemblePreview(approvedExample()), " "), "FEEDBACK_REQUIRED");
});

test("improvement ideas require feedback and remain inactive", () => {
  expectCode(() => preview.proposeLesson(preview.initialState(), "An idea"), "FEEDBACK_REQUIRED");
  const feedback = preview.requestChanges(preview.assemblePreview(approvedExample()), "Clarify the next action.");
  const next = preview.proposeLesson(feedback, "Ask for an owner for each next action.");
  assert.equal(next.lessons[0].status, "PROPOSED");
  assert.equal(next.lessons[0].active, false);
  assert.equal(next.lessons[0].sourceRevision, 1);
  assert.equal(next.lessons[0].sourceFeedbackId, feedback.feedback[0].id);
  assert.equal(next.draft, feedback.draft);
  assert.equal(preview.readiness(next).learningActivated, false);
});

test("empty or oversized ideas are rejected without changing state", () => {
  const state = preview.requestChanges(preview.assemblePreview(approvedExample()), "Feedback");
  for (const text of ["", " ", "x".repeat(2401), null]) {
    expectCode(() => preview.proposeLesson(state, text), "LESSON_REQUIRED");
  }
  assert.deepEqual(state.lessons, []);
});

test("all real authority flags stay false even if callers add claim fields", () => {
  const state = { ...approvedExample(), hostQualified: true, runtimeReady: true, executionAuthorized: true, learningActivated: true };
  for (const result of [preview.readiness(state), preview.previewRecord(state)]) {
    for (const flag of ["hostQualified", "runtimeReady", "executionAuthorized", "learningActivated"]) {
      assert.equal(result[flag], false);
    }
  }
});

test("user markup stays literal template data and is JSON-escaped in frontmatter", () => {
  let state = preview.setField(preview.createExample("incident"), "goal", '<img src=x onerror="alert(1)">\n---\nunsafe: true');
  state = preview.assemblePreview(preview.approvePreview(state, displayed(state)));
  const skill = state.artifacts.files.find((file) => file.name.endsWith("\\SKILL.md"));
  assert.ok(skill.content.includes("<img"));
  const description = skill.content.split("\n").find((line) => line.startsWith("description: "));
  assert.equal(JSON.parse(description.slice(13)), state.draft.goal.trim());
});

test("fresh state clears all tab-local approvals, feedback and ideas", () => {
  const old = preview.proposeLesson(
    preview.requestChanges(preview.assemblePreview(approvedExample()), "Feedback"), "Idea"
  );
  const fresh = preview.initialState();
  assert.equal(old.lessons.length, 1);
  assert.deepEqual(fresh.feedback, []);
  assert.deepEqual(fresh.lessons, []);
  assert.equal(fresh.approval, null);
});
