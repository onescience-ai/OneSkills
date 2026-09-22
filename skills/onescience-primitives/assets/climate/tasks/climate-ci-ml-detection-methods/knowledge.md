# 对流初生检测机器学习方法

## 适用范围
面向对流初生（CI）检测任务中机器学习模型的选择、训练和推理，适用于基于静止气象卫星数据的CI检测。覆盖传统ML（随机森林、XGBoost）和深度学习（CNN、U-Net）方法。

## 输入
- 卫星多通道亮温/反射率时序数据
- CI标签（来自雷达回波或人工标注）
- 物理特征（云顶温度、冷却率、多通道亮温差等）

## 输出
- 训练好的CI检测模型
- 模型性能评估报告（POD/FAR/CSI/AUC）
- 特征重要性分析

## 流程节点
1. **数据预处理** → 标准化、缺失值处理、时序对齐
2. **特征工程** → 提取CTT、冷却率、多通道亮温差、纹理特征等
3. **样本构建** → 正负样本配比（建议1:3至1:10）
4. **模型训练** → 选择模型架构、超参数调优、交叉验证
5. **模型评估** → ROC曲线、混淆矩阵、POD/FAR/CSI
6. **模型解释** → 特征重要性、SHAP值、物理一致性检查
7. **推理部署** → 模型序列化、输入输出契约定义

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 推荐ML模型 | Random Forest, XGBoost | [1][2] | 传统ML方法，训练快、可解释 |
| 推荐DL模型 | U-Net, ResNet | [3][5] | 深度学习方法，适合图像数据 |
| 核心特征：云顶温度（CTT） | 200K-320K | [1][4] | CI检测核心特征 |
| 核心特征：冷却率 | -2K/15min至-8K/15min | [4][6] | 云顶快速冷却指示CI |
| 核心特征：多通道亮温差 | Bt13.4-Bt10.8, Bt12.4-Bt10.8 | [1][3] | 水汽和云相态指标 |
| 样本不平衡处理 | SMOTE / 加权损失 | [2] | 正样本稀少时使用 |
| 推荐训练/验证比例 | 70%/30% 或 80%/20% | [1][2] | 时间序列需按时间分割 |

## 边界与分流
- **样本量不足**（<1000 CI事件）：优先使用Random Forest或XGBoost，避免深度学习过拟合
- **计算资源有限**：使用传统ML而非DL，推理速度快10-100倍
- **可解释性要求高**：使用Random Forest + SHAP，避免黑盒DL模型
- **实时性要求高**（<1分钟推理）：使用轻量级模型（XGBoost）而非复杂DL

## 质量检查
- 模型必须在独立测试集上评估，不得使用训练集性能
- 必须报告POD、FAR、CSI三个指标，不能只报AUC
- 特征重要性分析必须通过物理一致性检查（如CTT应为正向重要特征）
- 模型性能必须与基线方法（如固定阈值法）对比

## 回退策略
- 若ML模型性能不达标：回退到物理阈值法作为基线
- 若训练数据质量差：使用数据增强或迁移学习
- 若模型过拟合：增加正则化、减少特征维度、增加训练数据

## 资源召回建议
- 当任务涉及CI检测方法选择时召回本卡片
- 配套资源：climate-ci-threshold-selection、climate-ci-validation-protocol

## 证据来源
[1] A Novel Framework of Detecting Convective Initiation Combining Automated Sampling and Machine Learning, Remote Sensing, 2019, DOI: 10.3390/rs11172057
[2] Convective Initiation Nowcasting in South China Using Physics-Augmented Random Forest, Earth and Space Science, 2024, DOI: 10.1029/2023EA003252
[3] Physically Explainable Deep Learning for Convective Initiation Nowcasting, AI for the Earth Sciences, 2024, DOI: 10.1175/aies-d-23-0098.1
[4] Toward a Deep-Learning-Network-Based Convective Weather Initiation Algorithm, IEEE JSTARS, 2023, DOI: 10.1109/JSTARS.2023.3310056
[5] Probabilistic Convective Initiation Nowcasting Using Himawari-8 AHI with Explainable Deep Learning, Monthly Weather Review, 2023, DOI: 10.1175/MWR-D-22-0165.1
[6] Bayesian Deep Learning for Convective Initiation Nowcasting Uncertainty Estimation, AI for the Earth Sciences, 2026, DOI: 10.1175/AIES-D-25-0098.1
