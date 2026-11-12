"""Offline research-tool regressions. All writable fixtures are owned by this file."""

import base64
import contextlib
import copy
import hashlib
import importlib
import io
import json
import os
import shutil
import struct
import subprocess
import unittest
import zlib
from pathlib import Path
from unittest.mock import patch
from uuid import uuid4

from research_tools import _common
from research_tools.checkpoints import freeze_workspace, verify_checkpoint, verify_checkpoint_legacy
from research_tools.public_repositories import collect_github, study
from research_tools.repository_study import build_reference_views, catalog_source, inventory_source
from research_tools.repository_study import verify_corpus as repository_verify
from research_tools.wiki import build_corpus, collect_wiki, prepare_review, reindex_local
from research_tools.wiki import verify_corpus as wiki_verify


MODULES = [
    _common, collect_github, study, inventory_source, catalog_source, build_reference_views,
    repository_verify, collect_wiki, prepare_review, reindex_local, build_corpus,
    wiki_verify, freeze_workspace, verify_checkpoint, verify_checkpoint_legacy,
]
PROJECT = Path(__file__).resolve().parents[1]


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def png_fixture():
    def chunk(kind, payload):
        return struct.pack(">I", len(payload)) + kind + payload + struct.pack(">I", zlib.crc32(kind + payload) & 0xffffffff)
    return (
        b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", 1, 1, 8, 6, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(b"\0\xff\0\0\xff")) + chunk(b"IEND", b"")
    )


