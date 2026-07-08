#!/usr/bin/env python3
"""Lightweight sequence checks for primer/probe handoffs."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def read_sequence(value: str) -> str:
    path = Path(value)
    if path.exists():
        text = path.read_text(encoding="utf-8")
    else:
        text = value
    lines = [line.strip() for line in text.splitlines() if line.strip() and not line.startswith(">")]
    return re.sub(r"[^A-Za-z]", "", "".join(lines)).upper()


def gc_fraction(seq: str) -> float:
    return (seq.count("G") + seq.count("C")) / len(seq) if seq else 0.0


def wallace_tm(seq: str) -> int:
    seq = seq.upper()
    return 2 * (seq.count("A") + seq.count("T")) + 4 * (seq.count("G") + seq.count("C"))


def longest_poly_x(seq: str) -> int:
    best = 0
    for base in "ACGT":
        runs = [len(match.group(0)) for match in re.finditer(f"{base}+", seq)]
        best = max(best, max(runs, default=0))
    return best


def simple_self_complement_score(seq: str, k: int = 4) -> int:
    comp = str.maketrans("ACGT", "TGCA")
    rc = seq.translate(comp)[::-1]
    kmers = {seq[i : i + k] for i in range(max(0, len(seq) - k + 1))}
    return sum(1 for i in range(max(0, len(rc) - k + 1)) if rc[i : i + k] in kmers)


def main() -> int:
    parser = argparse.ArgumentParser(description="Summarize DNA sequence design checks.")
    parser.add_argument("sequence_or_fasta", help="Inline sequence or FASTA path.")
    parser.add_argument("--name", default="sequence")
    args = parser.parse_args()

    seq = read_sequence(args.sequence_or_fasta)
    invalid = sorted(set(seq) - set("ACGTN"))
    clean = seq.replace("N", "")
    result = {
        "name": args.name,
        "length_bp": len(seq),
        "valid_dna": not invalid and len(seq) > 0,
        "invalid_symbols": invalid,
        "gc_percent_without_n": round(gc_fraction(clean) * 100, 2) if clean else 0,
        "wallace_tm_without_n_c": wallace_tm(clean) if clean else 0,
        "longest_poly_x": longest_poly_x(clean),
        "self_complement_4mer_hits": simple_self_complement_score(clean),
        "warnings": [],
    }
    if result["gc_percent_without_n"] < 35 or result["gc_percent_without_n"] > 65:
        result["warnings"].append("GC outside typical primer-friendly range")
    if result["longest_poly_x"] > 4:
        result["warnings"].append("poly-X run longer than 4")
    if result["self_complement_4mer_hits"] > 4:
        result["warnings"].append("possible self-complementarity")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result["valid_dna"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
