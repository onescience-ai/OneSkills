# 规划决策

## when to use

需要对扩散生成模型做属性奖励对齐时使用；涉及可微/不可微奖励的区别

## procedure

1. 【概念】RAFT 对齐目标 max_w E_{x~D}[r(x,y)]，每个输入 x 独立处理；奖励可任意可微组合（论文 §3）
2. 【概念】Best-of-K（微调 top-K 子集）vs Best-of-N（免微调，采样 N 条取 reward 最优）的对比与适用场景（§5 / Table.3）
3. 【流程】reward_ranking：QED/SA 用 RDKit 计算并归一化到[0,1]，Vina docking 分数 min-max 归一化后反转（越低越好），加权求和作为 reward（§3.3）
4. 【约束】引导/奖励只支持可微属性；不可微属性（如任意打分项）只能用于 BoN 式选择，不能用于梯度引导
5. 【概念】DecompBF 配体分解为 fragments（arms + scaffold，|A|>=1,|S|<=1），原子位置 MLE 先验增强扩散训练（§2）

## constraints

- 按 source_refs 回溯原始论文，避免断章。

## fallback

- 目标方法不满足条件时，退回生成式深度分子模型（targetdiff/genscore primitive）或咨询对应论文。