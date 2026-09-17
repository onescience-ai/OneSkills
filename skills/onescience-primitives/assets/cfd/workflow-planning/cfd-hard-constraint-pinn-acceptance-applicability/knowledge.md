# 任务验收与适用域判定

## 适用范围

本卡片描述硬约束PINN复杂几何边界求解工作流的第五步：任务验收与适用域判定。适用于：
- 评估统计误差、关键物理约束、泛化能力和计算收益
- 使用验收指标给出PASS、REJECT或BLOCKED
- 执行几何或工况外推测试并明确适用域

**不适用场景**：
- 完整流场数据的正问题求解
- 无物理约束的数据处理

## 输入

1. **验收指标** `{METRICS}`：统计和物理指标
2. **相对误差门限** `{MAX_RELATIVE_L2}`：测试集放行阈值
3. **是否外推测试** `{RUN_OOD_TEST}`：测试域外工况

## 输出

1. **评估结果** `evaluation.json`：逐变量误差、边界误差、守恒或方程残差
2. **最差案例** `worst_cases.csv`：最差样本信息
3. **适用域报告** `applicability_report.md`：模型适用范围与复核建议
4. **验收结论** `PASS_REJECT_BLOCKED.txt`：PASS、REJECT或BLOCKED

## 流程节点

```
加载s04结果 → 按{METRICS}评价 → 报告逐变量误差 → 报告边界误差 → 报告守恒或方程残差 → 识别最差样本 → 计算推理成本 → 使用{MAX_RELATIVE_L2}及任务物理门限判定 → 若{RUN_OOD_TEST}为true执行外推测试 → 明确适用域 → 输出验收结论
```

### 详细操作

#### 1. 结果加载

**操作**：
- 加载s04解场与残差场
- 验证结果完整性
- 准备评估数据

**判定标准**：
- 结果加载成功
- 结果完整性通过
- 评估数据准备完成

#### 2. 统计误差评估

**操作**：
- 计算逐变量误差（如相对L2误差）
- 识别最差样本
- 计算推理成本

**判定标准**：
- 误差计算正确
- 最差样本可追溯
- 推理成本可量化

#### 3. 物理约束评估

**操作**：
- 评估边界误差
- 评估守恒误差（如质量守恒、动量守恒）
- 评估方程残差

**判定标准**：
- 边界误差在可接受范围
- 守恒误差在可接受范围
- 方程残差收敛

#### 4. 验收判定

**操作**：
- 使用{MAX_RELATIVE_L2}及任务物理门限判定
- 给出PASS、REJECT或BLOCKED结论
- 记录判定依据

**判定标准**：
- 判定依据充分
- 结论明确
- 依据可追溯

#### 5. 适用域判定

**操作**：
- 若{RUN_OOD_TEST}为true，执行几何或工况外推测试
- 分析模型泛化能力
- 明确适用域限制
- 提出复核建议

**判定标准**：
- 外推测试完成
- 适用域明确
- 复核建议可行

## 关键参数

### 通用判据

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 统计与物理指标 | 同时报告 | [场景需求书s05] | 统计与物理指标同时报告 |
| 最差样本可追溯 | 必须通过 | [场景需求书s05] | 最差样本可追溯 |
| 适用域限制 | 必须包含 | [场景需求书s05] | 结论含适用域限制与复核建议 |

### 校准数值

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 验收指标 | relative_L2, PDE_residual, boundary_error, conservation_error | [场景需求书s05] | 默认验收指标 |
| 相对误差门限 | 0.1 | [场景需求书s05] | 默认相对误差门限 |
| 是否外推测试 | true | [场景需求书s05] | 默认执行外推测试 |

以下数值来自CFD_S040场景，供量级校准；其他体系需以自身证据重新锚定。

## 边界与分流

1. **误差超标** → REJECT，分析原因，调整模型或数据
2. **物理约束违反** → REJECT，检查物理模型，调整损失权重
3. **泛化能力不足** → BLOCKED，明确适用域限制，建议CFD复核
4. **计算成本过高** → 评估成本效益，考虑降阶模型
5. **评估指标不达标** → 根据最差案例分析原因，调整模型或数据

## 质量检查

1. **评估全面性**：统计与物理指标同时报告
2. **最差样本可追溯**：最差样本信息完整
3. **适用域明确**：适用域限制明确
4. **复核建议可行**：复核建议具体可行
5. **结论明确**：PASS、REJECT或BLOCKED结论明确

## 回退策略

1. **评估失败** → 检查输入数据、评估指标
2. **适用域判定失败** → 增加外推测试，分析泛化能力
3. **复核建议不可行** → 调整建议，确保可行性
4. **结论不明确** → 重新评估，明确判定依据

## 资源召回建议

**何时召回本卡片**：
- 需要执行硬约束PINN复杂几何边界求解的任务验收阶段
- 需要评估PINN模型的统计和物理误差
- 需要判定模型的适用域和复核建议

**配套资源**：
- 场景卡：cfd-hard-constraint-pinn-complex-geometry-solution
- 工作流卡：cfd-hard-constraint-pinn-complex-geometry-workflow
- 任务卡：cfd-hard-constraint-pinn-data-intake-contract-validation
- 任务卡：cfd-hard-constraint-pinn-preprocessing-data-splitting
- 任务卡：cfd-hard-constraint-pinn-model-training
- 任务卡：cfd-hard-constraint-pinn-equation-solving-residual-recovery

## 证据来源

[1] Nonparametric Boundary Geometry in Physics Informed Deep Learning, 2020
[2] Solving Differential Equations with Constrained Learning, 2020
[3] Hybrid Boundary Physics-Informed Neural Networks for Solving Navier–Stokes Equations with Complex Boundary Conditions, 2025, URL: https://arxiv.org/abs/2507.17535
[4] SPINN: Separable Physics-Informed Neural Networks, 2021
[5] A Unified Hard-Constraint Framework for Solving Geometrically Complex PDEs, 2023
[6] Error analysis for physics informed neural networks (PINNs) approximating Kolmogorov PDEs, 2021, URL: https://arxiv.org/abs/2106.14473
[7] 场景需求书CFD_S040：硬约束PINN复杂几何边界求解，s05步骤定义