#!/usr/bin/env python3
"""VASP 输入文件一致性检查（纯标准库）。

    python3 check_vasp_inputs.py --poscar structures/POSCAR --potcar vasp_templates/POTCAR \
        --incar vasp_templates/INCAR --kpoints vasp_templates/KPOINTS

回答的问题是"这套输入能不能直接提交，还是会在几小时后给出不可信的数"：
  * POSCAR 元素顺序与 POTCAR 段顺序是否一致（错了 VASP 会静默算错）
  * ENCUT 是否真的覆盖 POTCAR 里的 ENMAX（从 POTCAR 现算，不信任 INCAR 注释）
  * 金属体系 + 色散/偶极修正等关键开关是否与体系性质匹配
  * K 点密度对当前晶胞是否过疏

退出码: 0 = PASS（可有 WARN）, 1 = 有 FAIL, 2 = 输入错误。
"""

import argparse
import math
import os
import re
import sys

RECOMMENDED = {
    "slab_dipole": ["LDIPOL", "IDIPOL"],
    "dispersion": ["IVDW", "LUSE_VDW", "VDW_SR"],
}


def parse_poscar_species(path):
    raw = open(path).read().splitlines()
    i = 5
    tok = raw[i].split()
    if any(re.search(r"[A-Za-z]", t) for t in tok):
        order, i = tok, i + 1
    else:
        order = raw[0].split()
    counts = [int(x) for x in raw[i].split()]
    cell = [[float(x) for x in raw[k].split()[:3]] for k in (2, 3, 4)]
    return order, counts, cell


def parse_potcar(path):
    txt = open(path).read()
    titels = re.findall(r"TITEL\s*=\s*(\S+)\s+(\S+)\s+(\S+)", txt)
    enmax = [float(x) for x in re.findall(r"ENMAX\s*=\s*([0-9.]+)", txt)]
    zval = [float(x) for x in re.findall(r"ZVAL\s*=\s*([0-9.]+)", txt)]
    datasets = txt.count("End of Dataset")
    species = []
    for t in titels:
        el = t[1]
        # K_pv / Cu_pv / Fe_pv 之类 -> 元素符号
        species.append(el.split("_")[0])
    return {"species": species, "enmax": enmax, "zval": zval, "datasets": datasets,
            "titels": [" ".join(t) for t in titels]}


def parse_incar(path):
    out = {}
    if not path or not os.path.isfile(path):
        return out
    for line in open(path):
        line = line.split("#")[0].split("!")[0].strip()
        if not line or "=" not in line:
            continue
        k, _, v = line.partition("=")
        out[k.strip().upper()] = v.strip()
    return out


def parse_kpoints(path):
    """按 VASP 语义解析 KPOINTS。

    VASP 约定: 第 1 行自由注释, **第 2 行必须是 Nk**（0 = 自动网格）。
    多写一行注释会让 VASP 把文字当成整数读取而直接失败，因此这里显式校验行序。
    """
    if not path or not os.path.isfile(path):
        return None
    raw = [l.rstrip("\n") for l in open(path)]
    lines = [l for l in raw if l.strip() and not l.strip().startswith(("#", "!"))]
    if len(lines) < 3:
        return {"format_ok": False, "reason": "有效行数不足 (<3)", "n_lines": len(lines)}
    tok = lines[1].split()
    nk_ok = bool(tok) and re.fullmatch(r"[+-]?\d+", tok[0]) is not None
    out = {"format_ok": nk_ok, "line2": lines[1].strip(),
           "n_comment_lines": len([l for l in raw if l.strip()]) - len(lines)}
    if not nk_ok:
        out["reason"] = "第 2 行不是整数 Nk: %r" % lines[1].strip()
        return out
    nk = int(tok[0])
    out["nk"] = nk
    if nk == 0:
        out["mode"] = lines[2].strip()
        out["mesh"] = [int(x) for x in re.split(r"\s+", lines[3].strip())[:3]] if len(lines) > 3 else None
    else:
        out["mode"] = "explicit"
        out["mesh"] = None
    return out


