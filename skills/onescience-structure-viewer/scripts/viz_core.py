"""Core helpers for onescience-structure-viewer.

Pure stdlib (no numpy / no ASE). Parses POSCAR / XYZ into an internal
Structure, detects bonds with periodic minimum-image convention, unwraps
molecules that straddle the cell boundary so they render intact, and
produces the JSON payload consumed by assets/viewer_template.html.

Everything here is deterministic: same input file -> same payload.
"""

from __future__ import annotations

import json
import math
import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

# ---------------------------------------------------------------------------
# Element data (kept small on purpose; extend as needed)
# ---------------------------------------------------------------------------

# Cordero 2008 covalent radii (Angstrom)
COVALENT_RADII: Dict[str, float] = {
    "H": 0.31, "He": 0.28, "Li": 1.28, "Be": 0.96, "B": 0.84, "C": 0.76,
    "N": 0.71, "O": 0.66, "F": 0.57, "Ne": 0.58, "Na": 1.66, "Mg": 1.41,
    "Al": 1.21, "Si": 1.11, "P": 1.07, "S": 1.05, "Cl": 1.02, "Ar": 1.06,
    "K": 2.03, "Ca": 1.76, "Sc": 1.70, "Ti": 1.60, "V": 1.53, "Cr": 1.39,
    "Mn": 1.39, "Fe": 1.32, "Co": 1.26, "Ni": 1.24, "Cu": 1.32, "Zn": 1.22,
    "Ga": 1.22, "Ge": 1.20, "As": 1.19, "Se": 1.20, "Br": 1.20, "Kr": 1.16,
    "Rb": 2.20, "Sr": 1.95, "Y": 1.90, "Zr": 1.75, "Nb": 1.64, "Mo": 1.54,
    "Tc": 1.47, "Ru": 1.46, "Rh": 1.42, "Pd": 1.39, "Ag": 1.45, "Cd": 1.44,
    "In": 1.42, "Sn": 1.39, "Sb": 1.39, "Te": 1.38, "I": 1.39, "Xe": 1.40,
    "Cs": 2.44, "Ba": 2.15, "La": 2.07, "Ce": 2.04, "Pr": 2.03, "Nd": 2.01,
    "Pt": 1.36, "Au": 1.36, "Hg": 1.32, "Tl": 1.45, "Pb": 1.46, "Bi": 1.48,
    "W": 1.62, "Re": 1.51, "Os": 1.44, "Ir": 1.41, "Ta": 1.70, "Hf": 1.75,
    "Gd": 1.96, "U": 1.96,
}

# Jmol / CPK-ish default colors (hex). Viewer may override via colorscheme.
DEFAULT_COLORS: Dict[str, str] = {
    "H":  "#ffffff", "C":  "#909090", "N":  "#3050f8", "O":  "#ff2020",
    "F":  "#90e050", "Na": "#ab5cf2", "Mg": "#8aff00", "Al": "#bfa6a6",
    "Si": "#f0c8a0", "P":  "#ff8000", "S":  "#ffff30", "Cl": "#1ff01f",
    "K":  "#8f40d4", "Ca": "#3dff00", "Ti": "#bfc2c7", "V":  "#a6a6ab",
    "Cr": "#8a99c7", "Mn": "#9c7ac7", "Fe": "#e06633", "Co": "#f090a0",
    "Ni": "#50d050", "Cu": "#c88033", "Zn": "#7d80b0", "Ga": "#c28f8f",
    "Ge": "#668f8f", "As": "#bd80e3", "Se": "#ffa100", "Br": "#a62929",
    "Sr": "#00ff00", "Y":  "#94ffff", "Zr": "#94e0e0", "Nb": "#73c2c9",
    "Mo": "#54b5b5", "Ru": "#248f8f", "Rh": "#0a7d8c", "Pd": "#006985",
    "Ag": "#c0c0c0", "Cd": "#ffd98f", "Sn": "#668080", "Sb": "#9e63b5",
    "Te": "#d47a00", "I":  "#940094", "Cs": "#57178f", "Ba": "#00c900",
    "La": "#70d4ff", "Ce": "#ffffc7", "Pt": "#d0d0e0", "Au": "#ffd123",
    "Hg": "#b8b8d0", "Pb": "#575961", "Bi": "#9e4fb5", "W":  "#2194d6",
    "Re": "#267dab", "Ir": "#175487", "Os": "#266696", "Ta": "#4da6ff",
    "Hf": "#4dc2ff", "N":  "#3050f8",
}

