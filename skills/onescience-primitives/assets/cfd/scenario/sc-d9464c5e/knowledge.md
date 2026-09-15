# 场景：CFD_S095

- domain: cfd
- type: paper_scenario
- 算力: ['NULL'] (is_one_hpc=[False])
- 模型: ['Conditional generative model', 'Neural SDE']
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
面向多物理多功能或随机PDE数据完成条件生成模型多物理与随机PDE模拟。产出可复现模型、任务结果、物理一致性评估和适用域报告；域外工况需经CFD复核。

## 工作流步骤（→workflow/→tasks）
- s01 数据接入与契约核验
- s02 预处理与数据切分
- s03 模型配置与训练
- s04 条件采样与物理一致性筛选
- s05 任务验收与适用域判定

## 关联论文
- M2PDE_ Compositional Generative Multiphysics and Multi-component PDE Simulation | doi:
- Arbitrarily-Conditioned Multi-Functional Diffusion for Multi-Physics Emulation | doi:
- Deep Sturm–Liouville_ From Sample-Based to 1D Regularization with Learnable Orthogonal Basis Functions | doi:
- SING_ SDE Inference via Natural Gradients | doi:
- SEA_ State-Exchange Attention for High-Fidelity Physics Based Transformers | doi:
- Unifying Predictions of Deterministic and Stochastic Physics in Mesh-Reduced Space with Sequential Flow Generative Model | doi:
- Neural Ordinary Differential Equations | doi:
- NeuroFluid_ Fluid Dynamics Grounding with Particle-Driven Neural Radiance Fields | doi:

## 验收与缺失信息策略
- acceptance_decision: （源场景未提供）
- missing_information_policy: （源场景未提供）
