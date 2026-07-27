## content_principle
DeepCFD 数据集原语描述 `/public/share/sugonhpcapp01/onestore/onedatasets/DeepCFD` 下的成对输入/输出规则网格 pickle 数据，用于二维 CFD 场回归。

## data_schema
核心文件为 `dataX.pkl` 和 `dataY.pkl`。已探测二者转换为数组后 shape 均为 `(981,3,172,79)`，dtype 为 `float32`。单样本协议为 `{"x": input_tensor, "y": target_tensor}`。

## directory_layout
```text
/DeepCFD
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
`dataY.pkl` 是监督目标，默认 3 个输出通道。通道物理含义需结合 DeepCFD 配置或原论文说明确认。

## split_strategy
datapipe 默认按 `split_ratio` 切分 train/test；`mode=val` 也落在剩余段，不是独立验证集。

## constraints
数据会一次性入内存；loss 权重默认 3 通道；不包含坐标、mask、图边或 case 参数。
