# 实例任务：功能或效应推理 @ B32

- domain: bio
- 骨架: bio-function-effect-reasoning-task
- 场景: bio-preference-optimization-driven-protein-function-annotation-scenario (B32)
- step_id: s03
- depend: ['s02']

## 场景研究主体
- B32
- 关联论文: AnnoDPO: Protein Functional Annotation Learning with Direct Preference Optimization | doi:; Fine-tuning Protein Language Models with Deep Mutational Scanning improves Variant Effect Prediction | doi:

## 本实例步骤描述
批量输出功能类别、连续效应或检索分数。

## 本实例执行 prompt
以批次{BATCH_SIZE}和种子{SEED}运行偏好优化驱动的蛋白功能注释，用{DECISION_THRESHOLD}产生标签或效应结果。

## 本实例输入槽
- {BATCH_SIZE} | required=True | type=int | var_name=批次大小 | hint=设置单批处理样本数 | default=32
- {DECISION_THRESHOLD} | required=False | type=float | var_name=判定阈值 | hint=设置阳性判定阈值 | default=0.5
- {SEED} | required=False | type=int | var_name=随机种子 | hint=固定评测随机过程 | default=11

## 本实例产出
- 样本级预测
- 模型分数
- 推理日志

## 本实例质量门禁
- 每个样本都有结果
- 分数为有限值
- 失败样本已记录

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
