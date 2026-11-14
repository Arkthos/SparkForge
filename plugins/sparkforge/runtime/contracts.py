"""Pure coordinated-record validation. Records bind proposals, never grant authority."""

from __future__ import annotations

import hashlib
import json
import math
import re
import unicodedata
from datetime import datetime
from typing import NoReturn, TypedDict


MAX_JSON_BYTES = 2 * 1024 * 1024
MAX_JSON_DEPTH = 32
MAX_TEXT_CHARS = 12000
MAX_ITEMS = 128
INTENT_VERSION = "sparkforge.intent.v1"
ENVELOPE_VERSION = "sparkforge.envelope.v1"


class ContractError(ValueError):
    def __init__(self, code: str, path: str, message: str) -> None:
        super().__init__(f"{path}: {message}")
        self.code = code
        self.path = path


class Reference(TypedDict):
    id: str
    revision: int


class Criterion(TypedDict):
    id: str
    behavior: str


class SourceReference(TypedDict):
    id: str
    revision: str | None
    sha256: str | None


class SourceAssumption(TypedDict):
    id: str
    status: str
    statement: str
    reason: str
    references: list[SourceReference]


class IntentBaseline(TypedDict):
    schema_version: str
    id: str
    revision: int
    problem: str
    outcome: str
    audience: str
    component_kind: str
    acceptance: list[Criterion]
    non_goals: list[str]
    material_constraints: list[str]
    source_assumptions: list[SourceAssumption]


class Root(TypedDict):
    id: str
    flavor: str
    path: str


class JobBounds(TypedDict):
    wall_seconds: int
    max_agent_attempts: int
    max_model_calls: int
    max_check_runs: int
    max_replans: int
    max_tokens: int


class AgentBounds(TypedDict):
    timeout_seconds: int
    max_attempts: int
    max_model_calls: int
    max_tokens: int


class CheckBounds(TypedDict):
    timeout_seconds: int
    max_attempts: int
    output_limit_bytes: int


class Bounds(TypedDict):
    job: JobBounds
    agent: AgentBounds
    check: CheckBounds


class IntentBinding(TypedDict):
    id: str
    sha256: str


class Routes(TypedDict):
    host: Reference
    provider: Reference


class Revocation(TypedDict):
    revoked_at: str | None
    reason: str | None


class ExecutionEnvelope(TypedDict):
    schema_version: str
    id: str
    revision: int
    intent: IntentBinding
    environment: str
    profile: Reference
    workspace_roots: list[Root]
    data_roots: list[Root]
    tools: list[str]
    effects: list[str]
    routes: Routes
    bounds: Bounds
    unknown_usage: str
    expires_at: str
    revocation: Revocation


def _fail(code: str, path: str, message: str) -> NoReturn:
    raise ContractError(code, path, message)


def _object(value: object, fields: set[str], path: str) -> dict:
    if type(value) is not dict or set(value) != fields:
        _fail("INVALID_FIELDS", path, f"Expected exactly: {', '.join(sorted(fields))}.")
    return value


def _text(value: object, path: str, *, limit: int = MAX_TEXT_CHARS) -> str:
    if type(value) is not str or not value.strip() or len(value) > limit:
        _fail("INVALID_TEXT", path, f"Expected nonblank text of at most {limit} characters.")
    if any(unicodedata.category(char) in {"Cc", "Cf", "Cs"} and char not in "\t\r\n" for char in value):
        _fail("INVALID_TEXT", path, "Control, formatting and surrogate characters are forbidden.")
    return value


def _identifier(value: object, path: str) -> str:
    if type(value) is not str or re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,79}", value) is None:
        _fail("INVALID_IDENTIFIER", path, "Expected 1-80 ASCII letters/digits/._-, starting with a letter or digit.")
    return value


def _integer(value: object, path: str, maximum: int = 1_000_000) -> int:
    if type(value) is not int or not 1 <= value <= maximum:
        _fail("INVALID_BOUND", path, f"Expected an integer in [1, {maximum}], not a boolean.")
    return value


