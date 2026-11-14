"""Protected behavioral fixture runner for trusted synthetic code, not an OS sandbox."""

from contextlib import redirect_stdout, redirect_stderr
from copy import deepcopy
import hashlib
import io
from pathlib import Path
from typing import Callable, TypedDict

from plugins.sparkforge.runtime import contracts as c
from plugins.sparkforge.scripts import factory as v1


ALLOWED_FILES = ("src/router.py", "tests/test_router.py")
MAX_CANDIDATE_BYTES = 64 * 1024


class OracleBinding(TypedDict):
    schema_version: str
    id: str
    revision: int
    intent_sha: str
    manifest_sha: str


def _protected_files() -> list[tuple[str, Path]]:
    root = Path(__file__).resolve().parent
    return [
        ("router_evaluator.py", root / "router_evaluator.py"),
        ("router_cases.json", root / "router_cases.json"),
        ("router_intent.json", root / "router_intent.json"),
        ("runtime/contracts.py", Path(c.__file__)),
        ("scripts/factory.py", Path(v1.__file__)),
    ]


def _oracle() -> tuple[c.IntentBaseline, dict, OracleBinding]:
    blobs = {}
    manifest = []
    for name, path in _protected_files():
        root = v1._directory(path.parent)
        path = v1._file(root, path.name)
        data = path.read_bytes()
        if len(data) > c.MAX_JSON_BYTES:
            c._fail("INPUT_TOO_LARGE", "oracle", "Protected evaluator input exceeds its byte bound.")
        blobs[name] = data
        manifest.append({"path": name, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()})
    intent = c.validate_intent(c.parse_json(blobs["router_intent.json"]), supported_component_kinds=("fictional-python-router",))
    oracle = c._object(c.parse_json(blobs["router_cases.json"]), {"schema_version", "id", "revision", "intent_id", "cases"}, "oracle")
    if oracle["schema_version"] != "sparkforge.router-oracle.v1" or oracle["intent_id"] != intent["id"]:
        c._fail("INVALID_ORACLE", "oracle", "Unsupported or foreign oracle.")
    ids, coverage, kinds = [], set(), set()
    criteria = {item["id"] for item in intent["acceptance"]}
    for item in c._list(oracle["cases"], "oracle.cases", minimum=1):
        case = c._object(item, {"id", "kind", "criteria", "request", "dispatch_result", "expected"}, "oracle.case")
        ids.append(c._identifier(case["id"], "oracle.case.id"))
        kinds.add(c._enum(case["kind"], ("positive", "negative"), "oracle.case.kind"))
        refs = c._strings(case["criteria"], "oracle.case.criteria", identifiers=True, minimum=1)
        if not set(refs) <= criteria:
            c._fail("INVALID_ORACLE", "oracle.case.criteria", "Case refers to unknown intent criteria.")
        coverage.update(refs)
        expected = c._object(case["expected"], {"value", "error", "calls"}, "oracle.case.expected")
        c._list(expected["calls"], "oracle.case.expected.calls")
        if expected["error"] not in (None, "ValueError") or (
            (case["kind"] == "negative") != (expected["error"] == "ValueError")
        ):
            c._fail("INVALID_ORACLE", "oracle.case.expected", "Negative controls must require the declared error.")
        if expected["error"] is not None and (expected["value"] is not None or expected["calls"]):
            c._fail("INVALID_ORACLE", "oracle.case.expected", "Rejected input cannot have a value or dispatched effect.")
    c._unique(ids, "oracle.cases")
    if coverage != criteria or kinds != {"positive", "negative"}:
        c._fail("INVALID_ORACLE", "oracle.cases", "Every criterion and both positive/negative controls are required.")
    binding: OracleBinding = {
        "schema_version": "sparkforge.oracle-binding.v1",
        "id": c._identifier(oracle["id"], "oracle.id"),
        "revision": c._integer(oracle["revision"], "oracle.revision"),
        "intent_sha": c.record_digest(intent), "manifest_sha": c.record_digest(manifest),
    }
    return intent, oracle, binding


def capture_binding() -> OracleBinding:
    """Evaluator-owner preparation before candidate access; not an approval endpoint."""
    return _oracle()[2]


def _expected_binding(value: object) -> OracleBinding:
    record = c._object(value, {"schema_version", "id", "revision", "intent_sha", "manifest_sha"}, "expected_binding")
    if record["schema_version"] != "sparkforge.oracle-binding.v1":
        c._fail("UNSUPPORTED_SCHEMA", "expected_binding", "Unsupported evaluator binding.")
    return {
        "schema_version": "sparkforge.oracle-binding.v1", "id": c._identifier(record["id"], "expected_binding.id"),
        "revision": c._integer(record["revision"], "expected_binding.revision"),
        "intent_sha": c._sha(record["intent_sha"], "expected_binding.intent_sha"),
        "manifest_sha": c._sha(record["manifest_sha"], "expected_binding.manifest_sha"),
    }


