# description

用于规划 Protenix trunk 的 pair/single 更新，以及判断应使用 block 还是 stack。

# when_to_use

- Protenix 主干需要 token/pair 表征更新。
- MSA block 或 template embedder 需要纯 pair update。
- 需要配置 recycling 后的 trunk。

# inputs

- `s/z/pair_mask` shape。
- `c_s/c_z` 与模型配置。
- block 数、checkpoint、显存预算。

# outputs

```text
component_choice:
  name: protenix_pairformer
  action: main_stack | pair_only_block | template_stack | reject
```

# procedure

1. 判断是否需要 single branch。
2. 检查 `z` 二阶 shape 和 `c_z`。
3. 确认 `c_s=0` 或 `c_s>0` 场景。
4. 设置 block 数和 checkpoint。
5. 小样本验证输出 `s/z` shape。

# constraints

不要把 Pairformer 当作普通 Transformer；不要把天气 fuser 或 ESM transformer 替代该组件。

# next_phase_recommendation

主 trunk 输出进入 `protenix_diffusion` 和 confidence/distogram heads；MSA 分支输出继续进入主 PairformerStack。

# fallback

显存不足时减少 token、减少 block、启用 checkpoint 或低显存 attention。
