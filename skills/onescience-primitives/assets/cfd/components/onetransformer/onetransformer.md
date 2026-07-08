# Contract: OneTransformer

## 基本信息

- 组件名：`OneTransformer`
- 所属模块族：`transformer`
- 统一入口：`OneTransformer`
- 注册名：`style="OneTransformer"`

## 组件说明
OneTransformer 位于 transformer 模块，是模型主干或 processor block 的统一构造入口，覆盖天气、CFD 神经算子、图 ViT 和生物结构 diffusion/atom transformer。

## 用途
- 做什么：执行 token 或网格隐表征的主干混合与更新。
- 解决问题：通过 style 配置统一接入多种 transformer block。
- 适用场景：天气模型主干、Transolver CFD、Galerkin/Factformer/GNOT、Protenix diffusion。
- 不适用场景：自动完成 embedding、采样、构图或输出投影。

## 输入规格
输入由 style 决定；Earth/Fuxi 多为网格或天气 token；Transolver 多为点云/网格 token `fx`；GraphViT 使用 cluster token 和 mask；Protenix 使用 token/pair/atom 表征。

## 输出规格
输出保持底层 transformer 约定，通常为更新后的隐表征；部分 block 可能返回 tuple 或中间状态。

## 参数
- `style`：注册表名称，常见取值包括 `EarthTransformer2DBlock`, `FuxiTransformer`, `Transolver_block`, `ProtenixDiffusionTransformer`。
- `**kwargs`：透传给目标 Transformer 实现。
- 常见参数：`dim`、`depth`、`heads`、`mlp_ratio`、窗口/shape 配置、物理注意力切片参数、Protenix 条件参数等。

## 关键依赖
- _lazy.py
- earthtransformer2Dblock.py
- earthtransformer3Dblock.py
- fuxitransformer.py
- Transolver_block.py
- Neural_Spectral_Block.py
- protenixtransformer.py

## 使用注意与风险
- wrapper 不统一 tensor 语义。
- EarthTransformer2D、FuxiTransformer 和 Transolver_block 输入结构不同。
- 内部 attention/MLP 参数需一起校验。
- Protenix transformer 不适合直接处理 CFD 规则网格。

## 启动方式
Python API 启动，调用方按目标 style 传入底层实现参数：

``` sh
python -c "from onescience.modules.transformer.onetransformer import OneTransformer; m=OneTransformer(style='EarthTransformer2DBlock'); print(type(m).__name__)"
```

在模型 pipeline 中通常由上层模型构造函数实例化，不单独提供 CLI。

## 输入规格
按所选 style 的 forward 签名准备张量和辅助字段；wrapper 不做数据读取、字段映射或 shape 修正。

## 运行接口
- 构造接口：`OneTransformer(style, **kwargs)`。
- 调用接口：`module(*args, **kwargs)` 透传到底层 Transformer。
- 若源码实现了属性转发，可直接访问底层实例属性。

## 主要函数
- `forward`

## 执行资源
资源需求由底层实现决定；规则网格算子通常随空间分辨率增长，图/点云算子随节点边数量增长，训练建议使用 GPU。

## 操作限制
style 必须已注册；kwargs 与输入必须匹配底层实现；该 wrapper 不保证不同 style 的输入输出可互换。

## 规划决策

### 描述
在规划中把 OneTransformer 作为主干计算阶段，选择 style 时同时规划其 attention、MLP、位置编码和采样前后关系。

### 使用时机
当模型需要通过统一入口切换或复用不同 Transformer 实现时使用。

### 输入
- 数据拓扑与空间维度。
- 上下游模块的 shape/字段契约。
- 目标 style 的参数需求。
- 资源预算与失败容忍度。

### 输出
- 选定 style。
- 构造参数。
- 运行时输入字段映射。
- 输出语义和后续连接策略。

### 执行步骤
1. 从任务数据形态筛选候选 style。
2. 回到目标 style 源码确认构造参数与 forward 参数。
3. 准备最小 batch 验证 shape。
4. 接入上游和下游模块。
5. 记录限制条件和 fallback。

### 约束
不跨语义混用 style；不把 wrapper 当作数据适配层；新增底层实现后必须注册。

### 下一阶段建议
为被选 style 增加端到端 smoke test，并补充示例配置。

### 回退策略
若 style 不支持当前输入，改用同 family 更匹配实现；若无可用 style，先实现专用适配层或回退到底层模块直接调用。

## 源码锚点

- `{onescience_path}/onescience/src/onescience/modules/transformer/onetransformer.py`
- `{onescience_path}/onescience/src/onescience/modules/transformer/earthtransformer2Dblock.py`
- `{onescience_path}/onescience/src/onescience/modules/transformer/earthtransformer3Dblock.py`
- `{onescience_path}/onescience/src/onescience/modules/transformer/fuxitransformer.py`
- `{onescience_path}/onescience/src/onescience/modules/transformer/Transolver_block.py`
- `{onescience_path}/onescience/src/onescience/modules/transformer/Neural_Spectral_Block.py`
- `{onescience_path}/onescience/src/onescience/modules/transformer/protenixtransformer.py`
