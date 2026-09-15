# 场景：CFD_S086

- domain: cfd
- type: paper_scenario
- 算力: ['NULL'] (is_one_hpc=[False])
- 模型: ['POD', 'Dynamic mode decomposition']
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
面向CFD快照矩阵与参数标签完成POD与模态分解流动降阶建模。产出可复现模型、任务结果、物理一致性评估和适用域报告；域外工况需经CFD复核。

## 工作流步骤（→workflow/→tasks）
- s01 数据接入与契约核验
- s02 预处理与数据切分
- s03 模型配置与训练
- s04 批量推理与物理恢复
- s05 任务验收与适用域判定

## 关联论文
- Machine learning for fluid mechanics | doi:
- Physics-informed Reduced Order Modeling of Time-dependent PDEs via Differentiable Solvers | doi:
- Prospects of federated machine learning in fluid dynamics | doi:
- Modal analysis of fluid flows_ Applications and outlook | doi:
- Nonlinear mode decomposition with convolutional neural networks for fluid dynamics | doi:
- OrthoSolver_ A Neural Proper Orthogonal Decomposition Solver For PDEs | doi:
- A priori Assessment of Tensor-Network Encoding for Isotropic Turbulent Flows | doi:
- Convolutional causal learning for aerodynamic flows | doi:
- Data-Driven Characterisation of Wave-Forced Turbulence Using Time-Resolved Forecast-Error Growth | doi:
- Data-driven linear analysis of turbulent flows | doi:

## 验收与缺失信息策略
- acceptance_decision: （源场景未提供）
- missing_information_policy: （源场景未提供）
