# 场景：CFD_S016

- domain: cfd
- type: paper_scenario
- 算力: ['NULL'] (is_one_hpc=[False])
- 模型: ['Bayesian PINN', 'Physics-informed GAN']
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
面向稀疏观测与CFD先验联合数据完成物理信息概率网络流场不确定性反演。产出可复现模型、任务结果、物理一致性评估和适用域报告；域外工况需经CFD复核。

## 工作流步骤（→workflow/→tasks）
- s01 数据接入与契约核验
- s02 预处理与数据切分
- s03 模型配置与训练
- s04 概率推理与不确定性校准
- s05 任务验收与适用域判定

## 关联论文
- Flow Field Tomography with Uncertainty Quantification using a Bayesian Physics-Informed Neural Network | doi:
- Calibrated Physics-Informed Uncertainty Quantification | doi:
- PID-GAN_ A GAN Framework based on a Physics-informed Discriminator for Uncertainty Quantification with Physics | doi:
- Physics-constrained deep learning for high-dimensional surrogate modeling and uncertainty quantification without | doi:

## 验收与缺失信息策略
- acceptance_decision: （源场景未提供）
- missing_information_policy: （源场景未提供）
