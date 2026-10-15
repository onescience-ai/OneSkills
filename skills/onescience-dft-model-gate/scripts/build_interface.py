#!/usr/bin/env python3
"""确定性界面构建器：fcc(111) slab + 多层均匀水膜 + 吸附物 + 离子 -> POSCAR（形态 A 仅结构）。

    python3 build_interface.py --contract model_contract.json --out structures/POSCAR

设计要点（与 check_geometry.py 门限共用同一套口径，避免"建的"和"查的"打架）：
  * 水分子数优先取契约 species.H2O.count；未给时按 N = A·ρ·t 反算（t = 水膜区厚度）。
  * 水膜子层数 = max(契约 layers_min, 由膜区厚度反推)，**禁止减层凑密度**；
    层内位点用 hbond_pack.hex_sites 准均匀排布，取向用 pack_solvent 全局供体-受体匹配。
  * 首层水 O 与金属顶层留足非键合余量；CO2 取层间空位、K 取水膜上部空隙
    （按门限下限做可行点搜索），位点先按非键合下限过滤再排布。
  * 输出元素顺序取契约 output_species_order（默认 H C O K Cu），Direct 坐标 wrap 到 [0,1)。
  * 底部 fix_bottom_layers 层金属置 F F F（Selective dynamics）。
  * 全程固定 seed，同契约同参数必得同一文件（可复现/可比对 sha256）。

纯标准库 + 同目录 hbond_pack/elements，无 ASE 依赖。
"""

import argparse
import json
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import elements as E  # noqa: E402
import hbond_pack as HP  # noqa: E402

# 参考基准晶胞（Cu(111) 4x4，a_lat=3.6147 Å）；可用 CLI 覆盖
DEFAULT_CELL = [[8.854171, -5.111956, 0.0],
                [0.0, 10.223915, 0.0],
                [0.0, 0.0, 35.0]]
RHO_WATER = 0.033429          # 体相水数密度 Å^-3 (~1 g/cm3)
LAYER_SPACING = 2.6           # 水膜子层间距目标 Å
CO2_BOND = 1.16
# 位点过滤用的最小间距（与 check_geometry 的 nonbonded_floor 同源并留余量）；
# O_co2 取 1.75：高于 O-O 成键判定线 1.65，否则六方格点上 CO2 取向无法避开所有水位；
# K 取 3.20：非环水推到此距离外，其 H 背向 K 时 H···K 才能稳定超过 3.16 下限
# （环水在 r_ring=2.95 显式放置，不受此过滤影响，CN 由环水锁定为 6）。
SITE_MIN = {"C": 1.90, "O_co2": 1.75, "K": 3.20, "Cu": 2.60}
WAT_MIN = 2.55                  # 水分子 O-O 互间距下限（短氢键距离）：再紧会让 H 碰撞无解
N_RING = 6                      # K 第一水合壳水分子数（顶层即水合壳；环上弦距 2.95 Å）


def inv3(m):
    d = (m[0][0] * (m[1][1] * m[2][2] - m[1][2] * m[2][1])
         - m[0][1] * (m[1][0] * m[2][2] - m[1][2] * m[2][0])
         + m[0][2] * (m[1][0] * m[2][1] - m[1][1] * m[2][0]))
    return [
        [(m[1][1] * m[2][2] - m[1][2] * m[2][1]) / d, (m[0][2] * m[2][1] - m[0][1] * m[2][2]) / d,
         (m[0][1] * m[1][2] - m[0][2] * m[1][1]) / d],
        [(m[1][2] * m[2][0] - m[1][0] * m[2][2]) / d, (m[0][0] * m[2][2] - m[0][2] * m[2][0]) / d,
         (m[0][2] * m[1][0] - m[0][0] * m[1][2]) / d],
        [(m[1][0] * m[2][1] - m[1][1] * m[2][0]) / d, (m[0][1] * m[2][0] - m[0][0] * m[2][1]) / d,
         (m[0][0] * m[1][1] - m[0][1] * m[1][0]) / d],
    ]


def to_frac(r, inv):
    return [sum(r[d] * inv[d][k] for d in range(3)) for k in range(3)]


def dmin(p, others):
    return min(math.sqrt(sum((p[k] - q[k]) ** 2 for k in range(3))) for q in others)


