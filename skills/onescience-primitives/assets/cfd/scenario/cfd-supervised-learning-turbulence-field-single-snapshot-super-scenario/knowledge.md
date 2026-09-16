# 场景：CFD_S098

- domain: cfd
- type: paper_scenario
- 算力: ['NULL'] (is_one_hpc=[False])
- 模型: ['Super-resolution CNN']
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
面向成对低高分辨率DNS快照完成监督学习湍流场单快照超分辨率重建。产出可复现模型、任务结果、物理一致性评估和适用域报告；域外工况需经CFD复核。

## 工作流步骤（→workflow/→tasks）
- s01 数据接入与契约核验
- s02 预处理与数据切分
- s03 模型配置与训练
- s04 低分辨或部分观测流场重构
- s05 任务验收与适用域判定

## 关联论文
- Single-snapshot machine learning for super-resolution of turbulence | doi:
- Super-resolution reconstruction of turbulent flows with machine learning | doi:
- Extending a Physics-Informed Machine Learning Network for Superresolution Studies of Rayleigh-Bénard Convection | doi:
- Turbulence in Focus_ Benchmarking Scaling Behavior of 3D Volumetric Super-Resolution with BLASTNet 2.0 Data | doi:

## 验收与缺失信息策略
- acceptance_decision: （源场景未提供）
- missing_information_policy: （源场景未提供）
