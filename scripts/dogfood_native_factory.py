"""Run SparkForge's own frozen engineering checks; never fabricate human acceptance."""

from __future__ import annotations

import argparse
import importlib.util
import json
import sqlite3
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_factory(root: Path):
    source = root / "plugins" / "sparkforge" / "scripts" / "factory.py"
    specification = importlib.util.spec_from_file_location("sparkforge_dogfood_core", source)
    if specification is None or specification.loader is None:
        raise RuntimeError("The native factory core is unavailable.")
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


def run_dogfood(root: Path, job_dir: Path, *, confirm_engineering_test: bool = False) -> dict:
    if not confirm_engineering_test:
        raise ValueError("Confirm this synthetic-decision engineering experiment before creating state or running checks.")
    core = load_factory(root)
    spec = core.validate_spec(core.load_json(root / "specs" / "native-factory-selfcheck.json"))
    if spec["id"] != "SFS-001-selfcheck" or spec["environment"] != "LOCAL_DEVELOPMENT":
        raise ValueError("Only the named LOCAL_DEVELOPMENT self-check spec is accepted by this experiment.")
    initial = core.init_job(spec, root.resolve(), job_dir)
    core.decide(job_dir, initial["spec_sha"], "accept", "synthetic-engineering-operator")
    results = []
    for check in spec["checks"]:
        result = core.run_check(job_dir, check["id"], confirm_run=True)
        observation = result["check"]
        results.append({
            key: observation[key] for key in (
                "run_id", "check_id", "spec_sha", "candidate_sha", "outcome",
                "reason", "exit_code", "output_sha256", "output_truncated",
            ) if key in observation
        })
        if observation["outcome"] != "PASS":
            break
    status = core.job_status(job_dir)
    successful = len(results) == len(spec["checks"]) and all(result["outcome"] == "PASS" for result in results)
    return {
        "scope": "engineering_dogfood_with_synthetic_decision",
        "result": "CHECKS_PASSED_REVIEW_PENDING" if successful and status["status"] == "REVIEW_PENDING" else "NOT_PASSED",
        "job_id": status["job_id"], "spec_sha": status["spec_sha"],
        "candidate_sha": status["candidate_sha"], "job_status": status["status"],
        "checks": results,
        "approval_is_synthetic": True, "reviewer_decision_fabricated": False,
        "human_acceptance": "NOT_ASSESSED", "native_model_workflow_executed": False,
        "host_security_qualified": False, "publication_authorized": False,
        "limits": [
            "The factory engine executed its own accepted check commands on actual controlled bytes.",
            "The operator decision is an explicit test fixture, not user approval of an end-user task.",
            "No review is auto-approved by this experiment; the candidate remains pending independent review.",
            "The coding session produced the implementation; this is not autonomous self-hosting or a live provider trial.",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--job-dir", type=Path, required=True, help="New explicit directory outside the candidate repository.")
    parser.add_argument("--confirm-engineering-test", action="store_true")
    args = parser.parse_args(argv)
    try:
        report = run_dogfood(ROOT, args.job_dir, confirm_engineering_test=args.confirm_engineering_test)
    except (ValueError, OSError, sqlite3.Error, RuntimeError) as error:
        code = getattr(error, "code", type(error).__name__)
        report = {
            "scope": "engineering_dogfood_with_synthetic_decision", "result": "BLOCKED",
            "error": {"code": code, "message": str(error) if isinstance(error, ValueError) else "The local experiment could not complete."},
            "human_acceptance": "NOT_ASSESSED", "publication_authorized": False,
        }
    print(json.dumps(report, indent=2, allow_nan=False))
    return 0 if report["result"] == "CHECKS_PASSED_REVIEW_PENDING" else 1


if __name__ == "__main__":
    raise SystemExit(main())
