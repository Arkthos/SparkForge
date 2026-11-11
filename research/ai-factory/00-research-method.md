# 00 - Research Method and Evidence Boundaries

[Back to the index](README.md)

## Research question

What knowledge, engineering practices, and organizational mechanisms are needed to turn AI-assisted work into a repeatable software delivery capability?

Subquestions:

- What do different communities mean by "AI factory"?
- What belongs in an agent harness, an evaluation harness, and a developer environment?
- How do tools, context, memory, skills, and orchestration interact?
- What makes generated work verifiable, recoverable, economical, and authorized?
- Which parts of the supplied Allbright stack are portable principles, and which are implementation choices?
- What must we learn or measure before designing our own solution?

The main scope is software engineering. Infrastructure factories and predictive ML are supporting context, not an instruction to build a data center or train a foundation model.

## Method

This is a **structured technical literature review and design synthesis**, not an exhaustive systematic review or meta-analysis.

The research used focused searches to discover sources, followed by direct reading of available original pages, documentation, and research abstracts. Source selection favored:

1. Maintainer-owned specifications for protocol and tool behavior.
2. Official technical documentation for product capabilities.
3. Original engineering reports for observed implementation patterns.
4. Research papers and independent studies for bounded empirical findings.
5. Practitioner writing for architecture proposals and operational experience.

Search summaries were discovery aids, not automatically treated as verified article contents. Where the source body could not be retrieved, that limitation is recorded. No benchmark was rerun and no private implementation was inspected.

## Evidence classes

| Class | What it can support | What it cannot establish alone |
|---|---|---|
| Specification | What a particular protocol version requires or describes | That a deployed implementation is compliant or secure |
| Official documentation | Documented capabilities and configuration concepts | Real-world reliability, actual enablement, or favorable economics |
| Vendor engineering report | A team's account of a design and its experience | Universal performance or independent replication |
| Research publication | Findings within a reported method, tasks, and models | Unqualified transfer to a different workload or current model |
| Independent empirical study | Evidence within its population and measurement design | Effects outside the studied population or after major tooling changes |
| Practitioner proposal | A concrete architecture and experience-based heuristics | A standard, universal maturity model, or proven scaling law |
| Corpus synthesis | Our recommended way to combine the evidence | A result that has already been implemented or tested here |

These classes are not a simple ranking. A specification is stronger than a blog for a message format; a measured study is more relevant than a specification for productivity. A research abstract is sufficient to identify a paper's reported contribution, but not to audit its experimental validity.

## Source access labels

The [catalog](sources.json) records access using these values:

- `page_text`: relevant page text was directly retrieved and read.
- `excerpt`: a directly retrieved portion was read; the entire document was not reviewed.
- `abstract`: the paper's abstract and available bibliographic metadata were read, not a full-paper replication review.
- `indexed_excerpt`: the original source's search-indexed excerpt was available, but full relevant page text was not successfully retrieved.
- `transcript_and_selected_frames`: the complete available auto-generated transcript was read and selected video frames were inspected; this is not a continuous audiovisual viewing or implementation audit.

These labels describe access, not credibility.

Important limitations:

- OpenAI's harness-engineering page returned HTTP 403 to direct retrieval. Its title, date, and limited claims were checked through indexed excerpts of the original page. We do not present a full close reading of that article.
- The OWASP Top 10 landing page's simplified retrieval did not expose its full risk list. The 2025 category names were checked through the original page's indexed excerpt; the prompt-injection page was directly read.
- Several research entries were reviewed at abstract level. Detailed quantitative claims are therefore intentionally avoided.
- Living documentation redirected in several cases. The bibliography and catalog retain the relevant observed destination or a clearly identified source.
- Retrieved pages are a dated observation. A `/latest/` page, repository default branch, or unversioned blog is not an immutable source snapshot.
- The requested Eric Risco video was identified through YouTube's own metadata. Its Spanish auto-generated transcript was read from 00:00 through 17:20, and frames around 06:40, 10:25, and 14:18 were inspected. Captions contain transcription errors; exact model names, numerical claims, and product capabilities are not accepted solely on that basis. A search result for a different video was excluded rather than used as a substitute.

