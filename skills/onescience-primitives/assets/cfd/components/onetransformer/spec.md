# component_info
OneTransformer 位于 transformer 模块，是模型主干或 processor block 的统一构造入口，覆盖天气、CFD 神经算子、图 ViT 和生物结构 diffusion/atom transformer。

# purpose
- 做什么：执行 token 或网格隐表征的主干混合与更新。
- 解决问题：通过 style 配置统一接入多种 transformer block。
- 适用场景：天气模型主干、Transolver CFD、Galerkin/Factformer/GNOT、Protenix diffusion。
- 不适用场景：自动完成 embedding、采样、构图或输出投影。

# input_schema
输入由 style 决定；Earth/Fuxi 多为网格或天气 token；Transolver 多为点云/网格 token `fx`；GraphViT 使用 cluster token 和 mask；Protenix 使用 token/pair/atom 表征。

# output_schema
输出保持底层 transformer 约定，通常为更新后的隐表征；部分 block 可能返回 tuple 或中间状态。

# parameters
- `style`：注册表名称，常见取值包括 `EarthTransformer2DBlock`, `FuxiTransformer`, `Transolver_block`, `ProtenixDiffusionTransformer`。
- `**kwargs`：透传给目标 Transformer 实现。
- 常见参数：`dim`、`depth`、`heads`、`mlp_ratio`、窗口/shape 配置、物理注意力切片参数、Protenix 条件参数等。

# key_dependencies
- _lazy.py
- earthtransformer2Dblock.py
- earthtransformer3Dblock.py
- fuxitransformer.py
- Transolver_block.py
- Neural_Spectral_Block.py
- protenixtransformer.py

# usage_and_risks
- wrapper 不统一 tensor 语义。
- EarthTransformer2D、FuxiTransformer 和 Transolver_block 输入结构不同。
- 内部 attention/MLP 参数需一起校验。
- Protenix transformer 不适合直接处理 CFD 规则网格。

# code_references
- `{onescience_path}/onescience/src/onescience/modules/transformer/onetransformer.py`
- `{onescience_path}/onescience/src/onescience/modules/transformer/earthtransformer2Dblock.py`
- `{onescience_path}/onescience/src/onescience/modules/transformer/earthtransformer3Dblock.py`
- `{onescience_path}/onescience/src/onescience/modules/transformer/fuxitransformer.py`
- `{onescience_path}/onescience/src/onescience/modules/transformer/Transolver_block.py`
- `{onescience_path}/onescience/src/onescience/modules/transformer/Neural_Spectral_Block.py`
- `{onescience_path}/onescience/src/onescience/modules/transformer/protenixtransformer.py`
