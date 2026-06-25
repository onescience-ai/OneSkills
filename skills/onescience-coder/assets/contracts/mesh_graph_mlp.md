# Contract: MeshGraphMLP

## 基本信息

- **组件名称**: MeshGraphMLP
- **模块族**: mlp
- **统一入口**: not_applicable
- **注册名称**: style="MeshGraphMLP"

## 组件说明

`mesh_graph_mlp` 属于 `mlp` 模块族，核心实现类/函数包括 `CustomSiLuLinearAutogradFunction`、`MeshGraphMLP`、`MeshGraphEdgeMLPConcat`、`MeshGraphEdgeMLPSum`。它的定位是图 MLP 模块，由上层 OneScience 模型或流水线通过 Python API 调用。

## 用途

以多层感知机形式变换图节点或边特征，适用于 GraphCast 消息传递模块。

## 输入规格

- 图节点特征：`(N_nodes, feature_dim)`
- 图边特征：`(N_edges, feature_dim)`
- 图结构：DGL 图或等价的源/目标索引关系。

## 输出规格

- 输出为更新后的节点特征、边特征或嵌入特征，维度由 `output_dim`、`hidden_dim` 等参数控制。

## 参数

- `MeshGraphMLP` 构造参数：`input_dim`, `output_dim`, `hidden_dim`, `hidden_layers`, `activation_fn`, `norm_type`, `recompute_activation`
- `MeshGraphEdgeMLPConcat` 构造参数：`efeat_dim`, `src_dim`, `dst_dim`, `output_dim`, `hidden_dim`, `hidden_layers`, `activation_fn`, `norm_type`, `bias`, `recompute_activation`
- `MeshGraphEdgeMLPSum` 构造参数：`efeat_dim`, `src_dim`, `dst_dim`, `output_dim`, `hidden_dim`, `hidden_layers`, `activation_fn`, `norm_type`, `bias`, `recompute_activation`

## 关键依赖

- `gnnlayer_utils`

## 使用注意与风险

- 输入张量维度必须与构造参数中的通道数、网格分辨率、patch 大小或图特征维度一致。
- 该组件通常依赖上层模型完成数据标准化、变量排序和设备迁移，单独调用时需显式准备。
- 图结构、节点顺序和边特征语义必须在 encoder、processor、decoder 阶段保持一致。

## 启动方式

主要通过 Python API 在模型配置或上层模块中实例化，不是独立 CLI 入口。下面的命令会从源码模块导入组件并打印完整构造签名，便于确认全部 API 参数：

```sh
python -c "from onescience.modules.mlp.mesh_graph_mlp import CustomSiLuLinearAutogradFunction; import inspect; print(inspect.signature(CustomSiLuLinearAutogradFunction))"
```

在真实任务中应由对应模型配置传入尺寸、通道数和隐空间维度等参数。

## 输入规格

- 图节点特征：`(N_nodes, feature_dim)`
- 图边特征：`(N_edges, feature_dim)`
- 图结构：DGL 图或等价的源/目标索引关系。

默认参数信息：

- `MeshGraphMLP` 构造默认参数：`output_dim=512`，`hidden_dim=512`，`hidden_layers=1`，`activation_fn=nn.SiLU()`，`norm_type='LayerNorm'`，`recompute_activation=False`
- `MeshGraphEdgeMLPConcat` 构造默认参数：`efeat_dim=512`，`src_dim=512`，`dst_dim=512`，`output_dim=512`，`hidden_dim=512`，`hidden_layers=2`，`activation_fn=nn.SiLU()`，`norm_type='LayerNorm'`，`bias=True`，`recompute_activation=False`
- `MeshGraphEdgeMLPSum` 构造默认参数：`output_dim=512`，`hidden_dim=512`，`hidden_layers=1`，`activation_fn=nn.SiLU()`，`norm_type='LayerNorm'`，`bias=True`，`recompute_activation=False`

## 运行接口

- `CustomSiLuLinearAutogradFunction`：实例化后通过 `forward`, `backward` 等运行时接口参与流水线。
- `MeshGraphMLP`：实例化后通过 `default_forward`, `custom_silu_linear_forward`, `forward` 等运行时接口参与流水线。
- `MeshGraphEdgeMLPConcat`：实例化后通过 `forward` 等运行时接口参与流水线。
- `MeshGraphEdgeMLPSum`：实例化后通过 `forward_truncated_sum`, `default_forward`, `custom_silu_linear_forward`, `forward` 等运行时接口参与流水线。

## 主要函数

- `forward`
- `backward`
- `default_forward`
- `custom_silu_linear_forward`
- `forward_truncated_sum`

## 执行资源

- 运行设备由上层任务决定，训练和高分辨率推理通常建议使用 GPU。
- 图构建、邻居搜索或大分辨率气象场处理会占用较多内存，批量大小需随网格规模调整。
- 需要保证依赖库和 OneScience 模块路径可用，并与模型配置中的精度、设备和维度设置一致。

## 操作限制

- 不负责完整数据预处理、变量标准化、训练循环或损失函数编排。
- 仅在输入形状、变量顺序、图结构和上下游组件契约一致时可稳定工作。
- 源码中未声明的 CLI 参数、自动下载或外部数据读取能力不应假定存在。

## 规划决策

### 描述

CustomSiLuLinearAutogradFunction 是 OneScience 中面向气象/地球系统建模的图 MLP 模块，用于在模型流水线中完成特征变换、尺度组织或结果重建。

```text
输入图/节点/边特征
  -> 特征嵌入或消息构造
  -> 边更新 / 节点聚合 / 图结构输出
  -> GraphCast 上层 encoder-processor-decoder 使用
```

### 使用时机

- 任务需要 `图 MLP 模块` 能力，且组件输入输出契约与当前模型阶段匹配。
- 组件所属模型族或图/生成网络语义与任务目标一致。

### 输入

- 上游模型阶段提供的张量、图结构、条件特征或噪声特征。
- 与源码构造参数一致的通道数、分辨率、patch/window 尺寸、隐层维度和特征语义。

### 输出

- 可直接交给下一阶段的中间特征、图对象、节点/边表示或预测场。
- 输出结构应按 `spec.md` 的 `output_schema` 和 `code_references` 进行校验。

### 执行步骤

1. 确认组件所属模型族、模块族和上游/下游阶段。
2. 根据源码构造参数准备尺寸、通道、图特征维度和可选超参数。
3. 按 `usage.md` 的运行接口实例化组件，并传入契约化输入。
4. 检查输出形状、数据类型、设备和变量顺序是否满足下一阶段要求。
5. 在完整模型中通过单步前向或小批量样例验证集成效果。

### 约束

- 不跨越组件职责边界承担数据下载、全局训练调度或模型族外的语义转换。
- 不在未确认形状、图结构或变量顺序时直接替换已有模块。
- 规划中涉及代码位置时只以 `spec.md` 的 `code_references` 为准。

### 下一阶段建议

- 若组件用于新流水线，下一阶段应补齐上游输入准备和下游形状断言。
- 若组件替换已有模块，下一阶段应做等价输入样例对比和端到端 smoke test。

### 回退策略

- 当输入维度或依赖不匹配时，退回到同模型族的统一入口组件或相邻基础组件。
- 当源码缺少独立运行入口时，优先在上层模型配置中集成验证，而不是为该组件臆造 CLI。

## 源码锚点

- `{onescience_path}/onescience/src/onescience/modules/mlp/mesh_graph_mlp.py`
