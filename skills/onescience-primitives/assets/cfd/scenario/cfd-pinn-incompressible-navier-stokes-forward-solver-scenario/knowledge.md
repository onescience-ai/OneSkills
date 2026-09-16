# 场景：CFD_S036

- domain: cfd
- type: paper_scenario
- 算力: ['NULL'] (is_one_hpc=[False])
- 模型: ['PINN', 'NSFnet']
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
面向不可压层流Navier-Stokes配置与配点完成PINN不可压Navier-Stokes正问题求解。产出可复现模型、任务结果、物理一致性评估和适用域报告；域外工况需经CFD复核。

## 工作流步骤（→workflow/→tasks）
- s01 数据接入与契约核验
- s02 预处理与数据切分
- s03 模型配置与训练
- s04 方程求解与物理残差恢复
- s05 任务验收与适用域判定

## 关联论文
- NSFnets (Navier–Stokes Flow Nets): Physics-Informed Neural Networks for the Incompressible Navier–Stokes Equations | doi:
- Physics-informed deep learning for incompressible laminar flows | doi:
- Self-adaptive loss balanced Physics-informed neural networks for the incompressible Navier-Stokes equations | doi:
- Complementary, Not Cumulative_ Interaction Effects in Physics-Informed Neural Networks for Navier - Stokes Vortex Shedding | doi:
- NeuralFlowNet_ Towards Data-Free Physics-Informed Neural Network Solutions of Navier-Stokes Equations Across Low and High Reynolds Numbers | doi:

## 验收与缺失信息策略
- acceptance_decision: （源场景未提供）
- missing_information_policy: （源场景未提供）
