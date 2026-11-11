(function () {
  "use strict";
  const frame = document.getElementById("fixture");
  const output = document.getElementById("results");
  const runButton = document.getElementById("run-checks");
  const source = new URL("index.html", location.href).href;
  const sizes = [
    { name: "wide", width: 1280, height: 900 },
    { name: "panel", width: 490, height: 828 },
    { name: "narrow", width: 390, height: 844 },
  ];
  let running = false;

  function assert(condition, message) {
    if (!condition) throw new Error(message);
  }

  function load(size) {
    frame.width = String(size.width);
    frame.height = String(size.height);
    return new Promise((resolve, reject) => {
      const timeout = setTimeout(() => {
        frame.removeEventListener("load", loaded);
        reject(new Error("The owned preview frame did not load within 10 seconds."));
      }, 10000);
      function loaded() {
        clearTimeout(timeout);
        try {
          const doc = frame.contentDocument;
          assert(doc && doc.getElementById("boot-status")?.hidden, "Preview did not initialize or its frame is not readable.");
          resolve({ doc, win: frame.contentWindow });
        } catch (error) {
          reject(error);
        }
      }
      frame.addEventListener("load", loaded, { once: true });
      frame.src = source;
    });
  }

  async function run() {
    if (running) return window.previewBrowserReport;
    running = true;
    runButton.disabled = true;
    const report = {
      scope: "synthetic_browser_preview_only",
      status: "RUNNING",
      checks: [],
      viewports: [],
      resourceOrigins: [],
      hostQualified: false,
      executionAuthorized: false,
      realUserAcceptance: "NOT_ASSESSED",
    };
    window.previewBrowserReport = report;
    const origins = new Set();
    try {
      for (const size of sizes) {
        output.textContent = `Running ${size.name} viewport...`;
        const { doc, win } = await load(size);
        const byId = (id) => {
          const node = doc.getElementById(id);
          assert(node, `Missing control: ${id}`);
          return node;
        };
        const click = (selector) => {
          const node = doc.querySelector(selector);
          assert(node && !node.disabled, `Unavailable control: ${selector}`);
          node.click();
        };
        const fill = (id, value) => {
          const node = byId(id);
          node.value = value;
          node.dispatchEvent(new win.Event(node.tagName === "SELECT" ? "change" : "input", { bubbles: true }));
        };
        const main = () => byId("main").dataset;
        const review = () => click('[data-step="2"]');
        const approve = () => click("#approve-button");
        const assemble = () => click("#assemble-button");
        const resetButton = () => byId("reset-compact").getBoundingClientRect().width > 0 ? "#reset-compact" : "#reset-button";
        const check = (name, operation) => {
          operation();
          report.checks.push({ name: `${size.name}: ${name}`, outcome: "PASS" });
        };
        report.viewports.push({ requested: size, actual: { width: win.innerWidth, height: win.innerHeight } });

        check("actual viewport and initialized unapproved state", () => {
          assert(win.innerWidth === size.width, "Frame viewport width differs from the requested size.");
          assert(main().previewApproved === "false" && main().executionAuthorized === "false", "Unexpected authority.");
          assert(byId("field-title").value === "", "A fresh frame restored prior user data.");
          assert(doc.documentElement.scrollWidth <= win.innerWidth, "Initial horizontal overflow.");
        });
        check("blank intake blocks progression and focuses the error", () => {
          click('#intake-form button[type="submit"]');
          assert(!byId("stage-0").hidden && !byId("error-title").hidden, "Blank intake advanced.");
          assert(doc.activeElement.id === "field-title", "First missing input did not receive focus.");
        });
        check("example fills the form without approving it", () => {
          click('[data-example="incident"]');
          assert(byId("field-title").value === "Incident handoff", "Example did not populate the form.");
          assert(doc.activeElement.id === "field-title", "Loaded example did not focus the editable form.");
          assert(main().previewApproved === "false", "Loading an example granted approval.");
        });
        const injection = '<img id="synthetic-xss-probe" src="missing-synthetic" onerror="window.__previewXss=1">';
        check("sample fit remains explicitly fictional and unassessed", () => {
          fill("field-goal", byId("field-goal").value + " " + injection);
          click('#intake-form button[type="submit"]');
          assert(!byId("stage-1").hidden, "Valid intake did not advance.");
          assert(doc.querySelector(".coverage-note").textContent.includes("not assessed"), "Coverage caveat missing.");
          assert(byId("sample-matches").textContent.includes("FICTIONAL SAMPLE"), "Sample source not labeled.");
        });
        check("review displays literal user text and the preview name", () => {
          click('#scope-form button[type="submit"]');
          assert(byId("brief-content").textContent.includes("Incident handoff"), "Preview name is absent from the review.");
          assert(byId("brief-content").textContent.includes(injection), "Input was not preserved as literal text.");
          assert(!doc.querySelector("#synthetic-xss-probe") && !win.__previewXss, "User markup became executable DOM.");
          assert(byId("assemble-button").disabled, "Unapproved brief could assemble.");
        });
        check("rejection leaves work unapproved", () => {
          click("#decline-button");
          assert(main().previewApproved === "false" && byId("assemble-button").disabled, "Rejection failed.");
        });
        check("explicit preview approval enables only template assembly", () => {
          approve();
          assert(main().previewApproved === "true" && main().executionAuthorized === "false", "Preview approval elevated real authority.");
          assemble();
          assert(!byId("stage-3").hidden && !byId("artifact-card").hidden, "Preview did not assemble.");
          assert(doc.querySelectorAll(".artifact-tab").length === 4, "Adaptation document set differs.");
        });
        check("keyboard artifact navigation exposes a non-authoritative record", () => {
          click(".artifact-tab");
          doc.activeElement.dispatchEvent(new win.KeyboardEvent("keydown", { key: "End", bubbles: true }));
          assert(doc.activeElement.id === "artifact-tab-3", "Artifact End key did not move focus.");
          assert(byId("artifact-panel").getAttribute("aria-labelledby") === "artifact-tab-3", "Panel label is not bound to the active tab.");
          const record = JSON.parse(byId("artifact-text").value);
          assert(record.previewApproved && !record.hostQualified && !record.executionAuthorized && !record.runtimeReady, "Record grants real authority.");
          assert(record.realCoverage === "NOT_ASSESSED", "Record fabricated real comparison coverage.");
        });
        check("editing an approved brief clears its prior documents", () => {
          click('[data-step="0"]');
          fill("field-goal", "Edited incident handoff outcome with clearer next actions.");
          assert(main().revision === "2" && main().previewApproved === "false", "Edit did not invalidate approval.");
          assert(byId("artifact-text").value === "" && byId("artifact-card").hidden, "Stale documents remain current.");
        });
        check("feedback references the reviewed revision and opens another draft", () => {
          review();
          approve();
          assemble();
          fill("feedback-text", "Put open questions before the timeline.");
          click("#feedback-button");
          assert(main().revision === "3" && main().previewApproved === "false", "Feedback did not open a draft revision.");
          assert(byId("feedback-list").textContent.includes("revision 2"), "Feedback lost its old-revision binding.");
          assert(byId("artifact-card").hidden && byId("artifact-text").value === "", "Feedback retained an active stale preview.");
        });
        check("learning ideas remain inactive and linked to feedback", () => {
          fill("lesson-text", "Ask for an explicit owner for the next action.");
          click("#lesson-button");
          assert(byId("lesson-list").textContent.includes("Proposed, not active"), "Idea was represented as active learning.");
          assert(byId("lesson-list").textContent.includes("feedback-1"), "Idea lacks its observation link.");
          click("#lesson-button");
          assert(byId("lesson-list").children.length === 1 && byId("notice").classList.contains("error"), "Empty idea silently succeeded.");
        });
        check("old feedback stays readable while the new draft is incomplete", () => {
          click('[data-step="0"]');
          fill("field-title", "");
          click('[data-step="3"]');
          assert(!byId("feedback-history-card").hidden && byId("artifact-card").hidden, "Read-only history was gated by new draft completeness.");
        });
        check("reset requires confirmation and cancellation preserves the draft", () => {
          click(resetButton());
          assert(byId("reset-dialog").open, "Reset did not ask for confirmation.");
          click("#cancel-reset");
          assert(main().revision === "3" && byId("feedback-list").children.length === 1, "Cancel reset lost data.");
          click(resetButton());
          click("#confirm-reset");
          assert(main().revision === "1" && byId("feedback-list").children.length === 0 && byId("lesson-list").children.length === 0, "Confirmed reset failed.");
        });
        check("reuse creates a plan instead of quietly creating another skill", () => {
          click('[data-example="weekly"]');
          click('#intake-form button[type="submit"]');
          click('input[name="decision"][value="reuse"]');
          click('#scope-form button[type="submit"]');
          approve();
          assemble();
          const names = [...doc.querySelectorAll(".artifact-tab")].map((node) => node.textContent);
          assert(names.includes("REUSE_PLAN.md") && !names.some((name) => name.endsWith("SKILL.md")), "Reuse generated a new skill.");
          click("#select-text");
          assert(doc.activeElement.id === "artifact-text" && byId("artifact-text").selectionEnd === byId("artifact-text").value.length, "Manual text selection failed.");
        });
        check("new draft clears the sample association and requires renewed approval", () => {
          click('[data-step="1"]');
          click('input[name="decision"][value="new"]');
          assert(byId("target-field").hidden && byId("field-targetId").value === "", "New draft retained a sample association.");
          assert(main().previewApproved === "false", "Route change inherited approval.");
          fill("field-rationale", "Explore a distinct template; real source coverage is still not assessed.");
          review();
          approve();
          assemble();
          const names = [...doc.querySelectorAll(".artifact-tab")].map((node) => node.textContent);
          assert(names.some((name) => name.endsWith("SKILL.md")) && !names.includes("CHANGE_PLAN.md"), "New-draft output route is wrong.");
        });
        check("active flow has no overflow, runtime error or external asset origin", () => {
          assert(doc.documentElement.scrollWidth <= win.innerWidth, "Preview horizontal overflow.");
          assert(byId("artifact-text").scrollWidth <= byId("artifact-text").clientWidth + 2, "Document preview requires horizontal scrolling.");
          assert(byId("fault").hidden, "Preview reported an unexpected runtime error.");
          assert(!win.__previewXss && !doc.querySelector("#synthetic-xss-probe"), "Input escaped text-only rendering.");
          for (const entry of win.performance.getEntriesByType("resource")) {
            const url = new URL(entry.name);
            origins.add(url.origin);
            assert(url.protocol === "file:" || url.protocol === "data:" || url.hostname === "localhost" || url.hostname.endsWith(".localhost") || url.hostname === "127.0.0.1" || url.hostname === "[::1]", "A resource used a non-local origin.");
          }
        });
        const fresh = await load(size);
        check("reload starts clean without restoring tab-local entries", () => {
          assert(fresh.doc.getElementById("field-title").value === "", "Reload restored input.");
          assert(fresh.doc.getElementById("main").dataset.previewApproved === "false", "Reload restored approval.");
          assert(fresh.doc.getElementById("feedback-list").children.length === 0, "Reload restored feedback.");
        });
      }
      report.status = "PASS";
    } catch (error) {
      report.status = "FAIL";
      report.error = { name: error.name, message: error.message };
    } finally {
      report.resourceOrigins = [...origins];
      report.passed = report.checks.length;
      output.textContent = JSON.stringify(report, null, 2);
      runButton.disabled = false;
      running = false;
    }
    return report;
  }

  window.runPreviewBrowserChecks = run;
  runButton.addEventListener("click", () => { window.previewBrowserRun = run(); });
})();
