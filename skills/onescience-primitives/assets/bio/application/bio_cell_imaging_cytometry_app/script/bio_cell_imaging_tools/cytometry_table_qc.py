#!/usr/bin/env python3
"""Basic QC for exported cytometry event tables."""

from __future__ import annotations

import argparse
import csv
import json
from statistics import mean


def parse_float(value: str):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def main() -> int:
    parser = argparse.ArgumentParser(description="Summarize numeric marker columns in a cytometry CSV/TSV table.")
    parser.add_argument("table")
    parser.add_argument("--delimiter", default=",")
    parser.add_argument("--max-rows", type=int, default=100000)
    args = parser.parse_args()

    with open(args.table, newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle, delimiter=args.delimiter)
        fields = reader.fieldnames or []
        values = {field: [] for field in fields}
        row_count = 0
        for row in reader:
            row_count += 1
            if row_count > args.max_rows:
                break
            for field in fields:
                number = parse_float(row.get(field, ""))
                if number is not None:
                    values[field].append(number)

    numeric = {}
    for field, vals in values.items():
        if vals:
            numeric[field] = {
                "n": len(vals),
                "min": min(vals),
                "mean": mean(vals),
                "max": max(vals),
                "zero_or_negative": sum(1 for value in vals if value <= 0),
            }
    print(json.dumps({"rows_read": row_count, "numeric_columns": numeric}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
