# 候选材料排序 (candidate-ranking)

## 任务目标

在**已通过结构核验与性质验证**的候选集上，按多目标判据产出**可审计的排序 + 取舍理由 + 不确定度**，而不是只给一个综合分数。排序结论用于实验优先级排序，不得表述为已验证性能。

## 适用范围 / 不适用场景

**适用**：候选集已带性质预测值与不确定度；判据可量化（目标性质、选择性、稳定性代理、成本代理）；允许输出 Pareto 前沿与淘汰原因。

**不适用**：性质值未经验证或无不确定度；判据只有「性能最好」这类模糊表述；要求直接给出工程选型或商业化结论。

## 实体槽（Entity Slots）

| 槽名 | 类型 | 允许取值 | 必填 |
|---|---|---|---|
| `material_family` | enum | MOF, zeolite, amine-liquid, membrane | 否 |
| `adsorbate` | enum | CO2, SO2, H2S | 否 |
| `target_property` | enum | adsorption_energy, selectivity | 否 |

## 输入输出契约

| 项 | 内容 |
|---|---|
| 输入 | 候选性质表（预测值 + 单位 + 不确定度 + 验证标记）、判据与权重、约束阈值 |
| 输出 | 排序表（rank、候选 id、各判据得分、淘汰原因）+ Pareto 前沿 + 敏感性说明 |

## 方法路线（可替换）

1. **threshold-filtering（保守）**：先按硬约束淘汰，再单目标排序。适用：判据少、阈值明确。
2. **pareto-ranking（推荐）**：多目标 Pareto 前沿，不做主观加权。适用：判据互相冲突且权重无共识。
3. **weighted-scoring（改道）**：加权综合评分。前提：权重来源可审计（文献/需求方给定），否则视为伪精确。

权重不可审计时**改道** pareto-ranking，并显式说明未做加权的原因。

## 操作序列（Operations）

| 顺序 | 操作 | 说明 |
|---|---|---|
| 1 | `normalize-metrics` | 统一单位、量纲与方向（越大越好/越小越好） |
| 2 | `rank-candidates` | 按方法路线排序，保留全部判据得分 |
| 3 | `report-tradeoffs` | 输出取舍理由、Pareto 前沿与淘汰原因 |

## 验证契约（Validations）

- `ranking-stability`：对权重/阈值做扰动，Top-N 集合变动在可接受范围，否则标注排序不稳定。
- `uncertainty-propagation`：性质不确定度传播到排序，重叠区间内的候选不得断言先后。

## 资源引用（Resources）

| 资源 | 路径 | 角色 |
|---|---|---|
| MACE | `matchem/models/mace` | 提供性质预测输入 |
| pymatgen | `matchem/tools/pymatgen` | 结构特征统计（孔径、密度、比表面积代理） |

## 前后置任务（Task Graph）

`material-property-prediction` →（prev）**candidate-ranking**（next）→ `result-validation`；指标核算可交 `prediction-accuracy-evaluation`。

## 缺口与降级（Fallback / Gap）

- 改道触发：权重不可审计 → 改道 pareto-ranking；判据缺失（如无稳定性数据）→ 降维排序并标注缺失判据。
- 分层降级：`full` / `partial` / `task_only` / `none`；`retrieval_level != full` 时向 `references/tc/gaps.jsonl` 追加缺口记录。
- 已知缺口：成本与可合成性代理资源缺失；实验验证回路未接入。
