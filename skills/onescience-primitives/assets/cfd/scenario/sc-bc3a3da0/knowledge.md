# 场景：CFD_S049

- domain: cfd
- type: paper_scenario
- 算力: ['NULL'] (is_one_hpc=[False])
- 模型: ['Factorized FNO', 'Multigrid neural operator']
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
面向高分辨率规则网格PDE数据完成因子分解与多重网格FNO高效算子学习。产出可复现模型、任务结果、物理一致性评估和适用域报告；域外工况需经CFD复核。

## 工作流步骤（→workflow/→tasks）
- s01 数据接入与契约核验
- s02 预处理与数据切分
- s03 模型配置与训练
- s04 批量推理与物理恢复
- s05 任务验收与适用域判定

## 关联论文
- MgNO_ Efficient Parameterization of Linear Operators via Multigrid | doi:
- MGCFNN_ A Neural MultiGrid Solver with Novel Fourier Neural Network for High Wave Number Helmholtz Equations | doi:
- Operator SVD with Neural Networks via Nested Low-Rank Approximation | doi:
- U-NO_ U-Shaped Neural Operators | doi:

## 验收与缺失信息策略
- acceptance_decision: （源场景未提供）
- missing_information_policy: （源场景未提供）
