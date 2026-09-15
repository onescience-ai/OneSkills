# 数据契约审计器 (dataset-contract-auditor)

> 资源卡（type=tool），带 `runnable:script`，是 `tasks/data-target-definition` 的可执行落点。
> 位置：`assets/matchem/tools/dataset-contract-auditor/`，脚本在 `script/audit_dataset.py`。

## 能力边界

能做：
- 读 CSV（UTF-8 / UTF-8-BOM），输出机器可读的契约审计报告 JSON
- 全行重复 + 样本标识重复检测，给出 `duplicate_rate`
- 逐列缺失率（`NA/NAN/NULL/NONE/空串` 视为缺失）
- 划分齐备性检查（train / valid / test 三份是否都有样本）
- **scaffold 泄漏检测**：按 `--scaffold-col` 分组，若同一组同时出现在 train 与 test 则判 `REJECT`
- 冻结目标定义：性质名 / 单位 / 方向(max|min) / 可靠阈值
- 四态判定 `PASS / PARTIAL / REJECT / BLOCKED`（沿用场景需求书 `acceptance_decision` 词表）

不能做：
- 不解析 CIF/POSCAR 等结构文件（结构解析走 `tools/pymatgen`）
- 不做单位换算，只做单位声明一致性检查
- 不做数据补齐（按场景 `missing_information_policy`，缺就是缺，不用默认值填）
- 不训练模型、不算预测指标（算指标走 `tools/prediction-metric-calculator`）

## 依赖

仅 Python 标准库：`csv`、`json`、`argparse`、`io`、`os`、`sys`。无第三方包，无网络，离线可跑。

## 命令

```bash
# 干净样例 -> 判定 PASS
python script/audit_dataset.py --demo \
  --target bulk_modulus --unit GPa --direction max --threshold 10 \
  --license CC-BY-4.0 --out audit_clean.json

# 注入缺陷的样例 -> 判定 REJECT（骨架泄漏）
python script/audit_dataset.py --demo-leaky \
  --target bulk_modulus --unit GPa --direction max --threshold 10 \
  --license CC-BY-4.0 --out audit_leaky.json

# 用户自己的 CSV
python script/audit_dataset.py --csv path/to/data.csv \
  --target bulk_modulus --unit GPa --direction max --threshold 10 \
  --id-col sample_id --split-col split --scaffold-col framework_family \
  --split-scheme scaffold --min-samples 5 \
  --max-duplicate-rate 0.01 --max-missing-rate 0.20 --license CC-BY-4.0
```

在仓库根目录（oneskills-tc）运行时用完整相对路径：

```bash
python skills/onescience-primitives/assets/matchem/tools/dataset-contract-auditor/script/audit_dataset.py --demo --target bulk_modulus --unit GPa --direction max --threshold 10 --license CC-BY-4.0 --out audit_clean.json
```

## 参数

| 参数 | 必填 | 默认 | 说明 |
|---|---|---|---|
| `--demo` / `--demo-leaky` / `--csv PATH` | 三选一 | — | 数据来源，互斥 |
| `--target` | 是 | — | 目标性质名，用于定位目标列 |
| `--unit` | 否 | `UNDECLARED` | 目标单位 |
| `--direction` | 否 | `max` | 优化方向，`max` 或 `min` |
| `--threshold` | 否 | `null` | 可靠阈值；不给则报告里为 `null`，不下结论 |
| `--id-col` | 否 | `sample_id` | 样本标识列 |
| `--split-col` | 否 | `split` | 划分标签列 |
| `--scaffold-col` | 否 | `framework_family` | 骨架分组列，用于泄漏检测 |
| `--split-scheme` | 否 | `scaffold` | `random` / `scaffold` / `time-based` |
| `--min-samples` | 否 | `5` | 样本量下限，不足判 BLOCKED |
| `--max-duplicate-rate` | 否 | `0.01` | 重复率上限，超出判 PARTIAL |
| `--max-missing-rate` | 否 | `0.20` | 单列缺失率上限，超出判 PARTIAL |
| `--license` | 否 | 空 | 不给则记 `LICENSE_UNDECLARED` 并降为 PARTIAL |
| `--out PATH` | 否 | 空 | 写报告文件（推荐，避免控制台编码问题） |

## 输出结构

