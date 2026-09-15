# 场景：CFD_S056

- domain: cfd
- type: paper_scenario
- 算力: ['NULL'] (is_one_hpc=[False])
- 模型: ['PDE foundation model', 'Pretrained neural operator']
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
面向多物理多分辨率大规模预训练数据完成科学基础模型多物理算子迁移。产出可复现模型、任务结果、物理一致性评估和适用域报告；域外工况需经CFD复核。

## 工作流步骤（→workflow/→tasks）
- s01 数据接入与契约核验
- s02 预处理与数据切分
- s03 模型配置与训练
- s04 批量推理与物理恢复
- s05 任务验收与适用域判定

## 关联论文
- Poseidon_ Efficient Foundation Models for PDEs | doi:
- DGNet_ Discrete Green Networks for Data-Efficient Learning of Spatiotemporal PDEs | doi:
- OmniArch_ Building Foundation Model for Scientific Computing | doi:
- Towards a Physics Foundation Model | doi:
- Data-Efficient Operator Learning via Unsupervised Pretraining and In-Context Learning | doi:
- Pretraining Codomain Attention Neural Operators for Solving Multiphysics PDEs | doi:
- Differentiable Modal Synthesis for Physical Modeling of Planar String Sound and Motion Simulation | doi:
- Training Deep Surrogate Models with Large Scale Online Learning | doi:
- Learning Data-Efficient and Generalizable Neural Operators via Fundamental Physics Knowledge | doi:

## 验收与缺失信息策略
- acceptance_decision: （源场景未提供）
- missing_information_policy: （源场景未提供）
