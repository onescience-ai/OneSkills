---
name: bio-protein-design-generation
description: OneScience 蛋白设计和生成模型 skill。用于 RFdiffusion 骨架生成、motif scaffolding、binder design、partial diffusion、ProteinMPNN inverse folding、PT-DiT/ProToken 结构 token 和协同生成、SE3Transformer 内部等变模块任务。
---

# OneScience 蛋白设计与生成模型

## 模型分流

- `RFdiffusion`：骨架生成、motif scaffolding、binder design、对称设计、partial diffusion。
  - 输入：Hydra config、contig、input PDB、checkpoint。
  - 锚点：`examples/biosciences/RFdiffusion/scripts/run_inference.py`
- `ProteinMPNN`：backbone-to-sequence，固定链、固定位置、PSSM、tied positions、sampling temperature。
  - 输入：PDB backbone、chain masks、JSONL constraints。
  - 锚点：`examples/biosciences/ProteinMPNN/protein_mpnn_run.py`
- `ProToken`：结构 tokenization、VQ code、结构重建。
  - 输入：PDB-derived residue features、codebook/checkpoint。
  - 锚点：`src/onescience/flax_models/protoken`
- `PT-DiT`：ProToken + amino acid embedding 的 de novo design、RePaint、latent evolution。
  - 输入：ProToken/AA embeddings、diffusion config。
  - 锚点：`examples/biosciences/pt_dit/example_scripts`
- `SE3Transformer`：RFdiffusion 等变结构轨道内部组件。
  - 锚点：`src/onescience/models/se3_transformer`

## 链路规则

- RFdiffusion 生成骨架，不自动完成最终序列设计；需要设计序列时后接 ProteinMPNN。
- PT-DiT/ProToken 依赖结构 token 和 embedding 协议，不接受普通 FASTA 作为完整 batch。
- 只改 RFdiffusion 内部等变图层时才进入 SE3Transformer。

## 交接物

```yaml
bio_task_family: onescience-bio-model
design_stage: backbone-generation | inverse-folding | tokenization | latent-generation | module-change
onescience_model_family:
input_protocol:
constraint_spec:
checkpoint_or_weight_source:
example_entry:
source_anchors:
coder_assets_to_read:
execution_entry: onescience-skill -> onescience-coder
```

## 禁止事项

- 不要把 RFdiffusion 输出当作已完成序列设计。
- 不要把 ProteinMPNN 当结构预测模型。
- 不要绕过 ProToken checkpoint 和 codebook 协议。
