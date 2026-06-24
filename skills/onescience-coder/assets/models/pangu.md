# Model Card: pangu

## 基本信息

- 模型名：`pangu`
- 任务类型：`model`
- 当前状态：`public`
- 主实现文件：`{onescience_path}/onescience/src/onescience/models/pangu/pangu.py`

## 模型架构概览

Pangu 是统一三维 token 流的全球天气预报模型。它将地表分支补成一个压力层位置，再与 13 层高空变量 patch token 拼接，形成三维大气网格。
主干不是 surface / upper-air 两套完全分离的 encoder，而是统一的 3D token trunk；surface patch token 先补一个 `PressureLevels=1`，再与 upper-air patch token 沿压力层维拼接。

## 参数规模

- 默认 `embed_dim=192`。
- 主干分四段，深度分别为 2、6、6、2。
- 默认注意力头为 `(6, 12, 12, 6)`。
- 默认高空变量为 5 类、13 个压力层；地表输入 7 通道，地表输出 4 通道。

## 架构结构

```text
输入通道组织
  x: (Batch, 4 + 3 + 5 * 13, Height, Width)
    前 4 通道       -> 待预测 surface 变量
    接下来 3 通道   -> 静态 mask
    剩余 65 通道    -> upper-air 变量按 5 类 * 13 层展平

输入拆分
  SurfaceInput  : (Batch, 7, 721, 1440)
  UpperAirInput : (Batch, 5, 13, 721, 1440)

patch embedding
  SurfaceInput
    -> OneEmbedding(style="PanguEmbedding")
    -> (Batch, 192, 181, 360)
    -> unsqueeze(PressureLevels)
    -> (Batch, 192, 1, 181, 360)

  UpperAirInput
    -> OneEmbedding(style="PanguEmbedding")
    -> (Batch, 192, 7, 181, 360)

统一三维 token trunk
  concat on PressureLevels
    -> (Batch, 192, 8, 181, 360)
    -> flatten token
    -> (Batch, 8 * 181 * 360, 192)
    -> layer1: OneFuser(style="PanguFuser")
    -> 保存 SkipTokens
    -> downsample: (Batch, 8 * 91 * 180, 384)
    -> layer2: 深层三维融合
    -> layer3: 深层三维融合
    -> upsample: (Batch, 8 * 181 * 360, 192)
    -> layer4: 高分辨率三维融合

恢复头
  trunk 输出与 SkipTokens 拼接
    -> 通道维变为 384
    -> reshape 回 (Batch, 384, 8, 181, 360)
    -> pressure index 0      -> surface feature
    -> pressure index 1..end -> upper-air feature
    -> PanguPatchRecovery(surface)  -> (Batch, 4, 721, 1440)
    -> PanguPatchRecovery(upper)    -> (Batch, 5, 13, 721, 1440)
```

## 输入模式

- `x`: `(Batch, 4 + 3 + 5 * 13, Height, Width)`。
- 前 4 通道为待预报地表变量。
- 接着 3 通道为静态掩码。
- 剩余 65 通道 reshape 为 `(Batch, 5, 13, Height, Width)`。
- 默认空间尺寸 `(721, 1440)`。

## 输出模式

- 返回二元组 `(output_surface, output_upper_air)`。
- `output_surface`: `(Batch, 4, Height, Width)`。
- `output_upper_air`: `(Batch, 5, 13, Height, Width)`。

## 形状转换

1. 输入按通道拆分为地表与高空。
2. 地表经二维 patch embedding 得到 `(B,C,Hp,Wp)`，再 unsqueeze 为压力层长度 1。
3. 高空经三维 patch embedding 得到 `(B,C,7,Hp,Wp)`。
4. 两者拼接为压力层长度 8 的三维特征。
5. reshape 为 token 序列后进入四段融合主干。
6. 主干输出与 skip token 拼接，通道变为 `embed_dim*2`。
7. 拆出压力层 0 作为地表，其余层作为高空。
8. patch recovery 恢复到目标物理场。

## 常见修改点

- 修改地表变量或静态掩码数量时，需要同步调整输入切片和 `patchembed2d`。
- 修改高空变量数或压力层数时，需要同步调整 reshape、`patchembed3d` 和 recovery。
- 调整 `patch_size` 和 `window_size` 可改变三维感受野与计算量。
- 可借鉴 FengWu 的多分支方式，将变量族分开编码再融合。

## 实现风险

