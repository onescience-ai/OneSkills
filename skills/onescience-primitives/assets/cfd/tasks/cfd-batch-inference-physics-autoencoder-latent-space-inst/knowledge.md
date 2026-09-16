# 实例任务：批量推理与物理恢复 @ CFD_S087

- domain: cfd
- 骨架: cfd-batch-inference-physics-restoration-task
- 场景: cfd-autoencoder-latent-space-flow-reduced-order-time-series-scenario (CFD_S087)
- step_id: s04
- depend: ['s03']

## 场景研究主体
- CFD_S087
- 关联论文: Reduced-Order Modeling of Advection-Dominated Systems with Recurrent Neural Networks and Convolutional Autoencoders | doi:; β-Variational autoencoders and transformers for reduced-order modeling of fluid flows | doi:; GyroSwin_ 5D Surrogates for Gyrokinetic Plasma Turbulence Simulations | doi:; SINGER_ Stochastic Network Graph Evolving Operator for High Dimensional PDEs | doi:; Observable-augmented manifold learning for multi-source turbulent flow data | doi:; Slim multi-scale convolutional autoencoder-based reduced-order models for interpretable features of a complex dy | doi:; Evolve Smoothly, Fit Consistently_ Learning Smooth Latent Dynamics For Advection-Dominated Systems | doi:; Neural Lad_ A Neural Latent Dynamics Framework for Times Series Modeling | doi:; Cost function for low-dimensional manifold topology assessment | doi:; Time-series learning of latent-space dynamics for reduced-order model closure | doi:

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
