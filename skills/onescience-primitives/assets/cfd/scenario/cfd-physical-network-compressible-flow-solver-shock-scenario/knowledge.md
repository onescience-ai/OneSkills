# 场景：CFD_S005

- domain: cfd
- type: paper_scenario
- 算力: ['NULL'] (is_one_hpc=[False])
- 模型: ['Physics-informed neural network', 'Shock classifier']
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
面向亚声速至超声速可压缩绕流数据完成物理网络可压缩高速绕流求解与激波识别。产出可复现模型、任务结果、物理一致性评估和适用域报告；域外工况需经CFD复核。

## 工作流步骤（→workflow/→tasks）
- s01 数据接入与契约核验
- s02 预处理与数据切分
- s03 模型配置与训练
- s04 批量推理与物理恢复
- s05 任务验收与适用域判定

## 关联论文
- Solving nonlinear subsonic compressible flow in infinite domain via multi-stage neural networks | doi:
- An unsupervised machine-learning-based shock sensor for high-order supersonic flow solvers | doi:
- Supervised machine learning of compressible flow past a rotating cylinder | doi:

## 验收与缺失信息策略
- acceptance_decision: （源场景未提供）
- missing_information_policy: （源场景未提供）
