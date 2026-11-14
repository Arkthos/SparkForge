"""Fictional reference candidate, not an actual SPARK interface."""


def route(request, dispatch):
    if type(request) is not dict or not {"route", "payload"} <= set(request) <= {"route", "payload", "audit_only"}:
        raise ValueError("invalid request")
    name, payload = request["route"], request["payload"]
    audit_only = request.get("audit_only", False)
    if type(name) is not str or name not in ("read", "write"):
        raise ValueError("invalid request")
    if type(payload) is not str or not payload.strip():
        raise ValueError("invalid request")
    if type(audit_only) is not bool:
        raise ValueError("invalid request")
    if audit_only:
        return {"route": name, "payload": payload, "audit_only": True}
    return {"route": name, "result": dispatch(name, payload)}
