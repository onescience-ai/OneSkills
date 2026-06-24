# Model Card: nowcastnet

## 基本信息

- 模型名：`nowcastnet`
- 任务类型：`model`
- 当前状态：`public`
- 主实现文件：`{onescience_path}/onescience/src/onescience/models/nowcastnet/nowcastnet.py`

## 模型架构概览

NowcastNet 是演化网络加生成网络的短临降水模型。主模型为 `Net`，辅助实现包括 generator、evolutionnet 和 discriminator2。
主路径先做物理直觉更强的运动场/强度演化外推，再用生成网络补充局地纹理和细节。

## 参数规模

- 参数规模由 Evolution_Network、Generative_Encoder、Noise_Projector 和 Generative_Decoder 决定。
- `pred_length = total_length - input_length`。
- 演化网络默认 `base_c=32`。
- 生成网络通道宽度由 `configs.ngf` 控制。

## 架构结构

```text
输入序列
  all_frames: (Batch, total_length, Height, Width, Channels)
    -> 仅保留第一个通道
    -> frames: (Batch, total_length, 1, Height, Width)
    -> input_frames: (Batch, input_length, Height, Width)

演化网络路径
  input_frames
    -> Evolution_Network(input_length, pred_length)
    -> intensity: (Batch, pred_length, Height, Width)
    -> motion   : (Batch, pred_length * 2, Height, Width)
    -> motion_:   (Batch, pred_length, 2, Height, Width)
    -> intensity_: (Batch, pred_length, 1, Height, Width)

逐步平流外推
  last observed frame
    -> for each prediction step:
         warp(last_frame, motion_[i])
         add intensity_[i]
    -> concat series
    -> evo_result: (Batch, pred_length, Height, Width)
    -> evo_result / 128

生成式细节增强
  concat(input_frames, evo_result)
    -> Generative_Encoder
    -> evo_feature

  random noise: (Batch, ngf, Height/32, Width/32)
    -> Noise_Projector
    -> reshape / permute
    -> noise_feature: (Batch, *, Height/8, Width/8)

  concat(evo_feature, noise_feature)
    -> Generative_Decoder(feature, evo_result)
    -> gen_result
    -> optional sigmoid scaling

训练期辅助
  discriminator2.Net
    -> 2D/3D convolution branches
    -> projection blocks
    -> score map
```

## 输入模式

- 主网络输入 `all_frames`: `(Batch, total_length, Height, Width, Channels)`。
- 当前实现只取最后一维的第 1 个通道：`all_frames[:, :, :, :, :1]`。
- `configs` 至少需要 `total_length`、`input_length`、`img_height`、`img_width`、`ngf`、`device`、`pretrained_model`。

## 输出模式

- 主网络输出 `gen_result`，表示未来 `pred_length` 帧降水或雷达回波。
- evolutionnet 辅助输出包括 `evo_result`、`evo_motion`、`motion_`。
- 判别器输出为真实性评分图。

## 形状转换

1. 输入裁剪为单通道序列。
2. permute 为 `(B,T,1,H,W)`，再把历史帧 reshape 为 `(B,input_length,H,W)`。
3. 演化网络输出 intensity 与 motion。
4. motion reshape 为 `(B,pred_length,2,H,W)`，intensity reshape 为 `(B,pred_length,1,H,W)`。
5. 循环 warp 最后一帧，拼接得到 `(B,pred_length,H,W)`。
6. 演化结果除以 128 后与历史帧拼接送入生成编码器。
7. 噪声投影到 `H/8 x W/8` 级别特征。
8. 生成解码器输出未来序列。

## 常见修改点

- 调整 `input_length` 与 `total_length` 改变历史窗口和预测步数。
- 修改 `img_height/img_width` 时需保证噪声投影中的 `height // 32`、`height // 8` 等尺度合法。
- 改造多通道输入时需要移除或扩展单通道裁剪逻辑。
- 可只使用 evolutionnet 作为确定性外推基线，也可加入 discriminator2 进行生成式训练。

## 实现风险

- `configs.device` 必须与输入和模型设备一致。
- 高宽过小或不能被 32 合理下采样时，噪声特征 reshape 可能失败。
- `pretrained_model` 字符串控制是否乘以 128，路径判断较脆弱。
- 当前主模型输入只使用第一个通道，多通道数据会被忽略。
- 判别器固定第一层二维卷积输入通道为 29，训练配置需匹配。

## 启动方式

Python API 启动示例：

