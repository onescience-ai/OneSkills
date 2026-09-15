# 场景：CFD_S060

- domain: cfd
- type: paper_scenario
- 算力: ['NULL'] (is_one_hpc=[False])
- 模型: ['Continuous-time neural operator', 'Stochastic neural operator']
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
面向随机或连续时间PDE分布数据完成连续时间与随机生成神经算子预测。产出可复现模型、任务结果、物理一致性评估和适用域报告；域外工况需经CFD复核。

## 工作流步骤（→workflow/→tasks）
- s01 数据接入与契约核验
- s02 预处理与数据切分
- s03 模型配置与训练
- s04 批量推理与物理恢复
- s05 任务验收与适用域判定

## 关联论文
- CFO_ Learning Continuous-Time PDE Dynamics via Flow-Matched Neural Operators | doi:
- Wavelet Diffusion Neural Operator | doi:
- Learning Semilinear Neural Operators_ A Unified Recursive Framework for Prediction and Data Assimilation | doi:
- Boosting Generalization in Parametric PDE Neural Solvers through Adaptive Conditioning | doi:
- Convolutional Neural Operators for Robust and Accurate Learning of PDEs | doi:
- Deep Equilibrium Based Neural Operators for Steady-State PDEs | doi:
- Representation Equivalent Neural Operators_ a Framework for Alias-free Operator Learning | doi:
- Neural Stochastic PDEs_ Resolution-Invariant Learning of Continuous Spatiotemporal Dynamics | doi:
- Variational Autoencoding Neural Operators | doi:
- Newton Informed Neural Operator for Solving Nonlinear Partial Differential Equations | doi:
- Linearization Turns Neural Operators into Function-Valued Gaussian Processes | doi:
- Optimization for Neural Operators can Benefit from Width | doi:
- KANO_ Kolmogorov-Arnold Neural Operator | doi:
- Riesz Neural Operator for Solving Partial Differential Equations | doi:

## 验收与缺失信息策略
- acceptance_decision: （源场景未提供）
- missing_information_policy: （源场景未提供）
