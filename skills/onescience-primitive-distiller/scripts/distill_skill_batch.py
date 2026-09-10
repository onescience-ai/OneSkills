#!/usr/bin/env python3
"""Run the OneScience skill-to-primitive distillation pipeline.

The pipeline is conservative by design. It can build an inventory manifest and
materialize a selected primitive plan, but it never imports or executes source
scientific code.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import date
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_TARGET_ROOT = SCRIPT_DIR.parents[2]
DEFAULT_OUTPUT_DIR = DEFAULT_TARGET_ROOT / "docs" / "open-source"


def run_step(args: list[str]) -> None:
    completed = subprocess.run(args, check=False)
    if completed.returncode != 0:
        raise SystemExit(completed.returncode)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", required=True, type=Path)
    parser.add_argument("--target-root", type=Path, default=DEFAULT_TARGET_ROOT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--date", default=date.today().isoformat())
    parser.add_argument("--plan-file", type=Path, help="optional JSON materialization plan")
    parser.add_argument("--skill", action="append", help="selected source skill; repeatable")
    parser.add_argument("--inventory-only", action="store_true")
    parser.add_argument("--materialize-only", action="store_true")
    parser.add_argument("--force", action="store_true")
    parser.add_argument(
        "--copy-knowledge-references",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="copy source references into primitive knowledge_assets during materialization",
    )
    parser.add_argument(
        "--copy-source-payloads",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="copy source scripts/assets into inert primitive source_payload records during materialization",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.inventory_only and args.materialize_only:
        raise SystemExit("choose at most one of --inventory-only and --materialize-only")

    source_root = args.source_root.resolve()
    target_root = args.target_root.resolve()
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    manifest_json = output_dir / f"skill_migration_inventory_{args.date}.json"
    manifest_md = output_dir / f"skill_migration_inventory_{args.date}.md"
    summary: dict[str, Any] = {
        "source_root": str(source_root),
        "target_root": str(target_root),
        "manifest_json": str(manifest_json),
        "manifest_markdown": str(manifest_md),
        "materialized": not args.inventory_only,
    }

    if not args.materialize_only:
        run_step(
            [
                sys.executable,
                str(SCRIPT_DIR / "build_skill_migration_manifest.py"),
                "--source-root",
                str(source_root),
                "--target-root",
                str(target_root),
                "--output",
                str(manifest_json),
                "--markdown-output",
                str(manifest_md),
            ]
        )

    if not args.inventory_only:
        command = [
            sys.executable,
            str(SCRIPT_DIR / "materialize_skill_primitives.py"),
            "--source-root",
            str(source_root),
            "--target-root",
            str(target_root),
        ]
        if args.plan_file:
            command.extend(["--plan-file", str(args.plan_file.resolve())])
        for skill in args.skill or []:
            command.extend(["--skill", skill])
        if args.force:
            command.append("--force")
        command.append("--copy-knowledge-references" if args.copy_knowledge_references else "--no-copy-knowledge-references")
        command.append("--copy-source-payloads" if args.copy_source_payloads else "--no-copy-source-payloads")
        run_step(command)

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
