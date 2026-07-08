# component_info
将单个变量分支的中分辨率 token 序列与高分辨率 skip 特征解码为原始分辨率输出场。

补充说明：

- 该组件处理的是单个变量分支，不负责跨变量融合
- 内部使用 `EarthTransformer2DBlock`、`PanguUpSample` 和 `PanguPatchRecovery`
- 输入通常来自 `FengWuFuser` 的单分支切分结果和对应 encoder 的 skip 特征

该组件的核心实现包括 `FengWuDecoder`，定位为解码器，由上层 OneScience 模型或流水线通过 Python API 调用。

# purpose
将潜在表示恢复到目标网格、变量通道或图节点空间，适用于模型后段的结果重建。

# input_schema
- 2D 输入：
  - `inp[0]`: `(Batch, middle_resolution[0] * middle_resolution[1], 2 * dim)`
  - `inp[1]`: `(Batch, output_resolution[0], output_resolution[1], dim)`
- 3D 输入：`not_applicable`

内部统一做法：

- 先处理中分辨率 token 序列
- 上采样回高分辨率 token 网格
- 在高分辨率上继续做 2D Transformer
- 与 skip 特征拼接后恢复为原始分辨率场

# output_schema
- 2D 输出：`(Batch, out_chans, img_size[0], img_size[1])`
- 3D 输出：`not_applicable`

# parameters
- `output_resolution`
  - 高分辨率 patch 网格尺寸 `(Height, Width)`
- `middle_resolution`
  - 中分辨率 patch 网格尺寸 `(Height, Width)`
- `out_chans`
  - 输出变量通道数
- `img_size`
  - 原始输出场尺寸 `(Height, Width)`
- `patch_size`
  - patch 恢复尺寸 `(PatchHeight, PatchWidth)`
- `dim`
  - 高分辨率特征维度
- `depth`
  - 高分辨率 Transformer block 层数
- `depth_middle`
  - 中分辨率 Transformer block 层数
- `num_heads`
  - 若为二元组，顺序为 `(HighResolutionHeads, MiddleResolutionHeads)`
- `window_size`
  - 二维窗口大小
- `drop_path`
  - 可为单值或按层提供的序列

# key_dependencies
- `onedecoder`
- `onesample`
- `panguupsample`
- `onerecovery`
- `pangupatchrecovery`
- `onetransformer`
- `earthtransformer2dblock`
- `oneattention`
- `earthattention2d`

# usage_and_risks
- 该组件处理的是单个变量分支，不要把多个变量分支混在一起输入
- `num_heads` 二元组顺序是 `(高分辨率, 中分辨率)`
- `inp[1]` 是二维网格 skip 特征，不是展平 token 序列

# code_references
- `{onescience_path}/onescience/src/onescience/modules/decoder/fengwudecoder.py`
- `{onescience_path}/onescience/src/onescience/modules/decoder/onedecoder.py`
- `{onescience_path}/onescience/src/onescience/models/fengwu/fengwu.py`