# Visual sphere radius for ball-and-stick rendering (Angstrom, not physical).
DISPLAY_RADII: Dict[str, float] = {
    "H": 0.30, "C": 0.55, "N": 0.55, "O": 0.55, "F": 0.55,
    "Na": 0.90, "Mg": 0.85, "Al": 0.85, "Si": 0.75, "P": 0.75, "S": 0.75,
    "Cl": 0.75, "K": 1.15, "Ca": 1.00, "Ti": 0.85, "V": 0.85, "Cr": 0.85,
    "Mn": 0.85, "Fe": 0.80, "Co": 0.80, "Ni": 0.80, "Cu": 0.85, "Zn": 0.85,
    "Ag": 0.95, "Pt": 0.90, "Au": 0.90, "Pd": 0.90, "Ru": 0.85, "Rh": 0.85,
    "Ir": 0.85, "Cs": 1.30, "Ba": 1.15, "La": 1.10, "Ce": 1.10, "W": 0.85,
    "Mo": 0.85, "Ta": 0.85, "Nb": 0.85, "Zr": 0.85, "Hf": 0.85,
}

# Metallic / ionic species that should NOT form covalent-bond cylinders with
# each other in the viewer (a slab would become an unreadable hairball).
METALS = {
    "Li", "Na", "K", "Rb", "Cs", "Be", "Mg", "Ca", "Sr", "Ba",
    "Sc", "Y", "La", "Ce", "Pr", "Nd", "Gd",
    "Ti", "Zr", "Hf", "V", "Nb", "Ta", "Cr", "Mo", "W", "Mn", "Re",
    "Fe", "Ru", "Os", "Co", "Rh", "Ir", "Ni", "Pd", "Pt",
    "Cu", "Ag", "Au", "Zn", "Cd", "Hg", "Al", "Ga", "In", "Sn", "Pb", "Bi",
    "U",
}


# ---------------------------------------------------------------------------
# Structure container
# ---------------------------------------------------------------------------

class Atom:
    __slots__ = ("el", "xyz", "fixed", "tag", "group")

    def __init__(self, el: str, xyz: Sequence[float],
                 fixed: bool = False, tag: str = "", group: str = ""):
        self.el = el
        self.xyz = [float(xyz[0]), float(xyz[1]), float(xyz[2])]
        self.fixed = bool(fixed)
        self.tag = tag or ""
        self.group = group or ""   # role: slab / solvent / adsorbate / ion / molecule

    def to_dict(self) -> dict:
        return {
            "el": self.el,
            "xyz": [round(v, 6) for v in self.xyz],
            "fixed": self.fixed,
            "tag": self.tag,
            "group": self.group,
        }


