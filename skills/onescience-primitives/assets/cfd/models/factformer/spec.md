# architecture_overview

Factformer 的架构定位是 `factorized attention Transformer`。它在 CFD_Benchmark 中作为可被 `model_factory.get_model(args, device)` 或直接模块导入使用的模型原语，主要服务于 CFD 场预测、网格/点级回归和多模型 benchmark 对比。组件基础定位可以概括为：将坐标/位置编码与场特征拼接后映射为 token，通过多层 Factformer_block 做结构化网格全局建模。

# parameter_scale

参数规模不在源码中写死，主要由以下 `args` 字段和构造默认值决定：`act`, `dropout`, `fun_dim`, `geotype`, `mlp_ratio`, `n_heads`, `n_hidden`, `n_layers`, `out_dim`, `ref`, `shapelist`, `space_dim`, `time_input`, `unified_pos`。

- 隐藏宽度主要由 `n_hidden` 或 `hidden_dim_processor` 控制。
- 深度主要由 `n_layers`、`processor_size`、`branch_depth/trunk_depth` 或 U-shape 下采样层数控制。
- 输出规模由 `out_dim` 决定，输入规模由 `space_dim/fun_dim` 或显式图节点/边特征维度决定。
- 典型 benchmark 默认可从 `run.py` 继承：`n_hidden=64`、`n_layers=3`、`n_heads=4`、`dropout=0.0`、`modes=12`、`task='steady'`。

# architecture_structure

- 主干结构：OneMlp 预处理 + 多层 OneTransformer(Factformer_block)，末层 block 直接输出目标通道。
- 核心业务入口：`structured_geo`, `unstructured_geo`, `forward`。
- 源码类：`Model`；若存在辅助类，则包括 `Model`。
- 时间条件：若源码读取 `time_input`，则可用 `timestep_embedding` 将 `T` 注入隐藏表示。
- 位置条件：若源码读取 `unified_pos`，结构化网格可通过 `unified_pos_embedding(shapelist, ref)` 替换或增强坐标输入。

# input_schema

- `x`: `(Batch, NumPoints, space_dim)`，坐标、评估点或统一位置编码的输入载体。
- `fx`: `(Batch, NumPoints, fun_dim)` 或 `None`，与位置对齐的输入场特征；若模型依赖双分支或 branch 输入，应优先提供有效 `fx`。
- `T`: `(Batch,)` 或 `(Batch, 1)`，仅在 `time_input=True` 时作为时间条件使用。
- `geo`: 可选几何/图信息；大多数 `cfd_benchmark` operator 模型不直接消费该字段。
- `args` 默认/来源：
- `act`: 默认/来源 `gelu`。
- `dropout`: 默认/来源 `0.0`。
- `fun_dim`: 默认/来源 `INPUT_CHANNELS`。
- `geotype`: 默认/来源 `structured_2D`。
- `mlp_ratio`: 默认/来源 `1`。
- `n_heads`: 默认/来源 `4`。
- `n_hidden`: 默认/来源 `64`。
- `n_layers`: 默认/来源 `3`。
- `out_dim`: 默认/来源 `TARGET_CHANNELS`。
- `ref`: 默认/来源 `8`。
- `shapelist`: 默认/来源 `[H, W]`。
- `space_dim`: 默认/来源 `2`。
- `time_input`: 默认/来源 `False`。
- `unified_pos`: 默认/来源 `0`。
- `task`: 通用 runner 默认 `steady`，当前模型不一定直接读取。
- `T_in`: 通用 runner 默认 `10`，当前模型不一定直接读取。
- `T_out`: 通用 runner 默认 `10`，当前模型不一定直接读取。

# output_schema

- 输出通常为 `(Batch, NumPoints, out_dim)`；图/点云模型在内部可能 squeeze 单图 batch，但最终保持节点或点级目标变量输出。
- `out_dim` 必须与目标变量通道数一致，例如速度分量、压力、温度或其它 CFD 监督量。

# shape_transformations

```text
输入准备
  x / node_features / edge_features
    -> 与 datapipe 输出 schema 对齐
  fx
    -> 与 x 的点顺序严格对齐

特征编码
  原始输入
    -> 预处理/编码模块
    -> hidden: (..., n_hidden) 或 (..., hidden_dim_processor)

主干计算
  token 形态保持 `(Batch, NumPoints, n_hidden)`，block 内部依据 `shapelist` 理解结构网格。

输出恢复
  hidden
    -> decoder / head / final block
    -> prediction: (..., out_dim)
```

# key_dependencies

- `OneMlp`
- `OneTransformer`
- `timestep_embedding`
- `unified_pos_embedding`

# common_modification_points

- 按数据集输入/目标变量同步修改 `fun_dim`、`space_dim`、`out_dim`。
- 对结构化网格模型，优先修改 `shapelist`、`modes`、`unified_pos`、`ref`，确保 `NumPoints == prod(shapelist)`。
- 对注意力类模型，可调整 `n_layers`、`n_heads`、`mlp_ratio`、`dropout`、`slice_num/psi_dim/attn_type`。
- 对谱算子类模型，可调整 `modes`、Geo 投影分辨率、padding 策略和是否使用统一位置编码。
- 对图模型，可调整构图方式、边特征维度、聚合方式、processor 层数或图池化策略。

# implementation_risks

- `args` 字段缺失会在构造阶段直接触发属性错误；生成配置时应至少覆盖源码读取的字段。
- `shapelist` 与真实点数不一致会导致 reshape、padding 或窗口注意力阶段失败。
- `time_input=True` 但调用 `forward` 未传入 `T`，会造成时间条件缺失或维度不一致。
- 非结构任务不要强行套结构网格模型；需要先确认 Geo 投影、插值或构图策略。
- 图模型的 `geo/graph/edge_features` 必须由 datapipe 提前准备，模型不负责从坐标自动构图。

# code_references

- `{onescience_path}/onescience/src/onescience/models/cfd_benchmark/Factformer.py`
- `{onescience_path}/onescience/examples/cfd/CFD_Benchmark/exp/exp_steady.py`
