#!/usr/bin/env python3
"""Build a read-only coverage and migration manifest for source Agent Skills.

The manifest is deliberately evidence-based. It records source structure,
knowledge channels, code-risk signals, target provenance matches, and a
conservative migration recommendation. It never imports, executes, or copies
source code.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import date
from pathlib import Path
from typing import Any, Iterable


CODE_EXTENSIONS = {
    ".cjs",
    ".js",
    ".ipynb",
    ".mjs",
    ".py",
    ".r",
    ".rb",
    ".sh",
    ".sql",
    ".ts",
    ".tsx",
}
TEXT_EXTENSIONS = CODE_EXTENSIONS | {
    ".csv",
    ".json",
    ".md",
    ".rst",
    ".toml",
    ".txt",
    ".yaml",
    ".yml",
}
SKIP_NAMES = {".git", "__pycache__", ".pytest_cache", ".mypy_cache", "node_modules"}

RISK_PATTERNS: dict[str, tuple[str, ...]] = {
    "dynamic_execution": (r"\beval\s*\(", r"\bexec\s*\("),
    "network_access": (
        r"\brequests\b",
        r"\bhttpx\b",
        r"\burllib\b",
        r"\bcurl\b",
        r"\bwget\b",
        r"https?://",
    ),
    "process_execution": (
        r"\bsubprocess\b",
        r"\bos\.system\s*\(",
        r"shell\s*=\s*True",
        r"\bPopen\s*\(",
    ),
    "credential_handling": (
        r"api[_-]?key",
        r"access[_-]?token",
        r"password",
        r"secret",
        r"authorization\s*:",
        r"bearer\s+",
    ),
    "filesystem_mutation": (
        r"shutil\.rmtree",
        r"os\.remove\s*\(",
        r"os\.unlink\s*\(",
        r"rm\s+-rf",
        r"Remove-Item",
    ),
    "absolute_path": (
        r"[A-Za-z]:\\",
        r"(?<![A-Za-z])/(?:home|Users|mnt|tmp|var|opt)/",
    ),
}

INTERFACE_PATTERNS = (
    r"\bargparse\b",
    r"\bclick\b",
    r"\btyper\b",
    r"\bdef\s+main\s*\(",
    r"if\s+__name__\s*==\s*[\"']__main__[\"']",
    r"\binput(?:s)?\b",
    r"\boutput(?:s)?\b",
)

INSTALL_PATTERNS = (
    r"uv\s+(?:pip\s+)?install",
    r"pip\s+install",
    r"conda\s+install",
    r"npm\s+install",
    r"docker\s+run",
)

CONCERN_PATTERNS = {
    "tool": (r"\b(cli|sdk|package|software|command|install|import)\b",),
    "database_or_service": (
        r"\b(database|dataset|api|query|remote|credential|token|service)\b",
    ),
    "workflow": (r"\b(workflow|pipeline|nextflow|snakemake|stage|handoff)\b",),
    "analysis_or_model": (
        r"\b(analysis|model|inference|training|fit|normalization|clustering)\b",
    ),
    "visualization_or_output": (
        r"\b(visualization|plot|figure|report|markdown|mermaid|docx|pdf|pptx)\b",
    ),
}

ALIASES = {
    "database-lookup": ("public_database_lookup",),
    "markdown-mermaid-writing": ("markdown_mermaid",),
    "nextflow": ("nextflow_workflow",),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Inventory scientific-agent-skills and emit a conservative "
            "OneSkills migration manifest without executing source code."
        )
    )
    parser.add_argument(
        "--source-root",
        required=True,
        type=Path,
        help="scientific-agent-skills repository root",
    )
    parser.add_argument(
        "--target-root",
        type=Path,
        default=Path(__file__).resolve().parents[3],
        help="oneskills-dev repository root (default: inferred from this script)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="JSON manifest output path",
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        help="optional human-readable summary output path",
    )
    return parser.parse_args()


def read_text(path: Path, limit: int = 2_000_000) -> str:
    try:
        raw = path.read_bytes()
    except OSError:
        return ""
    if len(raw) > limit:
        raw = raw[:limit]
    return raw.decode("utf-8", errors="replace")


def safe_sha256(path: Path) -> str | None:
    digest = hashlib.sha256()
    try:
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
    except OSError:
        return None
    return digest.hexdigest()


def relative_path(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def iter_files(root: Path) -> Iterable[Path]:
    if not root.exists():
        return ()
    return (
        path
        for path in root.rglob("*")
        if path.is_file() and not any(part in SKIP_NAMES for part in path.parts)
    )


def normalized_name(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.lower())


def parse_frontmatter(path: Path) -> dict[str, str]:
    text = read_text(path)
    if not text.startswith("---"):
        return {}
    lines = text.splitlines()
    end = next((index for index in range(1, len(lines)) if lines[index].strip() == "---"), None)
    if end is None:
        return {}
    result: dict[str, str] = {}
    for line in lines[1:end]:
        match = re.match(r"^([A-Za-z][A-Za-z0-9_-]*)\s*:\s*(.*?)\s*$", line)
        if not match:
            continue
        value = match.group(2).strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        result[match.group(1)] = value
    return result


def file_summary(files: list[Path], root: Path, include_hash: bool = False) -> dict[str, Any]:
    by_extension: dict[str, int] = {}
    total_bytes = 0
    for path in files:
        extension = path.suffix.lower() or "<none>"
        by_extension[extension] = by_extension.get(extension, 0) + 1
        try:
            total_bytes += path.stat().st_size
        except OSError:
            pass
    result: dict[str, Any] = {
        "count": len(files),
        "bytes": total_bytes,
        "extensions": dict(sorted(by_extension.items())),
    }
    if include_hash:
        result["files"] = [
            {
                "path": relative_path(path, root),
                "bytes": path.stat().st_size if path.exists() else None,
                "sha256": safe_sha256(path),
            }
            for path in sorted(files)
        ]
    return result


def single_file_summary(path: Path, root: Path) -> dict[str, Any]:
    return {
        "present": path.exists(),
        "path": relative_path(path, root) if path.exists() else None,
        "bytes": path.stat().st_size if path.exists() else None,
        "sha256": safe_sha256(path) if path.exists() else None,
    }


def section_names(text: str) -> list[str]:
    return [match.group(1).strip() for match in re.finditer(r"^#{2,4}\s+(.+?)\s*$", text, re.MULTILINE)]


def knowledge_channels(skill_text: str, reference_files: list[Path]) -> list[str]:
    lower = skill_text.lower()
    channels: list[str] = []
    checks = {
        "trigger_and_scope": ("when to use", "use when", "trigger", "scope"),
        "workflow": ("workflow", "steps", "procedure", "pipeline"),
        "interface": ("api", "input", "output", "parameter", "dependency"),
        "validation_and_caveats": ("validation", "limitation", "warning", "failure"),
        "worked_examples": ("example", "```"),
    }
    for channel, signals in checks.items():
        if any(signal in lower for signal in signals):
            channels.append(channel)
    if reference_files:
        channels.append("references")
    return channels


def match_flags(text: str, patterns: Iterable[str]) -> list[str]:
    lower = text.lower()
    return [pattern for pattern in patterns if re.search(pattern, lower, re.IGNORECASE)]


def code_file_record(path: Path, skill_root: Path) -> dict[str, Any]:
    text = read_text(path)
    flags: list[str] = []
    for flag, patterns in RISK_PATTERNS.items():
        if match_flags(text, patterns):
            flags.append(flag)
    interface_signals = match_flags(text, INTERFACE_PATTERNS)
    install_signals = match_flags(text, INSTALL_PATTERNS)
    extension = path.suffix.lower()
    kind = "template" if extension in {".json", ".toml", ".yaml", ".yml"} else "code"
    return {
        "path": relative_path(path, skill_root),
        "kind": kind,
        "extension": extension or "<none>",
        "bytes": path.stat().st_size if path.exists() else None,
        "sha256": safe_sha256(path),
        "risk_flags": sorted(set(flags)),
        "interface_signals": sorted(set(interface_signals)),
        "install_signals": sorted(set(install_signals)),
    }


def code_assessment(
    skill_root: Path,
    skill_text: str,
    script_files: list[Path],
    asset_files: list[Path],
    reference_files: list[Path],
) -> dict[str, Any]:
    candidates = [
        path
        for path in [*script_files, *asset_files]
        if path.suffix.lower() in CODE_EXTENSIONS
    ]
    records = [code_file_record(path, skill_root) for path in sorted(set(candidates))]
    risk_flags = sorted({flag for record in records for flag in record["risk_flags"]})
    interface_count = sum(bool(record["interface_signals"]) for record in records)
    has_docs_io = bool(re.search(r"\b(input|output|interface|argument|parameter)\b", skill_text, re.I))
    has_tests = any("test" in path.name.lower() or "fixture" in path.parts for path in skill_root.rglob("*") if path.is_file())
    score = 0
    if records:
        score += 25
    if interface_count:
        score += 25
    if has_docs_io:
        score += 15
    if has_tests:
        score += 15
    if not risk_flags:
        score += 20
    score = min(score, 100)

    stable_io = bool(interface_count and has_docs_io)
    low_file_count = len(records) <= 2
    executor_evidence = stable_io and (has_tests or low_file_count)

    if not records:
        recommendation = "resource_only"
    elif score >= 75 and not risk_flags and executor_evidence:
        recommendation = "propose_executor"
    elif score >= 45 and not {"dynamic_execution", "credential_handling"}.intersection(risk_flags):
        recommendation = "resource_with_execution_assets"
    else:
        recommendation = "resource_only"

    return {
        "candidate_file_count": len(records),
        "candidate_files": records,
        "risk_flags": risk_flags,
        "interface_file_count": interface_count,
        "has_documented_io_signals": has_docs_io,
        "has_test_or_fixture_signals": has_tests,
        "readiness_score": score,
        "recommendation": recommendation,
    }


def concern_families(text: str) -> list[str]:
    lower = text.lower()
    return sorted(
        family
        for family, pattern_group in CONCERN_PATTERNS.items()
        if any(re.search(pattern, lower, re.IGNORECASE) for pattern in pattern_group)
    )


def recommended_shape(
    skill_text: str,
    reference_count: int,
    script_count: int,
    asset_count: int,
    code_recommendation: str,
) -> str:
    lower = skill_text.lower()
    has_workflow = bool(re.search(r"\b(workflow|pipeline|stage|handoff)\b", lower))
    has_secondary_concern = bool(
        re.search(
            r"\b(api|database|dataset|model|visualization|report|output|service|package)\b",
            lower,
        )
    )
    has_multiple_artifact_kinds = script_count > 0 and asset_count > 0 and reference_count > 0
    has_large_procedural_surface = script_count >= 3 and reference_count >= 5
    if has_multiple_artifact_kinds or (has_workflow and has_secondary_concern and has_large_procedural_surface):
        return "split_primitives"
    if code_recommendation == "propose_executor":
        return "primitive_plus_executor"
    return "single_primitive"


def extract_json_string(raw: str, key: str) -> str | None:
    match = re.search(rf'"{re.escape(key)}"\s*:\s*"([^"\n]*)"', raw)
    return match.group(1) if match else None


def parse_target_metadata(path: Path, asset_root: Path) -> dict[str, Any]:
    raw = read_text(path)
    record: dict[str, Any] = {
        "path": relative_path(path.parent, asset_root),
        "name": path.parent.name,
        "primitive_id": extract_json_string(raw, "primitive_id"),
        "type": extract_json_string(raw, "type"),
        "domain": extract_json_string(raw, "domain"),
        "category": extract_json_string(raw, "category"),
        "distilled_from": extract_json_string(raw, "distilled_from"),
        "distilled_from_version": extract_json_string(raw, "distilled_from_version"),
        "parse_mode": "strict_json",
    }
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        record["parse_mode"] = "regex_fallback"
    else:
        record.update(
            {
                "name": parsed.get("name") or record["name"],
                "primitive_id": parsed.get("primitive_id"),
                "type": parsed.get("type"),
                "domain": parsed.get("domain"),
                "category": parsed.get("category"),
                "distilled_from": (parsed.get("source") or {}).get("distilled_from"),
                "distilled_from_version": (parsed.get("source") or {}).get("distilled_from_version"),
            }
        )
    return record


def target_records(target_root: Path) -> list[dict[str, Any]]:
    asset_root = target_root / "skills" / "onescience-primitives" / "assets"
    return [
        parse_target_metadata(path, asset_root)
        for path in sorted(asset_root.rglob("metadata.json"))
        if path.is_file()
    ]


def source_locator_name(locator: str | None) -> str | None:
    if not locator:
        return None
    return locator.rstrip("/").split("/")[-1]


def target_matches(source_name: str, targets: list[dict[str, Any]]) -> dict[str, Any]:
    explicit = [
        record
        for record in targets
        if source_locator_name(record.get("distilled_from")) == source_name
    ]
    if explicit:
        return {"status": "explicit_provenance", "records": explicit}

    normalized = normalized_name(source_name)
    exact = [record for record in targets if normalized_name(record["name"]) == normalized]
    if exact:
        return {"status": "heuristic_name_match", "records": exact}

    aliases = ALIASES.get(source_name, ())
    aliased = [
        record
        for record in targets
        if any(normalized_name(alias) == normalized_name(record["name"]) for alias in aliases)
    ]
    if aliased:
        return {"status": "heuristic_alias_match", "records": aliased}
    return {"status": "uncovered", "records": []}


def inventory_skill(skill_root: Path, targets: list[dict[str, Any]]) -> dict[str, Any]:
    name = skill_root.name
    skill_md = skill_root / "SKILL.md"
    skill_text = read_text(skill_md)
    frontmatter = parse_frontmatter(skill_md)
    reference_files = list(iter_files(skill_root / "references"))
    script_files = list(iter_files(skill_root / "scripts"))
    asset_files = list(iter_files(skill_root / "assets"))
    text_files = [
        path
        for path in [skill_md, *reference_files, *script_files, *asset_files]
        if path.exists() and path.suffix.lower() in TEXT_EXTENSIONS
    ]
    combined_text = "\n".join(read_text(path) for path in text_files)
    code = code_assessment(skill_root, combined_text, script_files, asset_files, reference_files)
    match = target_matches(name, targets)
    shape = recommended_shape(
        skill_text,
        len(reference_files),
        len(script_files),
        len(asset_files),
        code["recommendation"],
    )
    priority = 0
    if match["status"] == "uncovered":
        priority += 45
    elif match["status"] != "explicit_provenance":
        priority += 25
    priority += min(code["readiness_score"] // 4, 25)
    priority += min(len(reference_files), 10)
    priority += min(len(script_files), 10)
    priority = min(priority, 100)

    return {
        "name": name,
        "source_path": relative_path(skill_root, skill_root.parent.parent),
        "frontmatter": {
            "name": frontmatter.get("name"),
            "description": frontmatter.get("description"),
        },
        "source_files": {
            "skill_md": single_file_summary(skill_md, skill_root),
            "references": file_summary(reference_files, skill_root, include_hash=True),
            "scripts": file_summary(script_files, skill_root, include_hash=True),
            "assets": file_summary(asset_files, skill_root, include_hash=True),
        },
        "knowledge": {
            "sections": section_names(skill_text),
            "channels": knowledge_channels(skill_text, reference_files),
            "text_file_count": len(text_files),
        },
        "code_migration": code,
        "concern_families": concern_families(combined_text),
        "recommended_shape": shape,
        "target_match": {
            "status": match["status"],
            "records": [
                {
                    "path": record["path"],
                    "name": record["name"],
                    "primitive_id": record.get("primitive_id"),
                    "parse_mode": record.get("parse_mode"),
                    "distilled_from": record.get("distilled_from"),
                }
                for record in match["records"]
            ],
        },
        "priority_score": priority,
    }


def build_manifest(source_root: Path, target_root: Path) -> dict[str, Any]:
    skills_root = source_root / "skills"
    if not skills_root.is_dir():
        raise SystemExit(f"source skills directory not found: {skills_root}")
    targets = target_records(target_root)
    skill_roots = sorted(path for path in skills_root.iterdir() if path.is_dir())
    records = [inventory_skill(path, targets) for path in skill_roots if (path / "SKILL.md").exists()]
    explicit = sum(record["target_match"]["status"] == "explicit_provenance" for record in records)
    heuristic = sum(record["target_match"]["status"] != "uncovered" for record in records) - explicit
    uncovered = sum(record["target_match"]["status"] == "uncovered" for record in records)
    return {
        "schema_version": "0.1",
        "generated_at": date.today().isoformat(),
        "source_root": "<source-root>",
        "target_root": "<target-root>",
        "policy": {
            "read_only": True,
            "executes_source_code": False,
            "copies_source_files": False,
            "recommendation_is_advisory": True,
        },
        "summary": {
            "source_skill_directories": len(skill_roots),
            "source_skills_with_skill_md": len(records),
            "source_skills_with_scripts": sum(record["source_files"]["scripts"]["count"] > 0 for record in records),
            "source_skills_with_assets": sum(record["source_files"]["assets"]["count"] > 0 for record in records),
            "target_primitive_metadata_files": len(targets),
            "target_metadata_regex_fallback": sum(record["parse_mode"] == "regex_fallback" for record in targets),
            "explicit_provenance_matches": explicit,
            "heuristic_matches": heuristic,
            "uncovered_source_skills": uncovered,
            "code_recommendations": {
                recommendation: sum(
                    record["code_migration"]["recommendation"] == recommendation for record in records
                )
                for recommendation in (
                    "resource_only",
                    "resource_with_execution_assets",
                    "propose_executor",
                )
            },
            "shape_recommendations": {
                shape: sum(record["recommended_shape"] == shape for record in records)
                for shape in (
                    "single_primitive",
                    "split_primitives",
                    "primitive_plus_executor",
                )
            },
        },
        "skills": sorted(records, key=lambda record: (-record["priority_score"], record["name"])),
    }


def markdown_summary(manifest: dict[str, Any]) -> str:
    summary = manifest["summary"]
    lines = [
        "# Skill Migration Inventory",
        "",
        f"Generated: `{manifest['generated_at']}`",
        "",
        "This inventory is read-only. It does not execute or copy source code.",
        "",
        "## Summary",
        "",
        f"- Source skills with `SKILL.md`: {summary['source_skills_with_skill_md']}",
        f"- Target primitive metadata files: {summary['target_primitive_metadata_files']}",
        f"- Explicit provenance matches: {summary['explicit_provenance_matches']}",
        f"- Heuristic matches: {summary['heuristic_matches']}",
        f"- Uncovered source skills: {summary['uncovered_source_skills']}",
        f"- Target metadata requiring regex fallback: {summary['target_metadata_regex_fallback']}",
        "",
        "## Highest-Priority Candidates",
        "",
        "| Skill | Coverage | Shape | Code recommendation | Score |",
        "| --- | --- | --- | --- | ---: |",
    ]
    for record in manifest["skills"][:30]:
        lines.append(
            "| `{name}` | `{coverage}` | `{shape}` | `{recommendation}` | {score} |".format(
                name=record["name"],
                coverage=record["target_match"]["status"],
                shape=record["recommended_shape"],
                recommendation=record["code_migration"]["recommendation"],
                score=record["priority_score"],
            )
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- `explicit_provenance` is auditable integration through `source.distilled_from`.",
            "- `heuristic_*` is a candidate relationship and requires manual review.",
            "- `resource_with_execution_assets` means code may be selectively promoted after allowlist, hash, dependency, and boundary review.",
            "- `propose_executor` is only a candidate; it still requires isolated execution and acceptance evidence.",
            "- `split_primitives` indicates that one source skill appears to contain multiple reusable concerns.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    args = parse_args()
    manifest = build_manifest(args.source_root.resolve(), args.target_root.resolve())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(manifest, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    if args.markdown_output:
        args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
        args.markdown_output.write_text(markdown_summary(manifest), encoding="utf-8")
    summary = manifest["summary"]
    print(
        "inventory=ok "
        f"skills={summary['source_skills_with_skill_md']} "
        f"explicit={summary['explicit_provenance_matches']} "
        f"heuristic={summary['heuristic_matches']} "
        f"uncovered={summary['uncovered_source_skills']}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
