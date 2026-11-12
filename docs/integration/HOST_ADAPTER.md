# Native host adapter contract

**Planned abstraction, not a selected Copilot launcher.** P1 implements a deterministic fake; P6 binds actual supported mechanisms in one selected host/build. Current package metadata declaring Copilot/Windows does not establish this API.

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

Protocol function names/return types are defined in WP-114 with tests, not assumed from a vendor SDK. The selected native adapter must translate the protocol to documented/observed capabilities and reject unsupported options before effects.

## Qualification procedure

Record exact host/build, profile, supported package resource format, delegation/session mechanism, environment, allowed model/data routes and finite disposable trial scope. Verify a task dispatch and result binding; independent review context; owned stop and restart reconciliation; usage visibility; installed resource relocation; and tool/file/effect limits actually enforced.

Retain selected observations in the approved environment. Publish only cleared aggregate capability/support statements. No credentials/private platform captures/raw model transcripts in Git. A subscription, executable or another client's API does not prove this host has the capability.

If actual support is insufficient, record the gap and concrete options: narrower assisted operation, another explicitly selected native capability, or an owner-approved runtime change. Source-neutral design/tests continue meanwhile; silent provider substitution is not an option.