```sh
python -c "import torch; from types import SimpleNamespace; from onescience.models.nowcastnet.nowcastnet import Net; cfg=SimpleNamespace(total_length=29, input_length=9, img_height=256, img_width=256, ngf=64, device='cpu', pretrained_model='./data/checkpoints/mrms_model.ckpt'); model=Net(cfg); x=torch.randn(1,29,256,256,1); y=model(x); print(y.shape)"
```

## 输入模式

- 输入为 `(Batch, total_length, Height, Width, Channels)`。
- 示例默认配置：`total_length=29`，`input_length=9`，`img_height=256`，`img_width=256`，`ngf=64`，`device="cpu"`，`pretrained_model="./data/checkpoints/mrms_model.ckpt"`。
- 示例默认输入 shape：`(Batch, 29, 256, 256, 1)`。
- 默认预测长度由配置计算：`pred_length=total_length-input_length=20`。
- `input_length` 前的帧作为历史观测。
- `total_length - input_length` 决定预测长度。
- 当前主模型只使用第一个通道。

## 运行时接口

- `forward(all_frames)`：主生成网络推理入口。
- evolutionnet 的 `forward(all_frames)`：输出演化结果、双线性平流结果和运动场。
- discriminator2 的 `forward(x)`：训练期判别入口。

## 主要函数

- `forward`

## 运行资源

- 适合 GPU 训练与推理，CPU 可用于小尺寸调试。
- 运行时需要 `configs.device` 与模型、输入张量保持一致。
- 生成式路径会采样随机噪声，复现实验需固定随机种子。

## 运行限制

- 主模型仅消费单通道。
- 对输入尺寸的下采样倍数有隐含要求。
- 不包含数据集读取、雷达拼图、质量控制或后处理。
- 若 `pretrained_model` 路径字符串变化，输出缩放逻辑可能改变。

## 规划决策

### 描述

NowcastNet 规划知识用于短临降水预测任务的模型选择、配置和执行，强调运动外推与生成式细节补偿的组合。

### 适用场景

- 输入是雷达回波、降水强度或类似二维时序图像。
- 目标是分钟到小时级短临预测。
- 需要显式建模运动场和平流演化。
- 希望在确定性外推基础上生成更清晰的空间细节。

### 输入

- 历史帧数、总帧数、图像高宽。
- 单通道降水或雷达数据。
- 设备、生成网络宽度和预训练权重路径。
- 是否需要训练判别器。

### 输出

- 未来 `pred_length` 帧预测序列。
- 可选的运动场和演化基线结果。
- 训练时可输出判别器评分用于对抗损失。

### 流程

1. 构造包含必要字段的 `configs`。
2. 将数据整理为 `(B,T,H,W,C)` 并确保单通道在最后一维。
3. 实例化主网络并加载权重。
4. 调用 `forward` 得到生成式预测。
5. 反缩放并按业务阈值生成降水产品。

### 约束

- 只使用第一个通道。
- 输入高宽需满足生成网络下采样和噪声投影约束。
- 预测长度由 `total_length - input_length` 固定。
- 随机噪声会影响输出可复现性。

### 下一阶段建议

- 封装 deterministic evolution 输出，作为质量诊断和兜底产品。
- 将输出缩放从路径字符串判断改为配置字段。
- 为多通道雷达或多源观测扩展输入层。

### 备选方案

- 若生成网络不稳定，可仅使用 evolutionnet 输出作为保守外推。
- 若显存不足，降低图像尺寸、batch size 或 `ngf`。
- 若多通道输入不可避免，应先做通道融合预处理，再送入当前单通道模型。

## 组件契约入口

- ../contracts/evolutionnetwork.md
- ../contracts/generativeencoder.md
- ../contracts/generativedecoder.md
- ../contracts/noiseprojector.md
- ../contracts/warp.md
- ../contracts/makegrid.md
- ../contracts/projblock.md
- ../contracts/lastconv.md

## 源码锚点

- `{onescience_path}/onescience/src/onescience/models/nowcastnet/nowcastnet.py`
- `{onescience_path}/onescience/src/onescience/models/nowcastnet/generator.py`
- `{onescience_path}/onescience/src/onescience/models/nowcastnet/evolutionnet.py`
- `{onescience_path}/onescience/src/onescience/models/nowcastnet/discriminator2.py`
- `{onescience_path}/onescience/src/onescience/modules/layer/evolution/evolution_network.py`
- `{onescience_path}/onescience/src/onescience/modules/layer/generation/generative_network.py`
- `{onescience_path}/onescience/src/onescience/modules/layer/generation/noise_projector.py`
- `{onescience_path}/onescience/src/onescience/modules/layer/discrimination/DBlock.py`
