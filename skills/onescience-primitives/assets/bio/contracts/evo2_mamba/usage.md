# launch

```sh
python {onescience_path}/onescience/examples/biosciences/evo2/train_one_node.py --config-name evo2_8b --trainer.devices 1 --model.seq_length 8192
```

# input_schema

准备 FASTA、Evo2Tokenizer、position ids、loss mask 和训练/推理脚本所需配置。prediction dataset 可由 `SimpleFastaDataset(fasta_path, tokenizer, prepend_bos=True)` 构造。

# runtime_interfaces

- `Evo2Tokenizer`: DNA 文本到 token ids。
- `SimpleFastaDataset.__getitem__`: 返回 prediction 样本。
- `MambaModel.forward`: 返回 logits 或 loss。
- `mamba_forward_step`: 训练 step 的 batch 入口。

# main_functions

- `forward`
- `mamba_forward_step`
- `__getitem__`
- `write_idx_map`

# execution_resources

依赖 NeMo、Megatron、BioNeMo 生态和大模型 checkpoint。长序列、pipeline 并行和 inference context 会影响显存与 logits 返回形态。

# operation_limits

`contract_only` 表示不可假设 `OneTransformer(style="Evo2Mamba")` 可运行。`attention_mask` 在 Mamba 路线中通常不按 Transformer mask 使用；大小写 reweighting 会影响 loss 语义。
