# 场景：CFD_S087

- domain: cfd
- type: paper_scenario
- 算力: ['NULL'] (is_one_hpc=[False])
- 模型: ['Convolutional autoencoder', 'Latent dynamics model']
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
面向高维流场快照时序数据完成自编码器潜空间流动降阶时序预测。产出可复现模型、任务结果、物理一致性评估和适用域报告；域外工况需经CFD复核。

## 工作流步骤（→workflow/→tasks）
- s01 数据接入与契约核验
- s02 预处理与数据切分
- s03 模型配置与训练
- s04 批量推理与物理恢复
- s05 任务验收与适用域判定

## 关联论文
- Reduced-Order Modeling of Advection-Dominated Systems with Recurrent Neural Networks and Convolutional Autoencoders | doi:
- β-Variational autoencoders and transformers for reduced-order modeling of fluid flows | doi:
- GyroSwin_ 5D Surrogates for Gyrokinetic Plasma Turbulence Simulations | doi:
- SINGER_ Stochastic Network Graph Evolving Operator for High Dimensional PDEs | doi:
- Observable-augmented manifold learning for multi-source turbulent flow data | doi:
- Slim multi-scale convolutional autoencoder-based reduced-order models for interpretable features of a complex dy | doi:
- Evolve Smoothly, Fit Consistently_ Learning Smooth Latent Dynamics For Advection-Dominated Systems | doi:
- Neural Lad_ A Neural Latent Dynamics Framework for Times Series Modeling | doi:
- Cost function for low-dimensional manifold topology assessment | doi:
- Time-series learning of latent-space dynamics for reduced-order model closure | doi:

## 验收与缺失信息策略
- acceptance_decision: （源场景未提供）
- missing_information_policy: （源场景未提供）
