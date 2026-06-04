#!/usr/bin/env python3
"""Compute VAF and QC flags from ctDNA target count tables."""

from __future__ import annotations

import argparse
import csv
import sys


def main() -> int:
    parser = argparse.ArgumentParser(description="Add VAF and simple QC flags to a ctDNA count table.")
    parser.add_argument("counts_tsv", help="TSV with sample_id, chrom, pos, ref_count, alt_count.")
    parser.add_argument("--min-depth", type=int, default=1000)
    parser.add_argument("--min-alt", type=int, default=3)
    args = parser.parse_args()

    with open(args.counts_tsv, newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        fields = list(reader.fieldnames or []) + ["depth", "vaf", "qc_flags"]
        writer = csv.DictWriter(sys.stdout, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for row in reader:
            ref = int(float(row.get("ref_count", 0) or 0))
            alt = int(float(row.get("alt_count", 0) or 0))
            depth = ref + alt
            flags = []
            if depth < args.min_depth:
                flags.append("low_depth")
            if alt < args.min_alt:
                flags.append("low_alt_count")
            row["depth"] = depth
            row["vaf"] = f"{(alt / depth if depth else 0):.6f}"
            row["qc_flags"] = ";".join(flags) if flags else "pass"
            writer.writerow(row)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
