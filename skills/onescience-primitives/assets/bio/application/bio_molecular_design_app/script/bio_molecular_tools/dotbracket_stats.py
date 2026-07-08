#!/usr/bin/env python3
"""Summarize dot-bracket RNA secondary structures."""

from __future__ import annotations

import argparse
import json


def summarize(dotbracket: str) -> dict:
    stack: list[int] = []
    pairs: list[tuple[int, int]] = []
    unpaired = 0
    for i, char in enumerate(dotbracket.strip()):
        if char == "(":
            stack.append(i)
        elif char == ")":
            if stack:
                pairs.append((stack.pop(), i))
        elif char == ".":
            unpaired += 1
    paired_positions = len(pairs) * 2
    length = len(dotbracket.strip())
    return {
        "length": length,
        "base_pairs": len(pairs),
        "unmatched_open": len(stack),
        "paired_fraction": round(paired_positions / length, 4) if length else 0,
        "unpaired_fraction": round(unpaired / length, 4) if length else 0,
        "first_pairs_0based": pairs[:10],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Summarize a dot-bracket RNA structure.")
    parser.add_argument("dotbracket")
    args = parser.parse_args()
    print(json.dumps(summarize(args.dotbracket), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
