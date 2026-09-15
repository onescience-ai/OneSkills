# 骨架任务：候选排序与实验/文献交叉验证

- domain: matchem
- 复用场景数: 1
- 实例任务数: 1

## 步骤描述（跨场景聚合去重）
- 按层状结构稳定性、低应变和力学风险代理指标排序，优先输出前 3 个候选；若提供验证数据，则对晶格、相变、循环或裂纹趋势进行独立对照。

## 执行 prompt（跨场景聚合去重）
- 依据 {ANALYSIS_TABLES} 对候选排序；有 {VALIDATION_DATA} 时逐项对照，无验证数据时明确写出计算范围和未验证项，输出 PASS、REJECT 或 BLOCKED。

## 输入槽（var/hint/default）
- {ANALYSIS_TABLES} | required=True | type=doc | var_name=分析结果表 | hint=s03-s04 输出。 | default={ANALYSIS_TABLES}
- {VALIDATION_DATA} | required=False | type=doc | var_name=验证数据 | hint=实验或文献数据；缺失时不做实验结论。 | default={VALIDATION_DATA}

## 产出
- 候选排序与推荐理由
- 可复现实验配置与最终判定
- 结构—掺杂—应变关系

## 质量门禁 quality_gate
- 推荐候选的原始结构、参数和日志齐全
- 未提供实验数据时不得声称已验证开裂强度或循环寿命
- 每个结论都能回溯到 PDF 证据、计算结果或明确假设

## 可调资源（edge:resource，仅真实存在）
- datapipes/xps-nife-oer-surface-analysis
- tools/pymatgen

## 实例任务（本骨架在各场景的实例化）
- it-d2fdc49b

## 复用场景
- LiNiCo_高镍层状正极掺杂结构优化与应变风险分析
