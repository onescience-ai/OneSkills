# 场景：CFD_S079

- domain: cfd
- type: paper_scenario
- 算力: ['NULL'] (is_one_hpc=[False])
- 模型: ['Neural SDE closure', 'Probabilistic coarse-graining model']
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
面向多尺度湍流粗细状态轨迹完成随机微分与概率粗粒化湍流闭合。产出可复现模型、任务结果、物理一致性评估和适用域报告；域外工况需经CFD复核。

## 工作流步骤（→workflow/→tasks）
- s01 数据接入与契约核验
- s02 预处理与数据切分
- s03 模型配置与训练
- s04 闭合项预测与后验CFD耦合
- s05 任务验收与适用域判定

## 关联论文
- A physics-aware, probabilistic machine learning framework for coarse-graining high-dimensional systems in the Sm | doi:
- Neural Ideal Large Eddy Simulation_ Modeling Turbulence with Neural Stochastic Differential Equations | doi:
- Learning Stochastic Multiscale Models | doi:
- Echo state network for two-dimensional turbulent moist Rayleigh-Bénard convection | doi:
- Machine-learning energy-preserving nonlocal closures for turbulent fluid flows and inertial tracers | doi:

## 验收与缺失信息策略
- acceptance_decision: （源场景未提供）
- missing_information_policy: （源场景未提供）
