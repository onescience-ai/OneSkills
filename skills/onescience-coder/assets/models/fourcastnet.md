# Model Card: fourcastnet

## 基本信息

- 模型名：`fourcastnet`
- 任务类型：`model`
- 当前状态：`public`
- 主实现文件：`{onescience_path}/onescience/src/onescience/models/fourcastnet/fourcastnet.py`

## 模型架构概览

FourCastNet 是二维 patch 预测模型，核心思想是在 patch 网格上做频域混合，再恢复为完整气象场。
输入不包含压力层维度，主干不是注意力 Transformer，而是 AFNO 频域混合加逐位置前馈网络。关键调用约定是 embedding 输出展平 token 序列，进入 trunk 前必须恢复为二维 patch 网格。

## 参数规模

- 默认输入尺寸 `(720, 1440)`，patch `(8, 8)`，patch 网格为 `90 x 180`。
- 默认 `in_chans=19`，`out_chans=19`，`embed_dim=768`，`depth=12`。
- 默认 AFNO 分块数 `num_blocks=8`。
- 参数主要集中在 patch embedding、12 层 fuser 与线性恢复头。

## 架构结构

```text
输入通道组织
  x: (Batch, Channels, Height, Width)
    默认 Channels=19
    默认 Height=720, Width=1440

二维 patch embedding
  x
    -> OneEmbedding(style="FourCastNetEmbedding", patch_size=(8, 8), embed_dim=768)
    -> (Batch, 16200, 768)

位置编码与网格恢复
  patch tokens
    -> + pos_embed: (1, 16200, 768)
    -> dropout
    -> reshape
    -> (Batch, 90, 180, 768)

AFNO patch-grid trunk
  (Batch, 90, 180, 768)
    -> OneFuser(style="FourCastNetFuser") block 1
       内部: FourCastNetAFNO2D + FourCastNetFC
    -> FourCastNetFuser block 2
    -> ...
    -> FourCastNetFuser block 12
    -> (Batch, 90, 180, 768)

patch 输出头与恢复
  trunk 输出
    -> linear head
    -> (Batch, 90, 180, out_chans * 8 * 8)
    -> einops.rearrange
    -> (Batch, out_chans, 720, 1440)
```

## 输入模式

- `x`: `(Batch, in_chans, Height, Width)`。
- 默认 `Height=720`，`Width=1440`。
- `Height` 和 `Width` 应能被 patch 尺寸整除，以避免 token 与恢复网格不一致。

## 输出模式

- 输出：`(Batch, out_chans, Height, Width)`。
- 输出网格由 patch 恢复得到，不额外插值。

## 形状转换

1. 输入 `(B,C,H,W)`。
2. patch embedding 得到 `(B, num_patches, embed_dim)`。
3. 加位置编码并 dropout。
4. reshape 为 `(B, H/ph, W/pw, embed_dim)`。
5. 逐层 fuser 保持 patch 网格尺寸。
6. 线性头输出 `(B, H/ph, W/pw, ph*pw*out_chans)`。
7. 重排为 `(B,out_chans,H,W)`。

## 常见修改点

- 修改 `in_chans/out_chans` 支持不同变量集合。
- 修改 `patch_size` 在分辨率、速度和局地细节之间折中。
- 调整 `depth`、`embed_dim`、`mlp_ratio` 改变模型容量。
- 调整 `num_blocks`、`sparsity_threshold`、`hard_thresholding_fraction` 影响频域混合行为。
- 可借鉴 Fuxi 添加时间 patch 维度，支持多历史步输入。

## 实现风险

- 位置编码长度与 patch 数必须一致，变更分辨率需重建或插值位置编码。
- `rearrange` 假设 patch 网格严格匹配输入尺寸。
- AFNO 稀疏阈值过高可能损失小尺度天气信号。
- 当前模型不显式建模压力层或变量族结构。
- `embed_dim` 必须能被 AFNO 的 `num_blocks` 整除。

## 启动方式

Python API 启动示例：

