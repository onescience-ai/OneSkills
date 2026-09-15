# 场景：CFD_S013

- domain: cfd
- type: paper_scenario
- 算力: ['NULL'] (is_one_hpc=[False])
- 模型: ['Transfer learning surrogate', 'Conformal predictor']
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
面向跨车型家族汽车CFD数据完成迁移与不确定性约束汽车气动快速评估。产出可复现模型、任务结果、物理一致性评估和适用域报告；域外工况需经CFD复核。

## 工作流步骤（→workflow/→tasks）
- s01 数据接入与契约核验
- s02 预处理与数据切分
- s03 模型配置与训练
- s04 批量推理与物理恢复
- s05 任务验收与适用域判定

## 关联论文
- A Blueprint for Self-Evolving Coding Agents in Vehicle Aerodynamic Drag Prediction | doi:
- Faster by Design_ Interactive Aerodynamics via Neural Surrogates Trained on Expert-Validated CFD | doi:
- Multi-Granularity Conformal Prediction for Reliable Neural-Operator Automotive Aerodynamic Surrogates | doi:
- Toward Generalizable Graph Learning for 3D Engineering AI_ Explainable Workflows for CAE Mode Shape Classification and CFD Field Prediction | doi:

## 验收与缺失信息策略
- acceptance_decision: （源场景未提供）
- missing_information_policy: （源场景未提供）
