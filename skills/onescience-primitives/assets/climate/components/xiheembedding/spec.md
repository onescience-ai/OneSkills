# component_info
`xiheembedding` 属于 `embedding` 模块族，核心实现类/函数包括 `XiheEmbedding`。它的定位是嵌入层，由上层 OneScience 模型或流水线通过 Python API 调用。

# purpose
把原始数值特征、patch 或图节点/边特征投影到统一隐空间，适用于主干网络进入前的特征标准化表达。

# input_schema
- 张量输入通常遵循 `(Batch, Channels, Height, Width)`、`(Batch, Tokens, Channels)` 或源码注释约定的三维气象场格式。
- 尺寸参数需要与上游 patch、窗口、网格分辨率保持一致。

# output_schema
- 输出为变换后的张量特征或预测场，空间尺度、token 数和通道数由构造参数及上游模型配置共同决定。

# parameters
- `XiheEmbedding` 构造参数：`img_size`, `patch_size`, `embed_dim`, `in_chans`, `norm_layer`

# key_dependencies
- `embedding` 模块族内的相邻组件

# usage_and_risks
- 输入张量维度必须与构造参数中的通道数、网格分辨率、patch 大小或图特征维度一致。
- 该组件通常依赖上层模型完成数据标准化、变量排序和设备迁移，单独调用时需显式准备。

# code_references
- `{onescience_path}/onescience/src/onescience/modules/embedding/xiheembedding.py`
