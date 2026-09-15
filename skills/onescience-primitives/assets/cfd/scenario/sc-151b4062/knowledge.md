# 场景：CFD_S053

- domain: cfd
- type: paper_scenario
- 算力: ['NULL'] (is_one_hpc=[False])
- 模型: ['Mamba Neural Operator', 'State-space operator']
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
面向时间依赖PDE轨迹数据完成Mamba状态空间神经算子时序预测。产出可复现模型、任务结果、物理一致性评估和适用域报告；域外工况需经CFD复核。

## 工作流步骤（→workflow/→tasks）
- s01 数据接入与契约核验
- s02 预处理与数据切分
- s03 模型配置与训练
- s04 批量推理与物理恢复
- s05 任务验收与适用域判定

## 关联论文
- Mamba Neural Operator_ Who Wins_ Transformers or State-Space Models for PDEs | doi:
- HEAP_ Hyper Extended A-PDHG Operator for Constrained High-dim PDEs | doi:
- Latent Mamba Operator for Partial Differential Equations | doi:
- Improved Operator Learning by Orthogonal Attention | doi:
- On the Benefits of Memory for Modeling Time-Dependent PDEs | doi:
- Adaptive Mamba Neural Operators | doi:
- A Compensated Koopman Neural Operator with Selective State-Space Dynamics for Unsteady Flows | doi:

## 验收与缺失信息策略
- acceptance_decision: （源场景未提供）
- missing_information_policy: （源场景未提供）
