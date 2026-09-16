# 实例任务：批量推理与物理恢复 @ CFD_S059

- domain: cfd
- 骨架: cfd-batch-inference-physics-restoration-task
- 场景: cfd-physical-boundary-invariant-constrained-neural-operator-learning-scenario (CFD_S059)
- step_id: s04
- depend: ['s03']

## 场景研究主体
- CFD_S059
- 关联论文: Guiding Continuous Operator Learning through Physics-Based Boundary Constraints | doi:; Holistic Physics Solver_ Learning PDEs in a Unified Spectral-Physical Space | doi:; Learn Singularly Perturbed Solutions via Homotopy Dynamics | doi:; A Physics-preserved Transfer Learning Method for Differential Equations | doi:; Nonlocal Attention Operator_ Materializing Hidden Knowledge Towards Interpretable Physics Discovery | doi:; PAPM_ A Physics-aware Proxy Model for Process Systems | doi:; Training neural operators to preserve invariant measures of chaotic attractors | doi:; Generic bounds on the approximation error for physics-informed (and) operator learning | doi:; Buckingham $_pi$-Invariant Test‐Time Projection for Robust PDE Surrogate Modeling | doi:; Towards Generalizable PDE Dynamics Forecasting via Physics-Guided Invariant Learning | doi:; WAN3DNS_ Weak Adversarial Networks for Solving 3D Incompressible Navier-Stokes Equations | doi:; Wrong-Physics Backdoors in Neural PDE Operators | doi:

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
