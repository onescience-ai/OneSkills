# architecture_overview

FengWu 是一个面向全球中期天气预报的多分支编码-融合-解码模型。主模型为 `Fengwu`，以地表变量和五类高空变量为独立分支，先在各自二维空间内编码，再把六个变量族作为三维变量轴送入统一融合器。
它最重要的结构特点是多分支 2D encoder/decoder 加一个中分辨率 3D fuser：变量族不在输入端直接拼成单一路径，而是在中分辨率 token 层面执行跨变量融合。

# parameter_scale

- 默认 `embed_dim=192`，编码后中分辨率特征维度为 `embed_dim * 2`。
- 默认包含 6 个编码器、1 个跨变量融合器、6 个解码器。
- 默认高空压力层数为 `pressure_level=37`，每个高空变量分支输出 37 个通道。
- 主干深度由各 `OneEncoder`、`OneFuser`、`OneDecoder` 的内部实现决定，源码中使用 8 段 drop path 配置。

# architecture_structure

```text
输入分支组织
  surface: (Batch, 4, Height, Width)
    4 个地表预报变量
  z: (Batch, pressure_level, Height, Width)
    位势高度变量族，默认 pressure_level=37
  r: (Batch, pressure_level, Height, Width)
    相对湿度变量族，默认 pressure_level=37
  u: (Batch, pressure_level, Height, Width)
    纬向风变量族，默认 pressure_level=37
  v: (Batch, pressure_level, Height, Width)
    经向风变量族，默认 pressure_level=37
  t: (Batch, pressure_level, Height, Width)
    温度变量族，默认 pressure_level=37

独立二维 encoder
  surface
    -> OneEncoder(style="FengWuEncoder", in_chans=4)
    -> feature_surface: (Batch, 91 * 180, 384)
    -> skip_surface   : (Batch, 181, 360, 192)

  z / r / u / v / t
    -> 各自的 OneEncoder(style="FengWuEncoder", in_chans=pressure_level)
    -> feature_*: (Batch, 91 * 180, 384)
    -> skip_*   : (Batch, 181, 360, 192)

跨变量三维融合
  concat on Variables
    -> (Batch, 6, 91 * 180, 384)
    -> flatten token
    -> (Batch, 6 * 91 * 180, 384)
    -> OneFuser(style="FengWuFuser", input_resolution=(6, 91, 180))
    -> (Batch, 6 * 91 * 180, 384)
    -> reshape by Variables
    -> surface/z/r/u/v/t feature branches

分支解码与输出
  [feature_surface, skip_surface]
    -> OneDecoder(style="FengWuDecoder", out_chans=4)
    -> surface: (Batch, 4, 721, 1440)

  [feature_z, skip_z] / [feature_r, skip_r] / [feature_u, skip_u] / [feature_v, skip_v] / [feature_t, skip_t]
    -> 各自的 OneDecoder(style="FengWuDecoder", out_chans=pressure_level)
    -> z/r/u/v/t: (Batch, 37, 721, 1440)
```

# input_schema

- `surface`: `(Batch, 4, Height, Width)`。
- `z`: `(Batch, pressure_level, Height, Width)`。
- `r`: `(Batch, pressure_level, Height, Width)`。
- `u`: `(Batch, pressure_level, Height, Width)`。
- `v`: `(Batch, pressure_level, Height, Width)`。
- `t`: `(Batch, pressure_level, Height, Width)`。
- 默认空间尺寸为 `(721, 1440)`，默认 `patch_size=(4, 4)`。

# output_schema

- 返回六元组：`(surface, z, r, u, v, t)`。
- 每个输出与对应输入分支保持相同的变量通道与空间尺寸。

# shape_transformations

1. 每个二维输入分支经编码器从原始分辨率变为 patch token。
2. 编码器内部形成 `input_resolution=(ceil(H/ph), ceil(W/pw))` 与 `middle_resolution=(ceil(input_h/2), ceil(input_w/2))`。
3. 六个分支特征堆叠为 `(Batch, Variables=6, NumTokensPerVariable, Channels)`。
4. reshape 为 `(Batch, Variables * NumTokensPerVariable, Channels)` 后送入三维融合器。
5. 融合后再拆回六个分支，并与各自 skip 特征一起送入解码器。
6. 解码器恢复到原始二维网格。

# key_dependencies

- `fengwuencoder`
- `fengwufuser`
- `fengwudecoder`
- `panguembedding`
- `pangudownsample`
- `panguupsample`
- `pangupatchrecovery`

# common_modification_points

- 调整 `pressure_level` 以适配不同气压层集合。
- 修改地表或高空变量分支时，需要同步调整编码器输入通道、融合器变量轴长度和解码器输出通道。
- 修改 `patch_size` 可改变 token 数量和计算开销。
- 调整 `window_size` 与 `num_heads` 可改变跨变量融合感受野。
- 可借鉴 Pangu 的单流拼接方式，将多分支输入合并为统一 token 流，但会牺牲 FengWu 当前按变量族建模的清晰边界。

# implementation_risks

- 六个分支的 token 数量必须一致，否则融合前 concat/reshape 会失败。
- `img_size` 与 `patch_size` 使用 `ceil` 推导分辨率，恢复阶段需要确认边界填充或裁剪逻辑符合数据网格。
- 高空变量通道必须等于 `pressure_level`，否则分支编码器输入不匹配。
- 修改变量数时若只改输入不改 `FengWuFuser` 的 `input_resolution=(6, ...)`，会导致三维融合器形状错误。

# code_references

- `{onescience_path}/onescience/src/onescience/models/fengwu/fengwu.py`
- `{onescience_path}/onescience/src/onescience/modules/encoder/fengwuencoder.py`
- `{onescience_path}/onescience/src/onescience/modules/fuser/fengwufuser.py`
- `{onescience_path}/onescience/src/onescience/modules/decoder/fengwudecoder.py`
- `{onescience_path}/onescience/src/onescience/modules/embedding/panguembedding.py`
- `{onescience_path}/onescience/src/onescience/modules/sample/pangudownsample.py`
- `{onescience_path}/onescience/src/onescience/modules/sample/panguupsample.py`
- `{onescience_path}/onescience/src/onescience/modules/recovery/pangupatchrecovery.py`
