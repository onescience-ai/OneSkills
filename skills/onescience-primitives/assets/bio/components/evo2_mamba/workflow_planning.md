# description

该卡用于 Evo2 genome language model 的训练、推理和数据准备规划。

# when_to_use

- 用户任务涉及长基因组序列建模。
- 输入是 FASTA 或 genome token ids。
- 需要分析 Evo2 Mamba forward、tokenizer 或 prediction dataset。

# inputs

- FASTA 路径或 tokenized batch。
- tokenizer 配置。
- seq length、checkpoint、并行配置。
- 是否训练、微调或 prediction。

# outputs

- Evo2 数据入口建议。
- Mamba forward/loss 说明。
- 配置一致性检查。

# procedure

1. 确认任务是 genome LM，不是蛋白结构模型。
2. 使用 Evo2Tokenizer 构造 token ids。
3. prediction 可用 SimpleFastaDataset；训练需使用完整训练数据协议。
4. 检查 seq length、checkpoint 和并行配置。

# constraints

- 不把 FASTA prediction dataset 当完整 pretraining 数据协议。
- 不随意统一大小写而不检查 `to_upper`。
- 不用蛋白 MSA/PDB feature dict。

# next_phase_recommendation

推理任务交给 runtime 检查 NeMo/Megatron 环境；数据问题先做 FASTA 和 tokenizer 验证。

# fallback

若大模型依赖不可用，降级为 tokenizer/dataset 静态检查；若 checkpoint 不匹配，回退到示例配置。
