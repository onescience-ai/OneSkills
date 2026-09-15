# 场景：CFD_S085

- domain: cfd
- type: paper_scenario
- 算力: ['OpenFOAM'] (is_one_hpc=[False])
- 模型: ['Deep reinforcement learning', 'Explainable CNN']
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
面向槽道DNS壁面观测与吹吸控制数据完成深度强化学习壁湍流摩阻削减。产出可复现模型、任务结果、物理一致性评估和适用域报告；域外工况需经CFD复核。

## 工作流步骤（→workflow/→tasks）
- s01 数据接入与契约核验
- s02 预处理与数据切分
- s03 模型配置与训练
- s04 闭环策略部署与滚动仿真
- s05 任务验收与适用域判定

## 关联论文
- Deep reinforcement learning for turbulent drag reduction in channel flows | doi:
- Identifying regions of importance in wall-bounded turbulence through explainable deep learning | doi:

## 验收与缺失信息策略
- acceptance_decision: （源场景未提供）
- missing_information_policy: （源场景未提供）