def main():
    ap = argparse.ArgumentParser(description="VASP 输入一致性检查")
    ap.add_argument("--poscar", required=True)
    ap.add_argument("--potcar")
    ap.add_argument("--incar")
    ap.add_argument("--kpoints")
    ap.add_argument("--metal", choices=["auto", "yes", "no"], default="auto")
    ap.add_argument("--kpoints-min", type=float, default=25.0,
                    help="金属体系每个倒格矢方向的最小 k 点线密度 (Å)")
    ap.add_argument("--delivery-dir",
                    help="交付目录：核对文件集形态（A 仅 POSCAR / B 四件套齐），禁止半套")
    a = ap.parse_args()

    if not os.path.isfile(a.poscar):
        print("找不到 POSCAR: %s" % a.poscar)
        return 2

    items = []

    def add(gate, status, detail):
        items.append((status, gate, detail))

    order, counts, cell = parse_poscar_species(a.poscar)
    comp = dict(zip(order, counts))
    natoms = sum(counts)
    lens = [math.sqrt(sum(x * x for x in v)) for v in cell]
    add("I1 POSCAR", "PASS", "%d 原子 %s | 晶胞 %.3f x %.3f x %.3f Å"
        % (natoms, comp, lens[0], lens[1], lens[2]))

    incar = parse_incar(a.incar) if a.incar else {}
    pot = parse_potcar(a.potcar) if a.potcar and os.path.isfile(a.potcar) else None

    # ---- POTCAR 顺序与完整性 ----
    if pot:
        problems = []
        if pot["species"] != order:
            problems.append("元素顺序不一致: POSCAR %s vs POTCAR %s" % (order, pot["species"]))
        if pot["datasets"] != len(order):
            problems.append("POTCAR 段数 %d != 元素种类 %d" % (pot["datasets"], len(order)))
        if len(pot["enmax"]) != len(order):
            problems.append("ENMAX 条目数 %d != 元素种类 %d" % (len(pot["enmax"]), len(order)))
        add("I2 POTCAR 匹配", "FAIL" if problems else "PASS",
            "; ".join(problems) if problems else
            "顺序与段数一致: %s" % ", ".join(pot["titels"]))
    else:
        if a.incar or a.kpoints:
            add("I2 POTCAR 匹配", "FAIL",
                "缺 POTCAR 却交付了 INCAR/KPOINTS：半套交付被禁止（BLOCKED）。POTCAR 依赖 VASP 商业赝势库，"
                "不可伪造、无合法公开下载渠道；补救路径 ① 管理员将授权库放置到 PMG_VASP_PSP_DIR，"
                "② 用户上传授权 POTCAR 集；两者皆不可得时回落形态 A 仅交付 POSCAR（撤掉 INCAR/KPOINTS）。")
        else:
            add("I2 POTCAR 匹配", "INFO",
                "交付形态 A（仅 POSCAR）：本次不含 INCAR/KPOINTS，无需 POTCAR，此项不构成缺陷")

    # ---- ENCUT vs ENMAX，从 POTCAR 现算 ----
    if pot and pot["enmax"]:
        need = max(pot["enmax"])
        got = None
        if "ENCUT" in incar:
            try:
                got = float(incar["ENCUT"])
            except ValueError:
                got = None
        if got is None:
            add("I3 ENCUT", "FAIL",
                "INCAR 未设 ENCUT（或不可解析）；POTCAR 最大 ENMAX = %.1f eV，"
                "ENCUT 须 >= %.1f eV" % (need, 1.3 * need))
        elif got < need:
            add("I3 ENCUT", "FAIL", "ENCUT = %.1f < 最大 ENMAX %.1f eV" % (got, need))
        elif got < 1.3 * need:
            add("I3 ENCUT", "WARN",
                "ENCUT = %.1f 仅 %.2f x 最大 ENMAX %.1f eV（惯用 >= 1.3x = %.1f）"
                % (got, got / need, need, 1.3 * need))
        else:
            add("I3 ENCUT", "PASS",
                "ENCUT = %.1f = %.2f x 最大 ENMAX %.1f eV" % (got, got / need, need))
        add("I3b 赝势实际 ENMAX", "INFO",
            "; ".join("%s %.1f" % (s, e) for s, e in zip(pot["species"], pot["enmax"])))

    # ---- 金属体系关键开关（形态 A 无 INCAR 时降级为 INFO） ----
    if not a.incar:
        add("I4-INCAR 类开关", "INFO",
            "形态 A（未交付 INCAR）：smearing/色散/偶极/ISIF/ISYM 等开关在形态 B 交付 INCAR 时才校验")
    else:
        ismear = incar.get("ISMEAR")
        sigma = incar.get("SIGMA")
        if ismear is None:
            add("I4 金属 smearing", "WARN", "未设 ISMEAR；金属体系常用 ISMEAR=1/2 (或 -5)")
        elif ismear.strip() in ("0", "0.0"):
            add("I4 金属 smearing", "WARN",
                "ISMEAR=0 (Gaussian) 用于金属不理想，能量收敛慢且易偏差；"
                "金属惯用 ISMEAR=1/2，SIGMA=0.1-0.2（现 SIGMA=%s）" % sigma)
        else:
            add("I4 金属 smearing", "PASS", "ISMEAR=%s, SIGMA=%s" % (ismear, sigma))

    # ---- slab / 色散 ----
    has_h = "H" in order
    has_mol = any(el in order for el in ("C", "N", "O", "S")) and has_h
    if not a.incar:
        add("I5 色散修正", "INFO", "形态 A（未交付 INCAR）：色散开关在形态 B 才校验")
    elif "IVDW" not in incar and not any(k in incar for k in ("LUSE_VDW", "VDW_SR")):
        if has_mol:
            add("I5 色散修正", "FAIL",
                "体系含分子/吸附物且未开色散（IVDW / LUSE_VDW）；物理吸附能会被严重低估")
        else:
            add("I5 色散修正", "WARN", "未开色散修正，若含物理吸附需补 IVDW")
    else:
        add("I5 色散修正", "PASS", "已开: %s" % {k: incar[k] for k in
                                                 ("IVDW", "LUSE_VDW", "VDW_SR") if k in incar})

    if "LDIPOL" in incar or "IDIPOL" in incar:
        add("I6 偶极修正", "PASS", "LDIPOL=%s IDIPOL=%s" % (incar.get("LDIPOL"), incar.get("IDIPOL")))
    else:
        add("I6 偶极修正", "WARN", "slab 沿 z 常有净偶极，建议 LDIPOL=.TRUE. / IDIPOL=3")

    if incar.get("ISIF", "").strip() not in ("2", "2.0"):
        add("I7 ISIF", "WARN", "slab 几何优化通常 ISIF=2（只松弛离子）；当前 ISIF=%s" % incar.get("ISIF"))
    else:
        add("I7 ISIF", "PASS", "ISIF=2 (仅离子)")

    if incar.get("ISYM", "").strip() not in ("0",):
        if has_mol:
            add("I8 ISYM", "WARN", "含无序溶剂/吸附物建议 ISYM=0 以免对称化约束构型；当前 ISYM=%s"
                % incar.get("ISYM"))
        else:
            add("I8 ISYM", "INFO", "ISYM=%s" % incar.get("ISYM"))

    is_metal = (a.metal == "yes") or (a.metal == "auto" and any(
        el in {"Cu", "Ag", "Au", "Pt", "Pd", "Ni", "Fe", "Co", "Ru", "Rh", "Ir",
               "Os", "Mo", "W", "Cr", "Mn", "V", "Nb", "Ta", "Ti", "Zr", "Hf", "Al"}
        for el in order))

    # ---- K 点密度 ----
    kp = parse_kpoints(a.kpoints) if a.kpoints else None
    if kp is not None and not kp.get("format_ok", True):
        add("I0 KPOINTS 格式", "FAIL",
            "%s | VASP 第 2 行必须是 Nk(整数)；当前第 2 行是 %r。多余的前导注释行会让 VASP 读取失败，"
            "请把说明合并到第 1 行或删掉。" % (kp.get("reason", "格式错误"), kp.get("line2", "")))
        kp = None
    if kp and kp.get("mesh"):
        mesh = kp["mesh"]
        lengths = [l for l in lens]
        dens = [lengths[k] * mesh[k] for k in range(3)]
        detail = "mesh %s -> 各方向 %.1f / %.1f / %.1f Å" % (mesh, dens[0], dens[1], dens[2])
        if is_metal and min(dens[0], dens[1]) < a.kpoints_min:
            add("I9 K 点密度", "FAIL",
                detail + " | 金属 slab 面内 k 点线密度 < %.0f Å 偏疏，吸附能不可信；"
                "建议至少 %s" % (a.kpoints_min,
                                 [max(1, int(math.ceil(a.kpoints_min / l))) for l in lengths[:2]] + [1]))
        else:
            add("I9 K 点密度", "PASS", detail)
    elif kp:
        add("I9 K 点密度", "INFO", "显式 k 点或无法解析网格: %s" % kp.get("mode"))
    else:
        add("I9 K 点密度", "WARN", "未提供 KPOINTS")

    # ---- I10 交付形态（文件集一致性硬门限） ----
    if a.delivery_dir:
        found = set()
        for _root, _dirs, files in os.walk(a.delivery_dir):
            for fn in files:
                u = fn.upper()
                if u.startswith("POSCAR"):
                    found.add("POSCAR")
                elif u == "INCAR" or u.startswith("INCAR."):
                    found.add("INCAR")
                elif u == "KPOINTS" or u.startswith("KPOINTS."):
                    found.add("KPOINTS")
                elif u == "POTCAR" or u.startswith("POTCAR."):
                    found.add("POTCAR")
        half = ("INCAR" in found or "KPOINTS" in found) and "POTCAR" not in found
        if half:
            add("I10 交付形态", "FAIL",
                "交付目录文件集 %s 构成半套：有 INCAR/KPOINTS 而缺 POTCAR。交付形态只允许二选一："
                "A 仅 POSCAR；B 四件套齐且 POTCAR 通过 I2/I3。POTCAR 不可得（BLOCKED）时回落形态 A，"
                "删掉 INCAR/KPOINTS 后重新交付。" % sorted(found))
        elif "POSCAR" in found and {"INCAR", "KPOINTS", "POTCAR"} <= found:
            add("I10 交付形态", "PASS", "形态 B：四件套齐 %s" % sorted(found))
        elif "POSCAR" in found and not (found & {"INCAR", "KPOINTS", "POTCAR"}):
            add("I10 交付形态", "PASS",
                "形态 A：仅 POSCAR（model_contract/门限报告/构建脚本属过程证据，不计入输入件套）")
        else:
            add("I10 交付形态", "FAIL", "文件集形态无法识别: %s" % sorted(found))

    print("=== VASP 输入一致性检查 ===")
    print("poscar : %s" % os.path.abspath(a.poscar))
    print("potcar : %s" % (os.path.abspath(a.potcar) if a.potcar else "-"))
    print("incar  : %s" % (os.path.abspath(a.incar) if a.incar else "-"))
    print("kpoints: %s" % (os.path.abspath(a.kpoints) if a.kpoints else "-"))
    print("-" * 92)
    for st, gate, detail in items:
        print("[%-4s] %-20s %s" % (st, gate, detail))
    print("-" * 92)
    fails = [x for x in items if x[0] == "FAIL"]
    warns = [x for x in items if x[0] == "WARN"]
    print("结论: %s   (%d 项未通过, %d 项警告)" % ("FAIL" if fails else "PASS", len(fails), len(warns)))
    if fails:
        print("未通过: %s" % ", ".join(g for _, g, _ in fails))
        print("规则: FAIL 项必须在交付说明中作为已知问题列出，不得写成 PASS。")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
