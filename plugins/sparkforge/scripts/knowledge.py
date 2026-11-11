"""Bounded, read-only adapters for explicitly supplied indexed snapshots.

Hashes establish agreement with the supplied index, not source authenticity,
permission, freshness, host qualification, or a semantic reuse decision.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import re
import stat
import sys
from urllib.parse import urlsplit


MAX_INDEX_BYTES = 8 * 1024 * 1024
MAX_SOURCE_BYTES = 1024 * 1024
MAX_MANIFEST_BYTES = 64 * 1024
MAX_TOTAL_READ_BYTES = 32 * 1024 * 1024
MAX_INDEX_ENTRIES = 10000
MAX_WIKI_PAGES = 2048
MAX_COMPONENTS = 256
MAX_DECLARED_RESOURCES = 128
MAX_RESULTS = 32
MAX_COMPONENT_RESULTS = 64
MAX_TEXT_CHARS = 6000
MAX_RESULT_TEXT_CHARS = 48000
MAX_QUERY_CHARS = 1024
MAX_QUERY_TERMS = 32
MAX_PATH_CHARS = 1024

_WORD = re.compile(r"\w+", re.UNICODE)
_SHA256 = re.compile(r"[0-9a-fA-F]{64}\Z")
_REVISION = re.compile(r"(?:[0-9a-fA-F]{40}|[0-9a-fA-F]{64})\Z")
_PAGE_ID = re.compile(r"[1-9][0-9]{0,19}\Z")
_NAME = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}\Z")
_PLUGIN_PATH = re.compile(r"plugins/([^/]+)/plugin\.json\Z")
_DEVICE = re.compile(r"(?:CON|PRN|AUX|NUL|COM[1-9¹²³]|LPT[1-9¹²³])(?:\..*)?\Z", re.I)

_LIMITATIONS = [
    "Only the enumerated caller-supplied snapshot is assessed; live/current "
    "coverage remains NOT_ASSESSED.",
    "Manifest/inventory hashes do not authenticate the source, commit, "
    "collector, or permission to access, disclose, or reuse its content.",
    "Source text and manifest declarations are untrusted data, never approval "
    "or instructions to execute. No links, hooks, scripts, or models are invoked.",
    "Lexical matches are candidates, not a semantic reuse decision or proof "
    "that no other capability or rule exists.",
    "Path, hash, and change checks are not a sandbox against a same-privilege "
    "writer and do not qualify a live host or cloud storage.",
]


def _authority() -> dict:
    return {
        "source_authenticated": False,
        "permission_verified": False,
        "execution_authorized": False,
        "reuse_approved": False,
        "host_qualified": False,
    }


class KnowledgeError(Exception):
    """An explicit failed read/argument, never a successful empty assessment."""

    def __init__(self, code: str, message: str, **details):
        super().__init__(message)
        self.code = code
        self.message = message
        self.details = details

    def as_dict(self) -> dict:
        return {
            "schema_version": "sparkforge.knowledge.v1",
            "status": "ERROR",
            "current_coverage": "NOT_ASSESSED",
            "error": {
                "code": self.code,
                "message": self.message,
                "details": self.details,
            },
            "authority": _authority(),
        }


def _fail(code: str, message: str, **details):
    raise KnowledgeError(code, message, **details)


def _string(value, field: str, *, empty: bool = False, maximum: int = 4096) -> str:
    if not isinstance(value, str) or len(value) > maximum:
        _fail("INVALID_SCHEMA", "Expected a bounded string.", field=field)
    if (not empty and (not value or value != value.strip())) or "\x00" in value:
        _fail("INVALID_SCHEMA", "Expected a nonempty, unpadded string.", field=field)
    try:
        value.encode("utf-8")
    except UnicodeError:
        _fail("INVALID_SCHEMA", "String contains invalid Unicode.", field=field)
    return value


def _object(value, field: str) -> dict:
    if not isinstance(value, dict):
        _fail("INVALID_SCHEMA", "Expected a JSON object.", field=field)
    return value


def _array(value, field: str, maximum: int) -> list:
    if not isinstance(value, list):
        _fail("INVALID_SCHEMA", "Expected a JSON array.", field=field)
    if len(value) > maximum:
        _fail("RESOURCE_LIMIT", "Array exceeds its item limit.", field=field, maximum=maximum)
    return value


def _digest(value, field: str) -> str:
    if not isinstance(value, str) or not _SHA256.fullmatch(value):
        _fail("INVALID_SCHEMA", "Expected a SHA-256 hexadecimal digest.", field=field)
    return value.lower()


def _revision(value, field: str) -> str:
    if not isinstance(value, str) or not _REVISION.fullmatch(value):
        _fail("INVALID_SCHEMA", "Expected an exact Git object revision.", field=field)
    return value.lower()


def _size(value, field: str) -> int:
    if type(value) is not int or value < 0:
        _fail("INVALID_SCHEMA", "Expected a nonnegative integer byte count.", field=field)
    return value


def _page_id(value, field: str) -> str:
    if type(value) is int:
        value = str(value)
    if not isinstance(value, str) or not _PAGE_ID.fullmatch(value):
        _fail("INVALID_SCHEMA", "Expected a positive canonical numeric page ID.", field=field)
    return value


def _relative(value, field: str, *, package: bool = False) -> str:
    value = _string(value, field, maximum=MAX_PATH_CHARS).replace("\\", "/")
    if package and value.startswith("./"):
        value = value[2:]
    parts = value.split("/")
    if any(
        not part or part in (".", "..") or part.endswith((" ", "."))
        or any(ord(char) < 32 or char in ':*?"<>|' for char in part)
        or _DEVICE.fullmatch(part)
        for part in parts
    ):
        _fail("UNSAFE_PATH", "Expected an unambiguous relative file path.", field=field)
    return "/".join(parts)


def _unique(value: str, seen: set, field: str, code: str) -> None:
    key = value.casefold()
    if key in seen:
        _fail(code, "Duplicate or case/separator-aliased identity.", field=field)
    seen.add(key)


def _pairs(pairs: list) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            _fail("DUPLICATE_JSON_KEY", "Duplicate JSON object key.")
        result[key] = value
    return result


def _constant(_value):
    _fail("INVALID_JSON", "Non-finite JSON numbers are not supported.")


def _float(value: str) -> float:
    number = float(value)
    if not math.isfinite(number):
        _constant(value)
    return number


def _integer(value: str) -> int:
    if len(value) > 32:
        _fail("INVALID_JSON", "JSON integer exceeds the supported size.")
    return int(value)


def _decode(raw: bytes, path: str) -> str:
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeError:
        _fail("INVALID_ENCODING", "Source is not valid UTF-8.", path=path)
    if "\x00" in text:
        _fail("INVALID_ENCODING", "Source contains a NUL character.", path=path)
    return text


def _json(raw: bytes, path: str) -> dict:
    text = _decode(raw, path)
    if not text.strip():
        _fail("EMPTY_DOCUMENT", "The JSON document is empty.", path=path)
    try:
        value = json.loads(
            text, object_pairs_hook=_pairs, parse_constant=_constant,
            parse_float=_float, parse_int=_integer,
        )
    except (ValueError, RecursionError):
        _fail("INVALID_JSON", "Malformed or excessively nested JSON.", path=path)
    return _object(value, path)


def _unsafe_reparse(info) -> bool:
    if stat.S_ISLNK(info.st_mode):
        return True
    if not getattr(info, "st_file_attributes", 0) & 0x400:
        return False
    # Cloud placeholders are not name-surrogate redirects. Unknown reparse
    # types, junctions and symlinks are refused rather than followed.
    tag = getattr(info, "st_reparse_tag", 0)
    return tag & 0xFFFF0FFF != 0x9000001A


def _inspect(path: Path):
    try:
        for part in (*reversed(path.parents), path):
            info = part.lstat()
            if _unsafe_reparse(info):
                _fail("UNSAFE_PATH", "Links or redirecting/unknown reparse points are refused.",
                      path=str(part))
        return info
    except FileNotFoundError:
        _fail("SOURCE_UNAVAILABLE", "An indexed file or explicit source location is missing.",
              path=str(path))
    except (OSError, ValueError):
        _fail("SOURCE_UNAVAILABLE", "Cannot inspect the explicit source location.", path=str(path))


def _location(value: Path, field: str) -> Path:
    if not isinstance(value, Path):
        _fail("INVALID_ARGUMENT", "Source locations must be pathlib.Path values.", field=field)
    if "\x00" in str(value) or str(value).startswith(("\\\\", "//")):
        _fail("UNSAFE_PATH", "Network/device paths are outside the local snapshot interface.",
              field=field)
    if value.drive and not value.is_absolute():
        _fail("UNSAFE_PATH", "Drive-relative paths are ambiguous.", field=field)
    try:
        absolute = value.absolute()
        _inspect(absolute)
        return absolute.resolve(strict=True)
    except (OSError, ValueError, RuntimeError):
        _fail("SOURCE_UNAVAILABLE", "Cannot resolve the explicit source location.", field=field)


class _Root:
    def __init__(self, path: Path, field: str):
        self.requested = path
        self.path = _location(path, field)
        info = _inspect(self.path)
        if not stat.S_ISDIR(info.st_mode):
            _fail("INVALID_ARGUMENT", "Expected a source directory.", field=field)
        self.identity = (info.st_dev, info.st_ino)

    def check(self) -> None:
        actual = _location(self.requested, "root")
        info = _inspect(actual)
        if actual != self.path or (info.st_dev, info.st_ino) != self.identity:
            _fail("SOURCE_CHANGED", "The source root changed during the read.")

    def file(self, relative: str):
        self.check()
        path = self.path.joinpath(*relative.split("/"))
        info = _inspect(path)
        try:
            resolved = path.resolve(strict=True)
        except (OSError, ValueError, RuntimeError):
            _fail("SOURCE_UNAVAILABLE", "Cannot resolve the indexed file.", path=relative)
        if not resolved.is_relative_to(self.path):
            _fail("UNSAFE_PATH", "Indexed file escapes its explicit source root.", path=relative)
        if not stat.S_ISREG(info.st_mode):
            _fail("UNSAFE_PATH", "Indexed content must be a regular file.", path=relative)
        if info.st_nlink > 1:
            _fail("UNSAFE_PATH", "Hard-linked files are not supported snapshot inputs.", path=relative)
        return resolved, info


def _signature(info) -> tuple:
    signature = _binding(info)
    # Windows handle ctime can change on an unchanged, read-only cloud-backed
    # file. Identity, size, mtime and the required content hash remain binding.
    return signature if os.name == "nt" else (*signature, info.st_ctime_ns)


def _binding(info) -> tuple:
    return (
        info.st_dev, info.st_ino, info.st_mode, info.st_nlink, info.st_size,
        info.st_mtime_ns,
    )


def _opener(path, flags):
    return os.open(path, flags | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0))


class _Reader:
    def __init__(self):
        self.bytes_read = 0
        self.records = []

    def read(self, root: _Root, relative: str, maximum: int, *,
             sha256: str | None = None, expected_size: int | None = None) -> tuple[bytes, str]:
        path, before = root.file(relative)
        if before.st_size > maximum:
            _fail("RESOURCE_LIMIT", "File exceeds the byte limit.", path=relative, maximum=maximum)
        if self.bytes_read + before.st_size > MAX_TOTAL_READ_BYTES:
            _fail("RESOURCE_LIMIT", "The operation exceeds its total read limit.",
                  maximum=MAX_TOTAL_READ_BYTES)
        try:
            with open(path, "rb", opener=_opener) as stream:
                opened = os.fstat(stream.fileno())
                if _binding(before) != _binding(opened):
                    _fail("SOURCE_CHANGED", "File changed before it could be read.", path=relative)
                current, info = root.file(relative)
                if current != path or _signature(info) != _signature(before):
                    _fail("SOURCE_CHANGED", "File binding changed before reading.", path=relative)
                raw = stream.read(maximum + 1)
                after = os.fstat(stream.fileno())
        except OSError:
            _fail("SOURCE_UNAVAILABLE", "Cannot read the indexed file.", path=relative)
        if _signature(opened) != _signature(after) or len(raw) != before.st_size:
            _fail("SOURCE_CHANGED", "File changed while being read.", path=relative)
        current, info = root.file(relative)
        if current != path or _signature(info) != _signature(before):
            _fail("SOURCE_CHANGED", "File binding changed while being read.", path=relative)
        self.bytes_read += len(raw)
        digest = hashlib.sha256(raw).hexdigest()
        if sha256 is not None and digest != sha256:
            _fail("HASH_MISMATCH", "File bytes do not match the supplied index.", path=relative,
                  expected_sha256=sha256, observed_sha256=digest)
        if expected_size is not None and len(raw) != expected_size:
            _fail("SIZE_MISMATCH", "File size does not match the supplied index.", path=relative)
        self.records.append((root, relative, _signature(info)))
        return raw, digest

    def finish(self) -> None:
        for root, relative, expected in self.records:
            try:
                _, info = root.file(relative)
            except KnowledgeError as error:
                if error.code == "SOURCE_UNAVAILABLE":
                    _fail("SOURCE_CHANGED", "A read source disappeared before completion.", path=relative)
                raise
            if _signature(info) != expected:
                _fail("SOURCE_CHANGED", "A source changed before completion.", path=relative)


def _query(value, *, optional: bool = False) -> tuple[str, set[str]]:
    if not isinstance(value, str) or len(value) > MAX_QUERY_CHARS or "\x00" in value:
        _fail("INVALID_ARGUMENT", "Query must be a bounded string.", maximum=MAX_QUERY_CHARS)
    try:
        value.encode("utf-8")
    except UnicodeError:
        _fail("INVALID_ARGUMENT", "Query contains invalid Unicode.")
    terms = {match.group().casefold() for match in _WORD.finditer(value)}
    if not terms and not (optional and not value.strip()):
        _fail("INVALID_ARGUMENT", "A lexical query needs at least one word.")
    if len(terms) > MAX_QUERY_TERMS:
        _fail("RESOURCE_LIMIT", "Too many query terms.", maximum=MAX_QUERY_TERMS)
    return value, terms


def _limit(value) -> int:
    if type(value) is not int or not 1 <= value <= MAX_RESULTS:
        _fail("INVALID_ARGUMENT", "Result limit must be an integer in the supported range.",
              minimum=1, maximum=MAX_RESULTS)
    return value


def _terms_in(text: str, terms: set[str]) -> set[str]:
    return {match.group().casefold() for match in _WORD.finditer(text)
            if match.group().casefold() in terms}


def _score(terms: set[str], metadata: str, text: str) -> int:
    named = _terms_in(metadata, terms)
    body = _terms_in(text, terms)
    return 4 * len(named) + len(body) if terms <= named | body else 0


def _citation(category: str, locator: str, revision: str, sha256: str) -> dict:
    return {"source": category, "locator": locator, "revision": revision, "sha256": sha256}


def _item(kind: str, identity: str, path: str, citation: dict, **data) -> dict:
    return {
        "kind": kind, "identity": identity, "path": path, "citation": citation,
        "revision": citation["revision"], "sha256": citation["sha256"],
        "data_trust": "UNTRUSTED_SOURCE",
        "evidence_class": "PINNED_SOURCE_OBSERVATION",
        **data,
    }


def _select(candidates: list[dict], limit: int, terms: set[str]) -> tuple[list, dict, list]:
    items = []
    omissions = []
    remaining = MAX_RESULT_TEXT_CHARS
    for candidate in candidates:
        if len(items) == limit:
            omissions.append({"identity": candidate["identity"], "reason": "RESULT_LIMIT"})
            continue
        item = dict(candidate)
        if "_text" in item:
            text = item.pop("_text")
            if text and not remaining:
                omissions.append({"identity": item["identity"], "reason": "TEXT_BUDGET"})
                continue
            count = min(MAX_TEXT_CHARS, remaining)
            start = 0
            if len(text) > count:
                match = next((match for match in _WORD.finditer(text)
                              if match.group().casefold() in terms), None)
                if match is not None:
                    start = max(0, min(match.start() - 160, len(text) - count))
            end = min(len(text), start + count)
            item["selected_text"] = text[start:end]
            item["content_state"] = "TEXT" if text.strip() else "EMPTY"
            item["selection"] = {
                "start_char": start, "end_char": end, "total_chars": len(text),
                "truncated": start != 0 or end != len(text),
            }
            remaining -= end - start
        items.append(item)
    text_truncated = any(item.get("selection", {}).get("truncated", False) for item in items)
    return items, {
        "requested_limit": limit,
        "max_index_bytes": MAX_INDEX_BYTES,
        "max_source_bytes": MAX_SOURCE_BYTES,
        "max_manifest_bytes": MAX_MANIFEST_BYTES,
        "max_total_read_bytes": MAX_TOTAL_READ_BYTES,
        "max_index_entries": MAX_INDEX_ENTRIES,
        "max_wiki_pages": MAX_WIKI_PAGES,
        "max_components": MAX_COMPONENTS,
        "max_declared_resources": MAX_DECLARED_RESOURCES,
        "max_text_chars_per_item": MAX_TEXT_CHARS,
        "max_result_text_chars": MAX_RESULT_TEXT_CHARS,
        "results_truncated": bool(omissions),
        "text_truncated": text_truncated,
        "partial": bool(omissions) or text_truncated,
        "omitted_items": len(omissions),
    }, omissions


def _result(reader: _Reader, source: dict, candidates: list, limit: int,
            terms: set[str], scope: dict, omissions: list | None = None) -> dict:
    items, limits, output_omissions = _select(candidates, limit, terms)
    scope = dict(scope)
    scope.update(
        matched_count=len(candidates), returned_count=len(items),
        omissions=(omissions or []) + output_omissions,
    )
    limits["partial"] = limits["partial"] or bool(omissions)
    limits["bytes_read"] = reader.bytes_read
    reader.finish()
    return {
        "schema_version": "sparkforge.knowledge.v1",
        "status": "ASSESSED_SNAPSHOT" if items else "NO_MATCH",
        "source": source,
        "current_coverage": "NOT_ASSESSED",
        "items": items,
        "scope": scope,
        "limits": limits,
        "authority": _authority(),
        "limitations": list(_LIMITATIONS),
    }


def _wiki_index(root: _Root, reader: _Reader) -> tuple[dict, list]:
    raw, index_sha = reader.read(root, "manifest.json", MAX_INDEX_BYTES)
    manifest = _json(raw, "manifest.json")
    revision = _revision(manifest.get("snapshot_commit"), "snapshot_commit")
    pages = _array(manifest.get("pages"), "pages", MAX_WIKI_PAGES)
    if not pages:
        _fail("EMPTY_INDEX", "The wiki manifest contains no pages.")
    corpus_id = _string(manifest.get("corpus_id", "explicit-wiki-snapshot"), "corpus_id")
    ids, local_paths, wiki_paths, urls = set(), set(), set(), set()
    normalized = []
    for entry in pages:
        entry = _object(entry, "pages[]")
        page_id = _page_id(entry.get("page_id"), "pages[].page_id")
        _unique(page_id, ids, "pages[].page_id", "DUPLICATE_ID")
        path = _string(entry.get("path"), "pages[].path", maximum=MAX_PATH_CHARS)
        _unique(path.replace("\\", "/"), wiki_paths, "pages[].path", "DUPLICATE_PATH")
        local = _relative(entry.get("local_path"), "pages[].local_path")
        _unique(local, local_paths, "pages[].local_path", "DUPLICATE_PATH")
        entry_revision = _revision(entry.get("snapshot_commit"), "pages[].snapshot_commit")
        if entry_revision != revision:
            _fail("REVISION_MISMATCH", "Wiki page belongs to a different snapshot.", page_id=page_id)
        status = _string(entry.get("status"), "pages[].status")
        if status != "EXPORTED":
            _fail("SOURCE_UNAVAILABLE", "Wiki index contains an unexported page.", page_id=page_id)
        sha256 = _digest(entry.get("sha256"), "pages[].sha256")
        url = _string(entry.get("canonical_url"), "pages[].canonical_url")
        try:
            parsed = urlsplit(url)
            valid_url = (
                parsed.scheme in ("https", "http") and parsed.netloc and parsed.hostname
                and not parsed.username and not parsed.password
                and not any(char.isspace() or ord(char) < 32 for char in url)
            )
        except ValueError:
            valid_url = False
        if not valid_url:
            _fail("INVALID_SCHEMA", "Expected a canonical HTTP(S) citation URL.",
                  field="pages[].canonical_url")
        _unique(url, urls, "pages[].canonical_url", "DUPLICATE_ID")
        size = _size(entry["bytes"], "pages[].bytes") if "bytes" in entry else None
        if "text_encoding" in entry:
            encoding = _string(entry["text_encoding"], "pages[].text_encoding").casefold()
            if encoding not in ("utf-8", "utf-8-sig"):
                _fail("INVALID_ENCODING", "Only UTF-8 snapshots are supported.", page_id=page_id)
        title = _string(entry.get("title", ""), "pages[].title", empty=True)
        normalized.append({
            "page_id": page_id, "path": path, "local_path": local, "sha256": sha256,
            "canonical_url": url, "bytes": size, "title": title,
        })
    return {
        "kind": "WIKI_SNAPSHOT", "identity": corpus_id, "revision": revision,
        "root": str(root.path),
        "index": {"path": str(root.path / "manifest.json"), "sha256": index_sha},
    }, normalized


def wiki_context(root: Path, query: str, *, page_ids=None, limit=6) -> dict:
    """Read verified originals; explicit IDs select pages without fuzzy filtering."""
    limit = _limit(limit)
    requested = None
    if page_ids is not None:
        if not isinstance(page_ids, (list, tuple)) or not page_ids:
            _fail("INVALID_ARGUMENT", "page_ids must be a nonempty list or tuple of exact IDs.")
        if len(page_ids) > MAX_RESULTS:
            _fail("RESOURCE_LIMIT", "Too many explicit page IDs.", maximum=MAX_RESULTS)
        requested, seen = [], set()
        for value in page_ids:
            try:
                identifier = _page_id(value, "page_ids")
            except KnowledgeError:
                _fail("INVALID_ARGUMENT", "page_ids contains an invalid exact page ID.")
            _unique(identifier, seen, "page_ids", "DUPLICATE_ID")
            requested.append(identifier)
    query, terms = _query(query, optional=requested is not None)
    reader, corpus = _Reader(), _Root(root, "root")
    source, pages = _wiki_index(corpus, reader)
    by_id = {page["page_id"]: page for page in pages}
    if requested is not None:
        missing = [identifier for identifier in requested if identifier not in by_id]
        if missing:
            _fail("UNKNOWN_PAGE_ID", "Requested page IDs are outside this index.", page_ids=missing)
        selected = [by_id[identifier] for identifier in requested]
    else:
        selected = pages
    candidates, empty, scores = [], [], {}
    for page in selected:
        raw, digest = reader.read(
            corpus, page["local_path"], MAX_SOURCE_BYTES,
            sha256=page["sha256"], expected_size=page["bytes"],
        )
        text = _decode(raw, page["local_path"])
        if not text.strip():
            empty.append(page["page_id"])
        score = _score(terms, f'{page["path"]} {page["title"]} {page["page_id"]}', text)
        if requested is None and not score:
            continue
        citation = _citation("wiki", page["canonical_url"], source["revision"], digest)
        candidates.append(_item(
            "WIKI_PAGE", page["page_id"], page["local_path"], citation,
            wiki_path=page["path"], _text=text,
        ))
        scores[page["page_id"]] = score
    if requested is None:
        candidates.sort(key=lambda item: (-scores[item["identity"]], int(item["identity"])))
    return _result(reader, source, candidates, limit, terms, {
        "operation": "EXPLICIT_PAGE_IDS" if requested is not None else "LEXICAL_WIKI_SEARCH",
        "query": query, "indexed_pages": len(pages),
        "inspected_page_ids": [page["page_id"] for page in selected],
        "empty_page_ids": empty, "search_complete_for_scope": True,
        "uninspected_pages": len(pages) - len(selected),
        "review_depth": "VERIFIED_ORIGINALS_WITH_BOUNDED_EXCERPTS",
        "excluded": ["derived source-notes.json", "attachments", "unindexed files", "live wiki"],
    })


def _inventory(root: _Root, inventory: Path, reader: _Reader) -> tuple[dict, dict]:
    location = _location(inventory, "inventory")
    index_root = _Root(location.parent, "inventory_parent")
    raw, digest = reader.read(index_root, _relative(location.name, "inventory"), MAX_INDEX_BYTES)
    data = _json(raw, str(location))
    snapshot = _object(data.get("snapshot"), "snapshot")
    revision = _revision(snapshot.get("commit"), "snapshot.commit")
    repository = _string(snapshot.get("repository"), "snapshot.repository", maximum=512)
    entries = _array(data.get("entries"), "entries", MAX_INDEX_ENTRIES)
    if not entries:
        _fail("EMPTY_INDEX", "The repository inventory contains no entries.")
    paths, indexed = set(), {}
    for entry in entries:
        entry = _object(entry, "entries[]")
        path = _relative(entry.get("path"), "entries[].path")
        _unique(path, paths, "entries[].path", "DUPLICATE_PATH")
        kind = _string(entry.get("git_type"), "entries[].git_type")
        if kind not in ("blob", "tree", "commit"):
            _fail("INVALID_SCHEMA", "Unknown Git entry type.", path=path)
        sha256 = _digest(entry.get("sha256"), "entries[].sha256") if kind == "blob" else None
        if kind != "blob" and entry.get("sha256") is not None:
            _fail("INVALID_SCHEMA", "Non-file entries cannot supply file digests.", path=path)
        size = entry.get("size_bytes")
        if size is not None or (kind == "blob" and "size_bytes" in entry):
            size = _size(size, "entries[].size_bytes")
        mode = entry.get("mode")
        modes = {"blob": ("100644", "100755", "120000"), "tree": ("040000",), "commit": ("160000",)}
        if "mode" in entry and (not isinstance(mode, str) or mode not in modes[kind]):
            _fail("INVALID_SCHEMA", "Git mode conflicts with the entry type.", path=path)
        for field in ("snapshot_commit", "commit"):
            if field in entry and _revision(entry[field], f"entries[].{field}") != revision:
                _fail("REVISION_MISMATCH", "Inventory entry belongs to another revision.", path=path)
        indexed[path] = {"sha256": sha256, "bytes": size, "kind": kind, "mode": mode}
    return {
        "kind": "REPOSITORY_SNAPSHOT", "identity": repository, "revision": revision,
        "root": str(root.path), "index": {"path": str(location), "sha256": digest},
    }, indexed


def _indexed_read(root: _Root, indexed: dict, path: str, reader: _Reader, maximum: int):
    if path not in indexed:
        _fail("NOT_INDEXED", "A required resource is not in the supplied inventory.", path=path)
    entry = indexed[path]
    if entry["kind"] != "blob" or entry["mode"] == "120000":
        _fail("UNSAFE_PATH", "Selected resource is not an indexed regular Git file.", path=path)
    return reader.read(
        root, path, maximum, sha256=entry["sha256"], expected_size=entry["bytes"],
    )


def _manifest(raw: bytes, path: str) -> dict:
    data = _json(raw, path)
    name = _string(data.get("name"), "plugin.name", maximum=128)
    if not _NAME.fullmatch(name):
        _fail("INVALID_SCHEMA", "Component name must be a simple package name.", path=path)
    _relative(name, "plugin.name")
    version = _string(data.get("version"), "plugin.version", maximum=128)
    description = _string(data.get("description", ""), "plugin.description", empty=True)
    declarations, resources, seen = {}, [], set()
    for kind in ("skills", "agents"):
        values = _array(data.get(kind, []), f"plugin.{kind}", MAX_DECLARED_RESOURCES)
        declarations[kind] = []
        for value in values:
            resource = _relative(value, f"plugin.{kind}[]", package=True)
            if kind == "skills":
                if resource != "SKILL.md" and not resource.endswith("/SKILL.md"):
                    resource += "/SKILL.md"
            elif not resource.endswith(".md"):
                _fail("INVALID_SCHEMA", "Only declared Markdown agent resources are supported.",
                      path=resource)
            _unique(resource, seen, f"plugin.{kind}[]", "DUPLICATE_PATH")
            declarations[kind].append(value)
            resources.append(("SKILL" if kind == "skills" else "AGENT", resource))
    if len(resources) > MAX_DECLARED_RESOURCES:
        _fail("RESOURCE_LIMIT", "Too many declared resources.", maximum=MAX_DECLARED_RESOURCES)
    return {
        "projection": {
            "name": name, "version": version, "description": description,
            "skills": declarations["skills"], "agents": declarations["agents"],
        },
        "resources": resources,
    }


def _catalog(root: _Root, inventory: Path, reader: _Reader) -> tuple[dict, dict, list]:
    source, indexed = _inventory(root, inventory, reader)
    paths = sorted(path for path in indexed if _PLUGIN_PATH.fullmatch(path))
    if not paths:
        _fail("EMPTY_CATALOG", "The inventory contains no package plugin.json entries.")
    if len(paths) > MAX_COMPONENTS:
        _fail("RESOURCE_LIMIT", "Too many indexed components.", maximum=MAX_COMPONENTS)
    seen, components = set(), []
    for path in paths:
        raw, digest = _indexed_read(root, indexed, path, reader, MAX_MANIFEST_BYTES)
        manifest = _manifest(raw, path)
        name = manifest["projection"]["name"]
        _unique(name, seen, "plugin.name", "DUPLICATE_ID")
        components.append({"path": path, "sha256": digest, **manifest})
    for component in components:
        if component["projection"]["name"] != component["path"].split("/")[1]:
            _fail("IDENTITY_MISMATCH", "Manifest name differs from its indexed package directory.",
                  path=component["path"])
    return source, indexed, components


def _component_item(source: dict, component: dict, kind: str) -> dict:
    name, path = component["projection"]["name"], component["path"]
    citation = _citation(
        "repository", f'{source["identity"]}@{source["revision"]}:{path}',
        source["revision"], component["sha256"],
    )
    return _item(kind, name, path, citation, manifest=component["projection"])


def catalog_context(root: Path, inventory: Path, query: str, *, limit=8) -> dict:
    """Return lexical manifest candidates, not an automatic reuse recommendation."""
    limit, (query, terms) = _limit(limit), _query(query)
    reader, corpus = _Reader(), _Root(root, "root")
    source, indexed, components = _catalog(corpus, inventory, reader)
    candidates, scores = [], {}
    for component in components:
        manifest = component["projection"]
        score = _score(
            terms, manifest["name"],
            " ".join([manifest["description"], *manifest["skills"], *manifest["agents"]]),
        )
        if score:
            item = _component_item(source, component, "COMPONENT_CANDIDATE")
            item["resource_review"] = "NOT_ASSESSED"
            candidates.append(item)
            scores[item["identity"]] = score
    candidates.sort(key=lambda item: (-scores[item["identity"]], item["identity"]))
    return _result(reader, source, candidates, limit, terms, {
        "operation": "LEXICAL_CATALOG_SEARCH", "query": query,
        "inventory_entries": len(indexed),
        "inspected_components": [component["projection"]["name"] for component in components],
        "search_complete_for_scope": True, "review_depth": "MANIFEST_PROJECTION_ONLY",
        "manifest_fields": ["name", "version", "description", "skills", "agents"],
        "excluded": ["resource bodies", "other manifest fields", "unindexed files", "live catalog"],
    })


def component_context(root: Path, inventory: Path, name: str) -> dict:
    """Inspect one exact component's manifest, indexed README and declared resources."""
    if not isinstance(name, str) or not _NAME.fullmatch(name):
        _fail("INVALID_ARGUMENT", "Component name must be an exact simple package name.")
    try:
        _relative(name, "name")
    except KnowledgeError:
        _fail("INVALID_ARGUMENT", "Component name is not a portable package name.")
    reader, corpus = _Reader(), _Root(root, "root")
    source, indexed, components = _catalog(corpus, inventory, reader)
    scope = {
        "operation": "EXACT_COMPONENT", "name": name, "inventory_entries": len(indexed),
        "inspected_components": [component["projection"]["name"] for component in components],
        "search_complete_for_scope": True, "verified_resource_paths": [],
        "review_depth": "MANIFEST_PROJECTION_AND_SELECTED_DECLARED_TEXT",
        "manifest_fields": ["name", "version", "description", "skills", "agents"],
        "excluded": [
            "other manifest fields", "hooks", "scripts", "undeclared resources",
            "unindexed README/content", "linked resources", "live catalog",
        ],
    }
    component = next((value for value in components if value["projection"]["name"] == name), None)
    if component is None:
        return _result(reader, source, [], MAX_COMPONENT_RESULTS, set(), scope)
    prefix = f"plugins/{name}/"
    candidates = [_component_item(source, component, "COMPONENT_MANIFEST")]
    resources, omissions = [], []
    readme = prefix + "README.md"
    if readme in indexed:
        resources.append(("README", "README.md"))
    else:
        omissions.append({"identity": readme, "reason": "OPTIONAL_README_NOT_INDEXED"})
    resources += component["resources"]
    seen = {component["path"].casefold()}
    for kind, relative in resources:
        path = prefix + relative
        _unique(path, seen, "component resources", "DUPLICATE_PATH")
        raw, digest = _indexed_read(corpus, indexed, path, reader, MAX_SOURCE_BYTES)
        citation = _citation(
            "repository", f'{source["identity"]}@{source["revision"]}:{path}',
            source["revision"], digest,
        )
        candidates.append(_item(
            kind, path, path, citation, component=name, _text=_decode(raw, path),
        ))
        scope["verified_resource_paths"].append(path)
    return _result(reader, source, candidates, MAX_COMPONENT_RESULTS, set(), scope, omissions)


