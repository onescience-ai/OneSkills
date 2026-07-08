# component_info
在二维特征图上执行 Fuxi 的 U 形 trunk 特征提取。

补充说明：

- 输入是二维特征图，不是展平 token 序列
- 内部结构为 `FuxiDownSample -> SwinTransformerV2Stage -> FuxiUpSample`
- 中间会通过 skip connection 将下采样输出与 trunk 输出拼接

该组件的核心实现包括 `FuxiTransformer`，定位为Transformer 模块，由上层 OneScience 模型或流水线通过 Python API 调用。

# purpose
使用注意力或窗口注意力对 token 序列建模，适用于 FuXi/FengWu 等天气预测主干。

# input_schema
- 2D 输入：`(Batch, embed_dim, Height, Width)`
- 3D 输入：`not_applicable`

内部统一做法：

- 先下采样到较低分辨率网格
- 对不整除窗口大小的 trunk 网格先做 ZeroPad
- `SwinTransformerV2Stage` 输出后做中心 crop
- 与下采样输出拼接后再上采样回原分辨率

# output_schema
- 2D 输出：`(Batch, embed_dim, Height, Width)`
- 3D 输出：`not_applicable`

明确约束：

- 输出 shape 与输入 shape 保持一致
- `input_resolution` 指的是下采样后的 trunk 网格尺寸，不是输入特征图尺寸

# parameters
- `embed_dim`
  - 输入与输出特征通道数
- `num_groups`
  - 采样模块 `GroupNorm` 分组数
- `input_resolution`
  - 下采样后 trunk 网格尺寸 `(Height, Width)`
- `num_heads`
  - Swin attention 头数
- `window_size`
  - 局部窗口大小
- `depth`
  - `SwinTransformerV2Stage` 的 block 层数

# key_dependencies
- `onetransformer`
- `onesample`
- `fuxidownsample`
- `fuxiupsample`
- `helpers`
- `swin_transformer_v2`
- `fuxi_utils`

# usage_and_risks
- 该组件输入是二维特征图，不是 token 序列
- `input_resolution` 与真实下采样后 trunk 尺寸不一致会导致 padding / crop 逻辑出错
- 上下游通道数必须与 `embed_dim` 对齐

# code_references
- `{onescience_path}/onescience/src/onescience/modules/transformer/fuxitransformer.py`
- `{onescience_path}/onescience/src/onescience/modules/transformer/onetransformer.py`
- `{onescience_path}/onescience/src/onescience/models/fuxi/fuxi.py`
