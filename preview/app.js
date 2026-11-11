(function () {
  "use strict";

  const P = window.SparkForgePreview;
  const element = (id) => {
    const found = document.getElementById(id);
    if (!found) throw new Error(`Preview element missing: ${id}`);
    return found;
  };
  const headings = [
    ["What would you like to make easier?", "Start with an idea, a playbook, or an improvement. We will turn the intent into a reviewable preview brief."],
    ["Check fit before creating more.", "Compare fictional patterns, choose a route, and make the boundaries explicit. Real source coverage remains unassessed."],
    ["Make sure the brief says what you mean.", "Your approval belongs to this exact preview revision. It does not authorize a real factory run."],
    ["Inspect a draft. Make the next one better.", "These are local text templates, not built or tested components. Use feedback to explore the revision loop."],
  ];
  const routeNames = { reuse: "Reuse a sample", adapt: "Adapt a sample", new: "Explore a new draft" };
  let state = P.initialState();
  let step = 0;
  let displayed = null;
  let selectedFile = 0;
  let errors = {};
  let pendingReset = null;

  window.addEventListener("error", () => {
    const fault = element("fault");
    fault.textContent = "The local preview encountered an unexpected error. No model or runtime work was started. Refresh to reset this tab and report what happened.";
    fault.hidden = false;
  });

  function textNode(tag, text, className) {
    const node = document.createElement(tag);
    node.textContent = text;
    if (className) node.className = className;
    return node;
  }

  function notify(message, failed = false) {
    const notice = element("notice");
    notice.textContent = message;
    notice.className = failed ? "notice error" : "notice";
    notice.hidden = !message;
  }

  function showErrors(nextErrors) {
    errors = nextErrors;
    for (const node of document.querySelectorAll("[data-error]")) {
      const message = errors[node.dataset.error];
      node.textContent = message || "";
      node.hidden = !message;
    }
    for (const node of document.querySelectorAll("[data-field]")) {
      if (errors[node.dataset.field]) node.setAttribute("aria-invalid", "true");
      else node.removeAttribute("aria-invalid");
    }
  }

  function syncFields() {
    for (const node of document.querySelectorAll("[data-field]")) {
      if (node.type === "radio") node.checked = node.value === state.draft[node.dataset.field];
      else node.value = state.draft[node.dataset.field];
    }
  }

  function permittedStep(target) {
    if (target === 0) return true;
    if (target === 3 && state.feedback.length) return true;
    if (Object.keys(P.validateDraft(state.draft, "intake")).length) return false;
    if (target === 1) return true;
    if (Object.keys(P.validateDraft(state.draft)).length) return false;
    if (target === 2) return true;
    return Boolean(state.artifacts || state.feedback.length);
  }

  function goTo(target, focus = true) {
    if (!permittedStep(target)) {
      const nextErrors = P.validateDraft(state.draft, target === 1 ? "intake" : "all");
      showErrors(nextErrors);
      if (Object.keys(nextErrors).length) {
        notify("Complete the highlighted fields before continuing.", true);
        focusFirstError();
      } else {
        notify("Approve the preview brief and create its document previews first.", true);
      }
      return;
    }
    step = target;
    showErrors({});
    notify("");
    refresh();
    if (focus) element("page-title").focus();
  }

  function focusFirstError() {
    const order = ["title", "goal", "audience", "inputs", "decision", "targetId", "rationale", "nonGoals", "criteria"];
    const field = order.find((name) => errors[name]);
    if (!field) return;
    step = ["title", "goal", "audience", "inputs"].includes(field) ? 0 : 1;
    refresh();
    const input = document.querySelector(`[data-field="${field}"]`);
    if (input) input.focus();
  }

  function action(operation, after) {
    try {
      state = operation();
      showErrors({});
      refresh();
      if (after) after();
    } catch (error) {
      if (!(error instanceof P.PreviewError)) throw error;
      showErrors(error.fields);
      notify(error.message, true);
      focusFirstError();
    }
  }

  function renderSummary() {
    const report = P.readiness(state);
    const badge = element("summary-status");
    badge.textContent = report.previewAvailable ? "Preview ready"
      : report.previewApproved ? "Preview approved"
        : state.reviewStatus === "REJECTED" ? "Not approved" : "Draft";
    badge.className = "status-pill" + (report.previewApproved ? " good" : state.reviewStatus === "REJECTED" ? " pending" : "");
    element("summary-title").textContent = state.draft.title.trim() || "Your idea starts here.";
    element("summary-audience").textContent = state.draft.audience.trim() || "Describe who you are helping.";
    element("summary-revision").textContent = String(state.revision).padStart(2, "0");
    element("summary-route").textContent = routeNames[state.draft.decision] || "Not chosen";
    element("revision-badge").textContent = "DRAFT " + String(state.revision).padStart(2, "0");
    element("main").dataset.previewApproved = String(report.previewApproved);
    element("main").dataset.revision = String(state.revision);
    element("main").dataset.executionAuthorized = "false";
    element("check-count").textContent = `${report.checks.filter((item) => item.passed).length} / ${report.checks.length}`;
    const list = element("check-list");
    list.replaceChildren();
    for (const check of report.checks) {
      const item = document.createElement("li");
      if (check.passed) item.className = "passed";
      const indicator = document.createElement("span");
      indicator.className = "check-indicator";
      indicator.setAttribute("aria-hidden", "true");
      item.append(indicator, textNode("span", check.label));
      item.setAttribute("aria-label", `${check.label}: ${check.passed ? "recorded" : "pending"}`);
      list.append(item);
    }
    const history = element("history-list");
    history.replaceChildren();
    for (const entry of [...state.history].reverse()) {
      const item = document.createElement("li");
      item.append(textNode("strong", `Revision ${entry.revision}`), textNode("span", entry.message));
      history.append(item);
    }
    element("history-count").textContent = String(state.history.length);
    element("history-empty").hidden = state.history.length > 0;
  }

  function renderSamples() {
    const assessment = P.assessSamples(state.draft);
    const matches = element("sample-matches");
    matches.replaceChildren();
    for (const item of assessment.matches) {
      const card = document.createElement("article");
      card.className = "sample-card";
      card.append(textNode("span", "FICTIONAL SAMPLE", "sample-label"), textNode("h3", item.name), textNode("p", item.summary));
      const tags = document.createElement("div");
      tags.className = "match-tags";
      tags.setAttribute("aria-label", "Matching words, not an AI score");
      for (const word of item.matchedWords) tags.append(textNode("span", word));
      card.append(tags);
      matches.append(card);
    }
    element("no-matches").hidden = assessment.matches.length > 0;
    element("target-field").hidden = state.draft.decision === "new";
  }

  function briefBlock(title, content, ordered = false) {
    const block = document.createElement("section");
    block.className = "brief-block";
    block.append(textNode("h3", title));
    if (Array.isArray(content)) {
      const list = document.createElement(ordered ? "ol" : "ul");
      for (const item of content) list.append(textNode("li", item));
      block.append(list);
    } else {
      block.append(textNode("p", content));
    }
    return block;
  }

  function renderBrief() {
    const d = state.draft;
    const target = P.sample(d.targetId);
    const content = element("brief-content");
    content.replaceChildren(
      briefBlock("Preview name", d.title),
      briefBlock("Desired outcome", d.goal),
      briefBlock("Audience", d.audience),
      briefBlock("Input notes", d.inputs.trim() || "No notes supplied. Clarify permitted inputs before real execution."),
      briefBlock("Preview route", `${routeNames[d.decision] || "Not chosen"}${target ? " - " + target.name + " (fictional)" : ""}\n${d.rationale}`),
      briefBlock("Out of scope", P.lines(d.nonGoals)),
      briefBlock("Acceptance checklist - not executed", P.lines(d.criteria), true),
      briefBlock("Evidence boundary", "Only fictional samples were compared. Real SPARK/wiki coverage remains NOT_ASSESSED. No model, host, implementation or component tests are connected."),
    );
    const approved = P.approvalCurrent(state);
    element("review-status").textContent = approved ? "Preview approved" : "Not approved";
    element("review-status").className = "status-pill" + (approved ? " good" : " pending");
    element("approve-button").disabled = approved;
    element("assemble-button").disabled = !approved;
    element("decline-button").textContent = approved ? "Withdraw preview approval" : "Keep unapproved";
    if (step === 2) displayed = { revision: state.revision, snapshotKey: P.snapshotKey(state) };
  }

  function renderArtifact() {
    const current = P.readiness(state).previewAvailable;
    element("artifact-card").hidden = !current;
    element("stale-artifacts").hidden = current;
    const tabs = element("artifact-tabs");
    tabs.replaceChildren();
    if (!current) {
      element("artifact-name").textContent = "";
      element("artifact-text").value = "";
      return;
    }
    const files = state.artifacts.files;
    selectedFile = Math.min(selectedFile, files.length - 1);
    element("artifact-description").textContent = `${files.length} document previews for revision ${state.revision}. Generated locally from templates; no files written.`;
    files.forEach((file, index) => {
      const button = textNode("button", file.name, "artifact-tab");
      button.type = "button";
      button.id = `artifact-tab-${index}`;
      button.tabIndex = index === selectedFile ? 0 : -1;
      button.setAttribute("role", "tab");
      button.setAttribute("aria-selected", String(index === selectedFile));
      button.setAttribute("aria-controls", "artifact-panel");
      button.addEventListener("click", () => {
        selectedFile = index;
        renderArtifact();
        const selected = element("artifact-tabs").children[index];
        if (selected) selected.focus();
      });
      button.addEventListener("keydown", (event) => {
        const offsets = { ArrowRight: 1, ArrowLeft: -1 };
        if (Object.hasOwn(offsets, event.key)) {
          selectedFile = (selectedFile + offsets[event.key] + files.length) % files.length;
        } else if (event.key === "Home") selectedFile = 0;
        else if (event.key === "End") selectedFile = files.length - 1;
        else return;
        event.preventDefault();
        renderArtifact();
        element(`artifact-tab-${selectedFile}`).focus();
      });
      tabs.append(button);
    });
    element("artifact-panel").setAttribute("aria-labelledby", `artifact-tab-${selectedFile}`);
    element("artifact-name").textContent = files[selectedFile].name;
    element("artifact-text").value = files[selectedFile].content;
  }

  function renderFeedback() {
    const available = P.readiness(state).previewAvailable;
    element("feedback-button").disabled = !available;
    element("feedback-text").disabled = !available;
    element("feedback-help").textContent = available
      ? "Submitting feedback withdraws this preview approval and opens another draft revision."
      : "Create a current document preview to attach more feedback. Earlier feedback is retained below.";
    element("feedback-history-card").hidden = state.feedback.length === 0;
    const feedback = element("feedback-list");
    feedback.replaceChildren();
    for (const item of [...state.feedback].reverse()) {
      const entry = document.createElement("li");
      entry.append(textNode("strong", `Feedback on revision ${item.revision} - ${item.id}`), textNode("p", item.text));
      feedback.append(entry);
    }
    element("lesson-button").disabled = state.feedback.length === 0;
    const lessons = element("lesson-list");
    lessons.replaceChildren();
    for (const item of [...state.lessons].reverse()) {
      const entry = document.createElement("li");
      entry.append(textNode("strong", `Proposed, not active - from ${item.sourceFeedbackId}, revision ${item.sourceRevision}`), textNode("p", item.text));
      lessons.append(entry);
    }
  }

  function refresh() {
    for (let index = 0; index < headings.length; index += 1) {
      element(`stage-${index}`).hidden = index !== step;
    }
    for (const button of document.querySelectorAll("[data-step]")) {
      const target = Number(button.dataset.step);
      button.disabled = !permittedStep(target);
      button.classList.toggle("active", target === step);
      if (target === step) button.setAttribute("aria-current", "step");
      else button.removeAttribute("aria-current");
    }
    element("step-label").textContent = `STEP ${step + 1} OF 4`;
    element("page-title").textContent = headings[step][0];
    element("page-description").textContent = headings[step][1];
    renderSummary();
    renderSamples();
    renderBrief();
    renderArtifact();
    renderFeedback();
  }

  function replacePreview(exampleId) {
    state = exampleId ? P.createExample(exampleId) : P.initialState();
    step = 0;
    selectedFile = 0;
    displayed = null;
    showErrors({});
    syncFields();
    element("feedback-text").value = "";
    element("lesson-text").value = "";
    refresh();
    notify(exampleId ? "Loaded a fictional example. Change anything, then review the route and scope." : "Started a fresh tab-local preview. Nothing was saved elsewhere.");
    element(exampleId ? "field-title" : "page-title").focus();
  }

  function requestReset(exampleId = null) {
    if (!P.FIELDS.some((field) => state.draft[field]) && !state.feedback.length && !state.lessons.length) {
      replacePreview(exampleId);
      return;
    }
    pendingReset = { exampleId };
    element("reset-dialog").showModal();
  }

  for (const item of P.CATALOG) {
    const option = textNode("option", item.name + " (fictional)");
    option.value = item.id;
    element("field-targetId").append(option);
  }
  for (const node of document.querySelectorAll("[data-field]")) {
    node.addEventListener(node.type === "radio" || node.tagName === "SELECT" ? "change" : "input", () => {
      if (node.type === "radio" && !node.checked) return;
      const hadApproval = Boolean(state.approval || state.artifacts);
      action(() => P.setField(state, node.dataset.field, node.value), () => {
        if (node.dataset.field === "decision") element("field-targetId").value = state.draft.targetId;
        if (hadApproval && !state.approval) {
          notify(`The edit opened draft revision ${state.revision}. Previous approval and document previews are no longer current.`);
        }
      });
    });
  }
  for (const button of document.querySelectorAll("[data-step], [data-go]")) {
    button.addEventListener("click", () => goTo(Number(button.dataset.step ?? button.dataset.go)));
  }
  for (const button of document.querySelectorAll("[data-example]")) {
    button.addEventListener("click", () => requestReset(button.dataset.example));
  }
  element("intake-form").addEventListener("submit", (event) => { event.preventDefault(); goTo(1); });
  element("scope-form").addEventListener("submit", (event) => { event.preventDefault(); goTo(2); });
  element("approve-button").addEventListener("click", () => {
    action(() => P.approvePreview(state, displayed), () => {
      notify(`Preview revision ${state.revision} approved. You can now assemble its local document previews. No runtime execution was authorized.`);
      element("assemble-button").focus();
    });
  });
  element("decline-button").addEventListener("click", () => {
    action(() => P.declinePreview(state), () => notify("This preview is unapproved. Edit it or review it again; no real work was started."));
  });
  element("assemble-button").addEventListener("click", () => {
    action(() => P.assemblePreview(state), () => {
      selectedFile = 0;
      goTo(3);
      notify("Document previews assembled locally. No AI call, file write, installation or component test was performed.");
    });
  });
  element("feedback-form").addEventListener("submit", (event) => {
    event.preventDefault();
    const revision = state.revision;
    action(() => P.requestChanges(state, element("feedback-text").value), () => {
      element("feedback-text").value = "";
      notify(`Feedback is linked to revision ${revision}. Draft ${state.revision} needs your edits and a fresh preview approval.`);
      element("lesson-text").focus();
    });
  });
  element("lesson-form").addEventListener("submit", (event) => {
    event.preventDefault();
    action(() => P.proposeLesson(state, element("lesson-text").value), () => {
      element("lesson-text").value = "";
      notify("Improvement idea captured as an inactive proposal. Nothing was learned, evaluated or promoted automatically.");
    });
  });
  element("select-text").addEventListener("click", () => {
    element("artifact-text").focus();
    element("artifact-text").select();
    notify("Text selected. Copy it manually if you want to discuss this preview. This page does not access your clipboard.");
  });
  element("about-button").addEventListener("click", () => element("about-dialog").showModal());
  element("close-about").addEventListener("click", () => element("about-dialog").close());
  element("reset-button").addEventListener("click", () => requestReset());
  element("reset-compact").addEventListener("click", () => requestReset());
  element("cancel-reset").addEventListener("click", () => { pendingReset = null; element("reset-dialog").close(); });
  element("confirm-reset").addEventListener("click", () => {
    const exampleId = pendingReset ? pendingReset.exampleId : null;
    pendingReset = null;
    element("reset-dialog").close();
    replacePreview(exampleId);
  });
  element("reset-dialog").addEventListener("cancel", () => { pendingReset = null; });
  syncFields();
  refresh();
  element("boot-status").hidden = true;
})();
