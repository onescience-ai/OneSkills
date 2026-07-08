# component_info
在三维网格 `(Variables, Height, Width)` 上融合多个变量分支的中分辨率特征。

补充说明：

- 该组件处理的是展平后的三维 token 序列
- 输入通常来自多个 `FengWuEncoder` 输出的中分辨率特征拼接
- 内部使用多层 `EarthTransformer3DBlock`

该组件的核心实现包括 `FengWuFuser`，定位为融合模块，由上层 OneScience 模型或流水线通过 Python API 调用。

# purpose
融合来自不同变量、尺度、时间步或分支的特征，适用于多源气象场建模。

# input_schema
- 2D 输入：`not_applicable`
- 3D 输入：`(Batch, Variables * Height * Width, dim)`

内部统一做法：

- 将输入视作三维网格对应的 token 序列
- 在 `(Variables, Height, Width)` 三维网格上堆叠多层 3D Transformer
- 输出 token 数与输入保持一致

# output_schema
- 2D 输出：`not_applicable`
- 3D 输出：`(Batch, Variables * Height * Width, dim)`

明确约束：

- 输出 token 数与输入 token 数保持一致
- `input_resolution` 必须与输入 token 数严格对应

# parameters
- `input_resolution`
  - 三维网格尺寸 `(Variables, Height, Width)`
- `dim`
  - 输入与输出 token 特征维度
- `depth`
  - 3D Transformer block 层数
- `num_heads`
  - 多头自注意力头数
- `window_size`
  - 三维窗口大小 `(VariablesWindow, HeightWindow, WidthWindow)`
- `drop_path`
  - 可为单值或按层提供的序列
- `mlp_ratio`, `qkv_bias`, `qk_scale`, `drop`, `attn_drop`, `norm_layer`
  - 标准 Transformer 配置项

# key_dependencies
- `onefuser`
- `onetransformer`
- `earthtransformer3dblock`
- `oneattention`
- `earthattention3d`

# usage_and_risks
- 该组件输入是展平 token 序列，不是二维网格特征
- 第一维 `Variables` 指的是变量分支数，不是时间步或气压层
- `dim` 必须与 encoder 输出和 decoder 输入保持一致

# code_references
- `{onescience_path}/onescience/src/onescience/modules/fuser/fengwufuser.py`
- `{onescience_path}/onescience/src/onescience/modules/fuser/onefuser.py`
- `{onescience_path}/onescience/src/onescience/models/fengwu/fengwu.py`
