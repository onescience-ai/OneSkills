# launch

```sh
python {onescience_path}/onescience/examples/biosciences/alphafold/run_alphafold.py --fasta_paths input.fasta --output_dir outputs/alphafold --model_preset monomer --db_preset reduced_dbs --max_template_date 2024-06-01
```

# input_schema

准备 FASTA、数据库路径和 template/MSA 相关配置。模型内部需要 `aatype`、`residue_index`、`seq_mask`、`msa`、`msa_mask`、`deletion_matrix`、template 原子坐标与 mask 等 feature。monomer 与 multimer 的 feature 处理路径不同，不能混用。

# runtime_interfaces

- `RunModel.process_features`: 将 raw feature dict 转为模型可用 batch。
- `RunModel.predict`: 执行模型推理并返回结构和置信度结果。
- `get_confidence_metrics`: 从模型输出计算 ranking confidence 相关指标。

# main_functions

- `process_features`
- `predict`
- `init_params`
- `get_confidence_metrics`

# execution_resources

需要 JAX/Haiku 运行环境、AlphaFold 参数、序列数据库、MSA/template 搜索工具和足够内存。长序列、多模型、多 recycle 会显著增加显存和运行时间。

# operation_limits

`contract_only` 风险来自原始 contract：不要直接写成已可运行的 `OneTransformer(style="AlphaFoldJAXEvoformer")`。若缺少参数会随机初始化并产生 warning，不适合真实推理；relax 输出不是模型 raw output，应分开处理。
