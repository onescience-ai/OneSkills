# 场景：CFD_S014

- domain: cfd
- type: paper_scenario
- 算力: ['NULL'] (is_one_hpc=[False])
- 模型: ['CNN', 'Aerodynamic foundation model']
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
面向翼型壁面压力剪切及速度测量数据完成壁面压力剪切与积分气动力联合反演。产出可复现模型、任务结果、物理一致性评估和适用域报告；域外工况需经CFD复核。

## 工作流步骤（→workflow/→tasks）
- s01 数据接入与契约核验
- s02 预处理与数据切分
- s03 模型配置与训练
- s04 批量推理与物理恢复
- s05 任务验收与适用域判定

## 关联论文
- Predicting the wall-shear stress and wall pressure through convolutional neural networks | doi:
- Data-driven estimation of scalar quantities from planar velocity measurements by deep learning applied to temper | doi:
- Towards a Foundation-Model Paradigm for Aerodynamic Prediction in Three-dimensional Design | doi:

## 验收与缺失信息策略
- acceptance_decision: （源场景未提供）
- missing_information_policy: （源场景未提供）
