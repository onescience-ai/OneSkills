#!/usr/bin/env python3
"""Scan simple CRISPR PAMs and emit guide candidates as TSV."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


IUPAC = {
    "A": "A",
    "C": "C",
    "G": "G",
    "T": "T",
    "N": "[ACGT]",
    "R": "[AG]",
    "Y": "[CT]",
    "V": "[ACG]",
}


def read_sequence(value: str) -> str:
    path = Path(value)
    text = path.read_text(encoding="utf-8") if path.exists() else value
    return re.sub(r"[^A-Za-z]", "", "".join(line for line in text.splitlines() if not line.startswith(">"))).upper()


def revcomp(seq: str) -> str:
    return seq.translate(str.maketrans("ACGT", "TGCA"))[::-1]


def pam_regex(pam: str) -> str:
    return "".join(IUPAC.get(base, re.escape(base)) for base in pam.upper())


def gc(seq: str) -> float:
    return (seq.count("G") + seq.count("C")) / len(seq) * 100 if seq else 0.0


def scan(seq: str, pam: str, guide_len: int, pam_side: str):
    pattern = re.compile(f"(?=({pam_regex(pam)}))")
    for strand, source in [("+", seq), ("-", revcomp(seq))]:
        for match in pattern.finditer(source):
            pam_start = match.start()
            pam_seq = source[pam_start : pam_start + len(pam)]
            if pam_side == "3prime":
                start = pam_start - guide_len
                end = pam_start
            else:
                start = pam_start + len(pam)
                end = start + guide_len
            if start < 0 or end > len(source):
                continue
            guide = source[start:end]
            original_start = start if strand == "+" else len(seq) - end
            yield {
                "guide": guide,
                "pam": pam_seq,
                "strand": strand,
                "start_0based": original_start,
                "gc_percent": round(gc(guide), 2),
                "poly_t": "TTTT" in guide,
            }


def main() -> int:
    parser = argparse.ArgumentParser(description="Scan a DNA sequence for CRISPR guide candidates.")
    parser.add_argument("sequence_or_fasta")
    parser.add_argument("--pam", default="NGG")
    parser.add_argument("--guide-len", type=int, default=20)
    parser.add_argument("--pam-side", choices=["3prime", "5prime"], default="3prime")
    args = parser.parse_args()

    seq = read_sequence(args.sequence_or_fasta)
    print("guide\tpam\tstrand\tstart_0based\tgc_percent\tpoly_t")
    for row in scan(seq, args.pam, args.guide_len, args.pam_side):
        print("\t".join(str(row[key]) for key in ["guide", "pam", "strand", "start_0based", "gc_percent", "poly_t"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
