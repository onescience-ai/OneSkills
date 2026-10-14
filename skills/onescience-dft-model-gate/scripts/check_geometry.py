#!/usr/bin/env python3
"""通用 DFT/VASP 初始模型几何验收门限。

纯标准库实现（无 numpy / ASE 依赖），任何 Python 3.8+ 环境可直接运行。

    python3 check_geometry.py <结构文件> [--contract model_contract.json] [--json out.json]

设计（重要）:
  * 物理门限全部由 elements.py 的半径数据推导，与体系无关；
    换体系不需要改这个脚本。
  * 体系相关的"预期"由 model_contract.json 声明（物种、计数、角色、模式），
    检查器只负责验证"交付的几何是否满足声明的预期"，不替使用者猜测意图。
  * 所有指标都从传入文件现场反算，报告内嵌 sha256，避免"校验的不是交付的那份文件"。

退出码: 0 = PASS, 1 = 有 FAIL, 2 = 输入/解析错误。
"""

import argparse
import hashlib
import json
import math
import os
import re
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import elements as E  # noqa: E402

# ------------------------------------------------------------------ 默认门限 --
DEFAULTS = {
    # 共用
    "bond_factor": 1.25,          # d <= f*(rcov_i+rcov_j) 判为化学键
    "metal_bond_factor": 1.25,    # 金属-金属（含格点近邻）
    "bond_len_range": [0.70, 1.30],   # 键长 / 共价半径和 的允许区间
    # 非键合接触
    "hh_vdw_factor": 0.80,        # 含 H 的非键合对: d >= f*(rvdw_i+rvdw_j)
    "heavy_rcov_factor": 1.00,    # 重原子非键合对: d >= f*(rcov_i+rcov_j)
    "absolute_floor": 1.00,       # 任意非键合对的绝对下限 (Å)
    # 氢键
    "hbond_h_min": 1.30,          # H...Y 下限，低于此值不算氢键而是重叠
    "hbond_h_max": 2.50,          # H...Y 上限
    "hbond_angle_min": 120.0,     # X-H...Y 最小角 (deg)
    # 体系
    "vacuum_min": 12.0,           # 2D 体系真空硬门限 (Å)
    "slab_gap_factor": 0.35,      # 判定"某一轴向有真空"的间隙阈值（归一化）
    "overlap_ok": True,
}


def nonbonded_floor(si, sj, cfg):
    """非键合原子对的最小允许距离。门限与建模工具共用这一个定义，避免两套标准打架。

    - H···H        : vdW 和 x hh_vdw_factor
    - H···电负性原子: hbond_h_min（这是质子转移下限；正常氢键 1.6-2.2 Å 应通过）
    - H···其它     : vdW 和 x hh_vdw_factor（例如 H 指向金属/碳）
    - 重原子···重原子: 共价半径和 x heavy_rcov_factor
    """
    if si == "H" and sj == "H":
        return cfg["hh_vdw_factor"] * (E.vdw("H") + E.vdw("H"))
    if si == "H" or sj == "H":
        other = sj if si == "H" else si
        if other in E.HBOND_ACCEPTOR_ELEMENTS:
            return cfg["hbond_h_min"]
        return cfg["hh_vdw_factor"] * (E.vdw(si) + E.vdw(sj))
    return cfg["heavy_rcov_factor"] * (E.covalent(si) + E.covalent(sj))


# ============================================================== 结构读取 ====
def read_poscar(path):
    raw = open(path).read().splitlines()
    if len(raw) < 8:
        raise ValueError("行数不足以构成 POSCAR")
    comment = raw[0]
    scale = float(raw[1].split()[0])
    cell = [[float(x) * scale for x in raw[i].split()[:3]] for i in (2, 3, 4)]
    i = 5
    tok = raw[i].split()
    if any(re.search(r"[A-Za-z]", t) for t in tok):
        symbols_line, i = tok, i + 1
    else:
        symbols_line = None
    counts = [int(x) for x in raw[i].split()]
    i += 1
    selective = raw[i].strip().lower().startswith("s")
    if selective:
        i += 1
    mode = raw[i].strip()
    i += 1
    nat = sum(counts)
    if len(raw) < i + nat:
        raise ValueError("原子数不一致: 期望 %d, 实际 %d" % (nat, len(raw) - i))
    coords, flags = [], []
    for k in range(nat):
        parts = raw[i + k].split()
        coords.append([float(x) for x in parts[:3]])
        flags.append(parts[3:6] if len(parts) >= 6 else ["T", "T", "T"])
    if not selective:
        flags = [["T", "T", "T"]] * nat
    if mode.lower().startswith(("c", "k")):
        pos = [[c * scale for c in q] for q in coords]
    else:
        pos = [[sum(coords[n][k] * cell[k][d] for k in range(3)) for d in range(3)] for n in range(nat)]
    if symbols_line:
        symbols = [s for s, c in zip(symbols_line, counts) for _ in range(c)]
    else:
        symbols = [s for s, c in zip(comment.split(), counts) for _ in range(c)]
    if len(symbols) != nat:
        raise ValueError("元素符号与计数不一致")
    return {"cell": cell, "symbols": symbols, "pos": pos, "flags": flags,
            "selective": selective, "order": symbols_line or comment.split(),
            "counts": counts, "fmt": "poscar"}


