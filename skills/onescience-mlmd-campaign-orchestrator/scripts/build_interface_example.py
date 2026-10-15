#!/usr/bin/env python3
"""Build the initial model: CO2 + K + explicit H2O film on Cu(111).

Geometry conventions (all in Angstrom):
  * Cu fcc a = 3.615, 4x4x4 slab, interlayer d111 = 2.087
  * water film: 2 quasi-planar layers of 9 molecules (liquid-like density on 90.5 A^2)
  * CO2 physisorbed flat at the metal/water interface (in a water vacancy)
  * K sitting in a first-shell water vacancy (hydration shell)
  * bottom 2 Cu layers fixed (F F F)
Coordinate system: z along surface normal, bottom Cu layer at z = 0.
"""

import sys
import math
from ase.build import fcc111
import numpy as np

SKILL = ".opencode/skills/onescience-dft-model-gate/scripts"
sys.path.insert(0, SKILL)
from hbond_pack import pack_solvent, WATER, hex_sites  # noqa: E402

A_CU = 3.615
N_LAYER_WATER = 9          # molecules per water layer
Z_LOW = 3.60               # lower water O plane, above top Cu layer
Z_UP = 6.40                # upper water O plane
DZ_CO2 = 3.45              # CO2 carbon height above top Cu layer
CO2_CO = 1.16
OH = 0.96
HOH = 104.5
VACUUM = 18.0


def build_slab():
    slab = fcc111("Cu", size=(4, 4, 4), a=A_CU, vacuum=0.0)
    pos = np.array(slab.get_positions())
    cell = np.array(slab.cell)
    zmin = pos[:, 2].min()
    pos[:, 2] -= zmin
    return cell.tolist(), pos.tolist()


def frac_to_cart2(cell, f):
    return [f[0] * cell[0][0] + f[1] * cell[1][0],
            f[0] * cell[0][1] + f[1] * cell[1][1]]


def _to_frac_xy(cell, xy):
    ax, ay = cell[0][:2], cell[1][:2]
    det = ax[0] * ay[1] - ax[1] * ay[0]
    return [(ay[1] * xy[0] - ay[0] * xy[1]) / det,
            (-ax[1] * xy[0] + ax[0] * xy[1]) / det]


def mindist_xy(cell, a, b):
    fa, fb = _to_frac_xy(cell, a), _to_frac_xy(cell, b)
    df = [fa[0] - fb[0], fa[1] - fb[1]]
    df = [df[0] - round(df[0]), df[1] - round(df[1])]
    c = frac_to_cart2(cell, df)
    return math.hypot(c[0], c[1])


def main():
    cell, cu = build_slab()
    zsurf = max(p[2] for p in cu)

    # ---- in-plane layout ---------------------------------------------------
    # A tall cell is mandatory for the packer: with the raw slab c (~6.3 A) the
    # fractional-z minimum image would wrap water back onto the bottom Cu layers.
    pack_cell = [cell[0], cell[1], [0.0, 0.0, 60.0]]

    # lower water layer: CO2 and K occupy two of its sites (far apart so the K
    # hydration shell is not squeezed against the adsorbate)
    lower_all = hex_sites(cell, N_LAYER_WATER, seed_xy=(0.5, 0.5))
    upper_sites = hex_sites(cell, N_LAYER_WATER, seed_xy=(0.25, 0.75))
    co2_xy = lower_all[0]
    k_xy = max(lower_all, key=lambda s: mindist_xy(cell, s, co2_xy))
    lower_water = [s for s in lower_all if s != co2_xy and s != k_xy]

    # ---- CO2 (flat, O-C-O along x) ----------------------------------------
    zc = zsurf + DZ_CO2
    co2 = [("C", (co2_xy[0], co2_xy[1], zc)),
           ("O", (co2_xy[0] + CO2_CO, co2_xy[1], zc)),
           ("O", (co2_xy[0] - CO2_CO, co2_xy[1], zc))]
    # ---- K ----------------------------------------------------------------
    zk = zsurf + Z_LOW
    k_atom = [("K", (k_xy[0], k_xy[1], zk))]

    # ---- water sites -------------------------------------------------------
    sites = [(x, y, zsurf + Z_LOW) for (x, y) in lower_water]
    sites += [(x, y, zsurf + Z_UP) for (x, y) in upper_sites]
    n_water = len(sites)
    print("water molecules: %d (lower %d + upper %d)" % (n_water, len(lower_water), len(upper_sites)))

    # ---- H orientation search ---------------------------------------------
    # only the top two Cu layers matter for the solvent/solute (they sit ~9 A up)
    cu_near = [p for p in cu if p[2] > zsurf - 2.5]
    existing = [("Cu", p) for p in cu_near] + [("C", co2[0][1]), ("O", co2[1][1]),
                                               ("O", co2[2][1])] + [("K", k_atom[0][1])]
    mols = pack_solvent(pack_cell, sites, WATER, existing=existing,
                        passes=3, n_random=180, seed=0, log=lambda m: print("  pack " + m))

    water_atoms = []
    for m in mols:
        water_atoms.append(("O", m["central"]))
        for h in m["H"]:
            water_atoms.append(("H", h))

    # ---- assemble ----------------------------------------------------------
    atoms = [("Cu", p) for p in cu] + k_atom + co2 + water_atoms
    # reorder per element: Cu, K, C, O, H
    order = ["Cu", "K", "C", "O", "H"]
    grouped = []
    for el in order:
        grouped += [a for a in atoms if a[0] == el]

    zmax = max(p[2] for _, p in grouped)
    c_len = zmax + VACUUM
    cell3 = [cell[0], cell[1], [0.0, 0.0, c_len]]

    # fractional coords
    A = np.array(cell3)
    def to_frac(p):
        return np.linalg.solve(A.T, np.array(p))

    counts = {el: sum(1 for a in grouped if a[0] == el) for el in order}
    lines = ["CO2 + K + H2O on Cu(111) initial model",
             "1.0"]
    for v in cell3:
        lines.append("  %.10f %.10f %.10f" % tuple(v))
    lines.append(" ".join(order))
    lines.append(" ".join(str(counts[el]) for el in order))
    lines.append("Selective dynamics")
    lines.append("Direct")
    zfix = sorted(set(round(p[2], 3) for p in cu))[:2]
    for el, p in grouped:
        f = to_frac(p)
        if el == "Cu" and round(p[2], 3) in zfix:
            flag = "F F F"
        else:
            flag = "T T T"
        lines.append("  %.10f %.10f %.10f %s" % (f[0], f[1], f[2], flag))

    with open("structures/POSCAR", "w") as fh:
        fh.write("\n".join(lines) + "\n")
    print("wrote structures/POSCAR  natoms=%d counts=%s c=%.3f vacuum=%.2f"
          % (len(grouped), counts, c_len, c_len - zmax))


if __name__ == "__main__":
    main()
