#!/usr/bin/env python3
"""Very small Newick QC utility."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def load_newick(value: str) -> str:
    path = Path(value)
    return path.read_text(encoding="utf-8").strip() if path.exists() else value.strip()


def leaf_names(newick: str) -> list[str]:
    tokens = re.findall(r"(?<=[(,])([^():,;]+)(?=[:),;])", newick)
    return [token.strip().strip("'\"") for token in tokens if token.strip()]


def main() -> int:
    parser = argparse.ArgumentParser(description="Check basic Newick syntax properties.")
    parser.add_argument("newick_or_path")
    args = parser.parse_args()
    text = load_newick(args.newick_or_path)
    leaves = leaf_names(text)
    result = {
        "ends_with_semicolon": text.endswith(";"),
        "open_parentheses": text.count("("),
        "close_parentheses": text.count(")"),
        "balanced_parentheses": text.count("(") == text.count(")"),
        "leaf_count_estimate": len(leaves),
        "duplicate_leaf_names": sorted({name for name in leaves if leaves.count(name) > 1}),
        "has_branch_lengths": bool(re.search(r":[0-9.eE+-]+", text)),
    }
    print(json.dumps(result, indent=2))
    return 0 if result["ends_with_semicolon"] and result["balanced_parentheses"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