def read_xyz(path):
    raw = open(path).read().split()
    nat = int(raw[0])
    cell_flat = [float(x) for x in raw[3:12]]
    cell = [cell_flat[0:3], cell_flat[3:6], cell_flat[6:9]]
    symbols, pos, flags = [], [], []
    k = 12
    for _ in range(nat):
        symbols.append(raw[k])
        pos.append([float(raw[k + 1]), float(raw[k + 2]), float(raw[k + 3])])
        flags.append(["T", "T", "T"])
        k += 4
    return {"cell": cell, "symbols": symbols, "pos": pos, "flags": flags,
            "selective": False, "order": [], "counts": [], "fmt": "xyz"}


def read_structure(path):
    head = open(path).read(200)
    if path.lower().endswith(".xyz") or (head.strip().splitlines() and
                                         re.match(r"^\d+\s*$", head.strip().splitlines()[0] or "")):
        return read_xyz(path)
    return read_poscar(path)


# ================================================================== 几何 =====
class Geom:
    def __init__(self, cell, pos, symbols):
        self.cell, self.pos, self.symbols = cell, pos, symbols
        self.n = len(pos)
        self.inv = inv3(cell)
        # 约定: 分数坐标是行向量, cart = frac @ cell。
        # 因此取逆必须是 f_k = sum_d r_d * inv[d][k]，
        # 不能写成列向量约定下的 (inv @ r)_k —— 晶胞非正交 (如 gamma=60°)
        # 时两者不同，会让跨周期边界的距离全错。
        self.frac = [cart_to_frac(p, self.inv) for p in pos]
        c = cell
        area = norm(cross(c[0], c[1])) or 1.0
        self.area_ab = area
        self.volume = abs(det3(c))

    def dist(self, i, j):
        df = [self.frac[i][k] - self.frac[j][k] for k in range(3)]
        df = [d - round(d) for d in df]
        return norm(frac_to_cart(df, self.cell))

    def dist_matrix(self):
        d = [[0.0] * self.n for _ in range(self.n)]
        for i in range(self.n):
            for j in range(i + 1, self.n):
                v = self.dist(i, j)
                d[i][j] = d[j][i] = v
        return d

    def angle(self, a, o, b):
        va = [self.pos[a][k] - self.pos[o][k] for k in range(3)]
        vb = [self.pos[b][k] - self.pos[o][k] for k in range(3)]
        na, nb = norm(va), norm(vb)
        if na < 1e-9 or nb < 1e-9:
            return float("nan")
        return math.degrees(math.acos(max(-1.0, min(1.0, dot(va, vb) / (na * nb)))))

    def axial_gaps(self):
        """每个晶胞轴向的最大空隙（归一化分数长度, Å）。用于通用地判定 2D 真空。"""
        out = []
        for k in range(3):
            fs = sorted(f[k] - math.floor(f[k]) for f in self.frac)
            gaps = [(fs[m + 1] - fs[m], (fs[m] + fs[m + 1]) / 2.0) for m in range(len(fs) - 1)]
            gaps.append((1.0 - fs[-1] + fs[0], (fs[-1] + fs[0] + 1.0) / 2.0))
            g, mid = max(gaps)
            out.append({"axis": k, "gap_frac": g, "gap_A": g * norm(self.cell[k]),
                        "center_frac": mid, "vec": norm(self.cell[k])})
        return out


def norm(v):
    return math.sqrt(sum(x * x for x in v))


def frac_to_cart(f, cell):
    """行向量约定: r_d = sum_k f_k * cell[k][d]"""
    return [sum(f[k] * cell[k][d] for k in range(3)) for d in range(3)]


def cart_to_frac(r, inv):
    """行向量约定的逆变换: f_k = sum_d r_d * inv[d][k]"""
    return [sum(r[d] * inv[d][k] for d in range(3)) for k in range(3)]


def dot(a, b):
    return sum(a[k] * b[k] for k in range(3))


def cross(a, b):
    return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]


def det3(m):
    return (m[0][0] * (m[1][1] * m[2][2] - m[1][2] * m[2][1])
            - m[0][1] * (m[1][0] * m[2][2] - m[1][2] * m[2][0])
            + m[0][2] * (m[1][0] * m[2][1] - m[1][1] * m[2][0]))


def inv3(m):
    d = det3(m)
    if abs(d) < 1e-12:
        raise ValueError("晶胞体积为零")
    return [
        [(m[1][1] * m[2][2] - m[1][2] * m[2][1]) / d, (m[0][2] * m[2][1] - m[0][1] * m[2][2]) / d,
         (m[0][1] * m[1][2] - m[0][2] * m[1][1]) / d],
        [(m[1][2] * m[2][0] - m[1][0] * m[2][2]) / d, (m[0][0] * m[2][2] - m[0][2] * m[2][0]) / d,
         (m[0][2] * m[1][0] - m[0][0] * m[1][2]) / d],
        [(m[1][0] * m[2][1] - m[1][1] * m[2][0]) / d, (m[0][1] * m[2][0] - m[0][0] * m[2][1]) / d,
         (m[0][0] * m[1][1] - m[0][1] * m[1][0]) / d],
    ]


