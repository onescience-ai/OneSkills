# SHAP可解释性框架

## 适用范围

用于黑箱或半黑箱机器学习模型的事后解释（post-hoc interpretation），核心任务是**量化每个输入特征对单个预测的贡献值**，并据此构建全局特征重要性排序与特征交互效应图谱。典型触发条件包括：需要理解模型决策依据以建立物理或因果机制认知；需要向非技术利益相关者说明模型输出的合理性；需要检测模型是否捕获了领域预期的特征关系。

SHAP 值的核心优势在于满足局部准确性（Local Accuracy）、缺失性（Missingness）和一致性（Consistency）三项公理，使得特征归因在数学上唯一且公平。该方法在环境科学（气象特征对污染物浓度的驱动分析）、金融（信贷风险因子归因）、医疗（诊断模型的关键指标识别）等领域已有广泛应用。

## 输入

- **必需**：
  - 训练好的机器学习模型对象，推荐树模型（Gradient Boosted Regression Trees、XGBoost、LightGBM、Random Forest 等）以利用 TreeSHAP 高效算法；线性模型、深度神经网络等也可使用，但计算策略不同。
  - 需要解释的样本特征矩阵（特征列名、数值范围、缺失处理方式须与模型训练时一致）。
- **可选**：
  - 目标变量真实值（用于与模型预测对比，辅助解释质量评估）。
  - 特征的领域元数据（物理含义、单位、因果方向），用于解读 SHAP 依赖图时建立机制性认知。
  - 分组变量（如季节、区域），用于分层分析不同条件下特征归因的异质性。

## 输出

- **逐样本 SHAP 值矩阵**：行对应样本，列对应特征，每个单元格为该特征对该样本预测的贡献值（单位与目标变量一致）。所有特征的 SHAP 值之和等于模型预测值与基线预测值之差。
- **全局特征重要性**：通过对每个特征的 |SHAP| 值取平均得到，用于特征筛选或模型简化的依据。
- **SHAP 依赖图**：展示单个特征的 SHAP 值随特征值的变化趋势，揭示非线性关系与阈值效应。
- **SHAP 交互效应矩阵**：量化任意两个特征的成对交互贡献（例如，温度对 PM1 预测的贡献取决于风速的状态），可用于识别协同或拮抗效应。

## 流程节点

1. **环境准备与模型加载**：安装 `shap` Python 库，加载训练好的模型对象与待解释数据集。确认特征列顺序与训练数据一致。

2. **选择解释器**：根据模型类型选择最优解释器。
   - 树模型（GBRT、XGBoost、LightGBM、Random Forest）→ `shap.TreeExplainer`，利用 TreeSHAP 算法，时间复杂度为 O(TLD²)（T 为树数，L 为叶节点数，D 为最大深度），在大规模数据上可行。
   - 线性模型 → `shap.LinearExplainer`。
   - 深度神经网络或通用模型 → `shap.KernelExplainer`（基于采样的近似方法，计算成本显著更高）。
   ```python
   import shap
   explainer = shap.TreeExplainer(model)
   ```

3. **计算 SHAP 值**：调用解释器的 `shap_values()` 方法，返回逐样本逐特征的归因矩阵。
   ```python
   shap_values = explainer.shap_values(X)
   ```
   对于多分类任务，返回值为列表（每个类别一个矩阵）。

4. **全局特征重要性汇总**：对每个特征计算平均绝对 SHAP 值，按降序排列。
   ```python
   shap.summary_plot(shap_values, X, plot_type="bar")
   ```

5. **SHAP 依赖图绘制**：选择关键特征，绘制 SHAP 值 vs. 特征值的散点图，颜色编码第二个特征以识别交互效应。
   ```python
   shap.dependence_plot("feature_name", shap_values, X)
   ```

6. **交互效应分析**（可选）：计算成对交互值，用于识别特征间协同或拮抗作用。
   ```python
   shap_interaction_values = explainer.shap_interaction_values(X)
   ```

7. **结果解读与导出**：结合领域知识解读归因结果，导出 SHAP 值矩阵与可视化图表。

## 边界与分流

- **树模型 vs. 非树模型**：TreeSHAP 是精确且高效的；对于非树模型（如 SVM、神经网络），需使用 KernelSHAP 等采样近似方法，计算成本可能高出数个数量级。若模型为线性回归，SHAP 归因等价于系数乘以特征值，此时直接分析系数即可。
- **与部分依赖图（PDP）的区分**：PDP 展示特征的全局平均边际效应，不解释单个预测；SHAP 提供逐样本的局部归因。两者互补，PDP 适合整体趋势判断，SHAP 适合个体决策溯源。
- **与 LIME 的对比**：LIME 通过局部线性近似解释单个预测，SHAP 基于博弈论公理提供唯一解。SHAP 在理论完备性与全局一致性上优于 LIME，但计算成本通常更高。
- **与不纯度重要性（Impurity-based Feature Importance）的对比**：树模型内置的特征重要性基于不纯度减少，存在对高基数特征的偏好偏差；SHAP 基于预测值变化，归因更公平。

## 回退策略

- **计算超时或内存不足**：对于超大规模数据集（>10⁵ 样本），可采样部分数据计算 SHAP 值（通常 1000–5000 个样本即可获得稳定的全局重要性排序）；或使用 `shap.sample()` 对背景数据集进行聚类降采样以加速 KernelExplainer。
- **模型过拟合导致的解释偏差**：SHAP 值忠实解释模型的决策逻辑，若模型本身过拟合或未捕获真实关系，SHAP 输出的也是错误模式。此时应优先通过交叉验证、特征工程、正则化修正模型本身，再重新解释。
- **特征高度共线性**：当特征间存在强相关性时，SHAP 值在相关特征间的分配可能不稳定且不易直接解读。应对策略包括：（1）基于领域知识手动聚合或剔除冗余特征；（2）使用 SHAP 交互效应图区分独立贡献与交互贡献；（3）报告共线性诊断结果作为解释的前提说明。

## 资源召回建议

- **官方实现**：`shap` Python 库（https://github.com/slundberg/shap），支持 TreeSHAP、KernelSHAP、LinearSHAP 等多种解释器。
- **配套可视化库**：SHAP 内置 `summary_plot`、`dependence_plot`、`force_plot`、`waterfall_plot`、`interaction_plot` 等函数，可直接调用。
- **相关方法参考**：部分依赖图（PDP）、累积局部效应图（ALE）、LIME、反事实解释（Counterfactual Explanations），可根据具体解释目标组合使用。
- **加速技巧**：对于 XGBoost 模型，可设置 `model.predict(X, pred_contribs=True)` 直接输出 SHAP 值（内部使用 TreeSHAP），避免额外的 Python 层开销。
