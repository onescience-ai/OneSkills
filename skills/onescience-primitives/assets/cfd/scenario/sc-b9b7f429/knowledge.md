# 场景：CFD_S072

- domain: cfd
- type: paper_scenario
- 算力: ['OpenFOAM'] (is_one_hpc=[False])
- 模型: ['Neural finite-volume solver', 'Domain-decomposition network']
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
面向有限体积离散与子域界面数据完成神经有限体积与域分解混合求解。产出可复现模型、任务结果、物理一致性评估和适用域报告；域外工况需经CFD复核。

## 工作流步骤（→workflow/→tasks）
- s01 数据接入与契约核验
- s02 预处理与数据切分
- s03 模型配置与训练
- s04 神经数值耦合求解
- s05 任务验收与适用域判定

## 关联论文
- Learning Interface Conditions in Domain Decomposition Solvers | doi:
- Unisoma_ A Unified Transformer-based Solver for Multi-Solid Systems | doi:
- Heavy-Ball Momentum Method in Continuous Time and Discretization Error Analysis | doi:
- Towards General Neural Surrogate Solvers with Specialized Neural Accelerators | doi:
- MG-GNN_ Multigrid Graph Neural Networks for Learning Multilevel Domain Decomposition Methods | doi:
- NeuralStagger_ Accelerating Physics-constrained Neural PDE Solver with Spatial-temporal Decomposition | doi:
- Accelerating Eulerian Fluid Simulation With Convolutional Networks | doi:
- DiscretizationNet_ A machine-learning based solver for Navier–Stokes equations using finite volume discretiz | doi:
- (U)NFV_ (Un)Supervised Neural Finite Volume Methods for Solving Hyperbolic PDEs | doi:

## 验收与缺失信息策略
- acceptance_decision: （源场景未提供）
- missing_information_policy: （源场景未提供）
