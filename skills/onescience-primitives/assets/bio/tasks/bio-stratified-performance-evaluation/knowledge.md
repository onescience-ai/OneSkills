# Stratified Performance Evaluation for DNA Language Models

## 适用范围
用于评估DNA语言模型在不同子集上的性能表现，识别模型的优势和劣势领域。

## 输入
- 模型预测结果
- 真实标签数据
- 分层维度信息

## 输出
- 分层性能报告
- 模型适用域分析

## 流程节点
1. 分层维度定义：定义分层维度（染色体/基因、物种、细胞类型、变异类别）
2. 数据分层：按维度对数据进行分层
3. 指标计算：按维度分别计算性能指标（AUC-ROC、Accuracy、Pearson Correlation等）
4. 报告生成：生成分层性能报告
5. 分析解读：分析模型在不同子集上的表现差异

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 分层维度 | 染色体/基因、物种、细胞类型、变异类别 | [1] | 多维度分层 |
| 评估指标 | AUC-ROC、Accuracy、Pearson Correlation | [1] | 多种指标 |
| 报告格式 | 结构化报告 | [1] | 包含多维度性能指标 |

## 边界与分流
- 如果某些维度数据不足，可跳过该维度或使用聚合数据
- 评估指标需根据任务类型选择

## 质量检查
- 检查分层报告是否包含多个维度的性能指标
- 验证是否提供了模型适用域分析
- 检查指标计算是否正确

## 回退策略
- 分层维度数据不足时，可使用其他维度替代
- 指标计算失败时，可使用其他评估指标

## 资源召回建议
- 当需要评估DNA语言模型在不同子集上的性能时召回本卡片
- 配套资源：BEND_tasks数据集、DNABERT-2模型、Caduceus模型

## 补充证据（开源文档/用户自有，可选）
无

## 证据来源
[1] A comprehensive survey of genome language models in bioinformatics, Liu Shu, Jiao Tang, Xiaoyu Guan, Briefings in Bioinformatics, 2025, DOI: 10.1093/bib/bbaf724