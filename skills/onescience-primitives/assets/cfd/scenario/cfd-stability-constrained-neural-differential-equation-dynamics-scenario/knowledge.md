# 场景：CFD_S065

- domain: cfd
- type: paper_scenario
- 算力: ['NULL'] (is_one_hpc=[False])
- 模型: ['Stable Neural ODE', 'Constrained neural process']
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
面向显式约束动力系统时序数据完成稳定性约束神经微分方程动力学学习。产出可复现模型、任务结果、物理一致性评估和适用域报告；域外工况需经CFD复核。

## 工作流步骤（→workflow/→tasks）
- s01 数据接入与契约核验
- s02 预处理与数据切分
- s03 模型配置与训练
- s04 批量推理与物理恢复
- s05 任务验收与适用域判定

## 关联论文
- Neural Processes with Stability | doi:
- Axial Neural Networks for Dimension-Free Foundation Models | doi:
- HHD-GP_ Incorporating Helmholtz-Hodge Decomposition into Gaussian Processes for Learning Dynamical Systems | doi:
- Stabilized Neural Differential Equations for Learning Dynamics with Explicit Constraints | doi:
- Spatio-Temporal Prediction of Unsteady Airfoil Aerodynamics Using Augmented Graph Neural Ordinary Differential Equations with Exogenous Controls | doi:

## 验收与缺失信息策略
- acceptance_decision: （源场景未提供）
- missing_information_policy: （源场景未提供）
