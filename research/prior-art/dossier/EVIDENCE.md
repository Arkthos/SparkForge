# Public source inspection register

**Historical reading:** 2026-11-05. **Publication edition:** 2026-11-12.

This register preserves all 90 inspection IDs and their inclusive, EOF-clipped
public source ranges across 88 files, including documentation, configurations,
skill contracts, selected implementation, and test-source reading. It adds no
new source inspection or execution claim. A recorded range is not exhaustive
semantic or security review; test-source inspection is not test execution.

Rendered from [public identity/range metadata](../sources.json) and
[public review notes](catalog-analysis.json). Source hashes and Git blob IDs
are retained historical bibliographic bindings, not source bytes rehashed by
this edition. The 136 originally captured source files are not redistributed.
Unregistered captures are not promoted to semantically reviewed material.

Upstream links identify exact revisions and ranges. There are no links to
absent local captures, private paths, raw transcripts, or images. For the
distinction between integrity and acceptance, read
[coverage and validation](COVERAGE_AND_VALIDATION.md).

## spec-kit-overview

**Candidate:** [spec-kit](CATALOG.md#spec-kit); **historical kind:** `documentation`.

**Original public path:** `README.md`.

**Pinned historical ranges:** [L1-L205](https://github.com/github/spec-kit/blob/ec9a6f3b94c0aa856f77e550785a1ddde1993de1/README.md#L1-L205).

**Historical source SHA-256:** `076c7ae6d7f58798a0c063ad398356bf64f1ce1002202b5f215a83d893c6fa29`.

**Historical Git blob:** `a4ea4f520add603de250c59f96037f0eb7be46e5`.

Selected candidate screening. Statements remain upstream documentation claims unless a separately registered mechanism supplies narrower implementation evidence.

## spec-kit-gate

**Candidate:** [spec-kit](CATALOG.md#spec-kit); **historical kind:** `implementation`.

**Original public path:** `src/specify_cli/workflows/step/gate/__init__.py`.

**Pinned historical ranges:** [L20-L215](https://github.com/github/spec-kit/blob/ec9a6f3b94c0aa856f77e550785a1ddde1993de1/src/specify_cli/workflows/step/gate/__init__.py#L20-L215).

**Historical source SHA-256:** `55da91c2d0cf0cfd674ae5af804e905d93dbed2ac6ea74da84ccbda4dc035474`.

**Historical Git blob:** `b20e26d18c0ddcf6cf1fd10d5ff83afdc8dbe318`.

Configured verdicts, non-TTY pause, invalid-input failures, and abort/retry/skip semantics. These mechanisms do not authenticate caller-supplied human consent.

## spec-kit-state

**Candidate:** [spec-kit](CATALOG.md#spec-kit); **historical kind:** `implementation`.

**Original public path:** `src/specify_cli/workflows/engine.py`.

**Pinned historical ranges:** [L630-L695](https://github.com/github/spec-kit/blob/ec9a6f3b94c0aa856f77e550785a1ddde1993de1/src/specify_cli/workflows/engine.py#L630-L695), [L808-L895](https://github.com/github/spec-kit/blob/ec9a6f3b94c0aa856f77e550785a1ddde1993de1/src/specify_cli/workflows/engine.py#L808-L895).

**Historical source SHA-256:** `286252739c4f51e9eab5869cc4d5d6f1a25c1914a72021984ba97a961d7cae7b`.

**Historical Git blob:** `7cd85c091aa63514ddd3240c827f826c5c65c44f`.

Run identity validation and atomic per-file persistence, including failure poisoning; not a whole-engine or external-effect transaction audit.

## spec-kit-offline

**Candidate:** [spec-kit](CATALOG.md#spec-kit); **historical kind:** `documentation`.

**Original public path:** `docs/install/air-gapped.md`.

**Pinned historical ranges:** [L1-L94](https://github.com/github/spec-kit/blob/ec9a6f3b94c0aa856f77e550785a1ddde1993de1/docs/install/air-gapped.md#L1-L94).

**Historical source SHA-256:** `c33d314743a1242a3165b632865a1525dfd137269c70d56019e596ce13a134b2`.

**Historical Git blob:** `81505e640bd455913b512291588cc09658407dc3`.

OS/Python-specific dependency bundles, PowerShell requirements, and component-specific catalog/archive and offline limits.

## openspec-overview

**Candidate:** [openspec](CATALOG.md#openspec); **historical kind:** `documentation`.

**Original public path:** `README.md`.

**Pinned historical ranges:** [L1-L205](https://github.com/Fission-AI/OpenSpec/blob/3e4d5f0769e2857c8eb54f149cbf5e4f703fa04c/README.md#L1-L205).

**Historical source SHA-256:** `e19ee7362ad043eeff0d3d1f1f0e5bf1ae195f4b34aa28e0107eae5eeaaad446`.

**Historical Git blob:** `7b8da04ac27fb1fa5a9578303873559e0c1b6ad2`.

Selected candidate screening. Statements remain upstream documentation claims unless a separately registered mechanism supplies narrower implementation evidence.

## openspec-artifacts

**Candidate:** [openspec](CATALOG.md#openspec); **historical kind:** `implementation`.

**Original public path:** `src/core/artifact-graph/types.ts`.

**Pinned historical ranges:** [L1-L79](https://github.com/Fission-AI/OpenSpec/blob/3e4d5f0769e2857c8eb54f149cbf5e4f703fa04c/src/core/artifact-graph/types.ts#L1-L79).

**Historical source SHA-256:** `922b4b13b5f86994312e9e737b966046a6b9149b086eb5b7cf5014d4efad8970`.

**Historical Git blob:** `9e281ad074e507d351efbe6c14bac53209005052`.

Relative-path constraints for Windows/POSIX forms, bounded artifact declarations, and apply prerequisites.

## openspec-validation

**Candidate:** [openspec](CATALOG.md#openspec); **historical kind:** `implementation`.

**Original public path:** `src/core/artifact-graph/schema.ts`.

**Pinned historical ranges:** [L1-L120](https://github.com/Fission-AI/OpenSpec/blob/3e4d5f0769e2857c8eb54f149cbf5e4f703fa04c/src/core/artifact-graph/schema.ts#L1-L120).

**Historical source SHA-256:** `29b22548191348feab826b8a08217cb051b20dba497f791686c9e168f2e5e04d`.

**Historical Git blob:** `ebaff3bcf40d3a552d53e6271094a5caf50658d6`.

Schema parsing, duplicate IDs, dependency references/cycles, and the distinction between structural validity and semantic acceptance.

## spec-kitty-overview

**Candidate:** [spec-kitty](CATALOG.md#spec-kitty); **historical kind:** `documentation`.

**Original public path:** `README.md`.

**Pinned historical ranges:** [L1-L160](https://github.com/spec-kitty/spec-kitty/blob/d7f91f37542c68d7ba019a3d22d5f5edec3e96f0/README.md#L1-L160).

**Historical source SHA-256:** `564e4a15c43ff31e42f3b2799368f038443c9362519fc95710b7460942bd38a3`.

**Historical Git blob:** `95a847bf3eff0e8385ad0f007877d2f281da2235`.

Selected candidate screening. Statements remain upstream documentation claims unless a separately registered mechanism supplies narrower implementation evidence.

## bmad-method-overview

**Candidate:** [bmad-method](CATALOG.md#bmad-method); **historical kind:** `documentation`.

**Original public path:** `README.md`.

**Pinned historical ranges:** [L1-L125](https://github.com/bmad-code-org/BMAD-METHOD/blob/022be9314e4facd16826104a9f8033e1c5ed4fdc/README.md#L1-L125).

**Historical source SHA-256:** `7547d18b57a7004a057ace1b03dd10394bd6f687f4174172b73d7d7cf5687d5a`.

**Historical Git blob:** `bd9fbb40ccb25207194dc9ed88b24134f4ae3d0c`.

Selected candidate screening. Statements remain upstream documentation claims unless a separately registered mechanism supplies narrower implementation evidence.

## bmad-builder-overview

**Candidate:** [bmad-builder](CATALOG.md#bmad-builder); **historical kind:** `documentation`.

**Original public path:** `README.md`.

**Pinned historical ranges:** [L1-L75](https://github.com/bmad-code-org/bmad-builder/blob/d4a921c49db71ad09c2dc62b8e62266b1f26ca4f/README.md#L1-L75).

**Historical source SHA-256:** `566f6efdab4af36e090c81e06907e242cddceb51df7d9e0eee58e6de7769b9ec`.

**Historical Git blob:** `da02ee81e3c73b140ed46657a9541ff9f1a708cd`.

Selected candidate screening. Statements remain upstream documentation claims unless a separately registered mechanism supplies narrower implementation evidence.

## bmad-tea-overview

**Candidate:** [bmad-tea](CATALOG.md#bmad-tea); **historical kind:** `documentation`.

**Original public path:** `README.md`.

**Pinned historical ranges:** [L1-L164](https://github.com/bmad-code-org/bmad-method-test-architecture-enterprise/blob/a2819f62fc1b56486d223895eaa50578b490f2f5/README.md#L1-L164).

**Historical source SHA-256:** `8d57dfc761d2c8ae3c3fd9f8cd86193c6c2909adaed8b312899c9d84390434c5`.

**Historical Git blob:** `694e834f811e121a3390e59af2a35e0703633e93`.

Selected candidate screening. Statements remain upstream documentation claims unless a separately registered mechanism supplies narrower implementation evidence.

## tea-trace

**Candidate:** [bmad-tea](CATALOG.md#bmad-tea); **historical kind:** `skill-contract`.

**Original public path:** `skills/bmad-tea-trace/SKILL.md`.

**Pinned historical ranges:** [L1-L94](https://github.com/bmad-code-org/bmad-method-test-architecture-enterprise/blob/a2819f62fc1b56486d223895eaa50578b490f2f5/skills/bmad-tea-trace/SKILL.md#L1-L94).

**Historical source SHA-256:** `702df8170d83c2993b334c05d5d1c3078c36f7a66af0df823b11d26af7504529`.

**Historical Git blob:** `74a322c0c3390aa05cfc0cb54be9cdb2e84eca29`.

Traceability, scope-bound outputs, required sibling knowledge, and formal versus optionally synthetic oracles.

## bmad-loop-overview

**Candidate:** [bmad-loop](CATALOG.md#bmad-loop); **historical kind:** `documentation`.

**Original public path:** `README.md`.

**Pinned historical ranges:** [L1-L175](https://github.com/bmad-code-org/bmad-loop/blob/49eb8a3f15b1cab9758948b5b341516de9c044df/README.md#L1-L175).

**Historical source SHA-256:** `cd3662535f89659b6ea7c9b3fcf12c4655eecf7622141406f1d300a9529e9981`.

**Historical Git blob:** `92fc0e4c5557a4e440bca643d7098a0d89802f85`.

Selected candidate screening. Statements remain upstream documentation claims unless a separately registered mechanism supplies narrower implementation evidence.

## bmad-loop-permissions

**Candidate:** [bmad-loop](CATALOG.md#bmad-loop); **historical kind:** `implementation`.

**Original public path:** `src/bmad_loop/adapters/profile.py`.

**Pinned historical ranges:** [L461-L525](https://github.com/bmad-code-org/bmad-loop/blob/49eb8a3f15b1cab9758948b5b341516de9c044df/src/bmad_loop/adapters/profile.py#L461-L525).

**Historical source SHA-256:** `c23cd353c11db5416a44bda8c067941cbba24e7d6cf06faf808bffd376bf22e2`.

**Historical Git blob:** `28e4437438a41e2653de0a5686263b8fd3d302ae`.

Non-bypass mapping, platform rejection, and exact replacement of launch permission arguments.

## bmad-loop-copilot

**Candidate:** [bmad-loop](CATALOG.md#bmad-loop); **historical kind:** `configuration`.

**Original public path:** `src/bmad_loop/data/profiles/copilot.toml`.

**Pinned historical ranges:** [L1-L60](https://github.com/bmad-code-org/bmad-loop/blob/49eb8a3f15b1cab9758948b5b341516de9c044df/src/bmad_loop/data/profiles/copilot.toml#L1-L60).

**Historical source SHA-256:** `e524f91cb99d90ba3e60fa265e6806c507eec4f7d04fd6a9fff74ee15f9916d6`.

**Historical Git blob:** `4a287ab7517226cb36441ade4cfbda24d7aad4a0`.

Broad bypass flags, version/OS-specific hook assumptions, main-session attribution, and usage-record grace.

## bmad-loop-policy

**Candidate:** [bmad-loop](CATALOG.md#bmad-loop); **historical kind:** `documentation`.

**Original public path:** `docs/reference/configuration.md`.

**Pinned historical ranges:** [L1-L125](https://github.com/bmad-code-org/bmad-loop/blob/49eb8a3f15b1cab9758948b5b341516de9c044df/docs/reference/configuration.md#L1-L125).

**Historical source SHA-256:** `adac227ff3199e7ba43fe9b7033a07607e30f4b74435d9dc4add99bfc99b809c`.

**Historical Git blob:** `e6b772cfc4c8d8b20c19f3a2447d41baaec442a9`.

Gate/review defaults, advisory versus enforced budgets, configured verification commands, and pause/resume policy.

## bmad-loop-transport

**Candidate:** [bmad-loop](CATALOG.md#bmad-loop); **historical kind:** `documentation`.

**Original public path:** `docs/adapter-authoring-guide.md`.

**Pinned historical ranges:** [L1-L120](https://github.com/bmad-code-org/bmad-loop/blob/49eb8a3f15b1cab9758948b5b341516de9c044df/docs/adapter-authoring-guide.md#L1-L120).

**Historical source SHA-256:** `bf84eaa960f51002370bca8e27692ed88353407dd8753bd5a2290a9b7f08e1f8`.

**Historical Git blob:** `513bc689ffb3aaba163469c263fc545b9a09c8ec`.

Separate coding-CLI and multiplexer contracts; observed effects and unknown liveness must be reported honestly.

## superpowers-overview

**Candidate:** [superpowers](CATALOG.md#superpowers); **historical kind:** `documentation`.

**Original public path:** `README.md`.

**Pinned historical ranges:** [L1-L195](https://github.com/obra/superpowers/blob/22f0b463e7a5e579904dd6211a520321035526f7/README.md#L1-L195).

**Historical source SHA-256:** `79f29f50c735862d2e304ea547b4c9aa67d9db6909ff6fb7b5ea922d7bcbc3e7`.

**Historical Git blob:** `c5bb59fdaf17ba154e803c549cd71a73ef36c24b`.

Selected candidate screening. Statements remain upstream documentation claims unless a separately registered mechanism supplies narrower implementation evidence.

## superpowers-intake

**Candidate:** [superpowers](CATALOG.md#superpowers); **historical kind:** `skill-contract`.

**Original public path:** `skills/brainstorming/SKILL.md`.

**Pinned historical ranges:** [L1-L125](https://github.com/obra/superpowers/blob/22f0b463e7a5e579904dd6211a520321035526f7/skills/brainstorming/SKILL.md#L1-L125).

**Historical source SHA-256:** `2c9ca71f94886f9ca9f4aef055f7cafb3e1a9bdf3aeebf8f4cb547c69405d207`.

**Historical Git blob:** `9eb0edc7fedf26e1d3e2f3f223e5bcc5058aed6a`.

Read context before asking, compare approaches, and obtain the required design decision.

## superpowers-tdd

**Candidate:** [superpowers](CATALOG.md#superpowers); **historical kind:** `skill-contract`.

**Original public path:** `skills/test-driven-development/SKILL.md`.

**Pinned historical ranges:** [L1-L120](https://github.com/obra/superpowers/blob/22f0b463e7a5e579904dd6211a520321035526f7/skills/test-driven-development/SKILL.md#L1-L120).

**Historical source SHA-256:** `64b03fce4aee5a97a93160cea8111f3ba13a17b7c001db4bd5836d67fd10705d`.

**Historical Git blob:** `46838cc9e893c06259e3bdad0fc2425b36242f15`.

Observe a meaningful failing test; blanket delete-first policy is not appropriate for legitimate existing work.

## superpowers-verification

**Candidate:** [superpowers](CATALOG.md#superpowers); **historical kind:** `skill-contract`.

**Original public path:** `skills/verification-before-completion/SKILL.md`.

**Pinned historical ranges:** [L1-L120](https://github.com/obra/superpowers/blob/22f0b463e7a5e579904dd6211a520321035526f7/skills/verification-before-completion/SKILL.md#L1-L120).

**Historical source SHA-256:** `2befe7fc55bcadaa3d97dd9e8efeb633d2561c0ebe74c5a8b17c4d9e7e4520b3`.

**Historical Git blob:** `7d45333cc4a49c57a80df6c1fe2fa777a207afbc`.

Fresh actual evidence before completion claims; a procedural contract rather than runtime enforcement.

## superpowers-workers

**Candidate:** [superpowers](CATALOG.md#superpowers); **historical kind:** `skill-contract`.

**Original public path:** `skills/subagent-driven-development/SKILL.md`.

**Pinned historical ranges:** [L1-L115](https://github.com/obra/superpowers/blob/22f0b463e7a5e579904dd6211a520321035526f7/skills/subagent-driven-development/SKILL.md#L1-L115).

**Historical source SHA-256:** `1baf70e307bde682c462513c86116333f1f066168c6710f45145bf5f0b00828d`.

**Historical Git blob:** `45195787cb3f5d141af203e2fdc12f158be14522`.

Fresh worker context, specification/quality review, persistent ledgers, and autonomy/cleanup rules requiring adaptation.

## addy-skills-overview

**Candidate:** [addy-skills](CATALOG.md#addy-skills); **historical kind:** `documentation`.

**Original public path:** `README.md`.

**Pinned historical ranges:** [L1-L175](https://github.com/addyosmani/agent-skills/blob/301b02b12bff98e4688e6984af6556802322bbde/README.md#L1-L175).

**Historical source SHA-256:** `b74ab722eeee706ff1c5c3ee55f5f2328368ec28c6368900bc80b857b5bc6b72`.

**Historical Git blob:** `7f610b8ca80ff9bc7ba7f95f3209430c3481891d`.

Selected candidate screening. Statements remain upstream documentation claims unless a separately registered mechanism supplies narrower implementation evidence.

## addy-intake

**Candidate:** [addy-skills](CATALOG.md#addy-skills); **historical kind:** `skill-contract`.

**Original public path:** `skills/interview-me/SKILL.md`.

**Pinned historical ranges:** [L1-L145](https://github.com/addyosmani/agent-skills/blob/301b02b12bff98e4688e6984af6556802322bbde/skills/interview-me/SKILL.md#L1-L145).

**Historical source SHA-256:** `ace4b675999bb504593d572e0f73f3d7e803ad6fddf318445598c82c11939db2`.

**Historical Git blob:** `200f9186ffa234708aa5deec1946c6dfcb7a7335`.

Focused questions, intent and non-goals, responsive-user confirmation, and the limits of heuristic confidence percentages.

## addy-copilot

**Candidate:** [addy-skills](CATALOG.md#addy-skills); **historical kind:** `documentation`.

**Original public path:** `docs/copilot-cli-setup.md`.

**Pinned historical ranges:** [L1-L64](https://github.com/addyosmani/agent-skills/blob/301b02b12bff98e4688e6984af6556802322bbde/docs/copilot-cli-setup.md#L1-L64).

**Historical source SHA-256:** `e624f0bff64f42b3a8034c7cba5e8a1907da81ad1e6f9ba3b6f9bcd5544993ec`.

**Historical Git blob:** `0abed10f61e49193d6fb9fc7b5597311240cfe32`.

Manifest precedence, discovered Copilot skills versus absent Claude lifecycle commands, and shared-reference portability.

## rsc-harness-overview

**Candidate:** [rsc-harness](CATALOG.md#rsc-harness); **historical kind:** `documentation`.

**Original public path:** `README.md`.

**Pinned historical ranges:** [L1-L125](https://github.com/ericrisco/rsc-harness/blob/726aaf3ba87c584329fc821f243a7ce5e62450fd/README.md#L1-L125).

**Historical source SHA-256:** `015c1e1d9baf09dec82cfe84627d7d388f7253188faec04fbc51294b8a145624`.

**Historical Git blob:** `e84ad353c44dbe4197b7ab3a118ddedd0592ee79`.

Selected candidate screening. Statements remain upstream documentation claims unless a separately registered mechanism supplies narrower implementation evidence.

## rsc-acceptance

**Candidate:** [rsc-harness](CATALOG.md#rsc-harness); **historical kind:** `implementation`.

**Original public path:** `scripts/lib/onboarding-apply.js`.

**Pinned historical ranges:** [L205-L315](https://github.com/ericrisco/rsc-harness/blob/726aaf3ba87c584329fc821f243a7ce5e62450fd/scripts/lib/onboarding-apply.js#L205-L315).

**Historical source SHA-256:** `979f64feb9d33e2929289b4241de5e4161b3f5feebec47621f5bedafcac55e64`.

**Historical Git blob:** `92f106fa93290d2f026726e76cf96b4fbf42c818`.

Governed artifact inventory/digests, exact plan identity, receipts, backups, and provenance; content binding is not authenticated consent.

## rsc-acceptance-tests

**Candidate:** [rsc-harness](CATALOG.md#rsc-harness); **historical kind:** `test-source`.

**Original public path:** `tests/onboarding-cli.test.js`.

**Pinned historical ranges:** [L40-L135](https://github.com/ericrisco/rsc-harness/blob/726aaf3ba87c584329fc821f243a7ce5e62450fd/tests/onboarding-cli.test.js#L40-L135).

**Historical source SHA-256:** `45dee76595f3e975e0056020f8d85930431af7b390836c31bff22a252cc58321`.

**Historical Git blob:** `6435eb82fa10d0c8bd50012c5549b349fe5d213f`.

Assertions for no-write preview, wrong-plan rejection, and receipt persistence; source reading, not executed tests.

## rsc-host-surfaces

**Candidate:** [rsc-harness](CATALOG.md#rsc-harness); **historical kind:** `documentation`.

**Original public path:** `README.md`.

**Pinned historical ranges:** [L349-L405](https://github.com/ericrisco/rsc-harness/blob/726aaf3ba87c584329fc821f243a7ce5e62450fd/README.md#L349-L405).

**Historical source SHA-256:** `015c1e1d9baf09dec82cfe84627d7d388f7253188faec04fbc51294b8a145624`.

**Historical Git blob:** `e84ad353c44dbe4197b7ab3a118ddedd0592ee79`.

Different assistant output surfaces and explicitly unsupported Copilot session memory.

## agent-os-overview

**Candidate:** [agent-os](CATALOG.md#agent-os); **historical kind:** `documentation`.

**Original public path:** `README.md`.

**Pinned historical ranges:** [L1-L41](https://github.com/buildermethods/agent-os/blob/e892e61d322759165e7d9173e92c1010406c9f4d/README.md#L1-L41).

**Historical source SHA-256:** `e02b640d2f1eb40d06ead692329b85be0f078bf1dd02b367c3931fda531e7fe0`.

**Historical Git blob:** `78e2756db5055ef039a6f94053e55187dc55fec1`.

Selected candidate screening. Statements remain upstream documentation claims unless a separately registered mechanism supplies narrower implementation evidence.

## sssf-overview

**Candidate:** [sssf](CATALOG.md#sssf); **historical kind:** `documentation`.

**Original public path:** `README.md`.

**Pinned historical ranges:** [L1-L210](https://github.com/disler/super-simple-software-factory/blob/de31374882e7a4e3e5b7bb9bd09e69dc2f779356/README.md#L1-L210).

**Historical source SHA-256:** `671478e3b20e7d0e5ff15b64cdfbd87117d4972dc02537888c5852b2e793b169`.

**Historical Git blob:** `0e73560581ac9cb01f6e7f92417ad182aa31f8f8`.

Selected candidate screening. Statements remain upstream documentation claims unless a separately registered mechanism supplies narrower implementation evidence.

## sssf-run-acceptance

**Candidate:** [sssf](CATALOG.md#sssf); **historical kind:** `implementation`.

**Original public path:** `.claude/skills/sssf/templates/adws/adw_modules/runner.py`.

**Pinned historical ranges:** [L1-L142](https://github.com/disler/super-simple-software-factory/blob/de31374882e7a4e3e5b7bb9bd09e69dc2f779356/.claude/skills/sssf/templates/adws/adw_modules/runner.py#L1-L142).

**Historical source SHA-256:** `b14af2d15d809747a678e2633af95b1b846d1bb010fc4646b8a9b5574b29e35f`.

**Historical Git blob:** `86bf2b30797f6e66e0aaf5fd02835a02dbd7b0f3`.

Phase completion versus whole-run acceptance, nonempty successful phases, and consistent status/exit reporting.

## sssf-agent-calls

**Candidate:** [sssf](CATALOG.md#sssf); **historical kind:** `implementation`.

**Original public path:** `.claude/skills/sssf/templates/adws/adw_modules/agents.py`.

**Pinned historical ranges:** [L1-L300](https://github.com/disler/super-simple-software-factory/blob/de31374882e7a4e3e5b7bb9bd09e69dc2f779356/.claude/skills/sssf/templates/adws/adw_modules/agents.py#L1-L300).

**Historical source SHA-256:** `a69f25115afe1eabb3702005469d18882b9c27a5a7ea705d7be26be797525eea`.

**Historical Git blob:** `7c9adb8ca41204c46ca74e673c9fa155144cb7e4`.

Pi-only backend validation, typed envelopes, bounded corrections, accumulated usage, and post-call write checking.

## sssf-tracing

**Candidate:** [sssf](CATALOG.md#sssf); **historical kind:** `implementation`.

**Original public path:** `.claude/skills/sssf/templates/adws/adw_modules/tracer.py`.

**Pinned historical ranges:** [L1-L130](https://github.com/disler/super-simple-software-factory/blob/de31374882e7a4e3e5b7bb9bd09e69dc2f779356/.claude/skills/sssf/templates/adws/adw_modules/tracer.py#L1-L130).

**Historical source SHA-256:** `f35a034f89d8d6c416fbe6ccc3ad59593e1b892736fce80429705d9b72f328e3`.

**Historical Git blob:** `54eb6385edbcfb0470fdab5fed93edd61b136040`.

Trace schemas, run/phase identities, JSONL append, SQLite mirror, and process-ownership fields; not tamper-proof audit storage.

## sssf-git

**Candidate:** [sssf](CATALOG.md#sssf); **historical kind:** `implementation`.

**Original public path:** `.claude/skills/sssf/templates/adws/adw_modules/git_helper.py`.

**Pinned historical ranges:** [L1-L120](https://github.com/disler/super-simple-software-factory/blob/de31374882e7a4e3e5b7bb9bd09e69dc2f779356/.claude/skills/sssf/templates/adws/adw_modules/git_helper.py#L1-L120).

**Historical source SHA-256:** `ea3e5fa959c37bc258e4ded8f3bae53ca7a13ed2a64355202bf6765924c062d7`.

**Historical Git blob:** `368d633493dd6d8f76ae177378d04b3aa986a31d`.

Repository-root discovery and broad git add -A behavior that should not be copied blindly.

## attractor-overview

**Candidate:** [attractor](CATALOG.md#attractor); **historical kind:** `documentation`.

**Original public path:** `README.md`.

**Pinned historical ranges:** [L1-L23](https://github.com/strongdm/attractor/blob/fb57a55ed97372a27ac90102f436947e29f48426/README.md#L1-L23).

**Historical source SHA-256:** `0b5f8d1b8ed4db6bec9060bb6b39dddbd38dec06a6958cd24f2dba4773068773`.

**Historical Git blob:** `f6db0fb68dffdd8f5ba850ed4a9019f3418a9566`.

Selected candidate screening. Statements remain upstream documentation claims unless a separately registered mechanism supplies narrower implementation evidence.

## attractor-design

**Candidate:** [attractor](CATALOG.md#attractor); **historical kind:** `specification`.

**Original public path:** `attractor-spec.md`.

**Pinned historical ranges:** [L1-L110](https://github.com/strongdm/attractor/blob/fb57a55ed97372a27ac90102f436947e29f48426/attractor-spec.md#L1-L110).

**Historical source SHA-256:** `235354496e2bc35cba9822cded2ebd71ff35a8fb7fce4e51f52b2788586e92ec`.

**Historical Git blob:** `aaaa969f0d5c1144b5c3b30b389e5fb6c588e53a`.

Declared graph, handlers, state, human nodes, backend and presentation separation; specification, not implemented behavior.

## fabro-overview

**Candidate:** [fabro](CATALOG.md#fabro); **historical kind:** `documentation`.

**Original public path:** `README.md`.

**Pinned historical ranges:** [L1-L185](https://github.com/fabro-sh/fabro/blob/1f5da01b47eeccb43b6b3bc79fe9cc455882a100/README.md#L1-L185).

**Historical source SHA-256:** `5a84078fc0b121be81c1cfc538c1dac92000c78bbe93cf8385e493140ab2705d`.

**Historical Git blob:** `73a1e4ffc68a65abde36a4421600a86520b1395f`.

Selected candidate screening. Statements remain upstream documentation claims unless a separately registered mechanism supplies narrower implementation evidence.

## roast-overview

**Candidate:** [roast](CATALOG.md#roast); **historical kind:** `documentation`.

**Original public path:** `README.md`.

**Pinned historical ranges:** [L1-L200](https://github.com/Shopify/roast/blob/93b2f5c99982bd3e8df426fa09da02a64a454263/README.md#L1-L200).

**Historical source SHA-256:** `efb9ff53ef1e0d250955476484e80dd6d8b5a24b9b529ac1cd43e54c7c0786b3`.

**Historical Git blob:** `b6e2ed6a10ec8901609e121f1cb13c184888e2e1`.

Selected candidate screening. Statements remain upstream documentation claims unless a separately registered mechanism supplies narrower implementation evidence.

## deepagents-overview

**Candidate:** [deepagents](CATALOG.md#deepagents); **historical kind:** `documentation`.

**Original public path:** `README.md`.

**Pinned historical ranges:** [L1-L115](https://github.com/langchain-ai/deepagents/blob/6cd647ba201d4612aeaa2d49d9588bd6e46ce250/README.md#L1-L115).

**Historical source SHA-256:** `738b16b9e3451b3e51f2818baa8e5c752960495b938c2b3ed4011c816fe9718d`.

**Historical Git blob:** `22c546cffc2365f7c97c2781aadb1b74eb28d2c3`.

Selected candidate screening. Statements remain upstream documentation claims unless a separately registered mechanism supplies narrower implementation evidence.

## openhands-sdk-overview

**Candidate:** [openhands-sdk](CATALOG.md#openhands-sdk); **historical kind:** `documentation`.

**Original public path:** `README.md`.

**Pinned historical ranges:** [L1-L180](https://github.com/OpenHands/software-agent-sdk/blob/2b4d980b6a54ef6685e4337e7643c40ec24be1bb/README.md#L1-L180).

**Historical source SHA-256:** `95094c9745c7cc58136d4eaa1688fb6038aafefec2be05344293f6df7e55dbf8`.

**Historical Git blob:** `386dc8945133cb51969192b0b29c8396719cbff6`.

Selected candidate screening. Statements remain upstream documentation claims unless a separately registered mechanism supplies narrower implementation evidence.

## mini-swe-agent-overview

**Candidate:** [mini-swe-agent](CATALOG.md#mini-swe-agent); **historical kind:** `documentation`.

**Original public path:** `README.md`.

**Pinned historical ranges:** [L1-L155](https://github.com/SWE-agent/mini-swe-agent/blob/04d809ceab9df28f9adaed044884180159172930/README.md#L1-L155).

**Historical source SHA-256:** `9982d90b7566f2f3fa5e9811b475d5e8e2a84e2df80cf3f1e4be6e820b129835`.

**Historical Git blob:** `7db1d82dfa92eaa00adeb10c8681677a9e6ec639`.

Selected candidate screening. Statements remain upstream documentation claims unless a separately registered mechanism supplies narrower implementation evidence.

## copilot-sdk-overview

**Candidate:** [copilot-sdk](CATALOG.md#copilot-sdk); **historical kind:** `documentation`.

**Original public path:** `README.md`.

**Pinned historical ranges:** [L1-L170](https://github.com/github/copilot-sdk/blob/c072001600018fe166910cfcb6eb42e769b9209d/README.md#L1-L170).

**Historical source SHA-256:** `096fa46c7ec63d4c92323566dbc3babce5f3b431ae063a2b96eecbcb27f5b9bb`.

**Historical Git blob:** `4420f13a1d91b9b172cdc9081798832f74dc36c4`.

Selected candidate screening. Statements remain upstream documentation claims unless a separately registered mechanism supplies narrower implementation evidence.

## sdk-local-cli

**Candidate:** [copilot-sdk](CATALOG.md#copilot-sdk); **historical kind:** `documentation`.

**Original public path:** `docs/setup/local-cli.md`.

**Pinned historical ranges:** [L1-L150](https://github.com/github/copilot-sdk/blob/c072001600018fe166910cfcb6eb42e769b9209d/docs/setup/local-cli.md#L1-L150).

**Historical source SHA-256:** `b1bf97295f46958812ee259fccdef147770ffa49607bb02d4682e0082bcd60ed`.

**Historical Git blob:** `f383e35ba31c99b10a4686bd867451e000706c5d`.

Explicit runtime connection and caller responsibility for custom CLI compatibility; bundled defaults differ by SDK.

## sdk-pretool

**Candidate:** [copilot-sdk](CATALOG.md#copilot-sdk); **historical kind:** `documentation`.

**Original public path:** `docs/hooks/pre-tool-use.md`.

**Pinned historical ranges:** [L1-L105](https://github.com/github/copilot-sdk/blob/c072001600018fe166910cfcb6eb42e769b9209d/docs/hooks/pre-tool-use.md#L1-L105).

**Historical source SHA-256:** `a1928a3db7a0097817676052f51e42ba371996b573387be3f8e12bea03a4ef8c`.

**Historical Git blob:** `cfcee3c568fb8cb61c0eb93d2b63751817960a14`.

Documented pre-execution approval/denial and language-specific hook interfaces; not proof of complete host enforcement.

## gh-aw-overview

**Candidate:** [gh-aw](CATALOG.md#gh-aw); **historical kind:** `documentation`.

**Original public path:** `README.md`.

**Pinned historical ranges:** [L1-L88](https://github.com/github/gh-aw/blob/0aa2738ed88dea9f3f0e400381dde0f102efafd4/README.md#L1-L88).

**Historical source SHA-256:** `2df16c5f3ae9282f0dfd717b9dacd47a84d74964705786a8e93c7e93f6f36bfa`.

**Historical Git blob:** `4e0667b04eb87108ea18aa995aecc7c108c61d91`.

Selected candidate screening. Statements remain upstream documentation claims unless a separately registered mechanism supplies narrower implementation evidence.

## eve-foreman-overview

**Candidate:** [eve-foreman](CATALOG.md#eve-foreman); **historical kind:** `documentation`.

**Original public path:** `README.md`.

**Pinned historical ranges:** [L1-L75](https://github.com/vercel-labs/eve-software-factory-template/blob/6bc5febab95de4c05fa08b164f544650f6aa11aa/README.md#L1-L75).

**Historical source SHA-256:** `0956fe7db06c3cfa35fd3ec25066a84d5f1dc3aa4bdf8dee541efbd40eb82f84`.

**Historical Git blob:** `b64f7688cf2d6fea1bac1989af367a5fcb397fe2`.

Selected candidate screening. Statements remain upstream documentation claims unless a separately registered mechanism supplies narrower implementation evidence.

## eve-pipeline-instructions

**Candidate:** [eve-foreman](CATALOG.md#eve-foreman); **historical kind:** `instruction-in-source`.

**Original public path:** `agent/instructions.ts`.

**Pinned historical ranges:** [L1-L91](https://github.com/vercel-labs/eve-software-factory-template/blob/6bc5febab95de4c05fa08b164f544650f6aa11aa/agent/instructions.ts#L1-L91).

**Historical source SHA-256:** `8528ee750bad5bcaccc68d9a3781a041562fa1bbf3520bc459b952d26f84753d`.

**Historical Git blob:** `dd23a6d973fb4671ff5c9a357ee03a59b9134492`.

Station order, clarification, self-contained handoffs, bounded rework, and draft delivery are expressed in the orchestrator prompt.

## eve-sandbox

**Candidate:** [eve-foreman](CATALOG.md#eve-foreman); **historical kind:** `implementation`.

**Original public path:** `agent/sandbox.ts`.

**Pinned historical ranges:** [L1-L39](https://github.com/vercel-labs/eve-software-factory-template/blob/6bc5febab95de4c05fa08b164f544650f6aa11aa/agent/sandbox.ts#L1-L39).

**Historical source SHA-256:** `7bca4fa11ccf57bd8e6078f56d08680d420330acf5d42306f779b597e4a6ff0d`.

**Historical Git blob:** `87efbb8efbff61dc333653bcf02d92bebf2c76de`.

Hosted Vercel Sandbox is selected in local development as well as production.

## eve-review-wrapper

**Candidate:** [eve-foreman](CATALOG.md#eve-foreman); **historical kind:** `implementation`.

**Original public path:** `agent/tools/run_reviewer.ts`.

**Pinned historical ranges:** [L1-L34](https://github.com/vercel-labs/eve-software-factory-template/blob/6bc5febab95de4c05fa08b164f544650f6aa11aa/agent/tools/run_reviewer.ts#L1-L34).

**Historical source SHA-256:** `10f3fe2d7b50860657fbf6ba582c8e6ae94a98335bfc192088ef4899da505509`.

**Historical Git blob:** `9b4fbcc4f81723422e36f9d3c393afb17e2bcb9f`.

Separate reviewer invocation with a required output schema and self-contained message.

## eve-trust

**Candidate:** [eve-foreman](CATALOG.md#eve-foreman); **historical kind:** `implementation`.

**Original public path:** `agent/lib/trust.ts`.

**Pinned historical ranges:** [L1-L133](https://github.com/vercel-labs/eve-software-factory-template/blob/6bc5febab95de4c05fa08b164f544650f6aa11aa/agent/lib/trust.ts#L1-L133).

**Historical source SHA-256:** `746d130eaed61f22212da6a60571ae5e4d7131e08eb15cca7f3f913078863fb5`.

**Historical Git blob:** `b46267fd6a3544ff8db8675e2c19f192234c054e`.

Separate service identity and trusted/context attributes; full upstream webhook/channel verification was not traced.

## eve-brain-write

**Candidate:** [eve-foreman](CATALOG.md#eve-foreman); **historical kind:** `implementation`.

**Original public path:** `agent/tools/update_factory_brain.ts`.

**Pinned historical ranges:** [L1-L66](https://github.com/vercel-labs/eve-software-factory-template/blob/6bc5febab95de4c05fa08b164f544650f6aa11aa/agent/tools/update_factory_brain.ts#L1-L66).

**Historical source SHA-256:** `b4208a329dab82399cdca83a4e7fa3ceb56710108d4e88444b08e8e94d3fdda4`.

**Historical Git blob:** `69ca557ed5a15c0b2d6fe40c0531e1347884fd7f`.

Configured repository brain key, action policy, whole-document overwrite, and explicit error results.

## eve-approval

**Candidate:** [eve-foreman](CATALOG.md#eve-foreman); **historical kind:** `implementation`.

**Original public path:** `agent/lib/github/approval.ts`.

**Pinned historical ranges:** [L1-L175](https://github.com/vercel-labs/eve-software-factory-template/blob/6bc5febab95de4c05fa08b164f544650f6aa11aa/agent/lib/github/approval.ts#L1-L175).

**Historical source SHA-256:** `5bb9fef0f7ef2aa3372917c63c584ecacbff91cddb268b5f9058ecdbb3c4f49d`.

**Historical Git blob:** `d1e5f870c611d56cd8c5acbcf78911faeab565ae`.

Different policies for unattended/trusted callers, intake-thread comments, shared-brain mutation, draft PRs, and shipping.

## archon-factory-overview

**Candidate:** [archon-factory](CATALOG.md#archon-factory); **historical kind:** `documentation`.

**Original public path:** `README.md`.

**Pinned historical ranges:** [L1-L180](https://github.com/coleam00/ai-software-factory/blob/f6d8f69e452607ceedc6d42f2ed0398db543ba71/README.md#L1-L180).

**Historical source SHA-256:** `3445735e661b3e523fc623f1ebe671f75639aaa1dcf9f0b572fe3ebac6ed1632`.

**Historical Git blob:** `e4476bf461014add0e91730f69efb0698d9be98f`.

Selected candidate screening. Statements remain upstream documentation claims unless a separately registered mechanism supplies narrower implementation evidence.

## waza-overview

**Candidate:** [waza](CATALOG.md#waza); **historical kind:** `documentation`.

**Original public path:** `README.md`.

**Pinned historical ranges:** [L1-L175](https://github.com/microsoft/waza/blob/f5789f75fa00924411734d07fd4012ba80e2154c/README.md#L1-L175).

**Historical source SHA-256:** `de3dcf7610ac6dd67a87c2d8ecec3eca3847599923fc23378753895957a2893d`.

**Historical Git blob:** `6ccb0930d98d3433ed72f9fce62ed868843e8f6a`.

Selected candidate screening. Statements remain upstream documentation claims unless a separately registered mechanism supplies narrower implementation evidence.

## waza-cli

**Candidate:** [waza](CATALOG.md#waza); **historical kind:** `implementation`.

**Original public path:** `internal/execution/sdkclient.go`.

**Pinned historical ranges:** [L90-L180](https://github.com/microsoft/waza/blob/f5789f75fa00924411734d07fd4012ba80e2154c/internal/execution/sdkclient.go#L90-L180).

**Historical source SHA-256:** `73c3ac756560e3cc605ef092512886990445e39710311cf46cbd56a2d0e5b160`.

**Historical Git blob:** `27681a17280e4bea964efb2e48e05dcfcff9e404`.

Usable explicit COPILOT_CLI_PATH versus embedded CLI; no silent fallback to arbitrary PATH executables.

## waza-judge-runtime

**Candidate:** [waza](CATALOG.md#waza); **historical kind:** `implementation`.

**Original public path:** `internal/execution/evidence_judge.go`.

**Pinned historical ranges:** [L475-L529](https://github.com/microsoft/waza/blob/f5789f75fa00924411734d07fd4012ba80e2154c/internal/execution/evidence_judge.go#L475-L529).

**Historical source SHA-256:** `b5099c1005a6f9ef139f0857ffc31e908369917504ecfc9103de89a8ffd8f386`.

**Historical Git blob:** `7bc8fe07e23808e077fd2d487c1ae10717a94f84`.

Owned transport cleanup and the isolated judge's exact pinned native-installation restriction.

## waza-judge

**Candidate:** [waza](CATALOG.md#waza); **historical kind:** `implementation`.

**Original public path:** `internal/graders/evidence_prompt_grader.go`.

**Pinned historical ranges:** [L20-L170](https://github.com/microsoft/waza/blob/f5789f75fa00924411734d07fd4012ba80e2154c/internal/graders/evidence_prompt_grader.go#L20-L170).

**Historical source SHA-256:** `e7faf07287a4e2d2c9781f77b0cacb0f2776c1171aecd3b2b15a335727509164`.

**Historical Git blob:** `8e2194a6a113d145661702e565bbadbc83c0ccfe`.

Frozen evidence, isolated executor, restricted verdict tools, and explicit failure on invalid, duplicate, or missing callbacks.

## waza-evidence-tests

**Candidate:** [waza](CATALOG.md#waza); **historical kind:** `test-source`.

**Original public path:** `cmd/waza/evidence_grade_test.go`.

**Pinned historical ranges:** [L110-L195](https://github.com/microsoft/waza/blob/f5789f75fa00924411734d07fd4012ba80e2154c/cmd/waza/evidence_grade_test.go#L110-L195).

**Historical source SHA-256:** `85eea5d637d1259215593aee6429b8581fdc1a31fe262fbf8a00fcb581a3d214`.

**Historical Git blob:** `5e9cca06d1bce6de1a9b50f9a4c7f931cd5e1fee`.

Foreign evaluation/task/run/attempt, digest tamper, original-file preservation, and snapshot-platform help assertions; not executed.

## waza-text-route

**Candidate:** [waza](CATALOG.md#waza); **historical kind:** `documentation`.

**Original public path:** `site/src/content/docs/guides/runner-contract.mdx`.

**Pinned historical ranges:** [L195-L260](https://github.com/microsoft/waza/blob/f5789f75fa00924411734d07fd4012ba80e2154c/site/src/content/docs/guides/runner-contract.mdx#L195-L260).

**Historical source SHA-256:** `e9bbe2b47b1726e5d81a9087da234b2b763632667c0907f6932a0fc5166aec4b`.

**Historical Git blob:** `df92ddfabfe8880c3c6112a6e5696d0fef343f21`.

Explicit execution opt-in, restricted text-only capability route, cancellation, and synthetic versus live evidence.

## promptfoo-overview

**Candidate:** [promptfoo](CATALOG.md#promptfoo); **historical kind:** `documentation`.

**Original public path:** `README.md`.

**Pinned historical ranges:** [L1-L98](https://github.com/promptfoo/promptfoo/blob/e3e2bb871540ae153a630878ecb17e56cfb487e3/README.md#L1-L98).

**Historical source SHA-256:** `7fd57809624e22da73bf6b6feb027c9e09aec74e0099bdea711fe2e276e87c4a`.

**Historical Git blob:** `2a56017c2609e3a92d7d5539147c9c7e620a3420`.

Selected candidate screening. Statements remain upstream documentation claims unless a separately registered mechanism supplies narrower implementation evidence.

## promptfoo-privacy

**Candidate:** [promptfoo](CATALOG.md#promptfoo); **historical kind:** `documentation`.

**Original public path:** `site/docs/red-team/troubleshooting/data-handling.md`.

**Pinned historical ranges:** [L1-L159](https://github.com/promptfoo/promptfoo/blob/e3e2bb871540ae153a630878ecb17e56cfb487e3/site/docs/red-team/troubleshooting/data-handling.md#L1-L159).

**Historical source SHA-256:** `99cede11952d621c3c01349fb957cbb82e3a38af96a2f197b2d4b2aed38e6d68`.

**Historical Git blob:** `a72f4f9e94cc71f5b4b6209a6698b317299a6c2c`.

Separate target, generation, grading, telemetry, hosted-only features, sharing, and network-boundary controls.

## promptfoo-remote

**Candidate:** [promptfoo](CATALOG.md#promptfoo); **historical kind:** `implementation`.

**Original public path:** `src/redteam/remoteGeneration.ts`.

**Pinned historical ranges:** [L120-L202](https://github.com/promptfoo/promptfoo/blob/e3e2bb871540ae153a630878ecb17e56cfb487e3/src/redteam/remoteGeneration.ts#L120-L202).

**Historical source SHA-256:** `ba5fb52c216ccf7ebe400ed6c2b8db69a912b6e1015d102905dff49765218c02`.

**Historical Git blob:** `8759d4c90f6ad91f84d40f88f6438b902d6fec16`.

Explicit-disable precedence, cloud preference/endpoints, and remote fallback when suitable local credentials are absent.

## rigour-overview

**Candidate:** [rigour](CATALOG.md#rigour); **historical kind:** `documentation`.

**Original public path:** `README.md`.

**Pinned historical ranges:** [L1-L140](https://github.com/rigour-labs/rigour/blob/7e0ef7f4e4ef614d55d83d2958e2603f65f019e7/README.md#L1-L140).

**Historical source SHA-256:** `91f776a292acfccad1e881a524d3a38ae13709e41e1613095be2a1a2089cf151`.

**Historical Git blob:** `81e8df61c444aeaab06389f7e32ff0582c03f44d`.

Selected candidate screening. Statements remain upstream documentation claims unless a separately registered mechanism supplies narrower implementation evidence.

## rigour-lessons

**Candidate:** [rigour](CATALOG.md#rigour); **historical kind:** `implementation`.

**Original public path:** `packages/rigour-core/src/review-learning/lessons.ts`.

**Pinned historical ranges:** [L135-L245](https://github.com/rigour-labs/rigour/blob/7e0ef7f4e4ef614d55d83d2958e2603f65f019e7/packages/rigour-core/src/review-learning/lessons.ts#L135-L245).

**Historical source SHA-256:** `479c9dcbc5e6640b15eaaa9b16d2eeeb060ed9e3716d99217b18236b5bb950ec`.

**Historical Git blob:** `dc5e4c0d2aff090f8e0316cbf643befbf6daa19a`.

Human-decision precedence, withdrawal/demotion, counterevidence, human-origin recurrence, and bot-only rejection.

## rigour-profiles

**Candidate:** [rigour](CATALOG.md#rigour); **historical kind:** `documentation`.

**Original public path:** `docs/PROFILES.md`.

**Pinned historical ranges:** [L1-L36](https://github.com/rigour-labs/rigour/blob/7e0ef7f4e4ef614d55d83d2958e2603f65f019e7/docs/PROFILES.md#L1-L36).

**Historical source SHA-256:** `400325c6b4f3a644253a5da2879a8b8a94b58996a762ac07a7fa9cb5cab4bd77`.

**Historical Git blob:** `8038481d2223803e144e7ad277b365c6e87d3621`.

Documented scoped state and identity configuration; not proof of operating-system isolation.

## rigour-goal

**Candidate:** [rigour](CATALOG.md#rigour); **historical kind:** `documentation`.

**Original public path:** `docs/GOAL.md`.

**Pinned historical ranges:** [L1-L75](https://github.com/rigour-labs/rigour/blob/7e0ef7f4e4ef614d55d83d2958e2603f65f019e7/docs/GOAL.md#L1-L75).

**Historical source SHA-256:** `50690e2137f3f0e6306185446e04c494883fb904c60ee4677c46b5cfbc63717c`.

**Historical Git blob:** `06b579a9352c53bbd13f4c8f6e3c9d2519a72a2e`.

Optional path/symbol checks, uncheckable semantic criteria, and no-check behavior without a PR description.

## compound-engineering-overview

**Candidate:** [compound-engineering](CATALOG.md#compound-engineering); **historical kind:** `documentation`.

**Original public path:** `docs/guides/ce-work.md`.

**Pinned historical ranges:** [L1-L100](https://github.com/EveryInc/compound-engineering-plugin/blob/799ac9aeb97bf1c51238c38122915470413c26c5/docs/guides/ce-work.md#L1-L100).

**Historical source SHA-256:** `7703889a0a4c206a2b7f07ee9c7a39982412d2f53c06c1e5c973de26df052d2c`.

**Historical Git blob:** `4787282d96ce6086188008eb9d2b7d9a9cf1186b`.

Selected candidate screening. Statements remain upstream documentation claims unless a separately registered mechanism supplies narrower implementation evidence.

## compound-work

**Candidate:** [compound-engineering](CATALOG.md#compound-engineering); **historical kind:** `documentation`.

**Original public path:** `docs/guides/ce-work.md`.

**Pinned historical ranges:** [L1-L100](https://github.com/EveryInc/compound-engineering-plugin/blob/799ac9aeb97bf1c51238c38122915470413c26c5/docs/guides/ce-work.md#L1-L100).

**Historical source SHA-256:** `7703889a0a4c206a2b7f07ee9c7a39982412d2f53c06c1e5c973de26df052d2c`.

**Historical Git blob:** `4787282d96ce6086188008eb9d2b7d9a9cf1186b`.

Host-owned verification, canonical commits/delivery, plan boundaries, and return-to-caller execution.

## compound-learning

**Candidate:** [compound-engineering](CATALOG.md#compound-engineering); **historical kind:** `documentation`.

**Original public path:** `docs/guides/ce-compound.md`.

**Pinned historical ranges:** [L1-L145](https://github.com/EveryInc/compound-engineering-plugin/blob/799ac9aeb97bf1c51238c38122915470413c26c5/docs/guides/ce-compound.md#L1-L145).

**Historical source SHA-256:** `8b4bd7f4dc32ddc2ff0c2cc08b685d8a716db6db1447aff423a1796a7084bdee`.

**Historical Git blob:** `7ae2a5dbfc05b89a4ceeeb67e04c4a8326cdd1ad`.

Durable, non-obvious, material learning, cheapest useful representation, retirement, and cross-history privacy implications.

## gsd-core-overview

**Candidate:** [gsd-core](CATALOG.md#gsd-core); **historical kind:** `documentation`.

**Original public path:** `README.md`.

**Pinned historical ranges:** [L1-L128](https://github.com/open-gsd/gsd-core/blob/93bb3b283998b5845cd94be98c9ce240d2946c12/README.md#L1-L128).

**Historical source SHA-256:** `66fe062ee3705af835b09ffa8da112fd14bc8a6025f0d4fb22b4291d353268a9`.

**Historical Git blob:** `82770333164cd599dfa2f1ee44cc66997913cc40`.

Selected candidate screening. Statements remain upstream documentation claims unless a separately registered mechanism supplies narrower implementation evidence.

## gsd-archived-overview

**Candidate:** [gsd-archived](CATALOG.md#gsd-archived); **historical kind:** `documentation`.

**Original public path:** `README.md`.

**Pinned historical ranges:** [L1-L12](https://github.com/gsd-build/get-shit-done/blob/bdcaab2c752d9a33a1a1ca9acf3a3c81fb991815/README.md#L1-L12).

**Historical source SHA-256:** `6530ef6aad23383980a7c405d32c40e73c798ee4263a883f804aef31548569b6`.

**Historical Git blob:** `6232a8c42bbdcd0ad5f290c41806c2728c68d194`.

Selected candidate screening. Statements remain upstream documentation claims unless a separately registered mechanism supplies narrower implementation evidence.

## engineering-plugin-overview

**Candidate:** [engineering-plugin](CATALOG.md#engineering-plugin); **historical kind:** `documentation`.

**Original public path:** `engineering/README.md`.

**Pinned historical ranges:** [L1-L136](https://github.com/anthropics/knowledge-work-plugins/blob/d900840716eb262e1feb17c6f4406c9ce0e06bcf/engineering/README.md#L1-L136).

**Historical source SHA-256:** `168c529ed659b79ac5736de9b9d9b9089c06e1998452f155e58ab2f6261d402f`.

**Historical Git blob:** `b3a368d30c744e6ee6f185733447022bf8878844`.

Selected candidate screening. Statements remain upstream documentation claims unless a separately registered mechanism supplies narrower implementation evidence.

## gitleaks-overview

**Candidate:** [gitleaks](CATALOG.md#gitleaks); **historical kind:** `documentation`.

**Original public path:** `README.md`.

**Pinned historical ranges:** [L1-L175](https://github.com/gitleaks/gitleaks/blob/5f6ec56cfa6f8c67648d863582c7ae2f206d5c1c/README.md#L1-L175).

**Historical source SHA-256:** `65e87e68f4a16aefa1f1fba55b2e7a9b9bc8716393b7ddb013fc7c7bef4e4bc1`.

**Historical Git blob:** `6bdd5d960fd9f81a5221819509c4e9f5cb7d251e`.

Selected candidate screening. Statements remain upstream documentation claims unless a separately registered mechanism supplies narrower implementation evidence.

## pester-overview

**Candidate:** [pester](CATALOG.md#pester); **historical kind:** `documentation`.

**Original public path:** `README.md`.

**Pinned historical ranges:** [L1-L155](https://github.com/pester/Pester/blob/98e56d65da1642a7158992b50ded240c42a3ac18/README.md#L1-L155).

**Historical source SHA-256:** `91dde4c51d8a54fc6489a823bdd45f192fa4c1b995b95b2fa4430b3fd00072f3`.

**Historical Git blob:** `a66cd068ad27e43d0fc7bbe80bf9fbd852502f8d`.

Selected candidate screening. Statements remain upstream documentation claims unless a separately registered mechanism supplies narrower implementation evidence.

## twelve-factor-overview

**Candidate:** [twelve-factor](CATALOG.md#twelve-factor); **historical kind:** `documentation`.

**Original public path:** `README.md`.

**Pinned historical ranges:** [L1-L200](https://github.com/humanlayer/12-factor-agents/blob/d20c728368bf9c189d6d7aab704744decb6ec0cc/README.md#L1-L200).

**Historical source SHA-256:** `898b8879be9279c5c90e302e58232ac4f4f4ab051efe69cff30738b2efbac3c7`.

**Historical Git blob:** `bf87693afef770e5da83ab3109b90f734f60b6e6`.

Selected candidate screening. Statements remain upstream documentation claims unless a separately registered mechanism supplies narrower implementation evidence.

## factor-pause

**Candidate:** [twelve-factor](CATALOG.md#twelve-factor); **historical kind:** `conceptual-document`.

**Original public path:** `content/factor-06-launch-pause-resume.md`.

**Pinned historical ranges:** [L1-L29](https://github.com/humanlayer/12-factor-agents/blob/d20c728368bf9c189d6d7aab704744decb6ec0cc/content/factor-06-launch-pause-resume.md#L1-L29).

**Historical source SHA-256:** `b6574ff34e727a88c56621f9d37a2de14375878c6a3eddf8c1bcb86a344467e2`.

**Historical Git blob:** `7a344a6c2bf79256718e5e661bd0e664518d36f6`.

Launch/pause/resume interfaces and the distinction between choosing a tool and invoking it.

## factor-control

**Candidate:** [twelve-factor](CATALOG.md#twelve-factor); **historical kind:** `conceptual-document`.

**Original public path:** `content/factor-08-own-your-control-flow.md`.

**Pinned historical ranges:** [L1-L86](https://github.com/humanlayer/12-factor-agents/blob/d20c728368bf9c189d6d7aab704744decb6ec0cc/content/factor-08-own-your-control-flow.md#L1-L86).

**Historical source SHA-256:** `3eec4727a3f5607efca7486430eff693810a12f7fcdb1dc0c6cc4ec4c97adcab`.

**Historical Git blob:** `99b5288f47104922c2a3a37f7b15078c0ed942d1`.

Deterministic interruption, human decisions, and durable continuation rather than in-memory waiting.

## factor-errors

**Candidate:** [twelve-factor](CATALOG.md#twelve-factor); **historical kind:** `conceptual-document`.

**Original public path:** `content/factor-09-compact-errors.md`.

**Pinned historical ranges:** [L1-L85](https://github.com/humanlayer/12-factor-agents/blob/d20c728368bf9c189d6d7aab704744decb6ec0cc/content/factor-09-compact-errors.md#L1-L85).

**Historical source SHA-256:** `32232adfb5ff0f7a28c29547ef3e5894ff16d37777c8446e8f7675fbac5cab79`.

**Historical Git blob:** `948c927a4f52f04a5f72cb3e26e15ec221eeae9a`.

Useful error context, bounded recovery, and escalation rather than unlimited self-healing.

## factor-reducer-heading

**Candidate:** [twelve-factor](CATALOG.md#twelve-factor); **historical kind:** `text-only-document`.

**Original public path:** `content/factor-12-stateless-reducer.md`.

**Pinned historical ranges:** [L1-L12](https://github.com/humanlayer/12-factor-agents/blob/d20c728368bf9c189d6d7aab704744decb6ec0cc/content/factor-12-stateless-reducer.md#L1-L12).

**Historical source SHA-256:** `4bafcd1337db57c193fb9fdc713272011f18d37714db9930df2443a0e422ca3a`.

**Historical Git blob:** `1370f5dc4d819521526623c2cc2fe68c88bba8ab`.

Heading and links only; the two referenced diagrams were not fetched or visually inspected.

## zazen-factory-overview

**Candidate:** [zazen-factory](CATALOG.md#zazen-factory); **historical kind:** `documentation`.

**Original public path:** `src/software-factory-claude-code/README.md`.

**Pinned historical ranges:** [L1-L112](https://github.com/zazencodes/zazencodes-season-3/blob/6c2b66b0f38fc883f773fe098214c0cef4ea7654/src/software-factory-claude-code/README.md#L1-L112).

**Historical source SHA-256:** `53c9bd4ae82bd45c4a4b142154c5aa337f74fb6be2c824a004d56dcbcca59b2e`.

**Historical Git blob:** `a34ceb08bf93ec30cc11e819844720b83796d73a`.

Selected candidate screening. Statements remain upstream documentation claims unless a separately registered mechanism supplies narrower implementation evidence.

## zazen-video-index

**Candidate:** [zazen-factory](CATALOG.md#zazen-factory); **historical kind:** `documentation`.

**Original public path:** `README.md`.

**Pinned historical ranges:** [L1-L38](https://github.com/zazencodes/zazencodes-season-3/blob/6c2b66b0f38fc883f773fe098214c0cef4ea7654/README.md#L1-L38).

**Historical source SHA-256:** `e9cf39332abcce5e209073b6543fa33e0ea8bd98e1fb9c83fb5c460cd37cac82`.

**Historical Git blob:** `7fdef48b4a1819044018bb11cc6ba6ebaf5edc7b`.

Explicit public link between the supplied video and v1 lesson folder; not a review of other repository lessons.

## zazen-build-prompt

**Candidate:** [zazen-factory](CATALOG.md#zazen-factory); **historical kind:** `prompt-template`.

**Original public path:** `src/software-factory-claude-code/BUILD_PROMPT.md`.

**Pinned historical ranges:** [L1-L106](https://github.com/zazencodes/zazencodes-season-3/blob/6c2b66b0f38fc883f773fe098214c0cef4ea7654/src/software-factory-claude-code/BUILD_PROMPT.md#L1-L106).

**Historical source SHA-256:** `cd1e9c7a0116a7faae173fc3cfa9ac2e1929e640dae27c28d5ffce18cd9c25b1`.

**Historical Git blob:** `ab7d5e4998e4237be960b0a086650afb58cd382b`.

Original shared board.json design, artifact roles, review barrier, and model-authorized local integration; upstream retains it as historical.

## zazen-orchestrator

**Candidate:** [zazen-factory](CATALOG.md#zazen-factory); **historical kind:** `skill-contract`.

**Original public path:** `src/software-factory-claude-code/.claude/skills/factory/SKILL.md`.

**Pinned historical ranges:** [L1-L221](https://github.com/zazencodes/zazencodes-season-3/blob/6c2b66b0f38fc883f773fe098214c0cef4ea7654/src/software-factory-claude-code/.claude/skills/factory/SKILL.md#L1-L221).

**Historical source SHA-256:** `2c06932abc4b3bf6810980cfe5e717a70b6d62034428b49013db2cbfce5690d9`.

**Historical Git blob:** `744086da794cd4ab5a177277c2a3c10c9f9da060`.

Later v1 per-job state, worktrees, absolute paths, complete review barrier, two resumptions/three rounds, fresh rework, local merge, and never-push instructions.

## zazen-spec-writer

**Candidate:** [zazen-factory](CATALOG.md#zazen-factory); **historical kind:** `skill-contract`.

**Original public path:** `src/software-factory-claude-code/.claude/agents/spec-writer.md`.

**Pinned historical ranges:** [L1-L65](https://github.com/zazencodes/zazencodes-season-3/blob/6c2b66b0f38fc883f773fe098214c0cef4ea7654/src/software-factory-claude-code/.claude/agents/spec-writer.md#L1-L65).

**Historical source SHA-256:** `46998bf65cdc935d3ea27753ccc3781d4ee852f4769077bf0c8d5acd68155af3`.

**Historical Git blob:** `df08de1f21bf14a8c64767d95437b14a9c602c8f`.

Existing-code grounding, reuse, observable acceptance, non-goals, and consequential assumptions deferred to the final approver rather than a pre-code human gate.

## zazen-builder

**Candidate:** [zazen-factory](CATALOG.md#zazen-factory); **historical kind:** `skill-contract`.

**Original public path:** `src/software-factory-claude-code/.claude/agents/builder.md`.

**Pinned historical ranges:** [L1-L96](https://github.com/zazencodes/zazencodes-season-3/blob/6c2b66b0f38fc883f773fe098214c0cef4ea7654/src/software-factory-claude-code/.claude/agents/builder.md#L1-L96).

**Historical source SHA-256:** `16126f86388b4c3f65a61d30b5c69d97b34997252283dc11f2e53c2b6f94c459`.

**Historical Git blob:** `4317392914dee7aa6085ea037e176062fdf445a2`.

Branch/path checks, actual repository validation commands, per-criterion evidence, explicit-path staging, preserved round history, and BLOCKED reporting.

## zazen-code-reviewer

**Candidate:** [zazen-factory](CATALOG.md#zazen-factory); **historical kind:** `skill-contract`.

**Original public path:** `src/software-factory-claude-code/.claude/agents/reviewer-code.md`.

**Pinned historical ranges:** [L1-L68](https://github.com/zazencodes/zazencodes-season-3/blob/6c2b66b0f38fc883f773fe098214c0cef4ea7654/src/software-factory-claude-code/.claude/agents/reviewer-code.md#L1-L68).

**Historical source SHA-256:** `6d5dc8eda9f81e2bed198d7e098ff2a39a1b152f9595cf0d5caf7ed555773619`.

**Historical Git blob:** `cf373e178d7b76ce4eb62eabf03829c030b489e0`.

Current diff and previous findings, rerun checks, path/line evidence, and separation of defects from style notes.

## zazen-approver

**Candidate:** [zazen-factory](CATALOG.md#zazen-factory); **historical kind:** `skill-contract`.

**Original public path:** `src/software-factory-claude-code/.claude/agents/approver.md`.

**Pinned historical ranges:** [L1-L65](https://github.com/zazencodes/zazencodes-season-3/blob/6c2b66b0f38fc883f773fe098214c0cef4ea7654/src/software-factory-claude-code/.claude/agents/approver.md#L1-L65).

**Historical source SHA-256:** `92e0baf08b0663c19a1913e742d467d68213f2a28ce605e9dace8ffddb56fc78`.

**Historical Git blob:** `b58bf444a719f8c15d11ed781256146dfe467aa9`.

Model APPROVE authorizes local-main integration; risk categories or product decisions can escalate. This is not human authorization.

## zazen-v2-overview

**Candidate:** [zazen-factory](CATALOG.md#zazen-factory); **historical kind:** `documentation`.

**Original public path:** `src/software-factory-claude-code-v2/README.md`.

**Pinned historical ranges:** [L1-L180](https://github.com/zazencodes/zazencodes-season-3/blob/6c2b66b0f38fc883f773fe098214c0cef4ea7654/src/software-factory-claude-code-v2/README.md#L1-L180).

**Historical source SHA-256:** `f027fbc9b7d9bf78f9d39725f17f892b3f9c092cc7c0640c5b3b1893e4c99984`.

**Historical Git blob:** `f0e64f4d033ed85dcb420a7b5675ace935bd7b2b`.

Separate issue-driven successor, documented script/state gates, PR delivery, recovery and cost claims; executable implementation not reviewed.

## zazen-v2-license

**Candidate:** [zazen-factory](CATALOG.md#zazen-factory); **historical kind:** `license-document`.

**Original public path:** `src/software-factory-claude-code-v2/LICENSE`.

**Pinned historical ranges:** [L1-L50](https://github.com/zazencodes/zazencodes-season-3/blob/6c2b66b0f38fc883f773fe098214c0cef4ea7654/src/software-factory-claude-code-v2/LICENSE#L1-L50).

**Historical source SHA-256:** `3972dc9744f6499f0f9b2dbf76696f2ae7ad8af9b23dde66d6af86c9dfb36986`.

**Historical Git blob:** `f288702d2fa16d3cdf0035b15a9fcbc552cd88e7`.

Scoped GPLv3 title and opening preamble, including charging for copies and redistribution responsibilities; not a complete legal assessment.

## zazen-video

[Video identity](https://www.youtube.com/watch?v=ctoaIC4LHmI) |
[Detailed historical analysis](VIDEO_ZAZEN_FACTORY.md) |
[Public review metadata](public-context-sources.json)

The historical supplement records available-caption review and two sampled
frames, not candidate runtime acceptance or continuous listening. The supplied
overview, raw captions, frames, and extraction fingerprints are not published.
Absent source bytes cannot be independently rehashed from this edition.
