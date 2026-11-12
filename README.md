# SparkForge

SparkForge is an experimental, native, spec-driven AI software factory for
turning ideas and existing content into new or improved SPARK components.
The host supplies the approved AI model and tools; SparkForge supplies the
workflow and small deterministic knowledge, specification and execution helpers.

The intended loop is:

**Idea and content -> authorized source/code inspection -> reuse/update/new
decision -> concrete specification -> human decision -> implementation ->
real checks -> independent review -> bounded repair -> reviewable delivery.**

## What is implemented

- One native agent and skill, with a complete operator-assisted workflow.
- Verified, bounded wiki/repository snapshot reads and implementation-file lookup.
- Strict specifications, exact-spec decision records and a separate local journal.
- Real subprocess checks with declared commands, output markers and finite limits.
- Candidate/check-context-bound review, revision invalidation and explicit recovery.
- Separate experimental `corp` and `acro` package metadata profiles.
- Synthetic tests, an engineering self-check harness and an older offline UX preview.

This is not an authenticated approval service, OS sandbox, autonomous publisher
or production-qualified deployment. Actual model-driven user acceptance, live
knowledge connectors, installed-host lifecycle and governed learning promotion
remain separate work. Corp and Acro are independent requested targets, not
inherited compatibility claims.

## Start here

Read the [native package guide](plugins/sparkforge/README.md) and
[operator workflow](docs/engineering/NATIVE_FACTORY.md), then use a small,
non-sensitive task inside an explicitly approved host/source/resource envelope.
The [source adapter guide](docs/engineering/NATIVE_KNOWLEDGE.md) explains the
external input formats. Missing current comparison remains `NOT_ASSESSED`.

The [offline preview](docs/engineering/USER_PREVIEW.md) is available at
`preview\index.html`. Its fictional catalog and deterministic templates are a
UX prototype, not an AI run or actual platform comparison.

## Development

Python 3.10+ and its standard library support the native factory helpers.
The separate research utilities use Python 3.12+ and the explicitly declared
Markdown/image packages. Git supports project checks; Node.js is needed only
for the preview tests. No research dependency is part of the native plugin.

For the native package alone:

```powershell
python -B -m unittest discover -s tests -p "test_native_*.py"
```

For the complete suite, first follow the scoped dependency instructions in
[research tools](research_tools/README.md), then:

```powershell
$env:PYTHONPATH = (Resolve-Path 'research_tools\.validation-deps').Path
python -B -m unittest discover -s tests
node --test tests\test_preview_model.cjs tests\test_preview_assets.cjs
python -B scripts\validate_plan.py --base HEAD
```

Build into a new owned output directory:

```powershell
python -B scripts\build_sparkforge_package.py --profile corp --output '<new-corp-output>'
python -B scripts\build_sparkforge_package.py --profile acro --output '<new-acro-output>'
```

Assembly is structural validation, not an installation or target qualification.
The builder refuses existing outputs. Runtime journals and generated packages
are not source files and are excluded from Git.

## Project and research

- [Current status](docs/PROJECT_STATUS.md), [roadmap](docs/ROADMAP.md) and
  [work backlog](docs/IMPLEMENTATION_BACKLOG.csv).
- [Requirements](docs/PRODUCT_REQUIREMENTS.md), [implementation plan](docs/IMPLEMENTATION_PLAN.md)
  and [native slice specification](docs/specs/NATIVE_FACTORY_SLICE.md).
- [Architecture](docs/design/ARCHITECTURE.md), [contracts](docs/design/CONTRACTS.md)
  and [decisions](docs/design/DECISIONS.md).
- [Validation history](docs/VALIDATION_HISTORY.md), [test strategy](docs/engineering/TEST_STRATEGY.md)
  and [planned acceptance scenarios](docs/engineering/ACCEPTANCE_MATRIX.csv).
- [Public research](research/README.md), [source provenance](docs/RESEARCH_PROVENANCE.md)
  and [governed learning](docs/research/SELF_IMPROVEMENT.md).
- [Publication scope](docs/delivery/GITHUB_PUBLICATION.md) and
  [contributor instructions](AGENTS.md).

The [corpus coverage ledger](docs/delivery/CORPUS_COVERAGE.md) distinguishes
complete application code, detailed public research, authored research tools
and local-only wiki/study review candidates. It does not label a condensed
reference or a mechanical redaction pass as the full published wiki.
All 19 inventoried research/checkpoint utility inputs are represented in
[the portable tooling edition](research_tools/README.md), with explicit
adaptation and test records rather than embedded private configuration.

## Publication boundary

This repository is a clean publication snapshot, not an upload of a
private workspace or its Git history. It contains project-owned software,
source-neutral project documentation, synthetic fixtures and reviewed public
research. Operator-private wiki/code captures, source-specific operating
material, runtime state, credentials, archives and raw transcripts are excluded.
The original working history is preserved separately, not rewritten.

**2026-11-12 publication hold:** GitHub now reports the repository as public,
whereas the earlier publication was private. The expanded detailed research
and authored tooling are committed locally at `13e15010ffc80546fc0cb8ef3ea58fbcc43c3886`;
the visibility guard stopped their push before any upload. The online branch
still points to `ef54878d1330e3d83089c87fcf799d2a88672a2e`.
An explicit audience decision is needed before publishing the new additions.

No private source is a test or installation dependency. Authorized private
knowledge can be supplied separately at runtime; it does not become repository
content. A private repository is not permission to add someone else's records.

No general distribution license has been selected. Upstream projects cited by
the research retain their own terms; references are not adopted dependencies.
