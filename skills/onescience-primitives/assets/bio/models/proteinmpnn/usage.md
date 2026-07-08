# launch

ProteinMPNN 用于给定蛋白骨架的序列设计、链级设计约束和候选序列打分。用户说“根据这个 backbone 设计序列”“RFdiffusion 生成骨架后补序列”“固定某些残基/链，只设计其他位置”“给 PDB 上的序列打分”时召回。

单个 PDB 设计示例：

```sh
cd "$ONESCIENCE_DIR" && python examples/biosciences/ProteinMPNN/protein_mpnn_run.py --pdb_path examples/biosciences/ProteinMPNN/inputs/PDB_monomers/pdbs/5L33.pdb --out_folder "$RUN_DIR/proteinmpnn_out" --num_seq_per_target 8 --sampling_temp 0.1 --seed 37 --batch_size 1 --model_name v_48_020 --path_to_model_weights "$ONESCIENCE_MODELS_DIR/ProteinMPNN/vanilla_model_weights"
```

指定设计链示例：

```sh
cd "$ONESCIENCE_DIR" && python examples/biosciences/ProteinMPNN/protein_mpnn_run.py --pdb_path "$RUN_DIR/backbone.pdb" --pdb_path_chains A --out_folder "$RUN_DIR/proteinmpnn_chain_A" --num_seq_per_target 16 --sampling_temp 0.1 0.2 --seed 37 --batch_size 1 --model_name v_48_020 --path_to_model_weights "$ONESCIENCE_MODELS_DIR/ProteinMPNN/vanilla_model_weights"
```

使用预解析 JSONL 与约束文件示例：

```sh
cd "$ONESCIENCE_DIR" && python examples/biosciences/ProteinMPNN/protein_mpnn_run.py --jsonl_path "$RUN_DIR/parsed_pdbs.jsonl" --chain_id_jsonl "$RUN_DIR/chain_id.jsonl" --fixed_positions_jsonl "$RUN_DIR/fixed_positions.jsonl" --out_folder "$RUN_DIR/proteinmpnn_constrained" --num_seq_per_target 8 --sampling_temp 0.1 --seed 37 --batch_size 1 --model_name v_48_020 --path_to_model_weights "$ONESCIENCE_MODELS_DIR/ProteinMPNN/vanilla_model_weights"
```

# input_schema

- 基础输入：PDB backbone 或已解析 JSONL、输出目录、模型权重目录、`model_name`、采样温度、每个目标生成序列数。
- PDB 输入：`--pdb_path` 指向单个结构；`--pdb_path_chains` 指定需要设计或处理的链。
- 批量/约束输入：`--jsonl_path`、`--chain_id_jsonl`、`--fixed_positions_jsonl`、`--tied_positions_jsonl`、`--omit_AA_jsonl`、`--pssm_jsonl` 等。
- 常用默认/显式参数：`model_name=v_48_020`，`batch_size=1`，`seed=37`，`sampling_temp=0.1`；`num_seq_per_target` 按候选规模设置。
- `chain_M` 表示设计 mask，不能理解为 padding mask；固定链和设计链必须按 ProteinMPNN helper JSON 语义生成。
- 智能体召回时建议记录：`usage_mode=sequence_design | constrained_design | score_only`，`entrypoint=protein_mpnn_run.py`，`input_artifacts=backbone_pdb | parsed_jsonl | constraints_jsonl`，`output_artifacts=fasta | score | probs`，`preflight_checks=pdb_chain_ids | fixed_positions | model_weights | output_folder`。

# runtime_interfaces

- `protein_mpnn_run.py`：主要 CLI，负责读取 PDB/JSONL、约束文件、模型权重并生成序列。
- `parse_multiple_chains.py`：把 PDB 目录转换为 ProteinMPNN JSONL。
- `assign_fixed_chains.py`：生成设计链/固定链配置。
- `make_fixed_positions_dict.py`：生成固定位置约束。
- `ProteinMPNN.forward`：模型前向，基于 backbone 几何预测氨基酸分布。

# main_functions

- `forward`
- `sample`
- `tied_sample`
- `conditional_probs`
- `unconditional_probs`

# execution_resources

- 推荐 GPU；小规模单个 PDB 可在较低资源下运行。
- 需要 ProteinMPNN 权重目录、结构输入、约束 JSONL 和可写输出目录。
- 输出通常包括 FASTA 序列、score 文件、可选 probability 文件；后续可进入 SimpleFold/OpenFold/ESMFold/Protenix 结构验证。
- 观察项应包含：FASTA 是否生成、序列数是否达到 `num_seq_per_target`、score/probs 是否可解析、失败是否来自 PDB 解析、链 ID、约束文件或权重路径。

# operation_limits

- ProteinMPNN 不生成 backbone；缺少骨架时应先召回 RFdiffusion 或使用已有/预测结构。
- ProteinMPNN 不预测结构置信度；序列设计后需要结构折叠和筛选。
- 输入 PDB 的链 ID、残基编号、缺失坐标和固定位置约束必须一致。
- 不把 DNA/RNA/配体作为 ProteinMPNN 设计对象；复合物结构验证应转 Protenix。
