# 骨架任务：构象采样与打分

- domain: bio
- 复用场景数: 10
- 实例任务数: 10

## 步骤描述（跨场景聚合去重）
- 采样平移、旋转和扭转自由度并输出候选得分。

## 执行 prompt（跨场景聚合去重）
- 运行全局盲对接构象生成与置信度排序，以种子{SEED}执行{INFERENCE_STEPS}步采样，为每个配体产生{POSES_PER_LIGAND}个姿态。
- 运行口袋预测增强的蛋白配体快速对接，以种子{SEED}执行{INFERENCE_STEPS}步采样，为每个配体产生{POSES_PER_LIGAND}个姿态。
- 运行多口袋条件的物理有效对接，以种子{SEED}执行{INFERENCE_STEPS}步采样，为每个配体产生{POSES_PER_LIGAND}个姿态。
- 运行对接引导的超大规模虚拟筛选，以种子{SEED}执行{INFERENCE_STEPS}步采样，为每个配体产生{POSES_PER_LIGAND}个姿态。
- 运行未知结合位点的蛋白口袋识别，以种子{SEED}执行{INFERENCE_STEPS}步采样，为每个配体产生{POSES_PER_LIGAND}个姿态。
- 运行测地路径引导的柔性分子对接，以种子{SEED}执行{INFERENCE_STEPS}步采样，为每个配体产生{POSES_PER_LIGAND}个姿态。
- 运行物理规则约束的对接姿态重排序，以种子{SEED}执行{INFERENCE_STEPS}步采样，为每个配体产生{POSES_PER_LIGAND}个姿态。
- 运行蛋白配体联合生成对接与亲和力预测，以种子{SEED}执行{INFERENCE_STEPS}步采样，为每个配体产生{POSES_PER_LIGAND}个姿态。
- 运行轻量可解释的蛋白配体构象预测，以种子{SEED}执行{INFERENCE_STEPS}步采样，为每个配体产生{POSES_PER_LIGAND}个姿态。
- 运行高精度蛋白配体对接与几何修正，以种子{SEED}执行{INFERENCE_STEPS}步采样，为每个配体产生{POSES_PER_LIGAND}个姿态。

## 输入槽（var/hint/default）
- {POSES_PER_LIGAND} | required=True | type=int | var_name=每配体姿态数 | hint=设置每个配体姿态数 | default=40
- {INFERENCE_STEPS} | required=False | type=int | var_name=推理步数 | hint=设置构象采样步数 | default=20
- {SEED} | required=False | type=int | var_name=随机种子 | hint=固定随机采样结果 | default=101

## 产出
- 候选姿态
- 对接得分
- 采样日志

## 质量门禁 quality_gate
- 坐标为有限值
- 每个成功配体有候选
- 配体键连接未改变

## 可调资源（edge:resource，仅真实存在）
- models/diffdock
- models/few-step-ode-sampling-for-diffusion-models

## 实例任务（本骨架在各场景的实例化）
- bio-conformation-sampling-scoring-docking-guided-large-scale-inst
- bio-conformation-sampling-scoring-geodesic-path-guided-flexibl-inst
- bio-conformation-sampling-scoring-global-blind-docking-conform-inst
- bio-conformation-sampling-scoring-high-precision-protein-inst
- bio-conformation-sampling-scoring-lightweight-interpretable-inst
- bio-conformation-sampling-scoring-multi-pocket-conditioned-inst
- bio-conformation-sampling-scoring-physical-rule-constrained-inst
- bio-conformation-sampling-scoring-pocket-prediction-enhanced-inst
- bio-conformation-sampling-scoring-protein-ligand-joint-generat-inst
- bio-conformation-sampling-scoring-unknown-binding-site-protein-inst

## 复用场景
- B41
- B45
- B50
- B47
- B46
- B49
- B42
- B43
- B48
- B44
