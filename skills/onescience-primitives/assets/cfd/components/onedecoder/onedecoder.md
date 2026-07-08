# Contract: OneDecoder

## 基本信息

- 组件名：`OneDecoder`
- 所属模块族：`decoder`
- 统一入口：`OneDecoder`
- 注册名：`style="OneDecoder"`

## 组件说明
OneDecoder 位于 decoder 模块，是把隐空间表征恢复为网格、节点、token 或原子坐标相关输出的统一入口。它的关键特征是轻量 wrapper、按 style 延迟实例化、运行时参数透传，并保持底层解码器的原始返回结构。

## 用途
- 做什么：统一创建和调用不同家族的解码器。
- 解决问题：上层模型无需直接 import UNetDecoder、GraphViTDecoder、MeshGraphDecoder、FengWuDecoder 或 ProtenixAtomAttentionDecoder。
- 适用场景：多尺度 U-Net 重建、图节点状态恢复、天气模型 token 解码、蛋白原子坐标更新。
- 不适用场景：单独完成完整预测头、损失计算或数据反归一化。

## 输入规格
输入由 style 决定：

UNetDecoder*d
  features/skips: 与对应 UNetEncoder*d 输出尺度顺序一致

GraphViTDecoder
  cluster token、节点特征、cluster 索引、位置编码、边与边表征

MeshGraphDecoder
  图隐状态或节点隐特征

FengWuDecoder / ProtenixAtomAttentionDecoder
  对应模型内部 token、skip 或 atom 表征

## 输出规格
输出由底层 decoder 决定；UNet 分支通常输出恢复空间分辨率后的特征图，Graph/Mesh 分支通常输出节点状态或增量，Protenix 分支输出原子注意力解码相关表征。

## 参数
- `style`：例如 `UNetDecoder2D`、`GraphViTDecoder`、`MeshGraphDecoder`、`FengWuDecoder`、`ProtenixAtomAttentionDecoder`。
- `**kwargs`：透传到底层 decoder。常见参数包括 `base_channels`、`num_stages`、`bilinear`、`normtype`、`kernel_size`、`w_size`、`state_size`、隐藏维度等。
- 典型值：规则 CFD 场恢复使用 `UNetDecoder2D/3D`；非结构图状态恢复使用 `MeshGraphDecoder`；FengWu 主模型使用 `FengWuDecoder`。

## 关键依赖
- _lazy.py
- unet_decoder.py
- graphvit_decoder.py
- mesh_graph_decoder.py
- fengwudecoder.py
- protenixdecoder.py

## 使用注意与风险
- decoder 与 encoder 参数必须匹配，尤其是尺度数、通道数和 skip 顺序。
- GraphViT/MeshGraph 解码输出可能是状态增量，不一定是最终物理量。
- ProtenixAtomAttentionDecoder 需要 atom encoder 提供的配套 skip 表征。
- style 未注册或 kwargs 不匹配会在实例化阶段失败。

## 启动方式
Python API 启动，调用方按目标 style 传入底层实现参数：

``` sh
python -c "from onescience.modules.decoder.onedecoder import OneDecoder; m=OneDecoder(style='UNetDecoder2D'); print(type(m).__name__)"
```

在模型 pipeline 中通常由上层模型构造函数实例化，不单独提供 CLI。

## 输入规格
从 encoder 或 processor 准备与 decoder family 匹配的特征：U-Net 需要多尺度 skip，图解码需要节点/边和拓扑索引，天气 token 解码需要模型约定的 token 排布。

## 运行接口
- 构造接口：`OneDecoder(style, **kwargs)`。
- 调用接口：`decoder(*args, **kwargs)` 透传到底层。
- 属性访问：未命中的属性转发到底层 decoder。

## 主要函数
- `forward`

## 执行资源
U-Net 解码器显存随空间分辨率和 skip 数增长；图解码器依赖图数据结构和节点数；Protenix 解码器通常面向 GPU 推理或训练。

## 操作限制
不自动适配 encoder 输出，不执行物理量反归一化，不保证不同 decoder 输出语义一致。

## 规划决策

### 描述
将 OneDecoder 作为隐表征到输出空间的恢复阶段，规划时优先确认上游表征来源和下游 loss/head 期望。

### 使用时机
当模型已经得到 trunk/processor 隐状态，需要按配置切换具体解码器时使用。

### 输入
- 上游 encoder/processor 的输出结构。
- 目标输出是网格场、节点状态、状态增量还是 atom 表征。
- 维度、尺度数、通道数、skip 顺序。
- 下游 head 或 loss 对输出的约束。

### 输出
- decoder style 与参数。
- 输入字段映射。
- 输出 shape/语义说明。
- 与后续 head 或 rollout 的连接策略。

### 执行步骤
1. 匹配 encoder family。
2. 核对隐藏维度、尺度数和拓扑字段。
3. 构造 OneDecoder。
4. 用样例 batch 验证输出是否能接入 head/loss。
5. 记录输出是绝对物理量还是增量。

### 约束
不要跨 family 混用 encoder/decoder；Graph decoder 需要图拓扑；U-Net decoder 需要尺度对齐的 skip。

### 下一阶段建议
为目标模型补充端到端 shape smoke test，并明确 decoder 输出到物理变量的映射。

### 回退策略
若 shape 不匹配，先回退到对应 encoder-decoder 成对实现；若图字段缺失，改用网格 decoder 或补齐构图预处理。

## 源码锚点

- `{onescience_path}/onescience/src/onescience/modules/decoder/onedecoder.py`
- `{onescience_path}/onescience/src/onescience/modules/decoder/fengwudecoder.py`
- `{onescience_path}/onescience/src/onescience/modules/decoder/unet_decoder.py`
- `{onescience_path}/onescience/src/onescience/modules/decoder/graphvit_decoder.py`
- `{onescience_path}/onescience/src/onescience/modules/decoder/protenixdecoder.py`
