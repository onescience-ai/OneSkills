# 场景：CFD_S077

- domain: cfd
- type: paper_scenario
- 算力: ['NULL'] (is_one_hpc=[False])
- 模型: ['CNN surrogate', 'Neural differential equation']
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
面向多孔介质微流动与输运CFD数据完成多孔与复杂输运流动场数据驱动预测。产出可复现模型、任务结果、物理一致性评估和适用域报告；域外工况需经CFD复核。

## 工作流步骤（→workflow/→tasks）
- s01 数据接入与契约核验
- s02 预处理与数据切分
- s03 模型配置与训练
- s04 闭合项预测与后验CFD耦合
- s05 任务验收与适用域判定

## 关联论文
- Data-Driven Design Optimization of Streaming-Potential-Mediated Electrokinetic Transport of Viscoelastic Fluids in Microchannels | doi:
- Advances in Scientific Machine Learning for Coupled Fluid Flow and Transport | doi:
- Online Gate-Driven Flow Control in Resin Transfer Moulding Using a Neural -Network Surrogate | doi:
- Turbulent Microscale Flow Field Prediction In Porous Media Using Convolutional Neural Networks | doi:

## 验收与缺失信息策略
- acceptance_decision: （源场景未提供）
- missing_information_policy: （源场景未提供）
