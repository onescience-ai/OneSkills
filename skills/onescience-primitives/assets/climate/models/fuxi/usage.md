# launch

Python API 启动示例：

```sh
python -c "import torch; from onescience.models.fuxi import Fuxi; model=Fuxi(img_size=(2,721,1440), patch_size=(2,4,4), in_chans=70, out_chans=70, embed_dim=1536, num_groups=32, num_heads=8, window_size=7); x=torch.randn(1,70,2,721,1440); y=model(x); print(y.shape)"
```

# input_schema

- 输入应组织为五维张量 `(Batch, Channels, TimeSteps, Height, Width)`。
- 默认参数：`img_size=(2, 721, 1440)`，`patch_size=(2, 4, 4)`，`in_chans=70`，`out_chans=70`，`embed_dim=1536`，`num_groups=32`，`num_heads=8`，`window_size=7`。
- 默认输入 shape：`(Batch, 70, 2, 721, 1440)`。
- 时间维必须与 patch 时间长度一致。
- 通道应包含模型训练时定义的气象变量集合。
- 数据预处理需在调用前完成，包括归一化、缺测值填补、经纬网格对齐。

# runtime_interfaces

- `forward(x)`：执行从多时间步输入到单个二维预测场的推理。

# main_functions

- `forward`

# execution_resources

- 默认配置适合 GPU 运行，尤其是 `embed_dim=1536` 时。
- CPU 可用于小尺寸调试，但不适合默认全球分辨率。
- 依赖 OneScience 模块中的 Fuxi embedding、transformer 和全连接恢复组件。

# operation_limits

- 当前实现只输出单个二维目标场。
- 不支持 batch 内不同时间步长度。
- 输入时间步与 patch 时间步不一致会直接失败。
- 非训练分辨率运行时，需要重新检查位置、patch 和插值恢复是否一致。
