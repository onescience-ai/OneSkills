# 无铅杂化钙钛矿稳定性机器学习筛选工作流

## 适用范围
本卡片服务于无铅杂化钙钛矿稳定性机器学习筛选任务，涵盖从数据准备、模型配置、不确定性估计、验证方法到过拟合处理的完整工作流。适用于需要高通量筛选具有热力学稳定性的无铅钙钛矿材料的场景，包括光伏、传感器、透明电子等领域的材料发现。

## 输入
- 无铅杂化钙钛矿晶体结构数据（CIF格式或Materials Project ID）
- 材料属性数据（形成能、带隙、弹性常数等）
- 稳定性标签（基于DFT计算的凸包稳定性判据）
- 计算资源（用于DFT验证的VASP/HPC环境）

## 输出
- 筛选出的稳定无铅钙钛矿候选材料列表
- 模型性能评估报告（包括不确定性估计和过拟合诊断）
- 独立验证数据对比报告
- 最终筛选结果与推荐

## 流程节点
1. **数据来源获取** → 2. **模型配置与训练** → 3. **不确定性估计** → 4. **候选生成与筛选** → 5. **独立验证** → 6. **结果分析与报告**

### 步骤1: 数据来源获取
- **操作**：从公开数据库获取无铅杂化钙钛矿稳定性数据集
- **参数**：数据规模通常需要数百到数千个样本（关联论文使用212个HOIPs样本）
- **工具**：Materials Project API（materialsproject.org）、OQMD API（oqmd.org）、ICSD、关联论文数据集
- **数据来源**：关联论文数据来自先前的高通量第一性原理计算（DOI:10.1038/ncomms15679, DOI:10.1038/ncomms16059）
- **质量门禁**：数据来源可追溯到公开数据库；稳定性标签有明确的DFT计算依据；训练集/测试集划分可追溯

### 步骤2: 模型配置与训练
- **操作**：根据关联论文配置机器学习模型（Gradient Boosted Regression, GBR）
- **参数**：特征工程、超参数调优、训练集/测试集划分
- **工具**：scikit-learn（GradientBoostingRegressor）
- **质量门禁**：模型配置与关联论文一致；使用5折交叉验证评估性能
- **关联论文配置**：GBR模型，超参数：loss=least_squares, learning_rate=0.2, max_depth=12, max_features=0.7, min_samples_leaf=3, n_estimators=100
- **特征工程**：30个初始特征，通过"last-place elimination"方法选择14个最重要特征（容忍因子Tf、八面体因子Of、离子电荷ICB、p轨道电子Xp-electron、电离能IEB、电负性χB、电子亲和能EAB、离子极化率PB/PA、s+p轨道半径rs+p_B、铁离子半径rB/rA、HOMO/LUMO等）

### 步骤3: 不确定性估计
- **操作**：实现不确定性估计方法（集成方法、贝叶斯神经网络、dropout）
- **参数**：集成模型数量（推荐10-100个模型）、dropout率（0.1-0.5）、置信区间（95%）
- **工具**：scikit-learn（BaggingRegressor、GradientBoostingRegressor的`predict`方法返回`std`）、TensorFlow Probability、PyTorch
- **方法选择**：对于GBR模型，推荐使用Bagging集成方法估计不确定性；对于神经网络模型，推荐使用Monte Carlo dropout
- **质量门禁**：不确定性估计与预测值相关（预测不确定性应随误差增大而增大）；校准良好（预测区间覆盖率应接近置信水平）

### 步骤4: 候选生成与筛选
- **操作**：在化学组成空间内生成候选材料，应用约束筛选
- **参数**：化学式合法性、稳定性阈值、不确定性阈值
- **工具**：从已知材料库采样、基于晶体结构原型生成
- **质量门禁**：候选化学式合法；预测不确定性在可接受范围内

### 步骤5: 独立验证
- **操作**：使用DFT计算或实验数据验证候选稳定性
- **参数**：形成能计算、凸包分析、声子色散关系
- **工具**：VASP、PHONOPY、pymatgen
- **质量门禁**：验证数据来源独立；误差容忍度明确

### 步骤6: 结果分析与报告
- **操作**：比较模型预测与独立验证结果，生成最终筛选报告
- **参数**：预测准确性（R2、MSE、MAE）、不确定性覆盖度、假阳性/假阴性率
- **工具**：pandas、matplotlib、scikit-learn（learning_curve、validation_curve）
- **过拟合诊断**：绘制学习曲线（training score vs validation score vs sample size）、验证曲线（model complexity vs score）、特征重要性稳定性
- **质量门禁**：结论有独立验证数据支撑；候选排序基于可验证的材料属性；训练/验证R2差距<0.1

