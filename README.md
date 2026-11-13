# SparkForge

SparkForge turns ideas, existing code and knowledge into software components that fit an existing SPARK platform. Its target is a coordinated multi-agent factory with a platform-aware brain, an independent intent controller, coding/testing/review/diagnosis roles, bounded correction loops, durable recovery and human decisions when scope or authority materially changes.

**Current implementation:** an experimental assisted native Copilot agent/skill, verified local snapshot lookup, strict v1 specifications, SQLite job state, bounded real check execution and revision-bound review evidence. Pure coordinated intent/envelope contracts are implemented alongside v1; the coordinated execution loop remains **planned**. Neither corp nor acro has been deployment-qualified here.

## Start development here

1. Read [AGENTS.md](AGENTS.md) and the [current status](docs/PROJECT_STATUS.md).
2. Read the [target architecture](docs/design/ARCHITECTURE.md) and [milestone roadmap](docs/ROADMAP.md).
3. Follow the [Copilot handoff](docs/development/COPILOT_HANDOFF.md) for the next dependency-ready task. **WP-110** is the implemented first slice in the [detailed plan](docs/IMPLEMENTATION_PLAN.md#wp-110-define-intent-baseline-and-delegated-execution-envelope).
4. Track work in the [active backlog](docs/IMPLEMENTATION_BACKLOG.csv); use [acceptance scenarios](docs/engineering/ACCEPTANCE_MATRIX.csv) and the [first factory slice](docs/specs/FIRST_FACTORY_SLICE.md) to decide whether it works.

The [documentation index](docs/README.md) identifies the owner of each kind of fact. Historical planning and publication material is under [archive](docs/archive/README.md); it is not the active backlog.

## Repository map

| Path | Purpose |
|---|---|
| `plugins/sparkforge/` | Existing assisted package and deterministic helpers; future coordinated runtime goes here without silently replacing v1 |
| `tests/` | Executable synthetic unit, contract, integration and engineering-tool checks |
| `scripts/` | Package builder, self-check, plan validation, host/storage probes and review preparation |
| `docs/design/` | Target architecture, role/data contracts, decision policy and technical decisions |
| `docs/development/` | Copilot work loop, first task, migration map and continuation instructions |
| `docs/roles/` | Agent responsibilities, inputs, outputs and boundaries; design contracts, not installed agents |
| `docs/engineering/` | Validation, evaluation, operating guides and append-only evidence history |
| `research/` | Dated public-source foundations and prior art; evidence and inspiration, not runtime policy |
| `research_tools/` | Explicit-input acquisition, indexing, verification and checkpoint utilities |
| `.github/` | Copilot repository instructions, PR template and regression CI |

## Validate locally

Use Python 3.12+ for the complete engineering suite. Runtime v1 remains standard-library Python 3.10+. Install the declared research-only dependencies locally, not globally:

```bash
python -m pip install --target research_tools/.validation-deps -r research_tools/wiki/requirements.txt
```

Then on Linux/macOS:

```bash
PYTHONPATH=research_tools/.validation-deps python -B -m unittest discover -s tests
python -B scripts/validate_plan.py --base HEAD
git diff --check
```

On PowerShell:

```powershell
$env:PYTHONPATH = (Resolve-Path 'research_tools/.validation-deps').Path
python -B -m unittest discover -s tests
python -B scripts/validate_plan.py --base HEAD
git diff --check
```

For a native-only baseline: `python -B -m unittest discover -s tests -p 'test_native_*.py'`. Before a commit use `--base HEAD`; after a commit use `--base HEAD~` to validate the changed boundary. A clean-tree validation against HEAD does not validate the previous commit's lifecycle updates.

See [test strategy](docs/engineering/TEST_STRATEGY.md) for environment skips and evidence limits. The obsolete fictional browser preview and its Node checks have been retired; Node is no longer a project validation prerequisite.

## Boundaries

corp and acro are isolated target environments with independent credentials, source knowledge, journals and qualification. No live bridge is required or planned. Private source captures, credentials, runtime stores and raw model transcripts stay outside Git. A local passing check is not deployment acceptance. No public distribution license has been selected; do not invent one.
