# 场景：CFD_S055

- domain: cfd
- type: paper_scenario
- 算力: ['NULL'] (is_one_hpc=[False])
- 模型: ['Wavelet Neural Operator', 'Localized-kernel operator']
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
面向多尺度高频PDE场数据完成小波与局部谱核多尺度算子学习。产出可复现模型、任务结果、物理一致性评估和适用域报告；域外工况需经CFD复核。

## 工作流步骤（→workflow/→tasks）
- s01 数据接入与契约核验
- s02 预处理与数据切分
- s03 模型配置与训练
- s04 批量推理与物理恢复
- s05 任务验收与适用域判定

## 关联论文
- Multiwavelet-based Operator Learning for Differential Equations | doi:
- DRIFT-Net_ A Spectral-Coupled Neural Operator for PDEs Learning | doi:
- Neural Operators with Localized Integral and Differential Kernels | doi:
- Gaussian Plane-Wave Neural Operator for Electron Density Estimation | doi:
- Learning High-Frequency Functions Made Easy with Sinusoidal Positional Encoding | doi:
- Spectral-Embedded Operator Learning for Three-Phase Interfacial Flow_ A Ternary Cahn-Hilliard-Navier-Stokes Benchmark | doi:

## 验收与缺失信息策略
- acceptance_decision: （源场景未提供）
- missing_information_policy: （源场景未提供）
