"""Validate a knowledge-capture contribution without third-party dependencies."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


REQUIRED_SECTIONS = [
    "Contribution Metadata",
    "Task Summary",
    "Interaction Timeline",
    "Decisions And Evidence",
    "Resources And Skills",
    "Artifacts And Verification",
    "Failures And Recovery",
    "Reusable Knowledge",
    "Integration Proposal",
    "Promotion Decision",
    "Privacy And Limitations",
]

SENSITIVE_PATTERNS = {
    "private_key": re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    "bearer_token": re.compile(r"\bBearer\s+[A-Za-z0-9._~+/=-]{16,}", re.I),
    "jwt": re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b"),
    "api_key_assignment": re.compile(
        r"\b(api[_-]?key|access[_-]?token|secret[_-]?key|password)\s*[:=]\s*[^\s`]{8,}",
        re.I,
    ),
}


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def scan_sensitive(paths: list[Path]) -> list[str]:
    findings: list[str] = []
    for path in paths:
        text = path.read_text(encoding="utf-8", errors="replace")
        for name, pattern in SENSITIVE_PATTERNS.items():
            if pattern.search(text):
                findings.append(f"{name}:{path.name}")
    return findings


def validate(directory: Path) -> list[str]:
    errors: list[str] = []
    metadata_path = directory / "contribution.json"
    markdown_path = directory / "contribution.md"
    if not metadata_path.is_file():
        errors.append("missing contribution.json")
        return errors
    if not markdown_path.is_file():
        errors.append("missing contribution.md")
        return errors

    try:
        metadata = load_json(metadata_path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        errors.append(f"invalid contribution.json: {exc}")
        return errors

    for key in ("schema_version", "contribution_id", "title", "domain", "kind", "evidence", "promotion"):
        if not metadata.get(key):
            errors.append(f"missing metadata field: {key}")

    if metadata.get("kind") not in {"knowledge", "integration", "both"}:
        errors.append("kind must be knowledge, integration, or both")
    if metadata.get("domain") not in {"bio", "cfd", "climate", "matchem", "general", "unknown"}:
        errors.append("domain is invalid")
    if not isinstance(metadata.get("evidence"), list) or not metadata["evidence"]:
        errors.append("evidence must be a non-empty list")
    promotion = metadata.get("promotion")
    if not isinstance(promotion, dict) or not promotion.get("recommendation"):
        errors.append("promotion.recommendation is required")

    markdown = markdown_path.read_text(encoding="utf-8", errors="replace")
    for section in REQUIRED_SECTIONS:
        if f"## {section}" not in markdown:
            errors.append(f"missing markdown section: {section}")

    findings = scan_sensitive([metadata_path, markdown_path])
    if findings:
        errors.append("sensitive patterns detected: " + ", ".join(findings))

    payload_path = directory / "issue_payload.json"
    if payload_path.exists():
        try:
            payload = load_json(payload_path)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            errors.append(f"invalid issue_payload.json: {exc}")
        else:
            if not payload.get("title") or not payload.get("body"):
                errors.append("issue payload requires title and body")
            if not isinstance(payload.get("labels"), list):
                errors.append("issue payload labels must be a list")
            payload_findings = scan_sensitive([payload_path])
            if payload_findings:
                errors.append("sensitive patterns detected: " + ", ".join(payload_findings))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path, help="contribution directory")
    args = parser.parse_args()
    errors = validate(args.directory)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(f"VALID: {args.directory}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
