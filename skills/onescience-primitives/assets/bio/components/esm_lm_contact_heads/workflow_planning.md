# description

用于规划 ESM 输出阶段的 token 预测和接触预测头，帮助判断是否需要语言模型监督或 contact map 辅助信息。

# when_to_use

- 需要 masked amino acid 预测。
- 需要基于 attention map 估计 residue contact。
- 需要评估或解释 ESM 表征。

# inputs

- hidden states 或 attention maps。
- tokens、padding、BOS/EOS 配置。
- 词表大小和特殊 token 编号。

# outputs

- LM logits 或 contact probabilities。
- head 连接方式。
- 特殊 token 裁剪策略。

# procedure

1. 若目标是 token 概率，选择 LM head。
2. 若目标是 contact map，准备 attention maps 和 tokens。
3. 校准 BOS/EOS/padding 裁剪。
4. 将输出用于评估或下游特征。

# constraints

- contact head 依赖 attention maps。
- LM head 依赖词表权重。
- 不输出 docking affinity。

# next_phase_recommendation

contact map 可作为结构先验；LM logits 可用于序列质量评估或突变打分。

# fallback

若 attention map 不可用，改用外部结构预测或预训练 contact predictor。
