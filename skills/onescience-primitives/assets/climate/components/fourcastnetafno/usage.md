# launch
主要通过 Python API 在模型配置或上层模块中实例化，不是独立 CLI 入口。下面的命令会从源码模块导入组件并打印完整构造签名，便于确认全部 API 参数：

```sh
python -c "from onescience.modules.afno.fourcastnetafno import FourCastNetAFNO2D; import inspect; print(inspect.signature(FourCastNetAFNO2D))"
```

在真实任务中应由对应模型配置传入尺寸、通道数和隐空间维度等参数。

# input_schema
- 2D 输入：`(Batch, Height, Width, Channels)`
- 3D 输入：`not_applicable`

内部统一做法：

- 先做 `rfft2` 将特征映射到频域
- 对各通道块执行复数 MLP 混合
- 用 `softshrink` 做频域稀疏化
- 再做 `irfft2` 回到空间域

默认参数信息：

- `FourCastNetAFNO2D` 构造默认参数：`hidden_size=768`，`num_blocks=8`，`sparsity_threshold=0.01`，`hard_thresholding_fraction=1`，`hidden_size_factor=1`

# runtime_interfaces
- `FourCastNetAFNO2D`：实例化后通过 `forward` 等运行时接口参与流水线。

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
