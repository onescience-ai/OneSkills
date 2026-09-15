# 场景：CFD_S018

- domain: cfd
- type: paper_scenario
- 算力: ['NULL'] (is_one_hpc=[False])
- 模型: ['Autoregressive CNN', 'PDE-Refiner']
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
面向圆柱绕流非定常时序数据完成自回归网络圆柱尾迹长时滚动预测。产出可复现模型、任务结果、物理一致性评估和适用域报告；域外工况需经CFD复核。

## 工作流步骤（→workflow/→tasks）
- s01 数据接入与契约核验
- s02 预处理与数据切分
- s03 模型配置与训练
- s04 批量推理与物理恢复
- s05 任务验收与适用域判定

## 关联论文
- PDE-Refiner_ Achieving Accurate Long Rollouts with Neural PDE Solvers | doi:
- Data-driven prediction of unsteady flow over a circular cylinder using deep learning | doi:
- ANTN_ Bridging Autoregressive Neural Networks and Tensor Networks for Quantum Many-Body Simulation | doi:

## 验收与缺失信息策略
- acceptance_decision: （源场景未提供）
- missing_information_policy: （源场景未提供）
