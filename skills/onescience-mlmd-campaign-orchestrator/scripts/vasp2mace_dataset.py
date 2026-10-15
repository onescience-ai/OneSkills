#!/usr/bin/env python3
"""Convert a VASP MD trajectory (vasprun.xml) into MACE-ready extxyz datasets.

Reads every ionic step (energy E0, forces, stress) with ASE and writes MACE's
REF_* key convention, then splits train/valid/test either randomly or by
TIME-BLOCK (contiguous blocks, no shuffling -> no leakage between neighbours).

  python vasp2mace_dataset.py --traj <vasprun.xml> --out-dir <dir> \
      --prefix aimd --split-policy time-block --block-frames 100
"""
import argparse
import json
import os
import random
import time

from ase.io import read, write


def split_random(n, valid_frac, test_frac, seed):
    idx = list(range(n))
    random.Random(seed).shuffle(idx)
    nva = int(round(n * valid_frac))
    nte = int(round(n * test_frac))
    return (sorted(idx[nva + nte:]), sorted(idx[:nva]), sorted(idx[nva:nva + nte]))


def split_time_block(n, block, valid_frac, test_frac):
    """Contiguous blocks, chronological assignment, no shuffling."""
    nb = n // block
    if nb < 3:
        # too few blocks to make three sets; fall back to contiguous cut points
        nte = int(n * test_frac)
        nva = int(n * valid_frac)
        cut1, cut2 = n - nte - nva, n - nte
        return list(range(0, cut1)), list(range(cut1, cut2)), list(range(cut2, n))
    nte_b = max(1, int(round(nb * test_frac)))
    nva_b = max(1, int(round(nb * valid_frac)))
    ntr_b = nb - nva_b - nte_b
    tr = [b for b in range(ntr_b)]
    va = [b for b in range(ntr_b, ntr_b + nva_b)]
    te = [b for b in range(ntr_b + nva_b, nb)]
    to_frames = lambda bs: [f for b in bs for f in range(b * block, (b + 1) * block) if f < n]
    return to_frames(tr), to_frames(va), to_frames(te)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--traj", required=True, help="vasprun.xml of the MD run")
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--prefix", default="aimd")
    ap.add_argument("--stride", type=int, default=1)
    ap.add_argument("--skip", type=int, default=0)
    ap.add_argument("--split-policy", choices=["time-block", "random"], default="time-block")
    ap.add_argument("--block-frames", type=int, default=100)
    ap.add_argument("--valid-frac", type=float, default=0.1)
    ap.add_argument("--test-frac", type=float, default=0.1)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--no-stress", action="store_true")
    a = ap.parse_args()

    os.makedirs(a.out_dir, exist_ok=True)

    t0 = time.time()
    imgs = read(a.traj, index=":")
    print("read %d frames in %.1f s" % (len(imgs), time.time() - t0))
    imgs = imgs[a.skip::a.stride]

    # Re-key to MACE/onescience REF_* convention (plain energy -> None via get_potential_energy)
    for at in imgs:
        e = at.get_potential_energy()
        f = at.get_forces()
        s = None if a.no_stress else at.get_stress()
        at.info["REF_energy"] = float(e)
        at.arrays["REF_forces"] = f
        if s is not None:
            at.info["REF_stress"] = s
        for k in ("energy", "free_energy", "stress", "move_mask"):
            at.info.pop(k, None)
        for k in ("forces", "move_mask"):
            at.arrays.pop(k, None)
        at.calc = None
    n = len(imgs)
    print("selected %d frames (skip=%d stride=%d)" % (n, a.skip, a.stride))

    if a.split_policy == "random":
        tr, va, te = split_random(n, a.valid_frac, a.test_frac, a.seed)
    else:
        tr, va, te = split_time_block(n, a.block_frames, a.valid_frac, a.test_frac)

    full = os.path.join(a.out_dir, "%s.extxyz" % a.prefix)
    write(full, imgs, format="extxyz")
    paths = {}
    for name, sel in (("train", tr), ("valid", va), ("test", te)):
        p = os.path.join(a.out_dir, "%s_%s.extxyz" % (a.prefix, name))
        write(p, [imgs[i] for i in sel], format="extxyz")
        paths[name] = p

    def rng(idx):
        return [idx[0], idx[-1]] if idx else None

    meta = {
        "source_traj": os.path.abspath(a.traj),
        "out_dir": os.path.abspath(a.out_dir),
        "prefix": a.prefix,
        "stride": a.stride,
        "skip": a.skip,
        "split_policy": a.split_policy,
        "block_frames": a.block_frames if a.split_policy == "time-block" else None,
        "shuffle": (a.split_policy == "random"),
        "valid_frac": a.valid_frac,
        "test_frac": a.test_frac,
        "seed": a.seed,
        "include_stress": not a.no_stress,
        "n_total": n,
        "n_train": len(tr),
        "n_valid": len(va),
        "n_test": len(te),
        "frame_ranges": {"train": rng(tr), "valid": rng(va), "test": rng(te)},
        "n_atoms": len(imgs[0]),
        "formula": imgs[0].get_chemical_formula(),
        "cell": imgs[0].cell.array.tolist(),
        "energy_min_eV": min(at.info["REF_energy"] for at in imgs),
        "energy_max_eV": max(at.info["REF_energy"] for at in imgs),
    }
    meta_path = os.path.join(a.out_dir, "%s_meta.json" % a.prefix)
    with open(meta_path, "w") as fh:
        json.dump(meta, fh, indent=2)
    print(json.dumps(meta, indent=2))
    for p in [full, *paths.values(), meta_path]:
        print("wrote %s  (%.1f MB)" % (p, os.path.getsize(p) / 1e6))


if __name__ == "__main__":
    main()
