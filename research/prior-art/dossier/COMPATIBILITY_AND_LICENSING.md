# Compatibility, data paths, and reuse conditions

**Public baseline:** 2026-11-05. **Edition:** 2026-11-12.
This is a record of adoption questions and selected findings, not a
pre-cleared stack. Private host configuration, operating destinations,
identity assignments, and source-specific deployment routing are withheld.

An open-source license, a familiar brand, a Copilot badge, and a local
executable answer different questions. None alone proves suitability,
permission, actual isolation, or acceptance.

## 1. Name the exact compatibility surface

| Surface | Evidence needed for a real adoption | Why a broad claim is insufficient |
|---|---|---|
| Selected coding executable | Exact binary/wrapper, version, supported entry points, identity, and policy behavior | A public CLI and a customized suite can expose different contracts |
| SDK connection | Actual server/stdio protocol, lifecycle, tool policy, cancellation, discovery | A constructor or connection is not a governed working session; an SDK may bundle its own CLI |
| Skill loading | Supported metadata, paths, references, invocation, complete required resources | One copied `SKILL.md` can omit scripts, sibling knowledge, or host conversion |
| Plugin packaging | Manifest mode/version, component paths, command/agent discovery, MCP configuration | Legacy and Agent Plugins modes differ; an unsupported manifest can reject a package |
| Windows execution | Native shell, paths with spaces, Unicode, subprocess ownership, tested routes | A macOS hook probe or Linux sandbox result is not Windows acceptance |
| Offline/restricted packaging | Reviewed dependency payloads, terms, signatures/hashes, target-platform fit | A wheel for another platform or a manifest without dependencies is not a self-contained package |
| Another deployment target | Its real host, sources, policies, storage, and local acceptance | Evidence does not transfer merely because source files or profile names match |

These are qualification questions, not commands to install or probe a
candidate as part of this publication.

### Concrete examples

