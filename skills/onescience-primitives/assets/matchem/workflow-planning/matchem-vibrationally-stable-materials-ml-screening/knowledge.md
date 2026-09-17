# 振动稳定材料机器学习筛选工作流

## 适用范围

**触发条件**：
- 需要大规模筛选振动稳定（dynamically stable）的晶体材料
- 希望用ML模型替代或加速VASP phonon计算
- 已有Materials Project等数据库的声子数据可用于训练

**适用场景**：
- 新材料发现：从候选空间中快速排除动力学不稳定结构
- 材料设计流程中的预筛选步骤：在DFT phonon计算前用ML过滤
- 高通量材料筛选：处理数千至数万个候选结构

**不适用场景**：
- 需要精确声子色散关系的研究（仍需DFT计算）
- 非晶体材料或无序体系的稳定性评估
- 极小样本（<50个样本）的模型训练

## 输入

**数据来源**：
- Materials Project数据库：提供phonon频率、热力学稳定性数据
- OMDB（Optical Materials Database）：光学材料相关数据
- 论文复现数据集：已发表论文中的声子计算结果

**数据格式**：
- 晶体结构：CIF或POSCAR格式
- 标签：动力学稳定性（有/无虚频）、声子频率数据
- 特征：元素组成、晶体结构原型、晶格参数

**预处理要求**：
- 结构标准化：统一为Primitive cell
- 特征工程：元素特征、结构特征、Bonding特征
- 数据清洗：去除重复结构、标注不确定性

## 输出

**产物**：
- 训练好的ML模型（如DynStabNet checkpoint）
- 候选材料的动力学稳定性预测分数
- 筛选后的候选材料列表

**验证标准**：
- 模型准确率：>95%（DynStabNet报告97%）
- 推理速度：每个结构~1ms（vs DFT phonon数小时）
- 与DFT结果的一致性：假阴性率<5%

## 流程节点

### Step 1：数据获取
- **操作**：从Materials Project API获取phonon数据
- **参数**：material_ids列表，properties=["phonon"]
- **工具**：mp-api (Materials Project Python API)
- **质量门禁**：数据量>1000个结构，标签完整性>90%

### Step 2：特征工程
- **操作**：提取晶体结构特征
- **参数**：元素特征（电负性、原子半径等）、结构特征（空间群、晶格参数）
- **工具**：pymatgen, matminer
- **质量门禁**：特征维度<100，缺失值<5%

### Step 3：模型训练
- **操作**：训练E(3)-等变图神经网络
- **参数**：架构=E3GNN, 训练集/验证集/测试集=7:1.5:1.5
- **工具**：PyTorch, e3nn
- **质量门禁**：测试集准确率>95%，CV标准差<5%

### Step 4：候选筛选
- **操作**：对候选结构进行动力学稳定性预测
- **参数**：阈值=0.5（概率>0.5为稳定）
- **工具**：训练好的DynStabNet模型
- **质量门禁**：输出概率分数，标记不确定性

## 关键参数

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 模型架构 | E(3)-等变GNN (DynStabNet) | [1] | 捕捉晶体对称性 |
| 训练数据来源 | Materials Project phonon | [1][2] | 需API访问权限 |
| 推理速度 | ~1ms/结构 | [1] | 比DFT快10^4倍 |
| 准确率 | 97% | [1] | 在测试集上 |
| 训练数据规模 | 数千结构 | [1] | 需足够覆盖化学空间 |
| 虚频判断阈值 | 最小频率<0 cm^-1 | [2] | 动力学不稳定判据 |

## 边界与分流

**异常处理**：
- 训练数据不足（<500结构）：降级为简单ML模型（RF/XGBoost）
- 元素不在训练集范围内：标记为"域外"，建议DFT计算
- 结构高度对称或高度无序：模型预测不确定性增大，需人工审核

**降级策略**：
- 无phonon训练数据：使用formation energy作为代理标签
- 计算资源不足：使用预训练模型进行迁移学习

## 质量检查

**验证点**：
- 训练/验证/测试集准确率差距<10%
- 学习曲线收敛
- 特征重要性稳定（多次运行变化<5%）
- 与DFT结果的Bland-Altman分析

**阈值**：
- 准确率>95%
- 假阴性率<5%（漏掉稳定材料的比例）
- 推理时间<10ms/结构

## 回退策略

**失败时的替代方案**：
- ML模型不可靠：回退到DFT phonon计算（VASP+PHONOPY）
- 数据质量问题：使用数据增强（WGAN-GP）或迁移学习
- 元素空间外推：标记为"需DFT验证"

## 资源召回建议

**何时应召回本卡片**：
- 用户需要大规模筛选振动稳定材料
- 用户提到"phonon stability"、"dynamical stability"、"ML screening"
- 用户希望加速材料发现流程

**配套资源**：
- matchem-phonon-calculation-vasp-validation：DFT phonon计算工作流
- matchem-applicability-domain-small-sample-ml：适用域评估方法

## 证据来源

[1] Li H, Chen Z, He T, et al. "DynStabNet: A Deep Learning Framework for Fast Dynamical Stability Prediction of Crystal Structures." J Phys Chem Lett, 2026, 17(30): 8585-8594. DOI: 10.1021/acs.jpclett.6c01523

[2] Lee H, Li Z, He J, Xia Y. "Data-Driven Exploration and Insights Into Temperature-Dependent Phonons in Inorganic Materials." Small, 2026, 22(46): e00071. DOI: 10.1002/smll.202600071

[3] Tee WS, Xia W, Flint R, Wang CZ. "Anharmonic effects on the dynamical stability of Ce-Co-Cu intermetallic ternary compounds." RSC Adv, 2026, 16(16): 14395-14405. DOI: 10.1039/d5ra09680d
