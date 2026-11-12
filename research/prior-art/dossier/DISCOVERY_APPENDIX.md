# Discovery method, returned resources, and unresolved leads

**Discovery baseline:** 2026-11-05. **Public edition:** 2026-11-12.
No new search, registry request, installation, connection, or source fetch was
made to prepare this edition. Original query/session payloads and private
search context are excluded.

## Method and selection

The study considered specification-driven development, software factories,
deterministic agent orchestration, coding harnesses, test generation,
evaluation, persistent project knowledge, review learning, human approval,
and reusable plugin/skill generation.

Discovery used public web and GitHub searches, primary project documentation,
code intelligence to locate implementation paths, and an Agent Finder query.
Public questions used generic capability abstractions rather than private
wiki text, source code, records, or organizational identifiers.

Promising projects were pinned using public repository metadata and
commit-qualified content reads. The historical collector's contract was to
refuse non-public repositories, capture inert UTF-8 text, verify Git blob
identity, and record content digests. That process does not make acquired
instructions trusted, install the discovered resource, or approve its
dependencies.

Selection favored a concrete reusable mechanism, relevance to the desired
workflow and host questions, inspectable evidence, and explicit limitations.
Popularity was not a safety or engineering-quality score. This is a broad
purposeful sample, not an exhaustive market census.

## All six Agent Finder results

The historical request returned six entries from
`https://agentfinder.github.com/api/v1/search`. Scores describe search
relevance only, not trust, licensing, security, or measured implementation
quality. The types below are the actual returned types, not inferred
compatibility promises.

### 1. Agent Skills

