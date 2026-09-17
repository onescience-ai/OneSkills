# 预处理与数据切分

## 适用范围

**触发条件**：
- 已完成数据接入与契约核验（s01）
- 需要为模型训练准备训练集、验证集、测试集

**适用场景**：
- Deep Ritz网络训练的数据准备
- 弱形式神经求解器训练的数据准备
- 任何变分PDE求解任务的预处理

**不适用场景**：
- 数据尚未通过s01核验
- 非变分形式的PDE数据

## 输入

- **SPLIT_CONFIG**（必需）：切分配置，含比例、随机种子、分组方式
- **TARGET_FIELDS**（必需）：目标变量列表
- **NONDIMENSIONALIZE**（可选）：是否无量纲化，默认true
- s01产出的dataset_manifest.json和data_contract.json

## 输出

- **train_manifest.json**：训练集清单
- **validation_manifest.json**：验证集清单
- **test_manifest.json**：测试集清单
- **normalization.json**：归一化/无量纲化统计量

## 流程节点

### 1. 质控与异常值处理
- 基于s01审计结果过滤异常样本
- 标记缺失值处理策略
- 记录质控前后样本数

### 2. 重采样或图构建
- 按需进行空间重采样
- 对非结构化数据构建图表示
- 保持物理量纲一致性

### 3. 归一化或无量纲化
- 仅用训练集计算统计量（均值、方差、最大最小值）
- 对所有数据集应用相同变换
- 保存变换参数供推理时逆变换

### 4. 无泄漏切分
- 按几何、完整轨迹或物理工况为单位切分
- 不得把同一轨迹的帧随机打散
- 确保三份切分的对象轨迹互斥

### 5. 统计量保存
- 保存各变量的均值、方差、范围
- 保存归一化参数
- 记录切分配置

## 关键参数

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| train比例 | 0.7 | [1] | 默认训练集比例 |
| validation比例 | 0.15 | [1] | 默认验证集比例 |
| test比例 | 0.15 | [1] | 默认测试集比例 |
| 随机种子 | 42 | [1] | 可复现性 |
| 分组方式 | geometry_or_trajectory | [1] | 按几何或轨迹分组 |
| 无量纲化 | true | [1] | 默认启用 |

## 边界与分流

- **样本数不足**：若切分后某集合样本过少（如<10），调整比例或报告警告
- **分组失败**：若无法按指定方式分组（如无轨迹信息），降级为随机切分并标记
- **统计量异常**：若某变量方差为0（常量），标记为"无信息变量"

## 质量检查

- [ ] 三份切分的对象轨迹互斥
- [ ] 仅用训练集计算变换统计量
- [ ] 边界与掩膜语义未破坏
- [ ] 归一化参数可逆

## 回退策略

- 切分比例不合理 → 自动调整并报告
- 统计量计算错误 → 重新计算并验证
- 信息泄漏 → 重新切分并检查分组逻辑

## 资源召回建议

本卡是Deep Ritz工作流的第二步。完成后进入模型配置与训练步骤（cfd-deep-ritz-model-training）。

## 证据来源

[1] "The Deep Ritz Method: A Deep Learning-Based Numerical Algorithm for Solving Variational Problems", E and Yu, 2017
[2] "Error Analysis of Deep Ritz Methods for Elliptic Equations", 2021
[3] "Characterizing possible failure modes in physics-informed neural networks", 2021
