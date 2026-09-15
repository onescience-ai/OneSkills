# 场景：CFD_S024

- domain: cfd
- type: paper_scenario
- 算力: ['NULL'] (is_one_hpc=[False])
- 模型: ['EddyFormer', 'Mesh Transformer']
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
面向三维DNS与LES体湍流数据完成三维湍流Transformer多尺度时空预测。产出可复现模型、任务结果、物理一致性评估和适用域报告；域外工况需经CFD复核。

## 工作流步骤（→workflow/→tasks）
- s01 数据接入与契约核验
- s02 预处理与数据切分
- s03 模型配置与训练
- s04 批量推理与物理恢复
- s05 任务验收与适用域判定

## 关联论文
- EAGLE_ Large-scale Learning of Turbulent Fluid Dynamics with Mesh Transformers | doi:
- EddyFormer_ Accelerated Neural Simulations of Three-Dimensional Turbulence at Scale | doi:
- Erwin_ A Tree-based Hierarchical Transformer for Large-scale Physical Systems | doi:

## 验收与缺失信息策略
- acceptance_decision: （源场景未提供）
- missing_information_policy: （源场景未提供）
