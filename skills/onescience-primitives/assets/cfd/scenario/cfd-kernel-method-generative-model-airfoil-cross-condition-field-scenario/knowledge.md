# 场景：CFD_S003

- domain: cfd
- type: paper_scenario
- 算力: ['NULL'] (is_one_hpc=[False])
- 模型: ['Kernel surrogate', 'Diffusion model']
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
面向参数化翼型多工况与多保真数据完成核方法与生成模型翼型跨工况场预测。产出可复现模型、任务结果、物理一致性评估和适用域报告；域外工况需经CFD复核。

## 工作流步骤（→workflow/→tasks）
- s01 数据接入与契约核验
- s02 预处理与数据切分
- s03 模型配置与训练
- s04 批量推理与物理恢复
- s05 任务验收与适用域判定

## 关联论文
- A Kernel-based Resource-efficient Neural Surrogate for Multi-fidelity Prediction of Aerodynamic Field | doi:
- AFBench_ A Large-scale Benchmark for Airfoil Design | doi:
- Airfoil optimization using Design-by-Morphing with minimized design-space dimensionality | doi:
- Predictive Criteria for Electrospray-Assisted Droplet Dynamics in Aerodynamic Flow Fields | doi:
- AeroJEPA_ Learning Semantic Latent Representations for Scalable 3D Aerodynamic Field Modeling | doi:
- AirfoilGen_ A valid-by-construction and performance-aware latent diffusion model for airfoil generation | doi:

## 验收与缺失信息策略
- acceptance_decision: （源场景未提供）
- missing_information_policy: （源场景未提供）
