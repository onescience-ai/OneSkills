# component_info
OneAttention 位于 attention 模块，是统一注意力原语入口，面向 EarthAttention、Transolver 物理注意力、线性注意力、窗口注意力和 Protenix 注意力等多类实现提供一致的构造与 forward 分发能力。它本身不定义张量语义，只负责 style 校验、实例化和运行时透传。

# purpose
- 做什么：为不同注意力实现提供统一入口，减少上层模型对具体模块路径的直接依赖。
- 解决问题：让气象网格、CFD token、非结构化网格、pair 表征等注意力实现通过同一调用模式接入。
- 适用场景：Transformer block、Transolver block、GraphViT/Factformer/GNOT、Protenix pair 或 atom 注意力。
- 不适用场景：需要自动完成网格展平、窗口划分、mask 构造或邻接图构建的场景；这些应由上游 pipeline 或具体 style 完成。

# input_schema
输入由 `style` 决定，常见分支如下：

规则网格注意力
  x: 2D/3D 网格或窗口 token
  mask/window metadata: 由 EarthAttention 或 WindowAttention 定义

CFD/物理注意力
  x/fx: (Batch, Points, Channels) 或结构化网格 token
  坐标/shape: `shapelist`、`slice_num` 等由具体 style 消费

Protenix 注意力
  token/pair/atom 表征: 维度和 mask 语义由 ProtenixAttention 系列定义

# output_schema
输出直接来自底层 attention，一般保持 batch 与 token/空间组织不变，仅更新最后一维特征；若底层实现返回附加权重、bias 或 tuple，则 OneAttention 不做拆包或改名。

# parameters
- `style`：注册表名称，例如 `EarthAttention2D`、`Physics_Attention_Irregular_Mesh`、`LinearAttention`、`ProtenixAttentionPairBias`。
- `**kwargs`：完整透传给目标 attention。常见参数包括 `dim`、`heads`、`dim_head`、`dropout`、`slice_num`、`shapelist`、窗口尺寸和 pair bias 配置。
- 典型值：结构化 2D 网格优先 `EarthAttention2D` 或 `Physics_Attention_Structured_Mesh_2D`；非结构化点云优先 `Physics_Attention_Irregular_Mesh`；低复杂度长序列可评估 `LinearAttention`。

# key_dependencies
- _lazy.py
- earthattention2d.py
- earthattention3d.py
- physicsattention.py
- linearattention.py
- protenixattention.py

# usage_and_risks
典型使用是由 Transformer 类组件在构造时创建并在 forward 中透传 token。风险点：

- wrapper 不检查 shape，错误的网格维度会在底层 attention 中暴露。
- EarthAttention2D 与 EarthAttention3D 不可仅通过参数替换互换。
- Protenix 的 `z`/pair bias 不是 CFD 窗口 mask。
- FactAttention 与物理注意力常依赖 `shapelist`，不能只根据 token 数推断。

# code_references
- `{onescience_path}/onescience/src/onescience/modules/attention/oneattention.py`
- `{onescience_path}/onescience/src/onescience/modules/attention/earthattention2d.py`
- `{onescience_path}/onescience/src/onescience/modules/attention/earthattention3d.py`
- `{onescience_path}/onescience/src/onescience/modules/attention/physicsattention.py`
- `{onescience_path}/onescience/src/onescience/modules/attention/linearattention.py`
- `{onescience_path}/onescience/src/onescience/modules/attention/protenixattention.py`