# ============================================================ 键与片段感知 ==
class Perception:
    """通用的化学键 / 片段 / 氢键感知。任何元素组合都按同一套半径规则处理。"""

    def __init__(self, geom, cfg, framework_elements=None):
        self.g, self.cfg = geom, cfg
        # 骨架元素由契约显式声明。声明后，只有骨架元素之间才自动生成金属键，
        # 吸附的碱金属/离子（如 K）不会被并进载体骨架而丢失为独立物种。
        self.framework = set(framework_elements) if framework_elements else None
        self.syms = geom.symbols
        self.n = geom.n
        self.dist = geom.dist_matrix()
        self.bonds = set()
        self.metal_bonds = set()
        self._perceive_bonds()
        self.fragments = self._fragments()
        self.hbonds = self._hbonds()
        self.hbond_pairs = set(frozenset((h, a)) for _, h, a, _ in self.hbonds)

    # ---- 化学键 -----------------------------------------------------------
    def _perceive_bonds(self):
        f = self.cfg["bond_factor"]
        fm = self.cfg["metal_bond_factor"]
        for i in range(self.n):
            for j in range(i + 1, self.n):
                si, sj = self.syms[i], self.syms[j]
                mi, mj = E.is_metal(si), E.is_metal(sj)
                d = self.dist[i][j]
                rcov = E.covalent(si) + E.covalent(sj)
                if mi and mj:
                    if self.framework is not None and not (si in self.framework and sj in self.framework):
                        continue
                    if d <= fm * rcov:
                        self.bonds.add((i, j))
                        self.metal_bonds.add((i, j))
                elif not mi and not mj:
                    if d <= f * rcov:
                        self.bonds.add((i, j))
                # 金属-非金属一律不自动成键：交给非键合接触 / 契约门限判定

    # ---- 连通分量 ---------------------------------------------------------
    def _fragments(self):
        parent = list(range(self.n))

        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        for a, b in self.bonds:
            ra, rb = find(a), find(b)
            if ra != rb:
                parent[rb] = ra
        groups = defaultdict(list)
        for i in range(self.n):
            groups[find(i)].append(i)
        frags = []
        for idx in groups.values():
            comp = Counter(self.syms[i] for i in idx)
            pure_metal = all(E.is_metal(self.syms[i]) for i in idx)
            formula = E.hill_formula_str(comp) if not pure_metal else None
            frags.append({
                "idx": sorted(idx), "comp": dict(comp), "pure_metal": pure_metal,
                "formula": formula,
                "label": E.KNOWN_FORMULAS.get(formula, formula) if formula else "金属骨架",
                "is_atom": len(idx) == 1,
            })
        frags.sort(key=lambda f: -len(f["idx"]))
        return frags

    # ---- 氢键 -------------------------------------------------------------
    def _hbonds(self):
        cfg = self.cfg
        frag_of = {}
        for k, fr in enumerate(self.fragments):
            for i in fr["idx"]:
                frag_of[i] = k
        out = []
        for i in range(self.n):
            if self.syms[i] != "H":
                continue
            donors = [j for j in range(self.n)
                      if self.syms[j] in E.HBOND_DONOR_ELEMENTS and (min(i, j), max(i, j)) in self.bonds]
            accs = [j for j in range(self.n)
                    if self.syms[j] in E.HBOND_ACCEPTOR_ELEMENTS
                    and frag_of.get(j) != frag_of.get(i)
                    and not E.is_metal(self.syms[j])]
            for d in donors:
                for a in accs:
                    dha = self.dist[i][a]
                    if not (cfg["hbond_h_min"] <= dha <= cfg["hbond_h_max"]):
                        continue
                    ang = self.g.angle(d, i, a)
                    if ang >= cfg["hbond_angle_min"]:
                        out.append((d, i, a, dha))
        return out

    # ---- 便捷查询 ---------------------------------------------------------
    def shortest(self, set_a, set_b, exclude_bonded=True):
        best = None
        for i in set_a:
            for j in set_b:
                if i == j:
                    continue
                if exclude_bonded and ((min(i, j), max(i, j)) in self.bonds):
                    continue
                d = self.dist[i][j]
                if best is None or d < best[0]:
                    best = (d, i, j)
        return best


# ================================================================ 报告 =======
class Report:
    def __init__(self):
        self.items = []

    def add(self, gate, status, detail):
        self.items.append({"gate": gate, "status": status, "detail": detail})

    def failed(self):
        return [x for x in self.items if x["status"] == "FAIL"]

    def warned(self):
        return [x for x in self.items if x["status"] == "WARN"]


