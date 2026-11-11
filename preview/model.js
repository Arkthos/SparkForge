(function (root, factory) {
  "use strict";
  const api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  else root.SparkForgePreview = api;
})(globalThis, function () {
  "use strict";

  const SCOPE = "local_user_preview";
  const CATALOG_VERSION = "fictional-catalog-v1";
  const FIELDS = Object.freeze([
    "title", "goal", "audience", "inputs", "nonGoals", "criteria",
    "decision", "targetId", "rationale",
  ]);
  const LIMITS = Object.freeze({
    title: 100, goal: 2400, audience: 200, inputs: 3600,
    nonGoals: 2400, criteria: 2400, rationale: 1600,
  });
  const CATALOG = Object.freeze([
    Object.freeze({
      id: "sample-incident-summary",
      name: "Incident Summary",
      summary: "Organizes incident notes into a short handoff with a timeline and open questions.",
      keywords: Object.freeze(["incident", "handoff", "timeline", "triage", "playbook"]),
    }),
    Object.freeze({
      id: "sample-weekly-brief",
      name: "Weekly Brief",
      summary: "Turns a team's weekly notes into a concise status update and a list of blockers.",
      keywords: Object.freeze(["weekly", "brief", "status", "blocker", "stakeholder"]),
    }),
    Object.freeze({
      id: "sample-knowledge-note",
      name: "Knowledge Note",
      summary: "Reshapes supplied reference notes into a readable guide without adding unsupported facts.",
      keywords: Object.freeze(["knowledge", "guide", "reference", "onboarding", "notes"]),
    }),
  ]);
  const EXAMPLES = Object.freeze({
    incident: Object.freeze({
      title: "Incident handoff",
      goal: "Turn a short incident playbook into a consistent analyst handoff with a timeline and clear next actions.",
      audience: "The analyst taking over an incident",
      inputs: "Non-sensitive example notes, the known timeline, and a list of open questions.",
      nonGoals: "No live telemetry queries\nNo changes to production systems\nDo not invent missing facts",
      criteria: "The handoff separates facts from open questions.\nMissing inputs are called out instead of invented.\nEach next action has an owner placeholder.",
      decision: "adapt",
      targetId: "sample-incident-summary",
      rationale: "Use the fictional summary pattern as a starting point and add a clearer next-action section.",
    }),
    weekly: Object.freeze({
      title: "Weekly decision brief",
      goal: "Improve a weekly status summary so that decisions, blockers, and next steps are easier to scan.",
      audience: "A project owner reviewing weekly progress",
      inputs: "A small set of fictional progress notes and explicitly supplied decisions.",
      nonGoals: "No automatic publishing\nNo access to project trackers\nDo not infer decisions that were not supplied",
      criteria: "Decisions appear before general progress.\nEvery blocker has a clearly stated next action.\nUncertain information is labeled as an open question.",
      decision: "adapt",
      targetId: "sample-weekly-brief",
      rationale: "Adapt the fictional weekly brief instead of duplicating its general summary structure.",
    }),
  });

  class PreviewError extends Error {
    constructor(code, message, fields = {}) {
      super(message);
      this.name = "PreviewError";
      this.code = code;
      this.fields = fields;
    }
  }

  function initialState() {
    return {
      scope: SCOPE,
      revision: 1,
      reviewStatus: "DRAFT",
      draft: Object.fromEntries(FIELDS.map((field) => [field, ""])),
      approval: null,
      artifacts: null,
      feedback: [],
      lessons: [],
      history: [],
    };
  }

  function createExample(id) {
    if (!Object.hasOwn(EXAMPLES, id)) {
      throw new PreviewError("UNKNOWN_EXAMPLE", "Choose one of the provided examples.");
    }
    const state = initialState();
    state.draft = { ...EXAMPLES[id] };
    state.history = [{ kind: "example", revision: 1, message: "Loaded a fictional example. Nothing is approved." }];
    return state;
  }

  function slug(title) {
    if (typeof title !== "string") return "";
    return title.normalize("NFKD").replace(/[\u0300-\u036f]/g, "")
      .toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
  }

  function lines(value) {
    return typeof value === "string"
      ? value.split(/\r?\n/).map((line) => line.trim().replace(/^[-*]\s+/, "")).filter(Boolean)
      : [];
  }

  function sample(id) {
    return CATALOG.find((item) => item.id === id) || null;
  }

  function assessSamples(draft) {
    const text = [draft.title, draft.goal, draft.inputs]
      .filter((value) => typeof value === "string").join(" ").toLowerCase();
    const words = new Set(text.match(/[a-z0-9]+/g) || []);
    return {
      catalogVersion: CATALOG_VERSION,
      source: "Fictional sample catalog",
      realCoverage: "NOT_ASSESSED",
      matches: CATALOG.map((item) => ({
        ...item,
        matchedWords: item.keywords.filter((word) => words.has(word)),
      })).filter((item) => item.matchedWords.length > 0)
        .sort((left, right) => right.matchedWords.length - left.matchedWords.length),
    };
  }

  function validateDraft(draft, stage = "all") {
    if (!["intake", "scope", "all"].includes(stage)) {
      throw new PreviewError("UNKNOWN_STAGE", "Unknown preview validation stage.");
    }
    const errors = {};
    const required = stage === "intake"
      ? ["title", "goal", "audience"]
      : stage === "scope" ? ["nonGoals", "criteria", "decision", "rationale"]
        : ["title", "goal", "audience", "nonGoals", "criteria", "decision", "rationale"];
    for (const field of required) {
      if (typeof draft[field] !== "string" || !draft[field].trim()) {
        const prompts = {
          title: "Give this idea a short name.",
          goal: "Describe the outcome you want.",
          audience: "Tell us who will use the result.",
          nonGoals: "State what this draft must not do.",
          criteria: "Add at least one observable acceptance condition.",
          decision: "Choose reuse, adapt, or a new draft.",
          rationale: "Explain your choice, even for this fictional catalog.",
        };
        errors[field] = prompts[field];
      }
    }
    for (const [field, limit] of Object.entries(LIMITS)) {
      if (stage === "intake" && !["title", "goal", "audience", "inputs"].includes(field)) continue;
      if (stage === "scope" && !["nonGoals", "criteria", "rationale"].includes(field)) continue;
      if (typeof draft[field] !== "string") errors[field] = "Enter text for this field.";
      else if (draft[field].length > limit) errors[field] = `Keep this preview field within ${limit} characters.`;
    }
    if (stage !== "scope" && typeof draft.title === "string" && draft.title.trim()) {
      const name = slug(draft.title);
      if (!name || name.length > 64) {
        errors.title = "Use a short name that produces 1-64 letters, numbers or hyphens.";
      }
    }
    if (stage !== "intake") {
      if (!["reuse", "adapt", "new"].includes(draft.decision)) {
        errors.decision = "Choose reuse, adapt, or a new draft.";
      }
      if (["reuse", "adapt"].includes(draft.decision) && !sample(draft.targetId)) {
        errors.targetId = "Choose a fictional sample to reuse or adapt.";
      }
      if (draft.decision === "new" && draft.targetId !== "") {
        errors.targetId = "A new draft must not retain an unrelated sample target.";
      }
      if (!lines(draft.criteria).length) errors.criteria = "Add at least one observable acceptance condition.";
      if (!lines(draft.nonGoals).length) errors.nonGoals = "State what this draft must not do.";
    }
    return errors;
  }

  function snapshot(state) {
    return {
      scope: SCOPE,
      revision: state.revision,
      catalogVersion: CATALOG_VERSION,
      realCoverage: "NOT_ASSESSED",
      draft: Object.fromEntries(FIELDS.map((field) => [field, state.draft[field]])),
    };
  }

  function snapshotKey(state) {
    return JSON.stringify(snapshot(state));
  }

  function approvalCurrent(state) {
    return Boolean(state.approval
      && state.approval.scope === "preview_only"
      && state.approval.revision === state.revision
      && state.approval.snapshotKey === snapshotKey(state));
  }

  function event(state, kind, message) {
    return [...state.history, { kind, revision: state.revision, message }];
  }

  function invalidate(state, message) {
    if (!state.approval && !state.artifacts) return state;
    return {
      ...state,
      revision: state.revision + 1,
      approval: null,
      artifacts: null,
      reviewStatus: "DRAFT",
      history: event(state, "invalidated", message),
    };
  }

  function setField(state, field, value) {
    if (!FIELDS.includes(field)) throw new PreviewError("UNKNOWN_FIELD", "This field is not part of the preview brief.");
    if (typeof value !== "string") throw new PreviewError("INVALID_FIELD_TYPE", "Preview fields must contain text.");
    if (state.draft[field] === value) return state;
    const next = invalidate(state, "The brief changed. Its approval and document previews are no longer current.");
    const draft = { ...next.draft, [field]: value };
    if (field === "decision" && value === "new") draft.targetId = "";
    return { ...next, draft, reviewStatus: "DRAFT" };
  }

  function assertReady(state) {
    const fields = validateDraft(state.draft);
    if (Object.keys(fields).length) {
      throw new PreviewError("BRIEF_INCOMPLETE", "Complete the highlighted fields before approving this preview.", fields);
    }
  }

  function approvePreview(state, displayed) {
    assertReady(state);
    if (!displayed || displayed.revision !== state.revision || displayed.snapshotKey !== snapshotKey(state)) {
      throw new PreviewError("STALE_REVIEW", "The brief changed after this review was displayed. Review the current version first.");
    }
    if (approvalCurrent(state)) return state;
    return {
      ...state,
      reviewStatus: "APPROVED",
      approval: { scope: "preview_only", revision: state.revision, snapshotKey: snapshotKey(state) },
      history: event(state, "approved", "Approved this exact preview brief. No runtime execution was authorized."),
    };
  }

  function declinePreview(state) {
    const next = invalidate(state, "Preview approval was withdrawn. Previous document previews are no longer current.");
    return {
      ...next,
      reviewStatus: "REJECTED",
      history: [...next.history, {
        kind: "rejected", revision: next.revision,
        message: "Kept this preview unapproved. No runtime work was started.",
      }],
    };
  }

  function readiness(state) {
    const errors = validateDraft(state.draft);
    return {
      scope: SCOPE,
      previewApproved: approvalCurrent(state),
      previewAvailable: Boolean(state.artifacts && approvalCurrent(state) && state.artifacts.revision === state.revision),
      fieldErrors: errors,
      checks: [
        { id: "intent", label: "Intent and audience recorded", passed: !["title", "goal", "audience", "inputs"].some((field) => errors[field]) },
        { id: "scope", label: "Non-goals and acceptance recorded", passed: !errors.nonGoals && !errors.criteria },
        { id: "reuse", label: "Sample-catalog choice explained", passed: !errors.decision && !errors.targetId && !errors.rationale },
        { id: "approval", label: "Current preview revision approved", passed: approvalCurrent(state) },
      ],
      realCoverage: "NOT_ASSESSED",
      hostQualified: false,
      executionAuthorized: false,
      runtimeReady: false,
      learningActivated: false,
    };
  }

  function previewRecord(state) {
    return {
      ...snapshot(state),
      previewApproved: approvalCurrent(state),
      hostQualified: false,
      executionAuthorized: false,
      runtimeReady: false,
      learningActivated: false,
      evidenceClass: "LOCAL_PREVIEW_ONLY",
      generation: "Deterministic text template; no model execution or component test run.",
    };
  }

  function assemblePreview(state) {
    assertReady(state);
    if (!approvalCurrent(state)) {
      throw new PreviewError("APPROVAL_REQUIRED", "Approve the current preview brief before assembling documents.");
    }
    if (state.artifacts && state.artifacts.revision === state.revision) return state;
    const d = state.draft;
    const target = sample(d.targetId);
    const warning = "> Local preview only. This is a deterministic template, not an installed or host-qualified component.";
    const criteria = lines(d.criteria).map((line) => `- [ ] ${line}`).join("\n");
    const nonGoals = lines(d.nonGoals).map((line) => `- ${line}`).join("\n");
    const files = [];
    if (d.decision === "reuse") {
      files.push({
        name: "REUSE_PLAN.md",
        content: `# Reuse preview: ${d.title}\n\n${warning}\n\n## Fictional starting point\n${target.name}\n\n## Desired outcome\n${d.goal}\n\n## Why reuse\n${d.rationale}\n\nNo new skill is generated for this reuse choice. Verify real source coverage, ownership and behavior before any actual reuse.\n`,
      });
    } else {
      if (d.decision === "adapt") {
        files.push({
          name: "CHANGE_PLAN.md",
          content: `# Adaptation preview: ${d.title}\n\n${warning}\n\n## Fictional baseline\n${target.name}: ${target.summary}\n\n## Proposed change\n${d.goal}\n\n## Reason for adapting\n${d.rationale}\n\n## Preserve or clarify before real work\n- Inspect the actual component and its source revision.\n- Identify existing behavior that must remain unchanged.\n- Obtain real comparison, acceptance and execution evidence.\n\nNo existing component has been read or modified by this preview.\n`,
        });
      }
      files.push({
        name: `skills\\${slug(d.title)}\\SKILL.md`,
        content: `---\nname: ${slug(d.title)}\ndescription: ${JSON.stringify(d.goal.trim())}\n---\n\n# ${d.title}\n\n${warning}\n\n## Intended audience\n${d.audience}\n\n## Intended outcome\n${d.goal}\n\n## Supplied input notes\n${d.inputs.trim() || "No input notes supplied. Clarify permitted inputs before real execution."}\n\n## Proposed working instructions\n1. Confirm the permitted inputs and accepted scope.\n2. Use only supplied facts; label gaps and uncertainty.\n3. Produce a result aligned with the outcome above.\n4. Check the acceptance conditions without inventing evidence.\n5. Do not invoke external tools or publish anything from this template.\n\n## Acceptance checklist - not executed\n${criteria}\n\n## Out of scope\n${nonGoals}\n\n## Reuse rationale\n${d.rationale}\n\nReal SPARK/wiki coverage remains NOT_ASSESSED. Actual host, data, tests and contribution approvals are still required.\n`,
      });
    }
    files.push({
      name: "REVIEW_CHECKLIST.md",
      content: `# Preview review: ${d.title}\n\n${warning}\n\n## Proposed behavior checks - not executed\n${criteria}\n\n## Required before real implementation\n- [ ] Assess authorized actual SPARK/wiki sources.\n- [ ] Bind a real approval to the exact brief and acceptance.\n- [ ] Qualify the selected Corp host, data, tools and resources.\n- [ ] Implement and run meaningful tests and independent review.\n- [ ] Verify package layout and the installed source.\n\nCheckboxes are a draft checklist, not test results.\n`,
    });
    files.push({ name: "PREVIEW_RECORD.json", content: JSON.stringify(previewRecord(state), null, 2) });
    return {
      ...state,
      artifacts: { revision: state.revision, files },
      history: event(state, "assembled", "Assembled document previews in this tab. No files were written or components tested."),
    };
  }

  function requestChanges(state, text) {
    if (typeof text !== "string" || !text.trim() || text.length > 2400) {
      throw new PreviewError("FEEDBACK_REQUIRED", "Describe the change in 1-2400 characters.");
    }
    if (!state.artifacts || !approvalCurrent(state)) {
      throw new PreviewError("PREVIEW_REQUIRED", "Create a current document preview before attaching feedback.");
    }
    const item = {
      id: `feedback-${state.feedback.length + 1}`,
      revision: state.revision,
      text: text.trim(),
      artifactNames: state.artifacts.files.map((file) => file.name),
    };
    const next = invalidate(state, "Feedback requested another revision. Review and approve the updated brief before regenerating.");
    return {
      ...next,
      feedback: [...state.feedback, item],
      history: [...next.history, { kind: "feedback", revision: item.revision, message: "Feedback is linked to the earlier preview; it was not silently applied to the brief." }],
    };
  }

  function proposeLesson(state, text) {
    if (typeof text !== "string" || !text.trim() || text.length > 2400) {
      throw new PreviewError("LESSON_REQUIRED", "Describe the improvement idea in 1-2400 characters.");
    }
    if (!state.feedback.length) {
      throw new PreviewError("FEEDBACK_REQUIRED", "Record feedback first so this idea has an explicit observation.");
    }
    const source = state.feedback[state.feedback.length - 1];
    return {
      ...state,
      lessons: [...state.lessons, {
        id: `idea-${state.lessons.length + 1}`,
        status: "PROPOSED",
        active: false,
        sourceFeedbackId: source.id,
        sourceRevision: source.revision,
        text: text.trim(),
      }],
      history: event(state, "idea", "Captured an inactive improvement idea. No learning, evaluation or promotion was performed."),
    };
  }

  return Object.freeze({
    SCOPE, CATALOG_VERSION, FIELDS, LIMITS, CATALOG, EXAMPLES, PreviewError,
    initialState, createExample, slug, lines, sample, assessSamples, validateDraft,
    snapshot, snapshotKey, approvalCurrent, setField, approvePreview, declinePreview, readiness,
    previewRecord, assemblePreview, requestChanges, proposeLesson,
  });
});
