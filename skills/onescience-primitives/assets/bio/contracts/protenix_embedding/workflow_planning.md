# description

该卡用于指导 agent 判断何时使用 Protenix embedding 组件族，以及如何在 Protenix 主模型、template 分支和 diffusion 条件中配置它。

# when_to_use

- 需要从 Protenix feature dict 构造 `s_inputs`。
- 需要在 recycling 中启用 template pair update。
- 需要为 diffusion noise level 生成 Fourier 条件。

# inputs

- Protenix feature dict 字段清单。
- `configs.c_s_inputs`、`c_token`、`c_z`。
- template 是否可用。
- diffusion noise embedding 维度。

# outputs

```text
component_choice:
  name: protenix_embedding
  style: ProtenixInputFeatureEmbedder | ProtenixTemplateEmbedder | ProtenixFourierEmbedding
  action: reuse | disable_template | adjust_dims | reject
```

# procedure

1. 判断场景是 input、template 还是 noise conditioning。
2. 校验 feature dict 字段和维度。
3. 对齐输出维度与 Protenix 主配置。
4. 小样本 forward 检查 `N_token`、`c_s_inputs`、`c_z`。

# constraints

不要把 ESM token、OpenFold batch 或普通坐标张量直接传入该组件。template 缺失时应允许分支返回 `0`，不要误判为模型失败。

# next_phase_recommendation

输入分支后接 `protenix_relative_position_encoding`、`protenix_msa` 和 `protenix_pairformer`；diffusion noise 分支后接 `protenix_diffusion`。

# fallback

字段缺失时回到 Protenix datapipe / adapter 检查；维度不一致时优先同步 `c_s_inputs` 与 input embedder 输出。