def build(contract, cell=None, seed=0):
    cell = cell or [list(v) for v in DEFAULT_CELL]
    species = contract.get("species", {})
    slab = contract.get("slab", {})
    n_layers_slab = slab.get("layers", 4)
    fix_layers = slab.get("fix_bottom_layers", 2)
    vacuum = slab.get("vacuum_min", 15.0)
    c = math.sqrt(sum(x * x for x in cell[2]))
    inv = inv3(cell)

    # ---- slab：fcc(111) ABC 堆垛，4x4 超胞 ----
    a_par = math.sqrt(sum(x * x for x in cell[1]))
    a_lat = a_par * math.sqrt(2) / 4.0
    d111 = a_lat / math.sqrt(3)
    z0 = 2.0
    cu, cu_fix, cu_top = [], [], []
    for k in range(n_layers_slab):
        off = (k % 3) / 12.0                      # (a1+a2)/3 的超胞分数表示
        z = z0 + k * d111
        for i in range(4):
            for j in range(4):
                f = [i / 4.0 + off, j / 4.0 + off, 0.0]
                cart = [f[0] * cell[0][m] + f[1] * cell[1][m] + z * (1 if m == 2 else 0)
                        for m in range(3)]
                cu.append(cart)
                cu_fix.append(k < fix_layers)
                if k == n_layers_slab - 1:
                    cu_top.append(cart)
    ztop_slab = z0 + (n_layers_slab - 1) * d111

    # ---- 水膜区：首层留非键合余量，顶层留 H 与真空 ----
    area = math.sqrt(sum(x * x for x in [
        cell[0][1] * cell[1][2] - cell[0][2] * cell[1][1],
        cell[0][2] * cell[1][0] - cell[0][0] * cell[1][2],
        cell[0][0] * cell[1][1] - cell[0][1] * cell[1][0]]))
    z1 = ztop_slab + 2.9                          # 首层 O 中心：H 朝下仍够非键合下限
    z_last = c - vacuum - 0.96                    # 顶层 O 中心：H 朝上不侵真空
    span = z_last - z1
    spec_w = species.get("H2O", {})
    t = span + 2.7                                # 门限同口径膜厚（重原子跨度+最近邻）
    n_water = spec_w.get("count") or int(round(area * RHO_WATER * t))
    layers_min = spec_w.get("layers_min", 3)
    n_layers = max(layers_min, int(round(span / LAYER_SPACING)) + 1)
    step = span / (n_layers - 1)
    # 顶层 = K 第一水合壳（N_RING 个水环布），其余水均分到下面各层；
    # K 与格点水混排同层会被排他盘挤进窄缝导致 H 碰撞
    n_ring = N_RING
    rest = n_water - n_ring
    # 首层受 CO2 合并排他盘（半径 CO2_BOND+O_co2≈2.91 > 晶格间距）削去中心+6近邻，
    # 容量最小，故首层份额下调；顶层是 K 水合壳（n_ring）。
    per0 = max(1, rest // (n_layers - 1) - 2)
    mid = rest - per0
    n_mid = n_layers - 2
    per = [per0] + [mid // n_mid] * n_mid
    for k in range(mid % n_mid):
        per[1 + k] += 1
    per.append(n_ring)

    # ---- 周期最小镜像距离 + 面内正交基（CO2 取向与 K 水合环共用）----
    def d3(p, q):
        """周期最小镜像距离——位点过滤/校验必须用这个口径，
        裸笛卡尔距离会被跨边界镜像骗过（门限是周期感知的）。"""
        fp, fq = to_frac(p, inv), to_frac(q, inv)
        df = [fp[m] - fq[m] for m in range(3)]
        df = [x - round(x) for x in df]
        return math.sqrt(sum(sum(df[k] * cell[k][m] for k in range(3)) ** 2
                             for m in range(3)))

    a1n = math.sqrt(sum(x * x for x in cell[0]))
    u = [x / a1n for x in cell[0]]
    proj = sum(cell[1][m] * u[m] for m in range(3))
    v = [cell[1][m] - proj * u[m] for m in range(3)]
    vn = math.sqrt(sum(x * x for x in v))
    v = [x / vn for x in v]

    # ---- 水膜位点池：用与晶胞共格的分数网格 (i/n1, j/n2) 生成候选。
    #      本晶胞是六方（|a1|=|a2|、夹角 120°），n=floor(|a|/WAT_MIN) 时网格
    #      间距 = |a|/n >= WAT_MIN，且完美周期无缝合（避免了非共格晶格折叠后
    #      在边界产生大量镜像近邻冲突），排他过滤后任取即满足互距，
    #      容量达理论上限。----
    b1n = math.sqrt(sum(x * x for x in cell[1]))
    n1 = max(1, int(a1n / WAT_MIN))
    n2 = max(1, int(b1n / WAT_MIN))
    base_frac = [(i / n1, j / n2) for i in range(n1) for j in range(n2)]
    pools = []
    for k in range(n_layers - 1):
        z = z1 + step * k
        pools.append([tuple(fx * cell[0][m] + fy * cell[1][m] + (z if m == 2 else 0)
                            for m in range(3)) for (fx, fy) in base_frac])

    # ---- CO2：占首层第一个格点（吸附质排开界面水，标准做法）；对水位的排他
    #      合并为"距 C >= CO2_BOND + O 排他半径"，几何上保证 O 距任何水 >= 1.75 Å，
    #      不再依赖取向躲避（FPS 前缀互距是裸距离假象，镜像口径下邻点可 < 2 Å）----
    z_c = ztop_slab + 3.35                        # 物理吸附接触 >= 0.90*(vdw 和) 门限
    # 取首层首个格点的 xy 作 CO2 面内位置，z 用绝对高度 z_c（不能叠加，
    # pools[0][0][2] 已是 z1）；否则 CO2 会飘到真空里。
    c_pos = [pools[0][0][m] if m < 2 else z_c for m in range(3)]

    # ---- K：对下层位点/CO2 最大化最小距离取空位，略沉入顶层水面下 ----
    k_z = z1 + step * (n_layers - 1) - 0.30
    lower_pts = [p for pool in pools for p in pool] + [c_pos]
    rng_k = random.Random(seed + 3)
    k_guess, best_s = None, -1.0
    for _ in range(800):
        f = [rng_k.random(), rng_k.random()]
        p = [f[0] * cell[0][m] + f[1] * cell[1][m] + k_z * (1 if m == 2 else 0)
             for m in range(3)]
        s = min(d3(p, q) for q in lower_pts)
        if s > best_s:
            best_s, k_guess = s, p

    # ---- K 第一水合壳：顶层平面内半径 2.95 Å 环布 n_ring 个水，整层即水合壳，
    #      配位数直接锁定在 [4,8]，环上水彼此间距 >= 2.9 Å 天然均匀 ----
    r_ring = 2.95   # K-O ≈ 2.96 ∈ [非键合下限 2.69, CN 截断 3.36]
    ring, ring_score = None, -1.0
    ring_ref = lower_pts
    for i in range(12):
        ph = 2 * math.pi * i / 12
        cand = []
        for j in range(n_ring):
            th = ph + 2 * math.pi * j / n_ring
            cand.append([k_guess[m] + r_ring * math.cos(th) * u[m]
                         + r_ring * math.sin(th) * v[m]
                         + 0.30 * (1 if m == 2 else 0) for m in range(3)])
        s = min(d3(p, q) for p in cand for q in ring_ref)
        if s > ring_score:
            ring_score, ring = s, cand

    # ---- 水位选取：直接按 hex_sites 的 FPS 顺序过滤（池点已按最大铺开
    #      排序，取前 per[k] 个满足排他与同层互距 >= WAT_MIN 的点即可），
    #      无需再做一遍昂贵的 farthest-first；对排他删点也鲁棒。
    #      排他：CO2 合并盘 / K / 顶层 Cu / 环水 ----
    cz_need = CO2_BOND + SITE_MIN["O_co2"]

    def site_ok(p):
        if d3(p, c_pos) < cz_need:
            return False
        if d3(p, k_guess) < SITE_MIN["K"]:
            return False
        if min(d3(p, q) for q in cu_top) < SITE_MIN["Cu"]:
            return False
        if min(d3(p, q) for q in ring) < WAT_MIN:
            return False
        return True

    sites = []
    for k in range(n_layers - 1):
        cands = [p for p in pools[k] if site_ok(p)]
        kept = []
        while len(kept) < per[k] and cands:           # 纯最远优先贪心（近似六方密堆）
            p = max(cands, key=lambda q: min(d3(q, r) for r in kept)) if kept else cands[0]
            cands.remove(p)
            if all(d3(p, q) >= WAT_MIN for q in kept):
                kept.append(p)
        if len(kept) < per[k]:
            raise SystemExit("第 %d 层过滤后位点不足 (%d/%d)，请调整 seed 或晶胞"
                             % (k, len(kept), per[k]))
        sites.extend(kept)
    sites.extend(ring)

    # ---- CO2 取向：对实际水位取"两个 O 最小距离最大"的面内方向（氢键网络更优）----
    best_e, best_sc = None, -1.0
    for i in range(24):
        th = 2 * math.pi * i / 24
        e = [math.cos(th) * u[m] + math.sin(th) * v[m] for m in range(3)]
        sc = min(d3([c_pos[m] + s * CO2_BOND * e[m] for m in range(3)], w)
                 for s in (1, -1) for w in sites)
        if sc > best_sc:
            best_sc, best_e = sc, e
    co2 = [("C", c_pos),
           ("O", [c_pos[m] + CO2_BOND * best_e[m] for m in range(3)]),
           ("O", [c_pos[m] - CO2_BOND * best_e[m] for m in range(3)])]

    pack_blockers = [(s, p) for s, p in co2] + [("K", k_guess)] + \
                    [("Cu", p) for p in cu_top]

    mols = HP.pack_solvent(cell, sites, HP.WATER, existing=pack_blockers,
                           passes=8, n_random=240, seed=seed)
    if any(m["H"] is None for m in mols):
        raise SystemExit("水排布失败：存在未取向分子，请调整 seed 或层数")

    # ---- 定向修复：取向搜索在紧位点可能返回"硬冲突未清零的次优解"
    #      （H 压到邻近 O 上→键长/计数/非键合连环 FAIL）。这里只挑出仍有冲突的
    #      水，用高 n_random 逐个重取向，Gauss-Seidel 迭代到干净；不赌幸运 seed。----
    tmpl = HP.WATER
    dirs = HP.local_h_directions(tmpl)
    hh_floor = HP.nonbonded_floor("H", "H", HP.FLOOR_DEFAULTS)
    packer = HP.Packer(cell, pack_blockers)
    existing_frac = [(el, packer._frac(p)) for el, p in pack_blockers]
    tg = packer.assign_targets(sites, len(dirs))

    def _others_for(i):
        out = list(existing_frac)
        nm = []
        for j, m in enumerate(mols):
            if j == i:
                continue
            cf = packer._frac(m["central"])
            hs = [packer._frac(h) for h in (m["H"] or [])]
            nm.append((cf, hs))
            out.append((tmpl["central"], cf))
            for hf in hs:
                out.append(("H", hf))
        return out, nm

    def _bad_mols():
        """返回存在非键合硬冲突的分子索引：H···H < hh_floor（跨分子）
        或 H···重原子（非本分子 O / 阻断重原子）< 对应非键合下限。"""
        bad = set()
        Hs = [(i, h) for i, m in enumerate(mols) for h in (m["H"] or [])]
        for a in range(len(Hs)):
            ia, ha = Hs[a]
            for b in range(a + 1, len(Hs)):
                ib, hb = Hs[b]
                if ia == ib:
                    continue
                if d3(ha, hb) < hh_floor:
                    bad.add(ia); bad.add(ib)
        heavy = [("O", m["central"], j) for j, m in enumerate(mols)] + \
                [(el, p, -1) for el, p in pack_blockers]
        for i, m in enumerate(mols):
            for h in m["H"]:
                for el, p, owner in heavy:
                    if el == "O" and owner == i:
                        continue                       # 本分子 O-H 键，恒 0.96
                    fl = HP.nonbonded_floor("H", el, HP.FLOOR_DEFAULTS)
                    if d3(h, p) < fl:
                        bad.add(i)
                        if owner >= 0:
                            bad.add(owner)
        return bad

    for _it in range(12):
        bad = _bad_mols()
        if not bad:
            break
        for i in sorted(bad):
            targets = [sites[j] for j in tg[i]]
            others, nm = _others_for(i)
            hpos, _key = packer.best_orientation(
                tmpl, mols[i]["central"], targets, others, 2000,
                seed + 977 * _it + i, neighbor_mols=nm)
            mols[i]["H"] = hpos
    else:
        raise SystemExit("水取向定向修复未收敛：残留非键合硬冲突，请调整 seed 或层数")

    wO = [m["central"] for m in mols]
    wH = [h for m in mols for h in m["H"]]

    # ---- K 终位：先校验占位点，不满足再在水膜上部搜索空隙 ----
    floor_ok = 1.0 * (E.covalent("K") + E.covalent("O"))
    cutoff = 1.25 * floor_ok
    kc_floor = 1.0 * (E.covalent("K") + E.covalent("C"))
    win = species.get("K", {}).get("coordination_range", [4, 8])

    def k_feasible(p):
        if min(d3(p, q) for q in wO) < floor_ok:
            return False
        if min(d3(p, q) for q in wH) < 3.16:
            return False
        if min(d3(p, q) for _, q in co2) < kc_floor:
            return False
        cn = sum(1 for q in wO if d3(p, q) <= cutoff)
        return win[0] <= cn <= win[1]

    k_pos = k_guess if k_feasible(k_guess) else None
    if k_pos is None:
        rng2 = random.Random(seed + 2)
        for _ in range(40000):
            f = [rng2.random(), rng2.random()]
            z = z1 + span * rng2.uniform(0.35, 1.0)
            p = [f[0] * cell[0][m] + f[1] * cell[1][m] + z * (1 if m == 2 else 0)
                 for m in range(3)]
            if k_feasible(p):
                k_pos = p
                break
    if k_pos is None:
        raise SystemExit("K 位点校验/搜索失败：无满足非键合下限与配位区间 %s 的位点，请调整 seed" % (win,))

    # ---- 汇总并按 output_species_order 输出 ----
    atoms = {"H": [], "C": [], "O": [], "K": [], "Cu": []}
    flags = {"H": [], "C": [], "O": [], "K": [], "Cu": []}
    for m in mols:
        atoms["O"].append(m["central"]); flags["O"].append(False)
        for h in m["H"]:
            atoms["H"].append(h); flags["H"].append(False)
    atoms["C"].append(c_pos); flags["C"].append(False)
    for s, p in co2[1:]:
        atoms[s].append(p); flags[s].append(False)
    atoms["K"].append(k_pos); flags["K"].append(False)
    for p, fx in zip(cu, cu_fix):
        atoms["Cu"].append(p); flags["Cu"].append(fx)

    order = contract.get("output_species_order") or ["H", "C", "O", "K", "Cu"]
    lines = ["CO2 + K + %d H2O on Cu(111) 4x4x%d (form A: POSCAR only)" % (n_water, n_layers_slab),
             "1.0"]
    lines += ["%.6f %.6f %.6f" % tuple(v) for v in cell]
    lines.append(" ".join(order))
    lines.append(" ".join(str(len(atoms[s])) for s in order))
    lines.append("Selective dynamics")
    lines.append("Direct")
    for s in order:
        for p, fx in zip(atoms[s], flags[s]):
            f = [round(v, 6) % 1.0 for v in to_frac(p, inv)]
            tag = "F F F" if fx else "T T T"
            lines.append("%.6f %.6f %.6f %s" % (f[0], f[1], f[2], tag))
    return "\n".join(lines) + "\n", {
        "n_water": n_water, "n_layers": n_layers, "per_layer": per,
        "z1": z1, "step": step, "counts": {s: len(atoms[s]) for s in order},
    }


def main():
    ap = argparse.ArgumentParser(description="确定性界面构建器（形态 A 仅 POSCAR）")
    ap.add_argument("--contract", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--seed", type=int, default=0)
    a = ap.parse_args()
    contract = json.load(open(a.contract, encoding="utf-8"))
    text, info = build(contract, seed=a.seed)
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    open(a.out, "w", encoding="utf-8").write(text)
    print("POSCAR: %s" % os.path.abspath(a.out))
    print("水分子 %d / %d 子层 %s | 首层 z=%.2f 层距 %.2f Å | 计数 %s"
          % (info["n_water"], info["n_layers"], info["per_layer"],
             info["z1"], info["step"], info["counts"]))


if __name__ == "__main__":
    sys.exit(main())
