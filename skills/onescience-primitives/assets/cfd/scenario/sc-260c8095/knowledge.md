# 场景：CFD_S017

- domain: cfd
- type: paper_scenario
- 算力: ['NULL'] (is_one_hpc=[False])
- 模型: ['Graph ODE', 'Conformal predictor']
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
面向跨雷诺数跨几何OOD流动数据完成分布外流动代理检测与校准预测。产出可复现模型、任务结果、物理一致性评估和适用域报告；域外工况需经CFD复核。

## 工作流步骤（→workflow/→tasks）
- s01 数据接入与契约核验
- s02 预处理与数据切分
- s03 模型配置与训练
- s04 概率推理与不确定性校准
- s05 任务验收与适用域判定

## 关联论文
- Prometheus_ Out-of-Distribution Fluid Dynamics Modeling with Disentangled Graph ODE | doi:
- Using Uncertainty Quantification to Characterize and Improve Out-of-Domain Learning for PDEs | doi:
- PURE_ Prompt Evolution with Graph ODE for Out-of-distribution Fluid Dynamics Modeling | doi:

## 验收与缺失信息策略
- acceptance_decision: （源场景未提供）
- missing_information_policy: （源场景未提供）
