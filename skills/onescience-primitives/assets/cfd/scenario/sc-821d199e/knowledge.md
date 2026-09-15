# 场景：CFD_S074

- domain: cfd
- type: paper_scenario
- 算力: ['NULL'] (is_one_hpc=[False])
- 模型: ['Transformer aerodynamic surrogate', 'Neural turbulence model']
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
面向高超声速冷壁与跨声速机翼CFD数据完成高超声速与跨声速边界层湍流代理。产出可复现模型、任务结果、物理一致性评估和适用域报告；域外工况需经CFD复核。

## 工作流步骤（→workflow/→tasks）
- s01 数据接入与契约核验
- s02 预处理与数据切分
- s03 模型配置与训练
- s04 闭合项预测与后验CFD耦合
- s05 任务验收与适用域判定

## 关联论文
- Data-Driven Turbulence Modeling Approach for Cold-Wall Hypersonic Boundary Layers | doi:
- Gaussian processes at the Helm(holtz)_ A more fluid model for ocean currents | doi:
- Scalable Transformer for PDE Surrogate Modeling | doi:
- Aeroelastic Reduced-Order Model Differential Equations in Transonic Buffeting Flow | doi:
- Compact representation of transonic airfoil buffet flows with observable-augmented machine learning | doi:
- SuperWing_ a comprehensive transonic wing dataset for data-driven aerodynamic design | doi:
- Neural Differential Equations for Oscillatory Flows in Aeroelasticity Applied to Transonic Buffet | doi:
- SMART_ Scalable Mesh-free Aerodynamic Simulations from Raw Geometries using a Transformer-based Surrogate Model | doi:

## 验收与缺失信息策略
- acceptance_decision: （源场景未提供）
- missing_information_policy: （源场景未提供）
