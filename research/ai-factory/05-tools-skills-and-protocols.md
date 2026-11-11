# 05 - Tools, Skills, Instruction Files, and Protocols

[Back to the index](README.md)

## Why interfaces matter

An agent's useful action space is shaped by the tools it can discover and operate. Poor interfaces cause errors even when the underlying model is capable.

Anthropic's tool-design guidance emphasizes clear boundaries, meaningful outputs, token efficiency, and evaluations. SWE-agent research studies the importance of an agent-computer interface rather than assuming a human-oriented shell is always the best interface. [S09](16-sources-and-reading-guide.md#s09) [S29](16-sources-and-reading-guide.md#s29)

## A tool is a behavioral contract

Document more than its name and parameter types:

| Contract element | Example question |
|---|---|
| Purpose | What user outcome does the operation support? |
| Preconditions | What must exist or be true first? |
| Identity and target | Under whose authority, against which resource? |
| Inputs | Which fields are required, bounded, and validated? |
| Side effects | Does it read, write, publish, spend, or delete? |
| Idempotency | What happens if the same operation is requested twice? |
| Output | What is authoritative in the returned result? |
| Errors | Which failures are retryable, permanent, or uncertain? |
| Observability | What operation ID and evidence are returned? |
| Limits | Timeout, result size, rate limit, and budget impact |

For example, `publish_report` needs more care than `render_report_preview`. Both may accept the same document, but only one creates an external side effect.

## Design for the agent's task

Good tools expose useful operations, not necessarily every low-level API endpoint.

Instead of returning an entire database table, a tool can support a bounded, permission-aware query. Instead of one ambiguous `manage_everything` operation, separate read, prepare, and commit operations.

Avoid the opposite extreme too: a giant collection of narrowly named tools can overwhelm selection. Measure whether the agent can choose the right operation and recover from errors.

Tool descriptions should make failure handling visible. An empty list should mean "no matching results" only when the search actually completed; an unavailable backend needs a distinct error.

## Structured output is necessary but insufficient

A valid JSON object can still contain the wrong customer identifier, a stale revision, or an unauthorized action. Validate:

1. Syntax and schema.
2. Domain constraints.
3. Identity and resource scope.
4. Current preconditions.
5. Required approval.
6. Postconditions after execution.

The first layer prevents malformed calls. The later layers prevent well-formed mistakes.

## Example result envelope

This is a conceptual interface, not a vendor API:

```json
{
  "operation_id": "op-demo-014",
  "status": "needs_reconciliation",
  "resource_id": "synthetic-ticket-27",
  "observed_revision": "rev-8",
  "side_effect": "possible",
  "retryable": false,
  "evidence_refs": ["restricted-run-store:event-92"],
  "message": "The connection ended before confirmation; inspect the operation status before retrying."
}
```

An uncertain result must not be collapsed into either success or failure. A tool should help the harness decide safely, not force it to guess.

## Skills, personas, and subagents

| Mechanism | What it is | What it is not |
|---|---|---|
| Persona | A role or behavioral specialization | An independent security principal |
| Skill | Reusable procedural instructions and resources | Necessarily a separate execution context |
| Subagent | A delegated execution with its own context/lifecycle | Automatically independent judgment or lower cost |
| Tool | A callable operation | A complete workflow or policy system |
| Instruction file | Project-specific guidance | An enforcement mechanism |

