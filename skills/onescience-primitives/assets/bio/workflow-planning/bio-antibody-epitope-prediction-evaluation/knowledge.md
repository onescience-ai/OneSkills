# 抗体结合位点预测的评估标准和最佳实践

## 适用范围
本知识适用于抗体结合位点预测模型的评估，特别是需要进行独立测试集评估和基线比较时。

## 输入
- 预测结果：模型预测的结合位点位置
- 真实标签：实验测定的结合位点位置
- 评估指标：AUPRC、AUROC、F1等
- 基线方法：Discotope-2、IEVpred等

## 输出
- 评估指标报告（AUPRC、AUROC、F1等）
- 分层性能分析（按抗原家族、抗体类型等）
- 基线比较结果
- 统计显著性检验结果

## 流程节点
1. **数据划分** → 划分独立测试集（按抗原家族分层）
2. **模型预测** → 在测试集上进行预测
3. **指标计算** → 计算AUPRC、AUROC、F1等指标
4. **基线比较** → 与Discotope-2、IEVpred等基线方法比较
5. **分层分析** → 按抗原家族、抗体类型等进行分层评估
6. **统计检验** → 进行统计显著性检验

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 核心指标 | 界面AUPRC | [论文1] | 抗体结合位点预测核心指标 |
| 测试集划分 | 按抗原家族分层 | [论文1] | 确保评估代表性 |
| 基线方法 | Discotope-2 | [论文1] | 经典结构预测方法 |
| 基线方法 | IEVpred | [论文1] | 界面预测方法 |
| 统计检验 | t-test/Mann-Whitney | [论文1] | 显著性检验 |

## 边界与分流
- **数据不平衡**：使用AUPRC而非准确率
- **测试集过小**：使用交叉验证
- **基线方法不可用**：使用其他基线方法
- **统计检验不显著**：增加数据量或调整模型

## 质量检查
- 验证测试集独立性（无数据泄露）
- 检查评估指标计算正确性
- 验证基线方法实现正确性
- 检查统计检验假设满足

## 回退策略
1. 使用其他评估指标（如AUROC、F1）
2. 使用其他基线方法
3. 使用交叉验证替代独立测试集
4. 报告评估局限性

## 资源召回建议
- 当任务需要评估模型性能时召回本卡片
- 当需要进行基线比较时召回本卡片
- 配套资源：bio-antibody-antigen-data-acquisition、bio-antibody-structure-prediction

## 证据来源
[1] BepiPred-2.0: improving sequence-based B-cell epitope prediction using conformational epitopes, Martin Closter Jespersen et al., Nucleic Acids Research, 2017, DOI: 10.1093/nar/gkx346
[2] Antibody Specific B-Cell Epitope Predictions: Leveraging Information From Antibody-Antigen Protein Complexes, Martin Closter Jespersen et al., Frontiers in Immunology, 2019, DOI: 10.3389/fimmu.2019.00298