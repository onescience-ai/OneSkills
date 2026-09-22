# 多标签蛋白功能预测可解释性方法

## 适用范围
蛋白功能预测模型的解释与归因分析，用于识别哪些样本预测错误及错误原因；适用于需要输出残基、结构域或样本层解释的场景。

## 输入
- 训练好的蛋白功能预测模型
- 测试集样本（含序列、结构、GO注释）
- 解释方法配置（CAM/注意力/梯度/SHAP）

## 输出
- 样本层解释（样本ID、预测GO术语、归因得分）
- 残基层解释（功能重要残基识别）
- 预测错误分析报告（错误类型、原因、改进建议）

## 流程节点
1. 解释方法选择 → 根据模型架构选择合适的解释方法
2. 归因计算 → 计算每个样本/残基对预测的贡献
3. 结果聚合 → 将解释结果关联到原始样本ID和GO术语
4. 错误分析 → 识别预测错误样本并分析原因

每步含：操作、参数、工具、质量门禁

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| CAM方法 | Class Activation Mapping | [1] | 事后解释方法，识别功能重要残基 |
| 注意力可视化 | Transformer注意力权重 | [1] | 可视化模型关注的序列位置 |
| 梯度归因 | Integrated Gradients / Grad-CAM | [1] | 基于梯度的归因方法 |
| SHAP值 | SHapley Additive exPlanations | [2] | 基于博弈论的特征重要性 |
| 输出格式 | 样本ID + GO术语 + 归因得分 | [1] | 可追溯到原始样本 |

## 边界与分流
- 若模型不支持注意力机制 → 使用CAM或梯度归因方法
- 若计算资源有限 → 优先使用CAM（计算成本较低）
- 若需要精确归因 → 使用SHAP值（计算成本较高但更准确）

## 质量检查
- 验证解释输出是否包含样本ID、GO术语和归因得分
- 检查归因结果的合理性（正负贡献是否符合生物学直觉）
- 对比不同解释方法的结果一致性

## 回退策略
- 若首选解释方法失败 → 尝试备选方法
- 若计算资源不足 → 使用采样策略对部分样本进行解释
- 记录解释方法选择的原因和失败情况

## 资源召回建议
- 当需要分析模型预测错误原因时召回本卡
- 当需要输出样本层解释时召回本卡
- 配套资源：bio-protein-prediction-target-validation（预测目标验证）

## 证据来源
[1] GOBoost: leveraging long-tail gene ontology terms for accurate protein function prediction, Bioinformatics, 2025, DOI: 10.1093/bioinformatics/btaf267
[2] GOBeacon: An ensemble model for protein function prediction enhanced by contrastive learning, Protein Science, 2025, DOI: 10.1002/pro.70182