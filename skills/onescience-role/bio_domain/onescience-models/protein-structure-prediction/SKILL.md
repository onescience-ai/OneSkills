---
name: bio-protein-structure-prediction
description: OneScience 蛋白和复合物结构预测模型 skill。用于 AlphaFold、OpenFold、AlphaFold3、Protenix、SimpleFold 的推理、训练、微调、输入 JSON/FASTA/MSA/template/mmCIF、confidence、diffusion、Pairformer/Evoformer/StructureModule 等任务。
---

# OneScience 蛋白结构预测模型

## 模型分流

- `AlphaFold`：AF2-style JAX/Haiku 推理，FASTA + MSA/template feature pipeline。
  - 锚点：`examples/biosciences/alphafold`、`src/onescience/flax_models/alphafold`
- `OpenFold`：AF2-style PyTorch，训练/推理/微调，OpenFold batch dict。
  - 锚点：`examples/biosciences/openfold`、`src/onescience/models/openfold`
- `AlphaFold3`：AF3 JAX 生物分子结构预测，JSON、data pipeline、JackHmmer/MMseqs。
  - 锚点：`examples/biosciences/alphafold3/run_alphafold.py`
- `Protenix`：PyTorch AF3 风格复合物结构预测，可训练复现，Protenix/AF3 feature dict。
  - 锚点：`examples/biosciences/protenix/runner/inference_unified.py`、`src/onescience/models/protenix`
- `SimpleFold`：flow matching 折叠，FASTA 推理、mmCIF 数据处理、Torch/MLX 后端。
  - 锚点：`examples/biosciences/simplefold`、`src/onescience/models/simplefold`

## 输入协议检查

- AF2 路线：FASTA、MSA、template features。
- AF3/Protenix 路线：JSON、MSA、CCD/ligand、feature dict、diffusion sampling。
- OpenFold：OpenFold AF2 batch dict，不等于 Protenix feature dict。
- SimpleFold：FASTA 或 tokenized structure data、`feats` dict、flow matching 设置。

## 交接物

```yaml
bio_task_family: onescience-bio-model
onescience_model_family:
task_mode: inference | training | finetuning | module-change | debug
input_protocol:
input_files:
checkpoint_or_weight_source:
example_entry:
source_anchors:
coder_assets_to_read:
execution_entry: onescience-skill -> onescience-coder
```

## 禁止事项

- 不要只写“结构预测模型”，必须命名具体模型族。
- 不要把 AlphaFold3 JSON 直接传给 OpenFold。
- 不要把 Protenix 的 ligand/CCD/MSA 需求省略。
