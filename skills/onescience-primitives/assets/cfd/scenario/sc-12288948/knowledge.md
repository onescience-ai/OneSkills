# 场景：CFD_S093

- domain: cfd
- type: paper_scenario
- 算力: ['NULL'] (is_one_hpc=[False])
- 模型: ['GAN', 'Normalizing flow']
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
面向湍流快照与低维潜变量数据完成GAN与正规化流湍流降阶生成。产出可复现模型、任务结果、物理一致性评估和适用域报告；域外工况需经CFD复核。

## 工作流步骤（→workflow/→tasks）
- s01 数据接入与契约核验
- s02 预处理与数据切分
- s03 模型配置与训练
- s04 条件采样与物理一致性筛选
- s05 任务验收与适用域判定

## 关联论文
- IG-GAN_ A Generative Adversarial Network for Aerodynamic Data Generation Based on Intrinsic Geometry | doi:
- Generative Adversarial Reduced Order Modeling | doi:
- MS^3D_ A RG Flow-Based Regularization for GAN Training with Limited Data | doi:
- Normalizing flow neural networks by JKO scheme | doi:
- Enforcing statistical constraints in generative adversarial networks for modeling chaotic dynamical systems | doi:

## 验收与缺失信息策略
- acceptance_decision: （源场景未提供）
- missing_information_policy: （源场景未提供）
