# 实例任务：批量推理与物理恢复 @ CFD_S048

- domain: cfd
- 骨架: tk-cfd-7217ff92
- 场景: sc-e5411074 (CFD_S048)
- step_id: s04
- depend: ['s03']

## 场景研究主体
- CFD_S048
- 关联论文: Tucker-FNO_ Tensor Tucker-Fourier Neural Operator and its Universal Approximation Theory | doi:; Fourier Neural Operator for Parametric Partial Differential Equations | doi:; Factorized Fourier Neural Operators | doi:; Maximal Update Parametrization and Zero-Shot Hyperparameter Transfer for Fourier Neural Operators | doi:; Sensitivity-Constrained Fourier Neural Operators for Forward and Inverse Problems in Parametric Differential Equations | doi:; Beyond Regular Grids_ Fourier-Based Neural Operators on Arbitrary Domains | doi:; Domain Agnostic Fourier Neural Operators | doi:; U-FNO_ An Enhanced Fourier Neural Operator-Based Deep-Learning Model for Multiphase Flow | doi:; Understanding the Expressivity and Trainability of Fourier Neural Operator_ A Mean-Field Perspective | doi:; Spectral-Refiner_ Accurate Fine-Tuning of Spatiotemporal Fourier Neural Operator for Turbulent Flows | doi:; Extending Fourier Neural Operators for Modeling Parameterized and Coupled PDEs | doi:; Evaluation of State-of-the-Art Deep Learning Architectures for Aerodynamical Predictions | doi:

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
