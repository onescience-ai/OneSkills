# 蛋白功能预测标签稀疏性处理策略

## 适用范围
多标签蛋白功能预测中，GO注释标签的长尾分布（标签稀疏性）问题；适用于处理高频广义术语与低频特异性术语的不平衡。

## 输入
- GO注释数据集（含标签频率分布）
- 标签信息内容（IC）值
- 模型训练配置

## 输出
- 标签分布分析报告（高频/低频/稀疏类别统计）
- 长尾优化策略配置
- 分层F1分析结果

## 流程节点
1. 标签分布分析 → 统计各GO术语的出现频率和IC值
2. 长尾类别识别 → 识别IC > 10的稀疏类别
3. 优化策略选择 → 选择合适的长尾优化方法
4. 性能验证 → 验证优化策略对稀疏类别的改善效果

每步含：操作、参数、工具、质量门禁

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| IC阈值 | IC > 10为稀疏类别 | [1] | 信息内容衡量GO术语特异性 |
| 长尾优化方法 | 长尾优化集成策略 | [1] | GOBoost提出的方法 |
| 损失函数 | 多粒度焦点损失（Multi-grained Focal Loss） | [1] | 为长尾标签分配更高权重 |
| 集成策略 | GOBoostHead + GOBoostTail + GOBoostAll | [1] | 三个基础模型集成 |
| 全局-局部标签图 | 捕捉高频和低频标签的共现关系 | [1] | 动态学习标签关系 |

## 边界与分流
- 若标签分布相对均匀 → 使用标准BCE损失即可
- 若存在严重长尾分布（如3627 GO terms中3337类<10样本） → 必须使用长尾优化策略
- 若计算资源有限 → 优先使用focal loss（成本较低）

## 质量检查
- 验证稀疏类别的F1提升（GOBoost在IC > 10组AUPR提升52.48%）
- 检查整体性能是否因长尾优化而下降
- 对比优化前后的分层F1分析

## 回退策略
- 若长尾优化效果不佳 → 尝试其他策略（如过采样、欠采样）
- 若集成策略成本过高 → 使用单一基础模型+焦点损失
- 记录长尾优化策略的选择原因和效果

## 资源召回建议
- 当发现宏平均F1极低（如<0.1）且存在标签稀疏时召回本卡
- 当需要处理GO注释的长尾分布时召回本卡
- 配套资源：bio-protein-prediction-target-validation（预测目标验证）

## 证据来源
[1] GOBoost: leveraging long-tail gene ontology terms for accurate protein function prediction, Bioinformatics, 2025, DOI: 10.1093/bioinformatics/btaf267
[2] GOBeacon: An ensemble model for protein function prediction enhanced by contrastive learning, Protein Science, 2025, DOI: 10.1002/pro.70182