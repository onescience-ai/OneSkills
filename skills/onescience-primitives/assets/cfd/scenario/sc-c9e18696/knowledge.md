# 场景：CFD_S058

- domain: cfd
- type: paper_scenario
- 算力: ['NULL'] (is_one_hpc=[False])
- 模型: ['Domain-decomposed neural operator', 'NUNO']
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
面向非均匀采样与变形几何PDE数据完成域分解与非均匀几何神经算子学习。产出可复现模型、任务结果、物理一致性评估和适用域报告；域外工况需经CFD复核。

## 工作流步骤（→workflow/→tasks）
- s01 数据接入与契约核验
- s02 预处理与数据切分
- s03 模型配置与训练
- s04 批量推理与物理恢复
- s05 任务验收与适用域判定

## 关联论文
- NUNO_ A General Framework for Learning Parametric PDEs with Non-Uniform Data | doi:
- Reference Neural Operators_ Learning the Smooth Dependence of Solutions of PDEs on Geometric Deformations | doi:
- Geometry-Informed Neural Operator for Large-Scale 3D PDEs | doi:
- From Cheap Geometry to Expensive Physics_ A Physics-agnostic Pretraining Framework for Neural Operators | doi:
- Operator Learning with Domain Decomposition for Geometry Generalization in PDE Solving | doi:
- DD-RNO_ A Domain-Decomposed Routed Neural Operator for Airfoil Flow Prediction | doi:
- Geometry-Aware Anisotropic Boundary Correction for Aerodynamic Simulation | doi:
- Striding Across Reynolds Numbers_ Representation Geometry in Neural PDE Generalisation | doi:

## 验收与缺失信息策略
- acceptance_decision: （源场景未提供）
- missing_information_policy: （源场景未提供）
