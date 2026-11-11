"""Cross-module acceptance: real snapshot readers, spec records, check processes and packaging."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts import build_sparkforge_package as packaging


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "plugins" / "sparkforge"


def load(name: str, path: Path):
    specification = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(specification)
    sys.modules[name] = module
    specification.loader.exec_module(module)
    return module


core = load("native_integration_factory", PACKAGE / "scripts" / "factory.py")
knowledge = load("native_integration_knowledge", PACKAGE / "scripts" / "knowledge.py")


class NativeIntegrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="native integration ", dir=ROOT / "tests")
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)
        self.wiki = self.base / "wiki"
        self.repo = self.base / "source"
        self.workspace = self.base / "candidate"
        for path in (self.wiki, self.repo, self.workspace):
            path.mkdir()
        self.wiki_revision = "a" * 40
        self.repository_revision = "b" * 40
        wiki_text = "SPARK contributor guidance: inspect existing components, freeze the spec, and preserve real check evidence."
        page = self.wiki / "guidance.md"
        page.write_text(wiki_text, encoding="utf-8")
        manifest = {
            "corpus_id": "synthetic-integration-wiki", "snapshot_commit": self.wiki_revision,
            "pages": [{
                "page_id": 1, "path": "/AI/SPARK/Contributor guidance", "local_path": "guidance.md",
                "snapshot_commit": self.wiki_revision, "status": "EXPORTED",
                "sha256": hashlib.sha256(page.read_bytes()).hexdigest(),
                "canonical_url": "https://example.invalid/wiki/1", "bytes": len(page.read_bytes()),
            }],
        }
        (self.wiki / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
        source_files = {
            "plugins/example/plugin.json": json.dumps({
                "name": "example", "description": "SPARK reuse decision component",
                "version": "0.1.0", "skills": ["skills/example"], "agents": [],
            }),
            "plugins/example/README.md": "# Existing component\nImprove this component rather than duplicate it.",
            "plugins/example/skills/example/SKILL.md": "# Example\nUse the existing bounded decision helper.",
            "plugins/example/scripts/decision.py": "# Untrusted source text; never execute on retrieval.\nraise RuntimeError('SOURCE_MUST_NOT_EXECUTE')\n",
        }
        entries = []
        for relative, content in source_files.items():
            path = self.repo.joinpath(*relative.split("/"))
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            data = path.read_bytes()
            entries.append({
                "path": relative, "git_type": "blob", "mode": "100644",
                "sha256": hashlib.sha256(data).hexdigest(), "size_bytes": len(data),
            })
        self.inventory = self.base / "inventory.json"
        self.inventory.write_text(json.dumps({
            "snapshot": {"repository": "synthetic/example", "commit": self.repository_revision},
            "entries": entries,
        }), encoding="utf-8")

    def spec(self) -> dict:
        wiki = knowledge.wiki_context(self.wiki, "SPARK", page_ids=[1])
        catalog = knowledge.catalog_context(self.repo, self.inventory, "reuse")
        component = knowledge.component_context(self.repo, self.inventory, "example")
        code = knowledge.source_context(self.repo, self.inventory, ["plugins/example/scripts/decision.py"])
        self.assertIn("SOURCE_MUST_NOT_EXECUTE", code["items"][0]["selected_text"])
        self.assertEqual(wiki["current_coverage"], "NOT_ASSESSED")
        self.assertEqual(catalog["items"][0]["manifest"]["name"], "example")
        self.assertGreaterEqual(len(component["items"]), 3)
        return {
            "schema_version": "sparkforge.spec.v1", "id": "INTEGRATION-001",
            "title": "Improve an existing decision helper",
            "problem": "An existing synthetic component needs exact supported-action validation.",
            "audience": "Synthetic integration operator", "environment": "LOCAL_DEVELOPMENT",
            "builder_actor": "fixture-builder",
            "non_goals": ["No model, network, install, publication or authentic user approval."],
            "knowledge": {
                "wiki_revision": wiki["source"]["revision"],
                "repository_revision": catalog["source"]["revision"],
                "citations": [wiki["items"][0]["citation"], component["items"][0]["citation"], code["items"][0]["citation"]],
                "coverage": "SNAPSHOT_SCOPE", "limitations": ["Synthetic sources only; current live coverage is NOT_ASSESSED."],
            },
            "reuse": {
                "decision": "UPDATE_EXISTING", "target": "example",
                "rationale": "The inspected component owns the requested behavior.",
                "inspected_candidates": ["example"],
            },
            "controlled_files": ["component.py", "check.py"],
            "acceptance": [{
                "id": "A1", "behavior": "All supported actions map correctly and unknown actions are rejected.",
                "checks": ["decision-behavior"],
            }],
            "checks": [{
                "id": "decision-behavior", "argv": ["python", "-B", "check.py"],
                "timeout_seconds": 5, "output_limit_bytes": 4096,
                "max_attempts": 2, "required_markers": ["REUSE-CONTRACT-OK"], "retain_output": False,
            }],
            "required_reviewers": ["quality"],
        }

    def test_adapter_citations_are_directly_usable_by_the_spec_validator(self) -> None:
        spec = self.spec()
        self.assertEqual(core.validate_spec(spec), spec)
        self.assertEqual({item["source"] for item in spec["knowledge"]["citations"]}, {"wiki", "repository"})

    def test_actual_code_inspection_preserves_source_integrity(self) -> None:
        path = self.repo / "plugins" / "example" / "scripts" / "decision.py"
        path.write_text("changed source\n", encoding="utf-8")
        with self.assertRaises(knowledge.KnowledgeError) as caught:
            knowledge.source_context(self.repo, self.inventory, ["plugins/example/scripts/decision.py"])
        self.assertEqual(caught.exception.code, "HASH_MISMATCH")

    def test_source_to_spec_to_real_failure_repair_and_review(self) -> None:
        spec = self.spec()
        checks = (
            "from component import classify\n"
            "assert classify('reuse') == 'REUSE'\n"
            "assert classify('update') == 'UPDATE_EXISTING'\n"
            "assert classify('new') == 'NEW_COMPONENT'\n"
            "try:\n    classify('unsupported')\n"
            "except ValueError:\n    pass\n"
            "else:\n    raise AssertionError('Unknown action was accepted')\n"
            "print('REUSE-CONTRACT-OK')\n"
        )
        (self.workspace / "check.py").write_text(checks, encoding="utf-8")
        job = self.base / "job"
        proposed = core.init_job(spec, self.workspace, job)
        self.assertEqual(proposed["status"], "AWAITING_APPROVAL")
        with self.assertRaises(core.FactoryError) as caught:
            core.run_check(job, "decision-behavior", confirm_run=True)
        self.assertEqual(caught.exception.code, "APPROVAL_REQUIRED")
        core.decide(job, proposed["spec_sha"], "accept", "synthetic-operator")
        candidate = self.workspace / "component.py"
        candidate.write_text("def classify(value):\n    return value.upper()\n", encoding="utf-8")
        failed = core.run_check(job, "decision-behavior", confirm_run=True)
        self.assertEqual(failed["check"]["outcome"], "FAIL")
        candidate.write_text(
            "def classify(value):\n"
            "    choices = {'reuse': 'REUSE', 'update': 'UPDATE_EXISTING', 'new': 'NEW_COMPONENT'}\n"
            "    if value not in choices:\n        raise ValueError('Unsupported action')\n"
            "    return choices[value]\n",
            encoding="utf-8",
        )
        passed = core.run_check(job, "decision-behavior", confirm_run=True)
        self.assertEqual(passed["check"]["outcome"], "PASS")
        self.assertNotEqual(failed["check"]["candidate_sha"], passed["check"]["candidate_sha"])
        review = core.job_status(job)
        final = core.record_review(
            job, review["candidate_sha"], "quality", "pass", "synthetic-reviewer",
            "Synthetic reviewer fixture; actual subprocess behavior was observed.",
            review_context=review["review_context"],
        )
        self.assertEqual(final["status"], "CANDIDATE_VERIFIED")
        self.assertTrue(final["human_acceptance_required"])
        self.assertFalse(final["publication_authorized"])
        self.assertEqual(final["attempt_count"], 2)

    def test_shipped_spec_example_passes_the_actual_factory_schema(self) -> None:
        document = (PACKAGE / "references" / "SPEC_FORMAT.md").read_text(encoding="utf-8")
        examples = re.findall(r"```json\s*\n(.*?)\n```", document, re.S)
        self.assertTrue(examples)
        for example in examples:
            core.validate_spec(json.loads(example))

    def test_both_real_packages_relocate_and_the_owned_helper_runs(self) -> None:
        for profile in ("corp", "acro"):
            with self.subTest(profile=profile):
                output = self.base / (profile + "-package")
                receipt = packaging.build_package(profile, output)
                self.assertEqual(receipt["compatibility"], "NOT_ASSESSED")
                relocated = self.base / ("relocated-" + profile)
                output.rename(relocated)
                self.assertTrue(packaging.validate_package(relocated, profile)["valid"])
                result = subprocess.run(
                    [sys.executable, "-B", str(relocated / "scripts" / "factory.py"), "--help"],
                    cwd=self.base, capture_output=True, text=True, timeout=10, check=False,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn("run-check", result.stdout)
                manifest = json.loads((relocated / "plugin.json").read_text(encoding="utf-8"))
                self.assertEqual((relocated / "agency.json").exists(), profile == "corp")
                self.assertEqual(manifest.get("engines"), ["copilot"] if profile == "acro" else None)


if __name__ == "__main__":
    unittest.main()
