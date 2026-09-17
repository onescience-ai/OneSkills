# 聚类评估与标签映射任务

## 适用范围

**触发条件**：
- Leiden聚类标签（如0,1,2）与真实细胞类型标签（如T_cell,B_cell）空间不同
- 需要计算宏平均F1等需要标签对齐的指标
- 聚类结果评估需要与真实标签比较

**适用场景**：
- scATAC-seq细胞类型注释质量评估
- scRNA-seq聚类结果评估
- 任何需要比较聚类标签与真实标签的场景
- 多分类问题的标签映射

**不适用场景**：
- 已经使用相同标签空间的评估（如两个聚类结果比较）
- 使用不需要标签映射的指标（如ARI、NMI）

## 输入

- **聚类标签**：Leiden聚类输出的标签（如字符串'0','1','2'）
- **真实标签**：细胞类型注释（如'T_cell','B_cell','Monocyte'等）
- **数据格式**：
  - `cluster_labels`：list或array，长度=n_cells
  - `true_labels`：list或array，长度=n_cells

## 输出

- **映射字典**：聚类ID → 真实细胞类型的映射关系
- **评估指标**：
  - 宏平均F1分数（macro F1）
  - 各细胞类型的F1分数
  - 混淆矩阵
- **评估报告**：包含映射结果和各类型性能

## 流程节点

### Step 1：验证标签空间
- **操作**：检查聚类标签和真实标签的格式
- **检查项**：
  1. 标签长度一致（均为n_cells）
  2. 无空值或NaN
  3. 聚类标签和真实标签空间不同
- **质量门禁**：标签格式正确，长度一致

### Step 2：构建成本矩阵
- **操作**：计算聚类标签与真实标签的匹配成本
- **公式**：cost[i,j] = -count(cluster_i == true_j)
  - 负号是因为linear_sum_assignment求最小成本
  - 实际是最大化匹配数
- **实现**：
  ```python
  import numpy as np
  from sklearn.metrics import confusion_matrix
  
  # 获取唯一标签
  unique_clusters = np.unique(cluster_labels)
  unique_true = np.unique(true_labels)
  
  # 构建成本矩阵（负混淆矩阵）
  cm = confusion_matrix(true_labels, cluster_labels, labels=unique_true)
  cost_matrix = -cm.T  # 转置使行列对应正确
  ```
- **质量门禁**：成本矩阵形状正确，无异常值

### Step 3：匈牙利算法匹配
- **操作**：使用匈牙利算法找到最优标签映射
- **实现**：
  ```python
  from scipy.optimize import linear_sum_assignment
  
  # 执行匈牙利算法
  row_ind, col_ind = linear_sum_assignment(cost_matrix)
  
  # 构建映射字典
  mapping = {}
  for r, c in zip(row_ind, col_ind):
      if c < len(unique_clusters):
          mapping[unique_clusters[c]] = unique_true[r]
  ```
- **质量门禁**：映射字典完整，无重复映射

### Step 4：应用标签映射
- **操作**：将聚类标签转换为真实标签空间
- **实现**：
  ```python
  # 应用映射
  mapped_labels = [mapping.get(l, 'Unknown') for l in cluster_labels]
  
  # 统计未映射比例
  unknown_ratio = mapped_labels.count('Unknown') / len(mapped_labels)
  ```
- **质量门禁**：未映射比例 < 10%

### Step 5：计算评估指标
- **操作**：计算宏平均F1和其他指标
- **实现**：
  ```python
  from sklearn.metrics import f1_score, classification_report, confusion_matrix
  
  # 计算宏平均F1
  macro_f1 = f1_score(true_labels, mapped_labels, average='macro')
  
  # 详细分类报告
  report = classification_report(true_labels, mapped_labels)
  
  # 混淆矩阵
  cm = confusion_matrix(true_labels, mapped_labels)
  ```
- **质量门禁**：宏平均F1 > 0，各类型F1合理

### Step 6：生成评估报告
- **操作**：汇总评估结果
- **内容**：
  - 映射字典
  - 宏平均F1分数
  - 各细胞类型的F1、Precision、Recall
  - 混淆矩阵可视化
- **质量门禁**：报告完整，可读性强

## 关键参数

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 匈牙利算法 | scipy.optimize.linear_sum_assignment | [1] | 最优标签匹配 |
| 评估指标 | macro F1 | [2] | 宏平均F1分数 |
| 备选指标 | ARI, NMI | [2] | 不需要标签映射的指标 |
| 映射质量阈值 | 未映射比例 < 10% | [2] | 确保映射有效性 |
| F1分数阈值 | > 0 | [2] | 基本有效性检查 |

## 边界与分流

- **标签空间完全不匹配**：检查数据标签是否正确
- **映射后F1仍为0**：可能是数据质量问题或标签错误
- **未映射比例过高**：考虑增加聚类数或检查真实标签
- **内存不足**：分批计算成本矩阵

## 质量检查

- 验证点1：映射字典完整，无重复映射
- 验证点2：未映射比例 < 10%
- 验证点3：宏平均F1 > 0
- 验证点4：各细胞类型F1分数合理（不全为0或1）
- 验证点5：混淆矩阵对角线元素较大

## 回退策略

- **首选**：使用匈牙利算法进行最优标签映射
- **备选1**：使用ARI或NMI（不需要标签映射）
- **备选2**：手动指定映射关系（如果已知）
- **最终方案**：标记评估失败，说明标签映射问题

## 资源召回建议

- **召回场景**：当聚类标签与真实标签空间不同时
- **配套资源**：
  - scATAC-seq数据获取任务（提供真实标签）
  - ChromFound模型加载任务（提供聚类标签）
  - 生物一致性评估任务（评估表征质量）

## 证据来源

[1] Pedregosa, F. et al. "Scikit-learn: Machine Learning in Python". JMLR 12, 2011
[2] Van der Maaten, L. & Hinton, G. "Visualizing Data using t-SNE". JMLR 9, 2008
