## content_principle
DeepCFD 数据集原语描述共享目录 `/public/share/sugonhpcapp01/onestore/onedatasets/DeepCFD/data` 下的成对规则网格 pickle 数据，用于二维稳态层流代理建模。目标场由 OpenFOAM `simpleFOAM` 计算。共享数据包版本未声明；来源见 `usage.md`。

## data_schema
核心文件为 `dataX.pkl` 和 `dataY.pkl`。已探测二者转换为数组后 shape 均为 `(981,3,172,79)`，dtype 为 `float32`。单样本协议为 `{"x": input_tensor, "y": target_tensor}`。

## directory_layout
```text
/DeepCFD/data
├── dataX.pkl
└── dataY.pkl
```

## storage_format
pickle 存储 NumPy 风格数组。OneScience DeepCFD datapipe 会一次性加载到内存，并根据 `split_ratio` 和随机 seed 生成 train/test。

## scale_spec
当前样本数为 981，输入/输出均为 3 通道 `172 x 79` 规则网格。

## coverage_spec
适用于二维稳态或准稳态 CFD 场代理建模、CNN/UNet/DeepCFD 类模型训练和通道加权损失测试。

## label_spec
`dataX.pkl` 的通道顺序是障碍物表面的符号距离（SDF）、流动区域标签、上下壁面的 SDF；区域标签对应障碍物、自由流、壁面、入口和出口，不是第三种连续距离场。`dataY.pkl` 的通道顺序是水平速度 `Ux`、垂直速度 `Uy`、压力 `p`。尺寸和 dtype 不足以识别通道；pickle 不声明物理单位或每类区域的编号映射，需要物理单位或区域掩码时应核对上游生成定义。

## split_strategy
OneScience 示例使用 `random.Random(seed).shuffle` 对同一份样本索引排序，然后在 `int(N * split_ratio)` 处切分，输入和目标使用同一组索引。示例的 `seed=0`、`split_ratio=0.7` 对当前数据产生 686/295 个样本；这不是数据文件内置的固定划分。`mode=val` 与 `mode=test` 使用相同的剩余段，不是独立验证集。

## constraints
数据会一次性入内存；loss 权重默认 3 通道；不包含坐标、mask、图边或 case 参数。
