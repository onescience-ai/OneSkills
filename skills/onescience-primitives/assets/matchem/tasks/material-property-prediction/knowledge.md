# 材料性质预测 (material-property-prediction)

## 任务目标

给定候选材料结构与目标性质（`target_property`），产出**可核验的性质预测值 + 不确定度 + 证据来源**，供 `candidate-ranking` 排序与 `result-validation` 复核使用。本任务不宣称实验可用性，只给出计算/预测层面的结论与边界。

## 适用范围 / 不适用场景

**适用**：结构已确认（前置 `structure-validation` 通过）；目标性质属可计算量（吸附能、带隙、弹性模量、扩散系数、形成能）；允许输出不确定度与失败标记。

**不适用**：结构未优化或对称性未核验；目标性质需实验表征（如实际循环寿命、成本）；要求直接给出临床/工程安全性结论；实体槽取值落在所有方法覆盖范围外（见「缺口与降级」）。

## 实体槽（Entity Slots）

| 槽名 | 类型 | 允许取值 | 必填 | 说明 |
|---|---|---|---|---|
| `material_family` | enum | MOF, zeolite, amine-liquid, membrane, perovskite, alloy | 否 | 材料体系族，决定势函数/泛函适用性 |
| `adsorbate` | enum | CO2, SO2, H2S, N2, CH4, H2, O2 | 否 | 吸附质；**CO 不在 ML 势函数覆盖内**，需改道 DFT |
| `target_property` | enum | adsorption_energy, band_gap, elastic_modulus, diffusion_coefficient, formation_energy, selectivity | 否 | 目标性质；selectivity 需多性质组合计算 |

槽取值同时写入 `metadata.json` 的 `slot:*` tag，供检索期精确匹配。

## 输入输出契约

| 项 | 内容 |
|---|---|
| 输入 | 结构文件（CIF/POSCAR/extxyz）、`target_property`、实体槽取值、可选参考数据 |
| 输出 | 预测值 + 单位 + 不确定度 + 方法路线 + 收敛/精度证据 + `retrieval_level` |
| 失败输出 | 明确标记「无法回答」及原因（前提不满足 / 资源缺失 / 超出方法覆盖） |

## 方法路线（可替换）

1. **machine-learning-potential（首选，低成本）**：用 `models/mace` 等 MLIP 做能量/力推理。适用：训练分布内体系、`adsorbate ∈ {CO2, SO2, H2S, N2, CH4, H2, O2}`、大批量筛选。前提：结构在势函数训练分布内、预测置信度 ≥ 0.5。
2. **density-functional-theory（改道，高精度）**：PBE/GGA 级 DFT，ENCUT ≥ 520 eV、Γ 中心 k 点网格。适用：MLIP 分布外体系、需可逆化学键判定、`adsorbate = CO`。前提：本机具备 DFT 求解器与算力配额。

两条路线**互为 fallback**，选择依据是前提核验结果而非默认偏好。

## 操作序列（Operations）

| 顺序 | 操作 | 说明 |
|---|---|---|
| 1 | `prepare-input` | 结构转换/超胞构建/吸附位点放置，用 `tools/pymatgen` |
| 2 | `run-inference` | MLIP 推理（`models/mace`）或 DFT 自洽计算 |
| 3 | `parse-output` | 提取能量/力/应力，换算目标性质与单位 |
| 4 | `estimate-uncertainty` | 委员会模型方差 / 收敛性检验，给出不确定度 |

## 验证契约（Validations）

- `prediction-accuracy`：与参考基准比对，能量 MAE、力 MAE 达标才算通过（见 `atom:atom_mpp_mace_mae_energy`、`atom:atom_mpp_mace_mae_force`）。
- `physical-plausibility`：键长/配位数/能量符号物理合理，无原子重叠、无虚频发散。
- 未通过验证的结果**不得**进入排序，只能标记为待复核。

## 资源引用（Resources）

| 资源 | 路径 | 角色 |
|---|---|---|
| MACE | `matchem/models/mace` | MLIP 能量/力推理 |
| pymatgen | `matchem/tools/pymatgen` | 结构准备与结果解析 |
| DFT 求解器（VASP 等） | **缺失** | DFT 路线所需，当前域内无资源卡 → 记为缺口 |

## 前后置任务（Task Graph）

`structure-validation` →（prev）**material-property-prediction**（next）→ `candidate-ranking`；验证结果可交 `prediction-accuracy-evaluation` 做指标核算。

## 缺口与降级（Fallback / Gap）

- 改道触发：`prediction_confidence < 0.5`，或 `slot:adsorbate = CO` 且需可逆化学键判定 → 由 MLIP 改道 DFT；DFT 算力不足 → 改道回 MLIP 并显式标注精度降级。
- 分层降级：资源全命中 = `full`；仅命中部分资源（如缺 DFT 求解器）= `partial`；仅命中本 Task 卡 = `task_only`；无命中 = `none`。`retrieval_level != full` 时向 `.onescience/gaps.jsonl` 追加缺口记录。
- 已知缺口：DFT 求解器资源卡未建；`selectivity` 需多性质组合，尚无专用操作序列。
