# launch

Evo2 在 OneScience 中是基于 NeMo/Megatron Mamba 的基因组语言模型。训练和推理代码应直接构造 `MambaModel`，批处理适配使用 `mamba_forward_step`，checkpoint、tokenizer 和并行配置由调用方传入。

```sh
python -c "from onescience.models.evo2.models.mamba import MambaModel, mamba_forward_step; import inspect; print(inspect.signature(MambaModel)); print(inspect.signature(MambaModel.forward)); print(inspect.signature(MambaModel.get_inference_wrapper)); print(inspect.signature(mamba_forward_step))"
```

# input_schema

- `tokens`：整型 DNA token，形状通常为 `[batch, sequence_length]`。
- `position_ids`：与 `tokens` 同形状的位置编号。
- 训练还需要 `labels` 和 `loss_mask`；四个键必须同时出现在传给 `mamba_forward_step` 的字典中。
- 主要配置包括词表大小、隐藏维度、层数、状态空间参数、`sequence_length`，以及 tensor/pipeline/context parallel 大小。
- 推理输出为下一个 token 的 logits；带 `labels` 和 `loss_mask` 的训练调用返回模型计算的损失张量。
- DNA 字符表、大小写、BOS/EOD 与 padding 策略必须和 checkpoint 的 tokenizer 一致。

# runtime_interfaces

- `MambaModel`：NeMo `GPTModel` 兼容封装，负责模型构建、训练与推理。
- `MambaModel.forward(input_ids, position_ids, attention_mask=None, labels=None, ..., loss_mask=None)`：核心前向接口。
- `MambaModel.get_inference_wrapper(...)`：创建 Megatron 推理包装器。
- `mamba_forward_step(model, batch)`：把标准训练 batch 映射为模型参数。
- `Evo2Tokenizer` 与 FASTA 数据集接口负责 DNA 文本到 token batch 的转换。

# main_functions

- `mamba_forward_step`
- `MambaModel.forward`
- `MambaModel.get_inference_wrapper`

# execution_resources

- 依赖 PyTorch、NeMo、Megatron Core、BioNeMo 及与 checkpoint 匹配的 tokenizer。
- 长序列和大参数模型通常需要 GPU/DCU；并行组必须在构造模型前初始化。
- checkpoint 的模型规模、词表、序列长度和并行切分必须与配置一致。

# operation_limits

- 该模型只接受基因组/DNA token，不接受蛋白质 token、结构坐标或分子图。
- logits 和序列似然是模型分数，不等价于变异致病性、表达量或临床结论。
- 生成长度受训练上下文窗口和推理显存限制；不能在不匹配的 tokenizer 之间复用 token id。