```json
{
  "code": "OK",
  "message": "...",
  "version": "1.0.0",
  "source": "demo",
  "task": "data-target-definition",
  "step": "s01",
  "decision": "PASS",
  "audit": {
    "n_total": 24, "n_unique_rows": 24,
    "duplicate_rows": 0, "duplicate_ids": 0, "duplicate_rate": 0.0,
    "missing_rate_per_column": {"sample_id": 0.0, "...": 0.0},
    "target_column": "bulk_modulus_GPa",
    "split": {"scheme": "scaffold", "column": "split",
              "counts": {"train": 9, "valid": 8, "test": 7},
              "folds_present": ["train", "valid", "test"],
              "disjoint": true, "leaking_groups": []},
    "license": "CC-BY-4.0"
  },
  "target_definition": {"property": "bulk_modulus", "unit": "GPa",
                        "direction": "max", "reliable_threshold": 10.0,
                        "not_applicable_when": "target column missing or entirely null"},
  "violations": []
}
```

## 判定优先级

`BLOCKED` > `REJECT` > `PARTIAL` > `PASS`。同一份数据命中多条时取最严重的一条作为 `decision`，全部命中项都留在 `violations` 里。

| severity | 触发码 | 含义 |
|---|---|---|
| BLOCKED | `EMPTY_DATASET` / `INSUFFICIENT_SAMPLES` / `TARGET_COLUMN_NOT_FOUND` / `TARGET_ALL_MISSING` | 契约无法建立，不得进入 s02 |
| REJECT | `SCAFFOLD_LEAKAGE` | 硬门禁失败，必须重划分 |
| PARTIAL | `DUPLICATE_RATE_OVER_BUDGET` / `MISSING_RATE_OVER_BUDGET` / `SPLIT_FOLDS_INCOMPLETE` / `SPLIT_COLUMN_ABSENT` / `SCAFFOLD_COLUMN_ABSENT` / `LICENSE_UNDECLARED` / `TARGET_PARTIALLY_MISSING` | 可继续但须记录保留意见 |
| — | 无 violation | PASS |

退出码：`0` = 已产出报告（任何 decision）；`2` = 硬失败（`FILE_NOT_FOUND` / `READ_ERROR` / `PARSE_ERROR` / `WRITE_ERROR`）。

## 内置样例数据

`--demo`：24 条 MOF 力学稳定性样本，列为 `sample_id, framework_family, n_atoms, density_g_cm3, bulk_modulus_GPa, linker_length_A, split`；共 15 个骨架族（UiO-66 / UiO-67 / UiO-68 / ZIF-8 / ZIF-11 / ZIF-71 / ZIF-90 / MIL-53 / MIL-101 / MIL-125 / HKUST-1 / MOF-74 / Mg-MOF-74 / IRMOF-1 / IRMOF-16），划分为 train 9 / valid 8 / test 7，且**每个骨架族只出现在一个 fold 里**（train 族 = UiO-66/UiO-67/ZIF-8/ZIF-11/MIL-53，valid 族 = MOF-74/Mg-MOF-74/UiO-68/ZIF-71/MIL-101，test 族 = IRMOF-1/IRMOF-16/HKUST-1/ZIF-90/MIL-125），因此判 PASS。

`--demo-leaky`：在同一批上追加 4 条 ——
- `MOF-001` 全行重复（→ duplicate_rows=1）
- `MOF-001` 换成 ZIF-8 / valid 后重复使用标识（→ duplicate_ids）
- `MOF-025` 属 UiO-66 且 split=test，而 UiO-66 已在 train（→ **SCAFFOLD_LEAKAGE → REJECT**），同时其 `bulk_modulus_GPa` 为空（→ TARGET_PARTIALLY_MISSING）
- `MOF-026` 的 `density_g_cm3` 为空（→ 计入缺失率，未超 0.20 预算故不单独触发）

实测两份报告的差异（n=24/PASS/disjoint=true/0 violations vs n=28/REJECT/disjoint=false/leaking=UiO-66/3 violations）就是门禁生效的证据：如果 `--demo-leaky` 也返回 PASS，说明检查是空转的。

## 已知限制

- stdout 为 UTF-8 字节；GBK 代码页的 PowerShell 下 `message` 中文会乱码，但 `code`/`decision`/`audit` 数值字段不受影响。要留存证据请用 `--out` 写文件后再读，不要用 `>` 重定向。
- 目标列定位采用「精确名 → 名+单位 → 唯一子串模糊匹配」三级策略；若多个列名都含目标词且无法唯一确定，判 `TARGET_COLUMN_NOT_FOUND` 而不是猜一个。
- `time-based` 划分方案当前只做标签齐备性检查，尚未实现按时间切点的泄漏检测（属已知缺口）。
