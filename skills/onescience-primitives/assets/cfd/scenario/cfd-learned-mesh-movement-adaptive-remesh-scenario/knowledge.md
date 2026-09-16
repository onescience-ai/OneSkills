# 场景：CFD_S068

- domain: cfd
- type: paper_scenario
- 算力: ['OpenFOAM'] (is_one_hpc=[False])
- 模型: ['Mesh movement network']
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
面向网格误差指标与移动目标数据完成学习型网格移动与自适应重网格。产出可复现模型、任务结果、物理一致性评估和适用域报告；域外工况需经CFD复核。

## 工作流步骤（→workflow/→tasks）
- s01 数据接入与契约核验
- s02 预处理与数据切分
- s03 模型配置与训练
- s04 神经数值耦合求解
- s05 任务验收与适用域判定

## 关联论文
- UGM2N_ An Unsupervised and Generalizable Mesh Movement Network via M-Uniform Loss | doi:
- Better Neural PDE Solvers Through Data-Free Mesh Movers | doi:
- Self-Supervised Coarsening of Unstructured Grid with Automatic Differentiation | doi:
- Lie Point Symmetry and Physics-Informed Networks | doi:
- MMGP_ a Mesh Morphing Gaussian Process-based machine learning method for regression of physical problems under n | doi:
- M2N_ Mesh Movement Networks for PDE Solvers | doi:
- Learning Mesh-Based Simulation with Graph Networks | doi:

## 验收与缺失信息策略
- acceptance_decision: （源场景未提供）
- missing_information_policy: （源场景未提供）
