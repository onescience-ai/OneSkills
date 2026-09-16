# 抗体-抗原亲和力预测特征工程工作流

## 适用范围

**触发条件**：
- 需要从抗体序列中提取亲和力相关特征
- 需要构建特征向量用于机器学习或深度学习模型
- 需要CDR区域特异性特征进行亲和力预测

**适用场景**：
- 抗体-抗原结合亲和力预测
- 中和抗体筛选与排序
- 抗体工程优化

**不适用场景**：
- 基于结构的亲和力预测（需要3D结构信息）
- 纯文献综述或理论分析

## 输入

**输入数据格式**：
- 抗体重链和轻链氨基酸序列（字符串或FASTA）
- CDR区域掩码（来自ANARCI编号）
- 抗原序列（可选）

**来源**：
- 用户提供的抗体序列文件
- 数据库下载的抗体序列

**预处理要求**：
- 序列已完成标准编号（推荐使用ANARCI）
- CDR区域已识别并掩码

## 输出

**输出产物**：
1. 特征矩阵：每行对应一个抗体，每列对应一个特征
2. 特征名称列表：特征的解释性名称
3. 特征重要性排名（可选）

**格式**：
- NumPy数组或Pandas DataFrame
- CSV文件或HDF5文件

**验证标准**：
- 特征维度合理（通常50-500维）
- 无缺失值或已填充
- 特征值范围标准化

## 流程节点

### Step 1：CDR区域序列编码
- **操作**：提取CDR H1/H2/H3区域的氨基酸序列
- **参数**：CDR掩码（来自ANARCI）、编码方式（one-hot、k-mer、嵌入）
- **工具**：Python NumPy/Pandas
- **质量门禁**：CDR序列长度合理，编码无错误

### Step 2：界面残基识别
- **操作**：根据距离阈值识别抗原-抗体界面残基
- **参数**：距离阈值（8-10 Å）、残基类型（极性/非极性/带电）
- **工具**：Python SciPy（距离计算）
- **质量门禁**：界面残基数量合理（20-50个）

### Step 3：序列比对特征
- **操作**：与已知高亲和力抗体序列比对
- **参数**：比对算法（BLOSUM矩阵）、相似度阈值
- **工具**：BioPython（PairwiseAligner）
- **质量门禁**：比对得分合理

### Step 4：理化性质计算
- **操作**：计算疏水性、电荷、分子量等
- **参数**：性质数据库（AAindex）、计算窗口
- **工具**：BioPython（ProtParam）
- **质量门禁**：性质值范围合理

### Step 5：序列motif匹配
- **操作**：匹配已知亲和力相关序列motif
- **参数**：motif数据库（PROSITE、Pfam）、匹配阈值
- **工具**：BioPython（Prosite）
- **质量门禁**：匹配motif数量合理

### Step 6：特征组合与标准化
- **操作**：合并所有特征并标准化
- **参数**：标准化方法（Z-score、Min-Max）、特征选择（方差阈值）
- **工具**：Scikit-learn（StandardScaler）
- **质量门禁**：特征维度合理，无缺失值

## 关键参数

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| CDR区域定义 | H1: 26-32, H2: 56-58, H3: 95-102 (IMGT) | [1] | CDR区域位置 |
| 界面距离阈值 | 8-10 Å | [1] | 抗原-抗体界面定义 |
| 编码方式 | one-hot, k-mer (k=3), 嵌入 | [1] | 序列编码方法 |
| 理化性质 | 疏水性、电荷、分子量 | [2] | 序列性质计算 |
| 比对矩阵 | BLOSUM62 | [2] | 序列比对参数 |
| 标准化方法 | Z-score | [2] | 特征标准化 |

## 边界与分流

**异常处理**：
- 如果CDR区域提取失败，使用全序列特征替代
- 如果界面残基识别失败，使用随机残基作为近似
- 如果motif匹配失败，跳过该特征类型

**降级策略**：
- 当高级特征不可用时，使用简单序列特征（长度、氨基酸频率）
- 当特征维度过高时，使用PCA降维

## 质量检查

**验证点**：
- 特征矩阵无缺失值
- 特征值范围合理（无异常大或小的值）
- 特征维度与预期相符
- 特征重要性分析显示CDR相关特征有贡献

**阈值**：
- 缺失值比例 < 5%
- 特征方差 > 0
- 相关性矩阵无高度相关特征（r > 0.9）

**失败处理**：
- 如果特征提取失败，记录警告并使用备用特征集
- 如果标准化失败，使用原始特征

## 回退策略

**失败时的替代方案**：
1. 使用简单的氨基酸频率和序列长度特征（50维）
2. 使用预计算的CDR区域特征（从数据库下载）
3. 使用序列嵌入（如ESM-2、ProtBERT）作为特征

## 资源召回建议

**何时应召回本卡片**：
- 当任务涉及抗体亲和力预测特征构建时
- 当需要CDR区域特异性特征时
- 当执行抗体序列分析任务时

**配套资源**：
- `bio-anarci-antibody-numbering`：ANARCI抗体编号
- `bio-abaffinity-model-inference`：AbAffinity模型推理
- `bio-abaffinity-model-knowledge-graph`：AbAffinity模型知识图谱

## 证据来源

[1] "AbAgKer: a unified semi-supervised framework for antigen-antibody binding affinity and kinetics prediction", Luo G, Wang J, Zhang S, Bioinformatics, 2026, DOI: 10.1093/bioinformatics/btag606
[2] "Enhancing antibody affinity through experimental sampling of non-deleterious CDR mutations predicted by machine learning", Clark T, Subramanian V, Jayaraman A, Commun Chem, 2023, DOI: 10.1038/s42004-023-01037-7