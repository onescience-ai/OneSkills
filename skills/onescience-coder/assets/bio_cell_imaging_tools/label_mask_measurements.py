#!/usr/bin/env python3
"""Summarize a simple 2D integer label mask stored as CSV/TSV."""

from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict


def read_grid(path: str, delimiter: str) -> list[list[int]]:
    grid = []
    with open(path, newline="", encoding="utf-8-sig") as handle:
        for row in csv.reader(handle, delimiter=delimiter):
            if row:
                grid.append([int(float(value)) for value in row])
    return grid


def main() -> int:
    parser = argparse.ArgumentParser(description="Measure label areas and centroids from a mask grid.")
    parser.add_argument("mask_table")
    parser.add_argument("--delimiter", default=",")
    args = parser.parse_args()

    grid = read_grid(args.mask_table, args.delimiter)
    pixels = defaultdict(list)
    for y, row in enumerate(grid):
        for x, label in enumerate(row):
            if label > 0:
                pixels[label].append((x, y))
    objects = []
    for label, coords in sorted(pixels.items()):
        xs = [x for x, _ in coords]
        ys = [y for _, y in coords]
        objects.append({
            "label": label,
            "area_px": len(coords),
            "centroid_x": sum(xs) / len(xs),
            "centroid_y": sum(ys) / len(ys),
            "bbox": [min(xs), min(ys), max(xs), max(ys)],
        })
    print(json.dumps({"object_count": len(objects), "objects": objects}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
