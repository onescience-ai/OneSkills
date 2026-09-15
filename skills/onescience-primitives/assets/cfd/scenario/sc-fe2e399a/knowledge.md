# 场景：CFD_S083

- domain: cfd
- type: paper_scenario
- 算力: ['OpenFOAM'] (is_one_hpc=[False])
- 模型: ['Deep RL controller', 'Adjoint neural controller']
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
面向翼型压力阵风载荷与控制器数据完成机翼阵风与跨声速流动主动控制。产出可复现模型、任务结果、物理一致性评估和适用域报告；域外工况需经CFD复核。

## 工作流步骤（→workflow/→tasks）
- s01 数据接入与契约核验
- s02 预处理与数据切分
- s03 模型配置与训练
- s04 闭环策略部署与滚动仿真
- s05 任务验收与适用域判定

## 关联论文
- Shocks Under Control_ Taming Transonic Compressible Flow over an RAE2822 Airfoil with Deep Reinforcement Learning | doi:
- A Deep Learning Density Shaping Model Predictive Gust Load Alleviation Control of a Compliant Wing Subjected to Atmospheric Turbulence | doi:
- Active Control of Turbulent Airfoil Flows Using Adjoint-based Deep Learning | doi:
- A Provably Robust Multi-Jet Framework applied to Active Flow Control of an Airfoil in Weakly Compressible Flow | doi:

## 验收与缺失信息策略
- acceptance_decision: （源场景未提供）
- missing_information_policy: （源场景未提供）
