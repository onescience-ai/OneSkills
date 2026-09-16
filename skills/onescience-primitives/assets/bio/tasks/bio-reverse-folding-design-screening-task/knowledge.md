# 骨架任务：回折叠与设计筛选

- domain: bio
- 复用场景数: 10
- 实例任务数: 10

## 步骤描述（跨场景聚合去重）
- 按催化几何通过率、结构自洽性和约束满足度筛选候选。
- 按口袋互补度、结构自洽性和约束满足度筛选候选。
- 按基序RMSD、结构自洽性和约束满足度筛选候选。
- 按多态成功率、结构自洽性和约束满足度筛选候选。
- 按序列恢复率、结构自洽性和约束满足度筛选候选。
- 按界面置信度、结构自洽性和约束满足度筛选候选。
- 按膜区恢复率、结构自洽性和约束满足度筛选候选。
- 按自洽TM-score、结构自洽性和约束满足度筛选候选。
- 按设计成功率、结构自洽性和约束满足度筛选候选。

## 执行 prompt（跨场景聚合去重）
- 计算催化几何通过率并以{METRIC_THRESHOLD}筛选；按{KEEP_DIVERSE}控制去冗余后导出候选。
- 计算口袋互补度并以{METRIC_THRESHOLD}筛选；按{KEEP_DIVERSE}控制去冗余后导出候选。
- 计算基序RMSD并以{METRIC_THRESHOLD}筛选；按{KEEP_DIVERSE}控制去冗余后导出候选。
- 计算多态成功率并以{METRIC_THRESHOLD}筛选；按{KEEP_DIVERSE}控制去冗余后导出候选。
- 计算序列恢复率并以{METRIC_THRESHOLD}筛选；按{KEEP_DIVERSE}控制去冗余后导出候选。
- 计算界面置信度并以{METRIC_THRESHOLD}筛选；按{KEEP_DIVERSE}控制去冗余后导出候选。
- 计算膜区恢复率并以{METRIC_THRESHOLD}筛选；按{KEEP_DIVERSE}控制去冗余后导出候选。
- 计算自洽TM-score并以{METRIC_THRESHOLD}筛选；按{KEEP_DIVERSE}控制去冗余后导出候选。
- 计算设计成功率并以{METRIC_THRESHOLD}筛选；按{KEEP_DIVERSE}控制去冗余后导出候选。

## 输入槽（var/hint/default）
- {METRIC_THRESHOLD} | required=False | type=float | var_name=筛选阈值 | hint=设置核心指标下限 | default=0.6
- {KEEP_DIVERSE} | required=False | type=bool | var_name=保留多样候选 | hint=是否执行序列去冗余 | default=True

## 产出
- 催化几何通过率汇总表
- 入选设计
- 口袋互补度汇总表
- 基序RMSD汇总表
- 多态成功率汇总表
- 序列恢复率汇总表
- 界面置信度汇总表
- 约束质控报告
- 膜区恢复率汇总表
- 自洽TM-score汇总表
- 设计成功率汇总表

## 质量门禁 quality_gate
- 入选设计满足硬约束
- 序列多样性已报告
- 结构几何无严重冲突

## 可调资源（edge:resource，仅真实存在）
- datasets/tm-score-evaluation

## 实例任务（本骨架在各场景的实例化）
- bio-reverse-folding-design-all-atom-protein-structure-inst
- bio-reverse-folding-design-functional-site-constrained-inst
- bio-reverse-folding-design-given-protein-backbone-inst
- bio-reverse-folding-design-multi-conformation-state-inst
- bio-reverse-folding-design-multi-functional-motif-inst
- bio-reverse-folding-design-protoken-latent-protein-inst
- bio-reverse-folding-design-reaction-condition-driven-inst
- bio-reverse-folding-design-substrate-pocket-constrained-inst
- bio-reverse-folding-design-target-specific-all-atom-inst
- bio-reverse-folding-design-transmembrane-protein-inst

## 复用场景
- B14
- B13
- B11
- B20
- B15
- B18
- B16
- B12
- B19
- B17
