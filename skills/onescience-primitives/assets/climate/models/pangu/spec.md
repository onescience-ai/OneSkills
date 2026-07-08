# architecture_overview

Pangu 是 **canonical unified 3D trunk** 的全球天气预报模型。它将地表分支补成一个压力层位置，再与 13 层高空变量 patch token 拼接，形成统一三维大气网格。
主干不是 surface / upper-air 两套完全分离的 encoder，而是统一的 3D token trunk；surface patch token 先补一个 `PressureLevels=1`，再与 upper-air patch token 沿压力层维拼接。

补充说明：

- 本知识描述的是 **Pangu-Weather 原始/同构三维主干** 的内部契约。
- 它适用于“surface 与 upper-air 在进入主干前合并为统一 3D token 流”的实现。
- 若任务要求“保持 Pangu 外部 I/O，但替换内部 3D 主干为 2D 主干”，必须额外读取对应变体卡或 2D 主干组件卡，不能把本卡直接当作变体内部契约。

# parameter_scale

- 默认 `embed_dim=192`。
- 主干分四段，深度分别为 2、6、6、2。
- 默认注意力头为 `(6, 12, 12, 6)`。
- 默认高空变量为 5 类、13 个压力层；地表输入 7 通道，地表输出 4 通道。

# architecture_structure

```text
输入通道组织
  x: (Batch, 4 + 3 + 5 * 13, Height, Width)
    前 4 通道       -> 待预测 surface 变量
    接下来 3 通道   -> 静态 mask
    剩余 65 通道    -> upper-air 变量按 5 类 * 13 层展平

输入拆分
  SurfaceInput  : (Batch, 7, 721, 1440)
  UpperAirInput : (Batch, 5, 13, 721, 1440)

patch embedding
  SurfaceInput
    -> OneEmbedding(style="PanguEmbedding")
    -> (Batch, 192, 181, 360)
    -> unsqueeze(PressureLevels)
    -> (Batch, 192, 1, 181, 360)

  UpperAirInput
    -> OneEmbedding(style="PanguEmbedding")
    -> (Batch, 192, 7, 181, 360)

统一三维 token trunk
  concat on PressureLevels
    -> (Batch, 192, 8, 181, 360)
    -> flatten token
    -> (Batch, 8 * 181 * 360, 192)
    -> layer1: OneFuser(style="PanguFuser")
    -> 保存 SkipTokens
    -> downsample: (Batch, 8 * 91 * 180, 384)
    -> layer2: 深层三维融合
    -> layer3: 深层三维融合
    -> upsample: (Batch, 8 * 181 * 360, 192)
    -> layer4: 高分辨率三维融合

恢复头
  trunk 输出与 SkipTokens 拼接
    -> 通道维变为 384
    -> reshape 回 (Batch, 384, 8, 181, 360)
    -> pressure index 0      -> surface feature
    -> pressure index 1..end -> upper-air feature
    -> PanguPatchRecovery(surface)  -> (Batch, 4, 721, 1440)
    -> PanguPatchRecovery(upper)    -> (Batch, 5, 13, 721, 1440)
```

# input_schema

- `x`: `(Batch, 4 + 3 + 5 * 13, Height, Width)`。
- 前 4 通道为待预报地表变量。
- 接着 3 通道为静态掩码。
- 剩余 65 通道 reshape 为 `(Batch, 5, 13, Height, Width)`。
- 默认空间尺寸 `(721, 1440)`。

# output_schema

- 返回二元组 `(output_surface, output_upper_air)`。
- `output_surface`: `(Batch, 4, Height, Width)`。
- `output_upper_air`: `(Batch, 5, 13, Height, Width)`。

# shape_transformations

1. 输入按通道拆分为地表与高空。
2. 地表经二维 patch embedding 得到 `(B,C,Hp,Wp)`，再 unsqueeze 为压力层长度 1。
3. 高空经三维 patch embedding 得到 `(B,C,7,Hp,Wp)`。
4. 两者拼接为压力层长度 8 的三维特征。
5. reshape 为 token 序列后进入四段融合主干。
6. 主干输出与 skip token 拼接，通道变为 `embed_dim*2`。
7. 拆出压力层 0 作为地表，其余层作为高空。
8. patch recovery 恢复到目标物理场。
9. 若目标是 lite/shared-2D trunk 变体，本卡只能提供 family-level 输入输出语义与 canonical 3D 参考，不能直接替代变体自己的中间 rank 契约。

# key_dependencies

- `panguembedding`
- `pangufuser`
- `pangudownsample`
- `panguupsample`
- `pangupatchrecovery`

# common_modification_points

- 修改地表变量或静态掩码数量时，需要同步调整输入切片和 `patchembed2d`。
- 修改高空变量数或压力层数时，需要同步调整 reshape、`patchembed3d` 和 recovery。
- 调整 `patch_size` 和 `window_size` 可改变三维感受野与计算量。
- 可借鉴 FengWu 的多分支方式，将变量族分开编码再融合。
- 若仅替换内部 trunk 而保持外部 Pangu I/O，不应默认沿用本卡的统一 3D trunk 结构。

# implementation_risks

- 输入通道顺序强绑定切片逻辑。
- `patchrecovery2d/3d` 中 `img_size` 写死为 `(721,1440)` 与 `(13,721,1440)`，修改 `img_size` 时需同步改恢复层。
- 地表静态掩码只作为输入，不在输出中恢复。
- 压力层 patch 后长度与地表补层拼接逻辑必须保持一致。
- 常见误用是把本卡的统一 3D trunk 直接套用到 2D-lite 任务，导致错误保留 5D 中间特征或错误要求 trunk 接受 5D 输入。

# code_references

- `{onescience_path}/onescience/src/onescience/models/pangu/pangu.py`
- `{onescience_path}/onescience/src/onescience/modules/fuser/pangufuser.py`
- `{onescience_path}/onescience/src/onescience/modules/sample/pangudownsample.py`
- `{onescience_path}/onescience/src/onescience/modules/sample/panguupsample.py`
- `{onescience_path}/onescience/src/onescience/modules/recovery/pangupatchrecovery.py`
- `{onescience_path}/onescience/src/onescience/modules/embedding/panguembedding.py`
