# 方案评估任务

## 适用范围
适用于钙钛矿太阳能电池钝化方案的优先级评估，包括多目标决策分析、敏感性分析。

## 输入
- 候选钝化方案列表（性能数据、成本、稳定性）
- 评估指标（PCE、Voc、FF、Jsc、稳定性、成本）
- 权重设置（各指标相对重要性）

## 输出
- 优先方案排序列表
- 敏感性分析结果
- 独立复核条件（独立计算验证、实验验证标准）
- PASS/REJECT/BLOCKED结论

## 操作步骤
1. 收集候选方案性能数据
2. 设计评估指标矩阵
3. 进行多目标决策分析（如TOPSIS、AHP）
4. 执行敏感性分析（权重变化对排序影响）
5. 制定独立复核条件
6. 生成优先方案列表和结论

## 输出产物
- `priority_ranking.csv`：优先方案排序
- `sensitivity_analysis.png`：敏感性分析图表
- `review_plan.md`：独立复核计划
- `conclusion.txt`：PASS/REJECT/BLOCKED结论

## 质量门禁
- 验证评估指标完整性
- 检查敏感性分析合理性
- 确认复核条件可操作性

## 回退策略
- 若评估指标不足，增加补充指标
- 若敏感性分析异常，调整权重范围
- 若复核条件不明确，参考国际标准

## 资源召回建议
- 当需要多目标决策分析方法时召回本任务
- 当需要敏感性分析方法时召回本任务
- 当需要独立复核标准时召回本任务

## 证据来源
[1] Understanding of Defect Passivation Effect on Wide Band Gap pin Perovskite Solar Cell, ACS Applied Materials & Interfaces, 2024, DOI: 10.1021/acsami.4c05838.s001