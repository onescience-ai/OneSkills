# 场景：CFD_S091

- domain: cfd
- type: paper_scenario
- 算力: ['NULL'] (is_one_hpc=[False])
- 模型: ['Physics-informed diffusion model']
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
面向条件流场与物理残差数据完成物理信息扩散模型流场分布生成。产出可复现模型、任务结果、物理一致性评估和适用域报告；域外工况需经CFD复核。

## 工作流步骤（→workflow/→tasks）
- s01 数据接入与契约核验
- s02 预处理与数据切分
- s03 模型配置与训练
- s04 条件采样与物理一致性筛选
- s05 任务验收与适用域判定

## 关联论文
- Physics-Informed Diffusion Models | doi:
- Broadband Ground Motion Synthesis by Diffusion Model with Minimal Condition | doi:
- Improved Sampling Of Diffusion Models In Fluid Dynamics With Tweedie's Formula | doi:
- Learning Distributions of Complex Fluid Simulations with Diffusion Graph Networks | doi:
- Physics-Informed Variational State-Space Gaussian Processes | doi:
- How well can Diffusion Models learn Lagrangian-Tracer Statistics in Non-reciprocal Turbulence | doi:

## 验收与缺失信息策略
- acceptance_decision: （源场景未提供）
- missing_information_policy: （源场景未提供）
