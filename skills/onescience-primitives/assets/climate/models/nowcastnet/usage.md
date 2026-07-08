# launch

Python API 启动示例：

```sh
python -c "import torch; from types import SimpleNamespace; from onescience.models.nowcastnet.nowcastnet import Net; cfg=SimpleNamespace(total_length=29, input_length=9, img_height=256, img_width=256, ngf=64, device='cpu', pretrained_model='./data/checkpoints/mrms_model.ckpt'); model=Net(cfg); x=torch.randn(1,29,256,256,1); y=model(x); print(y.shape)"
```

# input_schema

- 输入为 `(Batch, total_length, Height, Width, Channels)`。
- 示例默认配置：`total_length=29`，`input_length=9`，`img_height=256`，`img_width=256`，`ngf=64`，`device="cpu"`，`pretrained_model="./data/checkpoints/mrms_model.ckpt"`。
- 示例默认输入 shape：`(Batch, 29, 256, 256, 1)`。
- 默认预测长度由配置计算：`pred_length=total_length-input_length=20`。
- `input_length` 前的帧作为历史观测。
- `total_length - input_length` 决定预测长度。
- 当前主模型只使用第一个通道。

# runtime_interfaces

- `forward(all_frames)`：主生成网络推理入口。
- evolutionnet 的 `forward(all_frames)`：输出演化结果、双线性平流结果和运动场。
- discriminator2 的 `forward(x)`：训练期判别入口。

# main_functions

- `forward`

# execution_resources

- 适合 GPU 训练与推理，CPU 可用于小尺寸调试。
- 运行时需要 `configs.device` 与模型、输入张量保持一致。
- 生成式路径会采样随机噪声，复现实验需固定随机种子。

# operation_limits

- 主模型仅消费单通道。
- 对输入尺寸的下采样倍数有隐含要求。
- 不包含数据集读取、雷达拼图、质量控制或后处理。
- 若 `pretrained_model` 路径字符串变化，输出缩放逻辑可能改变。
