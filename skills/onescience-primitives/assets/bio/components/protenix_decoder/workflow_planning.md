# description

用于规划 Protenix diffusion 中 atom decoder 的使用，重点确认 skip 表征和 token-to-atom broadcast。

# when_to_use

- diffusion transformer 已输出 token latent。
- 需要从 token latent 生成 atom coordinate update。

# inputs

- `a` token latent。
- `q_skip/c_skip/p_skip`。
- `atom_to_token_idx`。
- local window 配置。

# outputs

```text
component_choice:
  name: protenix_decoder
  action: decode_atom_update | fix_skip_features | reject
```

# procedure

1. 检查 skip 表征是否来自同一个 atom encoder。
2. 校验 `atom_to_token_idx` 范围。
3. 对齐 `c_token` 和 local window。
4. 检查输出 `[..., N_atom, 3]`。

# constraints

不要在缺少 skip 表征时单独实例化 decoder；不要把输出当最终坐标。

# next_phase_recommendation

decoder 输出交回 `protenix_diffusion` 合成 denoised coordinates。

# fallback

skip 缺失时重新运行 atom encoder；维度错时同步 diffusion module 的 encoder/decoder 配置。