class Structure:
    """Minimal periodic structure container."""

    def __init__(self,
                 cell: Sequence[Sequence[float]],
                 comment: str = "",
                 selective_dynamics: bool = False):
        self.cell = [[float(v) for v in row] for row in cell]
        if len(self.cell) != 3 or any(len(r) != 3 for r in self.cell):
            raise ValueError("cell must be 3x3")
        self.comment = comment or "structure"
        self.selective_dynamics = selective_dynamics
        self.atoms: List[Atom] = []

    def add(self, el: str, xyz: Sequence[float],
            fixed: bool = False, tag: str = "", group: str = "") -> Atom:
        a = Atom(el, xyz, fixed=fixed, tag=tag, group=group)
        self.atoms.append(a)
        return a

    # -- derived ------------------------------------------------------------
    def composition(self) -> Dict[str, int]:
        out: Dict[str, int] = {}
        for a in self.atoms:
            out[a.el] = out.get(a.el, 0) + 1
        return out

    def formula(self) -> str:
        comp = self.composition()
        return "".join(k if v == 1 else f"{k}{v}" for k, v in sorted(comp.items()))

    def cell_lengths(self) -> Tuple[float, float, float]:
        return tuple(math.sqrt(sum(v * v for v in row)) for row in self.cell)  # type: ignore

    def cell_angles(self) -> Tuple[float, float, float]:
        a, b, c = self.cell
        def dot(u, v): return sum(u[i] * v[i] for i in range(3))
        def norm(u): return math.sqrt(dot(u, u))
        alpha = math.degrees(math.acos(max(-1, min(1, dot(b, c) / (norm(b) * norm(c))))))
        beta  = math.degrees(math.acos(max(-1, min(1, dot(a, c) / (norm(a) * norm(c))))))
        gamma = math.degrees(math.acos(max(-1, min(1, dot(a, b) / (norm(a) * norm(b))))))
        return alpha, beta, gamma

    def volume(self) -> float:
        a, b, c = self.cell
        return abs(a[0] * (b[1] * c[2] - b[2] * c[1])
                   - a[1] * (b[0] * c[2] - b[2] * c[0])
                   + a[2] * (b[0] * c[1] - b[1] * c[0]))

    def inverse_cell(self) -> List[List[float]]:
        m = self.cell
        d = (m[0][0] * (m[1][1] * m[2][2] - m[1][2] * m[2][1])
             - m[0][1] * (m[1][0] * m[2][2] - m[1][2] * m[2][0])
             + m[0][2] * (m[1][0] * m[2][1] - m[1][1] * m[2][0]))
        if abs(d) < 1e-12:
            raise ValueError("singular cell")
        return [
            [(m[1][1] * m[2][2] - m[1][2] * m[2][1]) / d,
             (m[0][2] * m[2][1] - m[0][1] * m[2][2]) / d,
             (m[0][1] * m[1][2] - m[0][2] * m[1][1]) / d],
            [(m[1][2] * m[2][0] - m[1][0] * m[2][2]) / d,
             (m[0][0] * m[2][2] - m[0][2] * m[2][0]) / d,
             (m[0][2] * m[1][0] - m[0][0] * m[1][2]) / d],
            [(m[1][0] * m[2][1] - m[1][1] * m[2][0]) / d,
             (m[0][1] * m[2][0] - m[0][0] * m[2][1]) / d,
             (m[0][0] * m[1][1] - m[0][1] * m[1][0]) / d],
        ]

    def to_frac(self, xyz: Sequence[float]) -> List[float]:
        inv = getattr(self, "_inv", None)
        if inv is None:
            inv = self.inverse_cell()
            self._inv = inv
        return [sum(xyz[d] * inv[d][k] for d in range(3)) for k in range(3)]

    def to_cart(self, frac: Sequence[float]) -> List[float]:
        return [sum(frac[k] * self.cell[k][m] for k in range(3)) for m in range(3)]


# ---------------------------------------------------------------------------
# Parsers
# ---------------------------------------------------------------------------

_P_LINE = re.compile(r"^\s*([+-]?\d*\.?\d+(?:[eE][+-]?\d+)?)\s+"
                     r"([+-]?\d*\.?\d+(?:[eE][+-]?\d+)?)\s+"
                     r"([+-]?\d*\.?\d+(?:[eE][+-]?\d+)?)\s*(.*)$")


def parse_poscar(path: str | os.PathLike) -> Structure:
    """Parse VASP POSCAR/CONTCAR (v4 or v5, Direct or Cartesian, Angstrom)."""
    text = Path(path).read_text(encoding="utf-8")
    lines = text.splitlines()
    if len(lines) < 8:
        raise ValueError("POSCAR too short: %s" % path)

    comment = lines[0].strip()
    scale = float(lines[1].strip())
    cell_raw = [[float(x) for x in lines[2 + i].split()[:3]] for i in range(3)]
    if scale < 0:
        # negative scale = target volume; extremely rare, skip support
        raise ValueError("negative POSCAR scale (volume mode) not supported")
    cell = [[v * scale for v in row] for row in cell_raw]

    tok5 = lines[5].split()
    if all(re.fullmatch(r"[+-]?\d+", t) for t in tok5):
        # v4 style: no element line
        elements = None
        counts = [int(t) for t in tok5]
        i = 6
    else:
        elements = tok5
        counts = [int(x) for x in lines[6].split()]
        i = 7

    selective = False
    if i < len(lines) and lines[i].strip().lower().startswith(("s", "selective")):
        selective = True
        i += 1
    mode_line = lines[i].strip().lower()
    if not mode_line:
        i += 1
        mode_line = lines[i].strip().lower()
    direct = mode_line.startswith(("d", "f"))  # Direct or Fractional
    i += 1

    order: List[str] = elements or [f"X{k+1}" for k in range(len(counts))]
    struct = Structure(cell, comment=comment, selective_dynamics=selective)
    for el, n in zip(order, counts):
        for _ in range(n):
            m = _P_LINE.match(lines[i])
            if not m:
                raise ValueError("bad POSCAR coordinate line %d: %r" % (i + 1, lines[i]))
            v = [float(m.group(1)), float(m.group(2)), float(m.group(3))]
            tail = m.group(4).strip()
            fixed = False
            if selective and tail:
                flags = tail.split()[:3]
                if flags and flags[0].upper().startswith("F"):
                    fixed = True
            if direct:
                cart = struct.to_cart(v)
            else:
                # Cartesian; scale was already applied to cell, but VASP also
                # multiplies cartesian coords by scale
                cart = [x * scale for x in v]
            struct.add(el, cart, fixed=fixed)
            i += 1
    return struct


