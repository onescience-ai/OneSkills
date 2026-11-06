# 使用方式

## 何时召回

需要对扩散生成模型做属性奖励对齐时使用；涉及可微/不可微奖励的区别

## 如何使用

- KNOW-BD-005：reward_alignment_objective（concept）
- KNOW-BD-006：best_of_k_vs_best_of_n（concept）
- KNOW-P-BD-002：reward_ranking（procedure）
- KNOW-C-BD-001：reward_differentiability（constraint）
- KNOW-BD-003：decompdiff_decomposition（concept）

## 局限性 / 注意

- 知识来自论文实现对目标的归纳；实际任务须按自身数据与工具链验证。
- 本卡仅作知识承载，不执行安装/运行；环境与资源由 installer/runtime 处理。
- 与既有 molecule/diffusion primitive（如 targetdiff）配合使用时，以其 spec 为准。