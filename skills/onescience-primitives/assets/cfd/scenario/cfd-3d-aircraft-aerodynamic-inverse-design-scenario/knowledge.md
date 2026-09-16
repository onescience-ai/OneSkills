# 场景：CFD_S035

- domain: cfd
- type: paper_scenario
- 算力: ['NULL'] (is_one_hpc=[False])
- 模型: ['3D inverse design network', 'Physics-aware optimizer']
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
面向三维机翼与融合翼身气动数据完成三维航空器目标气动响应逆向设计。产出可复现模型、任务结果、物理一致性评估和适用域报告；域外工况需经CFD复核。

## 工作流步骤（→workflow/→tasks）
- s01 数据接入与契约核验
- s02 预处理与数据切分
- s03 模型配置与训练
- s04 候选生成与约束优化
- s05 任务验收与适用域判定

## 关联论文
- BlendedNet++_ A dataset and benchmark for field-resolved aerodynamics and inverse design of blended wing body aircraft | doi:
- Inverse Design for Fluid-Structure Interactions using Graph Network Simulators | doi:
- PIED_ Physics-Informed Experimental Design for Inverse Problems | doi:
- 3DID_ Direct 3D Inverse Design for Aerodynamics with Physics-Aware Optimization | doi:

## 验收与缺失信息策略
- acceptance_decision: （源场景未提供）
- missing_information_policy: （源场景未提供）
