# 多孔材料数据获取与验证方法

## 适用范围

适用于多孔材料（MOF、沸石、多孔碳、多孔聚合物等）基础模型构建中的数据获取和验证环节。当任务要求基于真实多孔材料数据（非模拟数据）进行训练和验证时，必须使用本卡片描述的数据库和验证方法。

不适用场景：仅需使用模拟数据进行算法验证的场景（但需在报告中明确标注数据来源为模拟）。

## 输入

- **数据需求描述**：目标材料类型（MOF/沸石/多孔碳等）、目标性质（吸附容量/选择性/带隙等）、所需数据量
- **验证需求描述**：验证指标（MAE/RMSE/R²）、验证数据来源要求（实验/高保真计算）

## 输出

- **训练数据集**：包含结构信息和性质标签的标准化数据集
- **验证数据集**：独立于训练集的验证数据（实验或高保真计算结果）
- **数据质量报告**：数据来源、样本量、缺失值处理、异常值检测结果

## 流程节点

### 阶段1：数据获取
1. **数据库选择** → 根据材料类型选择合适数据库（见关键参数表）
2. **数据下载** → 通过API或批量下载获取结构数据
3. **数据清洗** → 去重、格式统一、缺失值处理
4. **质量筛选** → 剔除不合理结构（如原子间距过近）

### 阶段2：数据预处理
5. **结构统一** → 统一坐标系、晶胞参数归一化
6. **特征提取** → 原子坐标+类型（GNN端到端学习，无需手工特征）
7. **数据分割** → 训练集/验证集/测试集划分（通常70/15/15或80/10/10）

### 阶段3：验证数据获取
8. **实验验证** → 从文献或数据库获取实验吸附/分离数据
9. **计算验证** → 使用GCMC模拟或高精度DFT计算生成验证数据
10. **验证报告** → 模型预测与验证数据对比，计算验证指标

## 关键参数

| 参数 | 推荐值/来源 | 说明 |
|------|-------------|------|
| Materials Project | materialsproject.org | 约15万无机材料结构，含DFT计算性质，API免费 |
| ICSD | icsd.products.fiz-karlsruhe.de | 晶体结构数据库，约28万条目，需机构订阅 |
| QMOF Database | qmof.com | 量子力学计算的MOF数据库，约20万结构 |
| CSD MOF子集 | ccdc.cam.ac.uk | 剑桥结构数据库MOF子集，需商业许可 |
| QMOF Database (Zenodo) | zenodo.org | 开源MOF数据集，可免费下载 |
| 吸附数据来源 | NIST Isotherm Database | 实验吸附等温线数据 |
| GCMC模拟参数 | RASPA软件 | 标准GCMC模拟工具，需设置力场和温度/压力条件 |

## 边界与分流

- **数据库访问受限**：ICSD和CSD需机构订阅，优先使用Materials Project和QMOF（开源）
- **数据量不足**：使用迁移学习策略，从相似材料域迁移；或使用数据增强（结构扰动、旋转等）
- **验证数据缺失**：使用高保真计算（GCMC/DFT）生成验证数据，或从文献中提取实验数据
- **数据质量差**：进行异常值检测（如IQR方法），剔除明显不合理的数据点

## 质量检查

- **数据来源可追溯**：每个样本必须记录来源数据库和DOI/ID
- **结构合理性**：原子间距>0.5 Å，键长在合理范围内
- **性质标签合理性**：吸附容量>0，带隙≥0等物理约束
- **数据分割合理性**：训练集/验证集/测试集无重叠，分布一致
- **验证独立性**：验证数据必须完全独立于训练数据

## 回退策略

- 若数据库不可用：使用公开文献中的数据（需引用原文）
- 若数据量不足：使用迁移学习或few-shot策略
- 若验证数据缺失：使用交叉验证作为临时方案，但必须在报告中说明

## 资源召回建议

当任务涉及以下关键词时应召回本卡片：
- 多孔材料数据、MOF数据、沸石数据
- Materials Project、ICSD、QMOF、CSD
- 数据获取、数据下载、数据清洗
- 吸附验证、GCMC模拟、DFT验证
- 实验数据、验证数据集

配套资源：`matchem-porous-material-foundation-model`（模型架构选择）

## 证据来源

[1] Reiser P, et al. Graph neural networks for materials science and chemistry. Communications Materials, 2022, 3: 93. DOI: 10.1038/s43246-022-00315-6

[2] Clayson IG, et al. High Throughput Methods in the Synthesis, Characterization, and Optimization of Porous Materials. Advanced Materials, 2020, 32: e2002780. DOI: 10.1002/adma.202002780

[3] Porous materials for hydrogen storage. Chem, 2022. DOI: 10.1016/j.chempr.2022.01.012

[4] New insights into hydrogen uptake on porous carbon materials via explainable machine learning. Carbon, 2021. DOI: 10.1016/j.carbon.2021.07.053

[5] Machine-learning-assisted material discovery of oxygen-rich highly porous carbon materials. Nature Communications, 2023. DOI: 10.1038/s41467-023-39479-x

[6] Materials Project documentation. https://materialsproject.org/docs/

[7] QMOF Database. https://qmof.com/