def _enum(value: object, choices: tuple[str, ...], path: str) -> str:
    if type(value) is not str or value not in choices:
        _fail("INVALID_ENUM", path, f"Expected one of: {', '.join(choices)}.")
    return value


def _list(value: object, path: str, *, minimum: int = 0, maximum: int = MAX_ITEMS) -> list:
    if type(value) is not list or not minimum <= len(value) <= maximum:
        _fail("INVALID_LIST", path, f"Expected {minimum}-{maximum} entries.")
    return value


def _unique(values: list[str], path: str) -> list[str]:
    if len(values) != len(set(values)):
        _fail("DUPLICATE_VALUE", path, "Duplicate entries are forbidden.")
    return values


def _strings(value: object, path: str, *, identifiers: bool = False, minimum: int = 0) -> list[str]:
    validate = _identifier if identifiers else _text
    return _unique([validate(item, f"{path}[{index}]")
                    for index, item in enumerate(_list(value, path, minimum=minimum))], path)


def _sha(value: object, path: str) -> str:
    if type(value) is not str or re.fullmatch(r"[0-9a-f]{64}", value) is None:
        _fail("INVALID_DIGEST", path, "Expected a lowercase SHA-256 digest.")
    return value


def _reference(value: object, path: str) -> Reference:
    record = _object(value, {"id", "revision"}, path)
    return {"id": _identifier(record["id"], path + ".id"),
            "revision": _integer(record["revision"], path + ".revision")}


def _timestamp(value: object, path: str) -> str:
    if type(value) is not str or re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", value) is None:
        _fail("INVALID_TIME", path, "Expected a UTC timestamp YYYY-MM-DDTHH:MM:SSZ.")
    try:
        datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError:
        _fail("INVALID_TIME", path, "Invalid calendar timestamp.")
    return value


def _json_pairs(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            _fail("DUPLICATE_JSON_KEY", "$", "Duplicate JSON object keys are forbidden.")
        result[key] = value
    return result


def _nonfinite(value: str) -> NoReturn:
    _fail("INVALID_JSON", "$", "Nonfinite JSON numbers are forbidden.")


def parse_json(data: str | bytes) -> object:
    """Decode bounded UTF-8 JSON without reading files or accepting duplicate keys."""
    if type(data) not in (str, bytes):
        _fail("INVALID_JSON", "$", "Expected JSON text or UTF-8 bytes.")
    try:
        raw = data.encode("utf-8") if isinstance(data, str) else data
        if len(raw) > MAX_JSON_BYTES:
            _fail("INPUT_TOO_LARGE", "$", "JSON exceeds two MiB.")
        value = json.loads(raw.decode("utf-8"), object_pairs_hook=_json_pairs, parse_constant=_nonfinite)
        canonical_json(value)
        return value
    except (UnicodeError, ValueError, RecursionError) as error:
        if isinstance(error, ContractError):
            raise
        _fail("INVALID_JSON", "$", f"Invalid JSON ({type(error).__name__}).")


def canonical_json(value: object) -> str:
    """Serialize a normalized record, preserving list order and all bound fields."""
    pending = [(value, 0)]
    while pending:
        item, depth = pending.pop()
        if depth > MAX_JSON_DEPTH:
            _fail("INVALID_JSON", "$", "JSON nesting exceeds 32 levels.")
        if type(item) is dict:
            if any(type(key) is not str for key in item):
                _fail("INVALID_JSON", "$", "JSON object keys must be strings.")
            pending.extend((child, depth + 1) for child in item.values())
        elif type(item) is list:
            pending.extend((child, depth + 1) for child in item)
        elif type(item) not in (str, int, float, bool, type(None)):
            _fail("INVALID_JSON", "$", "Only JSON objects, arrays and scalar values are supported.")
        elif type(item) is float and not math.isfinite(item):
            _fail("INVALID_JSON", "$", "Nonfinite JSON numbers are forbidden.")
    try:
        result = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)
        if len(result.encode("utf-8")) > MAX_JSON_BYTES:
            _fail("INPUT_TOO_LARGE", "$", "JSON exceeds two MiB.")
        return result
    except (TypeError, ValueError, UnicodeError, RecursionError) as error:
        if isinstance(error, ContractError):
            raise
        _fail("INVALID_JSON", "$", f"Cannot encode canonical JSON ({type(error).__name__}).")


