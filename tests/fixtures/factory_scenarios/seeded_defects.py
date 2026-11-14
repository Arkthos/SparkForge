"""Single-fault candidate mutations; expected behavior lives in the separate oracle."""


MUTATIONS = {
    "audit-dispatches": (
        "    if audit_only:\n", "    if audit_only:\n        dispatch(name, payload)\n", "audit-read",
    ),
    "audit-ignored": (
        "    if audit_only:\n", "    if False:\n", "audit-read",
    ),
    "legacy-output-changed": (
        '"result": dispatch(name, payload)', '"output": dispatch(name, payload)', "legacy-read",
    ),
    "unknown-route-accepted": (
        'name not in ("read", "write")', "False", "unknown-route",
    ),
    "numeric-audit-accepted": (
        "    if type(audit_only) is not bool:\n", "    if False:\n", "numeric-audit-one",
    ),
    "extra-output": (
        '"audit_only": True}', '"audit_only": True, "deployed": False}', "audit-write",
    ),
    "request-mutated": (
        "    if audit_only:\n", '    request["audit_only"] = False\n    if audit_only:\n', "audit-read",
    ),
    "boolean-output-aliased": (
        '"audit_only": True}', '"audit_only": 1}', "audit-write",
    ),
    "default-write-audits": (
        'request.get("audit_only", False)', 'request.get("audit_only", name == "write")', "legacy-write-default",
    ),
    "null-audit-accepted": (
        "if type(audit_only) is not bool:", "if audit_only is not None and type(audit_only) is not bool:", "null-audit",
    ),
    "dispatch-result-discarded": (
        '"result": dispatch(name, payload)', '"result": (dispatch(name, payload), f"{name}:{payload}")[1]', "legacy-read",
    ),
    "normal-read-trims-payload": (
        '"result": dispatch(name, payload)',
        '"result": dispatch(name, payload.strip() if name == "read" else payload)',
        "legacy-read-padded-default",
    ),
}


def mutated_source(source: str, mutation: str) -> str:
    old, new, _case = MUTATIONS[mutation]
    if source.count(old) != 1:
        raise ValueError("Synthetic mutation does not match exactly one reference-candidate span.")
    return source.replace(old, new, 1)
