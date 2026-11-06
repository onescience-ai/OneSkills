# SBDD 生成/属性评估指标

## scope

分子生成场景指标口径（QED/SA/Vina/Success/Hit 率）的定义

## condition

用于分子生成任务（对接打分由外部 soft 提供）时

## 知识正文

- 【指标】QED（drug-likeness，RDKit，[0,1] 推荐≥0.4）、SA（合成可及性，≥0.5）
- 【指标】对接分数：Vina Score / Vina Min / Vina Dock（可负；对生成任务 hit 用 ≤-8.18）
- 【复合】Success Rate：同时满足 QED>0.25 & SA>0.59 & Vina Dock<-8.18 占比（BoN 论文定义）
- 【复合】Hit Rate：QED≥0.4 & SA≥0.5 & VinaDock≤-8.18 占比（TAGMol 定义），Diversity、JSD 等辅助（§4.3）
- 【对比】Baseline 对比注意：同分/同原子/same split 口径，与论文数值对齐（§4.5 Result）

## source_refs（可回溯）

| kid | uri | version | locator |
|---|---|---|---|
| KNOW-TM-007 | papers/2406.01650.pdf | v1 | §4.3 Metrics |
| KNOW-TM-008 | papers/2406.01650.pdf | v1 | §4.5 Result |

## 来源条目原文（kid -> body）

### KNOW-TM-007 (concept)

> 指标: QED, SA, Diversity(Tanimoto), 键长分布JSD; 对接: Vina Score/Min/Dock; Hit标准: QED>=0.4, SA>=0.5, Vina Dock<=-8.18。

### KNOW-TM-008 (example)

> 结果: TAGMol在V/SA QED分别提高, Vina Score较SOTA平均改善22%, 高亲和率69.8%, 多目标时同时提升。消融: 单目标+多目标均提升。