def record_digest(value: object) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def relative_path(value: object, path: str = "path") -> str:
    """Portable, canonical slash-separated relative identifier, not a host lookup."""
    if type(value) is not str or not value or len(value) > 500 or unicodedata.normalize("NFC", value) != value:
        _fail("UNSAFE_PATH", path, "Expected a nonempty NFC path of at most 500 characters.")
    reserved = {"con", "prn", "aux", "nul", "conin$", "conout$",
                *(f"{prefix}{digit}" for prefix in ("com", "lpt") for digit in "123456789\u00b9\u00b2\u00b3")}
    parts = value.split("/")
    if any(not part or part in {".", ".."} or part.endswith((" ", "."))
           or part.split(".")[0].rstrip(" ").casefold() in reserved
           or part.casefold() == ".git"
           or (part.casefold().startswith(".env") and part != ".env.example")
           or any(char in '<>:"\\|?*~' or unicodedata.category(char).startswith("C") for char in part)
           for part in parts):
        _fail("UNSAFE_PATH", path, "Expected a canonical relative path without traversal, aliases or reserved components.")
    return value


def _root(value: object, path: str) -> Root:
    record = _object(value, {"id", "flavor", "path"}, path)
    flavor = _enum(record["flavor"], ("windows", "posix"), path + ".flavor")
    root = _text(record["path"], path + ".path", limit=500)
    if flavor == "windows":
        if re.match(r"^[A-Z]:\\", root) is None or "/" in root:
            _fail("UNSAFE_PATH", path, "Use an uppercase local drive and backslashes; UNC/device/relative roots are forbidden.")
        relative_path(root[3:].replace("\\", "/"), path + ".path")
    else:
        if not root.startswith("/") or root.startswith("//"):
            _fail("UNSAFE_PATH", path, "Use an absolute POSIX path.")
        relative_path(root[1:], path + ".path")
    return {"id": _identifier(record["id"], path + ".id"), "flavor": flavor, "path": root}


def _intent(value: object) -> IntentBaseline:
    record = _object(value, {
        "schema_version", "id", "revision", "problem", "outcome", "audience", "component_kind",
        "acceptance", "non_goals", "material_constraints", "source_assumptions",
    }, "intent")
    if record["schema_version"] != INTENT_VERSION:
        _fail("UNSUPPORTED_SCHEMA", "intent.schema_version", "Unsupported intent version.")
    criteria: list[Criterion] = []
    for index, item in enumerate(_list(record["acceptance"], "intent.acceptance", minimum=1)):
        path = f"intent.acceptance[{index}]"
        criterion = _object(item, {"id", "behavior"}, path)
        criteria.append({"id": _identifier(criterion["id"], path + ".id"),
                         "behavior": _text(criterion["behavior"], path + ".behavior")})
    _unique([item["id"] for item in criteria], "intent.acceptance")
    assumptions: list[SourceAssumption] = []
    for index, item in enumerate(_list(record["source_assumptions"], "intent.source_assumptions", minimum=1)):
        path = f"intent.source_assumptions[{index}]"
        assumption = _object(item, {"id", "status", "statement", "reason", "references"}, path)
        refs: list[SourceReference] = []
        for ref_index, item in enumerate(_list(assumption["references"], path + ".references")):
            ref_path = f"{path}.references[{ref_index}]"
            ref = _object(item, {"id", "revision", "sha256"}, ref_path)
            refs.append({
                "id": _identifier(ref["id"], ref_path + ".id"),
                "revision": None if ref["revision"] is None else _text(ref["revision"], ref_path + ".revision", limit=200),
                "sha256": None if ref["sha256"] is None else _sha(ref["sha256"], ref_path + ".sha256"),
            })
        _unique([ref["id"] for ref in refs], path + ".references")
        assumptions.append({
            "id": _identifier(assumption["id"], path + ".id"),
            "status": _enum(assumption["status"], ("known", "unknown", "unavailable"), path + ".status"),
            "statement": _text(assumption["statement"], path + ".statement"),
            "reason": _text(assumption["reason"], path + ".reason"),
            "references": refs,
        })
    _unique([item["id"] for item in assumptions], "intent.source_assumptions")
    result: IntentBaseline = {
        "schema_version": INTENT_VERSION,
        "id": _identifier(record["id"], "intent.id"),
        "revision": _integer(record["revision"], "intent.revision"),
        "problem": _text(record["problem"], "intent.problem"),
        "outcome": _text(record["outcome"], "intent.outcome"),
        "audience": _text(record["audience"], "intent.audience"),
        "component_kind": _identifier(record["component_kind"], "intent.component_kind"),
        "acceptance": criteria,
        "non_goals": _strings(record["non_goals"], "intent.non_goals"),
        "material_constraints": _strings(record["material_constraints"], "intent.material_constraints"),
        "source_assumptions": assumptions,
    }
    canonical_json(result)
    return result


