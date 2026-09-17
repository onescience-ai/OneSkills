# 数据接入与契约核验

## 适用范围

本卡片描述硬约束PINN复杂几何边界求解工作流的第一步：数据接入与契约核验。适用于：
- 复杂几何边界数据的接入与验证
- 无网格配点数据的核验
- 物理信息网络训练前的数据审计

**不适用场景**：
- 完整流场数据的正问题求解
- 无物理约束的数据处理

## 输入

1. **数据集路径** `{DATASET_PATH}`：目录或清单文件
2. **数据集名称** `{DATASET_NAME}`：来源与数据版本
3. **数据契约** `{DATA_CONTRACT}`：变量单位网格定义

## 输出

1. **数据清单** `dataset_manifest.json`：样本数、变量、单位、坐标等信息
2. **数据契约** `data_contract.json`：机器可读的契约文件
3. **审计报告** `data_audit.md`：数据质量审计结果

## 流程节点

```
读取数据集 → 检查文件可读性 → 核验样本数 → 验证输入目标变量 → 检查单位坐标系 → 确认网格拓扑 → 检查时间工况范围 → 识别缺失值 → 确认使用许可 → 输出契约
```

### 详细操作

#### 1. 数据读取与可读性检查

**操作**：
- 读取`{DATASET_PATH}`中的`{DATASET_NAME}`
- 验证文件格式（支持常见格式：CSV、HDF5、NetCDF、NPY等）
- 检查文件完整性（无损坏、无截断）

**判定标准**：
- 文件可正常读取
- 数据类型符合预期
- 无异常值或缺失标记

#### 2. 样本与变量核验

**操作**：
- 统计样本数量
- 识别输入变量（如几何边界坐标、配点位置）
- 识别目标变量（如速度场、压力场）
- 验证变量名称与数据契约一致

**判定标准**：
- 样本数可追溯
- 变量名称完整
- 输入/目标变量定义明确

#### 3. 单位与坐标系检查

**操作**：
- 验证变量单位（SI单位制或一致的单位系统）
- 确认坐标系定义（笛卡尔、柱坐标等）
- 检查空间/时间维度的一致性

**判定标准**：
- 单位定义完整
- 坐标系明确
- 维度信息一致

#### 4. 网格拓扑与时间范围

**操作**：
- 检查网格类型（结构化/非结构化）
- 验证网格分辨率
- 确认时间或工况范围
- 识别边界条件信息

**判定标准**：
- 网格信息完整
- 时间/工况范围明确
- 边界条件可识别

#### 5. 缺失值与使用许可

**操作**：
- 识别缺失值比例与分布
- 检查数据使用许可
- 记录数据来源与版本

**判定标准**：
- 缺失值可接受（<5%或已处理）
- 使用许可明确
- 数据可追溯

## 关键参数

### 通用判据

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 数据文件可读性 | 必须通过 | [场景需求书s01] | 文件格式正确、无损坏 |
| 样本可追溯性 | 必须通过 | [场景需求书s01] | 样本数量与来源明确 |
| 变量单位完整性 | 必须通过 | [场景需求书s01] | 单位定义完整 |
| 坐标系定义 | 必须通过 | [场景需求书s01] | 坐标系明确 |
| 网格拓扑 | 必须通过 | [场景需求书s01] | 网格类型与分辨率明确 |
| 训练测试泄漏 | 不允许 | [场景需求书s01] | 无数据泄漏 |

### 校准数值

以下数值来自CFD_S040场景，供量级校准；其他体系需以自身证据重新锚定。

## 边界与分流

1. **文件不可读**：格式不支持或文件损坏 → 返回BLOCKED，列出缺项
2. **变量缺失**：必需变量未定义 → 返回BLOCKED，列出缺项
3. **单位不一致**：变量单位冲突 → 要求统一单位后重新接入
4. **坐标系不明**：坐标系未定义 → 要求补充坐标信息
5. **数据泄漏**：训练测试存在重叠 → 重新切分或标记泄漏样本

## 质量检查

1. **完整性**：所有必需字段均有定义
2. **一致性**：变量名称、单位、坐标系一致
3. **可追溯性**：样本来源、版本可追溯
4. **无泄漏**：训练测试无重叠
5. **可读性**：输出文件格式正确、可被后续步骤读取

## 回退策略

1. **数据格式不支持** → 转换为支持格式（CSV、HDF5等）
2. **变量缺失** → 要求数据提供方补充或使用替代变量
3. **单位不一致** → 统一转换为SI单位制
4. **坐标系不明** → 使用默认笛卡尔坐标系并标注

## 资源召回建议

**何时召回本卡片**：
- 需要执行硬约束PINN复杂几何边界求解的数据准备阶段
- 需要验证复杂几何边界数据的完整性
- 需要生成数据契约文件

**配套资源**：
- 场景卡：cfd-hard-constraint-pinn-complex-geometry-solution
- 工作流卡：cfd-hard-constraint-pinn-complex-geometry-workflow
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
[7] 场景需求书CFD_S040：硬约束PINN复杂几何边界求解，s01步骤定义