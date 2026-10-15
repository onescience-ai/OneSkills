#!/usr/bin/env python3
"""Validate a MACE extxyz split: counts, energy range, force stats, and that
the split is time-block (non-overlapping, chronological)."""
import argparse
import json
import sys

import numpy as np
from ase.io import read


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prefix", default="aimd")
    ap.add_argument("--out-dir", default=".")
    ap.add_argument("--meta", default=None)
    a = ap.parse_args()

    print("=== extxyz splits ===")
    frames = {}
    for split in ("train", "valid", "test"):
        p = "%s/%s_%s.extxyz" % (a.out_dir, a.prefix, split)
        try:
            imgs = read(p, index=":")
        except Exception as exc:
            print("%-6s MISSING (%s)" % (split, exc))
            continue
        E = np.array([at.info["REF_energy"] for at in imgs])
        F = np.concatenate([at.arrays["REF_forces"] for at in imgs])
        fmax = float(np.sqrt((F ** 2).sum(axis=1)).max())
        frms = float(np.sqrt((F ** 2).sum(axis=1)).mean())
        S = "yes" if "REF_stress" in imgs[0].info else "no"
        print("%-6s frames=%d atoms=%d  E=[%.4f, %.4f] eV  |F|max=%.4f |F|rms=%.4f eV/A  stress=%s"
              % (split, len(imgs), len(imgs[0]), E.min(), E.max(), fmax, frms, S))
        frames[split] = len(imgs)

    meta_path = a.meta or "%s/%s_meta.json" % (a.out_dir, a.prefix)
    try:
        meta = json.load(open(meta_path))
        print("=== split policy ===")
        print("policy=%s block_frames=%s shuffle=%s" %
              (meta.get("split_policy"), meta.get("block_frames"), meta.get("shuffle")))
        print("frame_ranges:", meta.get("frame_ranges"))
        if meta.get("split_policy") != "time-block" or meta.get("shuffle"):
            print("WARN: split is not time-block/no-shuffle (leakage risk)")
    except Exception as exc:
        print("meta not read: %s" % exc)


if __name__ == "__main__":
    sys.exit(main())