def parse_xyz(path: str | os.PathLike) -> Structure:
    """Parse plain XYZ. No cell -> a large cubic box is inferred so the viewer
    can still frame the molecule."""
    text = Path(path).read_text(encoding="utf-8")
    lines = text.splitlines()
    n = int(lines[0].strip())
    comment = lines[1].strip() if len(lines) > 1 else ""
    struct = Structure([[100.0, 0, 0], [0, 100.0, 0], [0, 0, 100.0]],
                       comment=comment, selective_dynamics=False)
    struct._no_cell = True  # type: ignore[attr-defined]
    for k in range(n):
        parts = lines[2 + k].split()
        el = parts[0]
        xyz = [float(parts[1]), float(parts[2]), float(parts[3])]
        tag = " ".join(parts[4:]) if len(parts) > 4 else ""
        struct.add(el, xyz, tag=tag)
    # Reshape cell to bound the molecule so the viewer can draw a wireframe
    xs = [a.xyz[0] for a in struct.atoms]
    ys = [a.xyz[1] for a in struct.atoms]
    zs = [a.xyz[2] for a in struct.atoms]
    if xs and ys and zs:
        pad = 5.0
        lx = max(xs) - min(xs) + 2 * pad
        ly = max(ys) - min(ys) + 2 * pad
        lz = max(zs) - min(zs) + 2 * pad
        struct.cell = [[lx, 0, 0], [0, ly, 0], [0, 0, lz]]
        # recenter atoms so the cell origin sits at the corner of the bounding box
        ox, oy, oz = min(xs) - pad, min(ys) - pad, min(zs) - pad
        for a in struct.atoms:
            a.xyz = [a.xyz[0] - ox, a.xyz[1] - oy, a.xyz[2] - oz]
    return struct


def load_structure(path: str | os.PathLike) -> Structure:
    p = Path(path)
    suffix = p.suffix.lower()
    if suffix in (".xyz",):
        return parse_xyz(p)
    if suffix in (".poscar", ".vasp", ".contcar"):
        return parse_poscar(p)
    # Sniff: vasp POSCAR line 2 is a single float, XYZ line 1 is an int
    first = p.read_text(encoding="utf-8").splitlines()
    if len(first) >= 2:
        try:
            int(first[0].strip())
            return parse_xyz(p)
        except ValueError:
            pass
        try:
            float(first[1].strip())
            return parse_poscar(p)
        except ValueError:
            pass
    raise ValueError("unrecognized structure format: %s" % p)


# ---------------------------------------------------------------------------
# Geometry helpers
# ---------------------------------------------------------------------------

def _min_image_frac(df: Sequence[float]) -> List[float]:
    return [x - round(x) for x in df]


def _min_image_vec(struct: Structure, dr_cart: Sequence[float]) -> List[float]:
    """Return dr adjusted by the shortest lattice translation."""
    f = struct.to_frac(dr_cart)
    f = _min_image_frac(f)
    return struct.to_cart(f)


def minimum_image_distance(struct: Structure,
                           p: Sequence[float], q: Sequence[float]) -> float:
    dr = [p[i] - q[i] for i in range(3)]
    dr = _min_image_vec(struct, dr)
    return math.sqrt(sum(v * v for v in dr))


# ---------------------------------------------------------------------------
# Bond detection
# ---------------------------------------------------------------------------

