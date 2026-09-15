# 结构核验 (structure-validation)

## 任务目标

在性质预测前确认候选结构的**几何与化学合理性**：几何优化收敛、对称性/空间群核验、键长与配位数检查、无原子重叠与虚频发散，输出通过/不通过判定与证据。未通过核验的结构不得进入 `material-property-prediction`。

## 适用范围 / 不适用场景

**适用**：已有候选结构（来自 `candidate-generation` 或数据库导入）；需要可审计的通过/不通过判定；允许保留失败结构及原因。

**不适用**：只有组成式无结构信息；要求实验级结构确认（如 XRD 精修）；结构属非晶/缺陷体系且无合理初始构型。

## 实体槽（Entity Slots）

| 槽名 | 类型 | 允许取值 | 必填 |
|---|---|---|---|
| `material_family` | enum | MOF, zeolite, perovskite, alloy | 否 |

## 输入输出契约

| 项 | 内容 |
|---|---|
| 输入 | 候选结构文件（CIF/POSCAR/extxyz）、收敛阈值、对称性容差 |
| 输出 | 优化后结构 + 收敛证据（能量/力变化）+ 对称性与键合检查结论 + 通过/不通过标记 |

## 方法路线（可替换）

1. **geometry-optimization（快速）**：力场或 MLIP（`models/mace`）弛豫，适用大批量初筛。前提：体系在势函数覆盖内。
2. **DFT 严格弛豫（改道）**：MLIP 覆盖外或需高精度晶胞参数时改道；当前域内缺 DFT 求解器资源卡，属已知缺口。
3. **symmetry-analysis**：空间群/对称操作核验，用 `tools/pymatgen`，与优化方法正交，可叠加。

## 操作序列（Operations）

| 顺序 | 操作 | 说明 |
|---|---|---|
| 1 | `optimize-geometry` | 弛豫至力/能量收敛，记录步数与残差 |
| 2 | `check-symmetry` | 空间群、对称操作、晶胞参数合理性 |
| 3 | `check-bonding` | 键长、配位数、原子间距、重叠排查 |

## 验证契约（Validations）

- `geometric-plausibility`：键长/配位数落在化学合理区间，无原子重叠。
- `convergence-check`：力残差与能量变化低于阈值，且非鞍点/虚频发散。

## 资源引用（Resources）

| 资源 | 路径 | 角色 |
|---|---|---|
| pymatgen | `matchem/tools/pymatgen` | 对称性分析、键合检查、结构 IO |
| MACE | `matchem/models/mace` | 快速几何优化 |
| DFT 求解器 | **缺失** | 严格弛豫所需 → 记为缺口 |

## 前后置任务（Task Graph）

`candidate-generation` →（prev）**structure-validation**（next）→ `material-property-prediction`。

## 缺口与降级（Fallback / Gap）

- 改道触发：MLIP 优化不收敛或体系超出覆盖 → 改道 DFT 弛豫（资源缺失时标记 `partial` 并说明精度降级）。
- 分层降级：`full` / `partial` / `task_only` / `none`；`retrieval_level != full` 时向 `references/tc/gaps.jsonl` 追加缺口记录。
- 已知缺口：DFT 求解器资源卡未建；非晶/缺陷体系核验方法缺失。
