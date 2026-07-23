# architecture_overview

OpenFold 的公开模型类是 `onescience.models.openfold.model.AlphaFold`。它接受 dict-like config，根据 `config.globals.is_multimer` 与 `config.globals.seqemb_mode_enabled` 选择输入嵌入路径，再组合 recycling、template、Extra MSA、Evoformer、StructureModule 和辅助 heads。`forward` 原生支持 autograd，因而可以作为训练或推理模型调用。

# parameter_scale

- `AlphaFold(config)` 的通道、block 数、template/extra-MSA 开关和结构模块规模全部由 `config.model` 决定。
- `config.globals.is_multimer` 控制多聚体分支；`seqemb_mode_enabled` 控制 preembedding 分支。
- recycling 次数不是构造参数，而是 `batch["aatype"].shape[-1]`。
- 长序列优化、chunking 和 activation checkpointing 由配置及模型辅助方法控制。

# architecture_structure

```text
OpenFold feature dict with recycle dimension
  -> InputEmbedder / InputEmbedderMultimer / PreembeddingEmbedder
  -> RecyclingEmbedder
  -> optional TemplateEmbedder
  -> optional ExtraMSAStack
  -> EvoformerStack
  -> StructureModule
  -> auxiliary heads
```

除最后一轮 recycling 外，中间轮默认不保留梯度；最终结果再经过辅助 heads。

# input_schema

- `forward(batch: dict[str, Tensor])`。
- 每个输入 tensor 的最后一维是 recycling 维。
- 核心字段包括 `aatype`、`target_feat`、`residue_index`、`msa_feat`、`seq_mask`、`msa_mask`、`pair_mask`、`extra_msa_mask`。
- 启用 template 时还需要 `template_mask`、`template_aatype`、`template_all_atom_positions`、`template_all_atom_mask`、`template_pseudo_beta` 与 `template_pseudo_beta_mask`。

# output_schema

- 结构输出包含 `final_atom_positions`、`final_atom_mask`、`final_affine_tensor`。
- 表征输出包含 `msa`、`pair`、`single` 和 structure-module 输出 `sm`。
- `num_recycles` 记录实际轮数；存在 `asym_id` 时会透传。
- 辅助 heads 根据配置加入 distogram、predicted LDDT、masked MSA、PAE/TM 等结果。

# shape_transformations

1. 每轮从所有 batch tensor 的末维选取当前 recycle slice。
2. 输入嵌入产生 MSA `(B, N_seq, N_res, C_m)` 与 pair `(B, N_res, N_res, C_z)` 表征。
3. Evoformer 更新 MSA/pair 并产生 single `(B, N_res, C_s)`。
4. StructureModule 生成 atom37 坐标 `(B, N_res, 37, 3)` 及相关表示。
5. 最后一轮结果进入辅助 heads。

# key_dependencies

- `openfold_evoformer`
- `openfold_structure_module`

# common_modification_points

- 切换 monomer、multimer 或 seq embedding 时同步替换输入特征与配置。
- 修改 recycling 次数时修改 batch 末维，而不是为模型添加不存在的参数。
- 调整长序列内存时优先使用源码已有 chunking、inplace-safe 和 activation-checkpointing 机制。
- 训练代码在 forward 结果上组合损失；推理代码使用 `torch.no_grad()` 并解析输出字典。

# implementation_risks

- OpenFold batch 不是通用蛋白数据字典，缺失专用 feature 字段不能通过填充占位值解决。
- 所有 feature 的 recycling 末维必须一致。
- monomer/multimer/template 配置与特征协议不匹配会在嵌入阶段失败。
- 输出辅助字段随配置变化，后续代码不应假设所有 heads 始终存在。

# code_references

- `{onescience_path}/onescience/src/onescience/models/openfold/model.py`
- `{onescience_path}/onescience/src/onescience/models/openfold/embedders.py`
- `{onescience_path}/onescience/src/onescience/models/openfold/evoformer.py`
- `{onescience_path}/onescience/src/onescience/models/openfold/structure_module.py`
- `{onescience_path}/onescience/src/onescience/models/openfold/heads.py`
