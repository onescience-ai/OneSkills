# scATAC-seq训练测试划分任务

## 适用范围

**触发条件**：
- 需要评估模型的泛化能力
- 需要避免训练集和测试集的数据泄露
- 需要确保评估结果可靠

**适用场景**：
- 机器学习模型训练和评估
- 跨数据集验证
- 细胞类型注释性能评估
- 模型选择和超参数调优

**不适用场景**：
- 无监督分析（如聚类，无需划分）
- 全数据训练（如基础表征学习）
- 小样本数据（样本量不足以划分）

## 输入

- **完整数据集**：包含所有细胞的特征矩阵和标签
- **划分比例**：训练集/测试集比例（如80/20）
- **可选输入**：
  - 批次信息（用于按批次划分）
  - 供体信息（用于按供体划分）

## 输出

- **训练集**：用于模型训练的细胞子集
- **测试集**：用于模型评估的细胞子集
- **划分报告**：包含划分统计信息

## 流程节点

### Step 1：确定划分策略
- **操作**：根据任务需求选择划分方法
- **策略选项**：
  1. **随机划分**：按细胞比例随机划分（最简单）
  2. **按批次划分**：留一批次用于测试（评估跨批次泛化）
  3. **按供体划分**：留一供体用于测试（评估跨供体泛化）
  4. **分层划分**：保持各细胞类型比例一致
- **选择依据**：
  - 有批次信息 → 按批次划分
  - 有供体信息 → 按供体划分
  - 仅需基本评估 → 随机划分
- **质量门禁**：划分策略合理，符合任务目标

### Step 2：执行划分
- **操作**：将数据划分为训练集和测试集
- **实现**：
  ```python
  import numpy as np
  from sklearn.model_selection import train_test_split
  
  # 随机划分
  train_idx, test_idx = train_test_split(
      np.arange(n_cells),
      test_size=0.2,
      random_state=42,
      stratify=cell_types  # 保持细胞类型比例
  )
  
  # 按批次划分
  unique_batches = np.unique(batches)
  test_batch = unique_batches[-1]  # 留最后一批次
  test_idx = np.where(batches == test_batch)[0]
  train_idx = np.where(batches != test_batch)[0]
  ```
- **质量门禁**：训练集和测试集无重叠

### Step 3：验证划分
- **操作**：检查划分结果的正确性
- **检查项**：
  1. 训练集和测试集细胞索引无重叠
  2. 各集合大小符合预期比例
  3. 细胞类型分布合理（如使用分层划分）
  4. 无数据泄露（同一细胞不在两个集合中）
- **实现**：
  ```python
  # 验证无重叠
  assert len(set(train_idx) & set(test_idx)) == 0
  
  # 验证比例
  train_ratio = len(train_idx) / n_cells
  test_ratio = len(test_idx) / n_cells
  print(f"Train: {train_ratio:.2%}, Test: {test_ratio:.2%}")
  ```
- **质量门禁**：所有检查项通过

### Step 4：应用划分
- **操作**：从原始数据中提取训练集和测试集
- **实现**：
  ```python
  # 提取训练集
  X_train = X[train_idx]
  y_train = cell_types[train_idx]
  
  # 提取测试集
  X_test = X[test_idx]
  y_test = cell_types[test_idx]
  ```
- **质量门禁**：数据形状正确，标签一致

### Step 5：生成划分报告
- **操作**：记录划分统计信息
- **内容**：
  - 总细胞数、训练集大小、测试集大小
  - 各细胞类型在训练集和测试集中的分布
  - 划分策略说明
  - 随机种子（如适用）
- **实现**：
  ```python
  import pandas as pd
  
  # 统计各类型分布
  train_dist = pd.Series(y_train).value_counts()
  test_dist = pd.Series(y_test).value_counts()
  
  report = {
      'total_cells': n_cells,
      'train_size': len(train_idx),
      'test_size': len(test_idx),
      'train_distribution': train_dist.to_dict(),
      'test_distribution': test_dist.to_dict()
  }
  ```
- **质量门禁**：报告完整，信息准确

### Step 6：保存划分结果
- **操作**：将划分索引保存以供后续使用
- **格式**：JSON或numpy数组
- **内容**：
  - train_idx：训练集细胞索引
  - test_idx：测试集细胞索引
  - 划分参数（比例、随机种子等）
- **质量门禁**：文件可正常加载

## 关键参数

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 默认训练比例 | 0.8 | [1] | 80%用于训练 |
| 默认测试比例 | 0.2 | [1] | 20%用于测试 |
| 随机种子 | 42 | [1] | 确保可重复性 |
| 分层划分 | stratify=cell_types | [2] | 保持类别比例 |
| 最小测试集大小 | >100 cells | [2] | 确保统计显著性 |
| 最小训练集大小 | >500 cells | [2] | 确保模型训练 |

## 边界与分流

- **数据量不足**：若总细胞数<200，考虑使用交叉验证
- **类别不平衡**：使用分层划分保持比例
- **批次效应明显**：按批次划分评估跨批次泛化
- **供体数量少**：使用留一法交叉验证

## 质量检查

- 验证点1：训练集和测试集无重叠
- 验证点2：划分比例符合预期（如80/20）
- 验证点3：细胞类型分布合理
- 验证点4：无数据泄露（同一细胞不在两个集合中）
- 验证点5：划分索引可正常加载和使用

## 回退策略

- **首选**：使用分层随机划分（保持类别比例）
- **备选1**：使用按批次划分（评估跨批次泛化）
- **备选2**：使用交叉验证（小样本情况）
- **最终方案**：使用全数据训练和评估（需注明数据泄露风险）

## 资源召回建议

- **召回场景**：当需要评估模型泛化能力时
- **配套资源**：
  - scATAC-seq数据获取任务（提供完整数据集）
  - ChromFound模型加载任务（需要训练和测试数据）
  - 聚类评估任务（评估测试集性能）

## 证据来源

[1] Efron, B. & Tibshirani, R. "An introduction to the bootstrap". Chapman and Hall, 1994
[2] Hastie, T. et al. "The Elements of Statistical Learning". Springer, 2009
