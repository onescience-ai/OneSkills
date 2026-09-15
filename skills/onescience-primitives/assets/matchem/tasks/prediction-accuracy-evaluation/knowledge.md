# 预测精度核算 (prediction-accuracy-evaluation)

> **本任务可本地端到端执行**：操作 `run-metric-script` 直接映射到白名单脚本
> `matchem/tools/prediction-metric-calculator/script/calc_metrics.py`，仅依赖 Python 标准库，无需 GPU/联网。

## 任务目标

给定「预测值 vs 参考值」配对数据，核算 **MAE、RMSE、R²、最大绝对误差、样本数**，输出机器可读 JSON 报告与通过/不通过判定，为 `material-property-prediction` 与 `result-validation` 提供精度复核证据。

## 适用范围 / 不适用场景

**适用**：已有配对的预测值与参考值（CSV 或内置 demo）；判定阈值由调用方显式给定；需要可复现的指标报告。

**不适用**：无参考真值（只能算分布统计，不能算精度）；要求评估实验可重复性；需要按体系分箱但数据无分组列（改用 binned 方法需补分组）。

## 实体槽（Entity Slots）

| 槽名 | 类型 | 允许取值 | 必填 |
|---|---|---|---|
| `target_property` | enum | adsorption_energy, formation_energy | 否 | 决定单位与阈值口径 |
| `material_family` | enum | MOF | 否 | 用于分箱核算 |

## 输入输出契约

| 项 | 内容 |
|---|---|
| 输入 | CSV（列 `pred,ref`，可选 `group`）或 `--demo` 内置样例；可选阈值 `--mae-max`、`--r2-min` |
| 输出 | JSON：`{code, message, n, mae, rmse, r2, max_abs_err, passed, thresholds, per_group?}` |
| 失败输出 | 非零退出码 + JSON `{code, message}`（列缺失、样本不足、方差为零等） |

## 方法路线（可替换）

1. **global-metric-evaluation（默认）**：整体核算 MAE/RMSE/R²。适用：单一体系、样本同质。
2. **binned-metric-evaluation（改道）**：按 `group` 列分箱核算，暴露子集失效。前提：数据带分组列。

无分组列但需子集分析时**改道**为 global 并显式标注「未按体系分箱，可能掩盖子集失效」。

## 操作序列（Operations）

| 顺序 | 操作 | 实现 |
|---|---|---|
| 1 | `load-prediction-pairs` | 读 CSV / 生成 demo 数据，校验列与数值可解析 |
| 2 | `run-metric-script` | 执行 `script/calc_metrics.py`（白名单脚本） |
| 3 | `parse-metric-report` | 解析 JSON 报告，给判定与证据摘要 |

**本机执行命令**（在仓库根 `oneskills-tc/` 下）：

```powershell
python skills/onescience-primitives/assets/matchem/tools/prediction-metric-calculator/script/calc_metrics.py --demo --mae-max 0.05 --r2-min 0.9
python skills/onescience-primitives/assets/matchem/tools/prediction-metric-calculator/script/calc_metrics.py --csv <path.csv> --mae-max 0.05 --r2-min 0.9
```

## 验证契约（Validations）

- `metric-threshold`：`mae ≤ --mae-max` 且 `r2 ≥ --r2-min` 才判 `passed=true`；未给阈值时只报指标、`passed=null`。
- `sample-count`：`n ≥ 5`，不足则报 `code=INSUFFICIENT_SAMPLES` 并退出非零。

## 资源引用（Resources）

| 资源 | 路径 | 角色 |
|---|---|---|
| prediction-metric-calculator | `matchem/tools/prediction-metric-calculator` | 指标核算脚本（可运行） |
| MACE | `matchem/models/mace` | 被核算预测值的来源模型（可选） |

## 前后置任务（Task Graph）

`material-property-prediction` →（prev）**prediction-accuracy-evaluation**；结论回流 `result-validation`。

## 缺口与降级（Fallback / Gap）

- 改道触发：需分箱但无 `group` 列 → 降级 global 并标注；参考值缺失 → 判 `none` 并写缺口。
- 分层降级：`full`（任务卡 + 脚本资源均命中）/ `partial` / `task_only` / `none`；`retrieval_level != full` 时向 `references/tc/gaps.jsonl` 追加缺口记录。
- 已知缺口：不确定度传播（委员会方差）尚未脚本化；分箱阈值缺省口径未定。
