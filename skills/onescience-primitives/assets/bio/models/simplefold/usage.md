# launch

SimpleFold 用于蛋白 FASTA 的快速单序列结构折叠和设计候选初筛。用户说“快速预测这些蛋白序列结构”“不用完整 MSA/template，先筛一下 ProteinMPNN 设计序列”“用 SimpleFold 生成 PDB 和 pLDDT”时召回。

CLI 推理示例：

```sh
cd "$ONESCIENCE_DIR/examples/biosciences/simplefold" && python -c "from simplefold.cli import main; main()" --simplefold_model simplefold_100M --ckpt_dir "$ONESCIENCE_MODELS_DIR/simplefold" --num_steps 500 --tau 0.01 --nsample_per_protein 1 --plddt --fasta_path "$RUN_DIR/simplefold_fasta_inputs" --output_dir "$RUN_DIR/simplefold_out" --backend torch --output_format pdb
```

# input_schema

- 输入对象：蛋白 FASTA 文件或目录、SimpleFold checkpoint 目录、输出目录、模型规模、采样步数、温度、每条序列采样数和后端。
- FASTA header 应能追踪候选来源；来自 ProteinMPNN 的批量候选建议使用稳定序列 ID。
- 常用默认/显式参数：`simplefold_model=simplefold_100M`，`num_steps=500`，`tau=0.01`，`nsample_per_protein=1`，`backend=torch`，`output_format=pdb`。
- `--plddt` 用于输出置信度；批量初筛可先降低 `num_steps`，高价值候选再用 OpenFold 或 Protenix 复核。
- SimpleFold 输入是氨基酸序列，不接受 RFdiffusion backbone 作为直接输入；骨架需先经 ProteinMPNN 转为序列。
- 智能体召回时建议记录：`usage_mode=fast_structure_prediction | design_screening`，`entrypoint=simplefold CLI | inference.py`，`input_artifacts=fasta | fasta_dir`，`output_artifacts=pdb | plddt`，`preflight_checks=fasta_validity | checkpoint_dir | output_dir | backend`。

# runtime_interfaces

- `simplefold.cli.main`：CLI 入口，可通过 `python -c "from simplefold.cli import main; main()"` 调用。
- `inference.py`：示例推理脚本，适合按 FASTA 文件或目录批量生成结构。
- `SimpleFold.sample`：执行结构采样。
- `SimpleFold.forward`：模型前向计算。

# main_functions

- `forward`
- `sample`

# execution_resources

- 推荐 GPU；短序列和小批量可用于快速初筛。
- 需要 SimpleFold checkpoint、FASTA 输入、可写输出目录；部分配置可能依赖 ESM 表征或模型 token/atom 特征。
- 输出通常为 PDB 和 pLDDT/置信度信息；用于快速过滤明显不可折叠候选。
- 观察项应包含：输出 PDB 数量、pLDDT 是否生成、序列是否被跳过、失败是否来自 FASTA 格式、checkpoint、后端或显存。

# operation_limits

- SimpleFold 不替代 OpenFold 的完整 MSA/template 协议；高价值候选应做更严格结构验证。
- 不用于蛋白-核酸-配体复合物预测；复合物任务召回 Protenix。
- 不生成骨架和序列设计；骨架生成用 RFdiffusion，序列设计用 ProteinMPNN。
- 长序列、大批量或低置信度结果需要拆分批次、调整步数或换用更合适模型复核。
