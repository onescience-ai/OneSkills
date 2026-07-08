# component_info
OneDecoder 位于 decoder 模块，是把隐空间表征恢复为网格、节点、token 或原子坐标相关输出的统一入口。它的关键特征是轻量 wrapper、按 style 延迟实例化、运行时参数透传，并保持底层解码器的原始返回结构。

# purpose
- 做什么：统一创建和调用不同家族的解码器。
- 解决问题：上层模型无需直接 import UNetDecoder、GraphViTDecoder、MeshGraphDecoder、FengWuDecoder 或 ProtenixAtomAttentionDecoder。
- 适用场景：多尺度 U-Net 重建、图节点状态恢复、天气模型 token 解码、蛋白原子坐标更新。
- 不适用场景：单独完成完整预测头、损失计算或数据反归一化。

# input_schema
输入由 style 决定：

UNetDecoder*d
  features/skips: 与对应 UNetEncoder*d 输出尺度顺序一致

GraphViTDecoder
  cluster token、节点特征、cluster 索引、位置编码、边与边表征

MeshGraphDecoder
  图隐状态或节点隐特征

FengWuDecoder / ProtenixAtomAttentionDecoder
  对应模型内部 token、skip 或 atom 表征

# output_schema
输出由底层 decoder 决定；UNet 分支通常输出恢复空间分辨率后的特征图，Graph/Mesh 分支通常输出节点状态或增量，Protenix 分支输出原子注意力解码相关表征。

# parameters
- `style`：例如 `UNetDecoder2D`、`GraphViTDecoder`、`MeshGraphDecoder`、`FengWuDecoder`、`ProtenixAtomAttentionDecoder`。
- `**kwargs`：透传到底层 decoder。常见参数包括 `base_channels`、`num_stages`、`bilinear`、`normtype`、`kernel_size`、`w_size`、`state_size`、隐藏维度等。
- 典型值：规则 CFD 场恢复使用 `UNetDecoder2D/3D`；非结构图状态恢复使用 `MeshGraphDecoder`；FengWu 主模型使用 `FengWuDecoder`。

# key_dependencies
- _lazy.py
- unet_decoder.py
- graphvit_decoder.py
- mesh_graph_decoder.py
- fengwudecoder.py
- protenixdecoder.py

# usage_and_risks
- decoder 与 encoder 参数必须匹配，尤其是尺度数、通道数和 skip 顺序。
- GraphViT/MeshGraph 解码输出可能是状态增量，不一定是最终物理量。
- ProtenixAtomAttentionDecoder 需要 atom encoder 提供的配套 skip 表征。
- style 未注册或 kwargs 不匹配会在实例化阶段失败。

# code_references
- `{onescience_path}/onescience/src/onescience/modules/decoder/onedecoder.py`
- `{onescience_path}/onescience/src/onescience/modules/decoder/fengwudecoder.py`
- `{onescience_path}/onescience/src/onescience/modules/decoder/unet_decoder.py`
- `{onescience_path}/onescience/src/onescience/modules/decoder/graphvit_decoder.py`
- `{onescience_path}/onescience/src/onescience/modules/decoder/protenixdecoder.py`
