# 场景：CFD_S020

- domain: cfd
- type: paper_scenario
- 算力: ['NULL'] (is_one_hpc=[False])
- 模型: ['Message-passing neural PDE solver', 'Adaptive mesh GNN']
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
面向动态图与拉格朗日粒子时序数据完成动态图网络与自适应网格物理时序模拟。产出可复现模型、任务结果、物理一致性评估和适用域报告；域外工况需经CFD复核。

## 工作流步骤（→workflow/→tasks）
- s01 数据接入与契约核验
- s02 预处理与数据切分
- s03 模型配置与训练
- s04 批量推理与物理恢复
- s05 任务验收与适用域判定

## 关联论文
- EvoMesh_ Adaptive Physical Simulation with Hierarchical Graph Evolutions | doi:
- Geometric and Physical Constraints Synergistically Enhance Neural PDE Surrogates | doi:
- Breaking the Discretization Barrier of Continuous Physics Simulation Learning | doi:
- Neural SPH_ Improved Neural Modeling of Lagrangian Fluid Dynamics | doi:
- Learning 3D Garment Animation from Trajectories of A Piece of Cloth | doi:
- Pluvial Flood Emulation with Hydraulics-informed Message Passing | doi:
- A Stable and Scalable Method for Solving Initial Value PDEs with Neural Networks | doi:
- ACMP_ Allen-Cahn Message Passing with Attractive and Repulsive Forces for Graph Neural Networks | doi:
- Learning Neural PDE Solvers with Parameter-Guided Channel Attention | doi:
- Newton–Cotes Graph Neural Networks_ On the Time Evolution of Dynamic Systems | doi:
- Message Passing Neural PDE Solvers | doi:

## 验收与缺失信息策略
- acceptance_decision: （源场景未提供）
- missing_information_policy: （源场景未提供）
