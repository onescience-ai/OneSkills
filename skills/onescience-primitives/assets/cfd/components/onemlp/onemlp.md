# Contract: OneMlp

## 基本信息

- 组件名：`OneMlp`
- 所属模块族：`mlp`
- 统一入口：`OneMlp`
- 注册名：`style="OneMlp"`

## 组件说明
OneMlp 位于 mlp 模块，是特征升维、通道混合、节点/边编码和轻量输出投影的统一入口。

## 用途
- 做什么：对点、token、节点、边或通道特征做非线性映射。
- 解决问题：统一管理 StandardMLP、MeshGraphMLP 和 GroupEquivariantMLP。
- 适用场景：输入 lifting、processor 内部 FFN、图节点/边 encoder/decoder、GFNO channel mixing。
- 不适用场景：需要空间卷积、频域卷积或显式注意力的阶段。

## 输入规格
StandardMLP 通常接收 `(..., FeatureDim)`；MeshGraphMLP 接收节点/边特征；GroupEquivariantMLP*d 通常接收等变通道布局的网格张量。

## 输出规格
StandardMLP 输出 `(..., output_dim)`；图 MLP 输出节点/边目标维度；等变 MLP 保持空间维并映射通道。

## 参数
- `style`：注册表名称，常见取值包括 `StandardMLP`, `MeshGraphMLP`, `GroupEquivariantMLP2d`, `XiheMlp`。
- `**kwargs`：透传给目标 MLP 实现。
- StandardMLP 常用 `input_dim`、`hidden_dims`、`output_dim`、`activation`。
- MeshGraphMLP 常用 `input_dim`、`output_dim`、`hidden_dim`、`hidden_layers`、`norm_type`。
- GroupEquivariantMLP 使用 `in_channels/out_channels/mid_channels` 等通道参数。

## 关键依赖
- _lazy.py
- MLP.py
- mesh_graph_mlp.py
- GMLP.py
- xihemlp.py

## 使用注意与风险
- 不同 MLP style 参数名不同。
- channel-first 张量不能直接当作 `(..., FeatureDim)` 输入 StandardMLP。
- 图 MLP 的 LayerNorm 和 residual 约定会影响 rollout 稳定性。
- style 未注册或 kwargs 冲突会失败。

## 启动方式
Python API 启动，调用方按目标 style 传入底层实现参数：

``` sh
python -c "from onescience.modules.mlp.onemlp import OneMlp; m=OneMlp(style='StandardMLP'); print(type(m).__name__)"
```

在模型 pipeline 中通常由上层模型构造函数实例化，不单独提供 CLI。

## 输入规格
按所选 style 的 forward 签名准备张量和辅助字段；wrapper 不做数据读取、字段映射或 shape 修正。

## 运行接口
- 构造接口：`OneMlp(style, **kwargs)`。
- 调用接口：`module(*args, **kwargs)` 透传到底层 MLP。
- 若源码实现了属性转发，可直接访问底层实例属性。

## 主要函数
- `forward`

## 执行资源
资源需求由底层实现决定；规则网格算子通常随空间分辨率增长，图/点云算子随节点边数量增长，训练建议使用 GPU。

## 操作限制
style 必须已注册；kwargs 与输入必须匹配底层实现；该 wrapper 不保证不同 style 的输入输出可互换。

## 规划决策

### 描述
在规划中把 OneMlp 作为局部特征映射层，根据特征布局选择 Standard、Graph 或 Equivariant family。

### 使用时机
当模型需要通过统一入口切换或复用不同 MLP 实现时使用。

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

- `{onescience_path}/onescience/src/onescience/modules/mlp/onemlp.py`
- `{onescience_path}/onescience/src/onescience/modules/mlp/MLP.py`
- `{onescience_path}/onescience/src/onescience/modules/mlp/mesh_graph_mlp.py`
- `{onescience_path}/onescience/src/onescience/modules/mlp/GMLP.py`