# ============================================================ 通用门限 =======
def universal_gates(P, G, pc, cfg, R):
    syms, pos = P["symbols"], P["pos"]
    n = len(syms)
    comp = Counter(syms)
    stats = {}

    # ---- U1 结构与晶胞 -----------------------------------------------------
    bad_cell = (abs(det3(P["cell"])) < 1.0)
    R.add("U1 结构可解析", "FAIL" if bad_cell else "PASS",
          "%d 原子 %s | 晶胞 a=%.3f b=%.3f c=%.3f Å, V=%.2f Å³"
          % (n, dict(comp), norm(P["cell"][0]), norm(P["cell"][1]), norm(P["cell"][2]),
             abs(det3(P["cell"]))))

    # ---- U2 片段识别 -------------------------------------------------------
    nmeta = sum(1 for f in pc.fragments if f["pure_metal"])
    nonmetal = [f for f in pc.fragments if not f["pure_metal"]]
    unknown = [f for f in nonmetal if f["is_atom"] or f["formula"] not in E.KNOWN_FORMULAS]
    desc = ", ".join("%s x%d" % (f["label"], 1) for f in nonmetal) or "无"
    all_isolated = bool(nonmetal) and all(len(f["idx"]) == 1 for f in nonmetal)
    if all_isolated:
        R.add("U2 片段识别", "FAIL",
              "%d 个金属片段; 非金属原子全部孤立（未成键）: %s"
              % (nmeta, [syms[i] for f in nonmetal for i in f["idx"]][:20]))
    else:
        R.add("U2 片段识别", "INFO",
              "%d 个金属片段; 非金属片段: %s%s"
              % (nmeta, desc,
                 " | 未收录式样（不影响门限）: %s" % sorted(set(f["formula"] for f in unknown))
                 if unknown else ""))
    if pc.framework is None:
        R.add("U2b 骨架声明", "WARN",
              "契约未声明 framework.elements：载体金属与吸附的金属离子会被并进同一片段，"
              "后者无法作为独立物种计数。含金属离子/双金属体系请显式声明载体元素。")
    else:
        R.add("U2b 骨架声明", "PASS", "载体骨架元素 = %s" % sorted(pc.framework))
    stats["fragments"] = [{"formula": f["formula"], "label": f["label"], "n": len(f["idx"]),
                           "pure_metal": f["pure_metal"]} for f in pc.fragments]

    # ---- U3 键长合理性 -----------------------------------------------------
    lo, hi = cfg["bond_len_range"]
    bad_bonds = []
    for (i, j) in pc.bonds:
        rsum = E.covalent(syms[i]) + E.covalent(syms[j])
        ratio = pc.dist[i][j] / rsum if rsum > 0 else 0
        if not (lo <= ratio <= hi):
            bad_bonds.append((i, j, pc.dist[i][j], ratio))
    bad_bonds.sort(key=lambda t: -abs(t[3] - 1.0))
    if bad_bonds:
        R.add("U3 键长合理性", "FAIL",
              "%d 条键的 d/(rcov_i+rcov_j) 超出 [%.2f,%.2f]: %s"
              % (len(bad_bonds), lo, hi,
                 ", ".join("%s%d-%s%d d=%.3f r=%.2f" % (syms[i], i, syms[j], j, d, r)
                           for i, j, d, r in bad_bonds[:10])))
    else:
        R.add("U3 键长合理性", "PASS", "%d 条键全部落在 [%.2f,%.2f]×共价半径和" % (len(pc.bonds), lo, hi))

    # ---- U4 非键合接触（核心硬门限） --------------------------------------
    # 排除 1-2（成键）与 1-3（共用一个成键邻居）原子对：
    # 水分子内的 H···H 天然约 1.5 Å，属分子内几何，不是"接触"问题。
    bonded = pc.bonds
    adj = defaultdict(set)
    for (a, b) in bonded:
        adj[a].add(b)
        adj[b].add(a)
    offenders, worst_hh, worst_heavy = [], None, None
    for i in range(n):
        for j in range(i + 1, n):
            if (i, j) in bonded:
                continue
            if adj[i] & adj[j]:
                continue
            if frozenset((i, j)) in pc.hbond_pairs:
                continue
            si, sj = syms[i], syms[j]
            if E.is_metal(si) and E.is_metal(sj):
                continue                      # 金属骨架格点间距由 U3/契约处理
            d = pc.dist[i][j]
            floor = nonbonded_floor(si, sj, cfg)
            if si == "H" or sj == "H":
                if worst_hh is None or d < worst_hh[0]:
                    worst_hh = (d, i, j, floor)
            else:
                if worst_heavy is None or d < worst_heavy[0]:
                    worst_heavy = (d, i, j, floor)
            if d < max(floor, cfg["absolute_floor"]):
                offenders.append((d, i, j, floor))
    offenders.sort()
    stats["min_hh"] = worst_hh
    stats["min_heavy"] = worst_heavy
    detail = []
    if worst_hh:
        detail.append("含H非键合最小 %.4f Å (%s%d-%s%d, 下限 %.3f)" %
                      (worst_hh[0], syms[worst_hh[1]], worst_hh[1], syms[worst_hh[2]], worst_hh[2], worst_hh[3]))
    if worst_heavy:
        detail.append("重原子非键合最小 %.4f Å (%s%d-%s%d, 下限 %.3f)" %
                      (worst_heavy[0], syms[worst_heavy[1]], worst_heavy[1],
                       syms[worst_heavy[2]], worst_heavy[2], worst_heavy[3]))
    if offenders:
        R.add("U4 非键合接触", "FAIL",
              "%d 对低于门限 | %s | %s" % (
                  len(offenders), " | ".join(detail),
                  ", ".join("%s%d-%s%d=%.3f<%.2f" % (syms[i], i, syms[j], j, d, fl)
                            for d, i, j, fl in offenders[:14])))
    else:
        R.add("U4 非键合接触", "PASS", " | ".join(detail) if detail else "无非键合对")

    # ---- U5 氢键几何 -------------------------------------------------------
    over = defaultdict(list)
    for d, h, a, dh in pc.hbonds:
        over[a].append(h)
    too_short = []
    for i in range(n):
        if syms[i] != "H":
            continue
        for j in range(n):
            if syms[j] in E.HBOND_ACCEPTOR_ELEMENTS and not E.is_metal(syms[j]):
                d = pc.dist[i][j]
                if cfg["absolute_floor"] < d < cfg["hbond_h_min"]:
                    donors = [k for k in range(n)
                              if syms[k] in E.HBOND_DONOR_ELEMENTS and (min(i, k), max(i, k)) in pc.bonds]
                    if donors:
                        too_short.append((d, i, j, donors[0]))
    detail = "%d 条氢键, 受体最大配位数 %d（配位上限属溶剂角色门限，见 C2-*）" % (len(pc.hbonds), max([len(v) for v in over.values()] or [0]))
    if too_short:
        R.add("U5 氢键几何", "FAIL", detail + " | H···受体过短(%.2f-%.2f Å，会引发质子转移): %s" % (
            cfg["absolute_floor"], cfg["hbond_h_min"],
            ", ".join("H%d-%s%d=%.3f" % (h, syms[a], a, d) for d, h, a, _ in
                      sorted(too_short)[:10])))
    else:
        R.add("U5 氢键几何", "PASS", detail)

    # ---- U6 维度 / 真空 ----------------------------------------------------
    gaps = G.axial_gaps()
    vac = max(gaps, key=lambda g: g["gap_A"])
    is_slab = vac["gap_frac"] >= cfg["slab_gap_factor"]
    stats["vacuum"] = vac
    stats["is_slab"] = is_slab
    G.is_slab = is_slab
    G.vacuum = vac
    if is_slab:
        if vac["gap_A"] < cfg["vacuum_min"]:
            R.add("U6 维度与真空", "FAIL",
                  "判定为 2D slab（轴向 %d 有 %.1f%% 空隙），真空 %.3f Å < 硬门限 %.1f Å"
                  % (vac["axis"], 100 * vac["gap_frac"], vac["gap_A"], cfg["vacuum_min"]))
        else:
            R.add("U6 维度与真空", "PASS",
                  "2D slab，真空 %.3f Å（轴向 %d，空隙占比 %.1f%%）"
                  % (vac["gap_A"], vac["axis"], 100 * vac["gap_frac"]))
    else:
        R.add("U6 维度与真空", "PASS",
              "判定为 3D 周期体系（各轴向最大空隙 %s Å），不检查真空"
              % ", ".join("%.2f" % g["gap_A"] for g in gaps))

    # ---- U7 骨架-分子最短接触（信息 + 契约入口） --------------------------
    fw = None
    for f in pc.fragments:
        if f["pure_metal"] and (fw is None or len(f["idx"]) > len(fw["idx"])):
            fw = f
    if fw and nonmetal:
        rows = []
        for f in nonmetal:
            s = pc.shortest(f["idx"], fw["idx"])
            if s:
                rows.append((s[0], f, s))
        rows.sort(key=lambda t: t[0])
        stats["min_framework_contact"] = [
            {"formula": f["formula"], "d": s[0], "pair": (syms[s[1]], s[1], syms[s[2]], s[2])}
            for _, f, s in rows]
        R.add("U7 骨架-分子接触", "INFO",
              "; ".join("%s 最近 %s%d-%s%d = %.3f Å"
                        % (f["label"], syms[s[1]], s[1], syms[s[2]], s[2], s[0])
                        for _, f, s in rows[:6]))
    else:
        R.add("U7 骨架-分子接触", "INFO", "无金属骨架或无非金属片段，跳过")
    return stats


