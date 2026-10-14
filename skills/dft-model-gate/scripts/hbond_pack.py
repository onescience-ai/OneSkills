#!/usr/bin/env python3
"""通用氢键溶剂层排布器。

解决的问题（不限于水，任何 X-H 型溶剂分子）:
  "每个分子都把自己的 H 指向最近邻"这种朴素做法会产生**互相为最近邻**的分子对：
  双方各投一个 H 到对方身上，于是两个 H 在中间迎面对撞（实测可到 1.0 Å），
  同时受体被过度配位。这个模块用"打分选优"取代"按最近邻硬投"，
  从构造上避免该缺陷。

算法:
  1. 每个分子的取向由旋转矩阵参数化，局部 H 方向由 X-H 键长与 H-X-H 角固定。
  2. 候选取向 = 若干随机均匀取向 ∪ "把某个 H 对准某个受体"的解析取向。
  3. 打分惩罚所有不物理接触（H···H 过近、H···其他原子过近、分子内键长偏离），
     奖励被指定受体上的合理氢键距离（1.6-2.2 Å）。
  4. 逐分子坐标下降（Gauss-Seidel），多轮扫描。

作为库使用:
    from hbond_pack import pack_solvent, WATER
    mols = pack_solvent(cell, sites, WATER, existing=framework_atoms, passes=3)
    # mols: [ {"central": (x,y,z), "H": [(x,y,z), ...]}, ... ]

作为命令行自测:
    python3 hbond_pack.py --selftest     # 在 4x4 Cu(111) 上摆 18 个水并自检 H···H
"""

import argparse
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from check_geometry import (Geom, cart_to_frac, frac_to_cart, inv3,  # noqa: E402
                            nonbonded_floor)
import elements as E  # noqa: E402

FLOOR_DEFAULTS = {
    "bond_factor": 1.25, "metal_bond_factor": 1.25, "bond_len_range": [0.70, 1.30],
    "hh_vdw_factor": 0.80, "heavy_rcov_factor": 1.00, "absolute_floor": 1.00,
    "hbond_h_min": 1.30, "hbond_h_max": 2.50, "hbond_angle_min": 120.0,
    "vacuum_min": 12.0, "slab_gap_factor": 0.35, "overlap_ok": True,
}

# 常用溶剂分子模板。要加新溶剂，照抄一条即可。
WATER = {"name": "H2O", "central": "O", "h_element": "H", "xh": 0.96, "hxh": 104.5}
AMMONIA = {"name": "NH3", "central": "N", "h_element": "H", "xh": 1.01, "hxh": 106.7}
METHANOL = {"name": "CH3OH", "central": "O", "h_element": "H", "xh": 0.96, "hxh": 108.0}


# ------------------------------------------------------------------ 线性代数 --
def _mm(a, b):
    return [[sum(a[r][k] * b[k][c] for k in range(3)) for c in range(3)] for r in range(3)]


def _mv(m, v):
    return [sum(m[r][k] * v[k] for k in range(3)) for r in range(3)]


def rotation_from(a, b):
    """把单位向量 a 旋转到单位向量 b 的旋转矩阵（Rodrigues）。"""
    v = [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]
    c = sum(a[k] * b[k] for k in range(3))
    s = math.sqrt(sum(x * x for x in v))
    if s < 1e-9:
        if c > 0:
            return [[1.0 if r == k else 0.0 for k in range(3)] for r in range(3)]
        # 反向：绕任一垂直轴转 180°
        axis = [1.0, 0.0, 0.0] if abs(a[0]) < 0.9 else [0.0, 1.0, 0.0]
        u = _mv([[0, -axis[2], axis[1]], [axis[2], 0, -axis[0]], [-axis[1], axis[0], 0]], a)
        n = math.sqrt(sum(x * x for x in u))
        u = [x / n for x in u]
        return [[2 * u[r] * u[k] - (1.0 if r == k else 0.0) for k in range(3)] for r in range(3)]
    K = [[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]]
    I = [[1.0 if r == k else 0.0 for k in range(3)] for r in range(3)]
    K2 = _mm(K, K)
    f = 1.0 / (1.0 + c)
    return [[I[r][k] + K[r][k] + f * K2[r][k] for k in range(3)] for r in range(3)]


