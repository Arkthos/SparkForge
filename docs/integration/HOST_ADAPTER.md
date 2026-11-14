# Native host adapter contract

**Implemented source-neutral protocol and scripted fake (WP-114), not a selected Copilot launcher.** P6 must bind actual supported mechanisms in one selected host/build. Current package metadata declaring Copilot/Windows does not establish a native API.

| Capability | Required semantics | When absent |
|---|---|---|
| Discover capabilities | Versioned host/build/profile, supported invocation/tools/context, producer and usage visibility | Return explicit unsupported/unknown; do not probe accounts or install replacements |
| Dispatch task | Versioned assignment and durable operation key; bounded authority/context/resources | No dispatch; explain concrete missing capability |
| Poll/read operation | Distinguish accepted/running/completed/failed/cancel-requested/stopped/unknown | Preserve unresolved reservation, not blind retry |
| Cancel owned work | Request cancellation using observed operation identity | Stop new admission; report residual uncertainty |
| Reconcile | Read actual operation/effects after lost response or restart | Require real operator assessment where host cannot establish outcome |
| Producer context | Task/role/session association sufficient for claimed independence | Narrow claim to assisted assertions; do not rename builder as reviewer |
| Usage receipt | Reliable measured values or explicit unknowns | Enforce observable call/time/attempt limits and selected unknown-usage policy |
| Tools/files/effects | Actual supported restrictions, identity and network/data routes | Prompts may guide; do not claim unenforced confinement |

`plugins.sparkforge.runtime.host.HostAdapter` defines `discover()`, `dispatch(task, operation_key, required=...)`, `poll(task, operation_key)`, `cancel(task, operation_key)` and `reconcile(task, operation_key)`. They return `HostCapabilities` or `HostReceipt`; these signatures are project contracts, not assumed vendor SDK commands.

`validate_capabilities`, `require_capabilities` and `validate_receipt` use the shared typed errors and strict WP-110/111 validators. Each capability explicitly reports `supported`, `unsupported` or `unknown`. Default dispatch requirements are dispatch/poll/reconcile/producer-context; callers can explicitly require usage, cancellation and scope-enforcement support too. Unsupported or unknown required capabilities fail before dispatch. Role/tool/effect support and selected environment/profile/host/provider must match the assignment; these consistency checks do not authorize execution.

Receipts bind exact operation/task/input/role digests and context references, including strict integer revisions. They preserve producer observations, known/unknown usage, effect uncertainty, cancellation acknowledgement, observed stop and an optional result digest. Completed host work does not imply a structured result exists or has been admitted. A stopped receipt requires an observed stop; acknowledged cancellation leaves effects possible. Unknown/unavailable usage remains null with a reason, never zero. Evidence class is explicit: `scripted_fake` cannot be relabeled `host_observed`.

The test-owned `tests/fakes/fake_host.py` executes only finite observation scripts, capped at 128 operations and 128 steps each. It exposes method-call, simulated-dispatch and cancellation counters; no worker code, file/process/network I/O, clock-based execution or real model is invoked. Poll/reconcile advances scripted observations. Reusing an operation key cannot create another simulated effect; lost responses require reconciliation. Acknowledged cancel can end in observed stopped or late completion. Unsupported observation capabilities are checked before the fake increments its effect counter.

Protocol objects and a fake's declared scope support are not host authentication, an OS sandbox or accumulated budget enforcement. WP-120 now supplies durable local persistence and WP-121 connects the scripted protocol to serial scheduling; actual ingress/admission and live-host qualification remain later tasks. TC-111/112 are implemented in `tests/test_host_adapter.py`; TC-117/118 in `tests/test_scheduler.py`.

The [WP-121 coordinator](../design/DATA_AND_STATE.md#implemented-wp-121-serial-coordinator) pins capability/context before effects, commits operation reservation/dispatch first, and preserves uncertain responses rather than retrying. It accepts only `scripted_fake` hosts at this stage. Unsupported cancellation is reported explicitly while polling/reconciliation stays available; it does not invent a cancel mechanism or assume work stopped. Structured results must match the completed host result digest; host completion alone cannot satisfy a task or job.

## Qualification procedure

Record exact host/build, profile, supported package resource format, delegation/session mechanism, environment, allowed model/data routes and finite disposable trial scope. Verify a task dispatch and result binding; independent review context; owned stop and restart reconciliation; usage visibility; installed resource relocation; and tool/file/effect limits actually enforced.

Retain selected observations in the approved environment. Publish only cleared aggregate capability/support statements. No credentials/private platform captures/raw model transcripts in Git. A subscription, executable or another client's API does not prove this host has the capability.

If actual support is insufficient, record the gap and concrete options: narrower assisted operation, another explicitly selected native capability, or an owner-approved runtime change. Source-neutral design/tests continue meanwhile; silent provider substitution is not an option.
