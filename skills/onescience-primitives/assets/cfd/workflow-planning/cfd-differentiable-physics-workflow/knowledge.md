# 可微分物理求解与方程结构学习工作流

## 适用范围

本工作流为可微分物理求解与方程结构学习提供标准化执行路径，覆盖从原始数据接入到适用域判定的完整生命周期。适用于需要从可微数值轨迹数据中同时学习物理场预测能力和自动发现控制方程的CFD任务。工作流设计为模块化，支持Differentiable simulator和Mechanistic PDE network两类主流模型。

## 输入

### 必需输入
- **数据集路径** (`{DATASET_PATH}`)：包含可微数值轨迹与算子数据的目录或清单文件
- **数据集名称** (`{DATASET_NAME}`)：标识数据来源与版本，默认"可微数值轨迹与算子数据"

### 可选输入
- **数据契约** (`{DATA_CONTRACT}`)：变量、单位、网格定义的JSON结构
- **切分配置** (`{SPLIT_CONFIG}`)：train/validation/test比例及切分策略
- **目标变量** (`{TARGET_FIELDS}`)：待预测的物理量列表
- **初始权重** (`{INIT_CHECKPOINT}`)：可选的预训练模型权重

## 输出

### 产物清单
| 步骤 | 主要产物 | 辅助产物 |
|------|----------|----------|
| s01 数据接入 | dataset_manifest.json, data_contract.json | data_audit.md |
| s02 预处理 | train/validation/test manifests | normalization.json |
| s03 模型训练 | best_checkpoint.pt | train_config.json, training_metrics.csv, environment.txt |
| s04 耦合求解 | coupled_solution/ | residual_history.csv, solver_timing.json |
| s05 验收评估 | evaluation.json, PASS_REJECT_BLOCKED.txt | worst_cases.csv, applicability_report.md |

## 流程节点

```
┌─────────────────────────────────────────────────────────────────────┐
│  s01 数据接入与契约核验                                              │
│  └─ 检查文件可读性、样本数、变量、单位、坐标、网格、许可              │
└─────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────┐
│  s02 预处理与数据切分                                                │
│  └─ 统一物理量、无量纲化、按几何/轨迹/工况无泄漏切分                 │
└─────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────┐
│  s03 模型配置与训练                                                  │
│  └─ Differentiable simulator / Mechananistic PDE network 训练      │
└─────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────┐
│  s04 神经数值耦合求解                                                │
│  └─ 网络嵌入数值求解器，端到端迭代至收敛                            │
└─────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────┐
│  s05 任务验收与适用域判定                                            │
│  └─ 统计误差、物理约束、泛化能力、计算收益综合评估                  │
└─────────────────────────────────────────────────────────────────────┘
```

## 关键参数

### 步骤依赖关系
| 步骤 | 前置步骤 | 说明 |
|------|----------|------|
| s01 | 无 | 入口步骤 |
| s02 | s01 | 依赖s01的数据契约 |
| s03 | s02 | 依赖s02的切分结果 |
| s04 | s03 | 依赖s03的模型权重 |
| s05 | s04 | 依赖s04的求解结果 |

### 默认配置
| 参数 | 值 | 适用步骤 |
|------|-----|----------|
| train比例 | 0.7 | s02 |
| validation比例 | 0.15 | s02 |
| test比例 | 0.15 | s02 |
| 随机种子 | 42 | s02, s03 |
| 学习率 | 0.001 | s03 |
| 批大小 | 8 | s03, s04 |
| 最大轮数 | 100 | s03 |
| 早停耐心 | 15 | s03 |
| 相对误差门限 | 0.1 | s05 |

## 边界与分流

### 正常流
s01 → s02 → s03 → s04 → s05 → 通过验收

### 异常分支
| 条件 | 转向 | 恢复路径 |
|------|------|----------|
| s01 数据不可读或缺必填项 | BLOCKED | 修复数据后重新s01 |
| s02 切分失败 | BLOCKED | 检查切分配置 |
| s03 训练发散 | 停止当前训练 | 调整超参后重新s03 |
| s04 求解发散 | 输出最后稳定状态 | 检查模型或降低步长 |
| s05 验收不通过 | REJECT | 分析失败原因，返回s03调整 |

### 降级策略
- 若方程发现任务困难，可退化为纯物理场预测
- 若神经网络嵌入失败，可回退到传统CFD求解

## 质量检查

### 数据质量门禁 (s01)
- [ ] 数据文件可读且样本可追溯
- [ ] 输入目标变量单位坐标定义完整
- [ ] 不存在训练测试泄漏

### 切分质量门禁 (s02)
- [ ] 三份切分的对象轨迹互斥
- [ ] 仅用训练集计算变换统计量
- [ ] 边界与掩膜语义未破坏

### 训练质量门禁 (s03)
- [ ] 训练验证损失均为有限值
- [ ] 最佳权重可重新加载
- [ ] 配置环境随机种子可复现

### 求解质量门禁 (s04)
- [ ] 耦合接口变量单位一致
- [ ] 残差达到数值收敛门限
- [ ] 相对原求解器误差和加速比均报告

### 验收质量门禁 (s05)
- [ ] 统计与物理指标同时报告
- [ ] 最差样本可追溯
- [ ] 结论含适用域限制与复核建议

## 回退策略

| 失败阶段 | 回退方案 |
|----------|----------|
| s01数据问题 | 停止，报告缺项 |
| s02切分问题 | 检查配置，必要时人工审查 |
| s03训练问题 | 超参搜索或模型切换 |
| s04求解问题 | 简化模型或降低精度要求 |
| s05验收问题 | 分析瓶颈，定向优化 |

## 资源召回建议

### 触发词
- 可微分物理求解
- PDE方程发现
- 物理信息神经网络
- Differentiable simulator
- Mechanistic PDE network
- 神经数值耦合

### 配套技能
- `onescience-data-standardizer`：数据格式标准化
- `onescience-trainer`：模型训练流程
- `onescience-infer`：推理执行
- `onescience-runtime`：HPC运行调度
- `onescience-coder`：代码生成

## 证据来源

[1] Mechanistic PDE Networks for Discovery of Governing Equations
[2] Hamiltonian Neural PDE Solvers through Functional Approximation, arXiv:2505.13275
[3] PhysPDE_ Rethinking PDE Discovery and a Physical Hypothesis Selection Benchmark
[4] Neural Stochastic Flows_ Solver-Free Modelling and Inference for SDE Solutions, arXiv:2510.25769
[5] Accelerating PDE Data Generation via Differential Operator Action in Solution Space
[6] Stochastic Taylor Derivative Estimator_ Efficient Amortization for Arbitrary Differential Operators
[7] ΦFlow_ Differentiable Simulations for PyTorch, TensorFlow and Jax
