# launch
Python API 启动，调用方按目标 style 传入底层实现参数：

``` sh
python -c "from onescience.modules.decoder.onedecoder import OneDecoder; m=OneDecoder(style='UNetDecoder2D'); print(type(m).__name__)"
```

在模型 pipeline 中通常由上层模型构造函数实例化，不单独提供 CLI。

# input_schema
从 encoder 或 processor 准备与 decoder family 匹配的特征：U-Net 需要多尺度 skip，图解码需要节点/边和拓扑索引，天气 token 解码需要模型约定的 token 排布。

# runtime_interfaces
- 构造接口：`OneDecoder(style, **kwargs)`。
- 调用接口：`decoder(*args, **kwargs)` 透传到底层。
- 属性访问：未命中的属性转发到底层 decoder。

# main_functions
- `forward`

# execution_resources
U-Net 解码器显存随空间分辨率和 skip 数增长；图解码器依赖图数据结构和节点数；Protenix 解码器通常面向 GPU 推理或训练。

# operation_limits
不自动适配 encoder 输出，不执行物理量反归一化，不保证不同 decoder 输出语义一致。
