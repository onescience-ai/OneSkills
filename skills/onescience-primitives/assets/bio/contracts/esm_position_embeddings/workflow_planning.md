# description

用于规划蛋白序列表征中的位置编码选择，在 ESM 风格模型或需要 protein token position 的任务中作为前置 embedding 组件。

# when_to_use

- 需要构建或改造 ESM 序列模型。
- 需要为 DiffDock/LaProteina 等蛋白任务补充序列表征候选。
- 输入是蛋白 token 序列而非三维坐标或分子图。

# inputs

- token 序列长度和 padding 规则。
- embedding dimension。
- 是否需要支持超过训练长度的长序列。

# outputs

- 位置编码组件选择建议。
- learned 或 sinusoidal 的使用边界。
- 与 token embedding/transformer 的连接方式。

# procedure

1. 确认输入是否为蛋白 token 序列。
2. 若长度固定且有 checkpoint，优先匹配 learned embedding。
3. 若需要外推长序列，优先考虑 sinusoidal embedding。
4. 检查 padding_idx 和 position id 是否一致。

# constraints

- 不处理 residue 坐标。
- 不生成语义 token embedding。
- learned embedding 受最大位置表限制。

# next_phase_recommendation

下一步连接 ESM transformer layer，或直接复用预训练 ESM hidden states 给对接、设计或打分模型。

# fallback

若位置表不匹配，退回 sinusoidal embedding；若序列长度超出模型能力，截断、分块或改用支持长序列的表征模型。
