# description

用于决定是否在 ESM attention 中启用旋转位置编码，以增强相对位置建模。

# when_to_use

- attention 配置声明使用 RoPE。
- 需要长序列或相对位置泛化能力。
- query/key head dimension 满足旋转要求。

# inputs

- head dimension。
- 序列长度。
- attention query/key tensor。

# outputs

- RoPE 启用建议。
- 缓存长度和维度检查结果。

# procedure

1. 检查 head dimension 是否可旋转拆分。
2. 根据序列长度准备 cos/sin 缓存。
3. 仅对 query/key 应用旋转。
4. 回到 attention kernel 继续计算。

# constraints

- 不应用于 value。
- 不替代绝对位置 embedding 的全部语义。
- 缓存与设备/精度需一致。

# next_phase_recommendation

若已启用 RoPE，继续调试 attention mask 和输出稳定性；否则保持原模型位置编码策略。

# fallback

如果 RoPE 造成 checkpoint 不兼容，关闭该选项并使用原始位置 embedding。
