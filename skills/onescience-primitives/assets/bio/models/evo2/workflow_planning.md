# description

Evo2 规划知识用于基于 `MambaModel`、tokenizer、FASTA dataset 与 `mamba_forward_step` 构建基因组语言模型训练或推理代码。

# when_to_use

- 任务是 DNA/genome token 序列的 logits、生成或语言模型训练。
- 已有 Evo2/Mamba 配置与 checkpoint，需要复用源码模型。
- 训练数据可提供 tokens、position ids、labels 和 loss mask。
- 不用于直接处理未 tokenized 的 FASTA 字符串。

# inputs

- Mamba/Megatron 模型配置和匹配 checkpoint。
- tokenizer 与 vocabulary 配置。
- 推理张量 `input_ids`、`position_ids`，或训练 batch 的 `tokens`、`position_ids`、`labels`、`loss_mask`。
- sequence length、parallel runtime 与 inference context 设置。

# outputs

- `MambaModel` 或 `Evo2StyleMCoreMambaModel` 构建代码。
- 推理 logits/hidden output，或按 loss mask 计算的训练 loss。
- 数据字段、上下文长度和并行配置契约。

# procedure

1. 从 checkpoint 确定准确的模型配置、vocabulary 和并行布局。
2. 使用源码 tokenizer/FASTA dataset 构造 token 与 position tensors。
3. 推理时构建模型并可调用 `get_inference_wrapper`；无 labels 调用 `forward`。
4. 训练时构造四字段 batch，复用 `mamba_forward_step` 或等价参数映射。
5. 校验 logits/labels/loss_mask sequence shape 完全对齐。
6. 执行 checkpoint 加载、前向和最小 loss/logits 验证。

# constraints

- 训练和推理入口直接使用 `onescience.models.evo2` 的类与函数。
- 模型配置、tokenizer 和 checkpoint 必须属于同一规格。
- `decoder_input` 非空时 input ids/position ids 不参与 embedding。
- 不能只提高 inference wrapper 长度而忽略模型和并行内存限制。

# next_phase_recommendation

- 训练任务进入分布式 runtime 和 checkpoint 保存规划。
- 推理输出进入序列概率、生成或 embedding 后处理。
- 对新数据先验证 tokenizer round-trip 与 label offset。

# fallback

- 依赖版本不匹配时对齐 NeMo/Megatron/BioNeMo 环境。
- 显存不足时缩短 sequence、减小 micro batch 或采用 checkpoint 原生并行配置。
- loss 异常时先检查 labels 与 loss mask，不修改模型输出层。