# ============================================================ 契约门限 =======
def contract_gates(P, G, pc, contract, cfg, R):
    syms, pos = P["symbols"], P["pos"]
    n = len(syms)
    stats = {}

    # ---- C1 物种计数 -------------------------------------------------------
    frags = [f for f in pc.fragments if not f["pure_metal"]]
    observed = Counter()
    for f in frags:
        if f["is_atom"]:
            observed[syms[f["idx"][0]]] += 1
        else:
            observed[f["formula"]] += 1
    # 金属离子（非骨架的单原子金属）也计入
    for f in pc.fragments:
        if f["pure_metal"] and f["is_atom"]:
            observed[syms[f["idx"][0]]] += 1

    declared = contract.get("species", {})
    mismatch = []
    for name, spec in declared.items():
        want = spec.get("count")
        got = observed.get(name, 0)
        if want is not None and want != got:
            mismatch.append("%s: 声明 %d, 实测 %d" % (name, want, got))
    undeclared = {k: v for k, v in observed.items() if k not in declared}
    if mismatch:
        R.add("C1 物种计数", "FAIL",
              "; ".join(mismatch) + " | 实测全部: %s" % dict(observed))
    else:
        R.add("C1 物种计数", "PASS",
              "声明物种计数全部匹配: %s" % {k: observed.get(k, 0) for k in declared}
              + (" | 未声明物种: %s" % undeclared if undeclared else ""))
    stats["observed_species"] = dict(observed)

    # ---- C2 逐物种角色门限 -------------------------------------------------
    for name, spec in declared.items():
        role = spec.get("role", "molecule")
        targets = [f for f in pc.fragments
                   if (f["formula"] == name) or (f["is_atom"] and syms[f["idx"][0]] == name)]

        if role == "solvent":
            _solvent_gate(name, spec, targets, P, G, pc, cfg, R, stats)
        elif role in ("adsorbate", "molecule"):
            _adsorbate_gate(name, spec, targets, P, G, pc, cfg, R, stats)
        elif role == "ion":
            _ion_gate(name, spec, targets, P, G, pc, cfg, R, stats)
        else:
            R.add("C2-%s" % name, "INFO", "未知 role=%s，仅做通用门限" % role)

    # ---- C3 slab 声明 ------------------------------------------------------
    slab = contract.get("slab")
    if slab:
        problems = []
        fw = None
        for f in pc.fragments:
            if f["pure_metal"] and (fw is None or len(f["idx"]) > len(fw["idx"])):
                fw = f
        if slab.get("layers") and fw:
            axis = getattr(pc.g, "vacuum", {}).get("axis", 2)
            zs = [pos[i][axis] for i in fw["idx"]]
            uniq = cluster_1d(sorted(zs), slab.get("layer_tol", 0.30))
            if len(uniq) != slab["layers"]:
                problems.append("金属层数: 声明 %d, 实测 %d (z=%s)"
                                % (slab["layers"], len(uniq), [round(u, 3) for u in uniq]))
        R.add("C3 slab 声明", "FAIL" if problems else "PASS",
              "; ".join(problems) if problems else "slab 声明满足: %s" % slab)

    # ---- C4 固定原子 -------------------------------------------------------
    flags = P["flags"]
    fixed = [i for i in range(n) if any(f == "F" for f in flags[i])]
    problems = []
    if not fixed:
        problems.append("没有固定原子（slab 会整体漂移）")
    nonmetal_fixed = [i for i in fixed if not E.is_metal(syms[i])]
    if nonmetal_fixed:
        problems.append("非金属被固定: %s" % [(syms[i], i) for i in nonmetal_fixed[:8]])
    partial = [i for i in fixed if not all(f == "F" for f in flags[i])]
    if partial:
        problems.append("部分方向固定: %s" % [(syms[i], i, flags[i]) for i in partial[:8]])
    detail = "%d/%d 原子固定" % (len(fixed), n)
    if fixed:
        axis = getattr(pc.g, "vacuum", {}).get("axis", 2)
        zf = sorted(set(round(pos[i][axis], 3) for i in fixed))
        detail += "，固定层坐标 = %s" % zf
        metal_z = sorted(set(round(pos[i][axis], 3) for i in range(n) if E.is_metal(syms[i])))
        want = metal_z[:len(zf)]
        if [round(x, 3) for x in zf] != [round(x, 3) for x in want]:
            problems.append("固定的不是最底部连续金属层: 固定 %s vs 金属层 %s" % (zf, metal_z))
    R.add("C4 固定原子", "FAIL" if problems else "PASS",
          detail + (" | " + "; ".join(problems) if problems else ""))
    return stats




