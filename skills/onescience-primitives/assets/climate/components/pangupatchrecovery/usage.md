# launch
主要通过 Python API 在模型配置或上层模块中实例化，不是独立 CLI 入口。下面的命令会从源码模块导入组件并打印完整构造签名，便于确认全部 API 参数：

```sh
python -c "from onescience.modules.recovery.pangupatchrecovery import PanguPatchRecovery; import inspect; print(inspect.signature(PanguPatchRecovery))"
```

在真实任务中应由对应模型配置传入尺寸、通道数和隐空间维度等参数。

# input_schema
- 2D 输入：`(Batch, in_chans, Height, Width)`
- 3D 输入：`(Batch, in_chans, PressureLevels, Height, Width)`

内部统一做法：

- 对 2D 输入补一个长度为 1 的伪 `PressureLevels`
- 统一走 `ConvTranspose3d`
- 恢复后按 `img_size` 做中心裁剪
- 若原始输入为 2D，最后再去掉伪三维层

默认参数信息：

- `PanguPatchRecovery` 构造默认参数：`img_size=(13, 721, 1440)`，`patch_size=(2, 4, 4)`，`in_chans=192 * 2`，`out_chans=5`

# runtime_interfaces
- `PanguPatchRecovery`：实例化后通过 `forward` 等运行时接口参与流水线。

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
