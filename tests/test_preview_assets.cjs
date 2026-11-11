"use strict";

const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");

const root = path.resolve(__dirname, "..", "preview");
const html = fs.readFileSync(path.join(root, "index.html"), "utf8");
const app = fs.readFileSync(path.join(root, "app.js"), "utf8");
const model = fs.readFileSync(path.join(root, "model.js"), "utf8");
const css = fs.readFileSync(path.join(root, "styles.css"), "utf8");

test("the user preview packages all assets locally without a server dependency", () => {
  const sources = [...html.matchAll(/\b(?:src|href)="([^"]+)"/g)].map((match) => match[1]);
  assert.ok(sources.includes("model.js"));
  assert.ok(sources.includes("app.js"));
  assert.ok(sources.includes("styles.css"));
  for (const source of sources) {
    if (source.startsWith("#") || source.startsWith("data:image/svg+xml,")) continue;
    assert.doesNotMatch(source, /^(?:[a-z]+:|\/\/|\/)/i);
    const resolved = path.resolve(root, source);
    assert.equal(path.dirname(resolved), root);
    assert.equal(fs.existsSync(resolved), true);
  }
});

test("the browser harness stays inside the opened local-file directory mount", () => {
  const harness = fs.readFileSync(path.join(root, "browser-checks.html"), "utf8");
  const checks = fs.readFileSync(path.join(root, "browser-checks.js"), "utf8");
  assert.match(harness, /src="browser-checks\.js"/);
  assert.ok(checks.includes('new URL("index.html", location.href)'));
  const resolved = new URL("index.html", "http://browser-preview-local.localhost/synthetic-mount/browser-checks.html");
  assert.equal(resolved.pathname, "/synthetic-mount/index.html");
  assert.doesNotMatch(checks, /\.\.\/preview/);
});

test("the page forbids connections, form submission, plugins and inline/eval scripts", () => {
  const match = html.match(/http-equiv="Content-Security-Policy" content="([^"]+)"/);
  assert.ok(match);
  for (const directive of [
    "default-src 'none'", "connect-src 'none'", "form-action 'none'",
    "object-src 'none'", "base-uri 'none'", "script-src 'self'", "style-src 'self'",
  ]) {
    assert.ok(match[1].includes(directive), directive);
  }
  assert.doesNotMatch(match[1], /unsafe-inline|unsafe-eval|https?:/);
});

test("the application has no storage, outbound-service or clipboard implementation", () => {
  const code = app + "\n" + model;
  assert.doesNotMatch(code, /\b(?:fetch|XMLHttpRequest|WebSocket|EventSource)\s*\(/);
  assert.doesNotMatch(code, /\b(?:localStorage|sessionStorage|indexedDB)\s*[.(]|\bnavigator\.(?:sendBeacon|clipboard)/);
  assert.doesNotMatch(code, /document\.cookie|serviceWorker|createObjectURL/);
});

test("user text uses text nodes and form values, not HTML or executable injection", () => {
  assert.doesNotMatch(app, /innerHTML|outerHTML|insertAdjacentHTML|document\.write|\beval\s*\(|new Function/);
  assert.match(app, /node\.textContent = text/);
  assert.match(app, /element\("artifact-text"\)\.value = files\[selectedFile\]\.content/);
  assert.doesNotMatch(html, /\son(?:click|input|change|submit|load|error)\s*=/i);
});

test("the review displays the title as well as every substantive brief section", () => {
  for (const expression of [
    'briefBlock("Preview name", d.title)',
    'briefBlock("Desired outcome", d.goal)',
    'briefBlock("Audience", d.audience)',
    'briefBlock("Input notes",',
    'briefBlock("Preview route",',
    'briefBlock("Out of scope", P.lines(d.nonGoals))',
    'briefBlock("Acceptance checklist - not executed", P.lines(d.criteria), true)',
    'briefBlock("Evidence boundary",',
  ]) {
    assert.ok(app.includes(expression), expression);
  }
});

test("the interface has labels, visible error targets and no duplicate HTML IDs", () => {
  const ids = [...html.matchAll(/\bid="([^"]+)"/g)].map((match) => match[1]);
  assert.equal(new Set(ids).size, ids.length);
  for (const field of ["title", "goal", "audience", "inputs", "targetId", "rationale", "nonGoals", "criteria"]) {
    assert.ok(html.includes(`for="field-${field}"`), field);
    assert.ok(ids.includes(`error-${field}`), field);
  }
  assert.match(html, /role="status" aria-live="polite"/);
  assert.match(html, /role="tabpanel"/);
  assert.match(app, /ArrowRight/);
  assert.match(css, /:focus-visible/);
});

test("privacy, preview limits and small-viewport reset are part of the shipped surface", () => {
  assert.match(html, /No AI connected/);
  assert.match(html, /Fictional samples and local text templates/);
  assert.match(html, /No automatic saves/);
  assert.match(html, /id="reset-compact"/);
  assert.match(app, /element\("reset-compact"\)\.addEventListener/);
  assert.match(css, /@media \(max-width: 520px\)/);
});
