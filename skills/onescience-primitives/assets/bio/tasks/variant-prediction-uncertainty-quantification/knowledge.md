# Variant Prediction Uncertainty Quantification

## 适用范围

本卡片描述蛋白语言模型（如 ESM-1v）在变异效应预测中量化不确定度的方法，适用于需要输出预测置信区间、可靠性评估和结果解释的任务。

## 输入

- 预测分数：每个突变的 esm_score
- 模型：已加载的 ESM-1v 或类似蛋白语言模型
- 突变集合：待评分的突变列表

## 输出

- 每个突变的 score_std（标准差）
- 95% 置信区间（ci_lower, ci_upper）
- 不确定度报告列

## 流程节点

1. **Bootstrap 采样** → 对突变集合进行 1000 次重采样
2. **多次推理** → 使用不同随机种子（如 0-4）重复推理
3. **模型集成** → 若有多个模型，取预测均值和标准差
4. **置信区间计算** → 使用分位数法计算 95% CI
5. **不确定度报告** → 在输出 CSV 中添加 score_std, ci_lower, ci_upper 列

## 关键参数

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| Bootstrap 次数 | 1000 | [1] | 标准重采样次数 |
| 随机种子数量 | 5 | [1] | 多次推理取均值 |
| 置信水平 | 95% | [1] | 标准置信区间 |
| 最低 CI 宽度 | 无固定阈值 | - | CI 越窄表示预测越可靠 |
| 不确定度来源 | 随机种子 + 采样 | [1] | 主要变异来源 |

## 边界与分流

- **CI 过宽**（>1.0）：预测不可靠，建议人工验证或使用其他方法
- **CI 与 0 重叠**：该突变效应不显著，标记为中性
- **计算资源不足**：可使用较少种子（如 3 次）或仅使用 Bootstrap 而非多次推理
- **模型集成不可用**：仅使用单模型 + 多种子方法

## 质量检查

- 验证 score_std 列存在且非零
- 验证 ci_lower < esm_score < ci_upper
- 验证 CI 宽度在合理范围内（通常 0.5-2.0）
- 检查不确定度是否与突变位置相关（活性位点通常不确定度更低）

## 回退策略

- 若不确定度计算失败，仅输出 point estimate（esm_score）并在报告中标注"无不确定度量化"
- 若计算资源不足，可减少 Bootstrap 次数至 100 次或种子数至 3 个

## 资源召回建议

- 在执行 TEM-1 DMS 评分步骤（s03）时召回本卡
- 配套资源：ESM-1v 模型卡（bio/models/esm1v-variant-effect-prediction）、质量评估卡（bio/tasks/dms-prediction-quality-assessment）

## 证据来源

[1] Chuang, K.V., Keiser, M.J. "Uncertainty quantification enables reliable deep learning for protein-ligand binding", Scientific Reports, 2025, DOI: 10.1038/s41598-025-89521-2
[2] Pejaver, V., Urresti, J., et al. "Enhancing missense variant pathogenicity prediction with protein language models", Human Mutation, 2024, DOI: 10.1038/s41431-024-01548-1
