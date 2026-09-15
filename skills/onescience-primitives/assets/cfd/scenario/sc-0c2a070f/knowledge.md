# 场景：CFD_S023

- domain: cfd
- type: paper_scenario
- 算力: ['NULL'] (is_one_hpc=[False])
- 模型: ['Parareal neural solver', 'Temporal neural operator']
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
面向长时间多尺度PDE轨迹完成时间并行与多时间尺度神经PDE推进。产出可复现模型、任务结果、物理一致性评估和适用域报告；域外工况需经CFD复核。

## 工作流步骤（→workflow/→tasks）
- s01 数据接入与契约核验
- s02 预处理与数据切分
- s03 模型配置与训练
- s04 批量推理与物理恢复
- s05 任务验收与适用域判定

## 关联论文
- A Neural PDE Solver with Temporal Stencil Modeling | doi:
- Advection Augmented Convolutional Neural Networks | doi:
- Continuous Temporal Domain Generalization | doi:
- RandNet-Parareal_ a time-parallel PDE solver using Random Neural Networks | doi:
- TENG_ Time-Evolving Natural Gradient for Solving PDEs With Deep Neural Nets Toward Machine Precision | doi:
- PARCv2_ Physics-aware Recurrent Convolutional Neural Networks for Spatiotemporal Dynamics Modeling | doi:
- Anamnesic Neural Differential Equations with Orthogonal Polynomial Projections | doi:
- CARE_ Modeling Interacting Dynamics Under Temporal Environmental Variation | doi:
- Neural-Fly enables rapid learning for agile flight in strong winds | doi:

## 验收与缺失信息策略
- acceptance_decision: （源场景未提供）
- missing_information_policy: （源场景未提供）