def source_context(root: Path, inventory: Path, paths: list[str]) -> dict:
    """Read only explicitly selected indexed UTF-8 files; code remains inert data."""
    if not isinstance(paths, list) or not paths:
        _fail("INVALID_ARGUMENT", "paths must be a nonempty list of indexed relative file paths.")
    if len(paths) > MAX_RESULTS:
        _fail("RESOURCE_LIMIT", "Too many selected source paths.", maximum=MAX_RESULTS)
    requested, seen = [], set()
    for value in paths:
        try:
            path = _relative(value, "paths[]")
        except KnowledgeError as error:
            if error.code == "INVALID_SCHEMA":
                _fail("INVALID_ARGUMENT", "Each selected source path must be a bounded nonempty string.")
            raise
        _unique(path, seen, "paths[]", "DUPLICATE_PATH")
        requested.append(path)
    reader, corpus = _Reader(), _Root(root, "root")
    source, indexed = _inventory(corpus, inventory, reader)
    candidates = []
    for path in requested:
        raw, digest = _indexed_read(corpus, indexed, path, reader, MAX_SOURCE_BYTES)
        citation = _citation(
            "repository", f'{source["identity"]}@{source["revision"]}:{path}',
            source["revision"], digest,
        )
        candidates.append(_item("SOURCE_FILE", path, path, citation, _text=_decode(raw, path)))
    return _result(reader, source, candidates, MAX_RESULTS, set(), {
        "operation": "EXPLICIT_SOURCE_PATHS", "inventory_entries": len(indexed),
        "requested_paths": requested, "verified_resource_paths": list(requested),
        "uninspected_files": sum(entry["kind"] == "blob" for entry in indexed.values()) - len(requested),
        "search_complete_for_scope": True,
        "review_depth": "EXPLICIT_INDEXED_TEXT_WITH_BOUNDED_EXCERPTS",
        "excluded": ["unselected files", "unindexed files", "linked resources", "live repository"],
    })


