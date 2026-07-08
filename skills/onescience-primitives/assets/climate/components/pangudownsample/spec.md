# component_info
对二维或三维 token 网格做统一下采样，将相邻 2×2 空间邻域聚合到更低分辨率的 token 表示中。

这是 Pangu 系列多尺度编码阶段的统一 token 下采样组件。

该组件的核心实现包括 `PanguDownSample`，定位为采样模块，由上层 OneScience 模型或流水线通过 Python API 调用。

# purpose
执行上采样或下采样，改变特征图/特征体的空间尺度或通道维度，适用于多尺度主干网络。

# input_schema
- 2D 输入：`(Batch, Height * Width, in_dim)`
- 3D 输入：`(Batch, PressureLevels * Height * Width, in_dim)`

内部统一做法：

- 对 2D 输入补一个长度为 1 的伪 `PressureLevels`
- 统一按三维网格恢复
- 只在 `Height` 和 `Width` 方向做 2×2 聚合
- 必要时自动做空间 padding

# output_schema
- 2D 输出：`(Batch, OutHeight * OutWidth, 2 * in_dim)`
- 3D 输出：`(Batch, OutPressureLevels * OutHeight * OutWidth, 2 * in_dim)`

默认约束：

- 只对空间维做 2 倍下采样
- `PressureLevels` 维通常保持不变

# parameters
- `input_resolution`
  - 2D: `(Height, Width)`
  - 3D: `(PressureLevels, Height, Width)`
- `output_resolution`
  - 2D: `(OutHeight, OutWidth)`
  - 3D: `(OutPressureLevels, OutHeight, OutWidth)`
- `in_dim`
  - 输入 token 特征维

# key_dependencies
- `sample` 模块族内的相邻组件

# usage_and_risks
- 这是 token 级组件，不接收图像张量
- 输入 token 数必须与 `input_resolution` 完全匹配
- 输出特征维固定为 `2 * in_dim`

# code_references
- `{onescience_path}/onescience/src/onescience/modules/sample/pangudownsample.py`
- `{onescience_path}/onescience/src/onescience/modules/sample/onesample.py`
