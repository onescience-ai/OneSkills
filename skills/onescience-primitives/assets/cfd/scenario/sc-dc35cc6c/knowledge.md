# 场景：CFD_S067

- domain: cfd
- type: paper_scenario
- 算力: ['OpenFOAM'] (is_one_hpc=[False])
- 模型: ['Neural corrector', 'Hybrid PDE solver']
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
面向粗细网格CFD成对轨迹完成神经校正器耦合粗网格CFD加速。产出可复现模型、任务结果、物理一致性评估和适用域报告；域外工况需经CFD复核。

## 工作流步骤（→workflow/→tasks）
- s01 数据接入与契约核验
- s02 预处理与数据切分
- s03 模型配置与训练
- s04 神经数值耦合求解
- s05 任务验收与适用域判定

## 关联论文
- INC_ An Indirect Neural Corrector for Auto-Regressive Hybrid PDE Solvers | doi:
- MultiPDENet_ PDE-embedded Learning with Multi-time-stepping for Accelerated Flow Simulation | doi:
- P2C2Net_ PDE-Preserved Coarse Correction Network for efficient prediction of spatiotemporal dynamics | doi:
- Toward Efficient Kernel-Based Solvers for Nonlinear PDEs | doi:
- Accelerating Legacy Numerical Solvers by Non-intrusive Gradient-based Meta-solving | doi:
- Neural Network Approximations of PDEs Beyond Linearity_ A Representational Perspective | doi:

## 验收与缺失信息策略
- acceptance_decision: （源场景未提供）
- missing_information_policy: （源场景未提供）