- Type: `application/vnd.anthropic.claude-plugin+json`
- Relevance: **95**
- [Returned public revision](https://github.com/addyosmani/agent-skills/tree/301b02b12bff98e4688e6984af6556802322bbde)

Selected intake, packaging, and review-related material subsequently received
bounded review. See the [candidate](CATALOG.md#addy-skills). The registry type
does not by itself establish behavior on every host.

### 2. Git Workflow Skill: MAUI/Comet example

- Type: `application/agent-skills+md`
- Relevance: **82**
- [Returned public revision and path](https://github.com/dotnet/maui-labs/tree/e2f4a89e8d3ccc0ead6fabef2a4f43bdd241ce82/src/Comet/.copilot/skills/git-workflow)

This remained a discovery-only, project-specific example. It was not installed
or deeply reviewed. Its branching conventions are not a product requirement
or authority for this repository.

### 3. Git Workflow Skill: Waza example

- Type: `application/agent-skills+md`
- Relevance: **82**
- [Returned public revision and path](https://github.com/microsoft/waza/tree/394196ccd02f5f161ed643ff731bff5930a75401/.github/skills/git-workflow)

The sample skill itself was not deeply reviewed. The separately studied
[Waza evaluator](CATALOG.md#waza) has a **different** immutable pin,
`f5789f75fa00924411734d07fd4012ba80e2154c`. Neither source identity should
overwrite the other or inherit its review coverage.

### 4. Git Workflow for Squad

- Type: `application/agent-skills+md`
- Relevance: **82**
- [Returned public revision and path](https://github.com/microsoft/github-vteam-industry-demos/tree/52a1e8c92456b3469b9a4afdc06d3f2cc4ab6796/industries/healthcare-life-sciences/claim-processing/.github/skills/git-workflow)

This remained a discovery-only example. Its workflow and domain conventions
were not adopted. An industry-demo path does not establish acceptance for a
different workload.

### 5. Rigour Code Reviewer

- Type: `application/mcp-server+json`
- Relevance: **79**
- [Returned descriptor, version 7.0.14](https://api.mcp.github.com/v0.1/servers/io.github.rigour-labs%2Frigour/versions/7.0.14)

The descriptor led to the public source repository. Selected lesson logic and
operating documentation were reviewed as [Rigour](CATALOG.md#rigour).
No MCP server was installed, connected, or invoked. A descriptor version
is not the same thing as the repository commit selected for source reading.

### 6. Engineering Plugin

- Type: `application/vnd.anthropic.claude-plugin+json`
- Relevance: **73**
- [Returned public revision and path](https://github.com/anthropics/knowledge-work-plugins/tree/2574e29377c7173d0cecffef29a6ecbd7f8ccb5d/engineering)

The engineering slice was separately screened at the newer catalog pin,
`d900840716eb262e1feb17c6f4406c9ce0e06bcf`. The
[catalog entry](CATALOG.md#engineering-plugin) applies only to that selected
slice and revision, not the complete plugin estate or the earlier search pin.

These are preserved response facts, not installation offers. Full registry
payloads, executable resources, and original search prompts are not included.

## Additional leads

All seven original additional leads remain visible, separate from the 33
reviewed repository snapshots:

| Lead | Why it appeared | Actual historical status |
|---|---|---|
| [Agent-Field/CodeAF](https://github.com/Agent-Field/CodeAF) | Software-factory search context | Search-only; no pinned implementation review |
| [iusztinpaul/squid](https://github.com/iusztinpaul/squid) | Related agent/factory approach | Search-only; not a qualified dependency |
| [warpdotdev/warp](https://github.com/warpdotdev/warp) | Agentic-development product context | Search-only; no product acceptance or source audit |
| [block/goose](https://github.com/block/goose) | Referenced by Stripe's Minions account | Not acquired or deeply inspected here |
| [betterleaks/betterleaks](https://github.com/betterleaks/betterleaks) | Named as the Gitleaks maintainer's new focus | Successor lead only; not vetted or substituted automatically |
| [coleam00/Archon](https://github.com/coleam00/Archon) | Dependency named by the factory wrapper | Wrapper README reviewed; underlying implementation not deeply reviewed |
| [OpenAI harness engineering](https://openai.com/index/harness-engineering/) | Relevant primary-source theory lead | Direct fetch returned HTTP 403; not used for new verified claims |

A named lead is not a downloaded, executed, licensed, or approved component.
The inaccessible article remains inaccessible evidence from that pass, not a
claim inferred from its title or substituted secondary material.

## Direct video reference added after the first baseline

The supplied [ZazenCodes walkthrough](https://www.youtube.com/watch?v=ctoaIC4LHmI)
and overview led to a focused follow-up on 2026-11-05. The video description
and the repository index identify `zazencodes/zazencodes-season-3` and its
`src/software-factory-claude-code` lesson.

This added one repository to the initial 32, not another indiscriminate
discovery pass. The [detailed review](VIDEO_ZAZEN_FACTORY.md) preserves the
historical available-caption coverage, selected visual observations, and
bounded companion-contract reading. V2 was screened only through its README
and opening license text, not executable implementation.

The user-provided overview, source captions, and frames are not copied into
this publication. The analysis distinguishes initial design, recorded
evolution, later pinned v1, and separate v2 rather than treating them as one
static blueprint.

## Acquisition and review limits

- Root and selected directory listings are not recursive whole-tree
  inventories.
- Source paths found through code intelligence were checked against the
  captured immutable revision before use as code evidence.
- A Foreman template `src` lookup did not resolve; its actual root inventory
  identified the `agent` directory. The study corrected the path rather than
  selecting another repository or credential.
- README claims about dependencies, platform support, or security remain
  documentation claims unless a corresponding mechanism is separately cited.
- README images and demonstrations were not exhaustively acquired or visually
  inspected. A caption alone does not establish an image's contents.
- Public web articles use canonical URLs and historical read dates, not
  immutable Git snapshot identities.
- The historical Risco author-repository listing did not locate a separately
  named complete video-factory implementation. That bounded result is not
  proof that none exists.

Use the [inspection register](EVIDENCE.md) for exact historical source ranges
and the [coverage statement](COVERAGE_AND_VALIDATION.md) for the evidence
denominators. [Public context metadata](public-context-sources.json) preserves
all discovery identities without importing private query/session records.
