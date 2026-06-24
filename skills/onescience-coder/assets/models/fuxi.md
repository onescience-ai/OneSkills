# Model Card: fuxi

## 基本信息

- 模型名：`fuxi`
- 任务类型：`model`
- 当前状态：`public`
- 主实现文件：`{onescience_path}/onescience/src/onescience/models/fuxi/fuxi.py`

## 模型架构概览

Fuxi 是时空 patch 编码加二维主干恢复模型。它把多个历史时间步压入一个 patch token 表示，使后续主干只处理二维空间网格。
它不是 Pangu 式三维 token 主干，也不是 FourCastNet 式单时刻二维输入；其核心是先用三维 patch embedding 将时间维压缩到 1，再交给二维 U 形 trunk。

## 参数规模

- 默认输入尺寸 `(2, 721, 1440)`，默认 patch `(2, 4, 4)`。
- 默认输入/输出通道均为 70。
- 默认 `embed_dim=1536`，主干注意力头数为 8。
- 参数规模主要由 embedding、FuxiTransformer 和 patch 恢复全连接层决定。

## 架构结构

```text
输入张量组织
  x: (Batch, in_chans, TimeSteps, Height, Width)
    默认 in_chans=70
    默认 TimeSteps=2
    默认 Height=721, Width=1440

三维时空 patch embedding
  x
    -> OneEmbedding(style="FuxiEmbedding", patch_size=(2, 4, 4), embed_dim=1536)
    -> (Batch, 1536, 1, 180, 360)

时间维压缩
  embedding 输出要求 TimeSteps' = 1
    -> squeeze(TimeSteps')
    -> (Batch, 1536, 180, 360)

二维 U 形 trunk
  (Batch, 1536, 180, 360)
    -> FuxiDownSample
    -> (Batch, 1536, 90, 180)
    -> SwinTransformerV2Stage / FuxiTransformer 主体
    -> FuxiUpSample
    -> (Batch, 1536, 180, 360)

patch 级输出恢复
  trunk 输出
    -> permute 为逐位置特征
    -> OneFC(style="FuxiFC")
    -> (Batch, 180, 360, out_chans * 4 * 4)
    -> patch 重排
    -> (Batch, 70, 720, 1440)
    -> F.interpolate(..., mode="bilinear")
    -> (Batch, 70, 721, 1440)
```

## 输入模式

- `x`: `(Batch, in_chans, TimeSteps, Height, Width)`。
- `img_size=(TimeSteps, Height, Width)`。
- `patch_size=(PatchTimeSteps, PatchHeight, PatchWidth)`。
- 当前实现要求 `PatchTimeSteps == TimeSteps`。

## 输出模式

- 输出：`(Batch, out_chans, Height, Width)`。
- 输出为空间二维场，不保留时间维。

## 形状转换

1. 输入 `(B, C_in, T, H, W)`。
2. `FuxiEmbedding` 输出 `(B, embed_dim, 1, H/ph, W/pw)`。
3. squeeze 时间维得到 `(B, embed_dim, H/ph, W/pw)`。
4. 二维 Transformer 输出同分辨率特征。
5. 全连接映射为每个 patch 的像素与变量通道。
6. reshape 为 `(B, out_chans, H_patch, W_patch)`。
7. 插值到 `img_size[1:]`。

## 常见修改点

- 修改 `img_size` 和 `patch_size` 以支持不同历史窗口和空间分辨率。
- 若需要保留多个未来时间步，应改造 `fc` 输出和 reshape 逻辑。
- 调整 `embed_dim`、`num_heads`、`window_size` 可改变容量和局部注意力范围。
- 可借鉴 FourCastNet 的二维 token 处理方式替换主干，也可借鉴 Pangu 引入三维压力层维度。

## 实现风险

- 当前强约束 `patch_size[0] == img_size[0]`，否则初始化直接抛错。
- `Height // PatchHeight` 与 `Width // PatchWidth` 使用整除，非整除网格可能丢失边界信息。
- `F.interpolate` 会掩盖 patch 恢复尺寸与目标尺寸不一致的问题，应在训练配置中显式校验。
- `embed_dim=1536` 对显存和吞吐要求较高。

## 启动方式

