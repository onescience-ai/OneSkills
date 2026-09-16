# 场景：CFD_S063

- domain: cfd
- type: paper_scenario
- 算力: ['NULL'] (is_one_hpc=[False])
- 模型: ['Lie-equivariant neural network', 'PDO convolution']
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
面向具有旋转平移群对称的PDE数据完成Lie群等变网络对称PDE预测。产出可复现模型、任务结果、物理一致性评估和适用域报告；域外工况需经CFD复核。

## 工作流步骤（→workflow/→tasks）
- s01 数据接入与契约核验
- s02 预处理与数据切分
- s03 模型配置与训练
- s04 批量推理与物理恢复
- s05 任务验收与适用域判定

## 关联论文
- Lie Algebra Canonicalization_ Equivariant Neural Operators under arbitrary Lie Groups | doi:
- Space-Time Continuous PDE Forecasting using Equivariant Neural Fields | doi:
- Physics and Lie symmetry informed Gaussian processes | doi:
- Equivariant Neural Simulators for Stochastic Spatiotemporal Dynamics | doi:
- Equivariant Spatio-Temporal Attentive Graph Networks to Simulate Physical Dynamics | doi:
- Self-Supervised Learning with Lie Symmetries for Partial Differential Equations | doi:
- Approximately Equivariant Networks for Imperfectly Symmetric Dynamics | doi:
- PDO-eConvs_ Partial Differential Operator Based Equivariant Convolutions | doi:
- PDO-s3DCNNs_ Partial Differential Operator Based Steerable 3D CNNs | doi:

## 验收与缺失信息策略
- acceptance_decision: （源场景未提供）
- missing_information_policy: （源场景未提供）
