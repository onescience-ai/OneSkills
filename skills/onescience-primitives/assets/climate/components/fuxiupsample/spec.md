# component_info
对二维特征图做 2 倍上采样，并通过残差卷积块细化特征。

补充说明：

- 该组件处理的是二维特征图
- 不是 token 序列
- 通常位于 `FuxiTransformer` 的末尾

该组件的核心实现包括 `FuxiUpSample`，定位为采样模块，由上层 OneScience 模型或流水线通过 Python API 调用。

# purpose
执行上采样或下采样，改变特征图/特征体的空间尺度或通道维度，适用于多尺度主干网络。

# input_schema
- 2D 输入：`(Batch, in_chans, Height, Width)`
- 3D 输入：`not_applicable`

内部统一做法：

- 先用转置卷积做 2 倍上采样
- 再通过若干残差卷积块细化特征
- 最终通过残差连接输出

# output_schema
- 2D 输出：`(Batch, out_chans, OutHeight, OutWidth)`
- 3D 输出：`not_applicable`

其中：

- `OutHeight = Height * 2`
- `OutWidth = Width * 2`

# parameters
- `in_chans`
  - 输入特征通道数
- `out_chans`
  - 输出特征通道数
- `num_groups`
  - `GroupNorm` 分组数
- `num_residuals`
  - 残差卷积块数量

# key_dependencies
- `sample` 模块族内的相邻组件

# usage_and_risks
- 该组件不处理 token 序列
- 输入通道数通常来自 skip 拼接后的 `2 * embed_dim`
- `num_groups` 需要与 `out_chans` 匹配

# code_references
- `{onescience_path}/onescience/src/onescience/modules/sample/fuxiupsample.py`
- `{onescience_path}/onescience/src/onescience/modules/sample/onesample.py`
- `{onescience_path}/onescience/src/onescience/modules/transformer/fuxitransformer.py`
