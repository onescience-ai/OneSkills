# 场景：CFD_S096

- domain: cfd
- type: paper_scenario
- 算力: ['NULL'] (is_one_hpc=[False])
- 模型: ['CNN decoder', '3D GAN']
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
面向壁面压力剪切与DNS体场配对数据完成稀疏壁面传感器三维湍流全场重构。产出可复现模型、任务结果、物理一致性评估和适用域报告；域外工况需经CFD复核。

## 工作流步骤（→workflow/→tasks）
- s01 数据接入与契约核验
- s02 预处理与数据切分
- s03 模型配置与训练
- s04 低分辨或部分观测流场重构
- s05 任务验收与适用域判定

## 关联论文
- Sparse sensor reconstruction of vortex-impinged airfoil wake with machine learning | doi:
- From coarse wall measurements to turbulent velocity fields with deep learning | doi:
- Three-dimensional generative adversarial networks for turbulent flow estimation from wall measurements | doi:
- Reconstruction of three-dimensional turbulent flow structures using surface measurements for free-surface flows | doi:

## 验收与缺失信息策略
- acceptance_decision: （源场景未提供）
- missing_information_policy: （源场景未提供）
