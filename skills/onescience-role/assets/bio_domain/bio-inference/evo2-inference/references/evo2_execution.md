# Evo2 执行要点

Evo2 基于 NeMo/Megatron Mamba 路线。`MambaModel.forward` 使用 `input_ids`、`position_ids`、可选 `labels/loss_mask`。FASTA 推理可走 `SimpleFastaDataset`，输出可用 `seq_idx_map.json` 追溯序列。

推理前确认：

- checkpoint 目录是 Evo2 NeMo/Savanna 对应格式。
- 输入是 DNA 序列或已明确的 genome tokens。
- 序列长度不超过配置和显存可承受范围。
- 不复用 ProteinMPNN/AF2/AF3 的任何特征协议。
