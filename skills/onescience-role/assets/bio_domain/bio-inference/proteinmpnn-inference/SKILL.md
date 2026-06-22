---
name: bio-proteinmpnn-inference
description: ProteinMPNN inverse folding 推理 skill。用于执行 OneScience ProteinMPNN 的 PDB 骨架到序列设计、score-only、conditional probabilities、fixed chains、fixed positions、tied positions、PSSM、omit AA 和 CA-only 推理，收紧 JSONL helper、chain_M、权重目录、采样温度和 FASTA/score 输出校验。
---

# ProteinMPNN 推理

## 使用边界

用于给已有骨架设计或打分序列。它不是结构预测模型。若上游骨架来自 RFdiffusion，先确认 PDB/链/残基编号，再进入本 skill。

## 可复用资源

- `{onescience_path}/onescience/examples/biosciences/_manifests/model_requests/proteinmpnn_request.yaml`：PDB、链、固定位置、采样温度、权重和输出模板。
- `references/proteinmpnn_execution.md`：helper JSON、CA-only、score-only 和约束检查。

## 推荐流程

1. 读模型卡：`onescience-coder/assets/models/proteinmpnn.md`。
2. 固定入口：`{onescience_path}/onescience/examples/biosciences/ProteinMPNN/protein_mpnn_run.py`。
3. Preflight：PDB backbone 是否含 N/CA/C/O，链 ID，设计链，固定位置，权重目录和模型名。
4. 如果有复杂约束，先生成 helper JSON：chain id、fixed positions、tied positions、PSSM、omit AA。
5. 运行：设置 `--sampling_temp`、`--num_seq_per_target`、`--batch_size`、`--seed`。
6. Postflight：FASTA 数量、score/probs、固定位置是否保持、设计链是否正确。

## 禁止事项

- 不要把 `chain_M` 与 padding mask 混用。
- CA-only 权重必须配套 `--ca_only` 和 CA-only 输入。
- 不要在 PDB 原子缺失或链名不明时直接设计。
