---
name: bio-genome-language-modeling
description: OneScience Evo2 基因组语言模型 skill。用于 Evo2 训练、推理、微调、长序列 DNA token、OpenGenome2 数据、FASTA/JSON 预处理、NeMo/Megatron batch、checkpoint 转换、variant effect 和 genome design 任务。
---

# OneScience Evo2 基因组语言模型

## 使用边界

用于 Evo2 和基因组长序列建模。传统 variant calling 或 genome assembly 不进入本 skill，除非用户明确要用 Evo2 做建模或推理。

## OneScience 锚点

- `examples/biosciences/evo2/README.md`
- `examples/biosciences/evo2/infer.py`
- `examples/biosciences/evo2/train_one_node.py`
- `examples/biosciences/evo2/train_slurm.py`
- `examples/biosciences/evo2/tools/data_process`
- `src/onescience/models/evo2`

## 输入协议

- 训练/推理 batch 关注：`tokens`、`position_ids`、`labels`、`loss_mask`。
- 数据预处理关注：FASTA、JSON、tokenizer、sample length、mmap dataset。
- checkpoint 关注：Savanna/NeMo 格式、model size、ZeRO 转换、并行配置。

## 交接物

```yaml
bio_task_family: onescience-bio-model
onescience_model_family: Evo2
task_mode: inference | training | finetuning | checkpoint-conversion | data-preprocessing
input_protocol:
sequence_length:
tokenizer:
checkpoint_or_weight_source:
parallel_strategy:
source_anchors:
coder_assets_to_read:
execution_entry: onescience-skill -> onescience-coder
```

## 禁止事项

- 不要把普通 FASTA 读取输出直接当 Evo2 训练 batch。
- 不要忽略 tokenizer、sample length、label 和 loss mask。
- 不要把蛋白质结构 datapipe 复用于 Evo2。
