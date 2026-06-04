#!/usr/bin/env python3
"""QC checks for GWAS summary statistics tables."""

from __future__ import annotations

import argparse
import csv
import json


def main() -> int:
    parser = argparse.ArgumentParser(description="Check required GWAS summary columns and P-value range.")
    parser.add_argument("summary_stats")
    parser.add_argument("--delimiter", default="\t")
    parser.add_argument("--p-column", default="P")
    args = parser.parse_args()

    required = {"CHR", "POS", "EA", "OA", args.p_column}
    with open(args.summary_stats, newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle, delimiter=args.delimiter)
        fields = set(reader.fieldnames or [])
        rows = 0
        bad_p = 0
        missing_p = 0
        for row in reader:
            rows += 1
            value = row.get(args.p_column, "")
            try:
                pvalue = float(value)
                if pvalue < 0 or pvalue > 1:
                    bad_p += 1
            except ValueError:
                missing_p += 1
    result = {
        "rows": rows,
        "missing_required_columns": sorted(required - fields),
        "bad_p_values": bad_p,
        "missing_or_non_numeric_p": missing_p,
    }
    print(json.dumps(result, indent=2))
    return 0 if not result["missing_required_columns"] and bad_p == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
