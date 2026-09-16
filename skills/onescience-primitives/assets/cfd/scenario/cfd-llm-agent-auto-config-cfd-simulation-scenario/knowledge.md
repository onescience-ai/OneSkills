# 场景：CFD_S070

- domain: cfd
- type: paper_scenario
- 算力: ['OpenFOAM'] (is_one_hpc=[False])
- 模型: ['CFD LLM agent']
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
面向OpenFOAM与FEM案例及运行日志完成LLM智能体自动配置与执行CFD仿真。产出可复现模型、任务结果、物理一致性评估和适用域报告；域外工况需经CFD复核。

## 工作流步骤（→workflow/→tasks）
- s01 数据接入与契约核验
- s02 预处理与数据切分
- s03 模型配置与训练
- s04 神经数值耦合求解
- s05 任务验收与适用域判定

## 关联论文
- MetaOpenFOAM_ an LLM-based multi-agent framework for CFD | doi:
- ALL-FEM_ Agentic Large Language Models fine-tuned for finite element methods | doi:
- MetaOpenFOAM 2.0_ Large Language Model Driven Chain of Thought for Automating CFD Simulation and Post-Processing | doi:
- Fine-tuning a Large Language Model for Automating Computational Fluid Dynamics Simulations | doi:
- OpenFOAMGPT_ a RAG-Augmented LLM Agent for OpenFOAM-Based Computational Fluid Dynamics | doi:

## 验收与缺失信息策略
- acceptance_decision: （源场景未提供）
- missing_information_policy: （源场景未提供）