def validate_intent(value: object, *, supported_component_kinds: tuple[str, ...]) -> IntentBaseline:
    """Validate using the caller's explicit profile vocabulary; do not probe a platform."""
    if type(supported_component_kinds) is not tuple or not 1 <= len(supported_component_kinds) <= MAX_ITEMS:
        _fail("INVALID_PROFILE", "supported_component_kinds", "Supply a bounded nonempty tuple of profile kinds.")
    kinds = _unique([_identifier(kind, "supported_component_kinds") for kind in supported_component_kinds],
                    "supported_component_kinds")
    result = _intent(value)
    if result["component_kind"] not in kinds:
        _fail("UNSUPPORTED_COMPONENT", "intent.component_kind", "Component kind is absent from the supplied profile vocabulary.")
    return result


def _bounds(value: object) -> Bounds:
    record = _object(value, {"job", "agent", "check"}, "envelope.bounds")
    job = _object(record["job"], {
        "wall_seconds", "max_agent_attempts", "max_model_calls", "max_check_runs", "max_replans", "max_tokens",
    }, "envelope.bounds.job")
    agent = _object(record["agent"], {"timeout_seconds", "max_attempts", "max_model_calls", "max_tokens"},
                    "envelope.bounds.agent")
    check = _object(record["check"], {"timeout_seconds", "max_attempts", "output_limit_bytes"}, "envelope.bounds.check")
    result: Bounds = {
        "job": {
            "wall_seconds": _integer(job["wall_seconds"], "bounds.job.wall_seconds", 604800),
            "max_agent_attempts": _integer(job["max_agent_attempts"], "bounds.job.max_agent_attempts"),
            "max_model_calls": _integer(job["max_model_calls"], "bounds.job.max_model_calls"),
            "max_check_runs": _integer(job["max_check_runs"], "bounds.job.max_check_runs"),
            "max_replans": _integer(job["max_replans"], "bounds.job.max_replans"),
            "max_tokens": _integer(job["max_tokens"], "bounds.job.max_tokens", 1_000_000_000),
        },
        "agent": {
            "timeout_seconds": _integer(agent["timeout_seconds"], "bounds.agent.timeout_seconds", 86400),
            "max_attempts": _integer(agent["max_attempts"], "bounds.agent.max_attempts", 20),
            "max_model_calls": _integer(agent["max_model_calls"], "bounds.agent.max_model_calls"),
            "max_tokens": _integer(agent["max_tokens"], "bounds.agent.max_tokens", 1_000_000_000),
        },
        "check": {
            "timeout_seconds": _integer(check["timeout_seconds"], "bounds.check.timeout_seconds", 3600),
            "max_attempts": _integer(check["max_attempts"], "bounds.check.max_attempts", 20),
            "output_limit_bytes": _integer(check["output_limit_bytes"], "bounds.check.output_limit_bytes", 16 * 1024 * 1024),
        },
    }
    if (result["agent"]["timeout_seconds"] > result["job"]["wall_seconds"]
            or result["check"]["timeout_seconds"] > result["job"]["wall_seconds"]
            or result["agent"]["max_attempts"] > result["job"]["max_agent_attempts"]
            or result["check"]["max_attempts"] > result["job"]["max_check_runs"]
            or result["agent"]["max_model_calls"] > result["job"]["max_model_calls"]
            or result["agent"]["max_tokens"] > result["job"]["max_tokens"]):
        _fail("INCONSISTENT_BOUNDS", "envelope.bounds", "Per-agent/check bounds must fit the job bounds.")
    return result


