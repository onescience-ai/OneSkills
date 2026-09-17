# 预处理与数据切分

## 适用范围

本卡片描述硬约束PINN复杂几何边界求解工作流的第二步：预处理与数据切分。适用于：
- 复杂几何边界数据的统一物理量与表示
- 按几何、工况或时间构造无泄漏切分
- 保存统计量与可逆变换

**不适用场景**：
- 完整流场数据的正问题求解
- 无物理约束的数据处理

## 输入

1. **切分配置** `{SPLIT_CONFIG}`：按对象工况切分
2. **目标变量** `{TARGET_FIELDS}`：待预测物理量
3. **是否无量纲化** `{NONDIMENSIONALIZE}`：统一跨工况量纲

## 输出

1. **训练集清单** `train_manifest.json`：训练集样本信息
2. **验证集清单** `validation_manifest.json`：验证集样本信息
3. **测试集清单** `test_manifest.json`：测试集样本信息
4. **归一化参数** `normalization.json`：归一化统计量

## 流程节点

```
依据s01契约完成质控 → 重采样或图构建 → 掩膜 → 归一化或无量纲化 → 按{SPLIT_CONFIG}以几何、完整轨迹或物理工况为单位切分 → 保存统计量与可逆变换
```

### 详细操作

#### 1. 数据质控

**操作**：
- 检查数据完整性
- 识别并处理异常值
- 确保数据一致性

**判定标准**：
- 数据完整性通过
- 异常值处理完成
- 数据一致性保证

#### 2. 重采样或图构建

**操作**：
- 对不规则数据进行重采样
- 构建图结构数据（如需要）
- 确保数据格式统一

**判定标准**：
- 重采样后数据分布合理
- 图结构正确构建
- 数据格式统一

#### 3. 掩膜

**操作**：
- 创建有效数据掩膜
- 处理缺失值
- 确保掩膜语义正确

**判定标准**：
- 掩膜覆盖所有有效数据
- 缺失值处理完成
- 掩膜语义未破坏

#### 4. 归一化或无量纲化

**操作**：
- 计算训练集统计量
- 应用归一化或无量纲化
- 保存变换参数

**判定标准**：
- 仅用训练集计算统计量
- 变换可逆
- 统计量保存完整

#### 5. 数据切分

**操作**：
- 按几何、完整轨迹或物理工况为单位切分
- 不得把同一轨迹的帧随机打散
- 为{TARGET_FIELDS}保存统计量与可逆变换

**判定标准**：
- 三份切分的对象轨迹互斥
- 切分比例符合配置
- 统计量仅从训练集计算

## 关键参数

### 通用判据

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 三份切分互斥 | 必须通过 | [场景需求书s02] | 训练、验证、测试集对象轨迹互斥 |
| 统计量仅训练集 | 必须通过 | [场景需求书s02] | 仅用训练集计算变换统计量 |
| 边界掩膜语义 | 必须通过 | [场景需求书s02] | 边界与掩膜语义未破坏 |

### 校准数值

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 训练集比例 | 0.7 | [场景需求书s02] | 默认训练集比例 |
| 验证集比例 | 0.15 | [场景需求书s02] | 默认验证集比例 |
| 测试集比例 | 0.15 | [场景需求书s02] | 默认测试集比例 |
| 随机种子 | 42 | [场景需求书s02] | 可复现性种子 |

以下数值来自CFD_S040场景，供量级校准；其他体系需以自身证据重新锚定。

## 边界与分流

1. **切分导致数据泄漏** → 重新切分，确保对象轨迹互斥
2. **统计量计算错误** → 重新计算，确保仅使用训练集
3. **掩膜语义破坏** → 重新创建掩膜，确保语义正确
4. **归一化不可逆** → 检查归一化方法，确保可逆性

## 质量检查

1. **切分正确性**：训练、验证、测试集互斥
2. **统计量正确性**：仅用训练集计算统计量
3. **掩膜正确性**：掩膜语义正确
4. **归一化正确性**：归一化可逆，统计量保存完整
5. **可复现性**：相同随机种子下结果可复现

## 回退策略

1. **数据切分失败** → 调整切分配置或方法
2. **归一化失败** → 尝试其他归一化方法
3. **掩膜创建失败** → 检查数据格式和完整性
4. **统计量计算失败** → 检查数据质量和格式

## 资源召回建议

**何时召回本卡片**：
- 需要执行硬约束PINN复杂几何边界求解的预处理阶段
- 需要验证复杂几何边界数据的切分正确性
- 需要生成归一化参数

**配套资源**：
- 场景卡：cfd-hard-constraint-pinn-complex-geometry-solution
- 工作流卡：cfd-hard-constraint-pinn-complex-geometry-workflow
- 任务卡：cfd-hard-constraint-pinn-data-intake-contract-validation
- 任务卡：cfd-hard-constraint-pinn-model-training
- 任务卡：cfd-hard-constraint-pinn-equation-solving-residual-recovery
- 任务卡：cfd-hard-constraint-pinn-acceptance-applicability

## 证据来源

[1] Nonparametric Boundary Geometry in Physics Informed Deep Learning, 2020
[2] Solving Differential Equations with Constrained Learning, 2020
[3] Hybrid Boundary Physics-Informed Neural Networks for Solving Navier–Stokes Equations with Complex Boundary Conditions, 2025, URL: https://arxiv.org/abs/2507.17535
[4] SPINN: Separable Physics-Informed Neural Networks, 2021
[5] A Unified Hard-Constraint Framework for Solving Geometrically Complex PDEs, 2023
[6] Error analysis for physics informed neural networks (PINNs) approximating Kolmogorov PDEs, 2021, URL: https://arxiv.org/abs/2106.14473
[7] 场景需求书CFD_S040：硬约束PINN复杂几何边界求解，s02步骤定义