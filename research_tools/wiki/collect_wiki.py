"""Explicitly configured, revision-bound Azure DevOps wiki export and offline checks.

No login, account discovery, token acquisition, model processing or publication
is performed. Network commands require a service configuration, an explicitly
selected token environment variable and --allow-network.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
import posixpath
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter, deque
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path

from .._common import (
    MAX_BYTES, atomic_bytes, child, inside, read_bytes, read_json, root_path,
    unique_records, verified_bytes, write_json, write_text,
)


API_VERSION = "7.1"


class CollectionError(ValueError):
    def __init__(self, code, http_status=None):
        super().__init__(code)
        self.code, self.http_status = code, http_status


def require(condition, code):
    if not condition:
        raise CollectionError(code)


def utc_now():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def sha256_file(root, path):
    return hashlib.sha256(read_bytes(inside(root, path))).hexdigest()


def git_blob_hash(root, path):
    data = read_bytes(inside(root, path))
    return hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()


def normalized_path(value):
    require(isinstance(value, str) and value.startswith("/"), "INVALID_SOURCE_PATH")
    require("\\" not in value and "\0" not in value and not value.startswith("//"), "INVALID_SOURCE_PATH")
    require(posixpath.normpath(value) == value, "NONCANONICAL_SOURCE_PATH")
    return value


def in_scope(path, root):
    return path == root or path.startswith(root.rstrip("/") + "/")


def identifier(prefix, value):
    return prefix + "-" + hashlib.sha256(value.encode("utf-8")).hexdigest()[:20]


def continued(headers):
    return headers.get("x-ms-continuationtoken") or headers.get("x-ms-continuation-token")


def selected_headers(headers):
    names = ("etag", "date", "content-type", "content-length", "x-ms-continuationtoken", "x-ms-continuation-token")
    return {name: headers[name] for name in names if name in headers}


def validate_service(config):
    config = dict(config)
    for key in ("base_url", "source_url", "principal_label", "project_name", "wiki_id"):
        require(isinstance(config.get(key), str) and bool(config[key].strip()), "MISSING_SERVICE_CONFIGURATION")
    require(type(config.get("root_page_id")) is int and config["root_page_id"] > 0, "INVALID_ROOT_PAGE_ID")
    require(re.fullmatch(r"[\w.-]+", config["wiki_id"]) is not None, "INVALID_WIKI_IDENTIFIER")
    require(isinstance(config.get("service_urls"), list) and config["service_urls"], "EXPLICIT_SERVICE_ALIASES_REQUIRED")
    for value in [config["base_url"], config["source_url"], *config["service_urls"]]:
        require(isinstance(value, str), "INVALID_SERVICE_URL")
        parsed = urllib.parse.urlsplit(value)
        require(
            parsed.scheme == "https" and bool(parsed.hostname) and not parsed.username
            and not parsed.password and parsed.port in (None, 443) and not parsed.query and not parsed.fragment,
            "INVALID_SERVICE_URL",
        )
        normalized_path(urllib.parse.unquote(parsed.path or "/"))
    require(config["base_url"].endswith("/_apis"), "BASE_MUST_BE_PROJECT_API_ROOT")
    require(config["base_url"].removesuffix("/_apis") in config["service_urls"], "BASE_NOT_IN_EXPLICIT_ALIASES")
    require(any(config["source_url"].startswith(url.rstrip("/") + "/") for url in config["service_urls"]), "SOURCE_URL_OUTSIDE_ALIASES")
    return config


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, file, code, message, headers, new_url):
        return None


class Client:
    def __init__(self, root, config, *, token_env, allow_network=False, expected_identity=None, max_attempts=1, max_bytes=MAX_BYTES):
        require(allow_network is True, "NETWORK_NOT_SELECTED")
        self.root, self.config = root_path(root, must_exist=False), validate_service(config)
        require(type(max_attempts) is int and 1 <= max_attempts <= 3, "INVALID_READ_ATTEMPTS")
        require(type(max_bytes) is int and 1 <= max_bytes <= MAX_BYTES, "INVALID_RESPONSE_BYTE_LIMIT")
        self.max_attempts, self.max_bytes = max_attempts, max_bytes
        binding = {key: self.config[key] for key in ("base_url", "wiki_id", "principal_label")}
        self.identity_hash = hashlib.sha256(json.dumps(binding, sort_keys=True).encode()).hexdigest()
        require(expected_identity in (None, self.identity_hash), "OPERATOR_PRINCIPAL_SELECTION_CHANGED")
        self.token = os.environ.get(token_env, "") if token_env else ""
        require(bool(self.token) and "\r" not in self.token and "\n" not in self.token, "SELECTED_TOKEN_UNAVAILABLE")
        self.opener = urllib.request.build_opener(NoRedirect())
        self.receipts = []

    def flush_receipts(self):
        if self.receipts:
            path = child(self.root, "request-receipts.jsonl")
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("a", encoding="utf-8", newline="\n") as stream:
                for receipt in self.receipts:
                    stream.write(json.dumps(receipt, ensure_ascii=True) + "\n")
            self.receipts.clear()

    def request(self, endpoint, parameters, operation, download=None, expected_blob=None):
        require(endpoint.startswith(self.config["base_url"] + "/"), "UNAPPROVED_SERVICE_ENDPOINT")
        require("?" not in endpoint and "#" not in endpoint, "INVALID_SERVICE_ENDPOINT")
        normalized_path(urllib.parse.unquote(urllib.parse.urlsplit(endpoint).path))
        url = endpoint + "?" + urllib.parse.urlencode({**parameters, "api-version": API_VERSION})
        headers = {
            "Authorization": "Bearer " + self.token,
            "Accept": "application/octet-stream" if download else "application/json",
            "Accept-Encoding": "identity", "User-Agent": "ExplicitLocalWikiResearch/1.0",
        }
        for attempt in range(1, self.max_attempts + 1):
            receipt = {
                "operation": operation, "method": "GET", "request_url": url,
                "attempt": attempt, "started_at_utc": utc_now(), "redirects_followed": False,
            }
            delay = 2 ** attempt
            try:
                request = urllib.request.Request(url, headers=headers, method="GET")
                with self.opener.open(request, timeout=90) as response:
                    response_headers = {key.lower(): value for key, value in response.headers.items()}
                    receipt.update(http_status=response.status, headers=selected_headers(response_headers))
                    data = response.read(self.max_bytes + 1)
                    require(len(data) <= self.max_bytes, "RESPONSE_BYTE_LIMIT")
                    expected_length = response_headers.get("content-length")
                    require(expected_length is None or int(expected_length) == len(data), "INCOMPLETE_DOWNLOAD")
                    if download:
                        actual = hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()
                        require(expected_blob is not None and actual == expected_blob, "DOWNLOADED_BLOB_HASH_MISMATCH")
                        destination = inside(self.root, download)
                        require(not destination.exists(), "DOWNLOAD_DESTINATION_ALREADY_EXISTS")
                        atomic_bytes(self.root, destination, data)
                        result = {"sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)}
                    else:
                        require(response_headers.get("content-type", "").split(";")[0] == "application/json", "UNEXPECTED_RESPONSE_MEDIA_TYPE")
                        result = json.loads(data)
                        receipt["response_sha256"] = hashlib.sha256(data).hexdigest()
                    receipt.update(status="SUCCESS", completed_at_utc=utc_now())
                    self.receipts.append(receipt)
                    self.flush_receipts()
                    return result, receipt
            except urllib.error.HTTPError as error:
                receipt.update(http_status=error.code, status="HTTP_ERROR")
                retry_after = error.headers.get("Retry-After")
                if retry_after and retry_after.isdigit():
                    delay = min(60, max(delay, int(retry_after)))
                retryable = error.code in (408, 429, 500, 502, 503, 504)
                code = "SERVICE_HTTP_" + str(error.code)
                error.close()
            except (urllib.error.URLError, TimeoutError, ConnectionError) as error:
                receipt.update(status="TRANSPORT_ERROR", exception_type=type(error).__name__)
                retryable, code = True, "TRANSPORT_ERROR"
            except (CollectionError, ValueError) as error:
                code = error.code if isinstance(error, CollectionError) else "INVALID_RESPONSE"
                receipt["status"], retryable = code, False
            receipt.update(completed_at_utc=utc_now(), retry_scheduled=retryable and attempt < self.max_attempts)
            self.receipts.append(receipt)
            self.flush_receipts()
            if not receipt["retry_scheduled"]:
                raise CollectionError(code, receipt.get("http_status"))
            print(json.dumps({"event": "READ_RETRY", "attempt": attempt, "delay_seconds": delay}), flush=True)
            time.sleep(delay)
        raise CollectionError("READ_ATTEMPTS_EXHAUSTED")


def version_parameters(commit):
    require(isinstance(commit, str) and re.fullmatch(r"[0-9a-f]{40}", commit) is not None, "INVALID_COMMIT_ID")
    return {"versionDescriptor.version": commit, "versionDescriptor.versionType": "commit"}


def git_endpoint(snapshot):
    repository_id = snapshot["repository_id"]
    require(re.fullmatch(r"[0-9a-fA-F]{8}(?:-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}", repository_id) is not None, "INVALID_REPOSITORY_ID")
    return snapshot["base_url"] + "/git/repositories/" + repository_id


def ref_commit(client, repository_endpoint, branch):
    reference = branch if branch.startswith("refs/heads/") else "refs/heads/" + branch
    parameters, seen, matches, requests = {"filter": reference.removeprefix("refs/"), "$top": 1000}, set(), [], 0
    while True:
        data, receipt = client.request(repository_endpoint + "/refs", parameters, "RESOLVE_WIKI_BRANCH")
        requests += 1
        values = data.get("value")
        require(isinstance(values, list), "INVALID_REF_RESPONSE")
        require(data.get("count", len(values)) == len(values), "REF_COUNT_MISMATCH")
        matches.extend(value for value in values if value.get("name") == reference)
        token = continued(receipt["headers"])
        if not token:
            break
        require(token not in seen, "REPEATED_REF_CONTINUATION")
        seen.add(token)
        parameters["continuationToken"] = token
    require(len(matches) == 1, "WIKI_BRANCH_NOT_UNIQUE")
    commit = matches[0].get("objectId")
    version_parameters(commit)
    return commit, requests


class HtmlReferences(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.targets = []

    def handle_starttag(self, tag, attributes):
        for name, value in attributes:
            if value and name in ("src", "href", "poster", "data"):
                self.targets.append(value)
            elif value and name == "srcset":
                if value.lstrip().startswith("data:"):
                    self.targets.append(value)
                else:
                    self.targets.extend(part.strip().split()[0] for part in value.split(",") if part.strip())


def markdown_parser():
    from markdown_it import MarkdownIt
    return MarkdownIt("commonmark", {"html": True})


def extract_references(text, parser):
    environment, found, code_lines = {}, [], set()
    tokens = parser.parse(text, environment)

    def walk(token, line):
        if token.map:
            line = token.map[0] + 1
        if token.type in ("fence", "code_block") and token.map:
            code_lines.update(range(token.map[0], token.map[1]))
        if token.type == "link_open":
            found.append((token.attrGet("href"), "MARKDOWN_LINK", line))
        elif token.type == "image":
            found.append((token.attrGet("src"), "MARKDOWN_IMAGE", line))
        elif token.type in ("html_inline", "html_block"):
            html_parser = HtmlReferences()
            html_parser.feed(token.content)
            found.extend((target, "HTML_ATTRIBUTE", line) for target in html_parser.targets)
        for token_child in token.children or []:
            walk(token_child, line)

    for token in tokens:
        walk(token, 1)
    for definition in environment.get("references", {}).values():
        found.append((definition["href"], "MARKDOWN_REFERENCE_DEFINITION", definition["map"][0] + 1))
    masked_lines = ["" if index in code_lines else line for index, line in enumerate(text.splitlines())]
    masked = "\n".join(masked_lines)
    # Wiki resizing syntax is not CommonMark.
    for match in re.finditer(r"!?\[[^\]\n]*\]\(\s*(<[^>\n]+>|[^\s\n]+?)\s+=\d*(?:x\d*)?\s*\)", masked):
        found.append((match.group(1).strip("<>"), "WIKI_RESIZED_IMAGE", masked[:match.start()].count("\n") + 1))
    for match in re.finditer(r"https?://[^\s<>\"'`]+", masked):
        target = match.group().rstrip(".,;*")
        while target.endswith(")") and target.count(")") > target.count("("):
            target = target[:-1]
        found.append((target, "BARE_URL", masked[:match.start()].count("\n") + 1))
    targets = {}
    for target, syntax, line in found:
        if not target:
            continue
        target = html.unescape(target).strip()
        entry = targets.setdefault(target, {"target": target, "syntaxes": [], "source_lines": []})
        if syntax not in entry["syntaxes"]:
            entry["syntaxes"].append(syntax)
        if line not in entry["source_lines"]:
            entry["source_lines"].append(line)
    unresolved = []
    decoded_targets = [urllib.parse.unquote(target) for target in targets]
    for number, line in enumerate(masked_lines, start=1):
        for _ in re.finditer(r"(?i)\.attachments(?:/|%2f)", line):
            decoded_line = urllib.parse.unquote(html.unescape(line))
            if not any(".attachments/" in target.lower() and target in decoded_line for target in decoded_targets):
                unresolved.append({"source_line": number, "status": "UNPARSED_ATTACHMENT_MARKER"})
    return list(targets.values()), unresolved


def source_text(root, path):
    body = read_bytes(inside(root, path))
    if body.startswith((b"\xff\xfe", b"\xfe\xff")):
        return body.decode("utf-16"), "UTF-16_WITH_BOM"
    return body.decode("utf-8-sig"), "UTF-8"


def local_reference_path(target, page, git=False):
    value = urllib.parse.unquote(target)
    require("\\" not in value and "\0" not in value and not value.startswith("//"), "INVALID_REFERENCE_PATH")
    base = page["git_path"] if git else page["path"]
    return posixpath.normpath(value if value.startswith("/") else posixpath.join(posixpath.dirname(base), value))


def classify_reference(target, page, snapshot, pages, backing):
    if target.startswith("aka.ms/"):
        return {"kind": "EXTERNAL_REFERENCE", "status": "SCHEMELESS_EXTERNAL_NOT_FETCHED"}
    parsed = urllib.parse.urlsplit(target)
    if target.startswith("#") or target == "":
        return {"kind": "LOCAL_FRAGMENT", "status": "PRESERVED_IN_SOURCE"}
    if parsed.scheme and parsed.scheme.lower() not in ("http", "https"):
        return {"kind": "UNSUPPORTED_URI_SCHEME", "status": "NOT_FETCHED"}
    query = urllib.parse.parse_qs(parsed.query, keep_blank_values=True)
    path = urllib.parse.unquote(parsed.path)
    is_service_url = bool(parsed.netloc) or "/_wiki/" in path or "/_apis/" in path
    attachment_path = page_id = page_path = None
    if is_service_url:
        if parsed.username or parsed.password or parsed.port not in (None, 443):
            return {"kind": "UNSUPPORTED_SERVICE_URL", "status": "NOT_FETCHED"}
        aliases = [urllib.parse.urlsplit(value) for value in snapshot.get("service_urls", [])]
        pieces = None
        if parsed.netloc:
            same_host = [alias for alias in aliases if parsed.netloc.casefold() == alias.netloc.casefold()]
            if not same_host or parsed.scheme != "https":
                return {"kind": "EXTERNAL_REFERENCE", "status": "OUT_OF_SCOPE_NOT_FETCHED"}
            for alias in same_host:
                prefix = urllib.parse.unquote(alias.path).rstrip("/") + "/"
                if path.casefold().startswith(prefix.casefold()):
                    pieces = path[len(prefix):].split("/")
                    break
            if pieces is None:
                return {"kind": "OTHER_PROJECT_REFERENCE", "status": "OUT_OF_SCOPE_NOT_FETCHED"}
        else:
            pieces = path.strip("/").split("/")
            projects = {str(snapshot.get(key, "")).casefold() for key in ("project_id", "project_name")}
            if not pieces or pieces[0].casefold() not in projects:
                return {"kind": "OTHER_PROJECT_REFERENCE", "status": "OUT_OF_SCOPE_NOT_FETCHED"}
            pieces = pieces[1:]
        lower = [piece.lower() for piece in pieces]
        wiki_aliases = (snapshot["wiki_id"].lower(), snapshot["wiki_name"].lower())
        if len(pieces) >= 3 and lower[:2] == ["_wiki", "wikis"] and lower[2] in wiki_aliases:
            if len(pieces) >= 4 and pieces[3].isdigit():
                page_id = int(pieces[3])
            page_path = (query.get("pagePath") or query.get("pagepath") or [None])[0]
            attachment_path = (query.get("attachmentPath") or [None])[0]
        elif len(pieces) >= 4 and lower[:3] == ["_apis", "wiki", "wikis"] and lower[3] in wiki_aliases:
            if len(pieces) >= 5 and lower[4] == "attachments":
                name = (query.get("name") or [None])[0]
                if name:
                    attachment_path = name if name.startswith("/") else "/.attachments/" + name
            elif len(pieces) >= 5 and lower[4] == "pages":
                if len(pieces) >= 6 and pieces[5].isdigit():
                    page_id = int(pieces[5])
                else:
                    page_path = (query.get("path") or [None])[0]
        elif len(pieces) >= 5 and lower[:3] == ["_apis", "git", "repositories"]:
            if lower[3] != snapshot["repository_id"].lower():
                return {"kind": "OTHER_REPOSITORY_REFERENCE", "status": "OUT_OF_SCOPE_NOT_FETCHED"}
            if lower[4] != "items":
                return {"kind": "UNSUPPORTED_SERVICE_REFERENCE", "status": "NOT_FETCHED"}
            item_path = (query.get("path") or query.get("scopePath") or [None])[0]
            if item_path and "/.attachments/" in item_path.lower():
                attachment_path = item_path
            elif item_path in backing:
                return {"kind": "IN_SCOPE_FILE", "status": "LOCAL_FILE_REFERENCE", "git_path": item_path}
            else:
                return {"kind": "OTHER_GIT_ITEM_REFERENCE", "status": "OUT_OF_SCOPE_NOT_FETCHED"}
        else:
            return {"kind": "OTHER_SERVICE_REFERENCE", "status": "OUT_OF_SCOPE_NOT_FETCHED"}
    else:
        resolved_git = local_reference_path(parsed.path, page, git=True)
        if "/.attachments/" in resolved_git.lower():
            attachment_path = resolved_git
        else:
            page_path = local_reference_path(parsed.path, page)
            if resolved_git in backing and not resolved_git.lower().endswith(".md"):
                return {"kind": "IN_SCOPE_FILE", "status": "LOCAL_FILE_REFERENCE", "git_path": resolved_git}
    if attachment_path is not None:
        attachment_path = normalized_path(posixpath.normpath(attachment_path))
        require("/.attachments/" in attachment_path.lower(), "INVALID_ATTACHMENT_SCOPE")
        requested_version = (query.get("versionDescriptor.version") or query.get("version") or [None])[0]
        if requested_version and requested_version not in {
            snapshot["commit"], snapshot["branch"], "GB" + snapshot["branch"],
            "GC" + snapshot["commit"], "refs/heads/" + snapshot["branch"],
        }:
            return {"kind": "CROSS_VERSION_ATTACHMENT_REFERENCE", "status": "UNSUPPORTED_NOT_FETCHED", "git_path": attachment_path}
        return {"kind": "WIKI_ATTACHMENT", "status": "PENDING", "git_path": attachment_path}
    for candidate in pages:
        if page_id is not None and candidate.get("page_id") == page_id:
            return {"kind": "IN_SCOPE_PAGE", "status": "LOCAL_PAGE_REFERENCE", "page_key": candidate["key"]}
        if page_path is not None and page_path in (
            candidate.get("path"), candidate.get("git_path"),
            candidate.get("git_path", "").removesuffix(".md"),
            urllib.parse.unquote(candidate.get("git_path", "")).removesuffix(".md"),
        ):
            return {"kind": "IN_SCOPE_PAGE", "status": "LOCAL_PAGE_REFERENCE", "page_key": candidate["key"]}
    if page_id is not None or page_path is not None:
        if page_path and in_scope(page_path, snapshot["root_path"]):
            return {"kind": "UNRESOLVED_IN_SCOPE_REFERENCE", "status": "TARGET_NOT_ENUMERATED"}
        return {"kind": "OUT_OF_SCOPE_WIKI_PAGE", "status": "NOT_FETCHED"}
    return {"kind": "UNSUPPORTED_REFERENCE", "status": "NOT_FETCHED"}


def preserve_preflight(root):
    for name in ("README.md", "manifest.json"):
        source, destination = child(root, name), child(root, "preflight/" + name)
        if source.exists() and not destination.exists():
            atomic_bytes(root, destination, read_bytes(source))


def prepare(root, config, *, token_env, allow_network=False, branch_metadata=False, resume=False, max_attempts=1):
    root, config = root_path(root, must_exist=False), validate_service(config)
    snapshot_path = child(root, "snapshot.json")
    if snapshot_path.exists():
        require(resume, "EXPLICIT_RESUME_REQUIRED")
        snapshot = read_json(snapshot_path)
        require("enumeration_completed_at_utc" not in snapshot, "ENUMERATION_ALREADY_COMPLETE")
        require(
            snapshot["base_url"] == config["base_url"]
            and snapshot["requested_wiki_id"] == config["wiki_id"]
            and snapshot["root_page_id"] == config["root_page_id"]
            and snapshot["service_urls"] == config["service_urls"],
            "SOURCE_SELECTION_CHANGED",
        )
        client = Client(
            root, config, token_env=token_env, allow_network=allow_network,
            expected_identity=snapshot["identity_fingerprint_sha256"], max_attempts=max_attempts,
        )
        if child(root, "enumeration.json").exists():
            atomic_bytes(root, child(root, f"attempts/enumeration-{time.time_ns()}.json"), read_bytes(child(root, "enumeration.json")))
    else:
        require(not resume, "NO_PREVIOUS_ENUMERATION")
        require(not root.exists() or not any(root.iterdir()), "INITIAL_OUTPUT_MUST_BE_EMPTY")
        client = Client(root, config, token_env=token_env, allow_network=allow_network, max_attempts=max_attempts)
        write_text(root, child(root, "README.md"), "# Local collection preflight\n\nNo publication or model-processing permission is granted by this tool.\n")
        write_json(root, child(root, "manifest.json"), {"schema_version": 1, "status": "PREFLIGHT", "publication_authorized": False})
        preserve_preflight(root)
        wiki_endpoint = config["base_url"] + "/wiki/wikis/" + urllib.parse.quote(config["wiki_id"], safe="")
        wiki, wiki_receipt = client.request(wiki_endpoint, {}, "WIKI_IDENTITY")
        root_page, root_receipt = client.request(
            wiki_endpoint + f"/pages/{config['root_page_id']}",
            {"includeContent": "false", "recursionLevel": "none"}, "ROOT_ID_RESOLUTION",
        )
        require(root_page.get("id") == config["root_page_id"], "ROOT_ID_MISMATCH")
        require(not root_page.get("content"), "UNEXPECTED_METADATA_CONTENT")
        versions = wiki.get("versions", [])
        require(len(versions) == 1 and versions[0].get("version"), "AMBIGUOUS_WIKI_VERSION")
        snapshot = {
            "schema_version": 2, "created_at_utc": utc_now(),
            "base_url": config["base_url"], "service_urls": config["service_urls"],
            "requested_wiki_id": config["wiki_id"], "source_url": config["source_url"],
            "root_page_id": config["root_page_id"], "wiki_id": wiki.get("id"), "wiki_name": wiki.get("name"),
            "project_id": wiki.get("projectId"), "project_name": config["project_name"],
            "repository_id": wiki.get("repositoryId"), "wiki_type": wiki.get("type"),
            "mapped_path": wiki.get("mappedPath"), "branch": versions[0]["version"],
            "root_path": normalized_path(root_page.get("path")),
            "root_git_path": normalized_path(root_page.get("gitItemPath")),
            "root_canonical_url": root_page.get("remoteUrl"),
            "identity_fingerprint_sha256": client.identity_hash,
            "identity_binding": "OPERATOR_LABEL_AND_SOURCE_SELECTION_NOT_AUTHENTICATED_BY_TOOL",
            "model_processing": "NOT_AUTHORIZED", "publication_authorized": False,
            "collection_mode": "LOCAL_READ_ONLY_SERVICE_EXPORT",
            "max_recorded_read_attempts": max_attempts,
            "initial_root_metadata_etag": root_receipt["headers"].get("etag"),
            "wiki_metadata_retrieved_at_utc": wiki_receipt["completed_at_utc"],
        }
        snapshot["commit"], snapshot["ref_enumeration_requests"] = ref_commit(
            client, git_endpoint(snapshot), snapshot["branch"],
        )
        snapshot["ref_pagination_exhausted"] = True
    wiki_endpoint = config["base_url"] + "/wiki/wikis/" + urllib.parse.quote(config["wiki_id"], safe="")
    commit, root_source, root_git_path = snapshot["commit"], snapshot["root_path"], snapshot["root_git_path"]
    if branch_metadata:
        head_before, _ = ref_commit(client, git_endpoint(snapshot), snapshot["branch"])
        require(head_before == commit, "BRANCH_MOVED_BEFORE_HIERARCHY_ENUMERATION")
        metadata_version = {"versionDescriptor.version": snapshot["branch"], "versionDescriptor.versionType": "branch"}
        snapshot.update(hierarchy_version_mode="BRANCH_METADATA_WITH_PINNED_GIT_RECONCILIATION", hierarchy_head_before=head_before)
    else:
        metadata_version = version_parameters(commit)
        snapshot["hierarchy_version_mode"] = "COMMIT_PINNED"
    write_json(root, snapshot_path, snapshot)
    queue, pages, seen, errors = deque([(root_source, None)]), [], set(), []
    while queue:
        path, parent_key = queue.popleft()
        require(path not in seen, "DUPLICATE_WIKI_PATH")
        require(in_scope(path, root_source), "WIKI_ENUMERATION_ESCAPED_SCOPE")
        seen.add(path)
        key = identifier("page", path)
        try:
            data, receipt = client.request(
                wiki_endpoint + "/pages",
                {"path": path, "includeContent": "false", "recursionLevel": "oneLevel", **metadata_version},
                "ENUMERATE_DIRECT_CHILDREN",
            )
            require(not continued(receipt["headers"]), "UNDOCUMENTED_WIKI_CONTINUATION")
            require(data.get("path") == path and not data.get("content"), "INVALID_WIKI_METADATA")
            if parent_key is None:
                require(data.get("id") == config["root_page_id"], "PINNED_ROOT_ID_MISMATCH")
            children = data.get("subPages")
            require(isinstance(children, list), "MISSING_CHILD_COLLECTION")
            child_paths = []
            for item in children:
                child_path = normalized_path(item.get("path"))
                require(posixpath.dirname(child_path) == path, "INVALID_DIRECT_CHILD")
                child_paths.append(child_path)
            require(len(set(child_paths)) == len(child_paths), "DUPLICATE_DIRECT_CHILD")
            queue.extend((child_path, key) for child_path in child_paths)
            pages.append({
                "key": key, "page_id": data.get("id"), "path": path, "parent_key": parent_key,
                "child_keys": [identifier("page", value) for value in child_paths],
                "git_path": normalized_path(data.get("gitItemPath")),
                "order": data.get("order"), "is_parent_page": data.get("isParentPage", False),
                "is_nonconformant": data.get("isNonConformant", False),
                "canonical_url": data.get("remoteUrl"), "source_api_url": data.get("url"),
                "metadata_etag": receipt["headers"].get("etag"),
                "metadata_retrieved_at_utc": receipt["completed_at_utc"],
                "snapshot_commit": commit, "enumeration_status": "DIRECT_CHILDREN_ENUMERATED", "status": "NOT_COLLECTED",
            })
        except CollectionError as error:
            pages.append({
                "key": key, "path": path, "parent_key": parent_key, "page_id": None,
                "child_keys": [], "snapshot_commit": commit, "enumeration_status": "FAILED",
                "status": "NOT_COLLECTED", "error_code": error.code, "http_status": error.http_status,
            })
            errors.append({"item_key": key, "error_code": error.code})
        write_json(root, child(root, "enumeration.json"), {"pages": pages, "pending_count": len(queue), "errors": errors})
    require(pages and pages[0]["enumeration_status"] != "FAILED", "PINNED_ROOT_UNAVAILABLE")
    endpoint = git_endpoint(snapshot) + "/items"
    root_item, _ = client.request(
        endpoint, {"path": root_git_path, "includeContentMetadata": "true", **version_parameters(commit)}, "ROOT_BACKING_ITEM",
    )
    require(root_item.get("path") == root_git_path and root_item.get("commitId") == commit, "ROOT_BACKING_MISMATCH")
    git_items = [root_item]
    subtree_path = root_git_path.removesuffix(".md")
    try:
        listing, receipt = client.request(
            endpoint, {"scopePath": subtree_path, "recursionLevel": "full", "includeContentMetadata": "true", **version_parameters(commit)},
            "ENUMERATE_BACKING_SUBTREE",
        )
        require(not continued(receipt["headers"]), "UNDOCUMENTED_GIT_ITEMS_CONTINUATION")
        values = listing.get("value")
        require(isinstance(values, list) and listing.get("count") == len(values), "GIT_ITEMS_COUNT_MISMATCH")
        for item in values:
            require(in_scope(normalized_path(item.get("path")), subtree_path), "BACKING_ENUMERATION_ESCAPED_SCOPE")
            require(item.get("commitId") == commit, "BACKING_COMMIT_MISMATCH")
        git_items.extend(values)
        backing_status = "ENUMERATED"
    except CollectionError as error:
        if error.http_status == 404 and len(pages) == 1 and not errors:
            backing_status = "NO_DESCENDANT_FOLDER"
        else:
            backing_status = "FAILED"
            errors.append({"operation": "ENUMERATE_BACKING_SUBTREE", "error_code": error.code})
    projected = [
        {key: item[key] for key in ("path", "objectId", "commitId", "gitObjectType", "isFolder", "isSymLink", "contentMetadata") if key in item}
        for item in git_items
    ]
    unique_records(projected, "path")
    page_git_paths = {page["git_path"] for page in pages if "git_path" in page}
    blob_paths = {item["path"] for item in projected if item.get("gitObjectType") == "blob"}
    listed_markdown = {path for path in blob_paths if path.lower().endswith(".md") and "/.attachments/" not in path.lower()}
    snapshot.update(
        enumeration_completed_at_utc=utc_now(), hierarchy_status="ENUMERATED" if not errors else "PARTIAL",
        hierarchy_pagination="Scoped direct-child enumeration; unexpected continuation headers fail closed.",
        backing_inventory_status=backing_status,
        backing_inventory_pagination="Scoped full recursion; response count checked; unexpected continuation rejected.",
        missing_backing_paths=sorted(page_git_paths - blob_paths),
        unlisted_markdown_paths=sorted(listed_markdown - page_git_paths),
    )
    if branch_metadata:
        head_after, _ = ref_commit(client, git_endpoint(snapshot), snapshot["branch"])
        snapshot.update(hierarchy_head_after=head_after, hierarchy_bracket_heads_match_snapshot=head_after == commit)
        if head_after != commit:
            snapshot["hierarchy_status"] = "REVISION_DRIFT"
            errors.append({"operation": "HIERARCHY_REVISION_CHECK", "error_code": "BRANCH_MOVED_DURING_ENUMERATION"})
    write_json(root, snapshot_path, snapshot)
    write_json(root, child(root, "enumeration.json"), {"pages": pages, "pending_count": 0, "errors": errors})
    write_json(root, child(root, "backing-items.json"), {"items": projected})
    return {
        "result": "FAIL" if errors or snapshot["missing_backing_paths"] or snapshot["unlisted_markdown_paths"] else "PASS",
        "phase": "ENUMERATED", "wiki_nodes": len(pages), "backing_blobs": len(blob_paths),
        "hierarchy_errors": len(errors), "source_content_output": False,
    }


def collect_blob(root, client, snapshot, item, destination, operation, previous=None):
    require(item.get("gitObjectType") == "blob", "NOT_A_GIT_BLOB")
    require(not item.get("isSymLink"), "SYMLINK_NOT_FOLLOWED")
    expected_hash = item.get("objectId")
    require(re.fullmatch(r"[0-9a-f]{40}", expected_hash or "") is not None, "INVALID_BLOB_ID")
    destination = inside(root, destination)
    if destination.exists():
        require(previous and previous.get("source_blob_id") == expected_hash, "EXISTING_FILE_WITHOUT_RECEIPT")
        require(previous.get("snapshot_commit") == snapshot["commit"], "EXISTING_FILE_REVISION_MISMATCH")
        verified_bytes(root, previous)
        require(git_blob_hash(root, destination) == expected_hash, "EXISTING_FILE_INTEGRITY_MISMATCH")
        return previous
    data, receipt = client.request(
        git_endpoint(snapshot) + "/items",
        {"path": item["path"], "download": "true", **version_parameters(snapshot["commit"])},
        operation, download=destination, expected_blob=expected_hash,
    )
    require(git_blob_hash(root, destination) == expected_hash, "DOWNLOADED_BLOB_HASH_MISMATCH")
    with destination.open("rb") as stream:
        lfs_pointer = stream.read(80).startswith(b"version https://git-lfs.github.com/spec/v1")
    return {
        "status": "LFS_POINTER_EXPORTED_TARGET_NOT_FETCHED" if lfs_pointer else "EXPORTED",
        "local_path": destination.relative_to(root).as_posix(), "source_blob_id": expected_hash,
        "verified_git_blob_sha1": expected_hash, "sha256": data["sha256"], "bytes": data["bytes"],
        "snapshot_commit": snapshot["commit"], "retrieved_at_utc": receipt["completed_at_utc"],
        "etag": receipt["headers"].get("etag"), "response_content_type": receipt["headers"].get("content-type"),
        "request_url": receipt["request_url"],
    }


def metadata_for_attachment(client, snapshot, path):
    data, receipt = client.request(
        git_endpoint(snapshot) + "/items",
        {"path": path, "includeContentMetadata": "true", **version_parameters(snapshot["commit"])},
        "ATTACHMENT_METADATA",
    )
    require(data.get("path") == path and data.get("commitId") == snapshot["commit"], "ATTACHMENT_METADATA_MISMATCH")
    return {
        name: data[name] for name in ("path", "objectId", "commitId", "gitObjectType", "isSymLink", "contentMetadata") if name in data
    }, receipt


def manifest_counts(manifest):
    pages, attachments, references = manifest["pages"], manifest["attachments"], manifest["references"]
    roots = sum(page.get("parent_key") is None for page in pages)
    return {
        "root_pages": roots, "descendant_pages": len(pages) - roots, "total_pages": len(pages),
        "pages_exported": sum(page.get("status") == "EXPORTED" for page in pages),
        "page_export_failures": sum(page.get("status") not in ("EXPORTED", "NOT_COLLECTED") for page in pages),
        "pages_not_yet_collected": sum(page.get("status") == "NOT_COLLECTED" for page in pages),
        "attachment_items_discovered": len(attachments),
        "attachments_exported": sum(item.get("status") == "EXPORTED" for item in attachments),
        "attachment_export_failures": sum(item.get("status") != "EXPORTED" for item in attachments),
        "ancillary_files_exported": sum(item.get("status") == "EXPORTED" for item in manifest["ancillary_items"]),
        "ancillary_file_failures": sum(item.get("status") != "EXPORTED" for item in manifest["ancillary_items"]),
        "reference_records": len(references), "reference_kinds": dict(sorted(Counter(ref["kind"] for ref in references).items())),
        "unparsed_attachment_markers": len(manifest["unparsed_attachment_markers"]),
        "pages_without_reference_scan": sum(page.get("reference_scan_status") != "PARSED" for page in pages),
        "pages_semantically_synthesized": manifest.get("synthesis", {}).get("content_pages_synthesized", 0),
    }


def coverage_status(manifest):
    counts = manifest_counts(manifest)
    gaps = sum(counts[key] for key in (
        "page_export_failures", "pages_not_yet_collected", "attachment_export_failures",
        "ancillary_file_failures", "unparsed_attachment_markers", "pages_without_reference_scan",
    ))
    gaps += sum(counts["reference_kinds"].get(key, 0) for key in (
        "CROSS_VERSION_ATTACHMENT_REFERENCE", "UNRESOLVED_IN_SCOPE_REFERENCE", "INVALID_REFERENCE",
    ))
    return "COMPLETE_ENUMERATED_SCOPE" if not gaps and counts["root_pages"] == 1 else "PARTIAL"


def checkpoint(root, manifest):
    manifest["updated_at_utc"], manifest["counts"] = utc_now(), manifest_counts(manifest)
    write_json(root, child(root, "manifest.json"), manifest)


def collect(root, config, *, token_env, allow_network=False, resume=False, max_attempts=1):
    root, config = root_path(root), validate_service(config)
    snapshot = read_json(child(root, "snapshot.json"))
    enumeration = read_json(child(root, "enumeration.json"))
    backing = unique_records(read_json(child(root, "backing-items.json"))["items"], "path")
    require(snapshot.get("enumeration_completed_at_utc"), "ENUMERATION_NOT_COMPLETED")
    require(snapshot["hierarchy_status"] == "ENUMERATED" and not enumeration["errors"], "HIERARCHY_INCOMPLETE")
    require(not snapshot["missing_backing_paths"] and not snapshot["unlisted_markdown_paths"], "UNACCOUNTED_BACKING_ITEMS")
    require(
        snapshot["base_url"] == config["base_url"] and snapshot["requested_wiki_id"] == config["wiki_id"]
        and snapshot["root_page_id"] == config["root_page_id"] and snapshot["service_urls"] == config["service_urls"],
        "SOURCE_SELECTION_CHANGED",
    )
    if snapshot["hierarchy_version_mode"].startswith("BRANCH_"):
        require(snapshot.get("hierarchy_bracket_heads_match_snapshot"), "HIERARCHY_REVISION_DRIFT")
    parser = markdown_parser()
    client = Client(
        root, config, token_env=token_env, allow_network=allow_network,
        expected_identity=snapshot["identity_fingerprint_sha256"], max_attempts=max_attempts,
    )
    previous = read_json(child(root, "manifest.json"))
    if previous.get("schema_version") == 3:
        require(resume, "EXPLICIT_RESUME_REQUIRED")
        require(previous["snapshot_commit"] == snapshot["commit"], "MANIFEST_SNAPSHOT_MISMATCH")
        manifest = previous
        manifest["references"], manifest["unparsed_attachment_markers"] = [], []
    else:
        require(not resume, "NO_PREVIOUS_COLLECTION")
        manifest = {
            "schema_version": 3, "corpus_id": identifier("corpus", snapshot["wiki_id"] + "\0" + snapshot["root_path"]),
            "artifact_kind": "LOCAL_SOURCE_EXPORT", "collection_started_at_utc": utc_now(),
            "snapshot_commit": snapshot["commit"],
            "source": {
                "service": "Azure DevOps Wiki", "root_page_id": snapshot["root_page_id"],
                "requested_url": snapshot["source_url"], "canonical_url": snapshot["root_canonical_url"],
                "wiki_id": snapshot["wiki_id"], "repository_id": snapshot["repository_id"],
                "project_id": snapshot["project_id"], "root_path": snapshot["root_path"],
                "scope": "Root, recursive descendants and referenced same-wiki attachments.",
            },
            "authorization": {
                "read_only_collection": "EXPLICIT_COMMAND_SELECTION",
                "storage_and_data_owner_clearance": "OPERATOR_RESPONSIBILITY_NOT_VERIFIED",
                "substantive_model_processing": "NOT_AUTHORIZED", "semantic_synthesis": "NOT_PERFORMED",
                "publication": "NOT_AUTHORIZED",
            },
            "pages": enumeration["pages"], "attachments": [], "ancillary_items": [],
            "references": [], "unparsed_attachment_markers": [],
            "preflight_artifacts": ["preflight/README.md", "preflight/manifest.json"],
        }
    manifest.update(status="COLLECTING", coverage_status="IN_PROGRESS")
    checkpoint(root, manifest)
    for page in manifest["pages"]:
        try:
            item = backing[page["git_path"]]
            destination = child(root, "sources/pages/" + page["key"] + ".md")
            page.update(collect_blob(root, client, snapshot, item, destination, "EXPORT_PAGE_BLOB", page if page.get("sha256") else None))
            text, page["text_encoding"] = source_text(root, destination)
            references, unresolved = extract_references(text, parser)
            for reference in references:
                target = reference["target"]
                reference.update(source_page_key=page["key"], source_page_id=page.get("page_id"), key=identifier("reference", page["key"] + "\0" + target))
                try:
                    reference.update(classify_reference(target, page, snapshot, manifest["pages"], backing))
                except ValueError:
                    reference.update(kind="INVALID_REFERENCE", status="NOT_FETCHED")
                manifest["references"].append(reference)
            for marker in unresolved:
                marker["source_page_key"] = page["key"]
            manifest["unparsed_attachment_markers"].extend(unresolved)
            page.update(reference_scan_status="PARSED", reference_count=len(references))
        except UnicodeError:
            page["reference_scan_status"] = "UNSUPPORTED_TEXT_ENCODING"
        except CollectionError as error:
            page.update(status="FAILED", error_code=error.code, http_status=error.http_status)
        checkpoint(root, manifest)
    page_paths = {page["git_path"] for page in manifest["pages"]}
    previous_ancillary = unique_records(manifest["ancillary_items"], "git_path")
    manifest["ancillary_items"] = []
    for path, item in backing.items():
        if path in page_paths or item.get("gitObjectType") != "blob":
            continue
        key = identifier("ancillary", path)
        ancillary = {"key": key, "git_path": path, "role": "SCOPED_BACKING_ARTIFACT"}
        try:
            ancillary.update(collect_blob(
                root, client, snapshot, item, child(root, "sources/ancillary/" + key + ".bin"),
                "EXPORT_SCOPED_ANCILLARY", previous_ancillary.get(path),
            ))
        except CollectionError as error:
            ancillary.update(status="FAILED", error_code=error.code, http_status=error.http_status)
        manifest["ancillary_items"].append(ancillary)
        checkpoint(root, manifest)
    referenced_attachments = {}
    for ref in manifest["references"]:
        if ref["kind"] == "WIKI_ATTACHMENT":
            referenced_attachments.setdefault(ref["git_path"], []).append(ref)
    previous_attachments = unique_records(manifest["attachments"], "git_path")
    manifest["attachments"] = []
    for path, references in referenced_attachments.items():
        key = identifier("attachment", path)
        attachment = {
            "key": key, "git_path": path, "reference_keys": [ref["key"] for ref in references],
            "source_page_keys": sorted({ref["source_page_key"] for ref in references}), "content_processing": "OPAQUE_BINARY_ONLY",
        }
        try:
            previous_item = previous_attachments.get(path)
            if previous_item and previous_item.get("status") == "EXPORTED":
                item = {"path": path, "objectId": previous_item["source_blob_id"], "gitObjectType": "blob"}
            else:
                item, receipt = metadata_for_attachment(client, snapshot, path)
                attachment.update(metadata_retrieved_at_utc=receipt["completed_at_utc"], metadata_etag=receipt["headers"].get("etag"), source_content_metadata=item.get("contentMetadata"))
            attachment.update(collect_blob(
                root, client, snapshot, item, child(root, "sources/attachments/" + key + ".bin"), "EXPORT_ATTACHMENT_BLOB", previous_item,
            ))
        except CollectionError as error:
            attachment.update(status="FAILED", error_code=error.code, http_status=error.http_status)
        for ref in references:
            ref.update(attachment_key=key, status=attachment["status"])
        manifest["attachments"].append(attachment)
        checkpoint(root, manifest)
    try:
        final_head, _ = ref_commit(client, git_endpoint(snapshot), snapshot["branch"])
        manifest.update(branch_head_at_collection_end=final_head, branch_unchanged_at_collection_end=final_head == snapshot["commit"])
    except CollectionError as error:
        manifest.update(branch_end_check_error=error.code, branch_unchanged_at_collection_end=None)
    manifest.update(
        collection_completed_at_utc=utc_now(), coverage_status=coverage_status(manifest),
        status="COLLECTED_LOCAL_SOURCE_REQUIRES_REVIEW",
        limitations=[
            "Scope covers the accessible enumerated subtree and discovered same-wiki attachments, not hidden content.",
            "Source bytes are commit-bound; hierarchy mode and branch observations are recorded separately.",
            "Remote references and nested attachments are not expanded. Acquired code is not executed.",
            "Binary files are opaque. Hashes do not prove source accuracy, malware safety or publication rights.",
            "This tool performs no model requests, substantive review, provider selection or publication.",
        ],
    )
    checkpoint(root, manifest)
    render_corpus(root, manifest, snapshot)
    return {"result": "PASS" if manifest["coverage_status"] == "COMPLETE_ENUMERATED_SCOPE" else "FAIL", "phase": "COLLECTED", "counts": manifest["counts"], "source_content_output": False}


def escape_markdown(value):
    return re.sub(r"([\\`*_[\]<>|])", r"\\\1", value.replace("\n", " ").replace("\r", " "))


def href(path):
    return urllib.parse.quote(str(path).replace("\\", "/"), safe="/.-")


def html_document(title, body):
    return (
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta http-equiv="Content-Security-Policy" content="default-src \'none\'; '
        'style-src \'unsafe-inline\'; base-uri \'none\'; form-action \'none\'">'
        '<meta name="referrer" content="no-referrer"><meta name="viewport" content="width=device-width, initial-scale=1">'
        f"<title>{html.escape(title)}</title>"
        "<style>body{font:16px system-ui;max-width:1000px;margin:2rem auto;padding:0 1rem}"
        "pre{white-space:pre-wrap;overflow-wrap:anywhere;border:1px solid #888;padding:1rem}"
        "li{margin:.4rem 0}table{border-collapse:collapse}td,th{padding:.4rem;border:1px solid #888}"
        "code{overflow-wrap:anywhere}</style></head><body>" + body + "</body></html>\n"
    )


def render_corpus(root, manifest, snapshot):
    root = root_path(root)
    pages = unique_records(manifest["pages"], "key")
    attachments = unique_records(manifest["attachments"], "key")
    ancillary = unique_records(manifest["ancillary_items"], "git_path")
    html_rows, markdown_rows, navigation = [], [], []
    for page in manifest["pages"]:
        title, key = page["path"].rsplit("/", 1)[-1], page["key"]
        view_path = "views/" + key + ".html"
        child(root, view_path)
        depth = max(0, page["path"].count("/") - snapshot["root_path"].count("/"))
        markdown_rows.append("  " * depth + f"- [{escape_markdown(title)}]({href(view_path)}) ({escape_markdown(page['status'])})")
        html_rows.append(f'<li style="margin-left:{depth * 1.2}rem"><a href="{href(view_path)}">{html.escape(title)}</a></li>')
        navigation += [{"from": "index.html", "to": view_path}, {"from": "INDEX.md", "to": view_path}, {"from": view_path, "to": "index.html"}]
        links = ['<a href="../index.html">Corpus index</a>']
        related = ([page["parent_key"]] if page.get("parent_key") else []) + (page.get("child_keys") or [])
        for related_key in related:
            target = pages[related_key]
            links.append(f'<a href="{href(target["key"])}.html">{html.escape(target["path"].rsplit("/", 1)[-1])}</a>')
            navigation.append({"from": view_path, "to": "views/" + target["key"] + ".html"})
        details = [
            f"<h1>{html.escape(title)}</h1>", "<p>" + " | ".join(links) + "</p>",
            "<p><strong>Original untrusted source, not a reviewed synthesis.</strong> Source text is escaped and remote resources are blocked.</p>",
            f"<p>Snapshot: <code>{html.escape(snapshot['commit'])}</code>; status: {html.escape(page['status'])}.</p>",
            f"<p>Source URL (not opened): <code>{html.escape(page.get('canonical_url') or '')}</code></p>",
        ]
        if page.get("local_path"):
            local = page["local_path"]
            verified_bytes(root, page)
            details.append(f'<p><a href="../{href(local)}" download>Original bytes (untrusted)</a></p>')
            navigation.append({"from": view_path, "to": local})
            try:
                text, _ = source_text(root, child(root, local))
                details.append("<pre>" + html.escape(text) + "</pre>")
            except UnicodeError:
                details.append("<p>Unsupported text encoding; no replacement content was invented.</p>")
        details.append("<h2>Reference inventory</h2><ul>")
        for reference in manifest["references"]:
            if reference["source_page_key"] != key:
                continue
            target = None
            if reference["kind"] == "IN_SCOPE_PAGE":
                target = "views/" + reference["page_key"] + ".html"
            elif reference.get("attachment_key"):
                target = attachments[reference["attachment_key"]].get("local_path")
            elif reference["kind"] == "IN_SCOPE_FILE":
                target = ancillary.get(reference["git_path"], {}).get("local_path")
            label = html.escape(f"{reference['kind']}: {reference['status']}")
            if target:
                child(root, target)
                details.append(f'<li><a href="../{href(target)}">{label}</a></li>')
                navigation.append({"from": view_path, "to": target})
            else:
                details.append("<li>" + label + "</li>")
        details.append("</ul>")
        write_text(root, child(root, view_path), html_document(title, "\n".join(details)))
    write_text(root, child(root, "INDEX.md"), (
        "# Original source hierarchy\n\n[Entry point](README.md) | [Offline index](index.html)\n\n"
        + "\n".join(markdown_rows) + "\n"
    ))
    write_text(root, child(root, "index.html"), html_document(
        "Local wiki source index",
        "<h1>Local wiki source index</h1><p>Unreviewed source evidence. No model synthesis or publication is implied.</p>"
        f"<p>Export coverage: <strong>{html.escape(manifest['coverage_status'])}</strong>.</p>"
        '<p><a href="README.md">Collection notes</a> | <a href="GAPS.md">Coverage gaps</a></p><ol>'
        + "".join(html_rows) + "</ol>",
    ))
    counts = manifest_counts(manifest)
    limitations = "\n".join("- " + text for text in manifest.get("limitations", []))
    readme = [
        "# Local wiki source corpus", "", f"**Export coverage: {manifest['coverage_status']}.**",
        "Local collection is not semantic review, approval, publication or data-owner clearance.", "",
        "## Start here", "", "- [Offline index](index.html) and [hierarchy](INDEX.md).",
        "- [Manifest](manifest.json), [snapshot](snapshot.json), [enumeration](enumeration.json), [backing items](backing-items.json).",
        "- [Coverage gaps](GAPS.md).", "", "## Inventory", "",
        "| Measure | Count |", "|---|---:|",
        *[f"| {name.replace('_', ' ')} | {counts[name]} |" for name in (
            "root_pages", "descendant_pages", "pages_exported", "attachment_items_discovered",
            "attachments_exported", "ancillary_files_exported", "reference_records",
        )],
        "", "## Safe handling", "",
        "Do not execute acquired scripts, render raw active markup, or publish this corpus without separate source/data-owner clearance.",
        "Source hashes bind bytes, not rights, semantic truth, malware safety or host qualification.",
        "Use the portable collector's verify command with an explicit --root; --receipt is optional.", "",
        "## Limitations", "", limitations, "",
    ]
    write_text(root, child(root, "README.md"), "\n".join(readme))
    failed = [item for item in manifest["pages"] + manifest["attachments"] + manifest["ancillary_items"] if item["status"] != "EXPORTED"]
    unsupported = Counter(ref["kind"] for ref in manifest["references"] if ref["kind"] not in {"IN_SCOPE_PAGE", "IN_SCOPE_FILE", "WIKI_ATTACHMENT", "LOCAL_FRAGMENT"})
    gap_lines = [
        "# Coverage gaps and boundaries", "", f"Export coverage: **{manifest['coverage_status']}**.",
        "Semantic coverage: **NOT_ASSESSED**. Publication permission: **false**.", "",
        f"Failed or unsupported export items: {len(failed)}. Unparsed attachment markers: {counts['unparsed_attachment_markers']}.",
        "", "| Excluded or unresolved category | Records |", "|---|---:|",
        *[f"| {kind} | {count} |" for kind, count in sorted(unsupported.items())], "",
        "Outbound links do not define descendants and were not crawled. Binary contents remain unreviewed.", "",
        "## Failed export records", "",
        *[f"- `{escape_markdown(item['key'])}`: {escape_markdown(item['status'])}." for item in failed],
        "", "## Limits", "", limitations, "",
    ]
    write_text(root, child(root, "GAPS.md"), "\n".join(gap_lines))
    for source, target in [
        ("README.md", "index.html"), ("README.md", "INDEX.md"), ("README.md", "manifest.json"),
        ("README.md", "snapshot.json"), ("README.md", "enumeration.json"), ("README.md", "backing-items.json"),
        ("README.md", "GAPS.md"), ("index.html", "README.md"), ("index.html", "GAPS.md"),
        ("INDEX.md", "README.md"), ("INDEX.md", "index.html"),
    ]:
        navigation.append({"from": source, "to": target})
    write_json(root, child(root, "navigation.json"), {"links": navigation})


def verify_sources(root, manifest, snapshot):
    root = root_path(root)
    require(manifest["snapshot_commit"] == snapshot["commit"], "MANIFEST_SNAPSHOT_MISMATCH")
    version_parameters(snapshot["commit"])
    items = manifest["pages"] + manifest["attachments"] + manifest["ancillary_items"]
    unique_records(items, "key")
    paths = set()
    for item in items:
        require(item.get("status") == "EXPORTED" and item.get("local_path"), "SOURCE_NOT_EXPORTED")
        require(item.get("snapshot_commit") == snapshot["commit"], "SOURCE_REVISION_MISMATCH")
        data = verified_bytes(root, item)
        expected_blob = hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()
        require(expected_blob == item["source_blob_id"] == item["verified_git_blob_sha1"], "SOURCE_BLOB_MISMATCH")
        folded = child(root, item["local_path"]).relative_to(root).as_posix().casefold()
        require(folded not in paths, "SOURCE_PATH_COLLISION")
        paths.add(folded)
    return len(items)


def verify(root, *, receipt=False):
    root = root_path(root)
    manifest, snapshot = read_json(child(root, "manifest.json")), read_json(child(root, "snapshot.json"))
    enumeration = read_json(child(root, "enumeration.json"))
    backing = unique_records(read_json(child(root, "backing-items.json"))["items"], "path")
    navigation = read_json(child(root, "navigation.json"))["links"]
    failures = []
    checked = verify_sources(root, manifest, snapshot)
    pages = unique_records(manifest["pages"], "key")
    unique_records(manifest["pages"], "page_id")
    unique_records(manifest["pages"], "path")
    enumerated = unique_records(enumeration["pages"], "key")
    if set(pages) != set(enumerated) or enumeration.get("pending_count") != 0 or enumeration.get("errors"):
        failures.append("PAGE_ACCOUNTING")
    roots = [page for page in pages.values() if page["parent_key"] is None]
    if len(roots) != 1 or roots[0]["page_id"] != snapshot["root_page_id"]:
        failures.append("ROOT_ACCOUNTING")
    visited, pending = set(), [page["key"] for page in roots]
    while pending:
        key = pending.pop()
        if key in visited or key not in pages:
            failures.append("HIERARCHY_CYCLE_OR_MISSING_NODE")
            continue
        visited.add(key)
        page = pages[key]
        for field in ("path", "git_path", "page_id", "parent_key", "child_keys"):
            if page[field] != enumerated.get(key, {}).get(field):
                failures.append("HIERARCHY_RECORD_BINDING")
        for child_key in page["child_keys"]:
            if pages.get(child_key, {}).get("parent_key") != key:
                failures.append("CHILD_REFERENCE")
            pending.append(child_key)
    if visited != set(pages):
        failures.append("UNREACHABLE_PAGE")
    blob_paths = {path for path, item in backing.items() if item.get("gitObjectType") == "blob"}
    source_records = manifest["pages"] + manifest["ancillary_items"]
    source_paths = unique_records(source_records, "git_path")
    if blob_paths != set(source_paths):
        failures.append("BACKING_ITEM_ACCOUNTING")
    for path, record in source_paths.items():
        if backing.get(path, {}).get("objectId") != record["source_blob_id"] or backing.get(path, {}).get("commitId") != snapshot["commit"]:
            failures.append("BACKING_BLOB_BINDING")
    attachments = unique_records(manifest["attachments"], "git_path")
    refs = unique_records(manifest["references"], "key")
    expected_attachments = {ref["git_path"] for ref in refs.values() if ref["kind"] == "WIKI_ATTACHMENT"}
    if expected_attachments != set(attachments):
        failures.append("ATTACHMENT_ACCOUNTING")
    for path, item in attachments.items():
        matching = [ref for ref in refs.values() if ref.get("attachment_key") == item["key"]]
        if (
            {ref["key"] for ref in matching} != set(item["reference_keys"])
            or {ref["source_page_key"] for ref in matching} != set(item["source_page_keys"])
            or any(ref.get("git_path") != path for ref in matching)
        ):
            failures.append("ATTACHMENT_REFERENCE_BINDING")
    if any(ref["source_page_key"] not in pages for ref in refs.values()):
        failures.append("REFERENCE_PAGE_BINDING")
    for link in navigation:
        if not child(root, link["from"]).is_file() or not child(root, link["to"]).is_file():
            failures.append("LOCAL_NAVIGATION_LINK")
    html_links = 0
    for path in [child(root, "index.html"), *child(root, "views").glob("*.html")]:
        contents = read_bytes(inside(root, path)).decode("utf-8")
        parser = HtmlReferences()
        parser.feed(contents)
        if "<script" in contents.lower() or "<iframe" in contents.lower():
            failures.append("ACTIVE_MARKUP_IN_VIEW")
        for target in parser.targets:
            url = urllib.parse.urlsplit(target)
            if url.scheme or url.netloc:
                failures.append("REMOTE_TARGET_IN_SAFE_VIEW")
            else:
                destination = (path.parent / urllib.parse.unquote(url.path)).resolve()
                if not destination.is_relative_to(root) or not inside(root, destination).is_file():
                    failures.append("HTML_LOCAL_LINK")
            html_links += 1
    if manifest_counts(manifest) != manifest["counts"]:
        failures.append("MANIFEST_COUNTS")
    if coverage_status(manifest) != manifest["coverage_status"]:
        failures.append("COVERAGE_STATUS")
    if snapshot.get("hierarchy_status") != "ENUMERATED" or snapshot.get("missing_backing_paths") or snapshot.get("unlisted_markdown_paths"):
        failures.append("HIERARCHY_ENUMERATION_STATUS")
    if snapshot.get("hierarchy_version_mode", "").startswith("BRANCH_") and not snapshot.get("hierarchy_bracket_heads_match_snapshot"):
        failures.append("HIERARCHY_REVISION_DRIFT")
    result = {
        "verified_at_utc": utc_now(), "result": "FAIL" if failures else "PASS",
        "source_files_checked": checked, "navigation_records_checked": len(navigation),
        "html_links_checked": html_links, "coverage_status": manifest["coverage_status"],
        "network_requests": 0, "source_content_output": False, "publication_authorized": False,
        "failure_counts": dict(Counter(failures)),
    }
    if receipt:
        write_json(root, child(root, "verification.json"), result)
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("phase", choices=("prepare", "collect", "render", "verify"))
    parser.add_argument("--root", required=True, help="Explicit local corpus; live output must be outside this code repository.")
    parser.add_argument("--service-config", help="Explicit service JSON; no credentials may be stored in it.")
    parser.add_argument("--token-env", help="Environment variable NAME for an already provisioned bearer token.")
    parser.add_argument("--allow-network", action="store_true")
    parser.add_argument("--branch-metadata", action="store_true", help="Explicit opt-in to bracketed branch metadata; no automatic fallback.")
    parser.add_argument("--resume", action="store_true", help="Explicitly continue an existing frozen operation.")
    parser.add_argument("--max-attempts", type=int, default=1, help="Recorded GET attempts, 1 to 3. Default: no retry.")
    parser.add_argument("--receipt", action="store_true", help="Write verification.json for verify.")
    args = parser.parse_args(argv)
    if args.phase in {"prepare", "collect"}:
        if not args.allow_network or not args.service_config or not args.token_env:
            parser.error("network phases require --allow-network, --service-config and --token-env")
        root = root_path(args.root, must_exist=args.phase == "collect")
        require(not root.is_relative_to(Path(__file__).resolve().parents[2]), "LIVE_CORPUS_MUST_BE_OUTSIDE_CODE_REPOSITORY")
        config = validate_service(read_json(Path(args.service_config)))
        options = dict(token_env=args.token_env, allow_network=True, resume=args.resume, max_attempts=args.max_attempts)
        if args.phase == "prepare":
            return prepare(root, config, branch_metadata=args.branch_metadata, **options)
        return collect(root, config, **options)
    root = root_path(args.root)
    if args.phase == "render":
        manifest, snapshot = read_json(child(root, "manifest.json")), read_json(child(root, "snapshot.json"))
        verify_sources(root, manifest, snapshot)
        render_corpus(root, manifest, snapshot)
        return {"result": "PASS", "phase": "RENDERED", "network_requests": 0}
    return verify(root, receipt=args.receipt)


def run_cli(entry):
    try:
        result = entry()
        print(json.dumps(result, indent=2))
        if result.get("result") == "FAIL":
            raise SystemExit(1)
    except Exception as error:
        # Arbitrary source-bearing exceptions stay out of terminal output.
        print(json.dumps({
            "result": "FAIL", "error_code": error.code if isinstance(error, CollectionError) else type(error).__name__,
            "http_status": error.http_status if isinstance(error, CollectionError) else None,
            "source_content_output": False,
        }))
        raise SystemExit(1) from None


if __name__ == "__main__":
    run_cli(main)
