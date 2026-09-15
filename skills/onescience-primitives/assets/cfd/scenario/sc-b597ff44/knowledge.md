# 场景：CFD_S076

- domain: cfd
- type: paper_scenario
- 算力: ['NULL'] (is_one_hpc=[False])
- 模型: ['Transfer-learning surrogate', 'Gaussian functional regressor']
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
面向跨几何族多保真RANS数据完成迁移与多保真航空汽车气动代理。产出可复现模型、任务结果、物理一致性评估和适用域报告；域外工况需经CFD复核。

## 工作流步骤（→workflow/→tasks）
- s01 数据接入与契约核验
- s02 预处理与数据切分
- s03 模型配置与训练
- s04 闭合项预测与后验CFD耦合
- s05 任务验收与适用域判定

## 关联论文
- Adapting Automotive Aerodynamics Surrogates to New Vehicle Families via Transfer Learning | doi:
- Multi-fidelity aerodynamic data fusion by autoencoder transfer learning | doi:
- Dimension Bridging for 3D RANS with Neural Network Accelerated Gaussian Functional Regression | doi:
- From Fixed Grids to Moving Particles_A Transferable Latent Operator for Fluid Dynamics | doi:
- RETO_ A Rotary-Enhanced Transformer Operator for High-Fidelity Prediction of Automotive Aerodynamics | doi:

## 验收与缺失信息策略
- acceptance_decision: （源场景未提供）
- missing_information_policy: （源场景未提供）