def rot_about(axis, ang):
    """绕单位轴 axis 旋转 ang（右手定则）的旋转矩阵。"""
    x, y, z = axis
    c, sn = math.cos(ang), math.sin(ang)
    C = 1.0 - c
    return [
        [c + x * x * C, x * y * C - z * sn, x * z * C + y * sn],
        [y * x * C + z * sn, c + y * y * C, y * z * C - x * sn],
        [z * x * C - y * sn, z * y * C + x * sn, c + z * z * C],
    ]


def _normalize(v):
    n = math.sqrt(sum(x * x for x in v))
    return [x / n for x in v] if n > 1e-12 else [1.0, 0.0, 0.0]


def _cross(a, b):
    return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]


def _frame(a, b):
    """由两个方向构造正交基（按列存放）。a,b 为同一分子的两个 H 方向或两个受体方向。"""
    e1 = _normalize([a[k] + b[k] for k in range(3)])
    t = [a[k] - b[k] for k in range(3)]
    if sum(x * x for x in t) < 1e-12:
        t = _cross(e1, [0.0, 0.0, 1.0])
        if sum(x * x for x in t) < 1e-12:
            t = _cross(e1, [1.0, 0.0, 0.0])
    e2 = _normalize(t)
    e3 = _cross(e1, e2)
    return [[e1[0], e2[0], e3[0]], [e1[1], e2[1], e3[1]], [e1[2], e2[2], e3[2]]]


def align_two(h1, h2, u1, u2):
    """把分子的两个 H 方向 (h1,h2) 最优地对准两个受体方向 (u1,u2)。

    H-X-H 角是固定的，所以只可能做到"平分线+平面"最优匹配，
    这正是双受体氢键应有的折中几何。
    """
    E, F = _frame(h1, h2), _frame(u1, u2)
    # R = F @ E^T
    return [[sum(F[r][k] * E[c][k] for k in range(3)) for c in range(3)] for r in range(3)]