class ResearchToolTests(unittest.TestCase):
    def setUp(self):
        self.root = PROJECT / "tests" / (".research-tools-" + uuid4().hex)
        self.root.mkdir()
        self.addCleanup(shutil.rmtree, self.root)

    def files(self, root):
        return {
            path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in root.rglob("*") if path.is_file()
        }

    def service(self):
        return {
            "base_url": "https://service.example/Project/_apis",
            "source_url": "https://service.example/Project/_wiki/wikis/Example.wiki/1",
            "service_urls": ["https://service.example/Project"],
            "project_name": "Project", "wiki_id": "Example.wiki", "root_page_id": 1,
            "principal_label": "synthetic-principal",
        }

    def wiki(self, texts=None, *, attachment=False):
        root = self.root / "wiki"
        root.mkdir()
        texts = texts if texts is not None else ["# Root\nUntrusted synthetic source.\n"]
        if attachment:
            texts = [texts[0] + "\n![Fixture](/.attachments/image.png)\n", *texts[1:]]
        snapshot = {
            **self.service(), "schema_version": 2, "commit": "a" * 40, "root_path": "/Guide",
            "wiki_id": "00000000-0000-0000-0000-000000000001", "wiki_name": "Example.wiki",
            "project_id": "00000000-0000-0000-0000-000000000002",
            "repository_id": "00000000-0000-0000-0000-000000000003", "branch": "wikiBranch",
            "hierarchy_status": "ENUMERATED", "hierarchy_version_mode": "COMMIT_PINNED",
            "missing_backing_paths": [], "unlisted_markdown_paths": [],
        }
        pages, items = [], []

        def source_record(key, relative, git_path, data):
            target = root / Path(relative)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
            blob = hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()
            return {
                "key": key, "local_path": relative, "git_path": git_path, "bytes": len(data),
                "sha256": hashlib.sha256(data).hexdigest(), "source_blob_id": blob,
                "verified_git_blob_sha1": blob, "snapshot_commit": snapshot["commit"], "status": "EXPORTED",
                "retrieved_at_utc": "2000-01-01T00:00:00Z",
            }

        for index, text in enumerate(texts):
            key, path = f"page-{index + 1}", "/Guide" if index == 0 else f"/Guide/Child-{index + 1}"
            record = source_record(key, f"sources/pages/{key}.md", path + ".md", text.encode("utf-8"))
            record.update(
                page_id=index + 1, path=path, parent_key=None if index == 0 else "page-1",
                child_keys=[f"page-{number + 1}" for number in range(1, len(texts))] if index == 0 else [],
                reference_scan_status="PARSED", canonical_url=snapshot["source_url"],
            )
            pages.append(record)
            items.append({"path": record["git_path"], "gitObjectType": "blob", "objectId": record["source_blob_id"], "commitId": snapshot["commit"]})
        attachments = []
        if attachment:
            record = source_record("attachment-1", "sources/attachments/attachment-1.bin", "/.attachments/image.png", png_fixture())
            record.update(reference_keys=[], source_page_keys=["page-1"])
            attachments.append(record)
        references = []
        for page, text in zip(pages, texts):
            found, unresolved = collect_wiki.extract_references(text, collect_wiki.markdown_parser())
            self.assertEqual(unresolved, [])
            for ref in found:
                ref.update(
                    key=collect_wiki.identifier("reference", page["key"] + "\0" + ref["target"]),
                    source_page_key=page["key"], source_page_id=page["page_id"],
                )
                ref.update(collect_wiki.classify_reference(ref["target"], page, snapshot, pages, {}))
                if ref["kind"] == "WIKI_ATTACHMENT" and attachments:
                    ref.update(attachment_key="attachment-1", status="EXPORTED")
                    attachments[0]["reference_keys"].append(ref["key"])
                references.append(ref)
            page["reference_count"] = len(found)
        manifest = {
            "schema_version": 3, "snapshot_commit": snapshot["commit"],
            "pages": pages, "attachments": attachments, "ancillary_items": [],
            "references": references, "unparsed_attachment_markers": [],
            "authorization": {"substantive_model_processing": "NOT_AUTHORIZED", "publication": "NOT_AUTHORIZED"},
            "status": "SYNTHETIC_SOURCE_FIXTURE", "limitations": ["Synthetic fixture, not live evidence."],
        }
        manifest["counts"] = collect_wiki.manifest_counts(manifest)
        manifest["coverage_status"] = collect_wiki.coverage_status(manifest)
        write_json(root / "manifest.json", manifest)
        write_json(root / "snapshot.json", snapshot)
        write_json(root / "enumeration.json", {"pages": pages, "pending_count": 0, "errors": []})
        write_json(root / "backing-items.json", {"items": items})
        collect_wiki.render_corpus(root, manifest, snapshot)
        return root, manifest, snapshot

    def test_imports_are_passive(self):
        with (
            patch.object(Path, "open", side_effect=AssertionError("import attempted local I/O")),
            patch.object(Path, "mkdir", side_effect=AssertionError("import attempted a write")),
            patch.object(Path, "iterdir", side_effect=AssertionError("import attempted a scan")),
            patch.object(subprocess, "run", side_effect=AssertionError("import attempted subprocess")),
            patch.object(collect_wiki.urllib.request.OpenerDirector, "open", side_effect=AssertionError("import attempted network")),
        ):
            for module in MODULES:
                with self.subTest(module=module.__name__):
                    importlib.reload(module)

    def test_help_and_missing_arguments_are_passive(self):
        with (
            patch.object(Path, "open", side_effect=AssertionError("argument parsing attempted I/O")),
            patch.object(subprocess, "run", side_effect=AssertionError("argument parsing attempted subprocess")),
            contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()),
        ):
            for module in MODULES[1:]:
                with self.subTest(module=module.__name__, mode="help"), self.assertRaises(SystemExit) as result:
                    module.main(["--help"])
                self.assertEqual(result.exception.code, 0)
                with self.subTest(module=module.__name__, mode="missing"), self.assertRaises(SystemExit) as result:
                    module.main([])
                self.assertEqual(result.exception.code, 2)

    def test_network_flags_are_not_inferred(self):
        with patch.object(subprocess, "run", side_effect=AssertionError("unexpected subprocess")):
            with self.assertRaisesRegex(ValueError, "explicitly selected"):
                collect_github.api("repos/example/project", token_env="NOT_SET", allow_network=False)
        with patch.object(collect_wiki.urllib.request, "build_opener", side_effect=AssertionError("unexpected client")):
            with self.assertRaisesRegex(ValueError, "NETWORK_NOT_SELECTED"):
                collect_wiki.Client(self.root, self.service(), token_env="NOT_SET")
        with contextlib.redirect_stderr(io.StringIO()):
            for args in (["prepare", "--root", str(self.root)], ["collect", "--root", str(self.root)]):
                with self.assertRaises(SystemExit) as result:
                    collect_wiki.main(args)
                self.assertEqual(result.exception.code, 2)

    def test_explicit_token_selection_does_not_fall_back(self):
        with patch.dict(os.environ, {"GH_TOKEN": "unrelated-synthetic-value"}):
            with patch.object(subprocess, "run", side_effect=AssertionError("unexpected fallback")):
                with self.assertRaisesRegex(ValueError, "unavailable"):
                    collect_github.api("repos/example/project", token_env="ABSENT_TEST_SELECTED_TOKEN", allow_network=True)

    def test_mocked_download_hash_failure_does_not_create_file(self):
        response = unittest.mock.MagicMock()
        response.__enter__.return_value = response
        response.status, response.headers = 200, {"Content-Type": "application/octet-stream"}
        response.read.return_value = b"synthetic wrong content"
        with patch.dict(os.environ, {"RESEARCH_SYNTHETIC_TOKEN": "not-a-real-credential"}):
            client = collect_wiki.Client(self.root, self.service(), token_env="RESEARCH_SYNTHETIC_TOKEN", allow_network=True)
        with patch.object(client.opener, "open", return_value=response):
            with self.assertRaisesRegex(ValueError, "DOWNLOADED_BLOB_HASH_MISMATCH"):
                client.request(
                    self.service()["base_url"] + "/git/repositories/example/items", {}, "SYNTHETIC",
                    download=self.root / "blob.bin", expected_blob="a" * 40,
                )
        self.assertFalse((self.root / "blob.bin").exists())
        receipts = (self.root / "request-receipts.jsonl").read_text(encoding="utf-8")
        self.assertNotIn("not-a-real-credential", receipts)

    def test_verified_blob_resume_requires_receipt(self):
        target = self.root / "source.bin"
        data = b"synthetic"
        target.write_bytes(data)
        item = {"gitObjectType": "blob", "objectId": hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()}
        with self.assertRaisesRegex(ValueError, "EXISTING_FILE_WITHOUT_RECEIPT"):
            collect_wiki.collect_blob(self.root, None, {"commit": "a" * 40}, item, target, "SYNTHETIC")

    def test_pinned_public_capture_keeps_exact_bytes(self):
        root = self.root / "capture"
        data = "line\r\n\u03b2\n".encode("utf-8")
        blob = hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()
        record = collect_github.capture_file(
            root, root / "sources" / "example--project", {"repository": "example/project", "commit": "a" * 40},
            {"type": "file", "path": "README.md", "size": len(data), "encoding": "base64", "content": base64.b64encode(data).decode(), "sha": blob},
            lambda endpoint: self.fail("inline base64 capture made a network request"),
        )
        self.assertEqual((root / record["local_file"]).read_bytes(), data)
        self.assertEqual(study.verify_record(root, {"repository": "example/project", "commit": "a" * 40}, record), data.decode())

    def test_cached_public_snapshot_does_not_bypass_current_visibility_check(self):
        root = self.root / "capture"
        directory = root / "sources" / "example--project"
        write_json(directory / "metadata.json", {
            "requested_repository": "example/project", "repository": "example/project",
            "visibility": "public", "commit": "a" * 40,
        })
        before = self.files(root)
        with self.assertRaisesRegex(ValueError, "non-public"):
            collect_github.snapshot(
                root, "example/project", directory,
                lambda endpoint: {"private": True, "visibility": "private", "full_name": "example/project"},
            )
        self.assertEqual(self.files(root), before)

    def test_service_path_traversal_is_rejected_before_request(self):
        with patch.dict(os.environ, {"RESEARCH_SYNTHETIC_TOKEN": "not-a-real-credential"}):
            client = collect_wiki.Client(self.root, self.service(), token_env="RESEARCH_SYNTHETIC_TOKEN", allow_network=True)
        with patch.object(client.opener, "open", side_effect=AssertionError("escaped service path")):
            for suffix in ("/../other", "/%2e%2e/other"):
                with self.subTest(suffix=suffix), self.assertRaises(ValueError):
                    client.request(self.service()["base_url"] + suffix, {}, "SYNTHETIC")

    def test_wiki_network_pipeline_uses_only_inert_service_mocks(self):
        root, config = self.root / "mocked-export", self.service()
        commit = "a" * 40
        data_by_path = {
            "/Guide.md": b"# Root\n[child](/Guide/Child)\n![image](/.attachments/image.png)\n",
            "/Guide/Child.md": b"# Child\n",
            "/Guide/.order": b"Child\n",
            "/.attachments/image.png": png_fixture(),
        }
        items = {
            path: {
                "path": path, "gitObjectType": "blob", "commitId": commit,
                "objectId": hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest(),
            }
            for path, data in data_by_path.items()
        }
        operations = []
        fake = unittest.mock.Mock()
        fake.identity_hash = "f" * 64

        def request(endpoint, parameters, operation, download=None, expected_blob=None):
            operations.append(operation)
            receipt = {
                "headers": {}, "completed_at_utc": "2000-01-01T00:00:00Z",
                "request_url": endpoint, "status": "SUCCESS",
            }
            if download is not None:
                data = data_by_path[parameters["path"]]
                self.assertEqual(items[parameters["path"]]["objectId"], expected_blob)
                download.parent.mkdir(parents=True, exist_ok=True)
                download.write_bytes(data)
                return {"sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)}, receipt
            if operation == "WIKI_IDENTITY":
                return {
                    "id": "00000000-0000-0000-0000-000000000001", "name": "Example.wiki",
                    "projectId": "00000000-0000-0000-0000-000000000002",
                    "repositoryId": "00000000-0000-0000-0000-000000000003",
                    "versions": [{"version": "wikiBranch"}],
                }, receipt
            if operation == "RESOLVE_WIKI_BRANCH":
                return {"count": 1, "value": [{"name": "refs/heads/wikiBranch", "objectId": commit}]}, receipt
            if operation in {"ROOT_ID_RESOLUTION", "ENUMERATE_DIRECT_CHILDREN"}:
                path = parameters.get("path", "/Guide")
                page = {
                    "id": 1 if path == "/Guide" else 2, "path": path, "gitItemPath": path + ".md",
                    "remoteUrl": config["source_url"], "subPages": [{"path": "/Guide/Child"}] if path == "/Guide" else [],
                }
                return page, receipt
            if operation == "ROOT_BACKING_ITEM":
                return copy.deepcopy(items["/Guide.md"]), receipt
            if operation == "ENUMERATE_BACKING_SUBTREE":
                return {"count": 2, "value": [copy.deepcopy(items["/Guide/Child.md"]), copy.deepcopy(items["/Guide/.order"])]}, receipt
            if operation == "ATTACHMENT_METADATA":
                return copy.deepcopy(items[parameters["path"]]), receipt
            raise AssertionError("Unexpected service operation")

        fake.request.side_effect = request
        with patch.object(collect_wiki, "Client", return_value=fake):
            prepared = collect_wiki.prepare(root, config, token_env="UNUSED_MOCK", allow_network=True, branch_metadata=True)
            self.assertEqual(prepared["result"], "PASS")
            collected = collect_wiki.collect(root, config, token_env="UNUSED_MOCK", allow_network=True)
        self.assertEqual(collected["result"], "PASS", collected)
        self.assertEqual(collected["counts"]["total_pages"], 2)
        self.assertEqual(collected["counts"]["attachments_exported"], 1)
        self.assertEqual(collected["counts"]["ancillary_files_exported"], 1)
        self.assertEqual(collect_wiki.verify(root)["result"], "PASS")
        self.assertIn("ATTACHMENT_METADATA", operations)

    def test_safe_paths_reject_escapes_and_links(self):
        for value in ("../outside", "a//b", "a/./b", r"C:\outside", r"\\server\share", "a:stream", "NUL.txt"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                _common.child(self.root, value)
        with patch.object(_common, "linked", side_effect=lambda path: path.name == "linked"):
            with self.assertRaisesRegex(ValueError, "Linked"):
                _common.child(self.root, "linked/file")

    def test_wiki_render_and_verification_are_read_only(self):
        root, _, _ = self.wiki(['# Root\n<script>untrusted()</script>\n![remote](https://outside.example/image)\n'])
        before = self.files(root)
        result = collect_wiki.verify(root)
        self.assertEqual(result["result"], "PASS")
        self.assertEqual(self.files(root), before)
        self.assertFalse((root / "verification.json").exists())
        self.assertNotIn("<script>", (root / "views" / "page-1.html").read_text(encoding="utf-8"))
        collect_wiki.verify(root, receipt=True)
        self.assertTrue((root / "verification.json").is_file())

    def test_wiki_changed_source_rejected(self):
        root, manifest, _ = self.wiki()
        (root / manifest["pages"][0]["local_path"]).write_bytes(b"changed")
        with self.assertRaisesRegex(ValueError, "mismatch"):
            collect_wiki.verify(root)

    def test_wiki_missing_export_path_rejected(self):
        root, manifest, _ = self.wiki()
        del manifest["pages"][0]["local_path"]
        write_json(root / "manifest.json", manifest)
        with self.assertRaisesRegex(ValueError, "SOURCE_NOT_EXPORTED"):
            collect_wiki.verify(root)

    def test_wiki_backing_revision_mismatch_is_not_passed(self):
        root, _, _ = self.wiki()
        data = json.loads((root / "backing-items.json").read_text(encoding="utf-8"))
        data["items"][0]["objectId"] = "b" * 40
        write_json(root / "backing-items.json", data)
        self.assertIn("BACKING_BLOB_BINDING", collect_wiki.verify(root)["failure_counts"])

    def test_review_packets_bound_long_pages_and_preserve_sources(self):
        text = ("line\r\n\u03b2\t" * 2000) + "\n"
        root, _, _ = self.wiki([text])
        before = self.files(root)
        output = self.root / "packets"
        result = prepare_review.prepare(root, output, max_characters=1400)
        self.assertFalse(result["publication_authorized"])
        self.assertEqual(self.files(root), before)
        inventory = json.loads((output / "inventory.json").read_text(encoding="utf-8"))
        cursor = 0
        self.assertGreater(len(inventory["packets"]), 1)
        for packet in inventory["packets"]:
            data = (output / packet["path"]).read_bytes().decode("utf-8")
            self.assertLessEqual(len(data), 1400)
            self.assertEqual(packet["text_start"], cursor)
            self.assertTrue(data.endswith(text[packet["text_start"]:packet["text_end"]]))
            cursor = packet["text_end"]
        self.assertEqual(cursor, len(text))

    def test_review_preparation_refuses_changed_sources_before_output(self):
        root, manifest, _ = self.wiki()
        manifest["pages"][0]["sha256"] = "b" * 64
        write_json(root / "manifest.json", manifest)
        output = self.root / "packets"
        with self.assertRaises(ValueError):
            prepare_review.prepare(root, output)
        self.assertFalse(output.exists())

    def test_reindex_is_offline_and_preserves_source_bytes(self):
        root, manifest, _ = self.wiki(attachment=True)
        source_before = self.files(root / "sources")
        with patch.object(collect_wiki.Client, "__init__", side_effect=AssertionError("offline reindex constructed client")):
            self.assertEqual(reindex_local.reindex(root)["result"], "PASS")
        self.assertEqual(self.files(root / "sources"), source_before)
        self.assertEqual(collect_wiki.verify(root)["result"], "PASS")
        current = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(current["authorization"], manifest["authorization"])

    def test_reindex_does_not_fetch_a_new_attachment(self):
        root, manifest, snapshot = self.wiki(["# Root\n"])
        page = manifest["pages"][0]
        data = b"![new](/.attachments/new.png)"
        (root / page["local_path"]).write_bytes(data)
        page.update(bytes=len(data), sha256=hashlib.sha256(data).hexdigest())
        page["source_blob_id"] = page["verified_git_blob_sha1"] = hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()
        write_json(root / "manifest.json", manifest)
        before = self.files(root)
        with self.assertRaisesRegex(ValueError, "NEW_ATTACHMENT_REQUIRES"):
            reindex_local.reindex(root)
        self.assertEqual(self.files(root), before)

    def build_inputs(self, root, manifest, snapshot):
        (root / "topics").mkdir()
        (root / "topics" / "foundation.md").write_text("# Foundation\n[Source](../SOURCE_GUIDE.md#page-1)\n", encoding="utf-8")
        plan = {
            "schema_version": 1, "source_commit": snapshot["commit"], "topics": ["foundation"],
            "page_topics": {str(page["page_id"]): "foundation" for page in manifest["pages"]},
        }
        summaries = {
            "schema_version": 1, "source_commit": snapshot["commit"],
            "pages": {
                str(page["page_id"]): {"source_sha256": page["sha256"], "summary": "Supplied synthetic note."}
                for page in manifest["pages"] if page["bytes"]
            },
        }
        return plan, summaries

    def test_supplied_notes_build_and_verify_without_granting_approval(self):
        root, manifest, snapshot = self.wiki(["# Root\n", ""], attachment=True)
        plan, summaries = self.build_inputs(root, manifest, snapshot)
        self.assertEqual(build_corpus.build(root, plan, summaries)["result"], "PASS")
        self.assertEqual(wiki_verify.verify(root, decode_images=True)["result"], "PASS")
        result = wiki_verify.verify(root, decode_images=True)
        self.assertEqual(result["png_integrity_checks"], 1)
        self.assertFalse(result["publication_authorized"])
        self.assertFalse((root / "corpus-verification.json").exists())
        current = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(current["authorization"], manifest["authorization"])
        reviews = json.loads((root / "attachment-review.json").read_text(encoding="utf-8"))
        self.assertEqual(reviews["attachments"][0]["review_status"], "NOT_REVIEWED")

    def test_stale_summary_is_rejected_before_derived_writes(self):
        root, manifest, snapshot = self.wiki()
        plan, summaries = self.build_inputs(root, manifest, snapshot)
        summaries["pages"]["1"]["source_sha256"] = "b" * 64
        before = self.files(root)
        with self.assertRaisesRegex(ValueError, "SOURCE_SUMMARY_HASH"):
            build_corpus.build(root, plan, summaries)
        self.assertEqual(self.files(root), before)

    def test_topic_output_collisions_are_rejected(self):
        root, manifest, snapshot = self.wiki()
        plan, summaries = self.build_inputs(root, manifest, snapshot)
        plan["topics"] = ["SOURCE_GUIDE"]
        plan["page_topics"]["1"] = "SOURCE_GUIDE"
        with self.assertRaisesRegex(ValueError, "COLLISION"):
            build_corpus.build(root, plan, summaries)

    def repository(self, *, bad_python=False):
        root, objects = self.root / "repository", self.root / "objects"
        objects.mkdir()
        source = {
            ".github/plugin/marketplace.json": json.dumps({"plugins": [{"name": "demo", "version": "1", "source": "./plugins/demo"}]}),
            ".github/CODEOWNERS": "* @example-maintainer\n",
            "plugins/demo/plugin.json": json.dumps({
                "name": "demo", "version": "1", "skills": ["./skills/read"], "agents": ["./agents/review.agent.md"],
            }),
            "plugins/demo/agency.json": json.dumps({"dependencies": [], "engines": [], "platforms": []}),
            "plugins/demo/skills/read/SKILL.md": "---\nname: read\ndescription: >\n  Read synthetic text.\n---\n# Read\nDo not execute source.\n",
            "plugins/demo/agents/review.agent.md": "---\nname: review\n---\n# Review\n",
            "plugins/demo/example.py": "def broken(:" if bad_python else "raise RuntimeError('must not execute')\ndef example():\n    return 1\n",
            "plugins/demo/example.ps1": "throw 'must not execute'\nfunction Invoke-Example { param($Value) $Value }\n",
            "plugins/demo/example.kql": "// endpoint: https://service.example\n// purpose: Synthetic\nprint value=1\n",
        }
        encoded = {path: text.encode("utf-8") for path, text in source.items()}
        blobs = {path: hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest() for path, data in encoded.items()}
        raw_tree = b"".join(
            f"100644 blob {blobs[path]} {len(data)}\t{path}".encode() + b"\0" for path, data in encoded.items()
        )

        def local_git(git_dir, *args, input=None):
            if args[0] == "rev-parse":
                return ("b" * 40 + "\n").encode()
            if args[0] == "ls-tree":
                return raw_tree
            if args[0] == "cat-file":
                return b"".join(
                    f"{blobs[path]} blob {len(data)}\n".encode() + data + b"\n" for path, data in encoded.items()
                )
            raise AssertionError("Unexpected mocked Git operation")

        with patch.object(inventory_source, "git", side_effect=local_git):
            inventory_source.inventory(root, objects, "a" * 40, "b" * 40, "https://example.test/source")
        return root, objects, local_git

    def test_repository_static_pipeline_and_powershell_parsing(self):
        root, objects, local_git = self.repository()
        result = catalog_source.catalog(root)
        self.assertEqual(result["static_failures"], 0)
        catalog = json.loads((root / "evidence" / "catalog.json").read_text(encoding="utf-8"))
        self.assertEqual(catalog["skills"][0]["declared_purpose"], "Read synthetic text.")
        write_json(root / "evidence" / "references.json", {
            "commit": "a" * 40, "references": [{
                "id": "read-contract", "path": "plugins/demo/skills/read/SKILL.md",
                "start": 1, "end": None, "title": "Synthetic contract", "kind": "instruction_contract",
            }],
        })
        write_json(root / "evidence" / "skill-summaries.json", {"skills": {"demo/read": ["Read", "Text"]}})
        write_json(root / "evidence" / "asset-classification.json", {"assets": []})
        write_json(root / "study.json", {"primary_source": {"commit": "a" * 40}})
        build_reference_views.build(root)
        pwsh = shutil.which("pwsh")
        if pwsh is None:
            self.skipTest("PowerShell 7 is required for the source-parser integration case")
        parsed = subprocess.run([
            pwsh, "-NoProfile", "-NonInteractive", "-File",
            str(PROJECT / "research_tools" / "repository_study" / "parse_powershell.ps1"),
            "-SourceRoot", str(root / "source"), "-Inventory", str(root / "evidence" / "inventory.json"),
            "-Output", str(root / "evidence" / "powershell-static-checks.json"),
        ], capture_output=True, text=True, timeout=30)
        self.assertEqual(parsed.returncode, 0, parsed.stdout + parsed.stderr)
        before = self.files(root)
        with patch.object(repository_verify, "git", side_effect=local_git):
            verified = repository_verify.verify(root, objects)
        self.assertEqual(verified["result"], "PASS", verified)
        self.assertEqual(self.files(root), before)
        self.assertEqual(verified["host_worktree"], "NOT_ASSESSED")

    def test_static_python_failure_is_not_reported_as_success(self):
        root, _, _ = self.repository(bad_python=True)
        result = catalog_source.catalog(root)
        self.assertEqual(result["status"], "FAIL")
        self.assertEqual(result["static_failures"], 1)

    def test_host_comparison_does_not_execute_status_filters_or_monitors(self):
        data = b"synthetic host file\n"
        (self.root / "tracked.txt").write_bytes(data)
        oid = hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()
        responses = [
            ("a" * 40 + "\n").encode(), f"100644 blob {oid}\ttracked.txt".encode() + b"\0",
            f"100644 {oid} 0\ttracked.txt".encode() + b"\0", b"",
        ]
        with patch.object(subprocess, "run", side_effect=[
            subprocess.CompletedProcess([], 0, stdout=value) for value in responses
        ]) as run:
            self.assertEqual(repository_verify.compare_host(self.root, "a" * 40), "CLEAN_UNCHANGED_EXACT_BYTES")
        for call in run.call_args_list:
            command = call.args[0]
            self.assertNotIn("status", command)
            self.assertNotIn("diff", command)
            self.assertIn("core.fsmonitor=false", command)
            self.assertEqual(call.kwargs["env"]["GIT_OPTIONAL_LOCKS"], "0")

    def test_host_exact_byte_comparison_reports_changed_content(self):
        (self.root / "tracked.txt").write_bytes(b"changed")
        responses = [
            ("a" * 40 + "\n").encode(), ("100644 blob " + "b" * 40 + "\ttracked.txt\0").encode(),
            ("100644 " + "b" * 40 + " 0\ttracked.txt\0").encode(), b"",
        ]
        with patch.object(subprocess, "run", side_effect=[
            subprocess.CompletedProcess([], 0, stdout=value) for value in responses
        ]):
            self.assertEqual(repository_verify.compare_host(self.root, "a" * 40), "REQUIRES_INSPECTION")

    def test_freeze_only_selected_files_and_verify_without_workspace_inference(self):
        source = self.root / "selected"
        source.mkdir()
        (source / "include.txt").write_bytes(b"selected")
        (source / "unrelated.txt").write_bytes(b"not selected")
        output = self.root / "checkpoint"
        before = self.files(source)
        result = freeze_workspace.freeze(source, output, "synthetic", {"schema_version": 1, "files": ["include.txt"]})
        self.assertEqual(result["status"], "FROZEN_VERIFIED")
        manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual([record["path"] for record in manifest["files"]], ["include.txt"])
        self.assertEqual(verify_checkpoint.verify(manifest, output)["status"], "PASS")
        self.assertEqual(self.files(source), before)
        with self.assertRaisesRegex(ValueError, "explicit workspace"):
            verify_checkpoint.verify(manifest, output, working=True)

    def test_checkpoint_limits_and_new_only_output(self):
        source = self.root / "source"
        source.mkdir()
        (source / "one.txt").write_bytes(b"synthetic")
        selection = {"schema_version": 1, "files": ["one.txt"]}
        with self.assertRaisesRegex(ValueError, "bound"):
            freeze_workspace.freeze(source, self.root / "too-small", "synthetic", selection, max_bytes=2)
        self.assertFalse((self.root / "too-small").exists())
        output = self.root / "checkpoint"
        output.mkdir()
        with self.assertRaisesRegex(ValueError, "new"):
            freeze_workspace.freeze(source, output, "synthetic", selection)

    def test_prior_checkpoint_helper_is_never_executed_or_auto_included(self):
        source = self.root / "source"
        source.mkdir()
        (source / "one.txt").write_bytes(b"original")
        selection = {"schema_version": 1, "files": ["one.txt"]}
        previous = self.root / "previous"
        freeze_workspace.freeze(source, previous, "previous", selection)
        (previous / "verify_checkpoint.py").write_text("raise RuntimeError('untrusted checkpoint helper')", encoding="utf-8")
        (source / "one.txt").write_bytes(b"intentional update")
        next_output = self.root / "next"
        with self.assertRaisesRegex(ValueError, "Unexpected change"):
            freeze_workspace.freeze(source, next_output, "next", selection, previous_root=previous)
        selection["expected_working_updates"] = ["one.txt"]
        freeze_workspace.freeze(source, next_output, "next", selection, previous_root=previous)
        manifest = json.loads((next_output / "manifest.json").read_text(encoding="utf-8"))
        self.assertFalse(manifest["previous_checkpoint"]["archive_automatically_included"])
        self.assertEqual(manifest["previous_checkpoint"]["intentional_working_updates"], ["one.txt"])


def load_tests(loader, tests, pattern):
    for name in (
        "research_tools.public_repositories.test_study",
        "research_tools.wiki.test_collect_wiki",
        "research_tools.checkpoints.test_checkpoint",
    ):
        tests.addTests(loader.loadTestsFromName(name))
    return tests


if __name__ == "__main__":
    unittest.main()
