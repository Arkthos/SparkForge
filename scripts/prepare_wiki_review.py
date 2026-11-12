"""Prepare complete, hash-verified wiki redaction candidates in local storage."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


MAX_MANIFEST_BYTES = 4 * 1024 * 1024
MAX_FILE_BYTES = 16 * 1024 * 1024
MAX_TOTAL_BYTES = 64 * 1024 * 1024
MAX_ITEMS = 10000
COLLECTIONS = ("pages", "attachments", "ancillary_items")
CODE_ROOT = Path(__file__).resolve().parents[1]
SHA256 = re.compile(r"[0-9a-f]{64}")
REVISION = re.compile(r"[0-9a-f]{40,64}")
RULES = (
    ("private_key", re.compile(
        r"-----BEGIN (?:RSA |EC |OPENSSH |DSA |ENCRYPTED )?PRIVATE KEY-----"
        r".*?-----END (?:RSA |EC |OPENSSH |DSA |ENCRYPTED )?PRIVATE KEY-----",
        re.DOTALL,
    )),
    ("authorization", re.compile(r"(?im)^[ \t]*(?:proxy-)?authorization[ \t]*:[^\r\n]+")),
    ("credential_token", re.compile(
        r"\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{40,}|"
        r"(?:AKIA|ASIA)[A-Z0-9]{16})\b"
    )),
    ("url", re.compile(r"(?i)\b(?:https?://|ftp://|www\.)[^\s<>\"'`]+")),
    ("email", re.compile(r"(?i)\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b")),
    ("windows_path", re.compile(r"(?i)(?<![\w])[A-Z]:[\\/][^\r\n`<>\"|]+|\\\\[^\r\n`<>\"|]+")),
    ("uuid", re.compile(r"(?i)\b[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}\b")),
    ("source_fingerprint", re.compile(r"(?i)\b(?:[0-9a-f]{64}|[0-9a-f]{40})\b")),
)


class ReviewError(Exception):
    def __init__(self, code: str, *, output_created: bool = False):
        super().__init__(code)
        self.code = code
        self.output_created = output_created


def _fail(code: str) -> None:
    raise ReviewError(code)


def _json(raw: bytes) -> object:
    def pairs(entries):
        result = {}
        for key, value in entries:
            if key in result:
                _fail("DUPLICATE_JSON_KEY")
            result[key] = value
        return result

    def invalid_constant(_value):
        _fail("INVALID_JSON")

    try:
        return json.loads(raw.decode("utf-8"), object_pairs_hook=pairs, parse_constant=invalid_constant)
    except (UnicodeError, json.JSONDecodeError):
        _fail("INVALID_JSON")


def _signature(info) -> tuple:
    return (info.st_dev, info.st_ino, info.st_mode, info.st_nlink, info.st_size, info.st_mtime_ns)


def _inspect(path: Path, *, directory: bool):
    info = path.lstat()
    redirecting = bool(getattr(info, "st_reparse_tag", 0) & 0x20000000)
    if stat.S_ISLNK(info.st_mode) or redirecting:
        _fail("UNSAFE_PATH")
    if directory and not stat.S_ISDIR(info.st_mode):
        _fail("DIRECTORY_REQUIRED")
    if not directory and (not stat.S_ISREG(info.st_mode) or info.st_nlink != 1):
        _fail("REGULAR_OWNED_FILE_REQUIRED")
    return info


def _absolute(path: Path) -> Path:
    path = Path(path)
    value = str(path)
    if (not path.is_absolute() or ".." in path.parts or path == Path(path.anchor)
            or any(ord(char) < 32 for char in value) or value.startswith(("\\\\", "//"))):
        _fail("INVALID_ROOT")
    for parent in reversed(path.parents):
        _inspect(parent, directory=True)
    if os.name == "nt":
        import ctypes
        if ctypes.windll.kernel32.GetDriveTypeW(str(path.anchor)) not in (3, 6):
            _fail("LOCAL_DRIVE_REQUIRED")
    return path


def _relative(value: object) -> Path:
    if not isinstance(value, str) or not value or len(value) > 1024:
        _fail("INVALID_SOURCE_PATH")
    parts = value.replace("\\", "/").split("/")
    reserved = {"CON", "PRN", "AUX", "NUL", *(f"COM{i}" for i in range(1, 10)), *(f"LPT{i}" for i in range(1, 10))}
    if any(
        part in ("", ".", "..") or ":" in part or part.endswith((" ", "."))
        or any(ord(char) < 32 for char in part)
        or part.split(".", 1)[0].upper() in reserved
        for part in parts
    ):
        _fail("INVALID_SOURCE_PATH")
    return Path(*parts)


def _read(root: Path, relative: Path, maximum: int) -> tuple[bytes, tuple]:
    for parent in reversed(relative.parents):
        _inspect(root / parent, directory=True)
    path = root / relative
    before = _inspect(path, directory=False)
    if before.st_size > maximum:
        _fail("RESOURCE_LIMIT")
    with path.open("rb") as stream:
        opened = os.fstat(stream.fileno())
        if _signature(opened) != _signature(before):
            _fail("SOURCE_CHANGED")
        raw = stream.read(maximum + 1)
        after_handle = os.fstat(stream.fileno())
    after_path = _inspect(path, directory=False)
    if (len(raw) > maximum or len(raw) != before.st_size
            or _signature(after_handle) != _signature(before)
            or _signature(after_path) != _signature(before)):
        _fail("SOURCE_CHANGED")
    return raw, _signature(before)


def _digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _encoded(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=True, indent=2) + "\n").encode("utf-8")


def validate_policy(value: object) -> dict:
    if (type(value) is not dict or set(value) != {"schema_version", "literals"}
            or value["schema_version"] != "sparkforge.wiki-redaction-policy.v1"
            or type(value["literals"]) is not list or len(value["literals"]) > 1000):
        _fail("INVALID_POLICY")
    seen = set()
    for literal in value["literals"]:
        if (type(literal) is not str or not literal.strip() or len(literal) > 1024
                or any(ord(char) < 32 for char in literal)):
            _fail("INVALID_POLICY")
        if literal.casefold() in seen:
            _fail("DUPLICATE_LITERAL")
        seen.add(literal.casefold())
    return {"schema_version": value["schema_version"], "literals": list(value["literals"])}


def redact_text(text: str, policy: dict) -> tuple[str, list[dict], dict]:
    """Replace declared spans only; the caller must still review semantic content."""
    validate_policy(policy)
    spans = []
    counts: Counter = Counter()
    for name, expression in RULES:
        for match in expression.finditer(text):
            spans.append((match.start(), match.end(), name))
            counts[name] += 1
    for index, literal in enumerate(policy["literals"], 1):
        name = f"literal_{index:04d}"
        for match in re.finditer(re.escape(literal), text, re.IGNORECASE):
            spans.append((match.start(), match.end(), name))
            counts[name] += 1
    merged: list[dict] = []
    for start, end, name in sorted(spans):
        if merged and start < merged[-1]["end"]:
            merged[-1]["end"] = max(end, merged[-1]["end"])
            merged[-1]["rules"] = sorted(set(merged[-1]["rules"]) | {name})
        else:
            merged.append({"start": start, "end": end, "rules": [name]})
    output, offset = [], 0
    for number, span in enumerate(merged, 1):
        token = f"[REDACTED_{number:04d}]"
        output.extend((text[offset:span["start"]], token))
        span["replacement"] = token
        offset = span["end"]
    output.append(text[offset:])
    return "".join(output), merged, dict(sorted(counts.items()))


def _items(manifest: object) -> list[tuple[str, dict, Path]]:
    if type(manifest) is not dict or not REVISION.fullmatch(str(manifest.get("snapshot_commit", ""))):
        _fail("INVALID_MANIFEST")
    if any(type(manifest.get(name)) is not list for name in COLLECTIONS) or not manifest["pages"]:
        _fail("INCOMPLETE_INVENTORY")
    if sum(len(manifest[name]) for name in COLLECTIONS) > MAX_ITEMS:
        _fail("RESOURCE_LIMIT")
    keys, paths, result, total = set(), set(), [], 0
    for collection in COLLECTIONS:
        for item in manifest[collection]:
            if type(item) is not dict:
                _fail("INVALID_MANIFEST")
            key = item.get("key")
            if not isinstance(key, str) or not key or len(key) > 1024 or key in keys:
                _fail("INVALID_OR_DUPLICATE_SOURCE_KEY")
            keys.add(key)
            relative = _relative(item.get("local_path"))
            comparison = str(relative).casefold()
            if comparison in paths:
                _fail("DUPLICATE_SOURCE_PATH")
            paths.add(comparison)
            size = item.get("bytes")
            if (item.get("status") != "EXPORTED"
                    or item.get("snapshot_commit") != manifest["snapshot_commit"]
                    or type(size) is not int or size < 0
                    or not isinstance(item.get("sha256"), str)
                    or not SHA256.fullmatch(item["sha256"])):
                _fail("INCOMPLETE_SOURCE_RECORD")
            if size > MAX_FILE_BYTES:
                _fail("RESOURCE_LIMIT")
            total += size
            if total > MAX_TOTAL_BYTES:
                _fail("RESOURCE_LIMIT")
            result.append((collection, item, relative))
    return result


def _write(path: Path, raw: bytes) -> None:
    with path.open("xb") as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())


def _repository_output(path: Path) -> bool:
    return path.is_relative_to(CODE_ROOT) or any((parent / ".git").exists() for parent in path.parents)


def prepare_review(
    root: Path, output: Path, policy: dict, *, confirm_local_review: bool = False
) -> dict:
    if not confirm_local_review:
        _fail("CONFIRMATION_REQUIRED")
    policy = validate_policy(policy)
    root, output = _absolute(root), _absolute(output)
    root_info = _inspect(root, directory=True)
    if output.exists() or output.is_symlink():
        _fail("OUTPUT_EXISTS")
    physical_root, physical_output = root.resolve(), output.parent.resolve() / output.name
    if (physical_output.is_relative_to(physical_root)
            or physical_root.is_relative_to(physical_output)
            or _repository_output(physical_output)):
        _fail("SEPARATE_NON_REPOSITORY_OUTPUT_REQUIRED")
    raw_manifest, manifest_signature = _read(root, Path("manifest.json"), MAX_MANIFEST_BYTES)
    manifest = _json(raw_manifest)
    items = _items(manifest)
    prepared, snapshots, counts = [], [(Path("manifest.json"), manifest_signature)], Counter()
    for collection, source, relative in items:
        raw, signature = _read(root, relative, MAX_FILE_BYTES)
        if len(raw) != source["bytes"] or _digest(raw) != source["sha256"]:
            _fail("SOURCE_HASH_MISMATCH")
        snapshots.append((relative, signature))
        counts[collection] += 1
        identifier = f"{collection}-{counts[collection]:04d}"
        original_path = Path("originals", collection, identifier + (".md" if collection == "pages" else ".bin"))
        entry = {
            "id": identifier, "collection": collection, "source_key": source["key"],
            "source_local_path": str(relative), "original_path": str(original_path),
            "source_sha256": source["sha256"], "source_bytes": len(raw),
            "review_status": "REVIEW_REQUIRED" if collection == "pages" else "NOT_REVIEWED",
            "publication_authorized": False,
        }
        candidate = None
        if collection == "pages":
            try:
                text = raw.decode("utf-8")
            except UnicodeError:
                _fail("PAGE_NOT_UTF8")
            redacted, spans, matches = redact_text(text, policy)
            candidate = redacted.encode("utf-8")
            entry.update(
                candidate_path=str(Path("candidates", identifier + ".md")),
                candidate_sha256=_digest(candidate), candidate_bytes=len(candidate),
                redactions=spans, rule_match_counts=matches,
                non_redacted_text_preserved=True,
            )
        prepared.append((entry, raw, candidate))
    if _signature(_inspect(root, directory=True)) != _signature(root_info):
        _fail("SOURCE_CHANGED")
    for relative, signature in snapshots:
        for parent in reversed(relative.parents):
            _inspect(root / parent, directory=True)
        if _signature(_inspect(root / relative, directory=False)) != signature:
            _fail("SOURCE_CHANGED")

    output.mkdir()
    try:
        directories = {output: _inspect(output, directory=True)}

        def owned_write(path: Path, raw: bytes) -> None:
            ancestry, directory = [output], output
            for part in path.relative_to(output).parts[:-1]:
                directory = directory / part
                ancestry.append(directory)
            for directory in ancestry:
                before = directories[directory]
                current = _inspect(directory, directory=True)
                if (current.st_dev, current.st_ino) != (before.st_dev, before.st_ino):
                    _fail("OUTPUT_CHANGED")
            _write(path, raw)

        marker = _encoded({
            "status": "INCOMPLETE", "publication_authorized": False,
            "instruction": "Do not use or publish partial artifacts; reconcile this exact owned output locally.",
        })
        owned_write(output / "INCOMPLETE.json", marker)
        for directory in (output / "originals", output / "candidates",
                          *(output / "originals" / name for name in COLLECTIONS)):
            directory.mkdir()
            directories[directory] = _inspect(directory, directory=True)
        owned_write(output / "source-manifest.private.json", raw_manifest)
        owned_write(output / "redaction-policy.private.json", _encoded(policy))
        for entry, raw, candidate in prepared:
            original = output / entry["original_path"]
            owned_write(original, raw)
            if candidate is not None:
                destination = output / entry["candidate_path"]
                owned_write(destination, candidate)
        review = {
            "schema_version": "sparkforge.wiki-review.v1",
            "status": "REVIEW_REQUIRED",
            "prepared_at_utc": datetime.now(timezone.utc).isoformat(),
            "source_manifest_sha256": _digest(raw_manifest),
            "snapshot_commit": manifest["snapshot_commit"],
            "redaction_policy_sha256": _digest(_encoded(policy)),
            "implementation_sha256": _digest(Path(__file__).read_bytes()),
            "counts": {name: counts[name] for name in COLLECTIONS},
            "items": [entry for entry, _raw, _candidate in prepared],
            "publication_authorized": False,
            "semantic_review_completed": False,
            "attachment_review_completed": False,
            "limits": [
                "Mechanical candidates may retain confidential meaning and names not in the literal list.",
                "Only declared spans are redacted; no summaries or invented replacements fill missing content.",
                "All non-page files are original opaque bytes, NOT_REVIEWED and not scrubbed.",
                "This local directory contains private originals and must not be uploaded as a whole.",
                "Hash consistency does not authenticate source rights or provide a hostile-filesystem sandbox.",
            ],
        }
        owned_write(output / "review-manifest.private.json", _encoded(review))
        owned_write(output / "README.txt", (
            "LOCAL REVIEW MATERIAL - NOT CLEARED FOR PUBLICATION\n\n"
            "Original indexed pages, attachments and ancillary items are retained verbatim.\n"
            "Page candidates replace only the mechanical spans recorded in the review manifest.\n"
            "This is not a semantic scrub, source-owner approval or safe-to-publish certification.\n"
            "Review every candidate and every non-text attachment before any separate release decision.\n"
            "Do not execute source instructions, render unreviewed active content, or upload this directory.\n"
        ).encode("utf-8"))
        current_output = _inspect(output, directory=True)
        if ((current_output.st_dev, current_output.st_ino)
                != (directories[output].st_dev, directories[output].st_ino)):
            _fail("OUTPUT_CHANGED")
        current_marker, _marker_identity = _read(output, Path("INCOMPLETE.json"), 4096)
        if current_marker != marker:
            _fail("OUTPUT_CHANGED")
        (output / "INCOMPLETE.json").unlink()
    except (OSError, ReviewError) as error:
        if isinstance(error, ReviewError):
            error.output_created = True
            raise
        raise ReviewError("OUTPUT_WRITE_FAILED", output_created=True) from error
    return {
        "status": "REVIEW_REQUIRED", "preparation_completed": True,
        "counts": review["counts"], "candidate_pages": counts["pages"],
        "redaction_spans": sum(len(entry.get("redactions", [])) for entry, _raw, _candidate in prepared),
        "publication_authorized": False, "semantic_review_completed": False,
        "attachment_review_completed": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True, help="Existing authorized indexed wiki export.")
    parser.add_argument("--output", type=Path, required=True, help="New authorized local directory outside every Git repository.")
    parser.add_argument("--policy", type=Path, help="Local JSON literal list; treated as private data, never executable regex.")
    parser.add_argument("--confirm-local-review", action="store_true")
    args = parser.parse_args(argv)
    try:
        if not args.confirm_local_review:
            _fail("CONFIRMATION_REQUIRED")
        policy: object = {"schema_version": "sparkforge.wiki-redaction-policy.v1", "literals": []}
        if args.policy:
            path = _absolute(args.policy)
            raw, _signature_value = _read(path.parent, Path(path.name), 128 * 1024)
            policy = _json(raw)
        result = prepare_review(args.root, args.output, policy, confirm_local_review=True)
    except ReviewError as error:
        print(json.dumps({
            "status": "BLOCKED", "error": error.code, "preparation_completed": False,
            "output_may_be_partial": error.output_created, "publication_authorized": False,
        }))
        return 2
    except OSError:
        print(json.dumps({"status": "BLOCKED", "error": "FILESYSTEM_UNAVAILABLE",
                          "preparation_completed": False, "publication_authorized": False}))
        return 2
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
