# 场景：CFD_S080

- domain: cfd
- type: paper_scenario
- 算力: ['NULL'] (is_one_hpc=[False])
- 模型: ['Data-driven LES source model']
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
面向叶轮高升力与工程LES及DNS数据完成工程LES等效源项与高保真校准。产出可复现模型、任务结果、物理一致性评估和适用域报告；域外工况需经CFD复核。

## 工作流步骤（→workflow/→tasks）
- s01 数据接入与契约核验
- s02 预处理与数据切分
- s03 模型配置与训练
- s04 闭合项预测与后验CFD耦合
- s05 任务验收与适用域判定

## 关联论文
- Data-driven impeller model for efficient large eddy simulations of metastable von Kármán flows | doi:
- Deep learning observables in computational fluid dynamics | doi:
- Learning to Estimate and Refine Fluid Motion with Physical Dynamics | doi:
- Bayesian optimization and topographic exploration of drag-reducing dimples for aerodynamic surfaces | doi:
- HiLiftAeroML_ High-Fidelity Computational Fluid Dynamics Dataset for High-Lift Aircraft Aerodynamics | doi:

## 验收与缺失信息策略
- acceptance_decision: （源场景未提供）
- missing_information_policy: （源场景未提供）
