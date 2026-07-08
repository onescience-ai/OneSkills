# launch
主要通过 Python API 在模型配置或上层模块中实例化，不是独立 CLI 入口。下面的命令会从源码模块导入组件并打印完整构造签名，便于确认全部 API 参数：

```sh
python -c "from onescience.modules.fuser.xihelocalsiefuser import XiheLocalSIEFuser; import inspect; print(inspect.signature(XiheLocalSIEFuser))"
```

在真实任务中应由对应模型配置传入尺寸、通道数和隐空间维度等参数。

# input_schema
- 张量输入通常遵循 `(Batch, Channels, Height, Width)`、`(Batch, Tokens, Channels)` 或源码注释约定的三维气象场格式。
- 尺寸参数需要与上游 patch、窗口、网格分辨率保持一致。

默认参数信息：

- `XiheLocalSIEFuser` 构造默认参数：`depth=2`，`num_heads=6`，`window_size=(1, 6, 12)`，`mlp_ratio=4.0`，`qkv_bias=True`，`qk_scale=None`，`drop=0.0`，`attn_drop=0.0`，`drop_path=0.0`，`norm_layer=nn.LayerNorm`

# runtime_interfaces
- `XiheLocalSIEFuser`：实例化后通过 `forward` 等运行时接口参与流水线。

# main_functions
- `forward`

# execution_resources
- 运行设备由上层任务决定，训练和高分辨率推理通常建议使用 GPU。
- 图构建、邻居搜索或大分辨率气象场处理会占用较多内存，批量大小需随网格规模调整。
- 需要保证依赖库和 OneScience 模块路径可用，并与模型配置中的精度、设备和维度设置一致。

# operation_limits
- 不负责完整数据预处理、变量标准化、训练循环或损失函数编排。
- 仅在输入形状、变量顺序、图结构和上下游组件契约一致时可稳定工作。
- 源码中未声明的 CLI 参数、自动下载或外部数据读取能力不应假定存在。
