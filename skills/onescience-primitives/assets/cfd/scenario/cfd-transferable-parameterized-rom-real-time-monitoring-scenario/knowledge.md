# 场景：CFD_S090

- domain: cfd
- type: paper_scenario
- 算力: ['NULL'] (is_one_hpc=[False])
- 模型: ['Transferable ROM', 'Shallow recurrent decoder']
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
面向跨几何参数CFD与稀疏监测数据完成可迁移参数化ROM与实时状态监测。产出可复现模型、任务结果、物理一致性评估和适用域报告；域外工况需经CFD复核。

## 工作流步骤（→workflow/→tasks）
- s01 数据接入与契约核验
- s02 预处理与数据切分
- s03 模型配置与训练
- s04 批量推理与物理恢复
- s05 任务验收与适用域判定

## 关联论文
- Real-Time Monitoring of MHD Liquid Metal Flows with Shallow Recurrent Decoders | doi:
- Non-intrusive, transferable model for coupled turbulent channel-porous media flow based upon neural networks | doi:
- Numerically Solving Parametric Families of High-Dimensional Kolmogorov Partial Differential Equations via De | doi:
- Intrusive versus non-intrusive reduced-order modeling of generalized Newtonian fluid flows | doi:
- Neural Network-Based Parametric Model Reduction for Predicting Turbulent Flow for Different Vehicle Geometries | doi:
- Reliable and efficient steady CFD from surrogate predictions through Newton-Krylov correction | doi:

## 验收与缺失信息策略
- acceptance_decision: （源场景未提供）
- missing_information_policy: （源场景未提供）
