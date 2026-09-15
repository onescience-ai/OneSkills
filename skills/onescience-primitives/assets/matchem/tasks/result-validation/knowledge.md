# 结果验证 (result-validation)

## 任务目标

在交付结论前对预测与排序结果做**独立复核**，输出三态结论：**可签收 / 待复核 / 无法回答**，并附证据链。未通过复核的结论必须降级为探索性线索，不得表述为已验证事实。

## 适用范围 / 不适用场景

**适用**：已有预测值、排序结果与不确定度；存在可对标基准或文献值；数据划分可审计。

**不适用**：无任何参考基准且不允许外推验证；数据划分不可复核（存在泄漏嫌疑）；要求以计算结果替代实验表征结论。

## 实体槽（Entity Slots）

| 槽名 | 类型 | 允许取值 | 必填 |
|---|---|---|---|
| `material_family` | enum | MOF, zeolite | 否 |
| `target_property` | enum | adsorption_energy, selectivity | 否 |

## 输入输出契约

| 项 | 内容 |
|---|---|
| 输入 | 预测结果表、排序结果、数据划分说明、基准/文献参考值、方法与参数记录 |
| 输出 | 三态结论 + 复核指标（MAE/RMSE/R²、稳定性、敏感性）+ 证据链 + 未通过原因 |

## 方法路线（可替换）

1. **holdout-cross-validation（基线）**：按化学系列/时间独立划分后重算指标。前提：划分可审计、无参考泄漏。
2. **committee-uncertainty（推荐）**：多模型/多种子委员会方差量化不确定度。适用：MLIP 或 ML 模型预测。
3. **perturbation-sensitivity（叠加）**：对输入结构、参数、阈值做扰动，检验结论稳定性。

划分不可审计时**改道**为仅做物理一致性与基准对标，并显式标注「无法复核泛化性」。

## 操作序列（Operations）

| 顺序 | 操作 | 说明 |
|---|---|---|
| 1 | `split-data` | 独立划分/留出，记录划分依据与种子 |
| 2 | `recompute-metrics` | 重算 MAE/RMSE/R² 等指标，可交 `prediction-accuracy-evaluation` 执行 |
| 3 | `compare-baseline` | 与基准/文献值对标，给出偏差与一致性判定 |

## 验证契约（Validations）

- `reproducibility`：同输入同种子可复现，参数与环境记录完整。
- `physical-plausibility`：结论不违反物理化学常识（能量符号、吸附趋势、选择性上下界）。
- `benchmark-agreement`：与已知基准偏差在声明范围内，超范围须标注并降级。

## 资源引用（Resources）

| 资源 | 路径 | 角色 |
|---|---|---|
| MACE | `matchem/models/mace` | 委员会不确定度来源 |
| pymatgen | `matchem/tools/pymatgen` | 结构一致性核验 |

## 前后置任务（Task Graph）

`candidate-ranking` →（prev）**result-validation**（终端）；指标核算复用 `prediction-accuracy-evaluation`。

## 缺口与降级（Fallback / Gap）

- 改道触发：无独立划分 → 仅做一致性核验并标注不可复核泛化性；无基准值 → 降级为内部一致性检查。
- 分层降级：`full` / `partial` / `task_only` / `none`；`retrieval_level != full` 时向 `references/tc/gaps.jsonl` 追加缺口记录。
- 已知缺口：实验数据回流通道未接入；文献基准值需 `onescience-live-literature` 在线补齐。
