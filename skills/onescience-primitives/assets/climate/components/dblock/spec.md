# component_info
`dblock` 属于 `layer` 模块族，核心实现类/函数包括 `DBlockDown`、`DBlockDownFirst`、`DBlock`、`DBlock3D_1`、`DBlock3D_2`、`LBlockDown`、`ProjBlock`、`LastConv`。它的定位是网络层，由上层 OneScience 模型或流水线通过 Python API 调用。

# purpose
提供生成、演化或判别网络的基础层，适用于时空场生成与对抗式判别任务。

# input_schema
- 输入由上层模型传入，通常为二维或三维张量特征、条件特征或噪声张量。

# output_schema
- 输出为变换后的张量特征或预测场，空间尺度、token 数和通道数由构造参数及上游模型配置共同决定。

# parameters
- `DBlockDown` 构造参数：`in_channels`, `out_channels`
- `DBlockDownFirst` 构造参数：`in_channels`, `out_channels`
- `DBlock` 构造参数：`in_channels`, `out_channels`
- `DBlock3D_1` 构造参数：`in_channels`, `out_channels`
- `DBlock3D_2` 构造参数：`in_channels`, `out_channels`
- `LBlockDown` 构造参数：`in_channels`, `out_channels`
- `ProjBlock` 构造参数：`in_channel`, `out_channel`
- `LastConv` 构造参数：`in_channels`, `out_channels`

# key_dependencies
- `spectralNormalization`

# usage_and_risks
- 输入张量维度必须与构造参数中的通道数、网格分辨率、patch 大小或图特征维度一致。
- 该组件通常依赖上层模型完成数据标准化、变量排序和设备迁移，单独调用时需显式准备。
- 生成/判别网络对空间尺寸和条件特征较敏感，错误的尺度会导致卷积或上采样阶段形状不匹配。

# code_references
- `{onescience_path}/onescience/src/onescience/modules/layer/discrimination/DBlock.py`
