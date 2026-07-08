# launch

Python API 启动示例：

```sh
python -c "import torch; from onescience.models.fourcastnet import FourCastNet; model=FourCastNet(img_size=(720,1440), patch_size=(8,8), in_chans=19, out_chans=19, embed_dim=768, depth=12, mlp_ratio=4.0, drop_rate=0.0, drop_path_rate=0.0, num_blocks=8, sparsity_threshold=0.01, hard_thresholding_fraction=1.0); x=torch.randn(1,19,720,1440); y=model(x); print(y.shape)"
```

# input_schema

- 输入为四维张量 `(Batch, Channels, Height, Width)`。
- 默认参数：`img_size=(720, 1440)`，`patch_size=(8, 8)`，`in_chans=19`，`out_chans=19`，`embed_dim=768`，`depth=12`，`mlp_ratio=4.0`，`drop_rate=0.0`，`drop_path_rate=0.0`，`num_blocks=8`，`sparsity_threshold=0.01`，`hard_thresholding_fraction=1.0`。
- 默认输入 shape：`(Batch, 19, 720, 1440)`。
- 通道顺序需与训练数据一致。
- 空间尺寸应与模型实例化的 `img_size` 一致。
- 数据应提前完成标准化和缺测处理。

# runtime_interfaces

- `forward(x)`：执行二维气象场预测。
- `no_weight_decay()`：返回不参与权重衰减的参数名集合。

# main_functions

- `forward`
- `no_weight_decay`

# execution_resources

- 默认全球分辨率适合 GPU 推理。
- 相比三维图模型，调用接口简单，适合批量二维场推理。
- 依赖 OneScience 的 FourCastNet embedding 与 fuser 组件。

# operation_limits

- 不处理时间序列输入。
- 不内置滚动预报、变量反归一化或物理约束。
- 变更输入分辨率时需要同步处理位置编码和 patch 网格。
- patch 不整除输入尺寸时恢复阶段容易失败。
