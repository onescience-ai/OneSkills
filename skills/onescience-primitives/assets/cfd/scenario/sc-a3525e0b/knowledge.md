# 场景：CFD_S021

- domain: cfd
- type: paper_scenario
- 算力: ['NULL'] (is_one_hpc=[False])
- 模型: ['Diffusion model', 'Stochastic process model']
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
面向随机或混沌PDE时空数据完成扩散与随机过程时空场概率预测。产出可复现模型、任务结果、物理一致性评估和适用域报告；域外工况需经CFD复核。

## 工作流步骤（→workflow/→tasks）
- s01 数据接入与契约核验
- s02 预处理与数据切分
- s03 模型配置与训练
- s04 批量推理与物理恢复
- s05 任务验收与适用域判定

## 关联论文
- DYffusion_ A Dynamics-informed Diffusion Model for Spatiotemporal Forecasting | doi:
- Predicting the Energy Landscape of Stochastic Dynamical System via Physics-informed Self-supervised Learning | doi:
- Diffusion-Based Hierarchical Graph Neural Networks for Simulating Nonlinear Solid Mechanics | doi:
- Neural MJD_ Neural Non-Stationary Merton Jump Diffusion for Time Series Prediction | doi:
- PGODE_ Towards High-quality System Dynamics Modeling | doi:
- Deep Stochastic Processes via Functional Markov Transition Operators | doi:
- Dynamic Tensor Decomposition via Neural Diffusion-Reaction Processes | doi:
- Learning Efficient Surrogate Dynamic Models with Graph Spline Networks | doi:
- Deep learning for physical processes_ Incorporating prior scientific knowledge | doi:

## 验收与缺失信息策略
- acceptance_decision: （源场景未提供）
- missing_information_policy: （源场景未提供）
