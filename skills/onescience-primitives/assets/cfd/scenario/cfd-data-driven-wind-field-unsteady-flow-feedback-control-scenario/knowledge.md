# 场景：CFD_S084

- domain: cfd
- type: paper_scenario
- 算力: ['OpenFOAM'] (is_one_hpc=[False])
- 模型: ['Reduced-order controller', 'Neural MPC']
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
面向风场尾迹状态与反馈控制数据完成数据驱动风场与非定常流反馈控制。产出可复现模型、任务结果、物理一致性评估和适用域报告；域外工况需经CFD复核。

## 工作流步骤（→workflow/→tasks）
- s01 数据接入与契约核验
- s02 预处理与数据切分
- s03 模型配置与训练
- s04 闭环策略部署与滚动仿真
- s05 任务验收与适用域判定

## 关联论文
- Deep Dynamical Modeling and Control of Unsteady Fluid Flows | doi:
- An Interactive Interface for Control Integration in Mid-Fidelity Wind Farm Simulation | doi:
- Feedback control of vortex shedding using data-driven modelling | doi:

## 验收与缺失信息策略
- acceptance_decision: （源场景未提供）
- missing_information_policy: （源场景未提供）
