# Contract: OneNode

## 基本信息

- 组件名：`OneNode`
- 所属模块族：`node`
- 统一入口：`OneNode`
- 注册名：`style="OneNode"`

## 组件说明
OneNode 位于 node 模块，是 MeshGraphNet 类 processor 中的节点状态更新原语，负责聚合邻接边消息并更新节点隐状态。

## 用途
- 做什么：根据边消息和当前节点表征更新节点状态。
- 解决问题：统一调用 MeshNodeBlock。
- 适用场景：非结构网格 CFD、图代理模型、粒子状态更新。
- 不适用场景：无显式图拓扑的规则网格卷积。

## 输入规格
典型输入为 `edge_features, node_features, graph`；graph 中的边方向决定消息聚合到哪个节点。

## 输出规格
通常返回更新后的节点特征或底层 block 约定的 `(edge_features, node_features)` 结构；节点最后一维多为 `output_dim`。

## 参数
- `style`：注册表名称，常见取值包括 `MeshNodeBlock`。
- `**kwargs`：透传给目标 节点更新 实现。
- 常见参数：`aggregation`、`input_dim_nodes`、`input_dim_edges`、`output_dim`、`hidden_dim`、`hidden_layers`、`norm_type`、`activation_fn`。

## 关键依赖
- _lazy.py
- mesh_node_block.py

## 使用注意与风险
- `aggregation` 会影响数值尺度和 rollout 稳定性。
- graph、edge_features、node_features 必须同序。
- 不负责边界条件 mask 或构图。
- 节点目标维度与最终物理变量维度不一定相同。

## 启动方式
Python API 启动，调用方按目标 style 传入底层实现参数：

``` sh
python -c "from onescience.modules.node.onenode import OneNode; m=OneNode(style='MeshNodeBlock'); print(type(m).__name__)"
```

在模型 pipeline 中通常由上层模型构造函数实例化，不单独提供 CLI。

## 输入规格
按所选 style 的 forward 签名准备张量和辅助字段；wrapper 不做数据读取、字段映射或 shape 修正。

## 运行接口
- 构造接口：`OneNode(style, **kwargs)`。
- 调用接口：`module(*args, **kwargs)` 透传到底层 节点更新。
- 若源码实现了属性转发，可直接访问底层实例属性。

## 主要函数
- `forward`

## 执行资源
资源需求由底层实现决定；规则网格算子通常随空间分辨率增长，图/点云算子随节点边数量增长，训练建议使用 GPU。

## 操作限制
style 必须已注册；kwargs 与输入必须匹配底层实现；该 wrapper 不保证不同 style 的输入输出可互换。

## 规划决策

### 描述
在规划中把 OneNode 放在边更新之后，用于把边消息聚合回节点隐状态。

### 使用时机
当模型需要通过统一入口切换或复用不同 节点更新 实现时使用。

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

- `{onescience_path}/onescience/src/onescience/modules/node/onenode.py`
- `{onescience_path}/onescience/src/onescience/modules/node/mesh_node_block.py`
- `{onescience_path}/onescience/src/onescience/models/meshgraphnet/meshgraphnet.py`
