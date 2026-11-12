"""Extract plugin declarations and static structure without importing studied modules."""

import argparse
import ast
import csv
import io
import json
import re
import warnings
from pathlib import PurePosixPath

from .._common import child, root_path, safe_main, write_json, write_text
from .inventory_source import load_inventory, source_bytes


def frontmatter(text):
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, 0
    end = next((index for index in range(1, len(lines)) if lines[index].strip() == "---"), None)
    if end is None:
        raise ValueError("Unclosed frontmatter")
    fields, current = {}, None
    for line in lines[1:end]:
        match = re.match(r"^([\w-]+):\s*(.*)", line)
        if match:
            current, value = match.groups()
            fields[current] = value.strip().strip("\"'")
        elif current and line.strip():
            fields[current] += " " + line.strip()
    return {key: re.sub(r"^[>|][-+]?\s*", "", value).strip() for key, value in fields.items()}, end + 1


def write_csv(root, name, rows, columns):
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=list(rows[0]) if rows else columns)
    writer.writeheader()
    for row in rows:
        writer.writerow({
            key: json.dumps(value, ensure_ascii=True) if isinstance(value, (list, dict)) else value
            for key, value in row.items()
        })
    write_text(root, child(root, "evidence/" + name), output.getvalue())


def catalog(root):
    root = root_path(root)
    inventory, source, entries = load_inventory(root)
    commit = inventory["snapshot"]["commit"]

    def read(relative):
        return source_bytes(source, entries[relative]).decode("utf-8-sig")

    def reference(relative, start=1, end=None):
        count = entries[relative]["line_count"]
        end = count if end is None else end
        return {
            "path": relative, "start": start, "end": end, "commit": commit,
            "url": entries[relative]["source_url"] + f"#L{start}-L{end}",
        }

    marketplace_path = ".github/plugin/marketplace.json"
    marketplace = json.loads(read(marketplace_path))
    registered = {row["name"]: row for row in marketplace["plugins"]}
    if len(registered) != len(marketplace["plugins"]):
        raise ValueError("Duplicate marketplace name")
    owner_rules = []
    for number, line in enumerate(read(".github/CODEOWNERS").splitlines(), 1):
        if line.strip() and not line.lstrip().startswith("#"):
            pattern, *owners = line.split()
            if pattern != "*" and not re.fullmatch(r"/plugins/[\w-]+/", pattern):
                raise ValueError("Ownership extractor needs review for a new pattern")
            owner_rules.append({"pattern": pattern, "owners": owners, "line": number})
    plugins, skills, agents, scripts, queries, checks = [], [], [], [], [], []
    folders = sorted({
        PurePosixPath(path).parts[1] for path in entries
        if path.startswith("plugins/") and len(PurePosixPath(path).parts) > 2
    })
    for name in folders:
        prefix = "plugins/" + name
        manifest_path = prefix + "/plugin.json"
        manifest = json.loads(read(manifest_path))
        agency = json.loads(read(prefix + "/agency.json"))
        if manifest["name"] != name:
            raise ValueError("Package name differs from its folder")
        if name in registered and (
            registered[name]["version"] != manifest["version"]
            or registered[name]["source"] != "./" + prefix
        ):
            raise ValueError("Registry identity/version drift")
        ownership = next(
            (rule for rule in reversed(owner_rules) if rule["pattern"] in ("*", f"/plugins/{name}/")),
            {"pattern": None, "owners": [], "line": None},
        )
        declared = {"skills": [], "agents": []}
        for kind, collection in [("skills", skills), ("agents", agents)]:
            for item in manifest.get(kind, []):
                relative = f"{prefix}/{item.removeprefix('./')}" + ("/SKILL.md" if kind == "skills" else "")
                child(source, relative)
                if relative not in entries:
                    raise ValueError("Missing declared resource")
                declared[kind].append(relative)
                text = read(relative)
                fields, header_end = frontmatter(text)
                collection.append({
                    "plugin": name, "name": fields.get("name", PurePosixPath(relative).stem),
                    "path": relative, "declared_purpose": fields.get("description", ""),
                    "declared_inputs": fields.get("argument-hint", ""),
                    "declared_tools": fields.get("allowed-tools", fields.get("tools", "")),
                    "frontmatter_end": header_end,
                    "headings": [
                        {"line": index, "heading": line.lstrip("# ").strip()}
                        for index, line in enumerate(text.splitlines(), 1) if re.match(r"^#{1,4} ", line)
                    ],
                    "inspection": "declaration_and_headings_extracted", "source": reference(relative),
                })
        plugins.append({
            "name": name, "version": manifest["version"], "marketplace_registered": name in registered,
            "marketplace_version": registered.get(name, {}).get("version"),
            "declared_agency_dependencies": agency.get("dependencies", []),
            "dependency_message": manifest.get("postInstallMessage", registered.get(name, {}).get("postInstallMessage")),
            "declared_engines": agency.get("engines", []), "declared_platforms": agency.get("platforms", []),
            "manifest_hook_reference": manifest.get("hooks"), "ownership": ownership,
            "hook_files": [path for path in entries if path.startswith(prefix + "/") and path.endswith("hooks.json")],
            **declared, "manifest_source": reference(manifest_path),
        })
    for path, entry in sorted(entries.items()):
        if entry["git_type"] != "blob" or entry["materialization"] != "exact_blob_bytes":
            continue
        if path.endswith(".json"):
            try:
                json.loads(read(path))
            except json.JSONDecodeError as error:
                checks.append({"check": "json_parse", "path": path, "status": "FAIL", "line": error.lineno})
            else:
                checks.append({"check": "json_parse", "path": path, "status": "PASS"})
        if path.endswith((".py", ".ps1", ".js")):
            text, definitions = read(path), []
            if path.endswith(".py"):
                try:
                    with warnings.catch_warnings(record=True) as captured:
                        warnings.simplefilter("always", SyntaxWarning)
                        tree = ast.parse(text, filename=path)
                except SyntaxError as error:
                    checks.append({"check": "python_ast_parse", "path": path, "status": "FAIL", "line": error.lineno})
                else:
                    checks.append({
                        "check": "python_ast_parse", "path": path, "status": "PASS",
                        "warnings": [{"line": item.lineno, "category": item.category.__name__} for item in captured],
                    })
                    definitions = [
                        {"name": node.name, "line": node.lineno, "end": node.end_lineno, "kind": type(node).__name__}
                        for node in ast.walk(tree) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
                    ]
            else:
                definitions = [
                    {"name": match.group(1), "line": text[:match.start()].count("\n") + 1}
                    for match in re.finditer(r"(?mi)^\s*(?:export\s+)?(?:async\s+)?function\s+([\w-]+)", text)
                ]
            parts = PurePosixPath(path).parts
            scripts.append({
                "path": path, "plugin": parts[1] if len(parts) > 2 and parts[0] == "plugins" else None,
                "role": "test_or_fixture" if "/tests/" in path else "source_script",
                "line_count": entry["line_count"], "definitions": definitions,
                "source_url": entry["source_url"], "runtime_execution": "NOT_RUN",
            })
        if path.endswith(".kql"):
            parts = PurePosixPath(path).parts
            queries.append({
                "path": path, "plugin": parts[1] if len(parts) > 2 and parts[0] == "plugins" else None,
                "headers": [
                    {"line": number, "text": line} for number, line in enumerate(read(path).splitlines()[:12], 1)
                    if re.match(r"^\s*//\s*(endpoint|database|purpose)\s*:", line, re.I)
                ],
                "line_count": entry["line_count"], "source_url": entry["source_url"],
                "inspection": "path_and_leading_metadata_only", "execution": "NOT_RUN",
            })
    result = {
        "schema_version": 1, "commit": commit, "marketplace_source": reference(marketplace_path),
        "counts": {
            "plugin_directories": len(plugins), "marketplace_entries": len(registered),
            "declared_skills": len(skills), "declared_agents": len(agents),
            "script_files": len(scripts), "kql_files": len(queries),
        },
        "unregistered_skill_files": sorted({p for p in entries if p.endswith("/SKILL.md")} - {r["path"] for r in skills}),
        "unregistered_agent_files": sorted({p for p in entries if p.endswith(".agent.md")} - {r["path"] for r in agents}),
        "plugins": plugins, "skills": skills, "agents": agents, "scripts": scripts, "queries": queries,
    }
    write_json(root, child(root, "evidence/catalog.json"), result)
    write_json(root, child(root, "evidence/static-checks.json"), {
        "commit": commit, "scope": "Parsing only; no studied code imported or executed.", "checks": checks,
    })
    for name, rows in [
        ("skills.csv", skills), ("agents.csv", agents),
        ("executable-surfaces.csv", scripts), ("queries.csv", queries),
    ]:
        write_csv(root, name, rows, ["path"])
    return {
        "status": "FAIL" if any(row["status"] != "PASS" for row in checks) else "CATALOGED",
        "counts": result["counts"], "static_checks": len(checks),
        "static_failures": sum(row["status"] != "PASS" for row in checks), "network_requests": 0,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, help="Selected inventory corpus; outputs go to its evidence directory.")
    return catalog(parser.parse_args(argv).root)


if __name__ == "__main__":
    safe_main(main)
