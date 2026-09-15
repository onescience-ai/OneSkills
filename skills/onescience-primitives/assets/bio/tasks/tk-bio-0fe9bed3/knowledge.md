# 骨架任务：结构推理与采样

- domain: bio
- 复用场景数: 10
- 实例任务数: 10

## 步骤描述（跨场景聚合去重）
- 运行结构推理并生成可复现的候选集合。

## 执行 prompt（跨场景聚合去重）
- 执行OpenFold组件消融与结构泛化评测，回收{NUM_RECYCLES}次并以种子{SEED}生成{NUM_SAMPLES}个结构候选。
- 执行原子级蛋白表征驱动的结构预测，回收{NUM_RECYCLES}次并以种子{SEED}生成{NUM_SAMPLES}个结构候选。
- 执行无MSA蛋白质快速折叠预测，回收{NUM_RECYCLES}次并以种子{SEED}生成{NUM_SAMPLES}个结构候选。
- 执行物理反馈约束的蛋白构象集合生成，回收{NUM_RECYCLES}次并以种子{SEED}生成{NUM_SAMPLES}个结构候选。
- 执行蛋白质单体结构预测与置信度评估，回收{NUM_RECYCLES}次并以种子{SEED}生成{NUM_SAMPLES}个结构候选。
- 执行蛋白质复合物结构精修与质量评估，回收{NUM_RECYCLES}次并以种子{SEED}生成{NUM_SAMPLES}个结构候选。
- 执行蛋白质多构象状态空间生成与筛选，回收{NUM_RECYCLES}次并以种子{SEED}生成{NUM_SAMPLES}个结构候选。
- 执行蛋白质核酸配体复合物全原子结构预测，回收{NUM_RECYCLES}次并以种子{SEED}生成{NUM_SAMPLES}个结构候选。
- 执行蛋白质配体复合物结构与结合亲和力联合预测，回收{NUM_RECYCLES}次并以种子{SEED}生成{NUM_SAMPLES}个结构候选。
- 执行轻量化多分子复合物结构预测，回收{NUM_RECYCLES}次并以种子{SEED}生成{NUM_SAMPLES}个结构候选。

## 输入槽（var/hint/default）
- {NUM_SAMPLES} | required=True | type=int | var_name=候选数量 | hint=设置候选结构数量 | default=5
- {NUM_RECYCLES} | required=False | type=int | var_name=回收次数 | hint=设置模型回收次数 | default=10
- {SEED} | required=False | type=int | var_name=随机种子 | hint=固定随机采样结果 | default=2026

## 产出
- 原始置信度
- 推理日志
- 结构候选

## 质量门禁 quality_gate
- 候选数量达标
- 坐标无NaN或Inf
- 实体数量与输入一致

## 可调资源（edge:resource，仅真实存在）
- models/alphafold
- models/alphafold3
- models/openfold

## 实例任务（本骨架在各场景的实例化）
- it-116f4d93
- it-174fde9b
- it-3c720d75
- it-3d8d557a
- it-65a7c0ed
- it-66ac47e1
- it-6738b1b9
- it-96417f24
- it-d256585c
- it-e9acfcf0

## 复用场景
- B02
- B08
- B03
- B10
- B01
- B09
- B07
- B04
- B05
- B06
