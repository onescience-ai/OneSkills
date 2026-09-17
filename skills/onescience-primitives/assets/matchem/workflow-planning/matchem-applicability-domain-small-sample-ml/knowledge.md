# 材料科学小样本ML适用域评估工作流

## 适用范围

**触发条件**：
- 训练样本量<100个的材料ML任务
- 需要评估模型预测的可靠性
- 候选材料可能超出训练数据分布

**适用场景**：
- 数据稀缺的材料属性预测（如稀有材料、新合成材料）
- 小数据集上的模型评估和验证
- 需要量化预测不确定性的场景

**不适用场景**：
- 大数据集（>1000样本）的标准ML任务
- 不需要不确定性量化的应用场景
- 实时性要求极高的筛选（AD计算增加计算成本）

## 输入

**数据来源**：
- 训练数据集：材料特征和目标属性
- 候选数据集：需要预测的材料
- 验证数据集：用于评估AD性能

**数据格式**：
- 特征矩阵：n_samples x n_features
- 标签向量：n_samples
- 候选矩阵：m_candidates x n_features

**预处理要求**：
- 特征标准化：Z-score或Min-Max归一化
- 缺失值处理：删除或插补
- 特征选择：去除冗余特征

## 输出

**产物**：
- AD评估分数：每个候选的适用域内/外判定
- 不确定性估计：预测值的置信区间
- 可靠预测子集：仅保留AD内的预测结果

**验证标准**：
- AD内预测准确性显著高于AD外
- 不确定性估计与实际误差一致
- 假阳性率（AD外预测为AD内）<10%

## 流程节点

### Step 1：特征工程与标准化
- **操作**：提取和标准化材料特征
- **参数**：标准化方法=Z-score, 特征选择=基于方差阈值
- **工具**：scikit-learn, matminer
- **质量门禁**：特征无缺失，分布合理

### Step 2：AD评估器训练
- **操作**：基于训练数据构建AD边界
- **参数**：方法=Mahalanobis距离+KNN, k=5
- **工具**：scikit-learn, scipy
- **质量门禁**：AD边界覆盖训练数据>95%

### Step 3：候选预测与AD评估
- **操作**：对候选进行预测并评估AD
- **参数**：AD阈值=0.95（95%置信度）
- **工具**：训练好的模型+AD评估器
- **质量门禁**：输出AD分数和不确定性估计

### Step 4：结果筛选与报告
- **操作**：筛选AD内候选，生成报告
- **参数**：仅保留AD内预测，按不确定性排序
- **工具**：pandas, numpy
- **质量门禁**：报告包含AD统计和不确定性分布

## 关键参数

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| AD方法 | Mahalanobis距离 + KNN | [1] | 组合方法更鲁棒 |
| KNN的k值 | 5 | [1] | 需交叉验证调整 |
| AD阈值 | 0.95 | [1] | 95%置信度 |
| 标准化方法 | Z-score | [2] | 对异常值鲁棒 |
| 数据增强方法 | WGAN-GP | [2] | 小样本下有效 |
| 不确定性量化 | Ensemble方法 | [3] | 多模型平均 |

## 边界与分流

**异常处理**：
- 训练数据过少（<20样本）：使用留一法交叉验证
- 特征维度过高：先进行PCA降维
- AD边界过于宽松：调整阈值或使用更严格的方法

**降级策略**：
- AD评估不可靠：标记所有预测为"需DFT验证"
- 不确定性估计失败：使用简单范围检查作为fallback

## 质量检查

**验证点**：
- AD内预测R²显著高于AD外（差异>0.2）
- 不确定性估计覆盖率与置信水平一致
- 学习曲线显示模型未严重过拟合
- 特征重要性在多次运行中稳定

**阈值**：
- AD内准确率>80%
- AD外准确率<60%（说明AD有效）
- 不确定性覆盖率：90%置信区间应覆盖~90%实际值

## 回退策略

**失败时的替代方案**：
- AD评估失败：使用简单min-max范围检查
- 不确定性量化失败：标记为"低置信度"
- 数据增强失败：使用过采样或欠采样

## 资源召回建议

**何时应召回本卡片**：
- 用户样本量<100个
- 用户提到"applicability domain"、"uncertainty"、"small sample"
- 需要评估模型预测可靠性

**配套资源**：
- matchem-vibrationally-stable-materials-ml-screening：ML筛选工作流
- matchem-phonon-calculation-vasp-validation：DFT验证工作流

## 证据来源

[1] Wei G, Li M, Cui B, Xiu W, Sarman AM. "Machine Learning for Structural Steels: Materials Design, Property Prediction, Durability, and Future Directions." Materials, 2026, 19(17): 3612. DOI: 10.3390/ma19173612

[2] Yue Q, Yu G, Yao Y, et al. "Prediction model for compressive strength of alkali-activated multi-source solid-waste grouting materials based on generative adversarial networks and machine learning." PLoS One, 2026, 21(9): e0357051. DOI: 10.1371/journal.pone.0357051

[3] Wang H, Ye H, Zhao T, Sun D, Yan F. "Machine Learning-Driven Prediction and Interactive Nonlinear Analysis of Compaction Parameters for Fine-Grained Soils." Materials, 2026, 19(17): 3717. DOI: 10.3390/ma19173717
