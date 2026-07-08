# launch
Python API 启动，调用方按目标 style 传入底层实现参数：

``` sh
python -c "from onescience.modules.encoder.oneencoder import OneEncoder; m=OneEncoder(style='UNetEncoder2D'); print(type(m).__name__)"
```

在模型 pipeline 中通常由上层模型构造函数实例化，不单独提供 CLI。

# input_schema
从 datapipe 输出中整理字段：规则场按 channel-first 张量组织；图数据需提供节点、边和 graph；GraphViT 还需 cluster/位置编码；Protenix 由模型特征构造器提供。

# runtime_interfaces
- 构造接口：`OneEncoder(style, **kwargs)`。
- 调用接口：`encoder(*args, **kwargs)`。
- 权重接口：`load_state_dict(state_dict, strict=True)` 对裸 encoder 权重键加前缀。
- 属性访问：未命中的属性转发到底层 encoder。

# main_functions
- `forward`

# execution_resources
规则网格 encoder 消耗随分辨率和通道数增长；图 encoder 消耗随节点/边数增长；通常建议在 GPU 上训练，轻量 shape 检查可在 CPU 上完成。

# operation_limits
不做数据格式转换、不构图、不创建位置编码；不同 encoder 的输出不能默认互换。
