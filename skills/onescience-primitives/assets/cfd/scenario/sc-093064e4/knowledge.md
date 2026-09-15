# 场景：CFD_S047

- domain: cfd
- type: paper_scenario
- 算力: ['NULL'] (is_one_hpc=[False])
- 模型: ['Meta-PINN', 'PINN agent', 'PINN Transformer']
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
面向PDEBench与PINNacle多方程基准完成自动化与元学习PINN跨方程求解。产出可复现模型、任务结果、物理一致性评估和适用域报告；域外工况需经CFD复核。

## 工作流步骤（→workflow/→tasks）
- s01 数据接入与契约核验
- s02 预处理与数据切分
- s03 模型配置与训练
- s04 方程求解与物理残差恢复
- s05 任务验收与适用域判定

## 关联论文
- PINNacle_ A Comprehensive Benchmark of Physics-Informed Neural Networks for Solving PDEs | doi:
- HyPINO_ Multi-Physics Neural Operators via HyperPINNs and the Method of Manufactured Solutions | doi:
- PINNsAgent_ Automated PDE Surrogation with Large Language Models | doi:
- DATS_ Difficulty-Aware Task Sampler for Meta-Learning Physics-Informed Neural Networks | doi:
- Hypernetwork-based Meta-Learning for Low-Rank Physics-Informed Neural Networks | doi:
- PPINN_ Parareal physics-informed neural network for time-dependent PDEs | doi:
- PDEBench_ An Extensive Benchmark for Scientific Machine Learning | doi:
- PINNsFormer_ A Transformer-Based Framework For Physics-Informed Neural Networks | doi:

## 验收与缺失信息策略
- acceptance_decision: （源场景未提供）
- missing_information_policy: （源场景未提供）
