# 实例任务：结构推理与采样 @ B02

- domain: bio
- 骨架: bio-structure-inference-and-sampling-task
- 场景: bio-openfold-component-ablation-structural-generalization-scenario (B02)
- step_id: s03
- depend: ['s02']

## 场景研究主体
- B02
- 关联论文: Quantifying the Role of OpenFold Components in Protein Structure Prediction | doi:; Highly accurate protein structure prediction with AlphaFold | doi:; OpenFold: Retraining AlphaFold2 yields new insights into its learning mechanisms and capacity for generalization | doi:

## 本实例步骤描述
运行结构推理并生成可复现的候选集合。

## 本实例执行 prompt
对同一靶标的可比组，用{SEED}构造相同的候选种子序列，按{NUM_RECYCLES}和{NUM_SAMPLES}生成结构候选。首次前向单独计数，不计入回收；记录实际回收次数和总前向次数。 比较回收次数时固定模型权重、输入特征和其他条件。单候选预检只验证推理与交接，不能替代正式多候选比较；推理和候选选择不读取独立参考或终评分。

## 本实例输入槽
- {NUM_SAMPLES} | required=True | type=int | var_name=候选数量 | hint=设置候选结构数量 | default=5
- {NUM_RECYCLES} | required=False | type=int | var_name=回收次数 | hint=设置模型回收次数 | default=10
- {SEED} | required=False | type=int | var_name=随机种子 | hint=固定随机采样结果 | default=2026

## 本实例产出
- 结构候选
- 原始置信度
- 推理日志：按靶标、消融组和候选记录实际使用的权重和特征、种子、初始前向及回收次数。

## 本实例质量门禁
- 候选数量达标
- 坐标无NaN或Inf
- 实体数量与输入一致

## 可调资源（edge:resource，仅真实存在）
- models/openfold

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
