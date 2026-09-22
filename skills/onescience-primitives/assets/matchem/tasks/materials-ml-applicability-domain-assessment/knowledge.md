# 材料科学机器学习适用域评估方法

## 适用范围
本知识卡片适用于材料科学领域机器学习模型的适用域（Applicability Domain, AD）评估任务，包括确定模型在哪些材料子空间内可提供可靠预测，以及量化预测不确定性。

## 输入
- 训练数据集特征空间描述
- 待预测候选材料的特征向量
- 已训练的机器学习模型

## 输出
- 适用域边界描述（逻辑条件或几何约束）
- 每个预测的AD分数或可靠性指标
- 域内/域外预测的分离标注

## 流程节点
1. **特征空间定义** → 2. **AD方法选择** → 3. **AD边界学习** → 4. **预测可靠性评估** → 5. **结果解释与可视化**

### 步骤1：特征空间定义
- **操作**：定义用于AD评估的特征表示
- **参数**：特征类型（组成、结构、电子）、归一化方法
- **工具**：pymatgen、scikit-learn
- **质量门禁**：特征能有效区分不同材料子空间

### 步骤2：AD方法选择
- **操作**：选择适合的AD评估方法
- **参数**：数据规模、特征维度、计算资源
- **工具**：scikit-learn、自定义实现
- **质量门禁**：方法选择与数据特性匹配

### 步骤3：AD边界学习
- **操作**：从训练数据学习AD边界
- **参数**：边界紧致度、覆盖率要求
- **工具**：聚类算法、密度估计
- **质量门禁**：边界学习收敛，无过拟合

### 步骤4：预测可靠性评估
- **操作**：对新预测进行AD评估
- **参数**：AD分数阈值、不确定性量化方法
- **工具**：距离计算、密度评估
- **质量门禁**：AD分数与预测误差相关

### 步骤5：结果解释与可视化
- **操作**：解释AD评估结果
- **参数**：可视化维度、解释性指标
- **工具**：matplotlib、seaborn
- **质量门禁**：结果可解释，支持决策

## 关键参数

### 通用判据
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| AD方法类型 | 基于距离、基于密度、基于模型 | [1] | 不同方法适用于不同场景 |
| 覆盖率要求 | >50% | [1] | AD应覆盖足够比例的候选空间 |
| 误差降低因子 | >2x | [1] | AD内误差应显著低于全局误差 |

### 校准数值（来自具体体系）
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| MBTR模型AD覆盖率 | 44% | [1] | 透明导电氧化物体系示例 |
| SOAP模型AD覆盖率 | 78% | [1] | 同上 |
| n-gram模型AD覆盖率 | 52% | [1] | 同上 |

## 边界与分流
- **小样本条件**：当训练样本<50时，使用留一法交叉验证AD
- **高维特征**：当特征维度>100时，先进行降维再评估AD
- **计算资源受限**：使用基于距离的简单AD方法替代复杂密度估计

## 质量检查
- AD边界在验证集上的性能评估
- 域内/域外预测误差差异显著性检验
- AD分数与实际预测误差的相关性分析
- AD覆盖率与预测可靠性的权衡分析

## 回退策略
- AD方法不收敛时，尝试替代算法或简化特征空间
- AD覆盖率过低时，放宽边界条件或使用集成方法
- AD评估计算成本过高时，使用采样近似方法

## 资源召回建议
- 当任务涉及模型可靠性评估时召回本卡片
- 配套资源：scikit-learn AD实现、pymatgen特征生成
- 相关卡片：vibrationally-stable-materials-dataset-source（数据获取）

## 补充证据
（无）

## 具体AD方法实现与参数

### kNN方法
```python
from sklearn.neighbors import NearestNeighbors
def knn_ad(X_train, X_new, k=5):
    nn = NearestNeighbors(n_neighbors=k).fit(X_train)
    distances, _ = nn.kneighbors(X_new)
    return distances.mean(axis=1)  # 越大越可能域外
```
- k值范围：5-30，根据数据集大小调整 [3]

### LOF方法
```python
from sklearn.neighbors import LocalOutlierFactor
def lof_ad(X_train, X_new, k=5):
    lof = LocalOutlierFactor(n_neighbors=k, novelty=True)
    lof.fit(X_train)
    return -lof.decision_function(X_new)  # 越大越可能域外
```
- 适用于数据密度分布不均匀的场景 [3]

### OCSVM方法
```python
from sklearn.svm import OneClassSVM
def ocsvm_ad(X_train, X_new, nu=0.1, gamma='scale'):
    ocsvm = OneClassSVM(nu=nu, gamma=gamma)
    ocsvm.fit(X_train)
    return -ocsvm.decision_function(X_new)  # 越大越可能域外
```
- ν ∈ (0, 0.50)：异常分数上界比例
- γ：RBF核带宽，推荐scale自动确定 [3]

### AUCR超参数优化准则 [3]
- 对每个AD方法和超参数组合：
  1. 使用双交叉验证（DCV）计算预测值
  2. 按AD指标降序排列样本
  3. 计算coverage-RMSE曲线
  4. 计算AUCR（曲线下面积的逆指标）
- 选择使AUCR最小的AD方法和超参数组合
- Python代码：https://github.com/hkaneko1985/dcekit

### OOD样本标记集成
- 在candidate_report.json中增加：
```json
{
  "ood_candidates": [{"candidate_id": "C001", "ad_score": 0.85, "reason": "kNN distance > threshold"}],
  "ood_statistics": {"total_candidates": 816, "ood_count": 42, "ood_ratio": 0.051}
}
```
- AD阈值设定：coverage = 90%对应的AD指标值（保守策略）[3]
- 域外候选标注为"待验证预测"，优先使用更高保真方法验证

### 关键参数补充
| 参数 | 推荐值 | 来源 | 说明 |
|------|--------|------|------|
| kNN/LOF k值 | 5-10 | [3] | 根据数据集大小调整 |
| OCSVM ν | 0.01-0.50 | [3] | 异常分数上界比例 |
| OCSVM γ | scale（自动） | [3] | RBF核带宽参数 |
| AD阈值 | coverage=90% | [3] | 保守策略 |
| 特征标准化 | 必须 | [3] | AD方法对尺度敏感 |

### 质量检查补充
- coverage-RMSE曲线应呈现单调递增趋势
- 域外样本比例通常 < 10%（>20%提示模型泛化问题）
- 域内样本预测精度应显著优于域外样本

## 补充证据
[K1] Kaneko H., "Evaluation and Optimization Methods for Applicability Domain Methods and Their Hyperparameters", ACS Omega, 2024, DOI: 10.1021/acsomega.3c08036（全文，提供kNN/LOF/OCSVM实现细节和AUCR优化方法）

## 证据来源
[1] Identifying domains of applicability of machine learning models for materials science, Sutton et al., Nature Communications, 2020, DOI: 10.1038/s41467-020-17112-9
[2] A general approach for determining applicability domain of machine learning models, Schultz et al., npj Computational Materials, 2025, DOI: 10.1038/s41524-025-01573-x
[3] Kaneko H., "Evaluation and Optimization Methods for Applicability Domain Methods and Their Hyperparameters, Considering the Prediction Performance of Machine Learning Models", ACS Omega, 2024, DOI: 10.1021/acsomega.3c08036
