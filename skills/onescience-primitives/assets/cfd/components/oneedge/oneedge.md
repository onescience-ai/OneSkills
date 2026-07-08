# Contract: OneEdge

## 基本信息

- 组件名：`OneEdge`
- 所属模块族：`edge`
- 统一入口：`OneEdge`
- 注册名：`style="OneEdge"`

## 组件说明
OneEdge 位于 edge 模块，是 MeshGraphNet 类 processor 中的边消息更新原语，负责基于相邻节点与边属性更新边隐状态。

## 用途
- 做什么：更新图边表征。
- 解决问题：把 MeshGraphNet 的边更新 block 纳入统一注册入口。
- 适用场景：非结构网格 CFD、粒子系统、显式图 message passing。
- 不适用场景：无边拓扑的规则 CNN/FNO 网格。

## 输入规格
典型输入为 `edge_features, node_features, graph`，其中边数量和顺序必须与 graph 内部边顺序一致。

## 输出规格
通常返回更新后的边特征以及底层 block 约定的附加结构；最后一维多为 `output_dim`。

## 参数
- `style`：注册表名称，常见取值包括 `MeshEdgeBlock`。
- `**kwargs`：透传给目标 边更新 实现。
- 常见参数：`input_dim_nodes`、`input_dim_edges`、`output_dim`、`hidden_dim`、`hidden_layers`、`aggregation`、`norm_type`、`activation_fn`。

## 关键依赖
- _lazy.py
- mesh_edge_block.py

## 使用注意与风险
- 不负责构图或补边。
- graph 必须兼容底层 MeshEdgeBlock。
- 节点/边特征维度不可混用。
- 边方向和顺序错误会造成静默语义错误。

## 启动方式
Python API 启动，调用方按目标 style 传入底层实现参数：

``` sh
python -c "from onescience.modules.edge.oneedge import OneEdge; m=OneEdge(style='MeshEdgeBlock'); print(type(m).__name__)"
```

在模型 pipeline 中通常由上层模型构造函数实例化，不单独提供 CLI。

## 输入规格
按所选 style 的 forward 签名准备张量和辅助字段；wrapper 不做数据读取、字段映射或 shape 修正。

## 运行接口
- 构造接口：`OneEdge(style, **kwargs)`。
- 调用接口：`module(*args, **kwargs)` 透传到底层 边更新。
- 若源码实现了属性转发，可直接访问底层实例属性。

## 主要函数
- `forward`

## 执行资源
资源需求由底层实现决定；规则网格算子通常随空间分辨率增长，图/点云算子随节点边数量增长，训练建议使用 GPU。

## 操作限制
style 必须已注册；kwargs 与输入必须匹配底层实现；该 wrapper 不保证不同 style 的输入输出可互换。

## 规划决策

### 描述
在规划中把 OneEdge 放在节点更新之前，用于从当前节点状态和边属性计算新的边消息。

### 使用时机
当模型需要通过统一入口切换或复用不同 边更新 实现时使用。

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

- `{onescience_path}/onescience/src/onescience/modules/edge/oneedge.py`
- `{onescience_path}/onescience/src/onescience/modules/edge/mesh_edge_block.py`
- `{onescience_path}/onescience/src/onescience/models/meshgraphnet/meshgraphnet.py`
