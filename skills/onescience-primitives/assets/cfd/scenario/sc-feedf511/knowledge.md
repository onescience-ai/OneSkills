# 场景：CFD_S031

- domain: cfd
- type: paper_scenario
- 算力: ['NULL'] (is_one_hpc=[False])
- 模型: ['Multi-fidelity surrogate', 'Bayesian optimizer']
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
面向多工况翼型几何与气动力数据完成多保真代理辅助翼型外形优化。产出可复现模型、任务结果、物理一致性评估和适用域报告；域外工况需经CFD复核。

## 工作流步骤（→workflow/→tasks）
- s01 数据接入与契约核验
- s02 预处理与数据切分
- s03 模型配置与训练
- s04 候选生成与约束优化
- s05 任务验收与适用域判定

## 关联论文
- Surrogate-Based Aerodynamic Shape Optimization in Multiscale Flows via the Implicit Unified Gas-Kinetic Scheme | doi:
- Multi-Timescale Dynamics Model Bayesian Optimization for Plasma Stabilization in Tokamaks | doi:
- Optimization-Embedded Active Multi-Fidelity Surrogate Learning for Multi-Condition Airfoil Shape Optimization | doi:
- ShapeBench_ A Scalable Benchmark and Diagnostic Suite for Standardized Evaluation in Aerodynamic Shape Optimization | doi:

## 验收与缺失信息策略
- acceptance_decision: （源场景未提供）
- missing_information_policy: （源场景未提供）