Python API 启动示例：

```sh
python -c "import torch; from onescience.models.fuxi import Fuxi; model=Fuxi(img_size=(2,721,1440), patch_size=(2,4,4), in_chans=70, out_chans=70, embed_dim=1536, num_groups=32, num_heads=8, window_size=7); x=torch.randn(1,70,2,721,1440); y=model(x); print(y.shape)"
```

## 输入模式

- 输入应组织为五维张量 `(Batch, Channels, TimeSteps, Height, Width)`。
- 默认参数：`img_size=(2, 721, 1440)`，`patch_size=(2, 4, 4)`，`in_chans=70`，`out_chans=70`，`embed_dim=1536`，`num_groups=32`，`num_heads=8`，`window_size=7`。
- 默认输入 shape：`(Batch, 70, 2, 721, 1440)`。
- 时间维必须与 patch 时间长度一致。
- 通道应包含模型训练时定义的气象变量集合。
- 数据预处理需在调用前完成，包括归一化、缺测值填补、经纬网格对齐。

## 运行时接口

- `forward(x)`：执行从多时间步输入到单个二维预测场的推理。

## 主要函数

- `forward`

## 运行资源

- 默认配置适合 GPU 运行，尤其是 `embed_dim=1536` 时。
- CPU 可用于小尺寸调试，但不适合默认全球分辨率。
- 依赖 OneScience 模块中的 Fuxi embedding、transformer 和全连接恢复组件。

## 运行限制

- 当前实现只输出单个二维目标场。
- 不支持 batch 内不同时间步长度。
- 输入时间步与 patch 时间步不一致会直接失败。
- 非训练分辨率运行时，需要重新检查位置、patch 和插值恢复是否一致。

## 规划决策

### 描述

Fuxi 规划知识用于选择和编排多时间步二维气象场预测流程，重点判断是否适合把时间维一次性压入 patch embedding 后交给二维空间主干处理。

### 适用场景

- 输入是固定长度历史序列，输出是单个未来二维气象场。
- 任务更关注空间场恢复，而不是显式逐层三维大气建模。
- 需要较强模型容量处理多变量全球场。

### 输入

- 历史时间步数。
- 输入/输出变量通道数。
- 空间网格尺寸和 patch 尺寸。
- 目标预报步长与归一化统计量。

### 输出

- 单个预测二维场张量。
- 可供后续反归一化、指标计算或滚动预报模块消费。

### 流程

1. 确认 `TimeSteps == PatchTimeSteps`。
2. 将数据整理为 `(B,C,T,H,W)`。
3. 实例化 Fuxi 并加载对应权重。
4. 执行 `forward` 得到 `(B,out_chans,H,W)`。
5. 做变量范围校验和反归一化。

### 约束

- 当前实现不输出时间序列。
- patch 空间尺寸应与训练配置一致。
- 插值恢复可能改变局地极值，需要在降水、风速等变量上额外评估。

### 下一阶段建议

- 增加配置驱动的 API 包装器，固定变量顺序和时间窗口。
- 为多步预报添加外层循环或改造输出头。
- 对边界尺寸和非整除 patch 情况补充测试。

### 备选方案

- 若任务需要显式高空压力层建模，优先考虑 Pangu 或 FengWu。
- 若只需要单帧二维场且追求频域混合，可考虑 FourCastNet。
- 若时间维长度变化频繁，应在数据层补齐或改造 embedding。

## 组件契约入口

- ../contracts/fuxiembedding.md
- ../contracts/fuxitransformer.md
- ../contracts/fuxidownsample.md
- ../contracts/fuxiupsample.md
- ../contracts/fuxifc.md

## 源码锚点

- `{onescience_path}/onescience/src/onescience/models/fuxi/fuxi.py`
- `{onescience_path}/onescience/src/onescience/modules/transformer/fuxitransformer.py`
- `{onescience_path}/onescience/src/onescience/modules/embedding/fuxiembedding.py`
- `{onescience_path}/onescience/src/onescience/modules/sample/fuxidownsample.py`
- `{onescience_path}/onescience/src/onescience/modules/sample/fuxiupsample.py`
- `{onescience_path}/onescience/src/onescience/modules/fc/fuxifc.py`
