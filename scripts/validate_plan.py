"""Validate planning records, not the SparkForge product or human authority."""

from __future__ import annotations

import argparse
import csv
import json
import re
import subprocess
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
LIVING = {
    "docs/PROJECT_STATUS.md",
    "docs/IMPLEMENTATION_BACKLOG.csv",
    "docs/ROADMAP.md",
    "docs/VALIDATION_HISTORY.md",
}
REQUIRED = (
    "README.md",
    "AGENTS.md",
    "docs/PRODUCT_REQUIREMENTS.md",
    "docs/IMPLEMENTATION_PLAN.md",
    "docs/RESEARCH_PROVENANCE.md",
    "docs/PROJECT_STATUS.md",
    "docs/IMPLEMENTATION_BACKLOG.csv",
    "docs/ROADMAP.md",
    "docs/VALIDATION_HISTORY.md",
    "docs/design/ARCHITECTURE.md",
    "docs/design/CONTRACTS.md",
    "docs/design/DECISIONS.md",
    "docs/engineering/TEST_STRATEGY.md",
    "docs/engineering/ACCEPTANCE_MATRIX.csv",
    "docs/engineering/DEVELOPMENT_OPERATING_MODEL.md",
    "docs/delivery/WIKI_AND_SUBMISSION.md",
    "docs/research/SELF_IMPROVEMENT.md",
    "docs/research/self-improvement-sources.json",
    "scripts/validate_plan.py",
    "tests/test_validate_plan.py",
)
BACKLOG_COLUMNS = (
    "id", "title", "milestone", "status", "depends_on", "requirements",
    "owner", "deliverables", "acceptance", "validation", "authorization",
)
TEST_COLUMNS = (
    "test_id", "requirements", "level", "scenario", "expected_outcome",
    "evidence", "gate", "owner",
)
STATES = {"not_started", "in_progress", "done", "blocked", "awaiting_approval", "deferred"}
LEVELS = {"documentation", "unit", "contract", "integration", "behavioral", "live_host", "manual_release"}
GATES = {f"P{i}" for i in range(9)}
REQ_PATTERN = r"(?:SF|NFR)-\d{2}"
CYCLE_DIRECTORY = "docs/engineering/cycles"


@dataclass
class Report:
    errors: list[str] = field(default_factory=list)
    counts: dict[str, int] = field(default_factory=dict)

    def require(self, condition: bool, message: str) -> None:
        if not condition:
            self.errors.append(message)


def read_text(path: Path, report: Report) -> str:
    try:
        return path.read_text(encoding="utf-8-sig")
    except (OSError, UnicodeError) as error:
        report.errors.append(f"Cannot read {path.name}: {error}")
        return ""


def prose(text: str) -> str:
    return re.sub(r"(?ms)^```[^\n]*\n.*?^```[ \t]*$", "", text)


def anchors(text: str) -> set[str]:
    found = set(re.findall(r'<a\s+(?:id|name)=["\']([^"\']+)["\']', text))
    for heading in re.findall(r"^#{1,6}\s+(.+?)\s*#*\s*$", prose(text), re.M):
        heading = re.sub(r"<[^>]+>", "", heading)
        slug = re.sub(r"[^\w -]", "", heading.lower()).replace(" ", "-")
        candidate, suffix = slug, 0
        while candidate in found:
            suffix += 1
            candidate = f"{slug}-{suffix}"
        found.add(candidate)
    return found


def check_links(root: Path, pages: dict[Path, str], report: Report) -> None:
    allowed = (root.resolve(), (root.parent / "docs").resolve())
    local_count = 0
    for page, text in pages.items():
        for raw in re.findall(r"\[[^\]\n]*\]\(([^)\n]+)\)", prose(text)):
            destination = raw.strip().strip("<>")
            try:
                target_url = urlsplit(destination)
            except ValueError as error:
                report.errors.append(f"{page.name}: malformed link: {error}")
                continue
            if target_url.scheme in {"http", "https", "mailto"}:
                continue
            if target_url.scheme or target_url.netloc:
                report.errors.append(f"{page.name}: unsupported link {destination}")
                continue
            local_count += 1
            target = (
                page.parent.joinpath(*unquote(target_url.path).replace("\\", "/").split("/"))
                if target_url.path else page
            ).resolve()
            if not any(target.is_relative_to(base) for base in allowed):
                report.errors.append(f"{page.name}: link escapes approved roots: {destination}")
                continue
            if not target.exists():
                report.errors.append(f"{page.name}: missing local link: {destination}")
                continue
            if target_url.fragment:
                if target.suffix.lower() != ".md" or not target.is_file():
                    report.errors.append(f"{page.name}: uncheckable local fragment: {destination}")
                    continue
                target_text = pages.get(target)
                if target_text is None:
                    target_text = read_text(target, report)
                fragment = unquote(target_url.fragment)
                report.require(
                    fragment in anchors(target_text),
                    f"{page.name}: missing anchor: {destination}",
                )
    report.counts["local_links"] = local_count


