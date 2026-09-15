# 场景：CFD_S038

- domain: cfd
- type: paper_scenario
- 算力: ['NULL'] (is_one_hpc=[False])
- 模型: ['Inverse PINN', 'Physics-informed data assimilation']
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
面向稀疏流场观测与未知PDE参数完成物理信息网络稀疏观测参数反演。产出可复现模型、任务结果、物理一致性评估和适用域报告；域外工况需经CFD复核。

## 工作流步骤（→workflow/→tasks）
- s01 数据接入与契约核验
- s02 预处理与数据切分
- s03 模型配置与训练
- s04 方程求解与物理残差恢复
- s05 任务验收与适用域判定

## 关联论文
- Inferring flow parameters and turbulent configuration with physics-informed data assimilation and spectral n | doi:
- CoPINN_ Cognitive Physics-Informed Neural Networks | doi:
- Parameterized Physics-Informed Neural Networks for Parameterized PDEs | doi:
- RoPINN_ Region Optimized Physics-Informed Neural Networks | doi:
- Multi-output physics-informed neural networks for forward and inverse PDE problems with uncertainties | doi:
- Physics-informed learning of governing equations from scarce data | doi:
- Surrogate modeling for fluid flows based on physics-constrained deep learning without simulation data | doi:
- Physics informed deep learning (Part I)_ Data-driven solutions of nonlinear partial differential equations | doi:
- Causal-PIK_ Causality-based Physical Reasoning with a Physics-Informed Kernel | doi:
- DiffWind_ Physics-Informed Differentiable Modeling of Wind-Driven Object Dynamics | doi:
- Physics-informed learning under mixing_ How physical knowledge speeds up learning | doi:

## 验收与缺失信息策略
- acceptance_decision: （源场景未提供）
- missing_information_policy: （源场景未提供）
