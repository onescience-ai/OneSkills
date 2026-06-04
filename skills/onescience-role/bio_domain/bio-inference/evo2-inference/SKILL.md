---
name: bio-evo2-inference
description: Evo2 基因组语言模型推理 skill。用于执行 OneScience Evo2 的 DNA prompt、FASTA、predict、logits、序列生成或变异打分类推理，收紧 NeMo/Megatron checkpoint、tokenizer、seq_length、position_ids、loss_mask、FASTA seq_idx 映射、设备资源和输出校验。
---

# Evo2 推理

## 使用边界

用于基因组 DNA token 语言模型推理。它不是蛋白模型，不接受 FASTA 蛋白结构特征、AF2 batch 或 Protenix feature dict。

## 可复用资源

- `{onescience_path}/onescience/examples/biosciences/_manifests/model_requests/evo2_request.yaml`：prompt/FASTA、checkpoint、seq length、生成/打分参数和输出模板。
- `references/evo2_execution.md`：NeMo/Megatron、tokenizer、dataset 和输出检查。

## 推荐流程

1. 读模型卡：`onescience-coder/assets/models/evo2.md`。
2. 固定入口：`{onescience_path}/onescience/examples/biosciences/evo2/infer.py` 或 `predict.py`。
3. Preflight：checkpoint 目录、NeMo/Megatron 依赖、tokenizer、prompt/FASTA、seq length、GPU/DCU 资源。
4. 输入检查：DNA 字符、大小写策略、BOS/EOD、position ids、seq_idx map。
5. Postflight：logits 或生成序列、prompt 映射、序列长度、异常 token、输出文件。

## 交接物

```yaml
bio_task_family: bio-inference
selected_concrete_skill: evo2-inference
model_family: Evo2
inference_mode: prompt_or_fasta_or_variant_scoring
input_protocol: DNA_tokens
entrypoint:
checkpoint_dir:
seq_length:
tokenizer:
expected_outputs:
output_validation_plan:
execution_entry:
```

## 禁止事项

- 不要把 Evo2 当普通 PyTorch Transformer；attention mask 通常不按 Transformer 路线使用。
- 不要把蛋白 FASTA 或结构特征送入 Evo2。
- 不要忽略 NeMo/Megatron checkpoint 与脚本版本匹配。
