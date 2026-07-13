# launch

```sh
python -c "from onescience.modules import OneMSA; m=OneMSA(style='ProtenixMSAModule', n_blocks=4, c_m=64, c_z=128, c_s_inputs=449, msa_configs={'enable': True, 'strategy': 'random'}); print(type(m).__name__)"
```

# input_schema

输入 MSA 已经是 Protenix feature dict 中的 tensor，不是 A3M 文件路径或 MSA dataclass。调用前应由 datapipe/featurizer 生成 `msa/has_deletion/deletion_value`。

# runtime_interfaces

- `OneMSA(style="ProtenixMSAModule", ...)`
- `ProtenixMSAModule.forward(input_feature_dict, z, s_inputs, pair_mask, ...)`

# main_functions

- `forward`
- `chunk_forward`
- `inference_forward`
- `one_hot_fp32`

# execution_resources

显存与 MSA 行数、token 数、pair 表征大小强相关；推理大样本路径会主动清理 CUDA cache。

# operation_limits

不做 MSA 搜索；缺少 MSA 会返回原 `z`；MSA 类别数和 deletion 字段必须符合 Protenix featurizer 协议。
