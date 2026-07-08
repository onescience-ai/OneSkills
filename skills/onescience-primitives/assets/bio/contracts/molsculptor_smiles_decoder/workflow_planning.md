# description

用于规划分子 latent 到 SMILES token 的解码阶段，将条件表征转换为可枚举的小分子序列。

# when_to_use

- 已有图 latent 或扩散 latent。
- 任务需要输出 SMILES。
- 需要小分子候选枚举。

# inputs

- 条件 latent。
- 起始 token、mask、rope index。
- 词表和采样策略。

# outputs

- token logits。
- 解码策略建议。
- 后处理检查清单。

# procedure

1. 准备 BOS 起始序列和 mask。
2. 根据条件 latent 逐步或并行输出 logits。
3. 使用采样策略生成 token。
4. 反 tokenization 并做 SMILES 合法性过滤。

# constraints

- 不保证化学有效。
- 词表必须匹配。
- 不直接计算分子性质。

# next_phase_recommendation

将生成 SMILES 接入 RDKit 标准化、性质预测、docking 或多目标筛选。

# fallback

若生成无效率高，降低采样温度、使用 beam search 或增加约束过滤。
