# 场景：CFD_S052

- domain: cfd
- type: paper_scenario
- 算力: ['NULL'] (is_one_hpc=[False])
- 模型: ['PDE Transformer', 'Universal Physics Transformer']
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
面向多方程多网格预训练数据完成Transformer通用PDE算子预训练与微调。产出可复现模型、任务结果、物理一致性评估和适用域报告；域外工况需经CFD复核。

## 工作流步骤（→workflow/→tasks）
- s01 数据接入与契约核验
- s02 预处理与数据切分
- s03 模型配置与训练
- s04 批量推理与物理恢复
- s05 任务验收与适用域判定

## 关联论文
- PDE-Transformer_ Efficient and Versatile Transformers for Physics Simulations | doi:
- Curvature-aware Graph Attention for PDEs on Manifolds | doi:
- Neural Interpretable PDEs_ Harmonizing Fourier Insights with Attention for Scalable and Interpretable Physics Di | doi:
- Unisolver_ PDE-Conditional Transformers Towards Universal Neural PDE Solvers | doi:
- S-Crescendo_ A Nested Transformer Weaving Framework for Scalable Nonlinear System in S-Domain Representation | doi:
- FUSE_ Fast Unified Simulation and Estimation for PDEs | doi:
- DPOT_ Auto-Regressive Denoising Operator Transformer for Large-Scale PDE Pre-Training | doi:
- Universal Physics Transformers_ A Framework For Efficiently Scaling Neural Operators | doi:
- Positional Knowledge is All You Need_ Position-induced Transformer (PiT) for Operator Learning | doi:
- Choose a Transformer_ Fourier or Galerkin | doi:

## 验收与缺失信息策略
- acceptance_decision: （源场景未提供）
- missing_information_policy: （源场景未提供）