## 关键参数
### 通用判据
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 数据来源 | Materials Project、OQMD、ICSD | [1] | 公开数据库提供无铅钙钛矿数据 |
| 模型配置 | XGBoost、Random Forest | [1] | 关联论文中记录的模型类型 |
| 不确定性估计方法 | 集成方法、贝叶斯神经网络、dropout | [3,4] | 适用于材料筛选的不确定性量化 |
| 独立验证来源 | DFT计算、实验文献 | [1,2] | 独立于训练数据的验证数据 |
| 过拟合诊断方法 | 学习曲线、验证曲线、交叉验证 | [3,4] | 诊断和缓解模型过拟合 |

### 校准数值
以下数值来自具体材料体系，供量级校准；其他体系需以自身证据重新锚定：
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 典型数据集规模 | 212个样本（关联论文），扩展至5158个候选 | [1] | 无铅钙钛矿ML筛选任务的常见数据规模 |
| 模型性能指标 | R2=0.97, r=0.985, MSE=0.086 | [1] | 关联论文中GBR模型性能 |
| 特征数量 | 30个初始特征，14个最优特征 | [1] | 通过last-place elimination方法选择 |
| 训练/测试集划分 | 80%/20% | [1] | 关联论文中的数据划分比例 |
| 交叉验证 | 5折交叉验证 | [1] | 关联论文中的验证方法 |
| GBR超参数 | learning_rate=0.2, max_depth=12, n_estimators=100 | [1] | 关联论文中优化的超参数 |
| 容忍因子范围 | 0.8-1.2（Tf），0.4-0.7（Of） | [1] | 结构稳定性筛选条件 |
| 带隙范围 | 0.9-1.6 eV（光伏应用） | [1] | 光伏材料筛选条件 |
| 不确定性估计方法 | 高斯过程回归、集成方法 | [3,4] | 材料性质预测的不确定性量化 |
| 过拟合诊断指标 | 训练/验证R2差距、学习曲线 | [3,4] | 小样本ML的过拟合风险评估 |

## 边界与分流
- **数据来源不足**：当公开数据库中无铅钙钛矿数据有限时，应转向文献挖掘或自行计算生成训练数据。
- **计算资源不足**：当无法执行DFT第一性原理计算时，应明确标记验证步骤为BLOCKED，并说明原因。
- **模型性能不佳**：当小样本条件下模型性能不达标时，应考虑迁移学习、数据增强或更简单的模型。
- **不确定性估计不准确**：当不确定性估计与预测值不相关时，应调整不确定性估计方法或增加集成模型数量。

## 质量检查
- **数据来源验证**：检查数据是否可追溯到公开数据库（Materials Project、OQMD）。
- **模型配置验证**：检查模型配置是否与关联论文一致。
- **不确定性估计验证**：检查不确定性估计是否与预测值相关，校准是否良好。
- **过拟合诊断**：检查训练/验证准确率差距、学习曲线、特征重要性稳定性。
- **独立验证**：检查验证数据来源是否独立，误差容忍度是否明确。

## 回退策略
- **数据不足回退**：使用迁移学习从相关材料体系迁移知识。
- **计算资源不足回退**：使用机器学习原子间势（如MACE、M3GNet）替代第一性原理计算进行初步筛选。
- **模型性能不足回退**：使用集成方法或贝叶斯优化调整模型超参数。
- **不确定性估计不足回退**：使用简单的集成方法（如Bagging）估计预测不确定性。

## 资源召回建议
- 当任务涉及无铅杂化钙钛矿稳定性机器学习筛选时召回本卡片
- 配套资源：onescience-primitives中的Materials Project数据获取工具、DFT计算工作流卡片
- 相关领域：材料基因组计划、高通量计算材料学、钙钛矿光伏材料

## 证据来源
[1] Accelerated discovery of stable lead-free hybrid organic-inorganic perovskites via machine learning, Lu et al., Nature Communications, 2018, DOI: 10.1038/s41467-018-05761-w
[2] New tolerance factor to predict the stability of perovskite oxides and halides, Bartel et al., Science Advances, 2019, DOI: 10.1126/sciadv.aav0693
[3] Genome-Guided Interpretable Screening of Phase-Stable, Lead-Free Double Perovskite Absorbers for All-Inorganic Semiconductors, Sensors, and Photovoltaics with DFT-Validated Design Rules, Ahtasu et al., 2026, DOI: 10.48550/arXiv.2605.22887
[4] Machine Learning Design of Perovskite Catalytic Properties, Jacobs et al., 2019, DOI: 10.1021/acs.chemmater.9b02166
[5] Clarifying Trust of Materials Property Predictions using Neural Networks with Distribution-Specific Uncertainty Quantification, Gruich et al., 2023, DOI: 10.48550/arXiv.2302.02595
[6] Methods for comparing uncertainty quantifications for material property predictions, Tran et al., 2019, DOI: 10.48550/arXiv.1912.10066