- 输入通道顺序强绑定切片逻辑。
- `patchrecovery2d/3d` 中 `img_size` 写死为 `(721,1440)` 与 `(13,721,1440)`，修改 `img_size` 时需同步改恢复层。
- 地表静态掩码只作为输入，不在输出中恢复。
- 压力层 patch 后长度与地表补层拼接逻辑必须保持一致。

## 启动方式

Python API 启动示例：

```sh
python -c "import torch; from onescience.models.pangu import Pangu; model=Pangu(img_size=(721,1440), patch_size=(2,4,4), embed_dim=192, num_heads=(6,12,12,6), window_size=(2,6,12)); x=torch.randn(1,72,721,1440); ys,yu=model(x); print(ys.shape, yu.shape)"
```

## 输入模式

- 输入为单个四维张量 `(Batch, 72, Height, Width)`。
- 默认参数：`img_size=(721, 1440)`，`patch_size=(2, 4, 4)`，`embed_dim=192`，`num_heads=(6, 12, 12, 6)`，`window_size=(2, 6, 12)`。
- 默认输入 shape：`(Batch, 72, 721, 1440)`，其中 `72 = 4 + 3 + 5 * 13`。
- 通道布局必须是 `4` 个地表预报变量、`3` 个静态掩码、`5*13` 个高空变量。
- 高空变量在通道维展平，模型内部 reshape 为变量与压力层。
- 输入应完成归一化、静态掩码拼接和经纬网格对齐。

## 运行时接口

- `forward(x)`：执行一次 Pangu 三维天气场预测。

## 主要函数

- `forward`

## 运行资源

- 推荐 GPU，默认全球分辨率与三维窗口融合显存开销较大。
- 元数据标记支持 AMP、cuda graphs 和 GPU ONNX runtime。
- 依赖 OneScience 的 embedding、fuser、sample、recovery 组件。

## 运行限制

- 默认只适配 13 个压力层。
- 输出地表变量为 4 通道，不输出输入中的 3 个静态掩码。
- 当前 recovery 层默认绑定 721x1440 网格。
- 通道顺序错误会产生语义错误，即使 shape 能通过。

## 规划决策

### 描述

Pangu 规划知识用于指导 agent 在三维全球大气预测任务中选择统一 token 流模型，并处理地表、静态掩码和高空变量的通道组织。

### 适用场景

- 需要在同一主干中联合建模地表和高空压力层。
- 输入可以被组织为单个拼接张量。
- 任务关注全球高分辨率中短期天气预报。
- 需要显式恢复地表场和高空场两个输出。

### 输入

- 地表变量、静态掩码和高空变量的通道顺序。
- 压力层集合、空间网格尺寸和 patch 配置。
- 预训练权重、归一化统计量和目标预报步长。

### 输出

- 地表预测张量。
- 高空变量预测张量。
- 可用于滚动预报的下一步输入片段。

### 流程

1. 将输入按约定通道顺序拼接为 `(B,72,H,W)`。
2. 校验空间尺寸与 recovery 配置。
3. 实例化 Pangu 并加载权重。
4. 调用 `forward` 得到地表和高空输出。
5. 将输出与静态掩码重新组合，用于后续滚动或后处理。

### 约束

- 默认通道数和压力层数固定。
- 静态掩码必须从外部持续提供。
- 修改分辨率时不能只改初始化参数，还要检查恢复层。

### 下一阶段建议

- 把通道布局写入配置并在运行前自动校验。
- 为不同空间分辨率抽象 recovery 配置。
- 增加输出物理范围检查和滚动预报接口。

### 备选方案

- 若输入天然是多分支变量族，改用 FengWu 可减少通道重排。
- 若只需要二维场预测，改用 FourCastNet 或 Fuxi。
- 若 recovery 尺寸不匹配，先使用默认训练分辨率验证端到端流程。

## 组件契约入口

- ../contracts/panguembedding.md
- ../contracts/pangufuser.md
- ../contracts/pangudownsample.md
- ../contracts/panguupsample.md
- ../contracts/pangupatchrecovery.md

## 源码锚点

- `{onescience_path}/onescience/src/onescience/models/pangu/pangu.py`
- `{onescience_path}/onescience/src/onescience/modules/fuser/pangufuser.py`
- `{onescience_path}/onescience/src/onescience/modules/sample/pangudownsample.py`
- `{onescience_path}/onescience/src/onescience/modules/sample/panguupsample.py`
- `{onescience_path}/onescience/src/onescience/modules/recovery/pangupatchrecovery.py`
- `{onescience_path}/onescience/src/onescience/modules/embedding/panguembedding.py`
