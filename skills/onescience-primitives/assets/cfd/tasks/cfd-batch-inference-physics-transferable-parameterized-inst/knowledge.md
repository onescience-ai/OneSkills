# 实例任务：批量推理与物理恢复 @ CFD_S090

- domain: cfd
- 骨架: cfd-batch-inference-physics-restoration-task
- 场景: cfd-transferable-parameterized-rom-real-time-monitoring-scenario (CFD_S090)
- step_id: s04
- depend: ['s03']

## 场景研究主体
- CFD_S090
- 关联论文: Real-Time Monitoring of MHD Liquid Metal Flows with Shallow Recurrent Decoders | doi:; Non-intrusive, transferable model for coupled turbulent channel-porous media flow based upon neural networks | doi:; Numerically Solving Parametric Families of High-Dimensional Kolmogorov Partial Differential Equations via De | doi:; Intrusive versus non-intrusive reduced-order modeling of generalized Newtonian fluid flows | doi:; Neural Network-Based Parametric Model Reduction for Predicting Turbulent Flow for Different Vehicle Geometries | doi:; Reliable and efficient steady CFD from surrogate predictions through Newton-Krylov correction | doi:

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
