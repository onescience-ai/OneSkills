# launch

OpenFold 原语表示 PyTorch `AlphaFold` 完整结构预测模型。训练器和推理器都应从 OneScience 模型包构造该类，并向 `forward` 传入已经特征化且带 recycling 维度的 batch。

```sh
python -c "from onescience.models.openfold.model import AlphaFold; import inspect; print(inspect.signature(AlphaFold)); print(inspect.signature(AlphaFold.forward)); print(inspect.signature(AlphaFold.iteration)); print(inspect.signature(AlphaFold.embed_templates))"
```

# input_schema

- `config.globals` 控制 multimer、chunk、低内存注意力、offload、精度等全局行为；`config.model` 描述 embedding、Evoformer、structure module 和辅助头。
- batch 是张量字典，核心字段包括 `aatype`、`target_feat`、`residue_index`、`seq_mask`、`msa_feat`、`msa_mask`、`atom37_atom_exists`；模板、多聚体和 extra-MSA 模式有附加字段。
- 训练/推理 batch 的最后一维通常是 recycling iteration；特征维度必须与配置一致。
- 输出字典包含 `final_atom_positions`、`final_atom_mask`、`final_affine_tensor`、`msa`、`pair`、`single`、结构模块结果以及启用的辅助头预测。

# runtime_interfaces

- `AlphaFold(config)`：OpenFold 完整模型。
- `AlphaFold.forward(batch)`：执行 recycling、Evoformer、结构模块和辅助头。
- `InputEmbedder`/`InputEmbedderMultimer`、`EvoformerStack`、`StructureModule`：模型内部主要模块。
- `AuxiliaryHeads`：pLDDT、distogram、masked-MSA、experimentally-resolved 等训练/推理输出头。

# main_functions

- `AlphaFold.forward`
- `AlphaFold.embed_templates`
- `AlphaFold.iteration`
- `AuxiliaryHeads.forward`

# execution_resources

- 依赖 PyTorch 和 OpenFold 数据特征；完整预测通常还依赖外部生成的 MSA、模板及残基常量。
- 从 FASTA、MSA、template 或 mmCIF 构造训练/推理 feature dict 时，召回 datapipe 资源 `openfold_data_pipeline`。
- 长链和复合物需要 GPU/DCU；可通过 chunk、offload、低内存注意力和 recycling 次数调节资源占用。
- checkpoint 必须与 monomer/multimer、模型宽度和特征模式一致。

# operation_limits

- 模型不直接接受 FASTA 字符串或 PDB 文件，必须先构建符合 OpenFold 契约的特征字典。
- 缺少 MSA/模板时只能使用相应无模板或简化配置，不能伪造占位张量替代真实特征。
- `final_atom_positions` 是预测坐标，仍需结合 mask、置信度和链映射解释。
- 训练损失、优化器和数据采样不由 `AlphaFold.forward` 自动创建。
