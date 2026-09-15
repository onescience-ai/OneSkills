# 实例任务：批量推理与物理恢复 @ CFD_S052

- domain: cfd
- 骨架: tk-cfd-7217ff92
- 场景: sc-ae96e6d8 (CFD_S052)
- step_id: s04
- depend: ['s03']

## 场景研究主体
- CFD_S052
- 关联论文: PDE-Transformer_ Efficient and Versatile Transformers for Physics Simulations | doi:; Curvature-aware Graph Attention for PDEs on Manifolds | doi:; Neural Interpretable PDEs_ Harmonizing Fourier Insights with Attention for Scalable and Interpretable Physics Di | doi:; Unisolver_ PDE-Conditional Transformers Towards Universal Neural PDE Solvers | doi:; S-Crescendo_ A Nested Transformer Weaving Framework for Scalable Nonlinear System in S-Domain Representation | doi:; FUSE_ Fast Unified Simulation and Estimation for PDEs | doi:; DPOT_ Auto-Regressive Denoising Operator Transformer for Large-Scale PDE Pre-Training | doi:; Universal Physics Transformers_ A Framework For Efficiently Scaling Neural Operators | doi:; Positional Knowledge is All You Need_ Position-induced Transformer (PiT) for Operator Learning | doi:; Choose a Transformer_ Fourier or Galerkin | doi:

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
