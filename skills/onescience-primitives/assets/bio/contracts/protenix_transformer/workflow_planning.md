# description

用于规划 Protenix diffusion 中 token transformer 和 atom local transformer 的选择与配置。

# when_to_use

- diffusion module 需要更新 token latent。
- atom encoder/decoder 需要局部 atom query 更新。
- 需要 conditioned transition。

# inputs

- `a/s/z` 或 `q/c/p` shape。
- `c_a/c_s/c_z/c_atom/c_atompair`。
- local window 参数。
- checkpoint 配置。

# outputs

```text
component_choice:
  name: protenix_transformer
  action: token_diffusion_stack | atom_local_transformer | transition_block | reject
```

# procedure

1. 判断 token 还是 atom local 场景。
2. 校验输入张量最后维和 local window。
3. 对齐 encoder/decoder/diffusion 参数。
4. 设置 checkpoint 和 drop path。

# constraints

不要把 atom local `p` 当作 global pair `z`；不要期待该组件直接输出坐标。

# next_phase_recommendation

token transformer 后接 `protenix_decoder`；完整 denoising 使用 `protenix_diffusion`。

# fallback

local window 不匹配时回到 atom encoder 生成 `p`；显存不足时减少 block 或启用 checkpoint。
