# 扩散模型奖励对齐与多目标选择（RAFT / Best-of-K / Best-of-N / DecompDiff 分解）

## scope

SBDD 分子生成；扩散模型的条件属性对齐（QED/SA/Vina 多目标）

## condition

需要对扩散生成模型做属性奖励对齐时使用；涉及可微/不可微奖励的区别

## 知识正文

- 【概念】RAFT 对齐目标 max_w E_{x~D}[r(x,y)]，每个输入 x 独立处理；奖励可任意可微组合（论文 §3）
- 【概念】Best-of-K（微调 top-K 子集）vs Best-of-N（免微调，采样 N 条取 reward 最优）的对比与适用场景（§5 / Table.3）
- 【流程】reward_ranking：QED/SA 用 RDKit 计算并归一化到[0,1]，Vina docking 分数 min-max 归一化后反转（越低越好），加权求和作为 reward（§3.3）
- 【约束】引导/奖励只支持可微属性；不可微属性（如任意打分项）只能用于 BoN 式选择，不能用于梯度引导
- 【概念】DecompBF 配体分解为 fragments（arms + scaffold，|A|>=1,|S|<=1），原子位置 MLE 先验增强扩散训练（§2）

## source_refs（可回溯）

| kid | uri | version | locator |
|---|---|---|---|
| KNOW-BD-005 | papers/2501.15631.pdf | v1 | §3 RAFT / Eq.2 |
| KNOW-BD-006 | papers/2501.15631.pdf | v1 | §5 Best-of-N Section + Table.3 |
| KNOW-P-BD-002 | papers/2501.15631.pdf | v1 | §3.3 / Data Ranking |
| KNOW-C-BD-001 | papers/2501.15631.pdf | v1 | §3.2 / 可微属性约束 |
| KNOW-BD-003 | papers/2501.15631.pdf | v1 | §2 Method / DecompDiff / Eq.1-3 |

## 来源条目原文（kid -> body）

### KNOW-BD-005 (concept)

> RAFT目标: max_w E_{x~D}[r(x,y)], 每个输入x独立处理, argmax reward的样本; 奖励r(x,y)可用任意可微组合属性(如QED/SA/亲和)。

### KNOW-BD-006 (concept)

> Best-of-K(BoK): 微调范式, 选出top-K样本用于对齐式微调(本文主要方法); Best-of-N(BoN): 免微调, 采样N个候选选奖励最高; BoN实现简单, BoK需额外调参但泛化更好; 两者可叠加, 权重(QED,SA,Vina)可调。

### KNOW-P-BD-002 (procedure)

> 排序: reward = w_QED·QED + w_SA·SA + w_Vina·Vina; QED/SA由RDKit计算并归一化[0,1]; Vina docking分数min-max归一化并反转(低更好); 选出最高reward样本与docking pose。

### KNOW-C-BD-001 (constraint)

> 约束: 引导/reward只支持可微属性(QED/SA/Vina对接打分均可微), 非可微属性(如通用二维穷举)不能直接用梯度引导, 只能用于BoN式选择。

### KNOW-BD-003 (concept)

> DecompDiff分解: 配体分成K个fragments: 若干arms A经至多一个scaffold S相连, |A|>=1,|S|<=1,K=|A|+|S|; 数据先验O_P={μ_1:K,Σ_1:K,H}由原子位置极大似然导出, 用于增强扩散训练。h种原子类型, 5类键。