def validate_envelope(value: object, *, intent: IntentBaseline) -> ExecutionEnvelope:
    """Bind a proposal to a structurally valid intent; no approval or clock/I/O checks."""
    record = _object(value, {
        "schema_version", "id", "revision", "intent", "environment", "profile", "workspace_roots",
        "data_roots", "tools", "effects", "routes", "bounds", "unknown_usage", "expires_at", "revocation",
    }, "envelope")
    if record["schema_version"] != ENVELOPE_VERSION:
        _fail("UNSUPPORTED_SCHEMA", "envelope.schema_version", "Unsupported envelope version.")
    baseline = _intent(intent)
    binding = _object(record["intent"], {"id", "sha256"}, "envelope.intent")
    intent_ref: IntentBinding = {"id": _identifier(binding["id"], "envelope.intent.id"),
                                 "sha256": _sha(binding["sha256"], "envelope.intent.sha256")}
    if intent_ref["id"] != baseline["id"] or intent_ref["sha256"] != record_digest(baseline):
        _fail("INTENT_MISMATCH", "envelope.intent", "Intent ID/digest does not match the supplied baseline.")
    workspace = [_root(item, "envelope.workspace_roots")
                 for item in _list(record["workspace_roots"], "envelope.workspace_roots", minimum=1, maximum=32)]
    data = [_root(item, "envelope.data_roots")
            for item in _list(record["data_roots"], "envelope.data_roots", maximum=32)]
    _unique([root["id"] for root in workspace + data], "envelope.roots")
    aliases = [(root["flavor"], root["path"].casefold() if root["flavor"] == "windows" else root["path"])
               for root in workspace + data]
    if len(aliases) != len(set(aliases)):
        _fail("UNSAFE_PATH", "envelope.roots", "Root aliases are forbidden.")
    routes = _object(record["routes"], {"host", "provider"}, "envelope.routes")
    revocation = _object(record["revocation"], {"revoked_at", "reason"}, "envelope.revocation")
    revoked_at, reason = revocation["revoked_at"], revocation["reason"]
    if (revoked_at is None) != (reason is None):
        _fail("INVALID_REVOCATION", "envelope.revocation", "Revocation needs both timestamp and reason, or neither.")
    result: ExecutionEnvelope = {
        "schema_version": ENVELOPE_VERSION,
        "id": _identifier(record["id"], "envelope.id"),
        "revision": _integer(record["revision"], "envelope.revision"),
        "intent": intent_ref,
        "environment": _enum(record["environment"], ("LOCAL_DEVELOPMENT", "CORP", "ACRO"), "envelope.environment"),
        "profile": _reference(record["profile"], "envelope.profile"),
        "workspace_roots": workspace,
        "data_roots": data,
        "tools": _strings(record["tools"], "envelope.tools", identifiers=True),
        "effects": _strings(record["effects"], "envelope.effects", identifiers=True),
        "routes": {"host": _reference(routes["host"], "envelope.routes.host"),
                   "provider": _reference(routes["provider"], "envelope.routes.provider")},
        "bounds": _bounds(record["bounds"]),
        "unknown_usage": _enum(record["unknown_usage"], ("stop", "reserve_maximum"), "envelope.unknown_usage"),
        "expires_at": _timestamp(record["expires_at"], "envelope.expires_at"),
        "revocation": {
            "revoked_at": None if revoked_at is None else _timestamp(revoked_at, "envelope.revocation.revoked_at"),
            "reason": None if reason is None else _text(reason, "envelope.revocation.reason"),
        },
    }
    canonical_json(result)
    return result
