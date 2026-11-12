# Pinned candidate catalog: detailed public edition

**Public source baseline:** 2026-11-05. **Edition:** 2026-11-12.

All 33 historical candidates are retained with their public identity, pin,
date, license observation, review depth, original analysis, and conditions.
These are references, not installed dependencies, a selected stack, or new
runtime acceptance. Private fit judgments and local source-cache links are
excluded rather than renamed.

Rendered from [public identity metadata](../sources.json) and
[public catalog analysis](catalog-analysis.json). A default-branch snapshot
is not necessarily a released package. Root licensing does not settle every
file, dependency, trademark, asset, or service; no upstream code or full
license text is copied here. Read the [license discussion](COMPATIBILITY_AND_LICENSING.md#4-license-findings-must-retain-their-scope).

| Candidate | Family | Historical review depth | Historical research disposition |
|---|---|---|---|
| [github/spec-kit](#spec-kit) | Specifications and lifecycle | Selected implementation and documentation | Compare first |
| [Fission-AI/OpenSpec](#openspec) | Specifications and lifecycle | Selected implementation and documentation | Compare first |
| [spec-kitty/spec-kitty](#spec-kitty) | Specifications and lifecycle | Selected README | Alternative lifecycle substrate |
| [bmad-code-org/BMAD-METHOD](#bmad-method) | Specifications and lifecycle | README and license | Methodology reference |
| [bmad-code-org/bmad-builder](#bmad-builder) | Skills and component generation | README and license | Generator reference |
| [bmad-code-org/bmad-method-test-architecture-enterprise](#bmad-tea) | Testing and evaluation | README, license, and selected skill contract | Compare first |
| [bmad-code-org/bmad-loop](#bmad-loop) | Factory orchestration | Selected adapter implementation, profile, and documentation | High-value control-loop reference |
| [obra/superpowers](#superpowers) | Skills and engineering practice | Selected README and skill contracts | Compare first |
| [addyosmani/agent-skills](#addy-skills) | Skills and engineering practice | Selected README, intake skill, and Copilot guide | Compare first |
| [ericrisco/rsc-harness](#rsc-harness) | Project knowledge and governance | Selected implementation, test source, and README | Compare first |
| [buildermethods/agent-os](#agent-os) | Project knowledge and governance | README | Focused knowledge reference |
| [disler/super-simple-software-factory](#sssf) | Factory orchestration | Selected implementation and README | High-value control-loop reference |
| [strongdm/attractor](#attractor) | Orchestration specifications | README and selected specification | Design-contract reference |
| [fabro-sh/fabro](#fabro) | Factory orchestration | README | Product comparison |
| [Shopify/roast](#roast) | Factory orchestration | Selected README | Composition reference |
| [langchain-ai/deepagents](#deepagents) | Alternative agent runtimes | README | Architecture comparison |
| [OpenHands/software-agent-sdk](#openhands-sdk) | Alternative agent runtimes | Selected README | Architecture comparison |
| [SWE-agent/mini-swe-agent](#mini-swe-agent) | Alternative agent runtimes | Selected README | Minimality reference |
| [github/copilot-sdk](#copilot-sdk) | Host integration | README and selected official SDK documentation | Conditional integration candidate |
| [github/gh-aw](#gh-aw) | Governed external effects | Selected README | Control-boundary reference |
| [vercel-labs/eve-software-factory-template](#eve-foreman) | Factory orchestration | Selected implementation, instructions, and README | High-value product comparison |
| [coleam00/ai-software-factory](#archon-factory) | Factory orchestration | Selected README and root inventory | Reference only; licensing unresolved |
| [microsoft/waza](#waza) | Testing and evaluation | Selected implementation, test source, and documentation | Compare first, route by route |
| [promptfoo/promptfoo](#promptfoo) | Testing and evaluation | README, selected implementation, and privacy documentation | Conditional complementary evaluator |
| [rigour-labs/rigour](#rigour) | Project knowledge and governance | Selected implementation and documentation | Compare first for feedback governance |
| [EveryInc/compound-engineering-plugin](#compound-engineering) | Project knowledge and governance | Selected workflow guides | Compare first for learning discipline |
| [open-gsd/gsd-core](#gsd-core) | Specifications and lifecycle | README | Context-lifecycle reference |
| [gsd-build/get-shit-done](#gsd-archived) | Historical discovery | README and repository metadata | Historical redirect only |
| [anthropics/knowledge-work-plugins](#engineering-plugin) | Skills and component generation | Selected engineering-package README and manifest capture | Plugin packaging and workflow reference |
| [gitleaks/gitleaks](#gitleaks) | Deterministic quality tools | Selected README | Secret-scanning reference |
| [pester/Pester](#pester) | Deterministic quality tools | Selected README and actual license | Relevant PowerShell test framework |
| [humanlayer/12-factor-agents](#twelve-factor) | Engineering principles | Selected README and factor documents | Conceptual foundation |
| [zazencodes/zazencodes-season-3](#zazen-factory) | Video-linked factory walkthrough | Selected v1 skill and role contracts; separate v2 README and license only | High-value conceptual example; conditional code reuse |

## spec-kit

**Repository:** [github/spec-kit](https://github.com/github/spec-kit/tree/ec9a6f3b94c0aa856f77e550785a1ddde1993de1)

**Pin:** `ec9a6f3b94c0aa856f77e550785a1ddde1993de1`; committed 2026-11-04T22:34:17Z.

**Root license at review:** MIT; **archived at observation:** false.

**Historical depth:** Selected implementation and documentation.

**Research disposition:** Compare first.

A specification/process toolkit with integrations, presets, extensions, workflows, step plugins, persisted runs, bundles, and catalogs. The reviewed source is broader than a static linear prompt collection.

**Reusable contribution:** Artifact-oriented intent and acceptance, explicit workflow state, resumable gates, and a versioned component inventory.

**Conditions and exclusions:**

- A caller-supplied gate verdict is not authenticated human consent. Generic reject-to-skip behavior cannot stand in for a mandatory accepted-brief gate.
- Selected state persistence uses atomic replacement and poisons a failed-save instance; it is not a complete transaction proof across artifacts and external effects.
- Offline bundles have OS/Python and component-specific limits. A manifest need not contain the dependency closure; adapter catalogs/archives and Windows PowerShell requirements remain relevant.

**Public license coordinates:** [MIT (repository_root)](https://github.com/github/spec-kit/blob/ec9a6f3b94c0aa856f77e550785a1ddde1993de1/LICENSE).

[Pinned overview](https://github.com/github/spec-kit/blob/ec9a6f3b94c0aa856f77e550785a1ddde1993de1/README.md) | [Historical inspection](EVIDENCE.md#spec-kit-overview) | [Public metadata](../sources.json)

## openspec

**Repository:** [Fission-AI/OpenSpec](https://github.com/Fission-AI/OpenSpec/tree/3e4d5f0769e2857c8eb54f149cbf5e4f703fa04c)

**Pin:** `3e4d5f0769e2857c8eb54f149cbf5e4f703fa04c`; committed 2026-11-04T17:05:54Z.

**Root license at review:** MIT; **archived at observation:** false.

**Historical depth:** Selected implementation and documentation.

**Research disposition:** Compare first.

A lightweight artifact-first change workflow for existing software. Proposals, specifications, design, tasks, application, and archival make a proposed change distinct from the current specification.

**Reusable contribution:** Brownfield change artifacts, explicit dependencies, relative-path and graph validation, and separate current versus proposed contracts.

**Conditions and exclusions:**

- Valid structure or artifact existence is not semantic completeness or human approval. The selected code checks bounded declarations, Windows/POSIX relative paths, duplicate IDs, references, prerequisites, and cycles.
- Copilot documentation does not demonstrate a customized host's compatibility.
- Shared specification stores are described as beta. Combining complete specification systems without one canonical owner can duplicate state.

**Public license coordinates:** [MIT (repository_root)](https://github.com/Fission-AI/OpenSpec/blob/3e4d5f0769e2857c8eb54f149cbf5e4f703fa04c/LICENSE).

[Pinned overview](https://github.com/Fission-AI/OpenSpec/blob/3e4d5f0769e2857c8eb54f149cbf5e4f703fa04c/README.md) | [Historical inspection](EVIDENCE.md#openspec-overview) | [Public metadata](../sources.json)

## spec-kitty

**Repository:** [spec-kitty/spec-kitty](https://github.com/spec-kitty/spec-kitty/tree/d7f91f37542c68d7ba019a3d22d5f5edec3e96f0)

**Pin:** `d7f91f37542c68d7ba019a3d22d5f5edec3e96f0`; committed 2026-11-04T23:44:07Z.

**Root license at review:** MIT; **archived at observation:** false.

**Historical depth:** Selected README.

**Research disposition:** Alternative lifecycle substrate.

A repository-native development workflow documenting work packages, lifecycle lanes, worktrees, review, acceptance, merge, and retrospective learning.

**Reusable contribution:** Traceable work-package boundaries, visible review state, and separation of agent execution workspaces from the canonical project record.

**Conditions and exclusions:**

- The captured main branch is a 4.x release-candidate line with stable launch acceptance explicitly pending.
- Only selected README material was reviewed; runtime governance was not exercised.
- Its merge/push route needs its own authorization assessment and does not define the selected product's delivery policy.

**Public license coordinates:** [MIT (repository_root)](https://github.com/spec-kitty/spec-kitty/blob/d7f91f37542c68d7ba019a3d22d5f5edec3e96f0/LICENSE).

[Pinned overview](https://github.com/spec-kitty/spec-kitty/blob/d7f91f37542c68d7ba019a3d22d5f5edec3e96f0/README.md) | [Historical inspection](EVIDENCE.md#spec-kitty-overview) | [Public metadata](../sources.json)

## bmad-method

**Repository:** [bmad-code-org/BMAD-METHOD](https://github.com/bmad-code-org/BMAD-METHOD/tree/022be9314e4facd16826104a9f8033e1c5ed4fdc)

**Pin:** `022be9314e4facd16826104a9f8033e1c5ed4fdc`; committed 2026-11-02T17:53:33Z.

**Root license at review:** MIT; **archived at observation:** false.

**Historical depth:** README and license.

**Research disposition:** Methodology reference.

A structured methodology organized around specialist roles, requirements, planning, and delivery artifacts.

**Reusable contribution:** Guided translation of user intent into engineering artifacts and explicit handoffs between responsibilities.

**Conditions and exclusions:**

- The captured main is v7 preview alpha; stable v6 is another branch. Their interfaces and adoption claims must not be mixed.
- A complete installation adds another methodology and dependency surface; individual artifacts may be the more appropriate reuse unit.

**License qualification:** The recorded root MIT grant includes a separate trademark notice; branding rights are not implied.

**Public license coordinates:** [MIT (repository_root)](https://github.com/bmad-code-org/BMAD-METHOD/blob/022be9314e4facd16826104a9f8033e1c5ed4fdc/LICENSE).

[Pinned overview](https://github.com/bmad-code-org/BMAD-METHOD/blob/022be9314e4facd16826104a9f8033e1c5ed4fdc/README.md) | [Historical inspection](EVIDENCE.md#bmad-method-overview) | [Public metadata](../sources.json)

## bmad-builder

**Repository:** [bmad-code-org/bmad-builder](https://github.com/bmad-code-org/bmad-builder/tree/d4a921c49db71ad09c2dc62b8e62266b1f26ca4f)

**Pin:** `d4a921c49db71ad09c2dc62b8e62266b1f26ca4f`; committed 2026-09-25T10:18:09Z.

**Root license at review:** MIT; **archived at observation:** false.

**Historical depth:** README and license.

**Research disposition:** Generator reference.

A BMad-ecosystem toolkit for authoring agents, skills, workflows, and distributable modules.

**Reusable contribution:** Treat generated agent capabilities as packages with structure, validation, dependencies, and documentation rather than isolated prompt text.

**Conditions and exclusions:**

- The module-generation implementation was not deeply traced.
- One ecosystem's marketplace acceptance is not another host's acceptance, and broad Agent Skills format support does not guarantee identical runtime behavior.

**License qualification:** MIT grant plus a separate trademark notice; no branding permission is inferred.

**Public license coordinates:** [MIT (repository_root)](https://github.com/bmad-code-org/bmad-builder/blob/d4a921c49db71ad09c2dc62b8e62266b1f26ca4f/LICENSE).

[Pinned overview](https://github.com/bmad-code-org/bmad-builder/blob/d4a921c49db71ad09c2dc62b8e62266b1f26ca4f/README.md) | [Historical inspection](EVIDENCE.md#bmad-builder-overview) | [Public metadata](../sources.json)

## bmad-tea

**Repository:** [bmad-code-org/bmad-method-test-architecture-enterprise](https://github.com/bmad-code-org/bmad-method-test-architecture-enterprise/tree/a2819f62fc1b56486d223895eaa50578b490f2f5)

**Pin:** `a2819f62fc1b56486d223895eaa50578b490f2f5`; committed 2026-10-31T10:38:31Z.

**Root license at review:** MIT; **archived at observation:** false.

**Historical depth:** README, license, and selected skill contract.

**Research disposition:** Compare first.

Test Engineering Architect combines risk-based planning, automation, test review, nonfunctional evidence, behavioral evaluation, and requirements traceability.

**Reusable contribution:** Requirements-to-evidence matrices, risk-prioritized test generation, distinct test-quality review, and explicit concerns or authorized waivers.

**Conditions and exclusions:**

- The selected trace skill depends on BMad configuration and sibling knowledge/contracts, and names scope-bound outputs.
- Optional synthetic oracles and inferred journeys must not silently replace accepted requirements.
- Stack execution support varies; documented red-mode generation differs from expanding coverage of existing behavior.

**License qualification:** The recorded grant is MIT with a separate trademark notice.

**Public license coordinates:** [MIT (repository_root)](https://github.com/bmad-code-org/bmad-method-test-architecture-enterprise/blob/a2819f62fc1b56486d223895eaa50578b490f2f5/LICENSE).

[Pinned overview](https://github.com/bmad-code-org/bmad-method-test-architecture-enterprise/blob/a2819f62fc1b56486d223895eaa50578b490f2f5/README.md) | [Historical inspection](EVIDENCE.md#bmad-tea-overview) | [Public metadata](../sources.json)

## bmad-loop

**Repository:** [bmad-code-org/bmad-loop](https://github.com/bmad-code-org/bmad-loop/tree/49eb8a3f15b1cab9758948b5b341516de9c044df)

**Pin:** `49eb8a3f15b1cab9758948b5b341516de9c044df`; committed 2026-11-02T03:33:28Z.

**Root license at review:** MIT; **archived at observation:** false.

**Historical depth:** Selected adapter implementation, profile, and documentation.

**Research disposition:** High-value control-loop reference.

A Python controller around coding CLIs, documenting story selection, implementation, verification, independent review, commit, durable state, and bounded attempts.

**Reusable contribution:** Separate CLI adapters from transport, observe actual completion rather than model prose, retain deferred work, distinguish environment faults, and use fresh review context.

**Conditions and exclusions:**

- Early beta; native Windows psmux transport is described as experimental.
- The bundled Copilot profile grants all tools, paths, and URLs and cites a specific macOS/CLI hook observation. It distinguishes main-session and subagent events and waits briefly for later usage records.
- The captured profile has no non-bypass mapping. Adapter platform rejection and missing mappings are integration constraints, not permission to bypass policy.
- Budget enforcement, verification selection, policy reload on resume, implementer-influenced review, and local merge behavior require deliberate assessment.

**License qualification:** Recorded MIT grant with a separate trademark notice.

**Public license coordinates:** [MIT (repository_root)](https://github.com/bmad-code-org/bmad-loop/blob/49eb8a3f15b1cab9758948b5b341516de9c044df/LICENSE).

[Pinned overview](https://github.com/bmad-code-org/bmad-loop/blob/49eb8a3f15b1cab9758948b5b341516de9c044df/README.md) | [Historical inspection](EVIDENCE.md#bmad-loop-overview) | [Public metadata](../sources.json)

## superpowers

**Repository:** [obra/superpowers](https://github.com/obra/superpowers/tree/22f0b463e7a5e579904dd6211a520321035526f7)

**Pin:** `22f0b463e7a5e579904dd6211a520321035526f7`; committed 2026-11-03T22:17:07Z.

**Root license at review:** MIT; **archived at observation:** false.

**Historical depth:** Selected README and skill contracts.

**Research disposition:** Compare first.

An engineering skill library spanning discovery, design approval, planning, TDD, diagnosis, review, and verification across coding hosts.

**Reusable contribution:** Understand context and intent before building, observe meaningful failures, review against the specification, and obtain fresh evidence before claiming completion.

**Conditions and exclusions:**

- Strong instructions are not runtime enforcement.
- Do not inherit blanket deletion of pre-existing code, an agent's ability to exceed a cap, or cleanup that discards useful user work or evidence.
- Fresh-worker context and spec/quality review still require bounded delegation and host-owned authority.
- Some optional visual features fetch external resources, requiring separate data and execution permission.

**Public license coordinates:** [MIT (repository_root)](https://github.com/obra/superpowers/blob/22f0b463e7a5e579904dd6211a520321035526f7/LICENSE).

[Pinned overview](https://github.com/obra/superpowers/blob/22f0b463e7a5e579904dd6211a520321035526f7/README.md) | [Historical inspection](EVIDENCE.md#superpowers-overview) | [Public metadata](../sources.json)

## addy-skills

**Repository:** [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills/tree/301b02b12bff98e4688e6984af6556802322bbde)

**Pin:** `301b02b12bff98e4688e6984af6556802322bbde`; committed 2026-11-01T19:24:49Z.

**Root license at review:** MIT; **archived at observation:** false.

**Historical depth:** Selected README, intake skill, and Copilot guide.

**Research disposition:** Compare first.

Lifecycle-oriented engineering skills for focused intent discovery, specification, TDD, review, and delivery.

**Reusable contribution:** One-question-at-a-time intake, a plain-language statement of intent, explicit non-goals, and focused quality-review checklists.

**Conditions and exclusions:**

- Intake confidence percentages are heuristics rather than calibrated evidence, and responsive-user confirmation is not an authentication protocol.
- Individual-skill copying can omit shared references.
- Copilot skill discovery is distinct from Claude lifecycle-command registration; manifest mode, precedence, and component paths matter.

**Public license coordinates:** [MIT (repository_root)](https://github.com/addyosmani/agent-skills/blob/301b02b12bff98e4688e6984af6556802322bbde/LICENSE).

[Pinned overview](https://github.com/addyosmani/agent-skills/blob/301b02b12bff98e4688e6984af6556802322bbde/README.md) | [Historical inspection](EVIDENCE.md#addy-skills-overview) | [Public metadata](../sources.json)

## rsc-harness

**Repository:** [ericrisco/rsc-harness](https://github.com/ericrisco/rsc-harness/tree/726aaf3ba87c584329fc821f243a7ce5e62450fd)

**Pin:** `726aaf3ba87c584329fc821f243a7ce5e62450fd`; committed 2026-11-04T11:15:02Z.

**Root license at review:** MIT; **archived at observation:** false.

**Historical depth:** Selected implementation, test source, and README.

**Research disposition:** Compare first.

A project-local meta-harness for selecting, deferring, or excluding capabilities, maintaining discoverable knowledge, and applying a specifically identified onboarding plan.

**Reusable contribution:** Exact-plan binding, stale-plan rejection, governed artifact digests, decision ledgers, provenance, receipts/backups, and explicit reasons not to install a capability.

**Conditions and exclusions:**

- A plan hash binds content, not the identity or authority of the person accepting it.
- Historical test-source assertions cover no-write preview, wrong-plan rejection, and receipts; the tests were not run.
- Host support is surface-specific; the captured table marks Copilot session memory unsupported.
- The public harness is not a separately verified complete implementation of the Risco video factory.

**Public license coordinates:** [MIT (repository_root)](https://github.com/ericrisco/rsc-harness/blob/726aaf3ba87c584329fc821f243a7ce5e62450fd/LICENSE).

[Pinned overview](https://github.com/ericrisco/rsc-harness/blob/726aaf3ba87c584329fc821f243a7ce5e62450fd/README.md) | [Historical inspection](EVIDENCE.md#rsc-harness-overview) | [Public metadata](../sources.json)

## agent-os

**Repository:** [buildermethods/agent-os](https://github.com/buildermethods/agent-os/tree/e892e61d322759165e7d9173e92c1010406c9f4d)

**Pin:** `e892e61d322759165e7d9173e92c1010406c9f4d`; committed 2026-10-07T04:18:58Z.

**Root license at review:** MIT; **archived at observation:** false.

**Historical depth:** README.

**Research disposition:** Focused knowledge reference.

A lightweight documented system for discovering, indexing, and injecting project standards and shaping specifications.

**Reusable contribution:** Select the standards relevant to the current task instead of loading an undifferentiated knowledge dump.

**Conditions and exclusions:**

- README review only, not a complete execution factory or tested host integration.
- Existing code patterns require judgment before promotion into authoritative standards.

**Public license coordinates:** [MIT (repository_root)](https://github.com/buildermethods/agent-os/blob/e892e61d322759165e7d9173e92c1010406c9f4d/LICENSE).

[Pinned overview](https://github.com/buildermethods/agent-os/blob/e892e61d322759165e7d9173e92c1010406c9f4d/README.md) | [Historical inspection](EVIDENCE.md#agent-os-overview) | [Public metadata](../sources.json)

## sssf

**Repository:** [disler/super-simple-software-factory](https://github.com/disler/super-simple-software-factory/tree/de31374882e7a4e3e5b7bb9bd09e69dc2f779356)

**Pin:** `de31374882e7a4e3e5b7bb9bd09e69dc2f779356`; committed 2026-08-02T17:57:38Z.

**Root license at review:** MIT; **archived at observation:** false.

**Historical depth:** Selected implementation and README.

**Research disposition:** High-value control-loop reference.

A small framework with deterministic Python phases and final acceptance, typed agent envelopes, JSONL traces, and a SQLite mirror.

**Reusable contribution:** Separate human/agent/code phases, bounded schema and claim-gate corrections, accumulated usage, current-run acceptance, and explicit process ownership records.

**Conditions and exclusions:**

- The reviewed backend validation accepts Pi only; this is not a drop-in Copilot plugin.
- Post-call write checking occurs before accepting the envelope, not before the effect; it is not a sandbox.
- The Git helper stages all changes with git add -A, which is not a safe automatic default for dirty or shared work.
- Final acceptance depends on the caller supplying the right condition. Trace storage is observable, not inherently tamper-proof.
- The separate example branch was not inspected.

**Public license coordinates:** [MIT (repository_root)](https://github.com/disler/super-simple-software-factory/blob/de31374882e7a4e3e5b7bb9bd09e69dc2f779356/LICENSE).

[Pinned overview](https://github.com/disler/super-simple-software-factory/blob/de31374882e7a4e3e5b7bb9bd09e69dc2f779356/README.md) | [Historical inspection](EVIDENCE.md#sssf-overview) | [Public metadata](../sources.json)

## attractor

**Repository:** [strongdm/attractor](https://github.com/strongdm/attractor/tree/fb57a55ed97372a27ac90102f436947e29f48426)

**Pin:** `fb57a55ed97372a27ac90102f436947e29f48426`; committed 2026-03-17T21:33:04Z.

**Root license at review:** Apache-2.0; **archived at observation:** false.

**Historical depth:** README and selected specification.

**Research disposition:** Design-contract reference.

Natural-language specifications for graph orchestration, a coding-agent loop, and a unified model interface.

**Reusable contribution:** Declared graphs, pluggable handlers, state, checkpoint/resume, human nodes, and a headless engine separated from backend and presentation concerns.

**Conditions and exclusions:**

- This is specification evidence, not an installed executable runtime.
- Only the opening main orchestration specification was semantically reviewed; companion specifications were not deeply inspected.

**Public license coordinates:** [Apache-2.0 (repository_root)](https://github.com/strongdm/attractor/blob/fb57a55ed97372a27ac90102f436947e29f48426/LICENSE).

[Pinned overview](https://github.com/strongdm/attractor/blob/fb57a55ed97372a27ac90102f436947e29f48426/README.md) | [Historical inspection](EVIDENCE.md#attractor-overview) | [Public metadata](../sources.json)

## fabro

**Repository:** [fabro-sh/fabro](https://github.com/fabro-sh/fabro/tree/1f5da01b47eeccb43b6b3bc79fe9cc455882a100)

**Pin:** `1f5da01b47eeccb43b6b3bc79fe9cc455882a100`; committed 2026-11-04T16:19:43Z.

**Root license at review:** MIT; **archived at observation:** false.

**Historical depth:** README.

**Research disposition:** Product comparison.

A graph-oriented factory product describing human gates, model routing, server/UI operation, checkpoints, durable outputs, and cloud sandboxes.

**Reusable contribution:** Visible graphs, inspectable outputs, and deliberate intervention points.

**Conditions and exclusions:**

- README quality guarantees and scale claims were not independently validated.
- Local server hosting does not prove local execution or storage.
- Cloud sandbox selection, automatic provider fallbacks, Git checkpoint policy, and selected-host integration need separate review.

**Public license coordinates:** [MIT (repository_root)](https://github.com/fabro-sh/fabro/blob/1f5da01b47eeccb43b6b3bc79fe9cc455882a100/LICENSE.md).

[Pinned overview](https://github.com/fabro-sh/fabro/blob/1f5da01b47eeccb43b6b3bc79fe9cc455882a100/README.md) | [Historical inspection](EVIDENCE.md#fabro-overview) | [Public metadata](../sources.json)

## roast

**Repository:** [Shopify/roast](https://github.com/Shopify/roast/tree/93b2f5c99982bd3e8df426fa09da02a64a454263)

**Pin:** `93b2f5c99982bd3e8df426fa09da02a64a454263`; committed 2026-10-21T17:43:55Z.

**Root license at review:** MIT; **archived at observation:** false.

**Historical depth:** Selected README.

**Research disposition:** Composition reference.

A Ruby DSL combining model calls, local coding agents, shell/code steps, iteration, mapping, and reusable workflow scopes.

**Reusable contribution:** Make deterministic operations explicit instead of using model calls for known sequencing or mechanical work.

**Conditions and exclusions:**

- The captured agent providers are Pi and Claude, not a qualified adapter for another selected host.
- It adds Ruby and provider configuration; local filesystem access does not imply isolation.

**Public license coordinates:** [MIT (repository_root)](https://github.com/Shopify/roast/blob/93b2f5c99982bd3e8df426fa09da02a64a454263/LICENSE.md).

[Pinned overview](https://github.com/Shopify/roast/blob/93b2f5c99982bd3e8df426fa09da02a64a454263/README.md) | [Historical inspection](EVIDENCE.md#roast-overview) | [Public metadata](../sources.json)

## deepagents

**Repository:** [langchain-ai/deepagents](https://github.com/langchain-ai/deepagents/tree/6cd647ba201d4612aeaa2d49d9588bd6e46ce250)

**Pin:** `6cd647ba201d4612aeaa2d49d9588bd6e46ce250`; committed 2026-11-04T23:59:49Z.

**Root license at review:** MIT; **archived at observation:** false.

**Historical depth:** README.

**Research disposition:** Architecture comparison.

A LangChain/LangGraph-based harness with subagents, filesystem backends, context management, memory, skills, and tool approval.

**Reusable contribution:** Explicit backend interfaces, context offloading, and durable state as separate capabilities.

**Conditions and exclusions:**

- Adopting this runtime is an explicit integration decision, not automatic use of the requested coding host.
- The README places security at the tool/sandbox boundary rather than trusting model self-restraint.
- Optional hosted tracing introduces its own data destination; README review is not runtime acceptance.

**Public license coordinates:** [MIT (repository_root)](https://github.com/langchain-ai/deepagents/blob/6cd647ba201d4612aeaa2d49d9588bd6e46ce250/LICENSE).

[Pinned overview](https://github.com/langchain-ai/deepagents/blob/6cd647ba201d4612aeaa2d49d9588bd6e46ce250/README.md) | [Historical inspection](EVIDENCE.md#deepagents-overview) | [Public metadata](../sources.json)

## openhands-sdk

**Repository:** [OpenHands/software-agent-sdk](https://github.com/OpenHands/software-agent-sdk/tree/2b4d980b6a54ef6685e4337e7643c40ec24be1bb)

**Pin:** `2b4d980b6a54ef6685e4337e7643c40ec24be1bb`; committed 2026-11-04T20:21:18Z.

**Root license at review:** MIT; **archived at observation:** false.

**Historical depth:** Selected README.

**Research disposition:** Architecture comparison.

A composable software-agent SDK and Agent Server with tools, conversations, workspace choices, events, and typed clients.

**Reusable contribution:** Separate execution engine, workspace, API/client, UI, and automation lifecycle.

**Conditions and exclusions:**

- This SDK repository is not the complete OpenHands product or automation service.
- Provider and host compatibility were not proven, and benchmark badges do not predict another component workload's acceptance.

**Public license coordinates:** [MIT (repository_root)](https://github.com/OpenHands/software-agent-sdk/blob/2b4d980b6a54ef6685e4337e7643c40ec24be1bb/LICENSE).

[Pinned overview](https://github.com/OpenHands/software-agent-sdk/blob/2b4d980b6a54ef6685e4337e7643c40ec24be1bb/README.md) | [Historical inspection](EVIDENCE.md#openhands-sdk-overview) | [Public metadata](../sources.json)

## mini-swe-agent

**Repository:** [SWE-agent/mini-swe-agent](https://github.com/SWE-agent/mini-swe-agent/tree/04d809ceab9df28f9adaed044884180159172930)

**Pin:** `04d809ceab9df28f9adaed044884180159172930`; committed 2026-09-03T05:05:59Z.

**Root license at review:** MIT; **archived at observation:** false.

**Historical depth:** Selected README.

**Research disposition:** Minimality reference.

A deliberately small software-agent loop emphasizing a linear trajectory and independent shell execution.

**Reusable contribution:** A simple observable baseline showing that every capability does not require a large framework.

**Conditions and exclusions:**

- The reviewed version is v2.
- One unrestricted shell tool can have broad authority. Bash-oriented execution and external model adapters are not native Windows or customized-host acceptance.

**Public license coordinates:** [MIT (repository_root)](https://github.com/SWE-agent/mini-swe-agent/blob/04d809ceab9df28f9adaed044884180159172930/LICENSE.md).

[Pinned overview](https://github.com/SWE-agent/mini-swe-agent/blob/04d809ceab9df28f9adaed044884180159172930/README.md) | [Historical inspection](EVIDENCE.md#mini-swe-agent-overview) | [Public metadata](../sources.json)

## copilot-sdk

**Repository:** [github/copilot-sdk](https://github.com/github/copilot-sdk/tree/c072001600018fe166910cfcb6eb42e769b9209d)

**Pin:** `c072001600018fe166910cfcb6eb42e769b9209d`; committed 2026-11-04T17:30:44Z.

**Root license at review:** MIT; **archived at observation:** false.

**Historical depth:** README and selected official SDK documentation.

**Research disposition:** Conditional integration candidate.

Programmatic Copilot sessions and tools, with documented local CLI connections, events, and lifecycle hooks.

**Reusable contribution:** Explicit runtime connection, structured events, and documented pre-tool approval/denial hooks where the selected host supports them.

**Conditions and exclusions:**

- Historical Node, Python, and .NET paths can automatically include a standard CLI. Do not silently replace an operator-selected host.
- Exact executable, version, protocol, identity, plugins, cancellation, and permission behavior remain qualification work.
- Examples using approve-all are not a recommended authorization policy. Documentation is not proof of complete hook coverage.

**Public license coordinates:** [MIT (repository_root)](https://github.com/github/copilot-sdk/blob/c072001600018fe166910cfcb6eb42e769b9209d/LICENSE).

[Pinned overview](https://github.com/github/copilot-sdk/blob/c072001600018fe166910cfcb6eb42e769b9209d/README.md) | [Historical inspection](EVIDENCE.md#copilot-sdk-overview) | [Public metadata](../sources.json)

## gh-aw

**Repository:** [github/gh-aw](https://github.com/github/gh-aw/tree/0aa2738ed88dea9f3f0e400381dde0f102efafd4)

**Pin:** `0aa2738ed88dea9f3f0e400381dde0f102efafd4`; committed 2026-11-05T00:51:19Z.

**Root license at review:** MIT; **archived at observation:** false.

**Historical depth:** Selected README.

**Research disposition:** Control-boundary reference.

Markdown-defined agentic workflows compiled into GitHub Actions, with read-oriented agent jobs and separately validated safe-output writes.

**Reusable contribution:** Separate reasoning from privileged mutation and validate structured requests in the effect executor.

**Conditions and exclusions:**

- Actions is a distinct execution and storage destination, not an assumed local runtime or an approved sink for restricted records.
- The chosen release's advisories, generated workflow, permissions, and egress require inspection rather than reliance on a security label.

**Public license coordinates:** [MIT (repository_root)](https://github.com/github/gh-aw/blob/0aa2738ed88dea9f3f0e400381dde0f102efafd4/LICENSE).

[Pinned overview](https://github.com/github/gh-aw/blob/0aa2738ed88dea9f3f0e400381dde0f102efafd4/README.md) | [Historical inspection](EVIDENCE.md#gh-aw-overview) | [Public metadata](../sources.json)

## eve-foreman

**Repository:** [vercel-labs/eve-software-factory-template](https://github.com/vercel-labs/eve-software-factory-template/tree/6bc5febab95de4c05fa08b164f544650f6aa11aa)

**Pin:** `6bc5febab95de4c05fa08b164f544650f6aa11aa`; committed 2026-09-29T14:57:51Z.

**Root license at review:** MIT; **archived at observation:** false.

**Historical depth:** Selected implementation, instructions, and README.

**Research disposition:** High-value product comparison.

Foreman routes work through classifier, analyst, implementer, and reviewer stations, with a maintained factory brain and draft-PR delivery.

**Reusable contribution:** Clarification before building, self-contained handoffs, separate review, unattended identity distinctions, and different policies for shared knowledge and shipping.

**Conditions and exclusions:**

- Selected sandbox code uses hosted Vercel Sandbox even during local development; the README also specifies a public Blob configuration.
- Station order and revision limits are present in orchestrator instructions; a complete code-enforced state machine was not established.
- Trusted/scheduled brain writes and draft PRs have different approval conditions from ordinary requests and ready-for-review shipping.
- The trust helpers use session context, but full webhook/channel verification was not traced.
- The brain tool performs a bounded document overwrite, not an immutable evidence-history update.

**Public license coordinates:** [MIT (repository_root)](https://github.com/vercel-labs/eve-software-factory-template/blob/6bc5febab95de4c05fa08b164f544650f6aa11aa/LICENSE).

[Pinned overview](https://github.com/vercel-labs/eve-software-factory-template/blob/6bc5febab95de4c05fa08b164f544650f6aa11aa/README.md) | [Historical inspection](EVIDENCE.md#eve-foreman-overview) | [Public metadata](../sources.json)

## archon-factory

**Repository:** [coleam00/ai-software-factory](https://github.com/coleam00/ai-software-factory/tree/f6d8f69e452607ceedc6d42f2ed0398db543ba71)

**Pin:** `f6d8f69e452607ceedc6d42f2ed0398db543ba71`; committed 2026-10-27T03:07:06Z.

**Root license at review:** NOT_ESTABLISHED; **archived at observation:** false.

**Historical depth:** Selected README and root inventory.

**Research disposition:** Reference only; licensing unresolved.

A factory setup around a pinned Archon SDLC pack, describing release intent, independent reviewers, user journeys, holdouts, scheduling, and staging feedback.

**Reusable contribution:** Mission/non-goals, user-level acceptance journeys, independent holdouts, and calibration using deliberate defects.

**Conditions and exclusions:**

- No root reuse license was established in the capture; source copying needs separately resolved permission.
- The underlying Archon implementation was not deeply reviewed.
- Automatic merge, deployment, and scheduled external actions are not authorized defaults.

No established root grant in the selected metadata; this is not a claim
that no license exists anywhere upstream.

[Pinned overview](https://github.com/coleam00/ai-software-factory/blob/f6d8f69e452607ceedc6d42f2ed0398db543ba71/README.md) | [Historical inspection](EVIDENCE.md#archon-factory-overview) | [Public metadata](../sources.json)

## waza

**Repository:** [microsoft/waza](https://github.com/microsoft/waza/tree/f5789f75fa00924411734d07fd4012ba80e2154c)

**Pin:** `f5789f75fa00924411734d07fd4012ba80e2154c`; committed 2026-11-04T21:40:52Z.

**Root license at review:** MIT; **archived at observation:** false.

**Historical depth:** Selected implementation, test source, and documentation.

**Research disposition:** Compare first, route by route.

A Copilot-oriented evaluation CLI for skills, agents, workflows, repository/CLI/MCP scenarios, trials, graders, and recorded evidence.

**Reusable contribution:** Freeze and bind evidence, isolate actor from judge, limit verdict tools, fail on missing/invalid callbacks, and distinguish process controls from live quality.

**Conditions and exclusions:**

- Ordinary custom-CLI execution, text-only execution, evidence judging, and preserved-snapshot grading have different contracts.
- Ordinary execution honors a usable COPILOT_CLI_PATH, otherwise uses an embedded CLI, without arbitrary PATH fallback.
- The evidence judge requires an absolute native executable identifying the tested pinned installation; matching version strings or arbitrary wrappers are insufficient.
- Test-source assertions describe Linux/macOS preserved-snapshot help. That limitation is not a claim about every Windows route.
- Text-only execution excludes tools, skills, fixtures/files, MCP, and agent definitions; its success would not qualify a tool-using factory.
- Foreign identity, digest-tamper, and source-preservation assertions were read, not executed.

**Public license coordinates:** [MIT (repository_root)](https://github.com/microsoft/waza/blob/f5789f75fa00924411734d07fd4012ba80e2154c/LICENSE).

[Pinned overview](https://github.com/microsoft/waza/blob/f5789f75fa00924411734d07fd4012ba80e2154c/README.md) | [Historical inspection](EVIDENCE.md#waza-overview) | [Public metadata](../sources.json)

## promptfoo

**Repository:** [promptfoo/promptfoo](https://github.com/promptfoo/promptfoo/tree/e3e2bb871540ae153a630878ecb17e56cfb487e3)

**Pin:** `e3e2bb871540ae153a630878ecb17e56cfb487e3`; committed 2026-11-04T22:20:50Z.

**Root license at review:** MIT; **archived at observation:** false.

**Historical depth:** README, selected implementation, and privacy documentation.

**Research disposition:** Conditional complementary evaluator.

An evaluation and red-teaming CLI/library with provider comparison, configurable assertions, rubrics, regression analysis, and adversarial cases.

**Reusable contribution:** Behavioral evaluation as a distinct layer from ordinary unit tests, with explicit cases, rubrics, and comparisons.

**Conditions and exclusions:**

- A local runner does not imply local data. Target calls, generation, grading, hosted-only features, telemetry, and sharing have separate paths.
- The selected implementation considers explicit disable flags, cloud preference/endpoints, and local credential availability.
- Disabling remote generation is not network isolation. No attack-generation workload, scan, or model trial was executed.

**License qualification:** The historical grant contains MIT terms without an MIT title; the research classifier was corrected after inspecting the grant.

**Public license coordinates:** [MIT (repository_root)](https://github.com/promptfoo/promptfoo/blob/e3e2bb871540ae153a630878ecb17e56cfb487e3/LICENSE).

[Pinned overview](https://github.com/promptfoo/promptfoo/blob/e3e2bb871540ae153a630878ecb17e56cfb487e3/README.md) | [Historical inspection](EVIDENCE.md#promptfoo-overview) | [Public metadata](../sources.json)

## rigour

**Repository:** [rigour-labs/rigour](https://github.com/rigour-labs/rigour/tree/7e0ef7f4e4ef614d55d83d2958e2603f65f019e7)

**Pin:** `7e0ef7f4e4ef614d55d83d2958e2603f65f019e7`; committed 2026-10-19T11:22:31Z.

**Root license at review:** MIT; **archived at observation:** false.

**Historical depth:** Selected implementation and documentation.

**Research disposition:** Compare first for feedback governance.

A review/checking system using repository rules and lessons, task tracking, and evidence-based lesson promotion, withdrawal, and demotion.

**Reusable contribution:** Candidate versus verified knowledge, counterevidence, human-decision precedence, recurrence criteria, task identity, and scoped profiles.

**Conditions and exclusions:**

- Human-origin recurrence can promote a lesson without a new explicit approval of that exact lesson; bot-only agreement is not sufficient.
- The optional goal check is narrower than semantic acceptance and may not run without a PR body, making it insufficient as a sole pre-code gate.
- Profiles do not establish OS isolation or authorize configured destinations.
- Setup changes hooks and may add components; that is separate from reading the source.

**Public license coordinates:** [MIT (repository_root)](https://github.com/rigour-labs/rigour/blob/7e0ef7f4e4ef614d55d83d2958e2603f65f019e7/LICENSE).

[Pinned overview](https://github.com/rigour-labs/rigour/blob/7e0ef7f4e4ef614d55d83d2958e2603f65f019e7/README.md) | [Historical inspection](EVIDENCE.md#rigour-overview) | [Public metadata](../sources.json)

## compound-engineering

**Repository:** [EveryInc/compound-engineering-plugin](https://github.com/EveryInc/compound-engineering-plugin/tree/799ac9aeb97bf1c51238c38122915470413c26c5)

**Pin:** `799ac9aeb97bf1c51238c38122915470413c26c5`; committed 2026-11-04T20:33:36Z.

**Root license at review:** MIT; **archived at observation:** false.

**Historical depth:** Selected workflow guides.

**Research disposition:** Compare first for learning discipline.

A workflow collection connecting intent, planning, implementation, review, and durable learning from verified outcomes.

**Reusable contribution:** Host-owned verification/delivery and the cheapest useful representation of a durable lesson, preferring a test or rule over duplicate narrative where possible.

**Conditions and exclusions:**

- Instruction contracts do not prove runtime enforcement.
- Full learning mode can discover histories across agent installations; project knowledge work does not imply permission to read unrelated transcripts.
- Lessons should preserve root causes, failed approaches, evidence, applicability, and retirement conditions rather than only the final success story.

**Public license coordinates:** [MIT (repository_root)](https://github.com/EveryInc/compound-engineering-plugin/blob/799ac9aeb97bf1c51238c38122915470413c26c5/LICENSE).

[Pinned overview](https://github.com/EveryInc/compound-engineering-plugin/blob/799ac9aeb97bf1c51238c38122915470413c26c5/docs/guides/ce-work.md) | [Historical inspection](EVIDENCE.md#compound-engineering-overview) | [Public metadata](../sources.json)

## gsd-core

**Repository:** [open-gsd/gsd-core](https://github.com/open-gsd/gsd-core/tree/93bb3b283998b5845cd94be98c9ce240d2946c12)

**Pin:** `93bb3b283998b5845cd94be98c9ce240d2946c12`; committed 2026-11-05T00:10:27Z.

**Root license at review:** MIT; **archived at observation:** false.

**Historical depth:** README.

**Research disposition:** Context-lifecycle reference.

A discuss-plan-execute-verify-ship workflow retaining durable phase artifacts and delegating substantial work into fresh contexts.

**Reusable contribution:** Explicit context handoffs, resumable phase state, and verification separate from implementation.

**Conditions and exclusions:**

- Fresh-context size and portability depend on the actual host.
- Installer runtime conversion means raw command copies are not necessarily equivalent.
- Avoid importing an entire second workflow or automatically spawning workers for simple work; this was README-level review.

**Public license coordinates:** [MIT (repository_root)](https://github.com/open-gsd/gsd-core/blob/93bb3b283998b5845cd94be98c9ce240d2946c12/LICENSE).

[Pinned overview](https://github.com/open-gsd/gsd-core/blob/93bb3b283998b5845cd94be98c9ce240d2946c12/README.md) | [Historical inspection](EVIDENCE.md#gsd-core-overview) | [Public metadata](../sources.json)

## gsd-archived

**Repository:** [gsd-build/get-shit-done](https://github.com/gsd-build/get-shit-done/tree/bdcaab2c752d9a33a1a1ca9acf3a3c81fb991815)

**Pin:** `bdcaab2c752d9a33a1a1ca9acf3a3c81fb991815`; committed 2026-05-31T13:34:35Z.

**Root license at review:** MIT; **archived at observation:** true.

**Historical depth:** README and repository metadata.

**Research disposition:** Historical redirect only.

The captured repository is archived and its README redirects current development to open-gsd/gsd-core.

**Reusable contribution:** Verify repository identity, archival status, and successor relationships rather than treating a popular historical link as the current implementation.

**Conditions and exclusions:**

- Do not select this snapshot as the maintained development home or transfer its old feature claims to the successor without checking.

**Public license coordinates:** [MIT (repository_root)](https://github.com/gsd-build/get-shit-done/blob/bdcaab2c752d9a33a1a1ca9acf3a3c81fb991815/LICENSE).

[Pinned overview](https://github.com/gsd-build/get-shit-done/blob/bdcaab2c752d9a33a1a1ca9acf3a3c81fb991815/README.md) | [Historical inspection](EVIDENCE.md#gsd-archived-overview) | [Public metadata](../sources.json)

## engineering-plugin

**Repository:** [anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins/tree/d900840716eb262e1feb17c6f4406c9ce0e06bcf)

**Pin:** `d900840716eb262e1feb17c6f4406c9ce0e06bcf`; committed 2026-11-04T02:50:55Z.

**Root license at review:** Apache-2.0; **archived at observation:** false.

**Historical depth:** Selected engineering-package README and manifest capture.

**Research disposition:** Plugin packaging and workflow reference.

The engineering package provides structured review, debugging, architecture, incident, testing, and documentation workflows with optional connectors.

**Reusable contribution:** Understandable domain workflows with a useful baseline experience even when optional integrations are not connected.

**Conditions and exclusions:**

- The package primarily targets Cowork and Claude Code; this study did not qualify another host.
- Connector categories are not installed or authorized services.
- Only the engineering slice and selected manifest material were screened, not the complete repository plugin estate.

**Public license coordinates:** [Apache-2.0 (repository_root)](https://github.com/anthropics/knowledge-work-plugins/blob/d900840716eb262e1feb17c6f4406c9ce0e06bcf/LICENSE).

[Pinned overview](https://github.com/anthropics/knowledge-work-plugins/blob/d900840716eb262e1feb17c6f4406c9ce0e06bcf/engineering/README.md) | [Historical inspection](EVIDENCE.md#engineering-plugin-overview) | [Public metadata](../sources.json)

## gitleaks

**Repository:** [gitleaks/gitleaks](https://github.com/gitleaks/gitleaks/tree/5f6ec56cfa6f8c67648d863582c7ae2f206d5c1c)

**Pin:** `5f6ec56cfa6f8c67648d863582c7ae2f206d5c1c`; committed 2026-10-23T20:44:59Z.

**Root license at review:** MIT; **archived at observation:** false.

**Historical depth:** Selected README.

**Research disposition:** Secret-scanning reference.

A deterministic scanner for credential-like content in Git history, files, and input streams, with machine-readable reporting.

**Reusable contribution:** Secret-pattern checking and redacted evidence as one concrete quality gate.

**Conditions and exclusions:**

- The captured README states that feature development ended and future releases focus on security patches, naming a successor not vetted here.
- A maintained, approved scanner must be chosen deliberately; a clean scan does not prove complete confidentiality or application security.
- No scanner installation or execution occurred in this study.

**Public license coordinates:** [MIT (repository_root)](https://github.com/gitleaks/gitleaks/blob/5f6ec56cfa6f8c67648d863582c7ae2f206d5c1c/LICENSE).

[Pinned overview](https://github.com/gitleaks/gitleaks/blob/5f6ec56cfa6f8c67648d863582c7ae2f206d5c1c/README.md) | [Historical inspection](EVIDENCE.md#gitleaks-overview) | [Public metadata](../sources.json)

## pester

**Repository:** [pester/Pester](https://github.com/pester/Pester/tree/98e56d65da1642a7158992b50ded240c42a3ac18)

**Pin:** `98e56d65da1642a7158992b50ded240c42a3ac18`; committed 2026-09-09T19:34:54Z.

**Root license at review:** Apache-2.0; **archived at observation:** false.

**Historical depth:** Selected README and actual license.

**Research disposition:** Relevant PowerShell test framework.

A PowerShell testing and mocking framework with assertions, execution, coverage, and machine-readable integration.

**Reusable contribution:** Behavior tests and service-isolating mocks for PowerShell/Windows component helpers.

**Conditions and exclusions:**

- Mocks constrain effects and also constrain the evidence they provide.
- Installed Windows versions, the current source, and release packages are different artifacts. No Pester installation or tests were run.

**License qualification:** Actual recorded root grant is Apache-2.0 despite the historical API NOASSERTION label.

**Public license coordinates:** [Apache-2.0 (repository_root)](https://github.com/pester/Pester/blob/98e56d65da1642a7158992b50ded240c42a3ac18/LICENSE).

[Pinned overview](https://github.com/pester/Pester/blob/98e56d65da1642a7158992b50ded240c42a3ac18/README.md) | [Historical inspection](EVIDENCE.md#pester-overview) | [Public metadata](../sources.json)

## twelve-factor

**Repository:** [humanlayer/12-factor-agents](https://github.com/humanlayer/12-factor-agents/tree/d20c728368bf9c189d6d7aab704744decb6ec0cc)

**Pin:** `d20c728368bf9c189d6d7aab704744decb6ec0cc`; committed 2025-09-21T14:37:40Z.

**Root license at review:** Apache-2.0; **archived at observation:** false.

**Historical depth:** Selected README and factor documents.

**Research disposition:** Conceptual foundation.

Practitioner principles for owned prompts, context, control flow, structured outputs, pause/resume, human contact, focused work, and bounded error recovery.

**Reusable contribution:** Persist meaningful business state and interrupt between proposed action and execution; use explicit bounded escalation rather than unlimited self-healing.

**Conditions and exclusions:**

- Conceptual guidance and illustrative pseudocode are not a qualified runtime.
- Factor 12 is largely image-based; the selected heading/link text does not establish what the uninspected diagrams show.

**License qualification:** The README declares CC-BY-SA-4.0 for written content separately from the Apache-2.0 code grant.

**Public license coordinates:** [Apache-2.0 (repository_root)](https://github.com/humanlayer/12-factor-agents/blob/d20c728368bf9c189d6d7aab704744decb6ec0cc/LICENSE).

[Pinned overview](https://github.com/humanlayer/12-factor-agents/blob/d20c728368bf9c189d6d7aab704744decb6ec0cc/README.md) | [Historical inspection](EVIDENCE.md#twelve-factor-overview) | [Public metadata](../sources.json)

## zazen-factory

**Repository:** [zazencodes/zazencodes-season-3](https://github.com/zazencodes/zazencodes-season-3/tree/6c2b66b0f38fc883f773fe098214c0cef4ea7654)

**Pin:** `6c2b66b0f38fc883f773fe098214c0cef4ea7654`; committed 2026-11-03T19:04:50Z.

**Root license at review:** NOT_ESTABLISHED; **archived at observation:** false.

**Historical depth:** Selected v1 skill and role contracts; separate v2 README and license only.

**Research disposition:** High-value conceptual example; conditional code reuse.

A video-linked small Claude skill-led factory that evolves toward parallel jobs. Later v1 contracts use per-job state, worktrees, distinct artifact owners, complete review rounds, and bounded builder resumptions.

**Reusable contribution:** Comprehensible control structure, inspectable handoffs, one intended state writer, complete current-round review, separate workspace/port identities, and visible blockers.

**Conditions and exclusions:**

- Original board.json prompt, recorded evolution, later pinned v1, and separate v2 are different evidence layers.
- V1 rules are instructions, not verified deterministic permission controls. The demo uses bypass permissions and does not demonstrate mandatory human brief approval before coding.
- V1 permits model-authorized local-main merge but says never to push; this is not proof of automatic production deployment.
- Two builder resumptions mean up to three review rounds per invocation; fresh user rework gets a new allowance, not an enforced lifetime budget.
- Claude/Bash interfaces require adaptation. Other reviewer contracts, the dashboard, general recovery, and v2 executable implementation were not audited.
- V2 README describes script/state gates and PR delivery while retaining model-authorized merging; those claims were not runtime-tested.

**License qualification:** No standard root/v1 license was established despite an invitation to copy. V2 has a scoped GPLv3 license, not a grant for sibling folders and not a noncommercial-only restriction.

**Public license coordinates:** [GPLv3 (src/software-factory-claude-code-v2 only; root/v1 not established)](https://github.com/zazencodes/zazencodes-season-3/blob/6c2b66b0f38fc883f773fe098214c0cef4ea7654/src/software-factory-claude-code-v2/LICENSE).

[Pinned overview](https://github.com/zazencodes/zazencodes-season-3/blob/6c2b66b0f38fc883f773fe098214c0cef4ea7654/src/software-factory-claude-code/README.md) | [Historical inspection](EVIDENCE.md#zazen-factory-overview) | [Public metadata](../sources.json)
