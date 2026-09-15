# 骨架任务：微生物预测与聚合

- domain: bio
- 复用场景数: 7
- 实例任务数: 7

## 步骤描述（跨场景聚合去重）
- 批量完成分类、分箱、宿主关联或耐药性预测。

## 执行 prompt（跨场景聚合去重）
- 以批次{BATCH_SIZE}和种子{SEED}运行DNA序列驱动的微生物致病性识别，用{DECISION_THRESHOLD}输出序列及样本级结果。
- 以批次{BATCH_SIZE}和种子{SEED}运行功能引导的宏基因组基因表征与分类，用{DECISION_THRESHOLD}输出序列及样本级结果。
- 以批次{BATCH_SIZE}和种子{SEED}运行噬菌体与原核宿主互作预测，用{DECISION_THRESHOLD}输出序列及样本级结果。
- 以批次{BATCH_SIZE}和种子{SEED}运行噬菌体生活方式分类预测，用{DECISION_THRESHOLD}输出序列及样本级结果。
- 以批次{BATCH_SIZE}和种子{SEED}运行对比学习驱动的宏基因组分箱，用{DECISION_THRESHOLD}输出序列及样本级结果。
- 以批次{BATCH_SIZE}和种子{SEED}运行病原监测宏基因组基础模型，用{DECISION_THRESHOLD}输出序列及样本级结果。
- 以批次{BATCH_SIZE}和种子{SEED}运行跨物种抗菌药物耐药性预测，用{DECISION_THRESHOLD}输出序列及样本级结果。

## 输入槽（var/hint/default）
- {BATCH_SIZE} | required=True | type=int | var_name=批次大小 | hint=设置序列批次大小 | default=64
- {DECISION_THRESHOLD} | required=False | type=float | var_name=判定阈值 | hint=设置阳性判定阈值 | default=0.5
- {SEED} | required=False | type=int | var_name=随机种子 | hint=固定聚类或评测结果 | default=29

## 产出
- 序列级预测
- 样本级汇总
- 运行日志

## 质量门禁 quality_gate
- 低置信结果未强制归类
- 每条序列有结果
- 聚合规则可复现

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 实例任务（本骨架在各场景的实例化）
- it-19906381
- it-5efbd16c
- it-815ccb40
- it-a2a4cd6b
- it-a2e0f6b6
- it-e4860626
- it-f822c019

## 复用场景
- B95
- B93
- B91
- B96
- B92
- B94
- B97