def detect_bonds(struct: Structure,
                 tol: float = 0.45,
                 max_len: float = 2.6,
                 skip_metal_metal: bool = True,
                 ) -> List[Tuple[int, int, float]]:
    """Return list of (i, j, distance) for covalent-looking bonds.

    Uses the Cordero covalent-radius sum + tol criterion, with periodic
    minimum-image distances. Metal-metal pairs are skipped by default so a
    slab doesn't render as an unreadable wire hairball.
    """
    n = len(struct.atoms)
    radii = [COVALENT_RADII.get(a.el, 1.0) for a in struct.atoms]
    has_cell = not getattr(struct, "_no_cell", False)
    out: List[Tuple[int, int, float]] = []

    # For large systems, bucket atoms into a coarse grid to keep O(N^2) down.
    # Threshold picked so typical slabs (<=2000 atoms) still use the direct path.
    if n > 1500 and has_cell:
        return _detect_bonds_bucketed(struct, tol, max_len, skip_metal_metal)

    for i in range(n):
        ai = struct.atoms[i]
        for j in range(i + 1, n):
            aj = struct.atoms[j]
            if skip_metal_metal and ai.el in METALS and aj.el in METALS:
                continue
            cutoff = radii[i] + radii[j] + tol
            if cutoff > max_len:
                cutoff = max_len
            dr = [ai.xyz[k] - aj.xyz[k] for k in range(3)]
            if has_cell:
                dr = _min_image_vec(struct, dr)
            d = math.sqrt(sum(v * v for v in dr))
            if d <= cutoff and d > 0.35:  # skip overlapping / duplicate atoms
                out.append((i, j, d))
    return out


def _detect_bounds_bucketed(struct: Structure, tol: float, max_len: float,
                            skip_metal_metal: bool) -> List[Tuple[int, int, float]]:
    """Cell-list accelerated bond detection for large systems."""
    n = len(struct.atoms)
    cell_len = [math.sqrt(sum(v * v for v in row)) for row in struct.cell]
    bin_size = max(max_len, 1.0)
    nb = [max(1, int(math.ceil(L / bin_size))) for L in cell_len]
    inv = struct.inverse_cell()

    buckets: Dict[Tuple[int, int, int], List[int]] = {}
    fracs = []
    for i, a in enumerate(struct.atoms):
        f = struct.to_frac(a.xyz)
        fracs.append(f)
        key = (int(f[0] * nb[0]) % nb[0],
               int(f[1] * nb[1]) % nb[1],
               int(f[2] * nb[2]) % nb[2])
        buckets.setdefault(key, []).append(i)

    radii = [COVALENT_RADII.get(a.el, 1.0) for a in struct.atoms]
    out: List[Tuple[int, int, float]] = []
    seen = set()

    def neighbors(key):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                for dz in (-1, 0, 1):
                    yield ((key[0] + dx) % nb[0],
                           (key[1] + dy) % nb[1],
                           (key[2] + dz) % nb[2])

    for key, idxs in buckets.items():
        for i in idxs:
            ai = struct.atoms[i]
            for nk in neighbors(key):
                for j in buckets.get(nk, ()):  # type: ignore[arg-type]
                    if j <= i:
                        continue
                    if (i, j) in seen:
                        continue
                    aj = struct.atoms[j]
                    if skip_metal_metal and ai.el in METALS and aj.el in METALS:
                        continue
                    cutoff = min(radii[i] + radii[j] + tol, max_len)
                    dr = [ai.xyz[k] - aj.xyz[k] for k in range(3)]
                    dr = _min_image_vec(struct, dr)
                    d = math.sqrt(sum(v * v for v in dr))
                    if d <= cutoff and d > 0.35:
                        out.append((i, j, d))
                        seen.add((i, j))
    return out


# ---------------------------------------------------------------------------
# Molecule unwrapping (so H2O / CO2 straddling PBC render intact)
# ---------------------------------------------------------------------------