def _solvent_gate(name, spec, targets, P, G, pc, cfg, R, stats):
    if not targets:
        R.add("C2-%s(溶剂)" % name, "FAIL", "声明为溶剂但几何中未找到该物种")
        return
    idx = [i for f in targets for i in f["idx"]]
    heavy = [i for i in idx if not E.is_metal(pc.syms[i]) and pc.syms[i] != "H"]
    model = spec.get("solvent_model", "liquid-film")
    axis = getattr(pc.g, "vacuum", {}).get("axis", 2)

    # 膜厚定义很关键：只用重原子 z 跨度会低估厚度（漏掉分子自身的尺寸），
    # 只用含 H 的全跨度又会高估。取"重原子跨度 + 一个最近邻间距"作为膜厚，
    # 相当于在膜两侧各加半个分子直径，是与液态密度可比的口径。
    nn = []
    for i, f in enumerate(targets):
        best = None
        for j, g in enumerate(targets):
            if i == j:
                continue
            for a in f["idx"]:
                if a not in heavy:
                    continue
                for b in g["idx"]:
                    if b not in heavy:
                        continue
                    d = pc.dist[a][b]
                    if best is None or d < best:
                        best = d
        if best is not None:
            nn.append(best)
    d_nn = (sum(nn) / len(nn)) if nn else 0.0

    if getattr(pc.g, "is_slab", False):
        zs = [pc.g.pos[i][axis] for i in idx]
        span_all = max(zs) - min(zs)
        zsh = [pc.g.pos[i][axis] for i in heavy]
        span_heavy = (max(zsh) - min(zsh)) if zsh else 0.0
        thickness = span_heavy + d_nn
        vol = G.area_ab * thickness
        volume_desc = ("面积 %.2f Å² × 膜厚 %.3f Å (重原子跨度 %.3f + 最近邻间距 %.3f)"
                       % (G.area_ab, thickness, span_heavy, d_nn))
    else:
        thickness = None
        span_all = None
        vol = G.volume
        volume_desc = "晶胞体积 %.2f Å³" % vol
    rho = len(targets) / vol if vol > 1e-9 else float("inf")
    rho_atoms = (len(targets) / (G.area_ab * span_all)) if span_all else None

    ref = spec.get("bulk_number_density") or E.LIQUID_NUMBER_DENSITY.get(name)
    ratio = (rho / ref) if ref else None
    detail = ("%d 个 %s / %s -> 数密度 %.5f Å⁻³%s"
              % (len(targets), name, volume_desc, rho,
                 " (%.3f × 体相)" % ratio if ratio else " (无体相参考值)"))
    if rho_atoms:
        detail += "; 含 H 全跨度口径 %.5f Å⁻³ (%.2f ×)" % (rho_atoms, rho_atoms / ref if ref else 0)
    if model == "liquid-film":
        win = spec.get("density_ratio_range", [0.75, 1.35])
        if ratio is None:
            R.add("C2-%s(溶剂)" % name, "FAIL",
                  detail + " | 声明 liquid-film 但缺少体相参考；请在契约里给 bulk_number_density 或改用 solvent_model=monolayer")
        elif not (win[0] <= ratio <= win[1]):
            R.add("C2-%s(溶剂)" % name, "FAIL",
                  detail + " | 液体膜密度须在 %.2f-%.2f × 体相内；偏离说明膜过厚（分子铺得太开）或过薄（被压实），"
                           "或与声明的液膜模型不符" % (win[0], win[1]))
        else:
            R.add("C2-%s(溶剂)" % name, "PASS", detail)
    else:
        R.add("C2-%s(溶剂)" % name, "INFO",
              detail + " | solvent_model=%s，密度仅报告；须在契约中同时声明 target_coverage 以便核对" % model)

    # 氢键配位
    hs = set(i for f in targets for i in f["idx"] if pc.syms[i] == "H")
    acc = defaultdict(list)
    for d, h, a, dh in pc.hbonds:
        if a in heavy:
            acc[a].append(h)
    cn_accept = [len(v) for v in acc.values()]
    mean_hb = 2.0 * len([1 for d, h, a, dh in pc.hbonds if a in heavy]) / max(1, len(targets))
    lo, hi = spec.get("hbond_per_molecule_range", [1.0, 4.5])
    amax = spec.get("hbond_accept_max", 2)
    problems = []
    if not (lo <= mean_hb <= hi):
        problems.append("平均氢键数 %.2f 越界 %.1f-%.1f" % (mean_hb, lo, hi))
    over = {a: len(v) for a, v in acc.items() if len(v) > amax}
    if over:
        problems.append("受体过配位(>%d): %s" % (amax, sorted(over.items(), key=lambda t: -t[1])[:6]))
    R.add("C2-%s(氢键网络)" % name, "FAIL" if problems else "PASS",
          "平均 %.2f 条氢键/分子, 受体配位数 %s" % (mean_hb, sorted(cn_accept, reverse=True)[:12])
          + (" | " + "; ".join(problems) if problems else ""))

    # 不穿金属
    fw = None
    for f in pc.fragments:
        if f["pure_metal"] and (fw is None or len(f["idx"]) > len(fw["idx"])):
            fw = f
    if fw and getattr(pc.g, "is_slab", False):
        ztop = max(pc.g.pos[i][axis] for i in fw["idx"])
        deep = [i for i in idx if pc.g.pos[i][axis] < ztop - spec.get("sink_tol", 0.20)]
        R.add("C2-%s(不穿金属)" % name, "FAIL" if deep else "PASS",
              ("%d 个溶剂原子低于金属顶层 %.3f Å: %s" % (len(deep), ztop,
                                                     [(pc.syms[i], i, round(pc.g.pos[i][axis], 3)) for i in deep[:8]]))
              if deep else "全部溶剂原子不低于金属顶层 %.3f Å" % ztop)
    stats["solvent_%s" % name] = {"n": len(targets), "rho": rho, "ratio": ratio, "mean_hbond": mean_hb}


