# Storage probe and qualification limits

## Implemented probe

`scripts\probe_local_storage.py` makes three bounded filesystem observations
using newly owned synthetic artifacts under one explicitly selected,
existing local directory. It does not choose a fallback root, inspect an
operator's real job database or qualify a runtime store.

| Check ID | Observation |
|---|---|
| `atomic_candidate_replace` | A child replaces an owned committed marker with its complete candidate; the parent observes the expected result and absent candidate path. This is not a concurrent-reader or power-loss proof. |
| `exclusive_create_conflict` | A child cannot exclusively create an already owned lock file; the existing marker remains unchanged. This is not SQLite transaction qualification. |
| `interrupted_publication` | A controlled child exits before publication; the original committed marker and complete unpublished candidate remain. This is a designed synthetic interruption, not an actual crash-recovery acceptance run. |

The probe uses one `.sparkforge-storage-probe-...` directory, fixed known
file names, identity/content checks and narrowly owned child processes.
Cleanup removes only artifacts whose ownership and expected content can
still be confirmed. Changed or unknown content is preserved and reported,
not recursively swept away.

## Explicit local invocation

This is synthetic diagnostic syntax from the repository root, not a
qualification receipt or an accepted brief. Run it only when the operator
authorizes disposable files and bounded local child processes in `tests`:

```powershell
$SyntheticProbeRoot = (Resolve-Path 'tests').Path
python -B scripts\probe_local_storage.py --root $SyntheticProbeRoot --scope-ref synthetic-storage --confirm-disposable
```

`--root` has no default and must be an existing absolute, non-root directory.
`--scope-ref` is a non-sensitive label of 1–64 ASCII letters, digits, dots,
underscores or hyphens, beginning with a letter or digit.
`--confirm-disposable` is mandatory at the CLI.
The Python API is `run_probe(root: Path, *, scope_ref: str)`; its caller owns
the authorization decision.

The current probe requires Windows drive-class inspection and refuses
unsupported platforms, ambiguous paths, UNC/device/network roots, traversal
and redirecting components. Ordinary cloud-placeholder metadata is not
proof that underlying cloud synchronization or storage is qualified.
Do not silently relocate to a system temporary directory if the chosen
root is blocked.

## Reading the result

The report's scope is `disposable_local_storage_probe`. Its `overall` value
is `PASS`, `FAIL` or `BLOCKED`, with check observations, diagnostics, cleanup
status and any unconfirmed owned child PID. CLI exit codes are respectively
0, 1 and 2. Later checks remain blocked when an earlier operation cannot
continue.

`runtime_store_qualified` is always false. A passing probe does not assess:

- cloud synchronization, mapped or virtual backing, or another machine;
- power-loss durability or concurrent-reader atomicity;
- database locking, transaction integrity or product recovery;
- host security, sandboxing or data permissions;
- hard deadlines for kernel filesystem calls;
- suitability of that directory for confidential persistent jobs.

Child timeouts are engineering bounds (five seconds for a child and two
seconds for stopping an owned child), not guaranteed OS deadlines.
If cleanup is blocked or a child is unconfirmed, preserve the reported
location and inspect that exact operation. Do not kill unrelated processes,
delete unknown files or rerun blindly.

## Factory storage is a separate decision

The factory uses an explicitly supplied local candidate workspace and a
new, non-overlapping job directory with an existing parent. Job state is
SQLite, containing spec text, paths, assertions and runner evidence.
Its path checks and SQLite transactions are useful local constraints,
not proof of cloud-sync suitability, source confidentiality or protection
against another same-privilege writer.

An operator must choose authorized storage and assess the actual backup,
retention, concurrency and recovery requirements before using real data.
A directory name or a local probe pass does not establish those properties.
This publication contains no prior private storage receipt and claims no
live runtime-store qualification.

See [host qualification](HOST_QUALIFICATION.md) and
[native factory](NATIVE_FACTORY.md).