def unwrap_molecules(struct: Structure,
                     bonds: Sequence[Tuple[int, int, float]]) -> List[List[float]]:
    """Return per-atom display positions where each connected molecule has
    been translated by integer multiples of cell vectors so bonds stay short.

    Only touches atoms that participate in a bond (i.e. molecular species);
    isolated metals in the slab keep their wrapped positions.
    """
    n = len(struct.atoms)
    positions = [list(a.xyz) for a in struct.atoms]
    if getattr(struct, "_no_cell", False):
        return positions

    adj: Dict[int, List[int]] = {i: [] for i in range(n)}
    for i, j, _ in bonds:
        adj[i].append(j)
        adj[j].append(i)

    visited = [False] * n
    for seed in range(n):
        if visited[seed] or not adj[seed]:
            continue
        # BFS
        queue = [seed]
        visited[seed] = True
        while queue:
            cur = queue.pop(0)
            for nb in adj[cur]:
                if visited[nb]:
                    continue
                visited[nb] = True
                # Move nb so that (nb - cur) is minimum-image
                dr = [positions[nb][k] - positions[cur][k] for k in range(3)]
                dr_min = _min_image_vec(struct, dr)
                positions[nb] = [positions[cur][k] + dr_min[k] for k in range(3)]
                queue.append(nb)
    return positions


# ---------------------------------------------------------------------------
# Payload / rendering
# ---------------------------------------------------------------------------

def build_payload(struct: Structure,
                  title: Optional[str] = None,
                  subtitle: Optional[str] = None,
                  notes_html: Optional[str] = None,
                  contract: Optional[dict] = None,
                  source_files: Optional[List[str]] = None,
                  extra: Optional[dict] = None,
                  bond_tol: float = 0.45,
                  bond_max_len: float = 2.6,
                  ) -> dict:
    bonds_raw = detect_bonds(struct, tol=bond_tol, max_len=bond_max_len)
    positions = unwrap_molecules(struct, bonds_raw)

    comp = struct.composition()
    lengths = struct.cell_lengths()
    angles = struct.cell_angles()
    vol = struct.volume()

    payload = {
        "title": title or struct.comment or "structure",
        "subtitle": subtitle or "",
        "notes_html": notes_html or "",
        "cell": [[round(v, 6) for v in row] for row in struct.cell],
        "cell_lengths": [round(v, 4) for v in lengths],
        "cell_angles": [round(v, 2) for v in angles],
        "volume": round(vol, 3),
        "has_cell": not getattr(struct, "_no_cell", False),
        "formula": struct.formula(),
        "composition": comp,
        "n_atoms": len(struct.atoms),
        "selective_dynamics": struct.selective_dynamics,
        "n_fixed": sum(1 for a in struct.atoms if a.fixed),
        "atoms": [
            {
                "el": a.el,
                "xyz": [round(positions[i][k], 6) for k in range(3)],
                "fixed": a.fixed,
                "tag": a.tag,
                "group": a.group,
            }
            for i, a in enumerate(struct.atoms)
        ],
        "bonds": [[i, j, round(d, 4)] for i, j, d in bonds_raw],
        "colors": {el: DEFAULT_COLORS.get(el, "#cccccc") for el in comp},
        "radii": {el: DISPLAY_RADII.get(el, 0.75) for el in comp},
        "elements_ordered": sorted(comp.keys()),
        "source_files": source_files or [],
        "contract": contract or None,
    }
    if extra:
        payload.update(extra)
    return payload


def render_html(payload: dict, template_path: str | os.PathLike) -> str:
    tpl = Path(template_path).read_text(encoding="utf-8")
    token = "__PAYLOAD_JSON__"
    if token not in tpl:
        raise RuntimeError("template missing %s placeholder: %s" % (token, template_path))
    # Ensure the payload can never break out of its <script> slot.
    body = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    body = body.replace("</", "<\\/").replace("<!--", "<\\!--")
    html = tpl.replace(token, body)
    # Also substitute the <title> placeholder so the tab shows a real title
    # even before JS runs (and so `grep __.*_PLACEHOLDER__` stays clean).
    title = (payload.get("title") or "structure").strip()
    # keep only chars that are safe inside <title>
    title = title.replace("<", "").replace(">", "").replace("&", "&amp;")
    html = html.replace("__TITLE_PLACEHOLDER__", title)
    return html


def write_outputs(payload: dict,
                  outdir: str | os.PathLike,
                  basename: str = "view",
                  template_path: Optional[str | os.PathLike] = None,
                  write_json: bool = True) -> Dict[str, str]:
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    if template_path is None:
        template_path = Path(__file__).resolve().parent.parent / "assets" / "viewer_template.html"
    paths: Dict[str, str] = {}
    if write_json:
        p = outdir / "structure.json"
        p.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        paths["json"] = str(p)
    html = render_html(payload, template_path)
    p = outdir / f"{basename}.html"
    p.write_text(html, encoding="utf-8")
    paths["html"] = str(p)
    return paths
