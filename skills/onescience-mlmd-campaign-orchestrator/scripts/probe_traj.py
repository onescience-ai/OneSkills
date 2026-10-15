#!/usr/bin/env python3
"""Probe a VASP MD trajectory to see what ASE can extract (energy/forces/stress)."""
import sys
import time

from ase.io import read

path = sys.argv[1]
t0 = time.time()
imgs = read(path, index=":")
print("file      :", path)
print("read time : %.1f s" % (time.time() - t0))
print("frames    :", len(imgs))
a0, aN = imgs[0], imgs[-1]
print("natoms    :", len(a0))
print("formula   :", a0.get_chemical_formula())
print("cell      :", a0.cell.array.round(4).tolist())
print("pbc       :", a0.pbc)
import numpy as np  # noqa: E402

for tag, a in (("first", a0), ("last", aN)):
    e = a.get_potential_energy()
    f = a.get_forces()
    fmax = float(np.sqrt((f ** 2).sum(axis=1)).max())
    try:
        s = a.get_stress()
        sdesc = "yes |sigma|max=%.4f" % float(abs(s).max())
    except Exception as exc:
        sdesc = "no (%s)" % type(exc).__name__
    print("%-5s E=%.6f eV  Fmax=%.4f eV/A  stress=%s" % (tag, e, fmax, sdesc))
