# launch

Python API 方式调用，作为 ESM trunk 层使用：

```sh
python -c "from onescience.modules.esm.transformer import TransformerLayer, AxialTransformerLayer; print(TransformerLayer.__name__, AxialTransformerLayer.__name__)"
```

# input_schema

普通序列层输入 `(Length, Batch, Channels)`；MSA 轴向层输入 `(Rows, Cols, Batch, Channels)`。根据任务准备 padding mask、attention mask 或 MSA mask。

# runtime_interfaces

- `TransformerLayer.forward`: 单序列 transformer 层前向。
- `AxialTransformerLayer.forward`: MSA 行列轴向层前向。
- `NormalizedResidualBlock.forward`: 归一化残差包装。
- `FeedForwardNetwork.forward`: 前馈网络更新。

# main_functions

- `forward`

# execution_resources

显存和序列长度、MSA 大小、层宽、头数成正相关。长序列建议复用预训练表征或分块处理。

# operation_limits

输入布局必须匹配层类型；普通序列层和 MSA 层不能直接互换。仅输出 hidden states，不给出结构坐标或分子评分。