def read_csv(path: Path, columns: tuple[str, ...], report: Report) -> list[dict[str, str]]:
    try:
        with path.open(encoding="utf-8-sig", newline="") as stream:
            reader = csv.DictReader(stream, strict=True)
            if reader.fieldnames != list(columns):
                report.errors.append(f"{path.name}: unexpected CSV header")
                return []
            raw_rows = list(reader)
    except (OSError, UnicodeError, csv.Error) as error:
        report.errors.append(f"{path.name}: CSV read failed: {error}")
        return []
    rows = []
    for line, row in enumerate(raw_rows, 2):
        if None in row or any(value is None for value in row.values()):
            report.errors.append(f"{path.name}:{line}: wrong column count")
            continue
        for key, value in row.items():
            if key != "depends_on":
                report.require(bool(value.strip()), f"{path.name}:{line}: empty {key}")
        rows.append(row)
    return rows


def values(text: str) -> list[str]:
    return [value.strip() for value in text.split(";") if value.strip()]


def index_rows(
    rows: list[dict[str, str]], key: str, pattern: str, report: Report
) -> dict[str, dict[str, str]]:
    indexed = {}
    for row in rows:
        identifier = row[key]
        report.require(re.fullmatch(pattern, identifier) is not None, f"Invalid ID: {identifier}")
        report.require(identifier not in indexed, f"Duplicate ID: {identifier}")
        indexed[identifier] = row
    return indexed


def continuous(ids: set[str], prefix: str, width: int, report: Report) -> None:
    expected = {f"{prefix}-{number:0{width}d}" for number in range(1, len(ids) + 1)}
    report.require(ids == expected, f"{prefix} identifiers must be unique and contiguous from 1")


def requirement_refs(text: str) -> set[str]:
    return set(re.findall(rf"\b{REQ_PATTERN}\b", text))


def test_refs(text: str, report: Report) -> set[str]:
    found = set(re.findall(r"\bTC-\d{3}\b", text))
    for start, end in re.findall(r"\bTC-(\d{3})\.\.TC-(\d{3})\b", text):
        first, last = int(start), int(end)
        report.require(first <= last, f"Reversed test range TC-{start}..TC-{end}")
        found.update(f"TC-{number:03d}" for number in range(first, last + 1))
    return found


def sections(text: str, prefix: str, report: Report) -> dict[str, str]:
    parts = re.split(rf"^## ({prefix}-\d{{3}}):[^\n]*\n", text, flags=re.M)
    result = {}
    for identifier, body in zip(parts[1::2], parts[2::2]):
        report.require(identifier not in result, f"Duplicate section: {identifier}")
        result[identifier] = body
    continuous(set(result), prefix, 3, report)
    report.require(bool(result), f"No {prefix} sections found")
    return result


def check_dependencies(work: dict[str, dict[str, str]], report: Report) -> None:
    graph = {key: values(row["depends_on"]) for key, row in work.items()}
    for identifier, dependencies in graph.items():
        report.require(len(dependencies) == len(set(dependencies)), f"{identifier}: duplicate dependency")
        for dependency in dependencies:
            report.require(dependency in work, f"{identifier}: unknown dependency {dependency}")
            report.require(dependency != identifier, f"{identifier}: self dependency")
            state = work[identifier]["status"]
            if dependency in work and state in {"in_progress", "awaiting_approval", "done"}:
                report.require(
                    work[dependency]["status"] == "done",
                    f"{identifier}: {state} before prerequisite {dependency}",
                )
    visited, active = set(), []

    def visit(identifier: str) -> None:
        if identifier in active:
            report.errors.append(f"Dependency cycle: {' -> '.join(active + [identifier])}")
            return
        if identifier in visited or identifier not in graph:
            return
        active.append(identifier)
        for dependency in graph[identifier]:
            visit(dependency)
        active.pop()
        visited.add(identifier)

    for identifier in graph:
        visit(identifier)
    pending = list(graph.get("WP-080", []))
    ancestors = set()
    while pending:
        identifier = pending.pop()
        if identifier in ancestors or identifier not in work:
            continue
        ancestors.add(identifier)
        pending.extend(graph[identifier])
    for identifier in ancestors:
        report.require(
            work[identifier]["milestone"] != "P8" and identifier not in {"WP-081", "WP-082"},
            f"Corp local readiness incorrectly depends on deferred transfer/submission {identifier}",
        )


