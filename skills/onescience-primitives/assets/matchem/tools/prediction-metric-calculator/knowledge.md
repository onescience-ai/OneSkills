# 预测精度核算工具 (prediction-metric-calculator)

## 能力概述

命令行工具，对「预测值 vs 参考值」配对数据核算精度指标：**MAE、RMSE、R²、最大绝对误差、样本数**，输出统一 JSON 报告。可选按 `group` 列分箱核算，暴露子集失效。仅依赖 Python 标准库，离线可跑。

## 执行方式

脚本路径（相对仓库根 `oneskills-tc/`）：

```
skills/onescience-primitives/assets/matchem/tools/prediction-metric-calculator/script/calc_metrics.py
```

```powershell
# 内置可复现样例（MOF CO2 吸附能，24 条，固定种子 20260914）
python <script> --demo --mae-max 0.05 --r2-min 0.9

# 外部 CSV（默认列名 pred / ref / group）
python <script> --csv predictions.csv --mae-max 0.05 --r2-min 0.9

# 只做整体核算，禁用分箱
python <script> --csv predictions.csv --no-group

# 写出报告文件
python <script> --demo --out report.json
```

## 接口与参数

| 参数 | 说明 | 默认 |
|---|---|---|
| `--demo` / `--csv PATH` | 数据来源，二选一且必填 | — |
| `--pred-col` / `--ref-col` | 预测值/参考值列名 | `pred` / `ref` |
| `--group-col` | 分组列名，缺列时自动降级为整体核算并 stderr 告警 | `group` |
| `--no-group` | 禁用分箱核算 | false |
| `--mae-max` / `--r2-min` | 判定阈值，**必须显式给定才下结论** | 无 |
| `--min-samples` | 最小样本数，不足则报错退出 | 5 |
| `--out PATH` | 报告写出路径（自动建目录） | 无 |

## 输入输出

**输入**：CSV（UTF-8，可带 BOM），至少含 `pred`、`ref` 两列数值；或 `--demo` 内置数据。

**输出**（stdout，JSON）：

```json
{
  "code": "OK",
  "message": "指标核算完成；满足给定阈值",
  "version": "1.0.0",
  "source": "demo",
  "method": "binned-metric-evaluation",
  "thresholds": {"mae_max": 0.05, "r2_min": 0.9, "min_samples": 5},
  "passed": true,
  "metrics": {"n": 24, "mae": 0.022, "rmse": 0.028, "max_abs_err": 0.061, "r2": 0.93, "degraded": null},
  "per_group": {"Mg-MOF-74": {"n": 6, "mae": 0.02, "rmse": 0.025, "max_abs_err": 0.05, "r2": 0.94, "degraded": null}}
}
```

**错误码**（退出码 2）：`FILE_NOT_FOUND`、`MISSING_COLUMN`、`PARSE_ERROR`、`INSUFFICIENT_SAMPLES`。

**降级标记**：参考值方差为零时 `metrics.r2 = null` 且 `degraded = "ZERO_VARIANCE"`，此时 `passed = null`（不下结论）。

## 依赖与环境

Python 3.9+，标准库 `argparse/csv/json/math/os/random/sys`。无第三方依赖、无 GPU、无网络访问。

> **Windows 控制台注意**：stdout 为 UTF-8 字节，在 GBK 代码页控制台下 `message` 中文会显示为乱码，但 `code` / `passed` / `metrics` / `per_group` 等字段值不受影响。需要留存可读报告时用 `--out report.json` 写出文件后再读取，不要用 PowerShell `>` 重定向捕获中文输出。

## 边界与失败模式

- 无参考真值时不能用本工具算「精度」，只能算分布统计。
- 阈值未给定时 `passed = null`，避免伪精确判定。
- 分组样本 < 2 时该组标记 `skipped = TOO_FEW_SAMPLES`，不参与分箱指标。
- 本工具不评估实验可重复性，也不替代 `result-validation` 的物理一致性核验。

## 被引用（反向边）

- `matchem/tasks/prediction-accuracy-evaluation`（`run-metric-script` 操作的执行落点）
- `matchem/tasks/result-validation`（`recompute-metrics` 操作可复用）
