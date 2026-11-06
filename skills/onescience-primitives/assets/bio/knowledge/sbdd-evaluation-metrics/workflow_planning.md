# 规划决策

## when to use

用于分子生成任务（对接打分由外部 soft 提供）时

## procedure

1. 【指标】QED（drug-likeness，RDKit，[0,1] 推荐≥0.4）、SA（合成可及性，≥0.5）
2. 【指标】对接分数：Vina Score / Vina Min / Vina Dock（可负；对生成任务 hit 用 ≤-8.18）
3. 【复合】Success Rate：同时满足 QED>0.25 & SA>0.59 & Vina Dock<-8.18 占比（BoN 论文定义）
4. 【复合】Hit Rate：QED≥0.4 & SA≥0.5 & VinaDock≤-8.18 占比（TAGMol 定义），Diversity、JSD 等辅助（§4.3）
5. 【对比】Baseline 对比注意：同分/同原子/same split 口径，与论文数值对齐（§4.5 Result）

## constraints

- 按 source_refs 回溯原始论文，避免断章。

## fallback

- 目标方法不满足条件时，退回生成式深度分子模型（targetdiff/genscore primitive）或咨询对应论文。