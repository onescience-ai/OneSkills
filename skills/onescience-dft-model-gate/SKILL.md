---
name: onescience-dft-model-gate
description: "DFT/VASP 初始原子结构建模与交付门限。任一信号命中必用：(a) 表面/界面：Cu/Fe/Pt/Pd/Ni/Au/Ag/TiO2/MoS2/石墨烯/ZnO/CeO2 等 slab、(111)/(100)/(110)/(001) 晶面、异质结、界面建模；(b) 吸附/溶剂化：吸附物放置、CO2/CO/H2O/N2/OH/H/O 等分子加到表面、显式水/水层/水膜、电解质、溶剂化；(c) 掺杂/缺陷：K/Li/Na/Ca 掺杂、空位、取代、表面重构；(d) VASP 输入交付：POSCAR/CONTCAR/INCAR/KPOINTS/POTCAR、model_contract.json、selective dynamics、固定底部原子、ENCUT、赝势、几何合理性；(e) 场景关键词：初始模型、起始结构、建模交付、计算前验收、VASP 计算前。构建前必先写 model_contract.json，通过硬性验收门限才能提交。本技能为 executor 类型，通常由 onescience-orchestrator 调度；用户未点名时优先走 orchestrator 入口。"
type: executor
---

# DFT 模型就绪门限（onescience-dft-model-gate）

## 这个技能解决什么

用基座能力"手搓"一个原子结构并写一份说明，**在几何上看起来没问题、实际不可计算**，是这类任务的
高频失效模式。典型症状（都真实发生过）：

| 症状 | 本质 |
|---|---|
| 两个 H 相距 1.0 Å | 分子取向按"最近邻"硬投，互相为最近邻的分子把 H 迎面对撞 |
| 某个 O 接受 5 个氢键 | 没有全局供体-受体匹配，受体被过度配位 |
| 交付说明写"最近非键距离 ≥ 2.36 Å"，文件实测 1.01 Å | **校验数字不是在这份文件上跑出来的** |
| 吸附物 2.5 Å 落在金属原子上方，却标称"物理吸附" | 声明意图与几何矛盾，无人核对 |
| 水膜标称"非晶态/近液态"，实为两层完全共面 | 无维度/密度口径，靠形容词 |
| KPOINTS 多写一行注释 | VASP 第 2 行必须是 Nk，多余注释会让作业直接读失败 |
| INCAR 注释写"K_pv ~ 250 eV"，实际 116.7 eV | 注释是不可信的二手信息，必须从 POTCAR 现算 |

本技能把"交付前必须自证"变成**可执行的硬门限**，并且**物理门限与体系无关**（全部由元素半径数据推导），
体系相关的预期由一份声明式契约给出。换任何材料/分子/溶剂都能用，不需要改检查器。

## 强制流程

### 1. 先写 `model_contract.json`（建模之前，不是之后）

契约是"这个模型的物理预期"。检查器只核对几何是否满足你的声明，不替你猜意图。
完整字段见 `assets/model_contract.example.json`。最小可用形态：

```json
{
  "system": "<吸附物> on <载体>(hkl) with <溶剂>/<离子>",
  "output_species_order": ["H", "C", "O", "K", "Cu"],
  "delivery_form": "A",
  "framework": { "elements": ["Cu"] },
  "species": {
    "H2O": { "count": 40, "role": "solvent", "solvent_model": "liquid-film", "layers_min": 3 },
    "CO2": { "count": 1,  "role": "adsorbate", "mode": "physisorbed" },
    "K":   { "count": 1,  "role": "ion" }
  },
  "slab": { "layers": 4, "fix_bottom_layers": 2, "vacuum_min": 15 }
}
```

要点：

- `framework.elements` **必须声明**。否则吸附的金属离子（K/Cs/Na…）会被并进载体骨架，
  无法作为独立物种计数。
- `role` 决定跑哪一组门限：`solvent`（密度+氢键网络+不穿金属）、
  `adsorbate`（与骨架最短接触 vs 吸附模式）、`ion`（配位壳层）、`molecule`。
- `mode: "physisorbed"` 会按 `0.90 × (r_vdw(金属) + r_vdw(近端原子))` 推导最小接触距离。
  **化学吸附必须显式给 `min_contact` 或 `mode: "chemisorbed"`**，否则会被判 FAIL。
- `solvent_model`：`liquid-film`（按体相密度卡门限）/ `monolayer`（只报告密度，
  但必须同时给 `target_coverage`）/ `none`。**模型是什么就写什么**，不要用形容词。

### 2. 构建

建模脚本自便（ASE / 纯 Python / 手写均可）。唯一要求：**构建过程必须自己先满足契约**。
界面体系（slab + 液膜 + 吸附物 + 离子）优先用随附的确定性构建器，同契约同 seed 必得同一文件：

```bash
python3 .opencode/skills/onescience-dft-model-gate/scripts/build_interface.py \
        --contract model_contract.json --out structures/POSCAR
```

