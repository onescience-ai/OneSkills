# 实例任务：批量推理与物理恢复 @ CFD_S056

- domain: cfd
- 骨架: cfd-batch-inference-physics-restoration-task
- 场景: cfd-scientific-foundation-model-multi-physics-operator-transfer-scenario (CFD_S056)
- step_id: s04
- depend: ['s03']

## 场景研究主体
- CFD_S056
- 关联论文: Poseidon_ Efficient Foundation Models for PDEs | doi:; DGNet_ Discrete Green Networks for Data-Efficient Learning of Spatiotemporal PDEs | doi:; OmniArch_ Building Foundation Model for Scientific Computing | doi:; Towards a Physics Foundation Model | doi:; Data-Efficient Operator Learning via Unsupervised Pretraining and In-Context Learning | doi:; Pretraining Codomain Attention Neural Operators for Solving Multiphysics PDEs | doi:; Differentiable Modal Synthesis for Physical Modeling of Planar String Sound and Motion Simulation | doi:; Training Deep Surrogate Models with Large Scale Online Learning | doi:; Learning Data-Efficient and Generalizable Neural Operators via Fundamental Physics Knowledge | doi:

## 本实例步骤描述
在独立测试集推理，恢复原始单位、网格和物理派生量。

## 本实例执行 prompt
加载{CHECKPOINT}及训练时数据契约，在s02独立测试集上以{DEVICE}和{BATCH_SIZE}推理。反归一化并恢复物理单位、坐标网格、边界掩膜及任务派生量，保存逐样本结果和耗时，禁止用测试标签修正预测。

## 本实例输入槽
- {CHECKPOINT} | required=True | type=doc | var_name=模型权重 | hint=通过训练门限权重 | default=best_checkpoint.pt
- {DEVICE} | required=True | type=str | var_name=计算设备 | hint=CPU或CUDA设备 | default=cuda
- {BATCH_SIZE} | required=False | type=int | var_name=推理批大小 | hint=按显存调整批量 | default=8

## 本实例产出
- predictions/
- inference_manifest.json
- timing.csv

## 本实例质量门禁
- 预测无NaN或Inf且形状单位正确
- 每个测试样本有唯一结果
- 推理未使用测试目标校正

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
