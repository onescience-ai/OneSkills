# 场景：CFD_S078

- domain: cfd
- type: paper_scenario
- 算力: ['NULL'] (is_one_hpc=[False])
- 模型: ['CNN SGS model']
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
面向二维湍流DNS滤波与LES数据完成卷积网络二维湍流LES亚格子闭合。产出可复现模型、任务结果、物理一致性评估和适用域报告；域外工况需经CFD复核。

## 工作流步骤（→workflow/→tasks）
- s01 数据接入与契约核验
- s02 预处理与数据切分
- s03 模型配置与训练
- s04 闭合项预测与后验CFD耦合
- s05 任务验收与适用域判定

## 关联论文
- Data-driven subgrid-scale modeling of forced Burgers turbulence using deep learning with generalization to h | doi:
- Subgrid modelling for two-dimensional turbulence using neural networks | doi:
- Stable a Posteriori LES of 2D Turbulence Using Convolutional Neural Networks: Backscattering Analysis and Generalization to Higher Re via Transfer Learning | doi:
- Sub-grid scale model classification and blending through deep learning | doi:

## 验收与缺失信息策略
- acceptance_decision: （源场景未提供）
- missing_information_policy: （源场景未提供）
