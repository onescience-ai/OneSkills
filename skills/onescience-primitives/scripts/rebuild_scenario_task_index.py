#!/usr/bin/env python3
"""Regenerate one scenario lineage from metadata; preserve unrelated entries."""
import argparse
import copy
import json
from pathlib import Path


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def edges(meta, kind):
    prefix = "edge:" + kind + ":"
    return sorted({tag[len(prefix):] for tag in meta.get("tags", [])
                   if tag.startswith(prefix)})


def safe_name(name):
    if not name or Path(name).name != name or name in (".", "..") or "\\" in name:
        raise ValueError("Unsafe card name")
    return name


def regenerate(assets, original, title, scenario_name=None):
    result = copy.deepcopy(original)
    entries = [e for e in result["entries"] if e.get("scenario_title") == title]
    if len(entries) != 1:
        raise ValueError("Expected exactly one existing scenario entry")
    entry = entries[0]
    domain = safe_name(entry["domain"])
    if scenario_name is None:
        matches = []
        for path in sorted((assets / domain / "scenario").glob("*/metadata.json")):
            meta = load(path)
            if "src:scenario_id:" + title in meta.get("tags", []):
                matches.append(path.parent.name)
        if len(matches) != 1:
            raise ValueError("Scenario source tag must resolve uniquely; use --scenario-name")
        scenario_name = matches[0]
    scenario = assets / domain / "scenario" / safe_name(scenario_name)
    smeta = load(scenario / "metadata.json")
    if smeta.get("name") != scenario_name or smeta.get("type") != "scenario":
        raise ValueError("Scenario metadata identity/type mismatch")
    source_tag = "src:scenario_id:" + title
    if source_tag not in smeta.get("tags", []) and title not in smeta.get("description", ""):
        raise ValueError("Selected scenario is not bound to --scenario-title")
    if not (scenario / "knowledge.md").is_file():
        raise ValueError("Scenario knowledge is unavailable")

    def card(category, name):
        directory = assets / domain / category / safe_name(name)
        metadata_file = directory / "metadata.json"
        meta = load(metadata_file) if metadata_file.is_file() else {}
        expected = {"tasks": "task", "workflow": "workflow"}[category]
        if meta and (meta.get("name") != name or meta.get("type") != expected):
            raise ValueError("Metadata identity/type mismatch: " + name)
        exists = bool(meta) and (directory / "knowledge.md").is_file()
        return {"name": name, "path": directory.relative_to(assets).as_posix() + "/",
                "exists": exists}, meta

    resource_types = {
        "datasets": {"dataset"}, "models": {"model"}, "tools": {"tool"},
        "components": {"component", "module", "components"},
        "datapipes": {"datapipe", "datapipes"}, "application": {"application"},
        "databases": {"database", "databases"}, "visualization": {"visualization"},
        "contracts": {"contract", "contracts"}, "output-format": {"output-format"},
    }

    def resource_exists(resource):
        parts = resource.split("/")
        if len(parts) != 2:
            raise ValueError("Unsafe resource edge")
        category, name = (safe_name(part) for part in parts)
        directory = assets / domain / category / name
        metadata_file = directory / "metadata.json"
        if not metadata_file.is_file():
            return False
        meta = load(metadata_file)
        if meta.get("name") != name or meta.get("type") not in resource_types.get(category, set()):
            return False
        four = all((directory / file).is_file()
                   for file in ("spec.md", "usage.md", "workflow_planning.md"))
        # Existing narrative resources retain their established two-file interface.
        return four or (directory / "knowledge.md").is_file()

    workflows = []
    pending = set(edges(smeta, "task"))
    for name in edges(smeta, "workflow"):
        item, meta = card("workflow", name)
        item["tasks"] = edges(meta, "task")
        pending.update(item["tasks"])
        workflows.append(item)
    resolved = {}
    while pending:
        name = min(pending)
        pending.remove(name)
        if name in resolved:
            continue
        item, meta = card("tasks", name)
        resources = edges(meta, "resource")
        item.update(resources=resources,
                    dangling_resources=[resource for resource in resources
                                        if not resource_exists(resource)])
        resolved[name] = item
        pending.update(set(edges(meta, "instance")) - resolved.keys())
    relative = scenario.relative_to(assets).as_posix() + "/"
    entry["entry_points"]["graph_scenario"] = relative
    entry["lineages"]["graph"] = {
        "scenario_card": relative, "workflows": workflows,
        "tasks": [resolved[name] for name in sorted(resolved)]}
    if result["entry_count"] != len(result["entries"]):
        raise ValueError("Index entry_count mismatch")
    # Preserve generated_at/how_to_use, legacy entry points and every other scenario.
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--assets", required=True, type=Path)
    parser.add_argument("--index", required=True, type=Path)
    parser.add_argument("--scenario-title", required=True)
    parser.add_argument("--scenario-name", help="Explicit scenario card bound to the title")
    parser.add_argument("--stdout", action="store_true", help="Print only; never write the index")
    args = parser.parse_args()
    result = regenerate(args.assets, load(args.index), args.scenario_title, args.scenario_name)
    text = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.stdout:
        print(text, end="")
    else:
        args.index.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    main()
