# 场景：CFD_S082

- domain: cfd
- type: paper_scenario
- 算力: ['OpenFOAM'] (is_one_hpc=[False])
- 模型: ['Differentiable controller', 'Diffusion policy']
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
面向PDE状态控制目标轨迹完成可微与生成式PDE最优控制。产出可复现模型、任务结果、物理一致性评估和适用域报告；域外工况需经CFD复核。

## 工作流步骤（→workflow/→tasks）
- s01 数据接入与契约核验
- s02 预处理与数据切分
- s03 模型配置与训练
- s04 闭环策略部署与滚动仿真
- s05 任务验收与适用域判定

## 关联论文
- NeuralFluid_ Nueral Fluidic System Design and Control with Differentiable Simulation | doi:
- From Uncertain to Safe_ Conformal Adaptation of Diffusion Models for Safe PDE Control | doi:
- DiffPhyCon_ A Generative Approach to Control Complex Physical Systems | doi:

## 验收与缺失信息策略
- acceptance_decision: （源场景未提供）
- missing_information_policy: （源场景未提供）
