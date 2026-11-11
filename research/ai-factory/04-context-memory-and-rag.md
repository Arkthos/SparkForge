# 04 - Context, Memory, and Retrieval-Augmented Generation

[Back to the index](README.md)

## Context is a selected view

The model does not see "the whole system." It sees the inputs assembled for a particular request, subject to the model's context and modality limits.

Context engineering is the discipline of selecting, organizing, updating, and constraining that information. Prompt engineering is one part of it, focused on instructions and examples. Anthropic's context-engineering account discusses instructions, tools, external information, message history, and long-horizon state together. [S08](16-sources-and-reading-guide.md#s08)

The design problem is not simply to maximize context length. It is to provide sufficient, relevant, trustworthy information without obscuring the task or exceeding practical limits.

## A context budget

Think of context as competing categories:

| Category | Purpose | Typical failure |
|---|---|---|
| Operating instructions | Define role and constraints | Too vague, contradictory, or overloaded |
| Task contract | State the requested outcome | Lost or superseded by incidental conversation |
| Tool descriptions | Explain available actions | Too many overlapping tools |
| Current state | Explain what has happened | Stale summary or missing unresolved operation |
| Retrieved evidence | Ground domain claims | Irrelevant, unauthorized, or misleading content |
| Recent observations | Support the next decision | Large logs overwhelm the useful error |
| Examples | Demonstrate expected behavior | Narrow examples bias behavior or leak holdouts |
| Output reserve | Leave room for a useful response | Input consumes the available window |

Do not set a universal percentage allocation without measuring the workload. A repository investigation and a structured extraction task have different needs.

