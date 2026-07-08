# architecture_overview

Fuxi 是时空 patch 编码加二维主干恢复模型。它把多个历史时间步压入一个 patch token 表示，使后续主干只处理二维空间网格。
它不是 Pangu 式三维 token 主干，也不是 FourCastNet 式单时刻二维输入；其核心是先用三维 patch embedding 将时间维压缩到 1，再交给二维 U 形 trunk。

# parameter_scale

- 默认输入尺寸 `(2, 721, 1440)`，默认 patch `(2, 4, 4)`。
- 默认输入/输出通道均为 70。
- 默认 `embed_dim=1536`，主干注意力头数为 8。
- 参数规模主要由 embedding、FuxiTransformer 和 patch 恢复全连接层决定。

# architecture_structure

```text
输入张量组织
  x: (Batch, in_chans, TimeSteps, Height, Width)
    默认 in_chans=70
    默认 TimeSteps=2
    默认 Height=721, Width=1440

三维时空 patch embedding
  x
    -> OneEmbedding(style="FuxiEmbedding", patch_size=(2, 4, 4), embed_dim=1536)
    -> (Batch, 1536, 1, 180, 360)

时间维压缩
  embedding 输出要求 TimeSteps' = 1
    -> squeeze(TimeSteps')
    -> (Batch, 1536, 180, 360)

二维 U 形 trunk
  (Batch, 1536, 180, 360)
    -> FuxiDownSample
    -> (Batch, 1536, 90, 180)
    -> SwinTransformerV2Stage / FuxiTransformer 主体
    -> FuxiUpSample
    -> (Batch, 1536, 180, 360)

patch 级输出恢复
  trunk 输出
    -> permute 为逐位置特征
    -> OneFC(style="FuxiFC")
    -> (Batch, 180, 360, out_chans * 4 * 4)
    -> patch 重排
    -> (Batch, 70, 720, 1440)
    -> F.interpolate(..., mode="bilinear")
    -> (Batch, 70, 721, 1440)
```

# input_schema

- `x`: `(Batch, in_chans, TimeSteps, Height, Width)`。
- `img_size=(TimeSteps, Height, Width)`。
- `patch_size=(PatchTimeSteps, PatchHeight, PatchWidth)`。
- 当前实现要求 `PatchTimeSteps == TimeSteps`。

# output_schema

- 输出：`(Batch, out_chans, Height, Width)`。
- 输出为空间二维场，不保留时间维。

# shape_transformations

1. 输入 `(B, C_in, T, H, W)`。
2. `FuxiEmbedding` 输出 `(B, embed_dim, 1, H/ph, W/pw)`。
3. squeeze 时间维得到 `(B, embed_dim, H/ph, W/pw)`。
4. 二维 Transformer 输出同分辨率特征。
5. 全连接映射为每个 patch 的像素与变量通道。
6. reshape 为 `(B, out_chans, H_patch, W_patch)`。
7. 插值到 `img_size[1:]`。

# key_dependencies

- `fuxiembedding`
- `fuxitransformer`
- `fuxidownsample`
- `fuxiupsample`
- `fuxifc`


# common_modification_points

- 修改 `img_size` 和 `patch_size` 以支持不同历史窗口和空间分辨率。
- 若需要保留多个未来时间步，应改造 `fc` 输出和 reshape 逻辑。
- 调整 `embed_dim`、`num_heads`、`window_size` 可改变容量和局部注意力范围。
- 可借鉴 FourCastNet 的二维 token 处理方式替换主干，也可借鉴 Pangu 引入三维压力层维度。

# implementation_risks

- 当前强约束 `patch_size[0] == img_size[0]`，否则初始化直接抛错。
- `Height // PatchHeight` 与 `Width // PatchWidth` 使用整除，非整除网格可能丢失边界信息。
- `F.interpolate` 会掩盖 patch 恢复尺寸与目标尺寸不一致的问题，应在训练配置中显式校验。
- `embed_dim=1536` 对显存和吞吐要求较高。

# code_references

- `{onescience_path}/onescience/src/onescience/models/fuxi/fuxi.py`
- `{onescience_path}/onescience/src/onescience/modules/transformer/fuxitransformer.py`
- `{onescience_path}/onescience/src/onescience/modules/embedding/fuxiembedding.py`
- `{onescience_path}/onescience/src/onescience/modules/sample/fuxidownsample.py`
- `{onescience_path}/onescience/src/onescience/modules/sample/fuxiupsample.py`
- `{onescience_path}/onescience/src/onescience/modules/fc/fuxifc.py`
