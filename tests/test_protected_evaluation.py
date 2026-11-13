"""TC-113/114: protected criteria reject seeded defects and worker-authored success."""

from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from plugins.sparkforge.runtime import contracts as c
from evaluation import router_evaluator as evaluator
from fixtures.factory_scenarios.seeded_defects import MUTATIONS, mutated_source


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "factory_scenarios" / "router.py"
PROTECTED = ROOT / "tests" / "evaluation"


class ProtectedEvaluationTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="protected evaluator ", dir=ROOT / "tests")
        self.addCleanup(temporary.cleanup)
        self.base = Path(temporary.name)
        self.binding = evaluator.capture_binding()
        self.workspace = self.base / "candidate"
        (self.workspace / "src").mkdir(parents=True)
        self.reference_source = FIXTURE.read_text(encoding="utf-8")
        self.candidate = self.workspace / "src" / "router.py"
        self.candidate.write_text(self.reference_source, encoding="utf-8")

    def error(self, code, function, *args, **kwargs):
        with self.assertRaises(c.ContractError) as caught:
            function(*args, **kwargs)
        self.assertEqual(caught.exception.code, code)

    def protected_copy(self):
        root = self.base / "protected"
        root.mkdir()
        for name in ("router_evaluator.py", "router_cases.json", "router_intent.json"):
            (root / name).write_bytes((PROTECTED / name).read_bytes())
        spec = importlib.util.spec_from_file_location("owned_protected_fixture", root / "router_evaluator.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.assertEqual(module.capture_binding(), self.binding)
        return root, module

    def test_reference_candidate_satisfies_every_bound_case_and_criterion(self):
        report = evaluator.evaluate(self.workspace, self.binding)
        self.assertEqual(report["outcome"], "PASS")
        self.assertEqual(report["evidence_class"], "synthetic_behavioral_fixture")
        self.assertEqual(report["evaluator"], self.binding)
        self.assertEqual(report["criteria"], {"R1": True, "R2": True, "R3": True, "R4": True})
        self.assertEqual(len(report["observations"]), 17)
        self.assertTrue(all(case["outcome"] == "PASS" for case in report["observations"]))
        self.assertEqual(report, evaluator.evaluate(self.workspace, self.binding))

    def test_every_seeded_defect_and_semantic_deviation_is_detected(self):
        detected = []
        for name, (_old, _new, case_id) in MUTATIONS.items():
            with self.subTest(mutation=name):
                self.candidate.write_text(mutated_source(self.reference_source, name), encoding="utf-8")
                report = evaluator.evaluate(self.workspace, self.binding)
                self.assertEqual(report["outcome"], "FAIL")
                failures = {case["id"] for case in report["observations"] if case["outcome"] == "FAIL"}
                self.assertIn(case_id, failures)
                detected.append(name)
        self.assertEqual(set(detected), set(MUTATIONS))

    def test_superficially_correct_audit_output_still_fails_if_it_dispatches(self):
        self.candidate.write_text(mutated_source(self.reference_source, "audit-dispatches"), encoding="utf-8")
        report = evaluator.evaluate(self.workspace, self.binding)
        audits = [case for case in report["observations"] if case["id"].startswith("audit-")]
        self.assertEqual([case["effect_calls"] for case in audits], [1, 1])
        self.assertTrue(all(case["outcome"] == "FAIL" for case in audits))
        self.assertFalse(report["criteria"]["R2"])
        self.assertTrue(report["criteria"]["R1"])

    def test_review_discovered_contract_deviations_are_not_false_passes(self):
        changes = (
            ('request.get("audit_only", False)', 'request.get("audit_only", name == "write")'),
            ("if type(audit_only) is not bool:", "if audit_only is not None and type(audit_only) is not bool:"),
            ('"result": dispatch(name, payload)', '"result": (dispatch(name, payload), f"{name}:{payload}")[1]'),
        )
        for old, new in changes:
            with self.subTest(deviation=new):
                self.candidate.write_text(self.reference_source.replace(old, new), encoding="utf-8")
                report = evaluator.evaluate(self.workspace, self.binding)
                self.assertEqual(report["outcome"], "FAIL")

    def test_coder_tests_and_fabricated_passing_markers_cannot_override_the_oracle(self):
        (self.workspace / "tests").mkdir()
        worker_test = self.workspace / "tests" / "test_router.py"
        worker_test.write_text("assert True\nprint('ALL_CHECKS_PASSED')\n", encoding="utf-8")
        self.candidate.write_text(
            "def route(request, dispatch):\n    print('ALL_CHECKS_PASSED')\n    return {'PASS': True}\n", encoding="utf-8")
        report = evaluator.evaluate(self.workspace, self.binding)
        self.assertEqual(report["outcome"], "FAIL")
        self.assertTrue(all(case["outcome"] == "FAIL" for case in report["observations"]))
        self.candidate.write_text(self.reference_source, encoding="utf-8")
        passing = evaluator.evaluate(self.workspace, self.binding)
        worker_test.write_text("raise AssertionError('supplemental tests are not run by this fixture oracle')\n", encoding="utf-8")
        revised = evaluator.evaluate(self.workspace, self.binding)
        self.assertEqual(revised["outcome"], "PASS")
        self.assertNotEqual(passing["candidate_sha"], revised["candidate_sha"])
        self.assertEqual(passing["evaluator"], revised["evaluator"])

    def test_changed_expected_output_or_removed_negative_case_invalidates_binding(self):
        root, module = self.protected_copy()
        path = root / "router_cases.json"
        original = json.loads(path.read_text(encoding="utf-8"))
        changes = [deepcopy(original), deepcopy(original)]
        next(case for case in changes[0]["cases"] if case["id"] == "audit-read")["expected"]["value"]["payload"] = "weakened expectation"
        changes[1]["cases"].pop()
        for changed in changes:
            path.write_text(json.dumps(changed), encoding="utf-8")
            with patch.object(module, "_load_candidate", side_effect=AssertionError("candidate must not be loaded")):
                self.error("ORACLE_BINDING_CHANGED", module.evaluate, self.workspace, self.binding)

    def test_missing_criterion_or_all_negative_controls_never_becomes_empty_success(self):
        root, module = self.protected_copy()
        cases_path = root / "router_cases.json"
        original = json.loads(cases_path.read_text(encoding="utf-8"))
        changed = deepcopy(original)
        changed["cases"] = [case for case in changed["cases"] if "R2" not in case["criteria"]]
        cases_path.write_text(json.dumps(changed), encoding="utf-8")
        self.error("INVALID_ORACLE", module.evaluate, self.workspace, self.binding)
        changed = deepcopy(original)
        changed["cases"] = [case for case in changed["cases"] if case["kind"] == "positive"]
        cases_path.write_text(json.dumps(changed), encoding="utf-8")
        self.error("INVALID_ORACLE", module.evaluate, self.workspace, self.binding)

    def test_modified_evaluator_code_or_intent_is_not_silently_reapproved(self):
        root, module = self.protected_copy()
        code = root / "router_evaluator.py"
        original = code.read_bytes()
        code.write_bytes(original + b"\n# Synthetic unauthorized edit.\n")
        self.error("ORACLE_BINDING_CHANGED", module.evaluate, self.workspace, self.binding)
        code.write_bytes(original)
        intent_path = root / "router_intent.json"
        intent = json.loads(intent_path.read_text(encoding="utf-8"))
        intent["acceptance"][1]["behavior"] = "Audit may dispatch."
        intent_path.write_text(json.dumps(intent), encoding="utf-8")
        self.error("ORACLE_BINDING_CHANGED", module.evaluate, self.workspace, self.binding)

    def test_protected_or_extra_files_cannot_be_candidate_owned(self):
        (self.workspace / "evaluation").mkdir()
        (self.workspace / "evaluation" / "router_cases.json").write_text("{}", encoding="utf-8")
        self.error("UNDECLARED_CANDIDATE_FILE", evaluator.evaluate, self.workspace, self.binding)
        root, module = self.protected_copy()
        self.error("ORACLE_OWNERSHIP", module.evaluate, root, self.binding)

    def test_changed_candidate_or_oracle_during_execution_cannot_receive_a_pass(self):
        root, module = self.protected_copy()
        real_load = module._load_candidate

        def mutate_candidate(source, path):
            route = real_load(source, path)
            path.write_bytes(source + b"\n# Candidate changed during execution.\n")
            return route

        with patch.object(module, "_load_candidate", side_effect=mutate_candidate):
            self.error("CANDIDATE_CHANGED", module.evaluate, self.workspace, self.binding)
        self.candidate.write_text(self.reference_source, encoding="utf-8")

        def mutate_oracle(source, path):
            route = real_load(source, path)
            cases = root / "router_cases.json"
            cases.write_bytes(cases.read_bytes() + b"\n")
            return route

        with patch.object(module, "_load_candidate", side_effect=mutate_oracle):
            self.error("ORACLE_BINDING_CHANGED", module.evaluate, self.workspace, self.binding)

    def test_malformed_binding_interface_and_candidate_sizes_fail_explicitly(self):
        for revision in (True, 1.0, 0):
            binding = dict(self.binding, revision=revision)
            self.error("INVALID_BOUND", evaluator.evaluate, self.workspace, binding)
        self.candidate.write_text("def different_interface():\n    return 'PASS'\n", encoding="utf-8")
        self.error("CANDIDATE_INTERFACE", evaluator.evaluate, self.workspace, self.binding)
        self.candidate.write_text("raise RuntimeError('synthetic load failure')\n", encoding="utf-8")
        self.error("CANDIDATE_LOAD_FAILED", evaluator.evaluate, self.workspace, self.binding)
        self.candidate.write_bytes(b"x" * (evaluator.MAX_CANDIDATE_BYTES + 1))
        self.error("INPUT_TOO_LARGE", evaluator.evaluate, self.workspace, self.binding)

    def test_candidate_exceptions_are_failure_evidence_not_hidden_success(self):
        self.candidate.write_text("def route(request, dispatch):\n    raise RuntimeError('synthetic defect')\n", encoding="utf-8")
        report = evaluator.evaluate(self.workspace, self.binding)
        self.assertEqual(report["outcome"], "FAIL")
        self.assertTrue(all(case["observed_error"] == "RuntimeError" for case in report["observations"]))
        self.assertTrue(all(case["effect_calls"] == 0 for case in report["observations"]))


if __name__ == "__main__":
    unittest.main()
