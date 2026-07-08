# architecture_overview

NowcastNet 是演化网络加生成网络的短临降水模型。主模型为 `Net`，辅助实现包括 generator、evolutionnet 和 discriminator2。
主路径先做物理直觉更强的运动场/强度演化外推，再用生成网络补充局地纹理和细节。

# parameter_scale

- 参数规模由 Evolution_Network、Generative_Encoder、Noise_Projector 和 Generative_Decoder 决定。
- `pred_length = total_length - input_length`。
- 演化网络默认 `base_c=32`。
- 生成网络通道宽度由 `configs.ngf` 控制。

# architecture_structure

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

# input_schema

- 主网络输入 `all_frames`: `(Batch, total_length, Height, Width, Channels)`。
- 当前实现只取最后一维的第 1 个通道：`all_frames[:, :, :, :, :1]`。
- `configs` 至少需要 `total_length`、`input_length`、`img_height`、`img_width`、`ngf`、`device`、`pretrained_model`。

# output_schema

- 主网络输出 `gen_result`，表示未来 `pred_length` 帧降水或雷达回波。
- evolutionnet 辅助输出包括 `evo_result`、`evo_motion`、`motion_`。
- 判别器输出为真实性评分图。

# shape_transformations

1. 输入裁剪为单通道序列。
2. permute 为 `(B,T,1,H,W)`，再把历史帧 reshape 为 `(B,input_length,H,W)`。
3. 演化网络输出 intensity 与 motion。
4. motion reshape 为 `(B,pred_length,2,H,W)`，intensity reshape 为 `(B,pred_length,1,H,W)`。
5. 循环 warp 最后一帧，拼接得到 `(B,pred_length,H,W)`。
6. 演化结果除以 128 后与历史帧拼接送入生成编码器。
7. 噪声投影到 `H/8 x W/8` 级别特征。
8. 生成解码器输出未来序列。

# key_dependencies

- `evolutionnetwork`
- `generativeencoder`
- `generativedecoder`
- `noiseprojector`
- `warp`
- `makegrid`
- `projblock`
- `lastconv`


# common_modification_points

- 调整 `input_length` 与 `total_length` 改变历史窗口和预测步数。
- 修改 `img_height/img_width` 时需保证噪声投影中的 `height // 32`、`height // 8` 等尺度合法。
- 改造多通道输入时需要移除或扩展单通道裁剪逻辑。
- 可只使用 evolutionnet 作为确定性外推基线，也可加入 discriminator2 进行生成式训练。

# implementation_risks

- `configs.device` 必须与输入和模型设备一致。
- 高宽过小或不能被 32 合理下采样时，噪声特征 reshape 可能失败。
- `pretrained_model` 字符串控制是否乘以 128，路径判断较脆弱。
- 当前主模型输入只使用第一个通道，多通道数据会被忽略。
- 判别器固定第一层二维卷积输入通道为 29，训练配置需匹配。

# code_references

- `{onescience_path}/onescience/src/onescience/models/nowcastnet/nowcastnet.py`
- `{onescience_path}/onescience/src/onescience/models/nowcastnet/generator.py`
- `{onescience_path}/onescience/src/onescience/models/nowcastnet/evolutionnet.py`
- `{onescience_path}/onescience/src/onescience/models/nowcastnet/discriminator2.py`
- `{onescience_path}/onescience/src/onescience/modules/layer/evolution/evolution_network.py`
- `{onescience_path}/onescience/src/onescience/modules/layer/generation/generative_network.py`
- `{onescience_path}/onescience/src/onescience/modules/layer/generation/noise_projector.py`
- `{onescience_path}/onescience/src/onescience/modules/layer/discrimination/DBlock.py`
