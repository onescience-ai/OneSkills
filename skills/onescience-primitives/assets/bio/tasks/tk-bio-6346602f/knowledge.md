# 骨架任务：功能或效应推理

- domain: bio
- 复用场景数: 10
- 实例任务数: 10

## 步骤描述（跨场景聚合去重）
- 批量输出功能类别、连续效应或检索分数。

## 执行 prompt（跨场景聚合去重）
- 以批次{BATCH_SIZE}和种子{SEED}运行低样本多模态蛋白功能预测，用{DECISION_THRESHOLD}产生标签或效应结果。
- 以批次{BATCH_SIZE}和种子{SEED}运行偏好优化驱动的蛋白功能注释，用{DECISION_THRESHOLD}产生标签或效应结果。
- 以批次{BATCH_SIZE}和种子{SEED}运行多尺度表征的蛋白适应度预测，用{DECISION_THRESHOLD}产生标签或效应结果。
- 以批次{BATCH_SIZE}和种子{SEED}运行残基层可解释的酶功能分类，用{DECISION_THRESHOLD}产生标签或效应结果。
- 以批次{BATCH_SIZE}和种子{SEED}运行深度突变扫描监督的蛋白变异效应预测，用{DECISION_THRESHOLD}产生标签或效应结果。
- 以批次{BATCH_SIZE}和种子{SEED}运行等变结构网络的突变稳定性预测，用{DECISION_THRESHOLD}产生标签或效应结果。
- 以批次{BATCH_SIZE}和种子{SEED}运行蛋白突变效应解释与序列工程，用{DECISION_THRESHOLD}产生标签或效应结果。
- 以批次{BATCH_SIZE}和种子{SEED}运行进化谱驱动的蛋白适应度预测，用{DECISION_THRESHOLD}产生标签或效应结果。
- 以批次{BATCH_SIZE}和种子{SEED}运行酶分类与反应检索基准评测，用{DECISION_THRESHOLD}产生标签或效应结果。
- 以批次{BATCH_SIZE}和种子{SEED}运行酶序列与底物联合的动力学常数预测，用{DECISION_THRESHOLD}产生标签或效应结果。

## 输入槽（var/hint/default）
- {BATCH_SIZE} | required=True | type=int | var_name=批次大小 | hint=设置单批处理样本数 | default=32
- {DECISION_THRESHOLD} | required=False | type=float | var_name=判定阈值 | hint=设置阳性判定阈值 | default=0.5
- {SEED} | required=False | type=int | var_name=随机种子 | hint=固定评测随机过程 | default=11

## 产出
- 推理日志
- 样本级预测
- 模型分数

## 质量门禁 quality_gate
- 分数为有限值
- 失败样本已记录
- 每个样本都有结果

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 实例任务（本骨架在各场景的实例化）
- it-161ac2a7
- it-33573bd6
- it-5085fb4d
- it-6cff96e8
- it-793c794f
- it-79a0640d
- it-996c1e31
- it-9f97f4ff
- it-a0319176
- it-b0a7adf2

## 复用场景
- B39
- B32
- B38
- B37
- B31
- B34
- B35
- B36
- B40
- B33
