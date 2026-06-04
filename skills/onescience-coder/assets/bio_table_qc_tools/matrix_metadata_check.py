#!/usr/bin/env python3
"""Check sample IDs between a feature-by-sample matrix and metadata."""

from __future__ import annotations

import argparse
import csv
import json


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate matrix sample columns against metadata sample IDs.")
    parser.add_argument("matrix_tsv")
    parser.add_argument("metadata_csv")
    parser.add_argument("--sample-id-column", default="sample_id")
    args = parser.parse_args()

    with open(args.matrix_tsv, newline="", encoding="utf-8-sig") as handle:
        matrix_reader = csv.reader(handle, delimiter="\t")
        header = next(matrix_reader)
    matrix_samples = header[1:]

    with open(args.metadata_csv, newline="", encoding="utf-8-sig") as handle:
        metadata = list(csv.DictReader(handle))
    metadata_samples = [row.get(args.sample_id_column, "") for row in metadata]

    result = {
        "matrix_sample_count": len(matrix_samples),
        "metadata_sample_count": len(metadata_samples),
        "missing_in_metadata": sorted(set(matrix_samples) - set(metadata_samples)),
        "missing_in_matrix": sorted(set(metadata_samples) - set(matrix_samples)),
        "duplicate_matrix_samples": sorted({sample for sample in matrix_samples if matrix_samples.count(sample) > 1}),
        "duplicate_metadata_samples": sorted({sample for sample in metadata_samples if metadata_samples.count(sample) > 1}),
        "same_order": matrix_samples == metadata_samples,
    }
    print(json.dumps(result, indent=2))
    ok = not result["missing_in_metadata"] and not result["missing_in_matrix"] and not result["duplicate_matrix_samples"] and not result["duplicate_metadata_samples"]
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
