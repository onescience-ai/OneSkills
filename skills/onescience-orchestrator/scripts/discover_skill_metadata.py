#!/usr/bin/env python3
"""Read installed SKILL.md frontmatter and emit routing metadata as JSON.

Requires PyYAML (see requirements.txt). Never loads skill bodies or assets.
Exit status: 0 = complete valid discovery, 1 = discovery error.
Emit all selected metadata in one compact JSON response by default; never paginate.
"""

import argparse
import json
import sys
from pathlib import Path

SKILL_TYPES = ("resource", "expert", "executor", "orchestrator")
CAPABILITY_FIELDS = (
    "owns", "not_owns", "inputs", "outputs", "downstream", "prereq",
    "intent_aspects", "operation_types", "artifact_types", "domains",
    "trigger_keywords",
)
MAX_FRONTMATTER_BYTES = 256 * 1024


def yaml_loader():
    import yaml

    class UniqueSafeLoader(yaml.SafeLoader):
        pass

    def unique_mapping(loader, node, deep=False):
        result = {}
        for key_node, value_node in node.value:
            key = loader.construct_object(key_node, deep=deep)
            if key in result:
                raise ValueError("duplicate YAML key: {!r}".format(key))
            result[key] = loader.construct_object(value_node, deep=deep)
        return result

    UniqueSafeLoader.add_constructor(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, unique_mapping
    )
    return yaml, UniqueSafeLoader


def read_frontmatter(path, yaml, loader):
    # Stop at the closing delimiter: even a huge body is never read/parsed.
    with path.open("rb") as stream:
        first = stream.readline(MAX_FRONTMATTER_BYTES + 1)
        if first.decode("utf-8-sig").strip() != "---":
            raise ValueError("missing opening frontmatter delimiter")
        lines = []
        size = len(first)
        while size <= MAX_FRONTMATTER_BYTES:
            line = stream.readline(MAX_FRONTMATTER_BYTES - size + 1)
            if not line:
                raise ValueError("missing closing frontmatter delimiter")
            size += len(line)
            if size > MAX_FRONTMATTER_BYTES:
                break
            decoded = line.decode("utf-8")
            if decoded.strip() in ("---", "..."):
                data = yaml.load("".join(lines), Loader=loader)
                if not isinstance(data, dict):
                    raise ValueError("frontmatter must be a mapping")
                return data
            lines.append(decoded)
    raise ValueError("frontmatter exceeds 256 KiB")


def validate_metadata(data):
    for field in ("name", "description", "type"):
        if not isinstance(data.get(field), str) or not data[field].strip():
            raise ValueError("{} must be a nonempty string".format(field))
    if data["type"] not in SKILL_TYPES:
        raise ValueError("unsupported type: {!r}".format(data["type"]))
    capabilities = data.get("capabilities")
    if not isinstance(capabilities, dict):
        raise ValueError("capabilities must be a mapping")
    for field in CAPABILITY_FIELDS:
        value = capabilities.get(field)
        if not isinstance(value, list) or any(
            not isinstance(item, str) or not item.strip() for item in value
        ):
            raise ValueError("capabilities.{} must be a list of strings".format(field))
    metadata = {key: data[key] for key in ("name", "description", "type", "capabilities")}
    json.dumps(metadata, allow_nan=False)
    return metadata


