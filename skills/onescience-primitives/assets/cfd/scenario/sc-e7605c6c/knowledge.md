# 场景：CFD_S073

- domain: cfd
- type: paper_scenario
- 算力: ['NULL'] (is_one_hpc=[False])
- 模型: ['Tensor-basis neural network', 'Symbolic closure model']
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
面向DNS与RANS配对湍流闭合数据完成数据驱动RANS雷诺应力与涡黏闭合。产出可复现模型、任务结果、物理一致性评估和适用域报告；域外工况需经CFD复核。

## 工作流步骤（→workflow/→tasks）
- s01 数据接入与契约核验
- s02 预处理与数据切分
- s03 模型配置与训练
- s04 闭合项预测与后验CFD耦合
- s05 任务验收与适用域判定

## 关联论文
- Quantifying model form uncertainty in Reynolds-averaged turbulence models with Bayesian deep neural networks | doi:
- Machine learning for RANS turbulence modeling of variable property flows | doi:
- Deep Learning Methods for Reynolds-Averaged Navier–Stokes Simulations of Airfoil Flows | doi:
- Data-driven nonlinear turbulent flow scaling with Buckingham Pi variables | doi:
- Turbulence model augmented physics-informed neural networks for mean-flow reconstruction | doi:
- Predictions of turbulent shear flows using deep neural networks | doi:
- Machine-Learning-Augmented Predictive Modeling of Turbulent Separated Flows over Airfoils | doi:
- Physics-informed machine learning approach for augmenting turbulence models_ A comprehensive framework | doi:
- RANS turbulence model development using CFD-driven machine learning | doi:
- From Bypass Transition to Flow Control and Data-Driven Turbulence Modeling_ An Input–Output Viewpoint | doi:
- Perspectives on machine learning-augmented Reynolds-averaged and large eddy simulation models of turbulence | doi:
- Discovering explicit Reynolds-averaged turbulence closures for turbulent separated flows through deep learni | doi:
- FoilDiff_ A Hybrid Transformer Backbone for Diffusion-based Modelling of 2D Airfoil Flow Fields | doi:
- A Symplectic Theory of Turbulence Closure_ Hidden Reservoir Dynamics, Endogenous Stochastic Transport, and Kraichnan Dual Cascades | doi:
- A high-fidelity numerical database for free-stream transition | doi:
- Learning Turbulence Closures with Physics-Informed Neural Networks for the Rayleigh-Taylor Transition to Turbulence | doi:
- Towards bridging the gap between data-driven and theoretical turbulence closures in stratified flows | doi:
- VATO_ A Vortex-Force-Aware Transformer Operator for Unsteady Separated Aerofoil Flows | doi:

## 验收与缺失信息策略
- acceptance_decision: （源场景未提供）
- missing_information_policy: （源场景未提供）
