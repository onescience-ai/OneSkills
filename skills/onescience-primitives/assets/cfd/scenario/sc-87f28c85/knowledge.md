# 场景：CFD_S041

- domain: cfd
- type: paper_scenario
- 算力: ['NULL'] (is_one_hpc=[False])
- 模型: ['FBPINN', 'XPINN', 'Parallel PINN']
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
面向分区PDE配点与界面条件数据完成区域分解并行PINN大域求解。产出可复现模型、任务结果、物理一致性评估和适用域报告；域外工况需经CFD复核。

## 工作流步骤（→workflow/→tasks）
- s01 数据接入与契约核验
- s02 预处理与数据切分
- s03 模型配置与训练
- s04 方程求解与物理残差恢复
- s05 任务验收与适用域判定

## 关联论文
- Finite Basis Physics-Informed Neural Networks (FBPINNs): A Scalable Domain Decomposition Approach for Solving Differential Equations | doi:
- PINN Balls_ Scaling Second-Order Methods for PINNs with Domain Decomposition and Adaptive Sampling | doi:
- Meta Learning of Interface Conditions for Multi-Domain Physics-Informed Neural Networks | doi:
- Parallel Physics-Informed Neural Networks via Domain Decomposition | doi:
- When Do Extended Physics-Informed Neural Networks (XPINNs) Improve Generalization | doi:

## 验收与缺失信息策略
- acceptance_decision: （源场景未提供）
- missing_information_policy: （源场景未提供）
