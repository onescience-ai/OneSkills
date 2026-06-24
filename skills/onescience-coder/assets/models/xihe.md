# Model Card: xihe

## 基本信息

- 模型名：`xihe`
- 任务类型：`model`
- 当前状态：`public`
- 主实现文件：`{onescience_path}/onescience/src/onescience/models/xihe/xihe.py`

## 模型架构概览

Xihe 是面向全球海洋预报的带掩膜二维 patch 模型。主干先在原 patch 网格上融合，再下采样到低分辨率多次融合，随后上采样回原网格，并与早期特征拼接恢复。
它的核心差异是每个融合阶段都可以接收由海陆掩膜降采样得到的 `TensorWithMask`，用于在海洋有效区域内建模。

## 参数规模

- 默认配置面向高分辨率海洋网格 `(2041, 4320)`。
- 默认 `embed_dim=192`，输入通道 96，输出通道 94。
- 主干包含 5 个 XiheFuser block、一次下采样、一次上采样和一个 skip 投影。
- 实际参数规模由配置对象覆盖的通道数和 embedding 宽度决定。

## 架构结构

```text
配置与输入
  config.img_size   : 默认可为 (2041, 4320)
  config.patch_size : 默认可为 (6, 12)
  config.mask       : numpy 可读取的二维海陆掩膜路径
  x                 : (Batch, in_chans, Height, Width)

patch embedding
  x
    -> OneEmbedding(style="XiheEmbedding")
    -> (Batch, embed_dim, H', W')
    -> flatten + transpose
    -> (Batch, H' * W', embed_dim)

第一尺度掩膜融合
  mask_full
    -> change_mask(mask_full, h_out=H', w_out=W')
    -> mask1: (Batch, 1, H', W')

  TensorWithMask(x, mask1)
    -> block1: OneFuser(style="XiheFuser", dim=embed_dim, num_local=1)
    -> x1: (Batch, H' * W', embed_dim)

低分辨率融合
  x1
    -> PanguDownSample
    -> (Batch, H'/2 * W'/2, 2 * embed_dim)

  mask_full
    -> change_mask(mask_full, h_out=H'/2, w_out=W'/2)
    -> mask2

  TensorWithMask(x, mask2)
    -> block2
    -> block3
    -> block4
    -> (Batch, H'/2 * W'/2, 2 * embed_dim)

上采样与 skip 融合
  low-resolution feature
    -> XiheUpSample
    -> (Batch, H' * W', embed_dim)
    -> TensorWithMask(x, mask1)
    -> block5
    -> concat with x1 on channel dim
    -> skip_proj: 2 * embed_dim -> embed_dim

输出恢复
  projected feature
    -> transpose + reshape
    -> (Batch, embed_dim, H', W')
    -> OneRecovery(style="XihePatchRecovery")
    -> (Batch, out_chans, Height, Width)
```

## 输入模式

- `x`: 通常为 `(Batch, in_chans, Height, Width)`。
- `config` 需要提供 `img_size`、`patch_size`、`mask`、`out_chans`、`in_chans`、`num_groups`、`embed_dim`。
- `mask` 指向可由 `numpy.load` 读取的二维海陆掩膜。

## 输出模式

- 输出为二维海洋变量预测场，通道数由 `config.out_chans` 控制。
- 空间尺寸由 `XihePatchRecovery` 的实现与配置共同决定。

## 形状转换

1. 输入经 patch embedding 得到 `(B, embed_dim, H', W')`。
2. flatten/transpose 为 `(B, H'*W', embed_dim)`。
3. 全分辨率 mask 聚合为 `(B,1,H',W')` 并随 TensorWithMask 传入 block。
4. 下采样至 `(H'/2, W'/2)` 级别，特征维变为 `2*embed_dim`。
5. 低分辨率 mask 聚合后执行三段融合。
6. 上采样回 `(H',W')`，特征维回到 `embed_dim`。
7. 与 block1 输出拼接为 `2*embed_dim`，再投影回 `embed_dim`。
8. reshape 回 `(B,embed_dim,H',W')` 并 patch recovery。

## 常见修改点

- 修改 `config.in_chans/out_chans` 以适配不同海洋变量集合。
- 修改 `mask` 路径或 `change_mask` 聚合逻辑以适配不同海陆掩膜。
- 调整 `patch_size` 在高分辨率细节与计算开销之间折中。
- 调整 block 数或 `embed_dim` 改变模型容量。
- 可借鉴 Pangu 的下采样/上采样结构，但保留 Xihe 的海陆掩膜传递机制。

## 实现风险

- 构造函数参数中同时存在默认值和 `config` 覆盖，实际以 `config` 为准。
- `mask_full` 通过路径加载，路径不存在或 shape 不匹配会失败。
- `change_mask` 使用 Python 循环聚合高分辨率掩膜，超大网格下可能较慢。
- 下采样时使用 `H_out // 2`、`W_out // 2`，奇数 patch 网格可能有边界风险。
- `OneFuser` 接收 `TensorWithMask`，替换 fuser 时需保持接口兼容。

## 启动方式

Python API 启动示例：

