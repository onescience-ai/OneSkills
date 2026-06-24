# Model Card: fengwu

## 基本信息

- 模型名：`fengwu`
- 任务类型：`model`
- 当前状态：`public`
- 主实现文件：`{onescience_path}/onescience/src/onescience/models/fengwu/fengwu.py`

## 模型架构概览

FengWu 是一个面向全球中期天气预报的多分支编码-融合-解码模型。主模型为 `Fengwu`，以地表变量和五类高空变量为独立分支，先在各自二维空间内编码，再把六个变量族作为三维变量轴送入统一融合器。
它最重要的结构特点是多分支 2D encoder/decoder 加一个中分辨率 3D fuser：变量族不在输入端直接拼成单一路径，而是在中分辨率 token 层面执行跨变量融合。

## 参数规模

- 默认 `embed_dim=192`，编码后中分辨率特征维度为 `embed_dim * 2`。
- 默认包含 6 个编码器、1 个跨变量融合器、6 个解码器。
- 默认高空压力层数为 `pressure_level=37`，每个高空变量分支输出 37 个通道。
- 主干深度由各 `OneEncoder`、`OneFuser`、`OneDecoder` 的内部实现决定，源码中使用 8 段 drop path 配置。

## 架构结构

```text
输入分支组织
  surface: (Batch, 4, Height, Width)
    4 个地表预报变量
  z: (Batch, pressure_level, Height, Width)
    位势高度变量族，默认 pressure_level=37
  r: (Batch, pressure_level, Height, Width)
    相对湿度变量族，默认 pressure_level=37
  u: (Batch, pressure_level, Height, Width)
    纬向风变量族，默认 pressure_level=37
  v: (Batch, pressure_level, Height, Width)
    经向风变量族，默认 pressure_level=37
  t: (Batch, pressure_level, Height, Width)
    温度变量族，默认 pressure_level=37

独立二维 encoder
  surface
    -> OneEncoder(style="FengWuEncoder", in_chans=4)
    -> feature_surface: (Batch, 91 * 180, 384)
    -> skip_surface   : (Batch, 181, 360, 192)

  z / r / u / v / t
    -> 各自的 OneEncoder(style="FengWuEncoder", in_chans=pressure_level)
    -> feature_*: (Batch, 91 * 180, 384)
    -> skip_*   : (Batch, 181, 360, 192)

跨变量三维融合
  concat on Variables
    -> (Batch, 6, 91 * 180, 384)
    -> flatten token
    -> (Batch, 6 * 91 * 180, 384)
    -> OneFuser(style="FengWuFuser", input_resolution=(6, 91, 180))
    -> (Batch, 6 * 91 * 180, 384)
    -> reshape by Variables
    -> surface/z/r/u/v/t feature branches

分支解码与输出
  [feature_surface, skip_surface]
    -> OneDecoder(style="FengWuDecoder", out_chans=4)
    -> surface: (Batch, 4, 721, 1440)

  [feature_z, skip_z] / [feature_r, skip_r] / [feature_u, skip_u] / [feature_v, skip_v] / [feature_t, skip_t]
    -> 各自的 OneDecoder(style="FengWuDecoder", out_chans=pressure_level)
    -> z/r/u/v/t: (Batch, 37, 721, 1440)
```

## 输入模式

- `surface`: `(Batch, 4, Height, Width)`。
- `z`: `(Batch, pressure_level, Height, Width)`。
- `r`: `(Batch, pressure_level, Height, Width)`。
- `u`: `(Batch, pressure_level, Height, Width)`。
- `v`: `(Batch, pressure_level, Height, Width)`。
- `t`: `(Batch, pressure_level, Height, Width)`。
- 默认空间尺寸为 `(721, 1440)`，默认 `patch_size=(4, 4)`。

## 输出模式

- 返回六元组：`(surface, z, r, u, v, t)`。
- 每个输出与对应输入分支保持相同的变量通道与空间尺寸。

## 形状转换

1. 每个二维输入分支经编码器从原始分辨率变为 patch token。
2. 编码器内部形成 `input_resolution=(ceil(H/ph), ceil(W/pw))` 与 `middle_resolution=(ceil(input_h/2), ceil(input_w/2))`。
3. 六个分支特征堆叠为 `(Batch, Variables=6, NumTokensPerVariable, Channels)`。
4. reshape 为 `(Batch, Variables * NumTokensPerVariable, Channels)` 后送入三维融合器。
5. 融合后再拆回六个分支，并与各自 skip 特征一起送入解码器。
6. 解码器恢复到原始二维网格。

## 常见修改点

- 调整 `pressure_level` 以适配不同气压层集合。
- 修改地表或高空变量分支时，需要同步调整编码器输入通道、融合器变量轴长度和解码器输出通道。
- 修改 `patch_size` 可改变 token 数量和计算开销。
- 调整 `window_size` 与 `num_heads` 可改变跨变量融合感受野。
- 可借鉴 Pangu 的单流拼接方式，将多分支输入合并为统一 token 流，但会牺牲 FengWu 当前按变量族建模的清晰边界。

## 实现风险

- 六个分支的 token 数量必须一致，否则融合前 concat/reshape 会失败。
- `img_size` 与 `patch_size` 使用 `ceil` 推导分辨率，恢复阶段需要确认边界填充或裁剪逻辑符合数据网格。
- 高空变量通道必须等于 `pressure_level`，否则分支编码器输入不匹配。
- 修改变量数时若只改输入不改 `FengWuFuser` 的 `input_resolution=(6, ...)`，会导致三维融合器形状错误。