def check_cycle(path: Path, cycle: object, work_ids: set[str], report: Report) -> None:
    if not isinstance(cycle, dict):
        report.errors.append(f"{path.name}: cycle must be an object")
        return
    report.require(
        cycle.get("schema_version") == "sparkforge-engineering-cycle.v1",
        f"{path.name}: unsupported cycle schema",
    )
    match = re.fullmatch(r"ENG-(\d{8})-[a-z0-9]+(?:-[a-z0-9]+)*", path.stem)
    report.require(match is not None and cycle.get("id") == path.stem, f"{path.name}: invalid cycle ID")
    try:
        recorded_date = date.fromisoformat(cycle.get("date", ""))
        report.require(bool(match) and recorded_date.strftime("%Y%m%d") == match[1], f"{path.name}: date mismatch")
    except (ValueError, TypeError):
        report.errors.append(f"{path.name}: invalid cycle date")
    for key in ("workstream", "cycle_type", "objective", "rollback"):
        report.require(isinstance(cycle.get(key), str) and bool(cycle[key].strip()), f"{path.name}: missing {key}")
    for key in ("work_items", "changes", "results", "limitations", "next_steps", "evidence"):
        entries = cycle.get(key)
        valid = isinstance(entries, list) and bool(entries) and all(
            isinstance(entry, str) and bool(entry.strip()) for entry in entries
        )
        report.require(valid, f"{path.name}: invalid {key}")
    items = cycle.get("work_items")
    if isinstance(items, list):
        report.require(all(isinstance(item, str) and item in work_ids for item in items), f"{path.name}: unknown work item")
    report.require(type(cycle.get("public_safe")) is bool, f"{path.name}: public_safe must be boolean")
    status = cycle.get("status")
    report.require(
        isinstance(status, str) and status in {"in_progress", "validated", "blocked", "awaiting_ci"},
        f"{path.name}: invalid status",
    )
    checks = cycle.get("validation")
    if not isinstance(checks, list) or not checks:
        report.errors.append(f"{path.name}: missing validation entries")
        return
    outcomes = []
    for check in checks:
        if not isinstance(check, dict):
            report.errors.append(f"{path.name}: invalid validation entry")
            continue
        for key in ("check", "scope", "reference"):
            report.require(isinstance(check.get(key), str) and bool(check[key].strip()), f"{path.name}: missing validation {key}")
        outcome = check.get("outcome")
        valid = isinstance(outcome, str) and outcome in {"PASS", "FAIL", "PENDING", "NOT_RUN", "NOT_ASSESSED"}
        report.require(valid, f"{path.name}: invalid outcome")
        outcomes.append(outcome if valid else "INVALID")
    if cycle.get("status") == "validated":
        report.require("PASS" in outcomes and not any(value in {"FAIL", "PENDING", "INVALID"} for value in outcomes), f"{path.name}: validated cycle has unresolved checks")


def git_lines(root: Path, *arguments: str) -> list[str]:
    result = subprocess.run(
        ["git", "-C", str(root), *arguments],
        capture_output=True, text=True, encoding="utf-8", errors="replace", check=False,
    )
    if result.returncode:
        raise RuntimeError(f"Git inspection failed: {result.stderr.strip()[:500]}")
    return result.stdout.splitlines()