```sh
python -c "import torch; from types import SimpleNamespace; from onescience.models.xihe import Xihe; cfg=SimpleNamespace(img_size=(2041,4320), patch_size=(6,12), mask='mask.npy', out_chans=94, in_chans=96, num_groups=32, embed_dim=192); model=Xihe(config=cfg, img_size=(2041,4320), patch_size=(6,12), window_size=(6,12), embed_dim=192, num_heads=(6,12,12,6), in_chans=96, depth=1, mask_full=None, out_chans=94, num_groups=32); x=torch.randn(1,96,2041,4320); y=model(x); print(y.shape)"
```

## 输入模式

- 输入为海洋变量二维场，通常形状 `(Batch, in_chans, Height, Width)`。
- 构造函数默认参数：`img_size=(2041, 4320)`，`patch_size=(6, 12)`，`window_size=(6, 12)`，`embed_dim=192`，`num_heads=(6, 12, 12, 6)`，`in_chans=96`，`depth=1`，`mask_full=None`，`out_chans=94`，`num_groups=32`。
- 实际运行以 `config` 字段覆盖为准；示例默认配置为 `config.img_size=(2041, 4320)`，`config.patch_size=(6, 12)`，`config.mask="mask.npy"`，`config.out_chans=94`，`config.in_chans=96`，`config.num_groups=32`，`config.embed_dim=192`。
- 默认输入 shape：`(Batch, 96, 2041, 4320)`。
- 配置对象必须提供模型所需尺寸、通道和掩膜路径。
- 掩膜文件应为二维数组，海洋区域为正值或大于 0.5。
- 输入变量需预先完成归一化和网格对齐。

## 运行时接口

- `forward(x)`：执行海洋变量预测。
- `change_mask(mask_full, x, h_out, w_out)`：将全分辨率掩膜降采样到当前 token 网格。

## 主要函数

- `forward`
- `change_mask`

## 运行资源

- 默认高分辨率海洋网格显存需求很高，推荐 GPU。
- 掩膜聚合在 CPU/GPU 张量之间转换，需注意设备和 dtype。
- 依赖外部 mask 文件和 OneScience 的 Xihe 组件。

## 运行限制

- 启动示例中的 `mask.npy` 必须替换为真实可读掩膜文件。
- 当前实现高度依赖配置对象字段。
- 不内置海洋数据读取、陆地区域后处理或物理守恒修正。
- 高分辨率默认网格可能不适合直接在小显存设备运行。

## 规划决策

### 描述

Xihe 规划知识用于海洋高分辨率预测任务，指导 agent 处理海陆掩膜、变量通道、patch 网格和多尺度融合。

### 适用场景

- 任务是全球或区域海洋变量预测。
- 需要显式利用海陆掩膜避免陆地区域干扰。
- 输入是规则二维海洋网格，变量通道较多。
- 需要保留高分辨率涡旋或海洋中尺度结构。

### 输入

- 海洋变量张量。
- `config` 中的图像尺寸、patch 尺寸、输入输出通道、embedding 宽度。
- 可读取的海陆掩膜文件。
- 预训练权重和归一化统计量。

### 输出

- 海洋变量预测场。
- 可选的后处理产品，如只保留海洋区域或写入网格文件。

### 流程

1. 校验 mask 文件存在、shape 与输入网格一致。
2. 构造配置对象并实例化 Xihe。
3. 将输入张量与模型放到目标设备。
4. 调用 `forward`，内部自动为不同尺度生成掩膜。
5. 对输出执行反归一化和海陆区域后处理。

### 约束

- 掩膜 shape 必须与原始网格对应。
- patch 尺寸会影响掩膜聚合和恢复尺寸。
- 高分辨率默认配置显存压力大。
- 替换 fuser 时必须保留带 mask 的输入约定。

### 下一阶段建议

- 缓存不同尺度 mask，避免每次 forward 重复 Python 循环聚合。
- 将 config 字段校验封装为初始化前检查。
- 为奇数 patch 网格和非默认分辨率补充 shape 测试。

### 备选方案

- 若掩膜不可用，可先用全 1 掩膜验证模型通路，但生产结果不建议这样使用。
- 若显存不足，降低空间分辨率、batch size 或 `embed_dim`。
- 若海陆掩膜逻辑导致失败，可临时绕过 mask 分支定位是否为 fuser 接口问题。

## 组件契约入口

- ../contracts/xiheembedding.md
- ../contracts/xihefuser.md
- ../contracts/pangudownsample.md
- ../contracts/xiheupsample.md
- ../contracts/xihepatchrecovery.md
- ../contracts/tensorwithmask.md

## 源码锚点

- `{onescience_path}/onescience/src/onescience/models/xihe/xihe.py`
- `{onescience_path}/onescience/src/onescience/modules/embedding/xiheembedding.py`
- `{onescience_path}/onescience/src/onescience/modules/fuser/xihefuse.py`
- `{onescience_path}/onescience/src/onescience/modules/fuser/xiheglobalsiefuser.py`
- `{onescience_path}/onescience/src/onescience/modules/fuser/xihelocalsiefuser.py`
- `{onescience_path}/onescience/src/onescience/modules/sample/pangudownsample.py`
- `{onescience_path}/onescience/src/onescience/modules/sample/xiheupsample.py`
- `{onescience_path}/onescience/src/onescience/modules/recovery/xihepatchrecovery.py`
