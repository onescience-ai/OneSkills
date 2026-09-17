# 可微分物理求解与方程结构学习

## 适用范围

本场景面向可微数值轨迹与算子数据，完成可微分物理求解与方程结构学习任务。适用于需要同时实现物理场预测和控制方程自动发现的CFD研究场景，包括但不限于流体动力学、热传导、对流扩散等偏微分方程描述的物理过程。不适用于：纯数据驱动无物理约束的黑箱预测、无需方程发现的单纯物理场重构、或强非连续介质（如多相流剧烈破碎）等传统CFD方法更具优势的场景。

## 输入

### 数据要求
- **可微数值轨迹数据**：时间序列形式的物理场快照（如速度场、压力场、温度场），支持自动微分计算
- **算子数据**：空间/时间微分算子的离散化表示，或可用于构造算子的网格信息
- **网格信息**：结构化或非结构化网格的坐标、拓扑、边界标识

### 模型与工具
- **核心模型**：Differentiable simulator（可微分模拟器）、Mechanistic PDE network（机理PDE网络）
- **HPC工具**：OpenFOAM（用于域外工况的CFD复核验证）

### 数据契约
- 输入变量单位需统一或可转换
- 网格坐标系定义明确
- 时间步长或工况参数范围清晰

## 输出

### 产物清单
1. **可复现模型**：训练好的神经网络权重与配置
2. **任务结果**：预测的物理场、识别的方程结构
3. **物理一致性评估**：残差分布、守恒误差、边界满足度
4. **适用域报告**：模型有效工况范围、域外行为警告

### 验证标准
- 统计误差（相对L2误差）≤10%
- 物理约束满足度（守恒误差、方程残差）可接受
- 最差样本误差可追溯
- 适用域边界明确

## 流程节点

```
数据接入与契约核验(s01)
    ↓
预处理与数据切分(s02)
    ↓
模型配置与训练(s03)
    ↓
神经数值耦合求解(s04)
    ↓
任务验收与适用域判定(s05)
```

### 各节点概要

| 节点 | 名称 | 核心任务 | 关键输出 |
|------|------|----------|----------|
| s01 | 数据接入与契约核验 | 数据可读性、变量、单位、网格核验 | dataset_manifest.json, data_contract.json |
| s02 | 预处理与数据切分 | 物理量统一、无量纲化、无泄漏切分 | train/validation/test manifests, normalization.json |
| s03 | 模型配置与训练 | Differentiable simulator或Mechanistic PDE network训练 | best_checkpoint.pt, training_metrics.csv |
| s04 | 神经数值耦合求解 | 神经网络嵌入数值求解器执行收敛 | coupled_solution/, residual_history.csv |
| s05 | 任务验收与适用域判定 | 统计误差、物理约束、泛化能力评估 | evaluation.json, applicability_report.md |

## 关键参数

### 模型参数
| 参数 | 默认值 | 说明 |
|------|--------|------|
| 模型类型 | Differentiable simulator / Mechanistic PDE network | 根据任务选择 |
| 框架 | PyTorch | 训练框架 |
| 学习率 | 0.001 | 优化器初始学习率 |
| 批大小 | 8 | 训练批大小 |
| 早停耐心 | 15 | 验证集无改善的最大轮数 |

### 训练参数
| 参数 | 默认值 | 说明 |
|------|--------|------|
| epochs | 100 | 最大训练轮数 |
| 随机种子 | 42 | 可复现性 |
| 切分比例 | 0.7/0.15/0.15 | train/validation/test |

### 验收参数
| 参数 | 默认值 | 说明 |
|------|--------|------|
| 相对误差门限 | 0.1 | 测试集放行阈值 |
| 验收指标 | solver_residual, relative_L2, speedup, conservation_error | 综合评估 |

## 边界与分流

### 场景边界
- **适用**：连续介质CFD问题、可获取可微轨迹数据、需要方程发现
- **不适用**：强间断问题（激波捕捉）、多尺度耦合严重、纯工程应用无需可解释性

### 异常处理
| 情况 | 处理 |
|------|------|
| 训练发散 | 停止并输出最后稳定状态，报告发散原因 |
| 残差不收敛 | 降低学习率或调整网络结构重试 |
| 域外工况预测 | 标记为不可信，建议CFD复核 |

### 降级策略
- 若Differentiable simulator失败，可尝试Mechanistic PDE network
- 若方程发现困难，可退化为纯物理场预测模式

## 质量检查

### 数据质量
- [ ] 数据文件可读且样本可追溯
- [ ] 输入目标变量单位坐标定义完整
- [ ] 不存在训练测试泄漏

### 训练质量
- [ ] 训练验证损失均为有限值
- [ ] 最佳权重可重新加载
- [ ] 配置环境随机种子可复现

### 求解质量
- [ ] 耦合接口变量单位一致
- [ ] 残差达到数值收敛门限
- [ ] 相对原求解器误差和加速比均报告

### 验收质量
- [ ] 统计与物理指标同时报告
- [ ] 最差样本可追溯
- [ ] 结论含适用域限制与复核建议

## 回退策略

| 失败点 | 替代方案 |
|--------|----------|
| 数据不可用 | 停止并返回BLOCKED |
| 模型训练失败 | 尝试替代模型或简化任务 |
| 耦合求解发散 | 回退到纯数据驱动预测 |
| 验收不通过 | 调整模型或数据，重新迭代 |

## 资源召回建议

### 触发条件
- 用户需要从轨迹数据学习物理规律
- 用户需要同时预测物理场和发现控制方程
- 用户需要可解释的物理模型而非纯黑箱

### 配套资源
- **数据标准器**：onescience-data-standardizer（数据格式统一）
- **训练技能**：onescience-trainer（训练流程）
- **推理技能**：onescience-infer（推理执行）
- **运行技能**：onescience-runtime（HPC调度）

## 证据来源

[1] Mechanistic PDE Networks for Discovery of Governing Equations
[2] Hamiltonian Neural PDE Solvers through Functional Approximation, arXiv:2505.13275
[3] PhysPDE_ Rethinking PDE Discovery and a Physical Hypothesis Selection Benchmark
[4] Neural Stochastic Flows_ Solver-Free Modelling and Inference for SDE Solutions, arXiv:2510.25769
[5] Accelerating PDE Data Generation via Differential Operator Action in Solution Space
[6] Stochastic Taylor Derivative Estimator_ Efficient Amortization for Arbitrary Differential Operators
[7] ΦFlow_ Differentiable Simulations for PyTorch, TensorFlow and Jax
