# 蛋白功能预测目标与GO标签类型对应关系验证

## 适用范围
蛋白功能预测任务中，验证预测目标类型（continuous/binary/multi-label）与GO注释标签类型的兼容性；适用于所有基于GO注释的蛋白功能预测场景。

## 输入
- GO注释数据集（含标签格式信息）
- 模型配置文件（含预测目标类型设置）
- 损失函数配置

## 输出
- 预测目标类型与标签类型兼容性验证结果
- 不兼容时的修正建议
- 验证日志

## 流程节点
1. 标签类型检测 → 分析GO注释数据的标签格式（one-hot、多标签二值等）
2. 预测目标匹配 → 验证模型预测目标类型与标签类型是否兼容
3. 损失函数验证 → 确认损失函数与预测目标类型匹配
4. 语义冲突检查 → 检查是否存在continuous目标与binary标签的冲突

每步含：操作、参数、工具、质量门禁

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| GO子本体 | MF（分子功能）、BP（生物过程）、CC（细胞组分） | [1] | GO三大分类 |
| 标签类型 | 多标签二值（multi-label binary） | [1] | 每个蛋白可对应多个GO术语 |
| 推荐预测目标 | multi-label 或 binary | [1] | 与GO标签类型一致 |
| 激活函数 | sigmoid（多标签）或 softmax（单标签） | [1] | 输出层激活函数 |
| 损失函数 | BCE（Binary Cross Entropy） | [1] | 多标签分类标准损失 |

## 边界与分流
- 若标签为多标签二值类型而目标设为continuous → 存在语义冲突，必须修正
- 若标签为连续值（如置信度分数）而目标设为binary → 需要离散化处理
- 若不确定标签类型 → 默认按multi-label处理，并在报告中标注

## 质量检查
- 验证模型损失函数与预测目标类型匹配
- 检查输出层激活函数与标签类型兼容
- 验证训练过程中损失值收敛情况

## 回退策略
- 发现类型不匹配时，修改模型预测目标类型
- 若无法修改模型，调整标签格式以匹配预测目标
- 记录类型不匹配的原因和修正方案

## 资源召回建议
- 当执行蛋白功能预测任务前需要验证配置时召回本卡
- 当发现训练目标与标签类型不一致时召回本卡
- 配套资源：bio-protein-label-sparsity-handling（标签稀疏性处理）

## 证据来源
[1] GOBeacon: An ensemble model for protein function prediction enhanced by contrastive learning, Protein Science, 2025, DOI: 10.1002/pro.70182
[2] GOBoost: leveraging long-tail gene ontology terms for accurate protein function prediction, Bioinformatics, 2025, DOI: 10.1093/bioinformatics/btaf267