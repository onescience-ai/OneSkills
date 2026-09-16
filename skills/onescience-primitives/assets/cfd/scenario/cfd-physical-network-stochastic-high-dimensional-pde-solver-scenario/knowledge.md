# 场景：CFD_S046

- domain: cfd
- type: paper_scenario
- 算力: ['NULL'] (is_one_hpc=[False])
- 模型: ['Physics-informed stochastic solver', 'Gaussian process']
- 工具: []

## 研究意图（agent_task_prompt）
（源场景未提供）

## 客户端请求
- task_title: 
- request: 
- scientific_context: 
- desired_outcome: 
- executor_role: 

## 问题与适用性
面向随机微分方程与高维PDE样本完成物理网络随机与高维PDE求解。产出可复现模型、任务结果、物理一致性评估和适用域报告；域外工况需经CFD复核。

## 工作流步骤（→workflow/→tasks）
- s01 数据接入与契约核验
- s02 预处理与数据切分
- s03 模型配置与训练
- s04 方程求解与物理残差恢复
- s05 任务验收与适用域判定

## 关联论文
- Aerodynamic force reconstruction using physics-informed Gaussian processes | doi:
- Integration Matters for Learning PDEs with Backward SDEs | doi:
- PIG_ Physics-Informed Gaussians as Adaptive Parametric Mesh Representations | doi:
- Score-based free-form architectures for high-dimensional Fokker-Planck equations | doi:
- In-Context Learning of Stochastic Differential Equations with Foundation Inference Models | doi:
- Learning in modal space_ Solving time-dependent stochastic PDEs using physics-informed neural networks | doi:
- Gaussian Process Priors for Systems of Linear Partial Differential Equations with Constant Coefficients | doi:
- Physics-informed machine learning with smoothed particle hydrodynamics_ Hierarchy of reduced Lagrangian mode | doi:
- Learning a Neural Solver for Parametric PDEs to Enhance Physics-Informed Methods | doi:
- Physics-Informed Inference Time Scaling for Solving High-Dimensional Partial Differential Equations | doi:
- UrbanGraph_ Physics-Informed Spatio-Temporal Dynamic Heterogeneous Graphs for Urban Microclimate Prediction | doi:
- Physics-Informed Kolmogorov-Arnold networks for viscoelastic fluid equations | doi:

## 验收与缺失信息策略
- acceptance_decision: （源场景未提供）
- missing_information_policy: （源场景未提供）
