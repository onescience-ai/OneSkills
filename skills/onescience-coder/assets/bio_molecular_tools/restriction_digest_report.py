#!/usr/bin/env python3
"""Small restriction digest reporter for common enzymes."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

ENZYMES = {
    "EcoRI": "GAATTC",
    "BamHI": "GGATCC",
    "HindIII": "AAGCTT",
    "XhoI": "CTCGAG",
    "NotI": "GCGGCCGC",
    "NheI": "GCTAGC",
    "SpeI": "ACTAGT",
    "XbaI": "TCTAGA",
    "KpnI": "GGTACC",
    "PstI": "CTGCAG",
    "SalI": "GTCGAC",
    "SmaI": "CCCGGG",
}


def read_sequence(value: str) -> str:
    path = Path(value)
    text = path.read_text(encoding="utf-8") if path.exists() else value
    return re.sub(r"[^A-Za-z]", "", "".join(line for line in text.splitlines() if not line.startswith(">"))).upper()


def find_sites(seq: str, enzyme: str) -> list[int]:
    motif = ENZYMES[enzyme]
    return [match.start() for match in re.finditer(f"(?={motif})", seq)]


def fragments(length: int, cuts: list[int], circular: bool) -> list[int]:
    cuts = sorted(set(cuts))
    if not cuts:
        return [length]
    if not circular:
        points = [0] + cuts + [length]
        return [points[i + 1] - points[i] for i in range(len(points) - 1) if points[i + 1] - points[i] > 0]
    if len(cuts) == 1:
        return [length]
    return [cuts[i + 1] - cuts[i] for i in range(len(cuts) - 1)] + [length - cuts[-1] + cuts[0]]


def main() -> int:
    parser = argparse.ArgumentParser(description="Report restriction sites and digest fragments.")
    parser.add_argument("sequence_or_fasta")
    parser.add_argument("--enzymes", default="EcoRI,BamHI,HindIII,XhoI")
    parser.add_argument("--topology", choices=["linear", "circular"], default="circular")
    args = parser.parse_args()

    seq = read_sequence(args.sequence_or_fasta)
    enzymes = [name.strip() for name in args.enzymes.split(",") if name.strip()]
    unknown = [name for name in enzymes if name not in ENZYMES]
    if unknown:
        raise SystemExit(f"Unknown built-in enzymes: {', '.join(unknown)}")
    all_cuts: list[int] = []
    print("enzyme\trecognition\tcut_count\tpositions_0based")
    for enzyme in enzymes:
        sites = find_sites(seq, enzyme)
        all_cuts.extend(sites)
        print(f"{enzyme}\t{ENZYMES[enzyme]}\t{len(sites)}\t{','.join(map(str, sites))}")
    print("\nfragments_bp\t" + ",".join(map(str, sorted(fragments(len(seq), all_cuts, args.topology == "circular"), reverse=True))))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
