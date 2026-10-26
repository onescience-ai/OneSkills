# VASP 固态 NMR / GIPAW 参数参考（通道③ · 模型可读说明）

> 本表是「软件级计算参数」的接地来源之一（`source_type=software-doc`、`evidence_level=curated-ref`）。
> 这些值来自 **VASP 官方 wiki 与领域惯例**，任何论文正文都不会写它们——所以**不要**给它们套「必须引 [n]」的门，也不要凭记忆默写。
> 机器可读版见 `param_reference.json`；查询用 `scripts/param_lookup.py --software VASP --calc NMR-GIPAW`。

## 一、结构优化（opt）常用标签

| 标签 | 推荐取值 | 含义 | 出处 | 可信度 |
|---|---|---|---|---|
| `ENCUT` | ≥ 1.3 × max(各元素 PAW 的 ENMAX) | 平面波截断能 | VASP wiki:ENCUT | 高（**具体 eV 须按 ENMAX 实算，勿照抄别体系死值**） |
| `EDIFF` | 1E-6 | 电子步收敛 | 惯例 | 中 |
| `IBRION` | 2 | 离子弛豫（共轭梯度） | VASP wiki:IBRION | 高 |
| `ISIF` | 3 | 弛豫 cell 形状+体积 | VASP wiki:ISIF | 高 |
| `IVDW` | 12 | DFT-D3(BJ) 色散（11=D3 zero） | VASP wiki:IVDW | 高 |
| `KPOINTS` | Monkhorst-Pack，分子晶体用 Γ-centered，k 间距 ≤~0.04 Å⁻¹ | k 网格 | 惯例 | 中（**网格随 cell 尺寸而变，勿照抄固定三元组**） |

## 二、NMR / GIPAW 屏蔽张量计算

| 标签 | 推荐取值 | 含义 | 出处 | 可信度 |
|---|---|---|---|---|
| `LCHIMAG` | `.TRUE.` | 磁化率 / NMR 屏蔽响应 | VASP wiki:LCHIMAG | 高 |
| `LEPSILON` | `.TRUE.` | DFPT 介电常数 + Born 有效电荷 | VASP wiki:LEPSILON | 高 |
| `LREAL` | `.FALSE.` | 含精确交换/响应时关实空间投影 | VASP wiki:LREAL | 高 |
| `ENCUT` | 500–800 eV（须对本体系收敛测试） | 响应性质需更高截断 | VASP wiki:ENCUT | 中 |
| `EDIFF` | 1E-8 | DFPT 响应精度 | 惯例 | 中 |
| `ISYM` | 0 | 显式列出全部原子位点 | 惯例 | 中 |
| `NPAR` | 1 | GIPAW 常不按 band 并行 | 惯例 | **低 ⚠ 随版本而变，须实测** |

## 三、方法学选择（属于文献通道，不在本表拍板）

- **泛函：PBE(GGA) 还是杂化(HSE06/PBE0)** —— 这是**方法学决策**，应由**通道① 文献**接地：不少体系报道杂化泛函显著提升固态 NMR 化学位移精度（如本任务参考的甘氨酸相关文献摘要即提及 hybrid 带来的改进）。选杂化对应 `LHFCALC=.TRUE.` + `HFSCREEN/GAMMA`（VASP wiki）。
- **化学位移参照化合物**（如 TMS 或某 IUPAC 基准） —— 属**文献/数据库**接地，不在本表写死。

## 四、存疑 / 需核对项（诚实标注，别当已核实）

- `ICHIBARE` —— **⚠ 疑似非 VASP 标签**（更接近 CASTEP 用语或误记）。写进 INCAR 前**必须核对 VASP wiki**，严禁凭记忆默写。
- 具体 `k` 网格三元组、`ENCUT` 的 eV 死值 —— 都是**随体系而变**的量，本表只给**确定方法**（收敛测试 / k 间距准则），不给照抄值。

> 一句话纪律：**软件参数走 software-doc 出处、不强凑论文引用；存疑项标 `⚠` 待核对；方法学选择（泛函/参照）交给文献通道接地。**
