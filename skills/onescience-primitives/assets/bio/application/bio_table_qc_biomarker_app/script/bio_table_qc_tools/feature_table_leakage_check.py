#!/usr/bin/env python3
"""Check common leakage risks in biomarker feature tables."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect sample IDs, patient IDs, splits, and endpoint completeness.")
    parser.add_argument("table_csv")
    parser.add_argument("--id-col", default="sample_id")
    parser.add_argument("--patient-col", default="patient_id")
    parser.add_argument("--split-col", default="split")
    parser.add_argument("--endpoint-col", default="endpoint")
    args = parser.parse_args()

    with open(args.table_csv, newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.DictReader(handle))
    sample_counts = Counter(row.get(args.id_col, "") for row in rows)
    patient_splits = defaultdict(set)
    missing_endpoint = 0
    for row in rows:
        patient = row.get(args.patient_col, "")
        split = row.get(args.split_col, "")
        if patient and split:
            patient_splits[patient].add(split)
        if not row.get(args.endpoint_col, ""):
            missing_endpoint += 1
    leaked_patients = sorted(patient for patient, splits in patient_splits.items() if len(splits) > 1)
    result = {
        "rows": len(rows),
        "duplicate_sample_ids": sorted(sample for sample, count in sample_counts.items() if sample and count > 1),
        "patients_in_multiple_splits": leaked_patients,
        "missing_endpoint_rows": missing_endpoint,
    }
    print(json.dumps(result, indent=2))
    return 0 if not leaked_patients and not result["duplicate_sample_ids"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