The Agent Skills format describes a folder centered on `SKILL.md`, with metadata, instructions, and optional scripts or resources. It uses progressive disclosure: discovery metadata first, full instructions when relevant, supporting material as needed. [S17](16-sources-and-reading-guide.md#s17)

A skill that contains executable code also introduces a software supply-chain surface. Its installation or discovery does not authorize unrestricted execution.

## Project instruction files

AGENTS.md is an open convention for providing coding agents with project guidance. Other systems have their own instruction-file conventions, including CLAUDE.md. [S18](16-sources-and-reading-guide.md#s18) [S12](16-sources-and-reading-guide.md#s12)

A good project guide describes:

- the codebase map;
- supported commands;
- architecture constraints;
- test and review expectations;
- how to locate more detailed documents;
- known environmental limitations.

Keep stable guidance distinct from a run's temporary plan. Avoid burying secrets, production credentials, or a full organization knowledge base in an automatically loaded file.

Different products can apply discovery, precedence, inheritance, and scope differently. Verify the selected runtime's behavior rather than assuming all instruction-file conventions are interchangeable.

## Model Context Protocol

MCP standardizes connections between AI applications and external context or capabilities. The observed 2026-07-28 specification describes hosts, clients, and servers, with resources, prompts, and tools among the core concepts. [S15](16-sources-and-reading-guide.md#s15)

- A **host** is the AI application.
- A **client** is a connector within the host.
- A **server** exposes supported capabilities.
- A **resource** supplies contextual information.
- A **prompt** packages templated interaction content.
- A **tool** exposes an operation.

This version is cited deliberately; it is not asserted to be the latest release. Features and extension semantics differ between versions. Negotiate and test the version and capabilities actually used.

MCP does not by itself answer:

- whether the user authorized a particular operation;
- whether a server is trustworthy;
- whether a returned document is accurate;
- whether a write is safe to retry;
- whether the endpoint can receive a particular data classification;
- whether tool descriptions are free of malicious instructions.

The specification explicitly discusses consent, data protection, and tool safety, while noting that protocol machinery alone cannot enforce all of those principles.

## Agent2Agent protocol

A2A provides an interoperability model for independent agent systems. The 1.0.0 specification includes agent cards, messages, tasks, parts, artifacts, and asynchronous interaction concepts. It supports collaboration without requiring access to another agent's internal state or implementation. [S16](16-sources-and-reading-guide.md#s16)

Its practical question is: **how can one system discover and delegate to another system through a common contract?**

MCP's practical question is usually: **how can an AI application access tools and context through a common interface?**

The distinction is helpful, but not absolute: an agent can be exposed behind a tool, and a remote agent may internally use MCP. Protocol choice does not determine the entire architecture.

## Identity is not the same as a capability description

An agent card or tool listing describes what a service claims it can do. It does not grant that service authority over our resources.

Before invoking a remote capability, establish:

- the intended service and its authenticated identity;
- the user's delegation and target scope;
- what data will leave the current boundary;
- the cost and side effects;
- cancellation and timeout behavior;
- how returned artifacts will be verified;
- what happens if the service asks for broader access.

A remote worker's request for a credential is not proof that the credential is necessary or authorized.

## Discoverability and progressive disclosure

A small, clearly described catalog is easier to use than a giant prompt containing every API.

One possible pattern:

1. Present concise capability descriptions.
2. Select relevant capabilities for the task.
3. Load precise schemas and guidance.
4. Apply policy before execution.
5. Return compact results with links to larger permitted artifacts.

Discovery must itself be permission-aware. Do not expose names or metadata that reveal another tenant's private resources.

## Choosing an integration

| Situation | Likely starting point |
|---|---|
| One application calling a stable internal function | Direct typed function |
| Multiple AI clients need the same tool/data surface | Consider MCP |
| Independent agent services exchange delegated work | Consider A2A |
| Reusable domain procedure within a compatible agent | Skill |
| Project-specific development guidance | Instruction file and linked documentation |
| Repeatable deterministic repository operation | Task runner or existing build command |

These are starting points, not mandatory layers. Do not add a protocol simply to appear more agentic.

## Integration acceptance checklist

Can the agent distinguish this tool from similar tools? Are invalid calls rejected explicitly? Can a human understand the side effect? Is the account correct? Does cancellation mean "request sent" or "operation stopped"? Can an old approval be reused accidentally? Are large outputs bounded? Is the tool's failure represented without a success-shaped fallback?

A strong interface makes these questions easy to answer.