def discover(roots, script_path, selected_type=None):
    result = {
        "metadata_source": "skill_frontmatter_script",
        "script_path": str(script_path),
        "skills_roots": [],
        "query_types": [selected_type] if selected_type is not None else list(SKILL_TYPES),
        "skills": [],
        "ignored_skills": [],
        "errors": [],
        "inventories": {},
        "inventory_complete": False,
    }
    try:
        yaml, loader = yaml_loader()
    except ImportError:
        result["errors"].append({
            "reason": "PyYAML is required; use an environment with PyYAML or install requirements.txt"
        })
        return result

    known = {kind: set() for kind in SKILL_TYPES}
    seen_files = set()
    candidates = []
    for root in roots:
        root = root.expanduser().resolve()
        if str(root) in result["skills_roots"]:
            continue
        result["skills_roots"].append(str(root))
        try:
            # Only immediate skill directories; never recurse into assets/references.
            children = sorted(root.iterdir())
        except OSError as exc:
            result["errors"].append({"path": str(root), "reason": str(exc)})
            continue
        for child in children:
            if child.name.startswith("."):
                continue
            path = child / "SKILL.md"
            try:
                if not child.is_dir():
                    continue
                if not path.exists():
                    if child.name.startswith("onescience-") or child.name == "scnet-chat":
                        raise ValueError("missing SKILL.md in OneScience skill directory")
                    continue
                canonical = path.resolve()
                if canonical in seen_files:
                    continue
                seen_files.add(canonical)
                data = read_frontmatter(path, yaml, loader)
                kind = data.get("type")
                name = data.get("name")
                if isinstance(kind, str) and kind in known:
                    known[kind].add(name if isinstance(name, str) and name.strip() else child.name)
                # Ordinary third-party skills need not implement the OneScience contract.
                if ("type" not in data and "capabilities" not in data
                        and not child.name.startswith("onescience-") and child.name != "scnet-chat"):
                    result["ignored_skills"].append(str(path))
                    continue
                metadata = validate_metadata(data)
                metadata["skill_file"] = str(path)
                candidates.append(metadata)
            except (OSError, ValueError, TypeError, yaml.YAMLError) as exc:
                result["errors"].append({"path": str(path), "reason": str(exc)})

    by_name = {}
    for item in candidates:
        by_name.setdefault(item["name"], []).append(item)
    valid = []
    for name, items in sorted(by_name.items()):
        if len(items) > 1:
            result["errors"].append({
                "name": name, "paths": [item["skill_file"] for item in items],
                "reason": "duplicate skill name across different files; specify unambiguous roots",
            })
        else:
            valid.extend(items)
    if not seen_files:
        result["errors"].append({"reason": "no SKILL.md files found in the supplied roots"})

    for kind in SKILL_TYPES:
        read = {item["name"] for item in valid if item["type"] == kind}
        result["inventories"][kind] = {
            "all_{}_skills".format(kind): sorted(known[kind]),
            "read_{}_skills".format(kind): sorted(read),
            "missing_{}_skills".format(kind): sorted(known[kind] - read),
            "{}_inventory_complete".format(kind): not result["errors"] and known[kind] == read,
        }
    result["skills"] = [item for item in valid if selected_type is None or item["type"] == selected_type]
    result["inventory_complete"] = not result["errors"]
    return result


def encode_result(result, compact=True):
    options = {"ensure_ascii": False, "allow_nan": False}
    options.update({"separators": (",", ":")} if compact else {"indent": 2})
    return json.dumps(result, **options) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--skills-root", type=Path, action="append",
        help="Parent of installed skill directories; repeat for multiple roots. "
             "Defaults to this installed orchestrator's sibling skills directory.",
    )
    parser.add_argument(
        "--type", choices=SKILL_TYPES,
        help="Return all metadata for this type in one response; default: all types. "
             "Validation remains global.",
    )
    formatting = parser.add_mutually_exclusive_group()
    formatting.add_argument("--compact", dest="compact", action="store_true",
                            help="Emit compact JSON without omitting fields (default).")
    formatting.add_argument("--pretty", dest="compact", action="store_false",
                            help="Indent the complete JSON for human inspection.")
    parser.set_defaults(compact=True)
    args = parser.parse_args()
    # Keep the installation path before resolving roots, including symlinked skills.
    script_path = Path(__file__).absolute()
    roots = args.skills_root if args.skills_root is not None else [script_path.parents[2]]
    result = discover(roots, script_path, args.type)
    result["skill_count"] = len(result["skills"])
    # Keep the completion marker at the end of the full document.
    result["output_complete"] = result["inventory_complete"]
    sys.stdout.write(encode_result(result, args.compact))
    return 0 if result["inventory_complete"] else 1


if __name__ == "__main__":
    sys.exit(main())