## Dates and versions

The research baseline is **2026-11-04**. An access date is not a publication date.

Only explicitly visible or otherwise verified dates are stated as such. Where publication timing was not established, the bibliography says so rather than using a crawler timestamp. For the supplied Allbright article, June 21, 2026 is the publication date shown in the user-provided article.

Protocol discussions are deliberately scoped:

- MCP is discussed using the **2026-07-28** specification observed during research. This is a versioned reference, not a claim that it is the newest available specification.
- A2A is discussed using the **1.0.0** specification.
- OpenTelemetry's former GenAI documentation location now points to a separate GenAI semantic-conventions repository. Exact attribute stability and implementation compatibility must be rechecked before adoption.

Product features, authentication arrangements, pricing, model names, and deployment availability have shorter shelf lives than the underlying engineering principles.

## Rules for claims in this corpus

**Reported result:** attribute it to the source, retain the studied setting, and include meaningful limitations.

**Recommendation:** identify it as a design recommendation or corpus synthesis. Do not imply that a source mandates our specific architecture.

**Example:** mark it synthetic or illustrative. A plausible event log is not a real run receipt.

**Unresolved question:** state what evidence would help answer it. Do not fill missing facts with confident extrapolation.

**Completion claim:** distinguish produced, checked, accepted, authorized, and released.

For example, Anthropic's long-running-agent report supports examining initializer/progress/test patterns. It does not establish that JSON progress files are always superior to Markdown, that a single agent always wins, or that its web-application findings generalize to every domain. [S07](16-sources-and-reading-guide.md#s07)

## Handling contradictory or evolving evidence

The METR productivity studies are an important example. The July 2025 report found a slowdown for experienced developers performing their own open-source tasks with the tools studied. The February 2026 update describes selection and measurement problems that make its newer data an unreliable estimate of current productivity effects. The appropriate lesson is **measure the actual workflow carefully**, not "AI always slows developers" or "the new study proves a universal speedup." [S32](16-sources-and-reading-guide.md#s32) [S33](16-sources-and-reading-guide.md#s33)

StrongDM's removal of human code review and Allbright's human-guided team practice are different operating choices. Neither can be selected solely because its story is compelling. Workload risk, verifier quality, organizational obligations, and measured outcomes determine the appropriate review model.

## Copyright and data handling

The corpus uses original explanation, short terminology references, and links. It is not a redistribution of full articles, paper text, screenshots, or proprietary training material.

Only public-source knowledge and synthetic examples are included. Public availability does not imply permission to scrape, train on, or redistribute every linked source. Future ingestion should check source terms, attribution needs, and storage permissions.

External pages are evidence to assess, not instructions to execute. A documentation page that contains installation commands does not authorize running them.

## Maintaining this knowledge base

When updating a chapter:

1. Identify the specific claim or design decision being refreshed.
2. Reopen the authoritative source and note its version or visible revision.
3. Update the source record and the affected chapter together.
4. Explain changed conclusions, especially when older guidance no longer applies.
5. Preserve an honest distinction between a historical finding and current behavior.
6. Recheck local links, source IDs, examples, and cross-chapter terminology.

Suggested review triggers are a protocol change, SDK adoption, new model, data-boundary change, failed experiment, or release decision. A recurring calendar review can help, but should not replace event-driven review.

## Definition of a useful corpus

The corpus is useful if a reader can explain the concepts, challenge unsupported claims, design a bounded workflow, and specify how to test it. Length and the number of sources are not substitutes for those abilities.

Use [the evidence map](17-evidence-map-and-open-questions.md) to scrutinize conclusions and [the assessment](19-competency-assessment.md) to evaluate understanding.
