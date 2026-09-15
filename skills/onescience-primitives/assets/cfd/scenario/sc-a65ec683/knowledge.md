# 场景：CFD_S071

- domain: cfd
- type: paper_scenario
- 算力: ['OpenFOAM'] (is_one_hpc=[False])
- 模型: ['Differentiable simulator', 'Mechanistic PDE network']
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
面向可微数值轨迹与算子数据完成可微分物理求解与方程结构学习。产出可复现模型、任务结果、物理一致性评估和适用域报告；域外工况需经CFD复核。

## 工作流步骤（→workflow/→tasks）
- s01 数据接入与契约核验
- s02 预处理与数据切分
- s03 模型配置与训练
- s04 神经数值耦合求解
- s05 任务验收与适用域判定

## 关联论文
- Mechanistic PDE Networks for Discovery of Governing Equations | doi:
- Hamiltonian Neural PDE Solvers through Functional Approximation | doi:
- PhysPDE_ Rethinking PDE Discovery and a Physical HYpothesis Selection Benchmark | doi:
- Neural Stochastic Flows_ Solver-Free Modelling and Inference for SDE Solutions | doi:
- Accelerating PDE Data Generation via Differential Operator Action in Solution Space | doi:
- Stochastic Taylor Derivative Estimator_ Efficient Amortization for Arbitrary Differential Operators | doi:
- ΦFlow_ Differentiable Simulations for PyTorch, TensorFlow and Jax | doi:

## 验收与缺失信息策略
- acceptance_decision: （源场景未提供）
- missing_information_policy: （源场景未提供）
