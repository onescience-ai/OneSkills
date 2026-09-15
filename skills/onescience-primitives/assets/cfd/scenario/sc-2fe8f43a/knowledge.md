# 场景：CFD_S019

- domain: cfd
- type: paper_scenario
- 算力: ['NULL'] (is_one_hpc=[False])
- 模型: ['Neural ODE', 'Latent neural field']
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
面向连续时间PDE状态序列完成潜空间神经ODE连续流动动力学预测。产出可复现模型、任务结果、物理一致性评估和适用域报告；域外工况需经CFD复核。

## 工作流步骤（→workflow/→tasks）
- s01 数据接入与契约核验
- s02 预处理与数据切分
- s03 模型配置与训练
- s04 批量推理与物理恢复
- s05 任务验收与适用域判定

## 关联论文
- AROMA_ Preserving Spatial Structure for Latent PDE Modeling with Local Neural Fields | doi:
- CALM-PDE_ Continuous and Adaptive Convolutions for Latent Space Modeling of Time-dependent PDEs | doi:
- Poisson-Dirac Neural Networks for Modeling Coupled Dynamical Systems across Domains | doi:
- Hierarchical Implicit Neural Emulators | doi:
- Zero-Shot Transfer of Neural ODEs | doi:
- ClimODE_ Climate and Weather Forecasting with Physics-informed Neural ODEs | doi:
- Vectorized Conditional Neural Fields_ A Framework for Solving Time-dependent Parametric Partial Differential Equ | doi:
- Implicit Neural Spatial Representations for Time-dependent PDEs | doi:
- Clifford Neural Layers for PDE Modeling | doi:
- Continuous PDE Dynamics Forecasting with Implicit Neural Representations | doi:
- Latent Field Discovery in Interacting Dynamical Systems with Neural Fields | doi:
- Modulated Neural ODEs | doi:
- Phase2vec_ dynamical systems embedding with a physics-informed convolutional network | doi:
- Learning to Accelerate Partial Differential Equations via Latent Global Evolution | doi:

## 验收与缺失信息策略
- acceptance_decision: （源场景未提供）
- missing_information_policy: （源场景未提供）
