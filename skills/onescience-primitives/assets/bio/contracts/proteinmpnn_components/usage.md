# launch

```sh
python {onescience_path}/onescience/examples/biosciences/ProteinMPNN/protein_mpnn_run.py --pdb_path input.pdb --out_folder outputs/proteinmpnn --num_seq_per_target 1 --sampling_temp 0.1
```

# input_schema

准备含主链 `N, CA, C, O` 的 PDB 或已 featurize 的 backbone batch。约束设计时通过 fixed chain、fixed position、omit AA、PSSM、tied positions 和 residue bias 等 helper JSON 表达。

# runtime_interfaces

- `ProteinFeatures`: 从 backbone 坐标构造几何图特征。
- `EncLayer`: 更新节点和边表征。
- `DecLayer`: 自回归序列解码。
- `sample` / `tied_sample`: 执行有约束采样。

# main_functions

- `forward`
- `sample`
- `tied_sample`
- `conditional_probs`
- `unconditional_probs`

# execution_resources

通常 GPU/CPU 均可小批量运行；批量 PDB、较大 `k_neighbors`、多 temperature 采样会增加内存和时间。

# operation_limits

`contract_only` 表示不可假设 `OneEncoder(style="ProteinMPNNFeatureEncoder")` 已可运行。`chain_M=1` 表示设计位置，不能和 padding mask 混用；缺主链原子会影响几何图。
