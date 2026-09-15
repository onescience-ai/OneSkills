#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Dataset contract auditor - executable landing point for the
`data-target-definition` Task card (materials generic 4-step skeleton, s01).

Stdlib only, offline, deterministic. Emits one machine-readable JSON report
with a four-state decision (PASS / PARTIAL / REJECT / BLOCKED) inherited from
the scenario catalogs' `acceptance_decision` vocabulary.

Checks performed
----------------
1. readability + sample count floor                -> BLOCKED
2. target column presence / unit consistency       -> BLOCKED
3. full-row duplicates + duplicate id              -> PARTIAL if over budget
4. per-column missingness                          -> PARTIAL if over budget
5. split traceability (all three folds present)    -> PARTIAL if incomplete
6. scaffold leakage across train / test            -> REJECT
7. target definition freeze (name/unit/dir/thresh) -> recorded in the report

Usage
-----
    python audit_dataset.py --demo            --target bulk_modulus --unit GPa --direction max --threshold 10
    python audit_dataset.py --demo-leaky      --target bulk_modulus --unit GPa --direction max --threshold 10
    python audit_dataset.py --csv my.csv      --target bulk_modulus --unit GPa --direction max --threshold 10
    ...  --out report.json

Exit codes: 0 = report produced (any decision), 2 = hard failure (no report).
"""

import argparse
import csv
import io
import json
import os
import sys

VERSION = "1.0.0"
HEADER = ["sample_id", "framework_family", "n_atoms", "density_g_cm3",
          "bulk_modulus_GPa", "linker_length_A", "split"]

# --- deterministic demo fixtures -------------------------------------------
# clean: 24 MOFs over 15 framework families, split fold-disjoint at the
# scaffold level (a family appears in exactly ONE of train / valid / test),
# no duplicate row, no duplicate id, no missing value.
_CLEAN = [
    # train: families UiO-66, UiO-67, ZIF-8, ZIF-11, MIL-53
    ("MOF-001", "UiO-66", 124, 4.01, 12.8, 14.2, "train"),
    ("MOF-002", "UiO-66", 130, 3.94, 11.9, 15.1, "train"),
    ("MOF-003", "UiO-67", 142, 3.72, 10.4, 16.8, "train"),
    ("MOF-004", "UiO-67", 146, 3.66, 10.0, 17.1, "train"),
    ("MOF-005", "ZIF-8", 88, 2.95, 6.1, 11.3, "train"),
    ("MOF-006", "ZIF-8", 92, 2.88, 5.7, 11.9, "train"),
    ("MOF-007", "ZIF-11", 96, 2.76, 5.2, 12.4, "train"),
    ("MOF-008", "MIL-53", 74, 3.10, 8.3, 10.6, "train"),
    ("MOF-009", "MIL-53", 78, 3.05, 8.0, 11.0, "train"),
    # valid: families MOF-74, Mg-MOF-74, UiO-68, ZIF-71, MIL-101
    ("MOF-010", "MOF-74", 102, 3.31, 9.6, 12.2, "valid"),
    ("MOF-011", "MOF-74", 106, 3.27, 9.2, 12.7, "valid"),
    ("MOF-012", "Mg-MOF-74", 100, 3.42, 10.1, 12.0, "valid"),
    ("MOF-013", "Mg-MOF-74", 104, 3.38, 9.8, 12.5, "valid"),
    ("MOF-014", "UiO-68", 150, 3.55, 9.1, 17.6, "valid"),
    ("MOF-015", "ZIF-71", 118, 2.51, 4.4, 13.8, "valid"),
    ("MOF-016", "MIL-101", 166, 2.29, 6.8, 15.4, "valid"),
    ("MOF-017", "MIL-101", 170, 2.24, 6.5, 15.9, "valid"),
    # test: families IRMOF-1, IRMOF-16, HKUST-1, ZIF-90, MIL-125
    ("MOF-018", "IRMOF-1", 96, 3.19, 8.7, 14.6, "test"),
    ("MOF-019", "IRMOF-1", 100, 3.14, 8.4, 15.0, "test"),
    ("MOF-020", "IRMOF-16", 144, 2.71, 6.2, 18.3, "test"),
    ("MOF-021", "HKUST-1", 110, 2.64, 7.4, 13.1, "test"),
    ("MOF-022", "HKUST-1", 114, 2.58, 7.1, 13.5, "test"),
    ("MOF-023", "ZIF-90", 102, 2.83, 5.9, 12.9, "test"),
    ("MOF-024", "MIL-125", 128, 2.47, 4.9, 16.2, "test"),
]

# leaky: same fixtures plus a full-row duplicate, a reused sample_id, two
# missing values and one scaffold (UiO-66) crossing train -> test.
_LEAKY_EXTRA = [
    ("MOF-001", "UiO-66", 124, 4.01, 12.8, 14.2, "train"),   # exact duplicate row
    ("MOF-025", "UiO-66", 128, 3.97, "", 14.8, "test"),      # scaffold leak + missing target
    ("MOF-026", "ZIF-8", 90, "", 5.5, 11.6, "train"),        # missing density, same fold
    ("MOF-001", "ZIF-8", 94, 2.91, 6.0, 11.1, "valid"),      # duplicate sample_id
]


def fail(code, message, exit_code=2):
    print(json.dumps({"code": code, "message": message, "version": VERSION},
                     ensure_ascii=False))
    sys.exit(exit_code)


def to_csv(rows):
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(HEADER)
    for r in rows:
        w.writerow(list(r))
    return buf.getvalue()


def read_rows(args):
    if args.demo:
        return to_csv(_CLEAN), "demo"
    if args.demo_leaky:
        return to_csv(_CLEAN + _LEAKY_EXTRA), "demo-leaky"
    if not os.path.isfile(args.csv):
        fail("FILE_NOT_FOUND", "CSV not found: %s" % args.csv)
    try:
        with open(args.csv, "r", encoding="utf-8-sig", newline="") as fh:
            return fh.read(), os.path.basename(args.csv)
    except Exception as exc:
        fail("READ_ERROR", "cannot read %s: %s" % (args.csv, exc))


def parse(text):
    rdr = csv.DictReader(io.StringIO(text))
    fields = rdr.fieldnames or []
    rows = [dict(r) for r in rdr]
    return fields, rows


def is_missing(v):
    return v is None or str(v).strip() == "" or str(v).strip().upper() in ("NA", "NAN", "NULL", "NONE")


def num(v):
    try:
        return float(v)
    except Exception:
        return None


def audit(fields, rows, args):
    v = []           # violations: (severity, code, detail)
    n = len(rows)

    if n == 0:
        return None, [("BLOCKED", "EMPTY_DATASET", "no data rows")]
    if n < args.min_samples:
        v.append(("BLOCKED", "INSUFFICIENT_SAMPLES",
                  "n=%d < min_samples=%d" % (n, args.min_samples)))

    # --- target column -----------------------------------------------------
    tcol = args.target
    target_col = None
    for cand in (tcol, tcol + "_" + args.unit.replace("/", ""),
                 "%s_%s" % (tcol, args.unit)):
        if cand in fields:
            target_col = cand
            break
    if target_col is None:
        hits = [f for f in fields if tcol.lower() in f.lower()]
        target_col = hits[0] if len(hits) == 1 else None
    if target_col is None:
        v.append(("BLOCKED", "TARGET_COLUMN_NOT_FOUND",
                  "no unambiguous column for target %r in %s" % (tcol, fields)))
    else:
        vals = [num(r.get(target_col)) for r in rows]
        miss = sum(1 for x in vals if x is None)
        if miss == len(vals):
            v.append(("BLOCKED", "TARGET_ALL_MISSING",
                      "target column %s has no usable value" % target_col))
        elif miss:
            v.append(("PARTIAL", "TARGET_PARTIALLY_MISSING",
                      "target column %s missing %d/%d" % (target_col, miss, len(vals))))

    # --- duplicates --------------------------------------------------------
    seen_rows, dup_rows = set(), 0
    seen_ids, dup_ids = {}, 0
    idc = args.id_col if args.id_col in fields else None
    for r in rows:
        key = tuple(str(r.get(f, "")) for f in fields)
        if key in seen_rows:
            dup_rows += 1
        seen_rows.add(key)
        if idc:
            k = str(r.get(idc, ""))
            if k in seen_ids and not is_missing(r.get(idc)):
                dup_ids += 1
            seen_ids[k] = seen_ids.get(k, 0) + 1
    dup_rate = round((dup_rows + dup_ids) / float(n), 6) if n else 0.0
    if dup_rate > args.max_duplicate_rate:
        v.append(("PARTIAL", "DUPLICATE_RATE_OVER_BUDGET",
                  "duplicate_rate=%.4f > %.4f (dup_rows=%d, dup_ids=%d)"
                  % (dup_rate, args.max_duplicate_rate, dup_rows, dup_ids)))

    # --- missingness -------------------------------------------------------
    missing = {}
    for f in fields:
        m = sum(1 for r in rows if is_missing(r.get(f)))
        missing[f] = round(m / float(n), 6) if n else 0.0
    over = {k: x for k, x in missing.items() if x > args.max_missing_rate}
    if over:
        v.append(("PARTIAL", "MISSING_RATE_OVER_BUDGET",
                  "columns over %.2f: %s" % (args.max_missing_rate, over)))

    # --- split traceability ------------------------------------------------
    spc = args.split_col if args.split_col in fields else None
    split_info = {"scheme": args.split_scheme, "column": spc,
                  "counts": {}, "disjoint": None, "folds_present": []}
    if spc is None:
        v.append(("PARTIAL", "SPLIT_COLUMN_ABSENT",
                  "no %r column -> split not traceable" % args.split_col))
    else:
        counts = {}
        for r in rows:
            lab = str(r.get(spc, "")).strip().lower() or "<unset>"
            counts[lab] = counts.get(lab, 0) + 1
        split_info["counts"] = counts
        present = [f for f in ("train", "valid", "test") if counts.get(f, 0) > 0]
        split_info["folds_present"] = present
        if len(present) < 3:
            v.append(("PARTIAL", "SPLIT_FOLDS_INCOMPLETE",
                      "expected train/valid/test, present=%s" % present))
        # scaffold leakage: same scaffold group in both train and test
        sc = args.scaffold_col if args.scaffold_col in fields else None
        if sc:
            groups = {}
            for r in rows:
                g = str(r.get(sc, "")).strip()
                lab = str(r.get(spc, "")).strip().lower()
                if not g:
                    continue
                groups.setdefault(g, set()).add(lab)
            crossed = sorted(g for g, s in groups.items()
                             if "train" in s and "test" in s)
            split_info["disjoint"] = (len(crossed) == 0)
            split_info["scaffold_column"] = sc
            split_info["leaking_groups"] = crossed
            if crossed:
                v.append(("REJECT", "SCAFFOLD_LEAKAGE",
                          "groups present in both train and test: %s" % crossed))
        else:
            split_info["disjoint"] = None
            v.append(("PARTIAL", "SCAFFOLD_COLUMN_ABSENT",
                      "no %r column -> leakage cannot be verified" % args.scaffold_col))

    audit_block = {
        "n_total": n,
        "n_unique_rows": len(seen_rows),
        "duplicate_rows": dup_rows,
        "duplicate_ids": dup_ids,
        "duplicate_rate": dup_rate,
        "missing_rate_per_column": missing,
        "target_column": target_col,
        "split": split_info,
        "license": args.license or "UNDECLARED",
    }
    if not args.license:
        v.append(("PARTIAL", "LICENSE_UNDECLARED",
                  "no --license given -> data usability unconfirmed"))
    return audit_block, v


def decide(violations):
    sev = {s for s, _, _ in violations}
    if "BLOCKED" in sev:
        return "BLOCKED"
    if "REJECT" in sev:
        return "REJECT"
    if "PARTIAL" in sev:
        return "PARTIAL"
    return "PASS"


MESSAGE = {
    "PASS": "data contract audit passed; dataset is usable for the downstream training step",
    "PARTIAL": "data contract audit passed with reservations; see violations",
    "REJECT": "data contract audit failed on a hard gate; re-split before proceeding",
    "BLOCKED": "cannot establish the data contract; required input is missing",
}


def main():
    ap = argparse.ArgumentParser(add_help=True)
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--demo", action="store_true", help="built-in clean MOF fixture")
    src.add_argument("--demo-leaky", action="store_true",
                     help="built-in fixture with duplicates, missing values and scaffold leakage")
    src.add_argument("--csv", help="path to a user CSV")
    ap.add_argument("--target", required=True, help="target property name, e.g. bulk_modulus")
    ap.add_argument("--unit", default="", help="target unit, e.g. GPa")
    ap.add_argument("--direction", choices=["max", "min"], default="max")
    ap.add_argument("--threshold", type=float, default=None,
                    help="reliability threshold for the target")
    ap.add_argument("--id-col", default="sample_id")
    ap.add_argument("--split-col", default="split")
    ap.add_argument("--scaffold-col", default="framework_family")
    ap.add_argument("--split-scheme", default="scaffold",
                    choices=["random", "scaffold", "time-based"])
    ap.add_argument("--min-samples", type=int, default=5)
    ap.add_argument("--max-duplicate-rate", type=float, default=0.01)
    ap.add_argument("--max-missing-rate", type=float, default=0.20)
    ap.add_argument("--license", default="", help="data license statement")
    ap.add_argument("--out", default="", help="write the JSON report to this path")
    args = ap.parse_args()

    text, source = read_rows(args)
    fields, rows = parse(text)
    if not fields:
        fail("PARSE_ERROR", "no CSV header detected")

    audit_block, violations = audit(fields, rows, args)
    decision = decide(violations)

    report = {
        "code": "OK",
        "message": MESSAGE[decision],
        "version": VERSION,
        "source": source,
        "task": "data-target-definition",
        "step": "s01",
        "decision": decision,
        "audit": audit_block if audit_block else {"n_total": len(rows)},
        "target_definition": {
            "property": args.target,
            "unit": args.unit or "UNDECLARED",
            "direction": args.direction,
            "reliable_threshold": args.threshold,
            "not_applicable_when": "target column missing or entirely null",
        },
        "violations": [
            {"severity": s, "code": c, "detail": d} for s, c, d in violations
        ],
    }

    text_out = json.dumps(report, ensure_ascii=False, indent=2)
    if args.out:
        try:
            with open(args.out, "w", encoding="utf-8") as fh:
                fh.write(text_out + "\n")
        except Exception as exc:
            fail("WRITE_ERROR", "cannot write %s: %s" % (args.out, exc))
        print("[info] report written -> %s" % os.path.abspath(args.out))
    print(text_out)
    return 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    sys.exit(main())
