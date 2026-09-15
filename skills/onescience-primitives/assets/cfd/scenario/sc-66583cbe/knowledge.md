# 场景：CFD_S092

- domain: cfd
- type: paper_scenario
- 算力: ['NULL'] (is_one_hpc=[False])
- 模型: ['Flow matching model']
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
面向参数条件与流场分布样本完成流匹配网络复杂流动概率代理。产出可复现模型、任务结果、物理一致性评估和适用域报告；域外工况需经CFD复核。

## 工作流步骤（→workflow/→tasks）
- s01 数据接入与契约核验
- s02 预处理与数据切分
- s03 模型配置与训练
- s04 条件采样与物理一致性筛选
- s05 任务验收与适用域判定

## 关联论文
- Switched Flow Matching_ Eliminating Singularities via Switching ODEs | doi:
- Physics vs Distributions_ Pareto Optimal Flow Matching with Physics Constraints | doi:
- Dflow-SUR_ Enhancing Generative Aerodynamic Inverse Design using Differentiation Throughout Flow Matching | doi:
- GeoFunFlow-3D_ A Physics-Guided Generative Flow Matching Framework for High-Fidelity 3D Aerodynamic Inference over Complex Geometries | doi:
- Physics-Guided Generative Surrogates for Parametric Rarefied Flows with Neural-Field Auto-Decoders_ A Pipeline-Level Study of Flow Matching and Diffusion | doi:

## 验收与缺失信息策略
- acceptance_decision: （源场景未提供）
- missing_information_policy: （源场景未提供）