def _adsorbate_gate(name, spec, targets, P, G, pc, cfg, R, stats):
    if not targets:
        R.add("C2-%s(吸附物)" % name, "FAIL", "声明为吸附物但几何中未找到该物种")
        return
    fw = None
    for f in pc.fragments:
        if f["pure_metal"] and (fw is None or len(f["idx"]) > len(fw["idx"])):
            fw = f
    if not fw:
        R.add("C2-%s(吸附物)" % name, "INFO", "无金属骨架，跳过骨架接触门限")
        return
    best = None
    for f in targets:
        s = pc.shortest(f["idx"], fw["idx"])
        if s and (best is None or s[0] < best[0]):
            best = (s[0], s[1], s[2], f)
    d, i, j, frag = best
    mode = spec.get("mode", "any")
    thr = spec.get("min_metal_contact")
    if thr is None and mode == "physisorbed":
        thr = spec.get("physisorbed_vdw_factor", 0.90) * (E.vdw(pc.syms[j]) + E.vdw(pc.syms[i]))
    detail = "最近骨架接触 %s%d-%s%d = %.3f Å" % (pc.syms[i], i, pc.syms[j], j, d)
    if thr is None:
        R.add("C2-%s(吸附物)" % name, "INFO",
              detail + " | mode=%s 且未声明 min_metal_contact，仅报告（建议显式声明）" % mode)
    elif d < thr:
        R.add("C2-%s(吸附物)" % name, "FAIL",
              detail + " | mode=%s 要求 ≥ %.3f Å；当前已进入排斥区，与声明的吸附模式矛盾"
              % (mode, thr))
    else:
        R.add("C2-%s(吸附物)" % name, "PASS", detail + " | mode=%s，门限 %.3f Å" % (mode, thr))
    stats["adsorbate_%s" % name] = {"min_contact": d, "mode": mode, "threshold": thr}


