# 骨架任务：RNA结构与功能质控

- domain: bio
- 复用场景数: 10
- 实例任务数: 10

## 步骤描述（跨场景聚合去重）
- 计算AUROC并检查结构一致性、序列约束和候选多样性。
- 计算F1并检查结构一致性、序列约束和候选多样性。
- 计算Pearson相关并检查结构一致性、序列约束和候选多样性。
- 计算RMSD并检查结构一致性、序列约束和候选多样性。
- 计算序列恢复率并检查结构一致性、序列约束和候选多样性。
- 计算约束满足率并检查结构一致性、序列约束和候选多样性。
- 计算结构恢复率并检查结构一致性、序列约束和候选多样性。
- 计算结构成功率并检查结构一致性、序列约束和候选多样性。
- 计算配对F1并检查结构一致性、序列约束和候选多样性。

## 执行 prompt（跨场景聚合去重）
- 计算AUROC，用{SCORE_THRESHOLD}筛选候选，并按{OUTPUT_FORMAT}导出结构、序列和质控结果。
- 计算F1，用{SCORE_THRESHOLD}筛选候选，并按{OUTPUT_FORMAT}导出结构、序列和质控结果。
- 计算Pearson相关，用{SCORE_THRESHOLD}筛选候选，并按{OUTPUT_FORMAT}导出结构、序列和质控结果。
- 计算RMSD，用{SCORE_THRESHOLD}筛选候选，并按{OUTPUT_FORMAT}导出结构、序列和质控结果。
- 计算序列恢复率，用{SCORE_THRESHOLD}筛选候选，并按{OUTPUT_FORMAT}导出结构、序列和质控结果。
- 计算约束满足率，用{SCORE_THRESHOLD}筛选候选，并按{OUTPUT_FORMAT}导出结构、序列和质控结果。
- 计算结构恢复率，用{SCORE_THRESHOLD}筛选候选，并按{OUTPUT_FORMAT}导出结构、序列和质控结果。
- 计算结构成功率，用{SCORE_THRESHOLD}筛选候选，并按{OUTPUT_FORMAT}导出结构、序列和质控结果。
- 计算配对F1，用{SCORE_THRESHOLD}筛选候选，并按{OUTPUT_FORMAT}导出结构、序列和质控结果。

## 输入槽（var/hint/default）
- {SCORE_THRESHOLD} | required=False | type=float | var_name=结果阈值 | hint=设置合格结果阈值 | default=0.6
- {OUTPUT_FORMAT} | required=False | type=enum | var_name=输出格式 | hint=选择RNA结果格式 | default=dot_bracket

## 产出
- AUROC汇总
- F1汇总
- Pearson相关汇总
- RMSD汇总
- RNA质控报告
- 序列恢复率汇总
- 排序候选
- 约束满足率汇总
- 结构恢复率汇总
- 结构成功率汇总
- 配对F1汇总

## 质量门禁 quality_gate
- 低质量候选已标记
- 硬约束全部满足
- 结构格式可解析

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 实例任务（本骨架在各场景的实例化）
- it-049af1ce
- it-18e34cca
- it-27bcef3f
- it-6485d363
- it-660cc843
- it-7d87fd4d
- it-957407ce
- it-ac1e1cf2
- it-c45c4fbe
- it-d8fbd63a

## 复用场景
- B83
- B90
- B85
- B82
- B86
- B88
- B87
- B84
- B89
- B81
