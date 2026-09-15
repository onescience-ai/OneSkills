# 场景：CFD_S100

- domain: cfd
- type: paper_scenario
- 算力: ['NULL'] (is_one_hpc=[False])
- 模型: ['Implicit neural representation', 'Diffusion bridge']
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
面向稀疏或缺损CFD场与坐标查询完成隐式表示与扩散桥CFD缺失区补全压缩。产出可复现模型、任务结果、物理一致性评估和适用域报告；域外工况需经CFD复核。

## 工作流步骤（→workflow/→tasks）
- s01 数据接入与契约核验
- s02 预处理与数据切分
- s03 模型配置与训练
- s04 低分辨或部分观测流场重构
- s05 任务验收与适用域判定

## 关联论文
- PEINR_ A Physics-enhanced Implicit Neural Representation for High-Fidelity Flow Field Reconstruction | doi:
- Physics-aligned field reconstruction with diffusion bridge | doi:
- Inpainting Computational Fluid Dynamics with Deep Learning | doi:
- SCoReT_ Super-Resolution Compression and Reconstruction of Turbulent Flows | doi:

## 验收与缺失信息策略
- acceptance_decision: （源场景未提供）
- missing_information_policy: （源场景未提供）