def check_git(root: Path, base: str, report: Report) -> None:
    try:
        revision = git_lines(root, "rev-parse", "--verify", "--end-of-options", base + "^{commit}")[0]
        original = {
            path for path in git_lines(root, "ls-tree", "-r", "--name-only", revision, "--", CYCLE_DIRECTORY)
            if path.endswith(".json")
        }
        changed = set(git_lines(root, "diff", "--no-ext-diff", "--no-textconv", "--no-renames", "--name-only", revision, "--"))
        changed.update(git_lines(root, "diff", "--cached", "--no-ext-diff", "--no-textconv", "--no-renames", "--name-only", revision, "--"))
        changed.update(git_lines(root, "ls-files", "--others", "--exclude-standard"))
        for path in sorted(original & changed):
            report.errors.append(f"Historical cycle modified/deleted: {path}")
        if changed:
            report.require(LIVING <= changed, f"Change boundary missing living records: {', '.join(sorted(LIVING - changed))}")
            additions = [
                path for path in changed - original
                if path.startswith(CYCLE_DIRECTORY + "/") and path.endswith(".json")
                and (root / path).is_file()
            ]
            report.require(bool(additions), "Change boundary requires a new append-only cycle")
        report.counts["changed_paths_against_base"] = len(changed)
        readme = read_text(root / "README.md", report)
        if "no configured remote" in readme:
            report.require(not git_lines(root, "remote"), "A remote exists despite the local-only README claim")
    except (OSError, RuntimeError, IndexError) as error:
        report.errors.append(str(error))


