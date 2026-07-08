# architecture_overview

Xihe 是面向全球海洋预报的带掩膜二维 patch 模型。主干先在原 patch 网格上融合，再下采样到低分辨率多次融合，随后上采样回原网格，并与早期特征拼接恢复。
它的核心差异是每个融合阶段都可以接收由海陆掩膜降采样得到的 `TensorWithMask`，用于在海洋有效区域内建模。

# parameter_scale

- 默认配置面向高分辨率海洋网格 `(2041, 4320)`。
- 默认 `embed_dim=192`，输入通道 96，输出通道 94。
- 主干包含 5 个 XiheFuser block、一次下采样、一次上采样和一个 skip 投影。
- 实际参数规模由配置对象覆盖的通道数和 embedding 宽度决定。

# architecture_structure

```text
配置与输入
  config.img_size   : 默认可为 (2041, 4320)
  config.patch_size : 默认可为 (6, 12)
  config.mask       : numpy 可读取的二维海陆掩膜路径
  x                 : (Batch, in_chans, Height, Width)

patch embedding
  x
    -> OneEmbedding(style="XiheEmbedding")
    -> (Batch, embed_dim, H', W')
    -> flatten + transpose
    -> (Batch, H' * W', embed_dim)

第一尺度掩膜融合
  mask_full
    -> change_mask(mask_full, h_out=H', w_out=W')
    -> mask1: (Batch, 1, H', W')

  TensorWithMask(x, mask1)
    -> block1: OneFuser(style="XiheFuser", dim=embed_dim, num_local=1)
    -> x1: (Batch, H' * W', embed_dim)

低分辨率融合
  x1
    -> PanguDownSample
    -> (Batch, H'/2 * W'/2, 2 * embed_dim)

  mask_full
    -> change_mask(mask_full, h_out=H'/2, w_out=W'/2)
    -> mask2

  TensorWithMask(x, mask2)
    -> block2
    -> block3
    -> block4
    -> (Batch, H'/2 * W'/2, 2 * embed_dim)

上采样与 skip 融合
  low-resolution feature
    -> XiheUpSample
    -> (Batch, H' * W', embed_dim)
    -> TensorWithMask(x, mask1)
    -> block5
    -> concat with x1 on channel dim
    -> skip_proj: 2 * embed_dim -> embed_dim

输出恢复
  projected feature
    -> transpose + reshape
    -> (Batch, embed_dim, H', W')
    -> OneRecovery(style="XihePatchRecovery")
    -> (Batch, out_chans, Height, Width)
```

# input_schema

- `x`: 通常为 `(Batch, in_chans, Height, Width)`。
- `config` 需要提供 `img_size`、`patch_size`、`mask`、`out_chans`、`in_chans`、`num_groups`、`embed_dim`。
- `mask` 指向可由 `numpy.load` 读取的二维海陆掩膜。

# output_schema

- 输出为二维海洋变量预测场，通道数由 `config.out_chans` 控制。
- 空间尺寸由 `XihePatchRecovery` 的实现与配置共同决定。

# shape_transformations

1. 输入经 patch embedding 得到 `(B, embed_dim, H', W')`。
2. flatten/transpose 为 `(B, H'*W', embed_dim)`。
3. 全分辨率 mask 聚合为 `(B,1,H',W')` 并随 TensorWithMask 传入 block。
4. 下采样至 `(H'/2, W'/2)` 级别，特征维变为 `2*embed_dim`。
5. 低分辨率 mask 聚合后执行三段融合。
6. 上采样回 `(H',W')`，特征维回到 `embed_dim`。
7. 与 block1 输出拼接为 `2*embed_dim`，再投影回 `embed_dim`。
8. reshape 回 `(B,embed_dim,H',W')` 并 patch recovery。

# key_dependencies

- `xiheembedding`
- `xihefuser`
- `pangudownsample`
- `xiheupsample`
- `xihepatchrecovery`
- `tensorwithmask`


# common_modification_points

- 修改 `config.in_chans/out_chans` 以适配不同海洋变量集合。
- 修改 `mask` 路径或 `change_mask` 聚合逻辑以适配不同海陆掩膜。
- 调整 `patch_size` 在高分辨率细节与计算开销之间折中。
- 调整 block 数或 `embed_dim` 改变模型容量。
- 可借鉴 Pangu 的下采样/上采样结构，但保留 Xihe 的海陆掩膜传递机制。

# implementation_risks

- 构造函数参数中同时存在默认值和 `config` 覆盖，实际以 `config` 为准。
- `mask_full` 通过路径加载，路径不存在或 shape 不匹配会失败。
- `change_mask` 使用 Python 循环聚合高分辨率掩膜，超大网格下可能较慢。
- 下采样时使用 `H_out // 2`、`W_out // 2`，奇数 patch 网格可能有边界风险。
- `OneFuser` 接收 `TensorWithMask`，替换 fuser 时需保持接口兼容。

# code_references

- `{onescience_path}/onescience/src/onescience/models/xihe/xihe.py`
- `{onescience_path}/onescience/src/onescience/modules/embedding/xiheembedding.py`
- `{onescience_path}/onescience/src/onescience/modules/fuser/xihefuse.py`
- `{onescience_path}/onescience/src/onescience/modules/fuser/xiheglobalsiefuser.py`
- `{onescience_path}/onescience/src/onescience/modules/fuser/xihelocalsiefuser.py`
- `{onescience_path}/onescience/src/onescience/modules/sample/pangudownsample.py`
- `{onescience_path}/onescience/src/onescience/modules/sample/xiheupsample.py`
- `{onescience_path}/onescience/src/onescience/modules/recovery/xihepatchrecovery.py`
