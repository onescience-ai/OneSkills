# description

用于决定是否在 Protenix pair 初始化或 diffusion conditioning 中使用相对位置编码，以及如何检查 token 元信息。

# when_to_use

- 构造 Protenix `z_init`。
- 需要编码链、实体、对称拷贝和残基/token 相对关系。

# inputs

- token metadata 字段完整性。
- `N_token` 长度和显存预算。
- `r_max/s_max/c_z` 配置。

# outputs

```text
component_choice:
  name: protenix_relative_position_encoding
  action: reuse | fix_token_metadata | reduce_length | reject
```

# procedure

1. 检查 token 元信息字段是否齐全。
2. 确认每个字段 shape 与 `N_token` 对齐。
3. 估算 `N_token^2 * c_z` 内存。
4. 与 `z_init` 和 token bond projection 相加前检查 dtype/device。

# constraints

不能用普通 residue index 替代完整 token metadata；不能把 OpenFold residue features 直接当 Protenix token metadata。

# next_phase_recommendation

后续接 `protenix_msa` 和 `protenix_pairformer`，长序列任务优先规划 chunk 和低显存 attention。

# fallback

缺少 token metadata 时回到 Protenix JSON/datapipe 生成；显存不足时缩短输入、裁剪复合物或使用推理 chunk。
