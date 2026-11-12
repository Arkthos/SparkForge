"""Run repository regressions and validate the actual local or CI change boundary."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SHA = re.compile(r"[0-9a-f]{40}")


def ci_base(event: object, event_name: str) -> str:
    """Use the push boundary or PR base; reject missing/unknown event payloads."""
    if not isinstance(event, dict):
        raise ValueError("CI event must be an object")
    if event_name == "pull_request":
        pull = event.get("pull_request")
        base = pull.get("base") if isinstance(pull, dict) else None
        value = base.get("sha") if isinstance(base, dict) else None
    elif event_name == "push":
        value = event.get("before")
    elif event_name == "workflow_dispatch":
        return "HEAD~"
    else:
        raise ValueError(f"Unsupported CI event: {event_name}")
    if not isinstance(value, str) or SHA.fullmatch(value) is None or value == "0" * 40:
        raise ValueError("CI change boundary is missing or not a non-root commit SHA")
    return value


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ci", action="store_true", help="Read the actual GitHub event base")
    parser.add_argument("--base", default="HEAD", help="Local pre-commit base; use HEAD~ after commit")
    args = parser.parse_args(argv)
    try:
        base = args.base
        if args.ci:
            event_path = os.environ.get("GITHUB_EVENT_PATH")
            if not event_path:
                raise ValueError("GITHUB_EVENT_PATH is required for CI validation")
            event = json.loads(Path(event_path).read_text(encoding="utf-8"))
            base = ci_base(event, os.environ.get("GITHUB_EVENT_NAME", ""))
        environment = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
        dependencies = ROOT / "research_tools/.validation-deps"
        environment["PYTHONPATH"] = os.pathsep.join(
            str(path) for path in (dependencies, ROOT)
        )
        commands = [
            [sys.executable, "-B", "-m", "unittest", "discover", "-s", "tests"],
            [sys.executable, "-B", "scripts/validate_plan.py", "--base", base],
            ["git", "diff", "--check", base, "--"],
        ]
        outcomes = []
        for command in commands:
            result = subprocess.run(command, cwd=ROOT, env=environment, check=False)
            outcomes.append({"command": command, "exit_code": result.returncode})
        print(json.dumps({"scope": "repository_checks_not_live_acceptance", "base": base,
                          "checks": outcomes}, indent=2))
        return 1 if any(check["exit_code"] for check in outcomes) else 0
    except (OSError, ValueError) as error:
        print(json.dumps({"result": "FAIL", "reason": str(error)}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
