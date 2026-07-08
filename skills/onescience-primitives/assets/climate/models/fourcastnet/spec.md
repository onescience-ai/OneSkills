# architecture_overview

FourCastNet 是二维 patch 预测模型，核心思想是在 patch 网格上做频域混合，再恢复为完整气象场。
输入不包含压力层维度，主干不是注意力 Transformer，而是 AFNO 频域混合加逐位置前馈网络。关键调用约定是 embedding 输出展平 token 序列，进入 trunk 前必须恢复为二维 patch 网格。

# parameter_scale

- 默认输入尺寸 `(720, 1440)`，patch `(8, 8)`，patch 网格为 `90 x 180`。
- 默认 `in_chans=19`，`out_chans=19`，`embed_dim=768`，`depth=12`。
- 默认 AFNO 分块数 `num_blocks=8`。
- 参数主要集中在 patch embedding、12 层 fuser 与线性恢复头。

# architecture_structure

```text
输入通道组织
  x: (Batch, Channels, Height, Width)
    默认 Channels=19
    默认 Height=720, Width=1440

二维 patch embedding
  x
    -> OneEmbedding(style="FourCastNetEmbedding", patch_size=(8, 8), embed_dim=768)
    -> (Batch, 16200, 768)

位置编码与网格恢复
  patch tokens
    -> + pos_embed: (1, 16200, 768)
    -> dropout
    -> reshape
    -> (Batch, 90, 180, 768)

AFNO patch-grid trunk
  (Batch, 90, 180, 768)
    -> OneFuser(style="FourCastNetFuser") block 1
       内部: FourCastNetAFNO2D + FourCastNetFC
    -> FourCastNetFuser block 2
    -> ...
    -> FourCastNetFuser block 12
    -> (Batch, 90, 180, 768)

patch 输出头与恢复
  trunk 输出
    -> linear head
    -> (Batch, 90, 180, out_chans * 8 * 8)
    -> einops.rearrange
    -> (Batch, out_chans, 720, 1440)
```

# input_schema

- `x`: `(Batch, in_chans, Height, Width)`。
- 默认 `Height=720`，`Width=1440`。
- `Height` 和 `Width` 应能被 patch 尺寸整除，以避免 token 与恢复网格不一致。

# output_schema

- 输出：`(Batch, out_chans, Height, Width)`。
- 输出网格由 patch 恢复得到，不额外插值。

# shape_transformations

1. 输入 `(B,C,H,W)`。
2. patch embedding 得到 `(B, num_patches, embed_dim)`。
3. 加位置编码并 dropout。
4. reshape 为 `(B, H/ph, W/pw, embed_dim)`。
5. 逐层 fuser 保持 patch 网格尺寸。
6. 线性头输出 `(B, H/ph, W/pw, ph*pw*out_chans)`。
7. 重排为 `(B,out_chans,H,W)`。

# key_dependencies

- `fourcastnetembedding`
- `fourcastnetfuser`
- `fourcastnetafno`
- `fourcastnetfc`

# common_modification_points

- 修改 `in_chans/out_chans` 支持不同变量集合。
- 修改 `patch_size` 在分辨率、速度和局地细节之间折中。
- 调整 `depth`、`embed_dim`、`mlp_ratio` 改变模型容量。
- 调整 `num_blocks`、`sparsity_threshold`、`hard_thresholding_fraction` 影响频域混合行为。
- 可借鉴 Fuxi 添加时间 patch 维度，支持多历史步输入。

# implementation_risks

- 位置编码长度与 patch 数必须一致，变更分辨率需重建或插值位置编码。
- `rearrange` 假设 patch 网格严格匹配输入尺寸。
- AFNO 稀疏阈值过高可能损失小尺度天气信号。
- 当前模型不显式建模压力层或变量族结构。
- `embed_dim` 必须能被 AFNO 的 `num_blocks` 整除。

# code_references

- `{onescience_path}/onescience/src/onescience/models/fourcastnet/fourcastnet.py`
- `{onescience_path}/onescience/src/onescience/modules/fuser/fourcastnetfuser.py`
- `{onescience_path}/onescience/src/onescience/modules/afno/fourcastnetafno.py`
- `{onescience_path}/onescience/src/onescience/modules/embedding/fourcastnetembedding.py`
- `{onescience_path}/onescience/src/onescience/modules/fc/fourcastnetfc.py`
