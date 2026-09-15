# 场景：CFD_S045

- domain: cfd
- type: paper_scenario
- 算力: ['NULL'] (is_one_hpc=[False])
- 模型: ['Symbolic physics learner', 'Sparse PDE discovery']
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
面向稀疏状态轨迹与导数观测完成符号与稀疏物理学习控制方程发现。产出可复现模型、任务结果、物理一致性评估和适用域报告；域外工况需经CFD复核。

## 工作流步骤（→workflow/→tasks）
- s01 数据接入与契约核验
- s02 预处理与数据切分
- s03 模型配置与训练
- s04 方程求解与物理残差恢复
- s05 任务验收与适用域判定

## 关联论文
- Universal Physics-Informed Neural Networks_ Symbolic Differential Operator Discovery with Sparse Data | doi:
- Sub-Sequential Physics-Informed Learning with State Space Model | doi:
- Understanding Generalization in Physics Informed Models through Affine Variety Dimensions | doi:
- Competitive Physics Informed Networks | doi:
- D-CIPHER_ Discovery of Closed-form Partial Differential Equations | doi:
- Homotopy-based training of NeuralODEs for accurate dynamics discovery | doi:
- Learning Neural Constitutive Laws from Motion Observations for Generalizable PDE Dynamics | doi:
- Symbolic Physics Learner_ Discovering governing equations via Monte Carlo tree search | doi:
- Deep hidden physics models_ Deep learning of nonlinear partial differential equations | doi:
- Physics informed deep learning (Part II)_ Data-driven discovery of nonlinear partial differential equations | doi:
- Learning fluid physics from highly turbulent data using sparse physics-informed discovery of empirical relat | doi:

## 验收与缺失信息策略
- acceptance_decision: （源场景未提供）
- missing_information_policy: （源场景未提供）
