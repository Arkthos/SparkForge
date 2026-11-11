# Authorized knowledge and host integration contract

## Source-neutral publication scope

This document defines the interfaces of project-owned software and the
evidence needed for a future integration. It is not a platform-specific
operating recipe or a publication of private wiki content.

No real source identities, source revision pins, page identifiers,
endpoints, captures, execution journals or historical approval receipts
are supplied. Operators select authorized sources and handling at runtime.
Missing selection, permission, current comparison or host observations
remain `NOT_ASSESSED`; they must not be inferred from local paths, account
names or a package profile.

## Knowledge side

The implemented boundary accepts local indexed snapshots:

1. An explicit wiki root with `manifest.json`, exact source revision and
   indexed original UTF-8 pages.
2. An explicit repository root and inventory identifying an exact revision,
   safe relative paths and content hashes.
3. A bounded query, exact page/component identity or selected source paths.

The [knowledge adapter](../engineering/NATIVE_KNOWLEDGE.md) verifies bytes,
returns citations and exposes selection/truncation limits. It does not
retrieve a live source, establish ownership, grant disclosure rights,
execute acquired instructions or prove the index is authentic.
Only the selected scope is assessed; current coverage is `NOT_ASSESSED`.

The host must inspect relevant actual implementation and tests, not only
manifest descriptions, before making a semantic reuse judgment.
`wiki_context`, `catalog_context`, `component_context` and `source_context`
are complementary reads. The host keeps source provenance and applicable
permissions separate from the product spec's validity.

If a future live adapter is proposed, specify and verify its allowed
service/account, authentication route, read scope, paging/completeness,
revision binding, limits, retention and failure behavior independently.
Do not silently replace an unavailable source with a different provider or
an unrelated snapshot. This publication supplies no such live integration.

## Host side

The selected host must provide separately authorized capabilities for:

- loading the intended agent/skill from its actual relocated package;
- permitted source reads and local editing;
- presenting the exact proposed spec and receiving a genuine operator
  decision before implementation;
- executing the accepted command envelope and observing cancellation;
- arranging an actual independent review with a pre-inspection context;
- inspecting and reconciling interrupted processes/effects;
- retaining and presenting local evidence under approved data handling.

The package frontmatter adds no tools, MCP servers or privilege grants.
If a capability is missing, stop that stage. Installation, credential
switching, external writes and model trials are not implied remedies.

Use the [host record checker](../engineering/HOST_QUALIFICATION.md) to
check a proposal's shape and bindings, not to manufacture qualification.
It always reports host qualification and execution authorization false.
Authenticated decisions and live behavior must be established outside
that consistency checker.

## Independent packaging targets

Corp and Acro are user-requested independent deployment targets, not
interchangeable environments. The package builder makes only a local,
deterministic structural projection of the owned canonical package:

| Profile | Projection implemented by the builder |
|---|---|
| `corp` | Preserve canonical `plugin.json`; include `agency.json` declaring `engines: ["copilot"]` and `platforms: ["windows"]`. |
| `acro` | Add `engines: ["copilot"]` to `plugin.json`; omit `agency.json` from output. |

Both use the same owned agent, skill, references and helper scripts.
These are descriptions of this project's generated files, not a claim of
either platform's authoritative manifest requirements or acceptance.
The inventory says `validation_scope: STRUCTURAL_ONLY` and
`compatibility: NOT_ASSESSED`.

The builder copies a fixed resource list into a new output directory,
records deterministic hashes, validates that exact inventory and refuses
existing outputs or unsupported linked paths. It does not install,
register, invoke or publish the package. Operator-specific configuration,
source captures and runtime state are not package resources.

## End-to-end authority boundary

A real native task must traverse intake, authorized source/code
inspection, focused clarification, justified reuse, concrete spec,
STOP for the operator, host implementation, actual accepted-command
checks, independent review, bounded repair/recovery and local handoff.
Preview approval, synthetic citations and structural package checks
cannot bypass any stage.

Manual `decide` and `reconcile` are OPERATOR-OWNED. A reviewer captures
`review_context` before inspection and submits that same token, bound to
job ID, exact spec SHA, candidate SHA, check round and check-evidence
sequence. Changed evidence requires re-review, never relabeling.

The runner inherits caller environment and is not an OS sandbox.
Checked-file hashes do not constrain process side effects; storage probes
do not establish durable or confidential runtime storage. End with a
local evidence handoff and an inactive improvement proposal or no-change.
Human acceptance, installation and publication remain separate decisions.

## Minimal future qualification evidence

For each target independently, an authorized operator should record the
exact host/build/configuration, package digest, synthetic scenario, actual
decision ingress, observed check/review/recovery behavior, data handling
and remaining gaps. Preserve negative results and unknown effects.
Keep sensitive evidence outside Git and link it only where disclosure is
authorized.

No real host trial, original private source receipt, genuine human
acceptance or platform qualification is claimed by this document.