def random_rotations(n, seed=0):
    rng = random.Random(seed)
    out = []
    for _ in range(n):
        q = [rng.gauss(0, 1) for _ in range(4)]
        nq = math.sqrt(sum(x * x for x in q))
        w, x, y, z = [v / nq for v in q]
        out.append([
            [1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
            [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
            [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)],
        ])
    return out


# --------------------------------------------------------------- 局部几何 ----
def local_h_directions(template):
    """分子在局部坐标系下的单位 H 方向（关于 +z 对称，夹角 = hxh）。"""
    nh = int(template.get("nh", 2))
    half = math.radians(template["hxh"]) / 2.0
    dirs = []
    for sgn in ((1, -1) if nh == 2 else (1,)):
        dirs.append(_normalize([sgn * math.sin(half), 0.0, math.cos(half)]))
    return dirs


# ------------------------------------------------------------------ 核心 -----
class Packer:
    """在一个周期晶胞内，对给定中心位点排布氢键溶剂分子。

    与"每个分子把 H 指向最近邻"的朴素做法相比，关键差别有两点：
      1. 供体受体做**全局匹配**（每个受体接受数有上限，且禁止互相双投）；
         互相双投正是"H 迎面对撞到 1.0 Å"的根因。
      2. 取向由"硬约束优先 + 解析对准 + 随机搜索"决定，且非键合下限与
         check_geometry.nonbonded_floor 完全共用同一套定义。
    """

    def __init__(self, cell, existing, cfg=None):
        self.cell = cell
        self.inv = inv3(cell)
        self.existing = list(existing)
        self.cfg = dict(cfg or {})
        self.floor_cfg = dict(FLOOR_DEFAULTS)
        self.floor_cfg.update(self.cfg.get("floor", {}))
        self.acceptors = set(self.cfg.get("acceptor_elements", list(E.HBOND_ACCEPTOR_ELEMENTS)))
        self.accept_max = self.cfg.get("hbond_accept_max", 2)
        self.hbond_h_max = self.cfg.get("hbond_h_max", 2.50)
        # 目标距中心 d 时，H 到受体最近约 d - xh；要让氢键落在 2.4 Å 内需 d <= 3.36
        self.donor_cutoff = self.cfg.get("donor_cutoff", 3.30)
        self.angle_min = self.floor_cfg["hbond_angle_min"]

    # ---- 周期距离（分数坐标版，避免重复求逆） -----------------------------
    def _frac(self, p):
        return cart_to_frac(p, self.inv)

    def _cart(self, f):
        return frac_to_cart(f, self.cell)

    def _d_frac(self, fa, fb):
        d = [fa[k] - fb[k] for k in range(3)]
        d = [x - round(x) for x in d]
        return math.sqrt(sum(x * x for x in self._cart(d)))

    def dist(self, p, q):
        return self._d_frac(self._frac(p), self._frac(q))

    def _angle_frac(self, donor_f, hf, acc_f):
        """以 H 为顶点的 D-H...A 角（最小镜像），与门限的氢键判据完全一致。"""
        v1 = self._cart([(donor_f[k] - hf[k]) - round(donor_f[k] - hf[k]) for k in range(3)])
        v2 = self._cart([(acc_f[k] - hf[k]) - round(acc_f[k] - hf[k]) for k in range(3)])
        n1 = math.sqrt(sum(x * x for x in v1))
        n2 = math.sqrt(sum(x * x for x in v2))
        if n1 < 1e-9 or n2 < 1e-9:
            return 0.0
        c = max(-1.0, min(1.0, sum(v1[k] * v2[k] for k in range(3)) / (n1 * n2)))
        return math.degrees(math.acos(c))

    def _floor(self, si, sj):
        return nonbonded_floor(si, sj, self.floor_cfg)

    # ---- 打分 -------------------------------------------------------------
    def score(self, hfrac, others_frac, assigned_frac):
        """返回 (硬违反数, 软惩罚)。硬违反优先降到 0。"""
        hard, pen = 0, 0.0
        for hf in hfrac:
            for el, pf in others_frac:
                d = self._d_frac(hf, pf)
                fl = self._floor("H", el)
                if d < fl:
                    hard += 1
                    pen += 40.0 * (fl - d) ** 2
        for af in assigned_frac:
            best = min(self._d_frac(hf, af) for hf in hfrac)
            if best > 2.40:
                pen += 20.0 * (best - 2.40) ** 2
        return hard, pen

    # ---- 候选取向 ---------------------------------------------------------
    def candidates(self, dirs, central, targets, n_random, seed):
        out = []
        u = []
        for t in targets:
            df = self._frac(t)
            dc = self._frac(central)
            d = [df[k] - dc[k] for k in range(3)]
            d = [x - round(x) for x in d]
            v = self._cart(d)
            n = math.sqrt(sum(x * x for x in v))
            if n > 1e-9:
                u.append([x / n for x in v])
        if len(u) == 1:
            base = rotation_from(dirs[0], u[0])
            out.append(base)
            for deg in range(0, 360, 15):
                out.append(_mm(rot_about(u[0], math.radians(deg)), base))
        elif len(u) >= 2:
            out.append(align_two(dirs[0], dirs[1], u[0], u[1]))
            out.append(align_two(dirs[1], dirs[0], u[0], u[1]))
        out.extend(random_rotations(n_random, seed))
        return out

    def best_orientation(self, template, central, targets, others_frac, n_random, seed,
                         neighbor_mols=(), accept_cap=True):
        dirs = local_h_directions(template)
        xh = template["xh"]
        cfrac = self._frac(central)
        tgt_frac = [self._frac(t) for t in targets]

        # 受体已接受数：与门限同一定义（距离 + D-H...A 角）
        acc_pool = [(k, pf) for k, (el, pf) in enumerate(others_frac) if el in self.acceptors]
        base_accept = {}
        if accept_cap:
            for k, pf in acc_pool:
                cnt = 0
                for donor_f, hs in neighbor_mols:
                    for hf in hs:
                        if self._d_frac(hf, pf) <= self.hbond_h_max and \
                           self._angle_frac(donor_f, hf, pf) >= self.angle_min:
                            cnt += 1
                base_accept[k] = cnt

        best, best_key = None, None
        for attempt, count in enumerate((n_random, n_random * 4)):
            for R in self.candidates(dirs, central, targets, count, seed + 31 * attempt):
                hpos = [[central[k] + xh * _mv(R, d)[k] for k in range(3)] for d in dirs]
                hfrac = [self._frac(h) for h in hpos]
                hard, pen = self.score(hfrac, others_frac, tgt_frac)
                if accept_cap:
                    add = {}
                    for hf in hfrac:
                        for k, pf in acc_pool:
                            if self._d_frac(hf, pf) <= self.hbond_h_max and \
                               self._angle_frac(cfrac, hf, pf) >= self.angle_min:
                                add[k] = add.get(k, 0) + 1
                    hard += sum(1 for k, c in add.items()
                                if base_accept.get(k, 0) + c > self.accept_max)
                key = (hard, pen)
                if best_key is None or key < best_key:
                    best, best_key = hpos, key
            if best_key[0] == 0:
                break
        return best, best_key

    # ---- 全局供体匹配 -----------------------------------------------------
    def assign_targets(self, sites, n_slots):
        n = len(sites)
        frac = [self._frac(p) for p in sites]
        pairs = []
        for i in range(n):
            for j in range(n):
                if i == j:
                    continue
                d = self._d_frac(frac[i], frac[j])
                if d <= self.donor_cutoff:
                    pairs.append((d, i, j))
        pairs.sort()
        targets = [[] for _ in range(n)]
        accept = [0] * n
        for d, i, j in pairs:
            if len(targets[i]) >= n_slots:
                continue
            if accept[j] >= self.accept_max:
                continue
            if j in targets[i]:
                continue
            # 禁止互相双投：对方已经在向本分子投氢时，本分子不能再投回去
            if i in targets[j]:
                continue
            targets[i].append(j)
            accept[j] += 1
        return targets

    def run(self, template, sites, donor_targets=None, passes=3, n_random=240, seed=0, log=None):
        dirs = local_h_directions(template)
        mols = [{"central": s, "H": None} for s in sites]
        existing_frac = [(el, self._frac(p)) for el, p in self.existing]

        def others_for(i):
            out = list(existing_frac)
            nm = []
            for j, m in enumerate(mols):
                if j == i:
                    continue
                cf = self._frac(m["central"])
                hs = [self._frac(h) for h in (m["H"] or [])]
                nm.append((cf, hs))
                out.append((template["central"], cf))
                for hf in hs:
                    out.append(("H", hf))
            return out, nm

        for p in range(passes):
            tg = donor_targets if donor_targets is not None else self.assign_targets(sites, len(dirs))
            for i in range(len(mols)):
                targets = [sites[j] for j in tg.get(i, [])] if isinstance(tg, dict) else \
                          [sites[j] for j in tg[i]]
                others, nm = others_for(i)
                hpos, key = self.best_orientation(template, mols[i]["central"], targets,
                                                  others, n_random, seed + 977 * p + i,
                                                  neighbor_mols=nm)
                mols[i]["H"] = hpos
            if log:
                log("pass %d 完成" % (p + 1))
        return mols


# --------------------------------------------------------------- 便捷入口 ----
def pack_solvent(cell, sites, template=WATER, existing=(), donor_targets=None,
                 passes=3, n_random=240, seed=0, cfg=None, log=None):
    return Packer(cell, existing, cfg).run(template, sites, donor_targets, passes,
                                           n_random, seed, log)


def hex_sites(cell, n_per_layer, seed_xy=(0.5, 0.5), spacing=0.35):
    """在一个 2D 周期晶胞里生成 n 个准均匀面内位点。

    做法: 细三角格点 -> 折叠进晶胞并用哈希去重 -> 最远点采样(FPS)。
    复杂度 O(N_cand * n)，与晶胞大小线性相关。
    """
    c2 = [cell[0][:2], cell[1][:2]]
    det = c2[0][0] * c2[1][1] - c2[0][1] * c2[1][0]

    def to_frac(v):
        return [((c2[1][1] * v[0] - c2[1][0] * v[1]) / det),
                ((-c2[0][1] * v[0] + c2[0][0] * v[1]) / det)]

    def to_cart(f):
        return [f[0] * c2[0][0] + f[1] * c2[1][0], f[0] * c2[0][1] + f[1] * c2[1][1]]

    # 覆盖一个基本域所需的格点范围
    reach = max(abs(c2[0][0]) + abs(c2[1][0]), abs(c2[0][1]) + abs(c2[1][1])) + 2 * spacing
    nmax = int(reach / spacing) + 2
    seen, cands = set(), []
    for n1 in range(-nmax, nmax + 1):
        for n2 in range(-nmax, nmax + 1):
            v = [n1 * spacing + n2 * spacing * 0.5, n2 * spacing * math.sqrt(3) / 2]
            f = [x - math.floor(x) for x in to_frac(v)]
            key = (round(f[0], 5) % 1.0, round(f[1], 5) % 1.0)
            if key in seen:
                continue
            seen.add(key)
            cands.append(f)

    def mi(a, b):
        df = [x - round(x) for x in (a[0] - b[0], a[1] - b[1])]
        v = to_cart(df)
        return math.sqrt(v[0] ** 2 + v[1] ** 2)

    sel = [min(range(len(cands)), key=lambda i: mi(cands[i], list(seed_xy)))]
    while len(sel) < min(n_per_layer, len(cands)):
        far = max((i for i in range(len(cands)) if i not in sel),
                  key=lambda i: min(mi(cands[i], cands[j]) for j in sel))
        sel.append(far)
    return [tuple(to_cart(cands[i])) for i in sel]


# --------------------------------------------------------------- 自测 -------
def _selftest():
    cu_a = 3.615
    n = 4
    # 4x4 Cu(111) 面内晶胞
    a1 = [n * cu_a / math.sqrt(2), 0.0]
    a2 = [n * cu_a / math.sqrt(2) / 2, n * cu_a / math.sqrt(2) * math.sqrt(3) / 2]
    cell = [[a1[0], a1[1], 0.0], [a2[0], a2[1], 0.0], [0.0, 0.0, 30.0]]
    area = abs(a1[0] * a2[1] - a1[1] * a2[0])

    n_mol = 18
    rho = E.LIQUID_NUMBER_DENSITY["H2O"]
    thickness = n_mol / (area * rho)
    n_layers = max(1, round(thickness / 2.90) + 1)
    per_layer = n_mol // n_layers
    print("面积 %.2f Å², 目标厚度 %.3f Å -> %d 层 x %d 分子" % (area, thickness, n_layers, per_layer))

    sites = []
    for li in range(n_layers):
        for (x, y) in hex_sites(cell, per_layer, seed_xy=(0.5 + 0.11 * li, 0.5 + 0.07 * li)):
            sites.append((x, y, 3.4 + li * 2.90))
    sites = sites[:n_mol]

    mols = pack_solvent(cell, sites, WATER, existing=[], passes=3, n_random=240, seed=1,
                        log=lambda m: print("  " + m))

    atoms, owner = [], []
    for mi, m in enumerate(mols):
        atoms.append(("O", m["central"]))
        owner.append(mi)
        for h in m["H"]:
            atoms.append(("H", h))
            owner.append(mi)
    g = Geom(cell, [p for _, p in atoms], [e for e, _ in atoms])
    D = g.dist_matrix()
    # 只统计分子间 H···H（分子内 H-O-H 的 H···H 本就约 1.5 Å，不是缺陷）
    hh = min((D[i][j], i, j) for i in range(len(atoms)) for j in range(i + 1, len(atoms))
             if atoms[i][0] == "H" and atoms[j][0] == "H" and owner[i] != owner[j])
    zh = [p[2] for e, p in atoms]
    rho_out = n_mol / (area * (max(zh) - min(zh)))
    floor = nonbonded_floor("H", "H", FLOOR_DEFAULTS)
    print("H···H 最小 = %.4f Å (共用下限 %.4f)" % (hh[0], floor))
    print("溶剂数密度 = %.5f Å⁻³ = %.3f × 体相" % (rho_out, rho_out / rho))
    ok = hh[0] >= floor and 0.75 <= rho_out / rho <= 1.35
    print("自测: %s" % ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser(description="通用氢键溶剂层排布器")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    ap.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
