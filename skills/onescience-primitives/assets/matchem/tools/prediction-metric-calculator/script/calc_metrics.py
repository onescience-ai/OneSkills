#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""预测精度核算脚本（prediction-metric-calculator）。

仅依赖 Python 标准库（3.9+），用于 Task-Centric 链中
`prediction-accuracy-evaluation` 任务的 `run-metric-script` 操作。

输出统一为 JSON（stdout），成功 code=OK，失败 code 为具体错误码，
退出码 0 表示核算完成，2 表示输入或前置条件不满足。
"""

import argparse
import csv
import json
import math
import os
import random
import sys

VERSION = "1.0.0"
MIN_SAMPLES_DEFAULT = 5


def fail(code, message, exit_code=2):
    """输出失败 JSON 并退出。"""
    print(json.dumps({"code": code, "message": message, "version": VERSION},
                     ensure_ascii=False))
    sys.exit(exit_code)


def build_demo_rows():
    """生成内置样例数据：MOF CO2 吸附能预测值 vs 参考值。

    使用固定随机种子保证可复现，误差量级贴近 MLIP 精度声明（~0.03 eV）。
    """
    rng = random.Random(20260914)
    groups = ["MOF-74", "ZIF-8", "UiO-66", "Mg-MOF-74"]
    rows = []
    for i in range(24):
        ref = round(rng.uniform(-1.20, -0.25), 4)
        noise = rng.gauss(0.0, 0.028)
        pred = round(ref + noise, 4)
        rows.append({"pred": pred, "ref": ref, "group": groups[i % len(groups)]})
    return rows


def load_csv_rows(path, pred_col, ref_col, group_col):
    """读取 CSV，校验必需列并解析数值。"""
    if not os.path.isfile(path):
        fail("FILE_NOT_FOUND", "找不到输入文件: {}".format(path))
    rows = []
    with open(path, "r", encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        fields = reader.fieldnames or []
        for col in (pred_col, ref_col):
            if col not in fields:
                fail("MISSING_COLUMN",
                     "输入文件缺少必需列 '{}'，现有列: {}".format(col, fields))
        for lineno, raw in enumerate(reader, start=2):
            try:
                pred = float(raw[pred_col])
                ref = float(raw[ref_col])
            except (TypeError, ValueError):
                fail("PARSE_ERROR",
                     "第 {} 行数值解析失败（列 {} / {}）".format(lineno, pred_col, ref_col))
            if math.isnan(pred) or math.isnan(ref):
                continue
            row = {"pred": pred, "ref": ref}
            if group_col and group_col in fields:
                row["group"] = (raw.get(group_col) or "ungrouped").strip()
            rows.append(row)
    if group_col and group_col not in fields:
        sys.stderr.write(
            "[warn] 未找到分组列 '{}'，已降级为整体核算（未按体系分箱，可能掩盖子集失效）\n".format(group_col))
    return rows


def metrics(pairs):
    """核算 MAE / RMSE / R² / 最大绝对误差。"""
    n = len(pairs)
    errs = [p - r for p, r in pairs]
    abs_errs = [abs(e) for e in errs]
    mae = sum(abs_errs) / n
    rmse = math.sqrt(sum(e * e for e in errs) / n)
    max_abs = max(abs_errs)
    ref_mean = sum(r for _, r in pairs) / n
    ss_tot = sum((r - ref_mean) ** 2 for _, r in pairs)
    ss_res = sum(e * e for e in errs)
    if ss_tot == 0.0:
        return {"n": n, "mae": mae, "rmse": rmse, "max_abs_err": max_abs,
                "r2": None, "degraded": "ZERO_VARIANCE"}
    return {"n": n, "mae": mae, "rmse": rmse, "max_abs_err": max_abs,
            "r2": 1.0 - ss_res / ss_tot, "degraded": None}


def round_metrics(m):
    """统一保留 6 位小数，便于对比与复现。"""
    out = {"n": m["n"], "degraded": m["degraded"]}
    for key in ("mae", "rmse", "max_abs_err", "r2"):
        out[key] = None if m[key] is None else round(m[key], 6)
    return out


def judge(m, mae_max, r2_min):
    """按阈值判定通过与否；阈值缺省或指标不可用时返回 None。"""
    if mae_max is None and r2_min is None:
        return None
    ok = True
    if mae_max is not None and not (m["mae"] <= mae_max):
        ok = False
    if r2_min is not None:
        if m["r2"] is None:
            return None
        if not (m["r2"] >= r2_min):
            ok = False
    return ok


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="核算预测值与参考值的 MAE/RMSE/R²，输出 JSON 报告")
    src = parser.add_mutually_exclusive_group(required=True)
    src.add_argument("--demo", action="store_true",
                     help="使用内置可复现样例数据（MOF CO2 吸附能）")
    src.add_argument("--csv", metavar="PATH", help="输入 CSV 路径")
    parser.add_argument("--pred-col", default="pred", help="预测值列名，默认 pred")
    parser.add_argument("--ref-col", default="ref", help="参考值列名，默认 ref")
    parser.add_argument("--group-col", default="group",
                        help="分组列名，默认 group；缺列时自动降级为整体核算")
    parser.add_argument("--no-group", action="store_true", help="禁用分箱核算")
    parser.add_argument("--mae-max", type=float, default=None, help="MAE 上限阈值")
    parser.add_argument("--r2-min", type=float, default=None, help="R² 下限阈值")
    parser.add_argument("--min-samples", type=int, default=MIN_SAMPLES_DEFAULT,
                        help="最小样本数，默认 5")
    parser.add_argument("--out", metavar="PATH", default=None, help="报告写出路径")
    args = parser.parse_args(argv)

    if args.demo:
        rows = build_demo_rows()
        source = "demo"
    else:
        rows = load_csv_rows(args.csv, args.pred_col, args.ref_col,
                             None if args.no_group else args.group_col)
        source = args.csv

    if len(rows) < args.min_samples:
        fail("INSUFFICIENT_SAMPLES",
             "有效样本 {} 少于最小要求 {}".format(len(rows), args.min_samples))

    pairs = [(r["pred"], r["ref"]) for r in rows]
    overall = round_metrics(metrics(pairs))

    per_group = None
    if not args.no_group and any("group" in r for r in rows):
        buckets = {}
        for r in rows:
            buckets.setdefault(r.get("group", "ungrouped"), []).append((r["pred"], r["ref"]))
        per_group = {}
        for name in sorted(buckets):
            if len(buckets[name]) >= 2:
                per_group[name] = round_metrics(metrics(buckets[name]))
            else:
                per_group[name] = {"n": len(buckets[name]), "skipped": "TOO_FEW_SAMPLES"}

    passed = judge(overall, args.mae_max, args.r2_min)
    message = "指标核算完成"
    if passed is None:
        message += "；未给定阈值或指标不可用，仅报指标不下结论"
    elif passed:
        message += "；满足给定阈值"
    else:
        message += "；未满足给定阈值"
    if overall.get("degraded") == "ZERO_VARIANCE":
        message += "；参考值方差为零，R² 不可定义"

    report = {
        "code": "OK",
        "message": message,
        "version": VERSION,
        "source": source,
        "method": "binned-metric-evaluation" if per_group else "global-metric-evaluation",
        "thresholds": {"mae_max": args.mae_max, "r2_min": args.r2_min,
                       "min_samples": args.min_samples},
        "passed": passed,
        "metrics": overall,
        "per_group": per_group,
    }
    text = json.dumps(report, ensure_ascii=False, indent=2)
    if args.out:
        out_dir = os.path.dirname(os.path.abspath(args.out))
        if out_dir and not os.path.isdir(out_dir):
            os.makedirs(out_dir, exist_ok=True)
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(text + "\n")
        sys.stderr.write("[info] 报告已写出: {}\n".format(os.path.abspath(args.out)))
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