```sh
python -c "import torch; from onescience.models.fourcastnet import FourCastNet; model=FourCastNet(img_size=(720,1440), patch_size=(8,8), in_chans=19, out_chans=19, embed_dim=768, depth=12, mlp_ratio=4.0, drop_rate=0.0, drop_path_rate=0.0, num_blocks=8, sparsity_threshold=0.01, hard_thresholding_fraction=1.0); x=torch.randn(1,19,720,1440); y=model(x); print(y.shape)"
```

## 输入模式

- 输入为四维张量 `(Batch, Channels, Height, Width)`。
- 默认参数：`img_size=(720, 1440)`，`patch_size=(8, 8)`，`in_chans=19`，`out_chans=19`，`embed_dim=768`，`depth=12`，`mlp_ratio=4.0`，`drop_rate=0.0`，`drop_path_rate=0.0`，`num_blocks=8`，`sparsity_threshold=0.01`，`hard_thresholding_fraction=1.0`。
- 默认输入 shape：`(Batch, 19, 720, 1440)`。
- 通道顺序需与训练数据一致。
- 空间尺寸应与模型实例化的 `img_size` 一致。
- 数据应提前完成标准化和缺测处理。

## 运行时接口

- `forward(x)`：执行二维气象场预测。
- `no_weight_decay()`：返回不参与权重衰减的参数名集合。

## 主要函数

- `forward`
- `no_weight_decay`

## 运行资源

- 默认全球分辨率适合 GPU 推理。
- 相比三维图模型，调用接口简单，适合批量二维场推理。
- 依赖 OneScience 的 FourCastNet embedding 与 fuser 组件。

## 运行限制

- 不处理时间序列输入。
- 不内置滚动预报、变量反归一化或物理约束。
- 变更输入分辨率时需要同步处理位置编码和 patch 网格。
- patch 不整除输入尺寸时恢复阶段容易失败。

## 规划决策

### 描述

FourCastNet 规划知识用于在二维全球天气场预测中选择频域 patch 主干，并指导变量集合、分辨率和推理吞吐之间的取舍。

### 适用场景

- 输入和输出都是单时刻二维气象场。
- 需要快速处理大范围规则经纬网格。
- 任务可以接受 patch 级建模，不要求显式三维压力层结构。
- 希望利用频域混合捕捉长距离空间依赖。

### 输入

- 输入变量通道数与输出变量通道数。
- 经纬网格尺寸和 patch 尺寸。
- 预报步长、归一化统计量和权重文件。
- 是否需要批量推理或滚动调用。

### 输出

- 与输入网格对齐的二维预测场。
- 下游可用于指标评估、可视化或下一步滚动输入。

### 流程

1. 校验 `img_size` 可被 `patch_size` 整除。
2. 实例化模型并加载对应权重。
3. 将输入整理为 `(B,C,H,W)`。
4. 调用 `forward`。
5. 反归一化并检查变量范围。

### 约束

- 位置编码绑定 patch 数。
- 输出空间分辨率由 patch 恢复决定，不额外修正边界。
- 模型不区分地表变量和高空变量结构。

### 下一阶段建议

- 为不同分辨率准备位置编码插值或重新训练方案。
- 封装滚动预报脚本，管理每一步输入输出变量映射。
- 在极端天气变量上评估频域稀疏阈值的影响。

### 备选方案

- 若需要多时间步输入，转向 Fuxi 或扩展 embedding。
- 若需要压力层和地表变量分开建模，转向 Pangu 或 FengWu。
- 若 patch 恢复出现尺寸问题，先回到训练分辨率验证权重和配置。

## 组件契约入口

- ../contracts/fourcastnetembedding.md
- ../contracts/fourcastnetfuser.md
- ../contracts/fourcastnetafno.md
- ../contracts/fourcastnetfc.md

## 源码锚点

- `{onescience_path}/onescience/src/onescience/models/fourcastnet/fourcastnet.py`
- `{onescience_path}/onescience/src/onescience/modules/fuser/fourcastnetfuser.py`
- `{onescience_path}/onescience/src/onescience/modules/afno/fourcastnetafno.py`
- `{onescience_path}/onescience/src/onescience/modules/embedding/fourcastnetembedding.py`
- `{onescience_path}/onescience/src/onescience/modules/fc/fourcastnetfc.py`
