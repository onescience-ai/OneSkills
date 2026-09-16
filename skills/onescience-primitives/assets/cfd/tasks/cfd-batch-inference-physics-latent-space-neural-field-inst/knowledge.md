# 实例任务：批量推理与物理恢复 @ CFD_S054

- domain: cfd
- 骨架: cfd-batch-inference-physics-restoration-task
- 场景: cfd-latent-space-neural-field-continuous-pde-operator-learning-scenario (CFD_S054)
- step_id: s04
- depend: ['s03']

## 场景研究主体
- CFD_S054
- 关联论文: Latent Neural Operator for Solving Forward and Inverse PDE Problems | doi:; Discretization-invariance_ On the Discretization Mismatch Errors in Neural Operators | doi:; Neural Emulator Superiority_ When Machine Learning for PDEs Surpasses its Training Data | doi:; Implicit Representations via Operator Learning | doi:; Neural operators meet conjugate gradients_ The FCG-NO method for efficient PDE solving | doi:; GNOT_ A General Neural Operator Transformer for Operator Learning | doi:; General Covariance Data Augmentation for Neural PDE Solvers | doi:; Operator Learning with Neural Fields_ Tackling PDEs on General Geometries | doi:; Solving High-Dimensional PDEs with Latent Spectral Models | doi:; Meta-Auto-Decoder for Solving Parametric Partial Differential Equations | doi:; A Bregman Proximal Viewpoint on Neural Operators | doi:; GridMix_ Exploring Spatial Modulation for Neural Fields in PDE Modeling | doi:; Quantitative Approximation for Neural Operators in Nonlinear Parabolic Equations | doi:; Disentangled Representation Learning for Parametric Partial Differential Equations | doi:; Accelerating Bayesian inverse design in computational fluid dynamics using neural operators | doi:

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
