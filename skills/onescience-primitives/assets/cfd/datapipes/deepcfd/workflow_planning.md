# description

该原语用于规划简单规则网格稳态 CFD 回归数据流，将成对输入/输出数组直接变成字典 batch。

# when_to_use

- 数据已经预处理为 `X -> Y` 成对规则网格张量。
- 模型是图像式或卷积式场回归模型。
- 不需要图结构、坐标网格、case 参数或时间序列逻辑。
- 需要复用 DeepCFD 示例训练流程。

# inputs

- 输入 pickle 文件名和目标 pickle 文件名。
- train/test 划分比例和随机种子。
- batch size、num_workers。
- 是否使用输出通道权重。

# outputs

- train/test dataloader。
- `{"x", "y"}` 样本 batch。
- 训练集通道权重。

# procedure

1. 确认 `dataX` 与 `dataY` 样本数一致。
2. 估算 pickle 全量加载内存。
3. 设置 split ratio 和随机种子。
4. 构造 datapipe 并读取 loss weights。
5. 将 batch 协议接入 DeepCFD 模型训练。

# constraints

- 输出通道默认 3。
- 没有独立验证集。
- 数据必须能完整加载到内存。

# next_phase_recommendation

若需要时间序列或物理参数，转向 CFDBench；若需要 HDF5 operator learning，转向 PDENNEval；若需要几何图结构，转向 AirfRANS 或 ShapeNetCar。

# fallback

- 内存不足时先离线切分 pickle 或改写 dataset 为懒加载。
- 需要验证集时在外部重新划分数据文件或扩展 datapipe。
- 通道数不同则禁用或重写 `get_loss_weights`。
