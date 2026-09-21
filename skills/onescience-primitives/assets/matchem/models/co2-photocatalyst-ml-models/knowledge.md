# CO2光催化剂机器学习模型

## 适用范围
用于CO2光催化剂性能预测的机器学习模型，包括带隙预测、光催化活性预测、稳定性预测、可合成性预测等。适用于数据驱动的材料筛选、高通量虚拟筛选、材料设计优化等场景。

## 输入
- 材料特征：晶体结构、组成、电子结构等
- 训练数据：实验或DFT计算数据集
- 模型参数：超参数配置

## 输出
- 预测属性：带隙、形成能、光催化活性、稳定性等
- 模型性能指标：MAE、R²、AUC等
- 特征重要性分析

## 流程节点
1. **数据准备** → 从Materials Project等数据库获取训练数据
2. **特征工程** → 提取材料描述符（组成特征、结构特征、电子特征）
3. **模型训练** → 选择合适模型架构进行训练
4. **模型评估** → 交叉验证、独立测试集评估
5. **预测应用** → 对新候选材料进行性能预测

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| model_type | GNN, Random Forest, Gradient Boosting | [1] | 模型类型选择 |
| features | composition, structure, electronic | [2] | 特征类型 |
| band_gap_range | (0.0, 3.0) eV | [1] | 光催化剂带隙目标范围 |
| train_test_split | 0.8/0.2 | [3] | 数据集划分比例 |
| cross_validation | 5-fold | [3] | 交叉验证折数 |

## 边界与分流
- 小数据集问题：使用迁移学习、数据增强、主动学习
- 过拟合风险：使用正则化、早停、交叉验证
- 模型可解释性：使用SHAP、特征重要性分析
- 分布外预测：使用不确定性量化、集成学习

## 质量检查
- 验证模型在独立测试集上的性能
- 检查预测值是否在合理物理范围内
- 与文献报道的实验数据对比
- 评估模型在不同材料体系上的泛化能力

## 回退策略
- 模型性能不足时：尝试不同模型架构或特征组合
- 数据不足时：使用迁移学习或预训练模型
- 预测不确定性高时：使用集成模型或多保真度建模

## 资源召回建议
- 当任务需要预测材料性能时召回此卡片
- 配套使用Materials Project API获取训练数据
- 与VASP计算工作流卡片结合进行高精度验证

## 证据来源
[1] Scaling deep learning for materials discovery, Nature, 2023, DOI: 10.1038/s41586-023-06735-9
[2] Data-Driven Strategies for Accelerated Materials Design, Accounts of Chemical Research, 2021, DOI: 10.1021/acs.accounts.0c00785
[3] Machine Learning for Materials Scientists: An Introductory Guide toward Best Practices, Chemistry of Materials, 2020, DOI: 10.1021/acs.chemmater.0c01907