[RSC's historical host table](EVIDENCE.md#rsc-host-surfaces) supports some
Copilot output surfaces while explicitly marking session memory unsupported.
One supported feature does not imply support for all others.

[Agent Skills' Copilot guide](EVIDENCE.md#addy-copilot) distinguishes
discovered skills from Claude lifecycle commands that are not registered
there. Manifest precedence and component paths matter. The historically read
[official plugin reference](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-plugin-reference)
describes recognized schemas, managed settings, legacy/Agent Plugins
distinctions, repository configuration, and update behavior. That mutable
page was not refreshed for this edition.

[BMad Loop's profile](EVIDENCE.md#bmad-loop-copilot) records a particular
macOS/CLI hook observation and launches with broad bypass flags. Its
[adapter](EVIDENCE.md#bmad-loop-permissions) rejects unsupported non-bypass
mapping rather than establishing a safe equivalent. Experimental native
Windows transport is a different claim from that hook observation.

[Copilot SDK's local-CLI documentation](EVIDENCE.md#sdk-local-cli) assigns
responsibility for compatibility to callers overriding the bundled runtime.
The historical Node, Python, and .NET paths can include a standard CLI.
Examples that approve all tools are not a recommended policy.
The [pre-tool guide](EVIDENCE.md#sdk-pretool) documents approval/denial
interfaces, but their coverage and real host enforcement still need evidence.

[Waza](QUALITY_AND_EVALUATION.md#3-waza-assess-each-route-separately) has
ordinary execution, text-only, isolated-judge, and preserved-snapshot routes
with materially different constraints. In particular, the exact native-runtime
requirement of the evidence judge and Linux/macOS snapshot-help assertion
must not be generalized to every route or silently ignored.

[Spec Kit's offline guide](EVIDENCE.md#spec-kit-offline) identifies
OS/Python-specific dependencies, PowerShell requirements, and continuing
catalog/archive needs for some components. A bundle directory alone is not
the dependency closure.

The [Agent Skills specification](https://agentskills.io/specification) is
useful for packaging and progressive loading. Its experimental `allowed-tools`
field is host-dependent, not a universal permission-enforcement standard.

## 2. Locality and egress need separate checks

| Resource | Historical observation | Consequence |
|---|---|---|
| Foreman/eve | [Sandbox code](EVIDENCE.md#eve-sandbox) selects hosted Vercel Sandbox even during local development | A local TUI is not a wholly local execution/data boundary |
| Promptfoo | [Data-handling guide](EVIDENCE.md#promptfoo-privacy) separates target, generation, grading, telemetry, sharing, and hosted-only features | Review each selected route; disabling remote generation does not disable all network activity |
| Fabro | README describes cloud sandboxes and automatic model/provider fallback | Local server hosting alone does not qualify execution or approve another provider |
| Deep Agents and OpenHands SDK | Alternative runtimes/providers and optional hosting/tracing surfaces | Integration and data handling are explicit decisions, not silent replacements |
| Rigour | [Profiles](EVIDENCE.md#rigour-profiles) organize configuration/state; model review and team sync have their own destinations | State organization does not authorize every configured request |
| Compound Engineering | [Learning mode](EVIDENCE.md#compound-learning) can discover histories across agent installations | Maintaining one project does not grant access to unrelated transcripts |
| GitHub Agentic Workflows | Compiles workflows into GitHub Actions | An Actions runner is a distinct execution and storage destination, not an assumed local one |

The Foreman README's public Blob configuration is another storage question,
separate from the sandbox. Promptfoo's
[remote-generation selector](EVIDENCE.md#promptfoo-remote) uses disable flags,
configured endpoints, cloud login, and credential availability; one flag does
not make an explicitly configured remote target local.

Permission to use a source in one approved context does not automatically
authorize another connector, telemetry endpoint, sandbox, model, or
publication destination. This is a general data-boundary principle, not a
restatement of any private destination or approval in the original study.

## 3. Authority and filesystem boundaries

The following limits recur across the public examples:

- A worktree separates Git work, not access to the rest of a machine,
  credentials, network, processes, ports, or external services.
- A post-call write check can detect an effect after it happened; it cannot
  prevent that effect or protect every other route.
- Structured model approval is an assessment or recommendation, not a human
  authorization.
- A digest binds content, not the identity or permission of an approver.
- An approval UI protecting one action does not demonstrate that every tool,
  shell command, or alternate path is governed.
- A private repository does not automatically make its runners, artifacts,
  integrations, or model destinations suitable for restricted data.
- A documented retry limit may be advisory, invocation-local, or reset by
  rework; it is not necessarily an enforced lifetime resource cap.

These are qualification cautions, not the result of an exhaustive
vulnerability audit. The historical source reading did not perform one.

## 4. License findings must retain their scope

The [catalog](CATALOG.md) and [public metadata](../sources.json) preserve
each candidate's pin, observed root-license classification, and source
coordinates for the grant. They distinguish actual historical grant review
from GitHub's API label.

| Finding | Required qualification |
|---|---|
| Most selected roots have an MIT grant | Preserve copyright/permission notices where required for substantial source reuse; inspect chosen files and dependencies |
| BMad roots reported API `NOASSERTION` | The captured grants were classified MIT; separate trademark notices do not grant branding rights |
| Pester reported API `NOASSERTION` | Its actual recorded root grant is Apache-2.0 |
| Attractor and the engineering-plugin repository have Apache-2.0 roots | Review notice, license, and modification obligations for actual selected material |
| 12-Factor Agents has separate code/content declarations | Root code is Apache-2.0; its README declares written content CC-BY-SA-4.0 |
| Promptfoo lacks an MIT title in the license | The recorded grant contains the MIT terms; the research classifier was corrected after inspecting that text |
| Archon-based factory wrapper | No root reuse license was established; keep source reference-only until rights are resolved |
| ZazenCodes root/v1 | No standard root/v1 reuse license was established from selected material, despite an invitation to copy in v1 |
| ZazenCodes v2 | Its separate subtree has an actual GPLv3 license; do not apply it to sibling folders or describe GPL as noncommercial-only |

The ZazenCodes author also offers separate commercial licensing. That does
not alter GPL's allowance for commercial use subject to its conditions.
Concrete code adaptation/distribution requires a deliberate scope and
obligations review.

This is not legal advice or a complete license audit. A root grant does not
settle file-level exceptions, vendored content, third-party dependencies,
assets, trademarks, model/service terms, or all relevant rights. The study
did not inventory every repository tree.

Reusing a mechanism in original analysis differs from redistributing code or
adapting an instructional collection. This publication includes the former,
plus citations and metadata; it does not copy upstream code, skill manuals,
full license texts, captions, or media. Public availability alone would not
authorize those copies.

## 5. Record the unit of actual reuse

When a specific adoption is later authorized, a useful record identifies:

| Record | Why it is needed |
|---|---|
| Repository, immutable commit, original paths | Reproducibility and attribution |
| Applicable terms, notices, and exceptions | Reviewable redistribution conditions |
| Copied, adapted, or conceptual-only use | Honest authorship and bounded obligations |
| Local modifications and rationale | Maintenance and future upstream comparison |
| Dependency/runtime/host requirements | Realistic offline or restricted-target adaptation |
| Evidence for the selected operation on the selected host | A concrete alternative to generic compatibility badges |
| Excluded routes, known failures, and remaining unknowns | Keeps unsafe defaults and unassessed behavior visible |

This is adoption guidance, not a selected package format or permission to
begin installation.

## 6. Independent deployment and transfer decisions

A configuration profile is not a second environment's qualification. A
transferable engineering package can preserve permitted code, rationale,
dependency identity, tests, and limitations, but actual transfer rights,
source access, host behavior, and acceptance must be established at the
destination.

The original source-specific rollout sequence and routing facts are withheld,
not generalized into evidence about anonymous environments. No private
distribution or launcher was inspected for this publication. Preserve the
public contracts now; qualify the selected integration only under explicit
authority and with actual target-local results.