class _Parser(argparse.ArgumentParser):
    def error(self, message):
        _fail("INVALID_ARGUMENT", message)


def main(argv: list[str] | None = None) -> int:
    parser = _Parser(description=__doc__, allow_abbrev=False)
    commands = parser.add_subparsers(dest="command", required=True, parser_class=_Parser)
    wiki = commands.add_parser("wiki", allow_abbrev=False)
    wiki.add_argument("--root", type=Path, required=True)
    wiki.add_argument("--query", required=True)
    wiki.add_argument("--page-id", action="append", dest="page_ids")
    wiki.add_argument("--limit", type=int, default=6)
    catalog = commands.add_parser("catalog", allow_abbrev=False)
    catalog.add_argument("--root", type=Path, required=True)
    catalog.add_argument("--inventory", type=Path, required=True)
    catalog.add_argument("--query", required=True)
    catalog.add_argument("--limit", type=int, default=8)
    component = commands.add_parser("component", allow_abbrev=False)
    component.add_argument("--root", type=Path, required=True)
    component.add_argument("--inventory", type=Path, required=True)
    component.add_argument("--name", required=True)
    source = commands.add_parser("source", allow_abbrev=False)
    source.add_argument("--root", type=Path, required=True)
    source.add_argument("--inventory", type=Path, required=True)
    source.add_argument("--path", action="append", dest="paths", required=True)
    try:
        args = vars(parser.parse_args(argv))
        command = args.pop("command")
        operation = {
            "wiki": wiki_context, "catalog": catalog_context,
            "component": component_context, "source": source_context,
        }[command]
        result, code = operation(**args), 0
    except KnowledgeError as error:
        result, code = error.as_dict(), 2
    print(json.dumps(result, ensure_ascii=True, sort_keys=True))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