def validate(root: Path, git_base: str | None = None) -> Report:
    root = root.resolve()
    report = Report()
    for name in REQUIRED:
        report.require((root / name).is_file(), f"Required file missing: {name}")
    paths = [root / "README.md", root / "AGENTS.md", *sorted((root / "docs").rglob("*.md"))]
    pages = {}
    for path in paths:
        if not path.resolve().is_relative_to(root):
            report.errors.append(f"Documentation file escapes repository: {path.name}")
        elif path.is_file():
            pages[path.resolve()] = read_text(path, report)

    def text(name: str) -> str:
        return pages.get((root / name).resolve(), "")

    raw_requirements = re.findall(rf"^\|\s*({REQ_PATTERN})\s*\|", text("docs/PRODUCT_REQUIREMENTS.md"), re.M)
    requirements = set(raw_requirements)
    report.require(bool(requirements) and len(requirements) == len(raw_requirements), "Requirement IDs missing or duplicated")
    for prefix in ("SF", "NFR"):
        identifiers = {value for value in requirements if value.startswith(prefix + "-")}
        report.require(bool(identifiers), f"No {prefix} requirements")
        continuous(identifiers, prefix, 2, report)
    work = index_rows(read_csv(root / "docs/IMPLEMENTATION_BACKLOG.csv", BACKLOG_COLUMNS, report), "id", r"WP-\d{3}", report)
    cases = index_rows(read_csv(root / "docs/engineering/ACCEPTANCE_MATRIX.csv", TEST_COLUMNS, report), "test_id", r"TC-\d{3}", report)
    continuous(set(cases), "TC", 3, report)
    for label, rows in (("Backlog", work), ("Matrix", cases)):
        covered = set()
        for identifier, row in rows.items():
            refs = values(row["requirements"])
            report.require(bool(refs) and len(refs) == len(set(refs)), f"{identifier}: empty/duplicate requirement refs")
            report.require(set(refs) <= requirements, f"{identifier}: unknown requirements {sorted(set(refs) - requirements)}")
            covered.update(refs)
        report.require(requirements <= covered, f"{label} missing requirement coverage: {sorted(requirements - covered)}")
    mapped_tests = set()
    for identifier, row in work.items():
        report.require(row["milestone"] in GATES, f"{identifier}: invalid milestone")
        report.require(row["status"] in STATES, f"{identifier}: invalid work state")
        refs = test_refs(row["validation"], report)
        report.require(bool(refs), f"{identifier}: no acceptance scenario linkage")
        report.require(refs <= set(cases), f"{identifier}: unknown tests {sorted(refs - set(cases))}")
        mapped_tests.update(refs)
    report.require(set(cases) <= mapped_tests, f"Matrix tests have no work package: {sorted(set(cases) - mapped_tests)}")
    for identifier, row in cases.items():
        report.require(row["gate"] in GATES, f"{identifier}: invalid gate")
        report.require(row["level"] in LEVELS, f"{identifier}: invalid level")
    check_dependencies(work, report)

    contracts = sections(text("docs/design/CONTRACTS.md"), "C", report)
    decisions = sections(text("docs/design/DECISIONS.md"), "D", report)
    contract_coverage = set()
    for identifier, body in {**contracts, **decisions}.items():
        header = re.search(r"^\*\*Requirements:\*\*\s*([^\n]+)", body, re.M)
        refs = requirement_refs(header[1]) if header else set()
        report.require(bool(refs), f"{identifier}: missing explicit requirement header")
        report.require(refs <= requirements, f"{identifier}: unknown requirement header")
        if identifier in contracts:
            contract_coverage.update(refs)
            linked = re.search(r"^\*\*Decisions:\*\*\s*([^\n]+)", body, re.M)
            report.require(linked is not None, f"{identifier}: missing decision header")
    report.require(requirements <= contract_coverage, f"Contracts missing requirement coverage: {sorted(requirements - contract_coverage)}")
    known = requirements | set(work) | set(cases) | set(contracts) | set(decisions)
    for page, content in pages.items():
        refs = set(re.findall(r"\b(?:SF-\d{2}|NFR-\d{2}|WP-\d{3}|TC-\d{3}|C-\d{3}|D-\d{3})\b", prose(content)))
        report.require(refs <= known, f"{page.name}: unknown references {sorted(refs - known)}")
    plan_refs = set(re.findall(r"^### (WP-\d{3}):", text("docs/IMPLEMENTATION_PLAN.md"), re.M))
    report.require(plan_refs == set(work), f"Plan work-package sections differ from backlog: {sorted(plan_refs ^ set(work))}")
    gates = set(re.findall(r"^\|\s*(P[0-8])(?:\s|:|\s*\|)", text("docs/ROADMAP.md"), re.M))
    report.require(gates == GATES, "Roadmap must declare P0 through P8")
    count = re.search(r"\*\*(\d+) planned\s+scenarios\*\*", text("docs/engineering/TEST_STRATEGY.md"))
    report.require(count is not None and int(count[1]) == len(cases), "Test strategy scenario count differs from matrix")
    report.require("WP-001" in work and "WP-080" in work, "Missing baseline approval or local-delivery work package")
    if work.get("WP-001", {}).get("status") != "done":
        for identifier, row in work.items():
            if identifier not in {"WP-000", "WP-001"}:
                report.require(row["status"] not in {"done", "in_progress"}, f"{identifier}: execution advanced before baseline approval")
        status = text("docs/PROJECT_STATUS.md")
        report.require("**Product implementation:** not started." in status, "Pending baseline must not claim product implementation")
        report.require("**Local plugin acceptance:** NOT_ASSESSED." in status, "Pending baseline must retain NOT_ASSESSED local acceptance")
        report.require(not (root / "plugins").exists(), "Product package exists before baseline approval")
    check_links(root, pages, report)
    cycles = 0
    for path in sorted((root / "docs").rglob("*.json")):
        if not path.resolve().is_relative_to(root):
            report.errors.append(f"JSON file escapes repository: {path.name}")
            continue
        try:
            data = json.loads(read_text(path, report))
        except json.JSONDecodeError as error:
            report.errors.append(f"{path.name}: invalid JSON: {error}")
            continue
        if path.parent == root / CYCLE_DIRECTORY:
            cycles += 1
            check_cycle(path, data, set(work), report)
    report.require(cycles > 0, "No engineering cycles")
    if git_base is not None:
        check_git(root, git_base, report)
    report.counts.update(
        markdown_files=len(pages), requirements=len(requirements), work_packages=len(work),
        planned_scenarios=len(cases), contracts=len(contracts), decisions=len(decisions), cycles=cycles,
    )
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", default="HEAD", help="Git commit to compare for immutable cycles and living records")
    arguments = parser.parse_args()
    report = validate(ROOT, arguments.base)
    print(json.dumps({
        "result": "FAIL" if report.errors else "PASS",
        "scope": "planning_documentation_and_governance_only",
        "counts": report.counts,
        "errors": report.errors,
        "limits": [
            "Does not run product, host, model, installation or acceptance scenarios.",
            "Does not authenticate decisions, establish semantic correctness or fetch external URLs.",
            "Local links may use the approved sibling docs corpus; these are not portable runtime dependencies.",
        ],
    }, indent=2))
    return 1 if report.errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
