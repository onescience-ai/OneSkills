# launch
主要通过 Python API 在模型配置或上层模块中实例化，不是独立 CLI 入口。下面的命令会从源码模块导入组件并打印完整构造签名，便于确认全部 API 参数：

```sh
python -c "from onescience.modules.fuser.pangufuser import PanguFuser; import inspect; print(inspect.signature(PanguFuser))"
```

在真实任务中应由对应模型配置传入尺寸、通道数和隐空间维度等参数。

# input_schema
- 2D 输入：`not_applicable`
- 3D 输入：`(Batch, PressureLevels * Height * Width, dim)`

内部统一做法：

- 不处理 2D/3D 双形态统一问题
- 输入默认已经被组织成三维网格对应的 token 序列
- 每一层内部调用 `OneTransformer(style="EarthTransformer3DBlock")`
- 多层 block 顺序堆叠完成融合

默认参数信息：

- `PanguFuser` 构造默认参数：`drop_path=0.0`，`mlp_ratio=4.0`，`qkv_bias=True`，`qk_scale=None`，`drop=0.0`，`attn_drop=0.0`，`norm_layer=nn.LayerNorm`

# runtime_interfaces
- `PanguFuser`：实例化后通过 `forward` 等运行时接口参与流水线。

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
