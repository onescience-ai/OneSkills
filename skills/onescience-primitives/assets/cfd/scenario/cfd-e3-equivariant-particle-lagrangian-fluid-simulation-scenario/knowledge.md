# 场景：CFD_S062

- domain: cfd
- type: paper_scenario
- 算力: ['NULL'] (is_one_hpc=[False])
- 模型: ['E3-equivariant GNN', 'Lagrangian simulator']
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
面向拉格朗日粒子轨迹数据完成E3等变粒子网络拉格朗日流体模拟。产出可复现模型、任务结果、物理一致性评估和适用域报告；域外工况需经CFD复核。

## 工作流步骤（→workflow/→tasks）
- s01 数据接入与契约核验
- s02 预处理与数据切分
- s03 模型配置与训练
- s04 批量推理与物理恢复
- s05 任务验收与适用域判定

## 关联论文
- Learning Lagrangian Fluid Mechanics with E(3)-Equivariant Graph Neural Networks | doi:
- DEL_ Discrete Element Learner for Learning 3D Particle Dynamics with Neural Rendering | doi:
- Learning Physical Models that Can Respect Conservation Laws | doi:
- Modeling Dynamics over Meshes with Gauge Equivariant Nonlinear Message Passing | doi:
- Incorporating Symmetry into Deep Dynamics Models for Improved Generalization | doi:
- LagrangeBench_ A Lagrangian Fluid Mechanics Benchmarking Suite | doi:
- Symmetric Basis Convolutions for Learning Lagrangian Fluid Mechanics | doi:

## 验收与缺失信息策略
- acceptance_decision: （源场景未提供）
- missing_information_policy: （源场景未提供）
