# 场景：CFD_S022

- domain: cfd
- type: paper_scenario
- 算力: ['NULL'] (is_one_hpc=[False])
- 模型: ['PDE foundation model', 'In-context learner']
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
面向多物理预训练PDE时序数据完成基础模型跨PDE零样本时序预测。产出可复现模型、任务结果、物理一致性评估和适用域报告；域外工况需经CFD复核。

## 工作流步骤（→workflow/→tasks）
- s01 数据接入与契约核验
- s02 预处理与数据切分
- s03 模型配置与训练
- s04 批量推理与物理恢复
- s05 任务验收与适用域判定

## 关联论文
- Zebra_ In-Context Generative Pretraining for Solving Parametric PDEs | doi:
- Physics-informed Temporal Alignment for Auto-regressive PDE Foundation Models | doi:
- Zero-shot forecasting of chaotic systems | doi:
- Multiple Physics Pretraining for Spatiotemporal Surrogate Models | doi:
- MetaPhysiCa_ Improving OOD Robustness in Physics-informed Machine Learning | doi:
- FLUID-LLM_ Learning Computational Fluid Dynamics with Spatiotemporal-aware Large Language Models | doi:

## 验收与缺失信息策略
- acceptance_decision: （源场景未提供）
- missing_information_policy: （源场景未提供）
