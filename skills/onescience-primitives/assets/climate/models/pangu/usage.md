# launch

Python API 启动示例：

```sh
python -c "import torch; from onescience.models.pangu import Pangu; model=Pangu(img_size=(721,1440), patch_size=(2,4,4), embed_dim=192, num_heads=(6,12,12,6), window_size=(2,6,12)); x=torch.randn(1,72,721,1440); ys,yu=model(x); print(ys.shape, yu.shape)"
```

# input_schema

- 输入为单个四维张量 `(Batch, 72, Height, Width)`。
- 默认参数：`img_size=(721, 1440)`，`patch_size=(2, 4, 4)`，`embed_dim=192`，`num_heads=(6, 12, 12, 6)`，`window_size=(2, 6, 12)`。
- 默认输入 shape：`(Batch, 72, 721, 1440)`，其中 `72 = 4 + 3 + 5 * 13`。
- 通道布局必须是 `4` 个地表预报变量、`3` 个静态掩码、`5*13` 个高空变量。
- 高空变量在通道维展平，模型内部 reshape 为变量与压力层。
- 输入应完成归一化、静态掩码拼接和经纬网格对齐。

# runtime_interfaces

- `forward(x)`：执行一次 Pangu 三维天气场预测。

# main_functions

- `forward`

# execution_resources

- 推荐 GPU，默认全球分辨率与三维窗口融合显存开销较大。
- 元数据标记支持 AMP、cuda graphs 和 GPU ONNX runtime。
- 依赖 OneScience 的 embedding、fuser、sample、recovery 组件。

# operation_limits

- 默认只适配 13 个压力层。
- 输出地表变量为 4 通道，不输出输入中的 3 个静态掩码。
- 当前 recovery 层默认绑定 721x1440 网格。
- 通道顺序错误会产生语义错误，即使 shape 能通过。
