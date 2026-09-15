# 实例任务：结构推理与采样 @ B06

- domain: bio
- 骨架: tk-bio-0fe9bed3
- 场景: sc-078cac5b (B06)
- step_id: s03
- depend: ['s02']

## 场景研究主体
- B06
- 关联论文: Protenix-Mini: Efficient Structure Predictor via Compact Architecture, Few-Step Diffusion and Switchable pLM | doi:; Boltz-2: Towards Accurate and Efficient Binding Affinity Prediction | doi:; Protenix Technical Report | doi:

## 本实例步骤描述
运行结构推理并生成可复现的候选集合。

## 本实例执行 prompt
执行轻量化多分子复合物结构预测，回收{NUM_RECYCLES}次并以种子{SEED}生成{NUM_SAMPLES}个结构候选。

## 本实例输入槽
- {NUM_SAMPLES} | required=True | type=int | var_name=候选数量 | hint=设置候选结构数量 | default=5
- {NUM_RECYCLES} | required=False | type=int | var_name=回收次数 | hint=设置模型回收次数 | default=10
- {SEED} | required=False | type=int | var_name=随机种子 | hint=固定随机采样结果 | default=2026

## 本实例产出
- 结构候选
- 原始置信度
- 推理日志

## 本实例质量门禁
- 候选数量达标
- 坐标无NaN或Inf
- 实体数量与输入一致

## 可调资源（edge:resource，仅真实存在）
- models/alphafold
- models/alphafold3

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
