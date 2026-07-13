# launch

```sh
python -c "from onescience.modules import OneEncoder; enc=OneEncoder(style='ProtenixRelativePositionEncoding', r_max=32, s_max=2, c_z=128); print(type(enc).__name__)"
```

# input_schema

输入应来自 Protenix datapipe / feature dict，必须包含 token 级 `asym_id/residue_index/entity_id/sym_id/token_index`，且各字段最后一维长度都等于 `N_token`。

# runtime_interfaces

- `OneEncoder(style="ProtenixRelativePositionEncoding", ...)`: 统一入口。
- `forward(input_feature_dict)`: 返回 pair 相对位置编码。

# main_functions

- `forward`

# execution_resources

主要消耗内存来自 `[..., N_token, N_token, c_z]`，长 token 推理路径会使用 chunk 化投影降低峰值显存。

# operation_limits

不读取 atom 坐标，也不替代 pairformer。缺少 `token_index` 或链实体 ID 语义错误时，模块可运行但结果语义错误。