def _ion_gate(name, spec, targets, P, G, pc, cfg, R, stats):
    if not targets:
        R.add("C2-%s(离子)" % name, "FAIL", "声明为离子但几何中未找到")
        return
    cutoff = spec.get("coordination_cutoff")
    idx = [i for f in targets for i in f["idx"]]
    if cutoff is None:
        acc = [i for i in range(pc.n) if pc.syms[i] in E.HBOND_ACCEPTOR_ELEMENTS]
        rmin = min((E.covalent(pc.syms[i]) + E.covalent(pc.syms[j]) for i in idx for j in acc), default=1.5)
        cutoff = 1.25 * rmin
    cn = Counter()
    for i in idx:
        for j in range(pc.n):
            if j in idx or pc.syms[j] in ("H",):
                continue
            if pc.syms[j] in E.HBOND_ACCEPTOR_ELEMENTS and pc.dist[i][j] <= cutoff:
                cn[pc.syms[j]] += 1
    win = spec.get("coordination_range")
    detail = "配位截断 %.2f Å -> CN(%s) = %s" % (cutoff, name, dict(cn))
    if win and not (win[0] <= sum(cn.values()) <= win[1]):
        R.add("C2-%s(离子)" % name, "FAIL",
              detail + " | 声明配位区间 %s 未满足（溶剂化壳层不完整或被过度裁剪）" % (win,))
    else:
        R.add("C2-%s(离子)" % name, "PASS" if win else "INFO",
              detail + ("" if win else " | 未声明 coordination_range，仅报告"))
    stats["ion_%s" % name] = {"cn": dict(cn), "cutoff": cutoff}


def cluster_1d(values, tol):
    out = []
    for v in values:
        if not out or v - out[-1] > tol:
            out.append(v)
    return out


# ================================================================== main =====
def main():
    ap = argparse.ArgumentParser(description="通用 DFT/VASP 初始模型几何验收门限")
    ap.add_argument("structure")
    ap.add_argument("--contract", help="model_contract.json 路径")
    ap.add_argument("--set", action="append", default=[], metavar="KEY=VALUE",
                    help="覆盖门限，例如 --set vacuum_min=15 --set hbond_h_max=2.4")
    ap.add_argument("--contract-optional", action="store_true",
                    help="临时排查用：无契约时降级为 WARN。正式交付不要用。")
    ap.add_argument("--json", dest="json_out")
    a = ap.parse_args()

    cfg = dict(DEFAULTS)
    for item in a.set:
        k, _, v = item.partition("=")
        if k not in cfg:
            print("未知门限参数: %s（可用: %s）" % (k, ", ".join(sorted(cfg))))
            return 2
        try:
            cfg[k] = json.loads(v)
        except Exception:
            cfg[k] = v

    if not os.path.isfile(a.structure):
        print("找不到结构文件: %s" % a.structure)
        return 2
    sha = hashlib.sha256(open(a.structure, "rb").read()).hexdigest()

    contract = {}
    csha = None
    if a.contract:
        if not os.path.isfile(a.contract):
            print("找不到契约文件: %s" % a.contract)
            return 2
        contract = json.load(open(a.contract))
        csha = hashlib.sha256(open(a.contract, "rb").read()).hexdigest()

    try:
        P = read_structure(a.structure)
        G = Geom(P["cell"], P["pos"], P["symbols"])
        pc = Perception(G, cfg, contract.get("framework", {}).get("elements"))
    except Exception as e:
        print("解析失败: %s" % e)
        return 2

    R = Report()
    stats = universal_gates(P, G, pc, cfg, R)
    if contract:
        stats.update(contract_gates(P, G, pc, contract, cfg, R))
    else:
        R.add("C0 契约", "WARN" if a.contract_optional else "FAIL",
              "未提供 --contract：只跑了通用门限，体系相关的预期（物种计数、溶剂密度、吸附模式、"
              "离子配位、slab 层数）全部未验证。请先写 model_contract.json"
              + ("（当前 --contract-optional，仅供临时排查）。" if a.contract_optional else "。"))

    print("=== DFT/VASP 初始模型几何验收 ===")
    print("structure : %s" % os.path.abspath(a.structure))
    print("sha256    : %s" % sha)
    if csha:
        print("contract  : %s  (sha256 %s)" % (os.path.abspath(a.contract), csha))
    print("command   : python3 check_geometry.py %s%s"
          % (a.structure, " --contract %s" % a.contract if a.contract else ""))
    print("-" * 96)
    for it in R.items:
        print("[%-4s] %-26s %s" % (it["status"], it["gate"], it["detail"]))
    print("-" * 96)
    verdict = "FAIL" if R.failed() else "PASS"
    print("结论: %s   (%d 项未通过, %d 项警告)" % (verdict, len(R.failed()), len(R.warned())))
    if R.failed():
        print("未通过: %s" % ", ".join(x["gate"] for x in R.failed()))
        print("规则: 未通过 FAIL 的结构不得提交 DFT 计算，也不得在交付说明里写成 PASS。")
    if a.json_out:
        json.dump({"structure": os.path.abspath(a.structure), "sha256": sha,
                   "contract": os.path.abspath(a.contract) if a.contract else None,
                   "contract_sha256": csha, "verdict": verdict,
                   "items": R.items, "stats": stats},
                  open(a.json_out, "w"), ensure_ascii=False, indent=2, default=str)
        print("JSON: %s" % a.json_out)
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
