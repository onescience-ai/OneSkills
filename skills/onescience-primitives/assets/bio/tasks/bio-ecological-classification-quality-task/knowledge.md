# 骨架任务：生态与分类质量评估

- domain: bio
- 复用场景数: 7
- 实例任务数: 7

## 步骤描述（跨场景聚合去重）
- 计算AUROC并检查跨物种、样本和数据集泛化。
- 计算HitAt10并检查跨物种、样本和数据集泛化。
- 计算分箱F1并检查跨物种、样本和数据集泛化。
- 计算宏平均F1并检查跨物种、样本和数据集泛化。
- 计算检出灵敏度并检查跨物种、样本和数据集泛化。

## 执行 prompt（跨场景聚合去重）
- 计算AUROC，按{MIN_CONFIDENCE}标记可信结果，并依据{REPORT_UNKNOWN}保留未知类别。
- 计算HitAt10，按{MIN_CONFIDENCE}标记可信结果，并依据{REPORT_UNKNOWN}保留未知类别。
- 计算分箱F1，按{MIN_CONFIDENCE}标记可信结果，并依据{REPORT_UNKNOWN}保留未知类别。
- 计算宏平均F1，按{MIN_CONFIDENCE}标记可信结果，并依据{REPORT_UNKNOWN}保留未知类别。
- 计算检出灵敏度，按{MIN_CONFIDENCE}标记可信结果，并依据{REPORT_UNKNOWN}保留未知类别。

## 输入槽（var/hint/default）
- {MIN_CONFIDENCE} | required=False | type=float | var_name=置信度下限 | hint=设置报告置信度下限 | default=0.7
- {REPORT_UNKNOWN} | required=False | type=bool | var_name=报告未知类别 | hint=是否保留未知类别结果 | default=True

## 产出
- AUROC明细
- HitAt10明细
- 分箱F1明细
- 宏平均F1明细
- 未知与异常清单
- 检出灵敏度明细
- 评测汇总

## 质量门禁 quality_gate
- 未知类别未被静默丢弃
- 结果可回溯原序列
- 评测按样本隔离

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 实例任务（本骨架在各场景的实例化）
- bio-ecological-classification-contrastive-learning-driven-inst
- bio-ecological-classification-cross-species-antimicrobial-inst
- bio-ecological-classification-dna-sequence-driven-microbia-inst
- bio-ecological-classification-function-guided-metageneome-inst
- bio-ecological-classification-pathogen-monitoring-metageno-inst
- bio-ecological-classification-phage-and-prokaryotic-host-inst
- bio-ecological-classification-phage-lifestyle-classificati-inst

## 复用场景
- B95
- B93
- B91
- B96
- B92
- B94
- B97
