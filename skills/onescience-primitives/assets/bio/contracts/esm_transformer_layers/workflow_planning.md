# description

用于规划 ESM 蛋白语言模型 trunk 层，决定采用普通序列 transformer 还是 MSA 轴向 transformer。

# when_to_use

- 需要从蛋白序列或 MSA 中提取上下文表征。
- 下游是 contact prediction、对接、设计或打分。
- 需要可复用 ESM 表征组件。

# inputs

- 输入类型：单序列或 MSA。
- hidden size、层数、head 数。
- mask 和 padding 策略。

# outputs

- 选用的 layer 类型。
- 资源预算。
- 下游 head 或模型的连接建议。

# procedure

1. 判断输入是单序列还是 MSA。
2. 单序列用 `TransformerLayer`，MSA 用 `AxialTransformerLayer`。
3. 对齐 mask 和位置编码。
4. 将输出交给 LM/contact head 或下游任务模型。

# constraints

- 不输出坐标。
- 不替代配体图网络。
- 长序列和大 MSA 需要显存预算。

# next_phase_recommendation

对 DiffDock/GenScore 这类蛋白-配体任务，优先输出蛋白 embedding；对 LaProteina，可作为序列表征或对照模块。

# fallback

若从头训练成本过高，直接使用预训练 ESM 模型生成 embedding。
