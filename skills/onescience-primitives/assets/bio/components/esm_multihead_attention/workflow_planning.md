# description

用于规划蛋白序列 transformer 中的多头注意力层，支持自注意力、交叉注意力和增量解码。

# when_to_use

- 构建 ESM 普通序列层或 inverse folding decoder。
- 需要 query/key/value attention。
- 输入为蛋白 hidden states。

# inputs

- hidden size、head 数和序列长度。
- attention mask、padding mask。
- 是否启用 rotary embedding 或增量缓存。

# outputs

- attention 配置。
- mask 组织方式。
- 与 transformer layer 的连接方式。

# procedure

1. 验证 hidden size 可被 head 数整除。
2. 选择 self/cross attention 模式。
3. 准备 mask 和可选 rotary embedding。
4. 将输出交给残差、归一化和 FFN。

# constraints

- 不处理 MSA 轴向拆分。
- 不直接输出接触图。
- 长序列有二次复杂度。

# next_phase_recommendation

继续接 ESM transformer layer 或 LM/contact heads；若是蛋白-配体任务，优先作为蛋白编码器上游特征。

# fallback

显存不足时缩短序列、减少 head/layer，或使用预计算 ESM embedding。