## 启动方式

Python API 启动示例：

```sh
python -c "import torch; from onescience.models.fengwu import Fengwu; model=Fengwu(img_size=(721,1440), pressure_level=37, embed_dim=192, patch_size=(4,4), num_heads=(6,12,12,6), window_size=(2,6,12)); surface=torch.randn(1,4,721,1440); z=torch.randn(1,37,721,1440); r=torch.randn(1,37,721,1440); u=torch.randn(1,37,721,1440); v=torch.randn(1,37,721,1440); t=torch.randn(1,37,721,1440); y=model(surface,z,r,u,v,t); print([o.shape for o in y])"
```

## 输入模式

- 准备 6 个张量，分别对应地表变量和 `z/r/u/v/t` 五类高空变量。
- 默认参数：`img_size=(721, 1440)`，`pressure_level=37`，`embed_dim=192`，`patch_size=(4, 4)`，`num_heads=(6, 12, 12, 6)`，`window_size=(2, 6, 12)`。
- 默认输入 shape：`surface=(Batch, 4, 721, 1440)`，`z/r/u/v/t=(Batch, 37, 721, 1440)`。
- 所有张量必须共享同一批大小、纬向网格数和经向网格数。
- 高空变量应预先按变量族拆分，每个张量通道数等于 `pressure_level`。
- 输入值应已完成归一化、缺测处理和网格对齐。

## 运行时接口

- `forward(surface, z, r, u, v, t)`：执行一次多变量天气场预测。

## 主要函数

- `forward`

## 运行资源

- 推荐 GPU 推理或训练，默认全球分辨率与多分支结构显存占用较高。
- 可使用混合精度推理；元数据中标记支持 GPU ONNX runtime 与 cuda graphs。
- 运行环境需具备 OneScience 模块及其气象网络组件。

## 运行限制

- 不直接负责数据读取、归一化、反归一化或滚动预报调度。
- 默认仅覆盖 4 个地表通道和 5 类高空变量分支。
- 变量顺序、压力层顺序、空间网格必须与训练时一致。
- 常见失败模式包括通道数不匹配、不同分支空间尺寸不一致、patch 配置导致恢复尺寸异常。

## 规划决策

### 描述

FengWu 规划知识用于指导 agent 在全球多变量中期天气预报任务中选择、配置和调用多分支跨变量融合模型，并在变量族、压力层、空间分辨率发生变化时做出改造判断。


### 适用场景

- 需要同时预测地表变量和多个高空变量族。
- 任务强调跨变量耦合，但仍希望保留每类变量的独立编码和解码路径。
- 输入已经被整理为 surface、z、r、u、v、t 六个张量。
- 中期或多步滚动预报中需要稳定的主干模型。

### 输入

- 数据网格尺寸与 `img_size`。
- 地表变量数、高空变量族与压力层数。
- 训练或推理模式、目标 lead time、是否滚动调用。
- 归一化统计量、变量顺序和压力层顺序。

### 输出

- 六个预测张量，对应输入六个变量分支。
- 下游可进一步合并为统一气象场、写入 NetCDF/Zarr，或作为下一步滚动预报输入。

### 流程

1. 校验输入变量族、通道数、空间网格和压力层顺序。
2. 按默认或任务配置实例化 `Fengwu`。
3. 将六个输入张量放到同一设备并执行推理。
4. 校验输出 shape 与物理变量范围。
5. 若做滚动预报，将输出按变量族重新组织为下一步输入。

### 约束

- 六个分支必须具有相同空间分辨率。
- 高空分支通道数必须与 `pressure_level` 一致。
- 修改变量族数量时必须同步改融合器三维变量轴。
- 模型不内置物理约束修正，异常值需要后处理。

### 下一阶段建议

- 为生产推理封装统一的数据适配器，显式记录变量顺序和标准化统计量。
- 增加滚动预报控制器，管理 lead time、检查点和中间结果落盘。
- 对改造后的变量配置补充 shape 单元测试。

### 备选方案

- 若多分支输入难以构造，可退回 Pangu 类单张量输入范式。
- 若显存不足，优先降低 batch size，再考虑增大 patch 或降低 `embed_dim`。
- 若某个高空变量族缺失，应先用数据同化或插值补齐，不建议直接以零张量替代。

## 组件契约入口

- ../contracts/fengwuencoder.md
- ../contracts/fengwufuser.md
- ../contracts/fengwudecoder.md
- ../contracts/panguembedding.md
- ../contracts/pangudownsample.md
- ../contracts/panguupsample.md
- ../contracts/pangupatchrecovery.md

## 源码锚点

- `{onescience_path}/onescience/src/onescience/models/fengwu/fengwu.py`
- `{onescience_path}/onescience/src/onescience/modules/encoder/fengwuencoder.py`
- `{onescience_path}/onescience/src/onescience/modules/fuser/fengwufuser.py`
- `{onescience_path}/onescience/src/onescience/modules/decoder/fengwudecoder.py`
- `{onescience_path}/onescience/src/onescience/modules/embedding/panguembedding.py`
- `{onescience_path}/onescience/src/onescience/modules/sample/pangudownsample.py`
- `{onescience_path}/onescience/src/onescience/modules/sample/panguupsample.py`
- `{onescience_path}/onescience/src/onescience/modules/recovery/pangupatchrecovery.py`
