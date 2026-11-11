"""Check proposed host records only; never qualify a host or authorize execution."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


SCHEMA_VERSION = "sparkforge-host-qualification.v1"
RECORD_FIELDS = (
    "schema_version", "scope_type", "environment_id", "record_revision",
    "selection", "capabilities",
)
CLIENT_FIELDS = (
    "product", "distribution", "launcher", "build", "profile_id",
    "profile_revision", "config_revision", "os", "architecture",
)
BINDING_FIELDS = ("environment_id", "record_revision", "capability_id", "client")
EVIDENCE_CLASSES = (
    "DOCUMENTATION_CLAIM", "PINNED_SOURCE_OBSERVATION",
    "SYNTHETIC_RESULT", "LIVE_HOST_RESULT",
)
STATUS_EVIDENCE = {
    "DOCUMENTED": ("DOCUMENTATION_CLAIM", "PINNED_SOURCE_OBSERVATION"),
    "SYNTHETIC_ONLY": ("SYNTHETIC_RESULT",),
    "OBSERVED": ("LIVE_HOST_RESULT",),
    "UNSUPPORTED": (
        "DOCUMENTATION_CLAIM", "PINNED_SOURCE_OBSERVATION", "LIVE_HOST_RESULT",
    ),
}


def _report(errors: list[str], blockers: list[str] | None = None) -> dict:
    return {
        "scope": "record_consistency_only",
        "valid": not errors,
        "errors": errors,
        "blockers": [
            "RECORD_ORIGIN_NOT_AUTHENTICATED",
            "HOST_QUALIFICATION_NOT_ESTABLISHED",
            "EXECUTION_AUTHORIZATION_NOT_ESTABLISHED",
            *(["INPUT_INVALID"] if errors else []),
            *(blockers if blockers is not None else []),
        ],
        "host_qualified": False,
        "execution_authorized": False,
    }


def _object(
    value: object, fields: tuple[str, ...], path: str, errors: list[str],
) -> dict | None:
    if type(value) is not dict:
        errors.append(f"{path}: expected an object.")
        return None
    missing = [field for field in fields if field not in value]
    unknown = any(field not in fields for field in value)
    if missing:
        errors.append(f"{path}: missing fields: {', '.join(missing)}.")
    if unknown:
        errors.append(f"{path}: unexpected fields; this schema is closed.")
    return None if missing or unknown else value


def _text(value: object, path: str, errors: list[str]) -> bool:
    if type(value) is not str or not value or value != value.strip():
        errors.append(f"{path}: expected a nonempty string without surrounding whitespace.")
        return False
    return True


def _choice(
    value: object, choices: tuple[str, ...], path: str, errors: list[str],
) -> bool:
    if type(value) is not str or value not in choices:
        errors.append(f"{path}: expected one of {', '.join(choices)}.")
        return False
    return True


def _client(value: object, path: str, errors: list[str]) -> bool:
    client = _object(value, CLIENT_FIELDS, path, errors)
    if client is None:
        return False
    start = len(errors)
    for field in CLIENT_FIELDS:
        _text(client[field], f"{path}.{field}", errors)
    return len(errors) == start


def validate_record(data: object) -> dict:
    """Validate a JSON-shaped record without mutating it or resolving any reference."""
    errors: list[str] = []
    blockers: list[str] = []
    record = _object(data, RECORD_FIELDS, "record", errors)
    if record is None:
        return _report(errors)

    _choice(record["schema_version"], (SCHEMA_VERSION,), "record.schema_version", errors)
    _choice(record["scope_type"], ("ENVIRONMENT",), "record.scope_type", errors)
    for field in ("environment_id", "record_revision"):
        _text(record[field], f"record.{field}", errors)

    selection = _object(
        record["selection"], ("status", "reason", "client"), "record.selection", errors,
    )
    selection_status = None
    client = None
    client_valid = False
    if selection is not None:
        selection_status = selection["status"]
        client = selection["client"]
        _text(selection["reason"], "record.selection.reason", errors)
        if _choice(
            selection_status, ("UNSELECTED", "SELECTED"), "record.selection.status", errors,
        ):
            if selection_status == "UNSELECTED":
                blockers.append("CLIENT_UNSELECTED")
                if client is not None:
                    errors.append("record.selection.client: UNSELECTED requires null.")
                else:
                    client_valid = True
            else:
                client_valid = _client(client, "record.selection.client", errors)

    capabilities = record["capabilities"]
    if type(capabilities) is not list:
        errors.append("record.capabilities: expected an array.")
        return _report(errors, blockers)
    if not capabilities:
        blockers.append("CAPABILITY_INVENTORY_NOT_ASSESSED")

    identifiers: set[str] = set()
    sources: dict[str, tuple[str, str]] = {}
    for index, value in enumerate(capabilities):
        path = f"record.capabilities[{index}]"
        capability = _object(value, ("id", "status", "reason", "evidence"), path, errors)
        if capability is None:
            continue
        if _text(capability["id"], f"{path}.id", errors):
            if capability["id"] in identifiers:
                errors.append(f"{path}.id: duplicate capability identifier.")
            identifiers.add(capability["id"])
        _text(capability["reason"], f"{path}.reason", errors)
        status = capability["status"]
        if not _choice(status, ("NOT_ASSESSED", *STATUS_EVIDENCE), f"{path}.status", errors):
            continue
        if status != "OBSERVED":
            blockers.append(f"{path}: {status}; dependent host use is not qualified.")
        if status == "NOT_ASSESSED":
            if capability["evidence"] is not None:
                errors.append(f"{path}.evidence: NOT_ASSESSED requires null.")
            continue

        evidence_path = f"{path}.evidence"
        evidence = _object(
            capability["evidence"], ("class", "reference", "revision", "binding"),
            evidence_path, errors,
        )
        if evidence is None:
            continue
        class_valid = _choice(
            evidence["class"], EVIDENCE_CLASSES, f"{evidence_path}.class", errors,
        )
        reference_valid = _text(evidence["reference"], f"{evidence_path}.reference", errors)
        revision_valid = _text(evidence["revision"], f"{evidence_path}.revision", errors)
        if class_valid:
            if evidence["class"] not in STATUS_EVIDENCE[status]:
                errors.append(f"{evidence_path}.class: incompatible with capability status.")
            if evidence["class"] == "LIVE_HOST_RESULT" and selection_status != "SELECTED":
                errors.append(f"{evidence_path}.class: LIVE_HOST_RESULT requires a selected client.")
        if class_valid and reference_valid and revision_valid:
            source = (evidence["revision"], evidence["class"])
            prior = sources.get(evidence["reference"])
            if prior is not None and prior != source:
                errors.append(f"{evidence_path}: conflicting revision or class for one reference.")
            else:
                sources[evidence["reference"]] = source

        binding_path = f"{evidence_path}.binding"
        binding = _object(evidence["binding"], BINDING_FIELDS, binding_path, errors)
        if binding is None:
            continue
        expected = {
            "environment_id": record["environment_id"],
            "record_revision": record["record_revision"],
            "capability_id": capability["id"],
        }
        for field, expected_value in expected.items():
            if _text(binding[field], f"{binding_path}.{field}", errors):
                if binding[field] != expected_value:
                    errors.append(f"{binding_path}.{field}: stale or foreign binding; must match record.")
        binding_client_valid = binding["client"] is None or _client(
            binding["client"], f"{binding_path}.client", errors,
        )
        if client_valid and binding_client_valid and binding["client"] != client:
            errors.append(f"{binding_path}.client: stale or foreign binding; must match selected client.")

    return _report(errors, blockers)


class _InputError(ValueError):
    pass


class _Parser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        raise _InputError("arguments: expected one record path; use --help for usage.")


def _unique_object(pairs: list[tuple[str, object]]) -> dict:
    result: dict = {}
    for key, value in pairs:
        if key in result:
            raise _InputError("record: duplicate JSON object key.")
        result[key] = value
    return result


def _reject_constant(value: str) -> None:
    raise _InputError("record: non-finite numeric literals are not valid JSON.")


def main(argv: list[str] | None = None) -> int:
    parser = _Parser(description=__doc__)
    parser.add_argument("record", help="UTF-8 JSON record to check; references remain inert")
    try:
        arguments = parser.parse_args(argv)
    except _InputError as error:
        report = _report([str(error)])
    else:
        try:
            text = Path(arguments.record).read_text(encoding="utf-8")
        except (OSError, UnicodeError) as error:
            report = _report([f"record: read failed ({type(error).__name__})."])
        else:
            try:
                data = json.loads(
                    text, object_pairs_hook=_unique_object, parse_constant=_reject_constant,
                )
            except _InputError as error:
                report = _report([str(error)])
            except json.JSONDecodeError as error:
                report = _report([
                    f"record: invalid JSON at line {error.lineno}, column {error.colno}.",
                ])
            except (ValueError, RecursionError):
                report = _report(["record: JSON exceeds parser limits."])
            else:
                report = validate_record(data)
    print(json.dumps(report, indent=2, allow_nan=False))
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
