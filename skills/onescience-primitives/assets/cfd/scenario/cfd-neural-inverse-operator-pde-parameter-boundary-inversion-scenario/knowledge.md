# 场景：CFD_S033

- domain: cfd
- type: paper_scenario
- 算力: ['NULL'] (is_one_hpc=[False])
- 模型: ['Neural inverse operator', 'Inverse DeepONet']
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
面向PDE观测与参数配对数据完成神经逆算子PDE参数与边界反演。产出可复现模型、任务结果、物理一致性评估和适用域报告；域外工况需经CFD复核。

## 工作流步骤（→workflow/→tasks）
- s01 数据接入与契约核验
- s02 预处理与数据切分
- s03 模型配置与训练
- s04 候选生成与约束优化
- s05 任务验收与适用域判定

## 关联论文
- Neural Inverse Operators for Solving PDE Inverse Problems | doi:
- Transformer Meets Boundary Value Inverse Problems | doi:
- Interpolating Neural Network-Tensor Decomposition (INN-TD)_ a scalable and interpretable approach for large-scal | doi:
- Physics-Informed Deep Inverse Operator Networks for Solving PDE Inverse Problems | doi:
- Physics-Informed DeepONets for drift-diffusion on metric graphs_ simulation and parameter identification | doi:
- Physics-Driven ML-Based Modelling for Correcting Inverse Estimation | doi:

## 验收与缺失信息策略
- acceptance_decision: （源场景未提供）
- missing_information_policy: （源场景未提供）