The Lost in the Middle study reports position-sensitive use of long context in its evaluated models and tasks. It supports testing effective information use, not a claim that every current model has an identical failure curve. [S28](16-sources-and-reading-guide.md#s28)

## Memory is not one thing

| Memory type | Example | Main design concern |
|---|---|---|
| Working memory | Current task plan and recent tool results | Relevance and bounded size |
| Episodic history | What happened in a particular run | Provenance, ordering, retention |
| Semantic knowledge | Reviewed facts about a system | Correctness, freshness, scope |
| Procedural knowledge | How to perform a recurring workflow | Applicability and versioning |
| Preferences | Approved user or team defaults | Consent, scope, conflict handling |
| Runtime state | Pending operation and budget balance | Durability and consistency |

Do not put all of these into a vector database and call the problem solved. They have different update, security, and retrieval semantics.

For example, the pending status of an external write should be retrieved by a reliable identifier, not by approximate semantic similarity. A style preference can be advisory; a permission boundary must come from an authoritative policy source.

## Retrieval-augmented generation

RAG combines generation with retrieved external information. The original RAG research combined parametric model knowledge with a non-parametric retrieval mechanism for knowledge-intensive tasks. Modern application usage is broader and can include keyword, vector, structured, or hybrid retrieval. [S27](16-sources-and-reading-guide.md#s27)

A practical pipeline:

```text
Authorized sources
    -> parsing and normalization
    -> metadata and provenance
    -> chunking and indexing
    -> permission-aware retrieval
    -> relevance filtering or reranking
    -> evidence selection
    -> generation with source references
    -> groundedness and outcome checks
```

Every stage can introduce errors. A plausible final answer can conceal incorrect parsing, missed evidence, stale indexing, or an unauthorized document.

## Ingestion design

Before indexing a source, record:

- owner or publisher;
- canonical location;
- revision or content identifier;
- retrieval or observation date;
- effective date where relevant;
- permission and retention classification;
- parser version and known extraction limitations;
- whether the source is authoritative, explanatory, or speculative.

Handle tables, code, diagrams, and attachments deliberately. Flattening a table can reverse relationships. A text extractor may omit important image content. A source containing a title and an empty body should not silently become evidence.

For this corpus, the chapter heading, section heading, source IDs, and research date should travel with a retrieved passage.

## Chunking and retrieval choices

**Fixed-size chunks** are simple but can split definitions from exceptions. **Structure-aware chunks** follow sections, functions, or tables but require suitable parsers. **Parent-child retrieval** can index small pieces and return a larger surrounding context when needed.

Choose retrieval based on the task:

| Need | Useful starting point |
|---|---|
| Exact error code, identifier, or filename | Keyword or structured search |
| Concept expressed in different language | Semantic retrieval |
| Join records by stable keys | Database query |
| Follow explicit dependencies or entities | Graph traversal |
| Mixed terminology and exact constraints | Hybrid retrieval |
| Small, stable set of highly relevant documents | Direct selection may be enough |

A vector database is not mandatory for RAG. A knowledge graph is not mandatory for a knowledge corpus. Use the simplest retrieval method that meets measured recall and precision requirements.

## Evaluate retrieval separately from generation

Questions for retrieval:

- Did it find the necessary evidence?
- Did it rank the relevant material highly enough to be used?
- Did it respect permissions?
- Did it return the right version?
- Did it preserve enough surrounding context?

Questions for generation:

- Does the answer actually follow from the retrieved evidence?
- Does it distinguish fact from inference?
- Are citations attached to the right claims?
- Does it abstain when evidence is insufficient?
- Does it meet the user's task rather than merely summarize sources?

If retrieval never supplied the relevant policy, changing the answer prompt may only produce a more convincing wrong answer.

## Citation quality

A citation can fail in several ways:

1. The source does not exist.
2. The source exists but does not contain the claim.
3. The source contains a related claim with different scope.
4. The source is outdated for the question.
5. The source is reporting someone else's unverified claim.
6. The answer omits a qualification that changes the conclusion.

Source grounding is therefore more than URL validation. It requires a claim-to-evidence relationship and attention to scope.

For consequential assertions, retain the exact source version or a permitted evidence excerpt. A content hash can help identify bytes, but does not establish truth or permission.

## Just-in-time context versus preloading

Preloading is useful when the relevant material is predictable and small. Just-in-time retrieval is useful when the information space is large or changes frequently.

Anthropic describes hybrid approaches in which stable instructions are loaded early while tools locate task-specific information as needed. [S08](16-sources-and-reading-guide.md#s08)

Tradeoffs:

- Preloading can reduce search latency but waste context and expose unnecessary data.
- Dynamic retrieval can improve focus but introduce tool cost, missed evidence, and search loops.
- Caching can reduce repeated work but creates invalidation and access-control obligations.
- Summaries can reduce size but lose details needed later.

A useful pattern is a short map of the knowledge system plus targeted retrieval, rather than a giant instruction file containing every fact.

## Compaction and recovery

Compaction should preserve goals, constraints, decisions, unresolved issues, and pointers to authoritative artifacts. It should not be the only surviving copy of evidence.

Before accepting a compacted state:

- reconcile it with the durable task state;
- retain identifiers for important artifacts;
- preserve uncertainty instead of converting it into certainty;
- keep the distinction between planned and completed actions;
- avoid promoting untrusted source instructions into trusted summaries.

This last failure is a form of **memory poisoning**: an untrusted document's instruction is summarized as if it were the user's decision.

## Memory write policy

Not every observed fact deserves long-term memory.

For a candidate memory, ask:

1. Is it true enough and useful beyond this task?
2. Who or what is it about?
3. Is its storage authorized?
4. What evidence supports it?
5. What scope should it have?
6. When should it expire or be rechecked?
7. Can it be corrected or deleted, including derived indexes?

Store tentative observations as tentative. A single workaround should not become a permanent operating rule. Do not infer sensitive personal preferences from behavior.

## Permission-aware knowledge

Enforce access before unauthorized content reaches a model, reranker, cache, or log sink. Filtering only the final answer is too late.

Cache keys and memory scopes may need tenant, user, policy, document revision, and purpose information. Revocation must propagate to indexes, summaries, and retained copies as required by the applicable policy.

An embedding is not automatically anonymous. A derived summary can remain confidential. A public URL embedded in a private report does not make the entire report public.

## RAG, fine-tuning, and prompting

| Technique | Main lever | Useful when | Does not inherently solve |
|---|---|---|---|
| Prompting | Instructions and examples at inference | Desired behavior can be specified clearly | Missing facts or permissions |
| RAG | External evidence at inference | Knowledge changes or must be attributable | Reasoning errors or prompt injection |
| Fine-tuning | Model parameters | Repeated behavior needs adaptation and suitable data exists | Live knowledge freshness or authorization |
| Tool access | Ability to observe or act | The task requires current state or computation | Safe authority and outcome verification |
| Workflow design | Sequence and control | The process is known and benefits from constraints | Poor criteria or unreliable components |

These methods can be combined. Investigate the failure before choosing the intervention.

## Practice question

An agent retrieves an old deployment guide and a newer exception policy. It cites the old guide, then stores "deployments never need approval" as memory. Identify the ingestion, ranking, generation, and memory-policy failures separately. A single "better prompt" is unlikely to be the complete fix.