溶剂层是这类任务最容易写错的部分。**不要**用“每个分子把 H 指向最近邻”的写法，那是上表第 1、2 条
症状的根因；也**不要**用减层数去凑密度门限（水分子数按 `N = A·ρ·t` 反算，层数由契约 `layers_min`
兜底）。用随附的通用排布器：

```python
import sys; sys.path.insert(0, ".opencode/skills/onescience-dft-model-gate/scripts")
from hbond_pack import pack_solvent, WATER, hex_sites

sites = [(x, y, z) for z in layer_z for (x, y) in hex_sites(cell, n_per_layer)]
mols = pack_solvent(cell, sites, WATER, existing=[(sym, pos), ...],
                    passes=4, n_random=240, seed=0)
```

它做三件朴素写法不做的事：**全局供体-受体匹配**（每受体接受数有上限、禁止互相双投）、
**解析取向对准 + 随机搜索**、**与门限共用同一套非键合下限**。
自测：`python3 .opencode/skills/onescience-dft-model-gate/scripts/hbond_pack.py --selftest`。

### 3. 跑门限（在**最终交付的那份文件**上）

```bash
cd <项目根>
python3 .opencode/skills/onescience-dft-model-gate/scripts/check_geometry.py \
        structures/POSCAR --contract model_contract.json --json /tmp/gate.json

python3 .opencode/skills/onescience-dft-model-gate/scripts/check_vasp_inputs.py \
        --poscar structures/POSCAR --potcar vasp_templates/POTCAR \
        --incar vasp_templates/INCAR --kpoints vasp_templates/KPOINTS
```

门限输出自带 `sha256` 与完整命令行 —— 把它**原样贴进交付说明**，这样"被校验的文件"和
"交付的文件"在证据上被绑死。重新生成结构后必须重跑，不允许沿用上一次的输出。

### 4. 交付

- 报告里**原样包含**两个脚本的真实输出（含 sha256），不要摘抄或转述数字。
- FAIL 项必须写清楚：实测值、门限值、为什么、打算怎么改。**不允许把 FAIL 写成 PASS**，
  也不允许把没跑过的数字写成结论。
- INFO/WARN 项要说明是否可接受。

## 硬性规则

1. **没跑过门限的结构不得提交计算，也不得声称 ready。** 缺少 `model_contract.json` 本身就是
   一个 FAIL（`C0 契约`）：没有契约，物种计数/溶剂密度/吸附模式/离子配位/slab 层数全部不会被验证。
2. **门限必须在最终交付文件上运行**；结构一变就重跑。
3. **FAIL 不可通过改契约来消掉**。改契约只有在"原先声明的意图本身写错了"时才合法，
   并且必须在报告里显式说明改了什么、为什么。
4. 不要修改门限脚本去迁就某个结构（`--set` 只用于门限确实不适用的少数参数；
   放宽门槛必须在报告中注明）。
5. 门限只看几何与输入一致性，**不判断科学合理性**（选哪个泛函、要不要预平衡、
   覆盖度是否代表真实条件，仍需人判断）。门限 PASS ≠ 科学结论可信。
6. **交付形态二选一**：形态 A 仅 POSCAR（+契约+门限报告）；形态 B 四件套
   POSCAR/INCAR/KPOINTS/POTCAR 齐且 POTCAR 通过 `check_vasp_inputs.py` 的 I2/I3。
   授权赝势库不可得时 **BLOCKED 并回落形态 A**；禁止交付“有 INCAR/KPOINTS 而缺 POTCAR”的半套。
   交付前跑 `check_vasp_inputs.py --poscar <P> --delivery-dir <交付目录>` 自证形态。
7. **溶剂层数与面内均匀是硬门限**：契约必须声明 `species.<溶剂>.layers_min`（液膜 ≥3）；
   水分子数按 `N = A·ρ·t` 反算；层内用 `hex_sites` 准均匀位点。门限 C2-溶剂层数 / C2-面内均匀 会
   拦住“减层凑密度”和“面内聚团/留洞”。
8. **POSCAR 元素顺序由契约声明**（`output_species_order`，如 H C O K Cu），门限 C5 逐位核对；
   下游 POTCAR 拼接顺序跟随它，不允许交付时临时改序。

## 文件

| 文件 | 作用 |
|---|---|
| `scripts/check_geometry.py` | 通用几何硬门限（纯标准库） |
| `scripts/check_vasp_inputs.py` | POSCAR/POTCAR/INCAR/KPOINTS 一致性 + 交付形态门限（纯标准库） |
| `scripts/build_interface.py` | 确定性界面构建器（slab+多层均匀水膜+吸附物+离子 → POSCAR） |
| `scripts/hbond_pack.py` | 通用氢键溶剂层排布器（供体匹配 + 取向搜索） |
| `scripts/elements.py` | 元素半径/质量数据表（门限与排布器的共同依据） |
| `assets/model_contract.example.json` | 契约模板（逐字段说明） |
| `references/acceptance_criteria.md` | 每个门限的定义、阈值、依据，以及如何合理放宽 |
| `references/failure_playbook.md` | 失败 → 通用修法（含失效模式与根因） |

无第三方依赖（不需要 numpy/ASE），Python 3.8+ 可运行。
