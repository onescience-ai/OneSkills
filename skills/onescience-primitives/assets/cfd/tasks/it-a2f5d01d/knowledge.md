# 实例任务：方程求解与物理残差恢复 @ CFD_S046

- domain: cfd
- 骨架: tk-cfd-ebecc632
- 场景: sc-d0848992 (CFD_S046)
- step_id: s04
- depend: ['s03']

## 场景研究主体
- CFD_S046
- 关联论文: Aerodynamic force reconstruction using physics-informed Gaussian processes | doi:; Integration Matters for Learning PDEs with Backward SDEs | doi:; PIG_ Physics-Informed Gaussians as Adaptive Parametric Mesh Representations | doi:; Score-based free-form architectures for high-dimensional Fokker-Planck equations | doi:; In-Context Learning of Stochastic Differential Equations with Foundation Inference Models | doi:; Learning in modal space_ Solving time-dependent stochastic PDEs using physics-informed neural networks | doi:; Gaussian Process Priors for Systems of Linear Partial Differential Equations with Constant Coefficients | doi:; Physics-informed machine learning with smoothed particle hydrodynamics_ Hierarchy of reduced Lagrangian mode | doi:; Learning a Neural Solver for Parametric PDEs to Enhance Physics-Informed Methods | doi:; Physics-Informed Inference Time Scaling for Solving High-Dimensional Partial Differential Equations | doi:; UrbanGraph_ Physics-Informed Spatio-Temporal Dynamic Heterogeneous Graphs for Urban Microclimate Prediction | doi:; Physics-Informed Kolmogorov-Arnold networks for viscoelastic fluid equations | doi:

## 本实例步骤描述
在查询配点或网格上恢复解场、导数、边界值与方程残差。

## 本实例执行 prompt
加载{CHECKPOINT}，在测试参数、边界和查询坐标上求解目标PDE，使用自动微分或离散算子恢复导数、通量和方程残差。保存解场与残差场；禁止只依据训练损失判定方程已求解。

## 本实例输入槽
- {CHECKPOINT} | required=True | type=doc | var_name=模型权重 | hint=通过训练门限权重 | default=best_checkpoint.pt
- {DEVICE} | required=True | type=str | var_name=计算设备 | hint=CPU或CUDA设备 | default=cuda
- {BATCH_SIZE} | required=False | type=int | var_name=推理批大小 | hint=按显存调整批量 | default=8

## 本实例产出
- solution_fields/
- pde_residuals/
- boundary_residuals.csv

## 本实例质量门禁
- 解场导数与残差均为有限值
- 边初值逐项满足门限
- 独立数值解或解析解可对照

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