def _candidate(workspace: Path) -> tuple[bytes, str]:
    workspace = v1._directory(workspace)
    if any(path.is_relative_to(workspace) for _, path in _protected_files()):
        c._fail("ORACLE_OWNERSHIP", "workspace", "The protected evaluator cannot be inside candidate-owned paths.")
    names = []
    for path in workspace.rglob("*"):
        info = path.lstat()
        if v1._redirected(info):
            c._fail("UNSAFE_PATH", "candidate", "Candidate links and redirected directories are forbidden.")
        if path.is_file():
            name = path.relative_to(workspace).as_posix()
            if name not in ALLOWED_FILES:
                c._fail("UNDECLARED_CANDIDATE_FILE", "candidate", "Candidate contains a file outside the fixed owned inventory.")
            names.append(name)
    if "src/router.py" not in names:
        c._fail("MISSING_CANDIDATE", "candidate", "The fictional routing component is missing.")
    manifest, implementation = [], b""
    for name in sorted(names):
        path = v1._file(workspace, name)
        with path.open("rb") as stream:
            data = stream.read(MAX_CANDIDATE_BYTES + 1)
        if len(data) > MAX_CANDIDATE_BYTES:
            c._fail("INPUT_TOO_LARGE", "candidate", "Synthetic candidate file exceeds 64 KiB.")
        manifest.append({"path": name, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()})
        if name == "src/router.py":
            implementation = data
    return implementation, c.record_digest(manifest)


def _load_candidate(source: bytes, path: Path) -> Callable:
    namespace = {"__name__": "synthetic_router_candidate", "__file__": str(path)}
    try:
        exec(compile(source, str(path), "exec"), namespace)
    except Exception as error:
        c._fail("CANDIDATE_LOAD_FAILED", "candidate", f"Synthetic component failed to load ({type(error).__name__}).")
    route = namespace.get("route")
    if not callable(route):
        c._fail("CANDIDATE_INTERFACE", "candidate", "Candidate must export route(request, dispatch).")
    return route


def evaluate(workspace: Path, expected_binding: OracleBinding) -> dict:
    """Evaluate owned trusted fixtures against a caller-pinned, outside-workspace oracle."""
    expected_binding = _expected_binding(expected_binding)
    intent, oracle, binding = _oracle()
    if binding != expected_binding:
        c._fail("ORACLE_BINDING_CHANGED", "oracle", "Protected evaluator/code/criteria differ from the selected revision.")
    source, candidate_sha = _candidate(workspace)
    observations = []
    with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
        route = _load_candidate(source, workspace / "src" / "router.py")
        for case in oracle["cases"]:
            request, calls = deepcopy(case["request"]), []

            def dispatch(name, payload):
                calls.append([name, payload])
                return deepcopy(case["dispatch_result"])

            result, error_name = None, None
            try:
                result = route(request, dispatch)
                c.canonical_json(result)
            except Exception as error:
                error_name = type(error).__name__
                result = None
            actual = {"value": result, "error": error_name, "calls": calls}
            actual_sha = c.record_digest(actual)
            expected_sha = c.record_digest(case["expected"])
            unchanged = c.canonical_json(request) == c.canonical_json(case["request"])
            observations.append({
                "id": case["id"], "criteria": case["criteria"][:],
                "outcome": "PASS" if actual_sha == expected_sha and unchanged else "FAIL",
                "expected_sha": expected_sha, "actual_sha": actual_sha, "input_unchanged": unchanged,
                "observed_error": error_name, "effect_calls": len(calls),
            })
    if _oracle()[2] != expected_binding:
        c._fail("ORACLE_BINDING_CHANGED", "oracle", "Evaluator inputs changed during candidate execution; no result admitted.")
    if _candidate(workspace)[1] != candidate_sha:
        c._fail("CANDIDATE_CHANGED", "candidate", "Candidate bytes changed during evaluation; no result admitted.")
    coverage = {item["id"]: all(observation["outcome"] == "PASS" for observation in observations
                               if item["id"] in observation["criteria"]) for item in intent["acceptance"]}
    return {
        "schema_version": "sparkforge.synthetic-evaluation.v1",
        "evidence_class": "synthetic_behavioral_fixture", "evaluator": binding, "candidate_sha": candidate_sha,
        "outcome": "PASS" if all(coverage.values()) else "FAIL", "criteria": coverage, "observations": observations,
        "limitations": [
            "Trusted finite fixture code only; in-process evaluation is not an OS sandbox or a bounded production runner.",
            "Independent role/controller/reuse/recovery and live platform/domain acceptance remain NOT_ASSESSED.",
            "Worker-owned tests and stdout/stderr markers are not protected acceptance evidence.",
        ],
    }
