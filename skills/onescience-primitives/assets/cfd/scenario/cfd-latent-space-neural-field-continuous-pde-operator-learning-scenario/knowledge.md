# 场景：CFD_S054

- domain: cfd
- type: paper_scenario
- 算力: ['NULL'] (is_one_hpc=[False])
- 模型: ['Latent Neural Operator', 'Neural field operator']
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
面向连续坐标与压缩潜空间PDE数据完成潜空间与神经场连续PDE算子学习。产出可复现模型、任务结果、物理一致性评估和适用域报告；域外工况需经CFD复核。

## 工作流步骤（→workflow/→tasks）
- s01 数据接入与契约核验
- s02 预处理与数据切分
- s03 模型配置与训练
- s04 批量推理与物理恢复
- s05 任务验收与适用域判定

## 关联论文
- Latent Neural Operator for Solving Forward and Inverse PDE Problems | doi:
- Discretization-invariance_ On the Discretization Mismatch Errors in Neural Operators | doi:
- Neural Emulator Superiority_ When Machine Learning for PDEs Surpasses its Training Data | doi:
- Implicit Representations via Operator Learning | doi:
- Neural operators meet conjugate gradients_ The FCG-NO method for efficient PDE solving | doi:
- GNOT_ A General Neural Operator Transformer for Operator Learning | doi:
- General Covariance Data Augmentation for Neural PDE Solvers | doi:
- Operator Learning with Neural Fields_ Tackling PDEs on General Geometries | doi:
- Solving High-Dimensional PDEs with Latent Spectral Models | doi:
- Meta-Auto-Decoder for Solving Parametric Partial Differential Equations | doi:
- A Bregman Proximal Viewpoint on Neural Operators | doi:
- GridMix_ Exploring Spatial Modulation for Neural Fields in PDE Modeling | doi:
- Quantitative Approximation for Neural Operators in Nonlinear Parabolic Equations | doi:
- Disentangled Representation Learning for Parametric Partial Differential Equations | doi:
- Accelerating Bayesian inverse design in computational fluid dynamics using neural operators | doi:

## 验收与缺失信息策略
- acceptance_decision: （源场景未提供）
- missing_information_policy: （源场景未提供）
