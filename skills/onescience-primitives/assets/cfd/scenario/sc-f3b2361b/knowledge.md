# 场景：CFD_S061

- domain: cfd
- type: paper_scenario
- 算力: ['NULL'] (is_one_hpc=[False])
- 模型: ['Conservative Graph Neural Network']
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
面向控制体网格与守恒通量数据完成守恒图网络有限体积PDE推进。产出可复现模型、任务结果、物理一致性评估和适用域报告；域外工况需经CFD复核。

## 工作流步骤（→workflow/→tasks）
- s01 数据接入与契约核验
- s02 预处理与数据切分
- s03 模型配置与训练
- s04 批量推理与物理恢复
- s05 任务验收与适用域判定

## 关联论文
- Riemann Tensor Neural Networks_ Learning Conservative Systems with Physics-Constrained Networks | doi:
- Graph Neural PDE Solvers with Conservation and Similarity-Equivariance | doi:
- Keep the Momentum_ Conservation Laws beyond Euclidean Gradient Flows | doi:
- Neural Conservation Laws_ A Divergence-Free Perspective | doi:
- PDE-GCN_ Novel Architectures for Graph Neural Networks Motivated by Partial Differential Equations | doi:
- Guaranteed Conservation of Momentum for Learning Particle-based Fluid Dynamics | doi:
- Hyperbolic-PDE GNN_ Spectral Graph Neural Networks in the Perspective of A System of Hyperbolic Partial Diff | doi:

## 验收与缺失信息策略
- acceptance_decision: （源场景未提供）
- missing_information_policy: （源场景未提供）
