# 场景：CFD_S089

- domain: cfd
- type: paper_scenario
- 算力: ['NULL'] (is_one_hpc=[False])
- 模型: ['Neural aerodynamic ROM', 'Neural ODE']
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
面向非定常气动力与耦合响应时序完成气动弹性与非定常载荷降阶响应预测。产出可复现模型、任务结果、物理一致性评估和适用域报告；域外工况需经CFD复核。

## 工作流步骤（→workflow/→tasks）
- s01 数据接入与契约核验
- s02 预处理与数据切分
- s03 模型配置与训练
- s04 批量推理与物理恢复
- s05 任务验收与适用域判定

## 关联论文
- Modeling Unsteady Aircraft Aerodynamics Using Lorenz Attractor_ A Reduced-Order Approach for Wing Rock | doi:
- Deep Learning-Based Reduced Order Model for Three-Dimensional Unsteady Flow Using Mesh Transformation and Stitching | doi:
- Stable Port-Hamiltonian Neural Networks | doi:
- Convolutional neural network and long short-term memory based reduced order surrogate for minimal turbulent chan | doi:
- A deep learning enabler for nonintrusive reduced order modeling of fluid flows | doi:
- Validation and parameterization of a novel physics-constrained neural dynamics model applied to turbulent fl | doi:
- Amortized Inference for Model Rocket Aerodynamics _ Learning to Estimate Physical Parameters from Simulation | doi:
- A Residual Learning Approach for Unsteady Aerodynamic Load Prediction | doi:
- Kolmogorov Arnold networks (KAN) for aerodynamic prediction_ a comparison with MLPs and GNNs | doi:
- Neural-Network and Reduced-order Modeling Workflows for AI-Driven CFD_ Fast Response Surfaces, Reduced Dynamics and Jet in Cross-flow Examples | doi:
- Nonlinear Model Order Reduction for Coupled Aeroelastic-Flight Dynamic Systems | doi:

## 验收与缺失信息策略
- acceptance_decision: （源场景未提供）
- missing_information_policy: （源场景未提供）
