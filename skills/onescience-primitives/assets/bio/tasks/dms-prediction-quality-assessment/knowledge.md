# DMS Prediction Quality Assessment Standards

## 适用范围

本卡片定义蛋白变异效应预测结果（如 ESM-1v 零样本评分）与 DMS 实验数据对照时的质量评估标准，包括 Spearman 相关性阈值、统计显著性要求和预期性能范围。

## 输入

- 预测分数列：esm_score（或类似语言模型评分）
- 实验分数列：func_score（DMS 实验功能得分）
- 样本量：通常 >500 个突变

## 输出

- Spearman 相关系数（rho）及其 p 值
- 95% Bootstrap 置信区间
- 质量门禁判定：PASS / FAIL

## 流程节点

1. **数据对齐** → 确保预测分数与实验分数在同一突变集合上对齐
2. **Spearman 计算** → 使用 scipy.stats.spearmanr 计算 rho 和 p 值
3. **Bootstrap 置信区间** → 1000 次重采样计算 95% CI
4. **质量门禁** → 根据阈值判定结果是否可用

## 关键参数

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 显著性阈值 | p < 0.05 | [1] | 统计显著性最低要求 |
| 中等相关阈值 | rho > 0.3 | [1] | 中等以上相关性 |
| 强相关阈值 | rho > 0.5 | [1] | 强相关性 |
| ESM-1v 在 TEM-1 上预期 rho | 0.4 - 0.6 | [1][2] | 文献报道范围 |
| Bootstrap 次数 | 1000 | [1] | 95% CI 计算标准 |
| 最低样本量 | 500 | [2] | 保证统计功效 |

## 边界与分流

- **rho < 0.3 且 p > 0.05**：结果无统计学意义，标记 FAIL，不用于生物学解释
- **rho > 0.3 但 p > 0.05**：可能样本量不足，建议增加突变数量后重试
- **rho > 0.5 且 p < 0.05**：结果可用，标记 PASS
- **模拟数据结果**：无论 rho 值如何，一律标记模拟数据，不作为科学结论

## 质量检查

- 验证 p 值 < 0.05（或至少 < 0.1）
- 验证 rho > 0.3（中等以上相关性）
- 验证 Bootstrap 95% CI 下界 > 0
- 检查是否存在系统偏差（如所有突变评分方向一致）

## 回退策略

- 若 rho 低于阈值，检查：(a) 数据是否为真实 DMS 数据而非模拟数据；(b) 评分方法是否正确；(c) 突变集合是否匹配
- 若 p 值不显著，建议使用更大样本量或非参数检验

## 资源召回建议

- 在执行 TEM-1 DMS 评估步骤（s04）时召回本卡
- 配套资源：ESM-1v 模型卡（bio/models/esm1v-variant-effect-prediction）

## 证据来源

[1] Pejaver, V., Urresti, J., et al. "Enhancing missense variant pathogenicity prediction with protein language models", Human Mutation, 2024, DOI: 10.1038/s41431-024-01548-1
[2] Zheng, Y., Liu, T., et al. "VenusMutHub - A benchmark for protein mutation effect prediction", Acta Pharmaceutica Sinica B, 2025, DOI: 10.1016/j.apsb.2025.01.016
