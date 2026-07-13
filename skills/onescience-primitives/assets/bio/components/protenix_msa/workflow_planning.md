# description

用于规划 Protenix recycling 中 MSA 分支是否启用、如何采样和如何控制显存。

# when_to_use

- Protenix 输入中存在 MSA 特征。
- 需要利用 MSA 更新 pair representation。
- 需要设置 train/test MSA cutoff。

# inputs

- `input_feature_dict` 中 MSA 字段。
- `msa_configs`。
- `N_msa`、`N_token`、显存预算。

# outputs

```text
component_choice:
  name: protenix_msa
  action: enable | bypass_no_msa | reduce_msa_cutoff | reject
```

# procedure

1. 检查 MSA 字段是否存在且维度足够。
2. 确认 `msa_configs` 是 dict。
3. 设置 train/test cutoff 和 min_size。
4. 估算 MSA 与 pair 表征显存。
5. 与 Pairformer 输出 shape 对齐。

# constraints

不要把原始 A3M 路径直接传给该模块；不要把通用 amino acid one-hot 当作 Protenix MSA token。

# next_phase_recommendation

MSA 更新后接 `protenix_pairformer`；显存紧张时先调 cutoff、chunk 和 checkpoint。

# fallback

无 MSA 时允许 bypass；字段错误时回到 Protenix datapipe/msa_featurizer 重新生成。
