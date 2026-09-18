# CFD数据无泄漏分组切分规范

## 适用范围

面向CFD数据驱动建模的数据预处理任务，定义无泄漏分组切分的规范。适用于所有需要将CFD仿真数据切分为训练集、验证集和测试集的场景，特别是当数据具有分组结构（同一几何体的多个时间步、同一工况的多次采样）时。核心原则：同一分组（geometry_id/operating_condition）的所有样本必须完整出现在且仅出现在一个切分中，防止数据泄漏。

## 输入

- 任务目标：将CFD数据集切分为互斥的训练集、验证集和测试集
- 数据需求：带分组键的CFD数据（geometry_id, operating_condition等）、切分比例配置
- 格式要求：Pandas DataFrame或NumPy数组，分组键列为字符串类型

## 输出

- train_manifest.json：训练集清单，包含样本路径和分组信息
- val_manifest.json：验证集清单
- test_manifest.json：测试集清单
- normalization.json：归一化参数（仅从训练集计算）
- 切分报告：三份切分的分组轨迹互斥验证结果

## 流程节点

1. **分组键类型校验** → 2. **分组策略选择** → 3. **执行分组切分** → 4. **互斥性验证** → 5. **生成切分清单**

### 步骤1：分组键类型校验
- 操作：检查分组键字段的数据类型，确保为字符串类型
- 参数：分组键列名、期望类型（str）
- 工具：Pandas dtype检查
- 质量门禁：分组键为str类型，无NaN，无空字符串

### 步骤2：分组策略选择
- 操作：根据数据特性选择合适的分组切分策略
- 参数：数据结构（时间序列/空间分布/参数扫描）、分组键类型
- 工具：策略选择器
- 质量门禁：策略与数据特性匹配

### 步骤3：执行分组切分
- 操作：使用GroupKFold或LeaveOneGroupOut执行分组切分
- 参数：切分比例（如60/20/20）、随机种子、分组键
- 工具：sklearn.model_selection.GroupKFold/LeaveOneGroupOut
- 质量门禁：切分完成，无异常

### 步骤4：互斥性验证
- 操作：验证三份切分的分组轨迹互斥
- 参数：三份切分的分组键集合
- 工具：集合交集检查
- 质量门禁：任意两份切分的分组键交集为空

### 步骤5：生成切分清单
- 操作：输出切分结果清单和验证报告
- 参数：切分结果、验证状态
- 工具：清单生成器
- 质量门禁：清单文件完整，验证通过

## 关键参数

### 通用判据（方法层）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 分组键类型 | str（必须） | [D1][D2] | 所有分组键必须为字符串类型 |
| 类型转换方式 | str()显式转换 | [用户案例] | 数据加载后立即转换 |
| 分组策略-几何分组 | GroupKFold | [D1] | 不同几何体作为分组 |
| 分组策略-工况分组 | StratifiedGroupKFold | [D1] | 工况+标签分层 |
| 分组策略-时间序列 | TimeSeriesSplit | [D1] | 按时间索引切分 |
| 互斥性验证 | 任意两组交集=空集 | [D1] | 切分后必须验证 |
| 预处理拟合范围 | 仅训练集 | [D1] | 归一化等预处理只在训练集上拟合 |

### 校准数值（体系专属值）

以下数值来自典型CFD数据切分任务，供量级校准；其他体系需以自身证据重新锚定：

| 参数 | 典型值 | 来源 | 说明 |
|------|--------|------|------|
| 训练集比例 | 60% | [典型值] | 根据数据量调整 |
| 验证集比例 | 20% | [典型值] | 用于超参调优 |
| 测试集比例 | 20% | [典型值] | 最终评估用 |
| 最少分组数 | ≥3组 | [典型值] | 每组至少有足够样本 |
| 随机种子 | 固定值 | [典型值] | 可复现性 |

## 边界与分流

### 前提1：分组键字段存在且非空
- **不成立时转向**：使用随机切分（非分组），但在报告中标注"无分组键，可能存在数据泄漏风险"

### 前提2：分组键类型正确（str）
- **不成立时转向**：在切分入口处增加类型断言，自动调用str()转换，转换失败时报错

### 前提3：每个分组有足够样本
- **不成立时转向**：合并小样本分组，或使用LeavePGroupsOut留出多个小分组

### 前提4：时间序列数据按时间索引切分
- **不成立时转向**：使用TimeSeriesSplit而非GroupKFold，确保不使用未来数据训练

## 质量检查

1. **类型校验**：分组键为str类型，无NaN
2. **互斥性验证**：三份切分的分组键交集为空
3. **完整性验证**：所有样本都被分配到某一切分
4. **比例验证**：各切分比例符合配置
5. **预处理隔离**：归一化参数仅从训练集计算

## 回退策略

1. **分组键类型错误**：自动调用str()转换，记录转换日志
2. **切分互斥性失败**：重新执行切分，调整随机种子
3. **样本不足**：合并小分组或使用数据增强
4. **时间序列泄露**：改用TimeSeriesSplit严格按时间切分

## 资源召回建议

- **何时召回本卡片**：当CFD任务需要将数据切分为训练/验证/测试集，且数据具有分组结构时
- **配套资源**：
  - cfd-data-normalization-manifest：数据归一化规范
  - general-data-contract-specification：数据契约规范
  - cfd-data-driven-model-data-availability-check：数据可用性检查

## 证据来源

[1] report.json中CFD_S080任务归因：preprocessing.py中identify_grouping_key返回的group_key类型未校验，与数据混合操作时产生tuple类型错误。
[2] scikit-learn官方文档：GroupKFold确保同一分组不会出现在训练集和测试集中，https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.GroupKFold.html
[3] scikit-learn官方文档：Cross-validation评估估计器性能，分组数据切分最佳实践，https://scikit-learn.org/stable/modules/cross_validation.html
[4] Guan Y, et al. "Learning physics-constrained SGS closures in small-data regime", arXiv:2201.07347, 2022. — CFD+ML中数据切分防止泄漏的实践。
[5] Toma C, et al. "Mixed data-source transfer learning for turbulence model augmented PINN", arXiv:2601.04921, 2026. — 迁移学习中数据划分策略。
