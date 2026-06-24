# Model Card: graphcast

## 基本信息

- 模型名：`graphcast`
- 任务类型：`model`
- 当前状态：`public`
- 主实现文件：`{onescience_path}/onescience/src/onescience/models/graphcast/graph_cast_net.py`

## 模型架构概览

GraphCastNet 是网格-网格图模型。它从经纬网格构造 mesh graph、grid-to-mesh graph、mesh-to-grid graph，再完成编码、mesh 处理和解码。
它的主路径是规则经纬网格到非结构 mesh，再从 mesh 回到规则网格。processor 可选择消息传递或图 Transformer。

## 参数规模

- 默认输入网格 `(721,1440)`。
- 默认 `input_dim_grid_nodes=237`，`output_dim_grid_nodes=227`。
- 默认 `hidden_dim=512`，`processor_layers=16`。
- 默认 `mesh_level=6`，可使用 multimesh。
- 参数规模主要由 embedding MLP、G2M/M2G 编解码器、processor 层和 finale MLP 决定。

## 架构结构

```text
图构造阶段
  lat_lon_grid: (721, 1440, 2)
    -> Graph(lat_lon_grid, mesh_level, multimesh, khop_neighbors)
    -> mesh_graph: icosahedral / multimesh 图
    -> g2m_graph : grid-to-mesh 边
    -> m2g_graph : mesh-to-grid 边
    -> mesh_ndata, mesh_edata, g2m_edata, m2g_edata

输入准备
  grid_nfeat: (Batch=1, input_dim_grid_nodes, Height, Width)
    -> prepare_input
    -> (Height * Width, input_dim_grid_nodes)

编码到 mesh
  grid_nfeat + mesh_ndata + g2m_edata + mesh_edata
    -> GraphCastEncoderEmbedder
    -> grid_nfeat_embedded, mesh_nfeat_embedded, g2m_efeat_embedded, mesh_efeat_embedded
    -> MeshGraphEncoder(g2m_graph)
    -> grid_nfeat_encoded, mesh_nfeat_encoded

mesh processor
  MessagePassing:
    mesh_efeat_embedded + mesh_nfeat_encoded
      -> processor_encoder
      -> processor
      -> processor_decoder
      -> mesh_efeat_processed, mesh_nfeat_processed

  GraphTransformer:
    mesh_nfeat_encoded
      -> GraphCastProcessorGraphTransformer(attention_mask)
      -> mesh_nfeat_processed

解码回 grid
  m2g_edata
    -> GraphCastDecoderEmbedder
    -> MeshGraphDecoder(m2g_graph)
    -> grid_nfeat_decoded
    -> MeshGraphMLP
    -> (Height * Width, output_dim_grid_nodes)

输出准备
  prepare_output
    -> (1, output_dim_grid_nodes, Height, Width)
```

## 输入模式

- 非分布式默认输入：`(Batch=1, input_dim_grid_nodes, Height, Width)`。
- 分布式模式可输入分区后的节点特征，取决于 `expect_partitioned_input`。
- 默认不支持 batch size 大于 1。

## 输出模式

- 聚合输出默认为 `(1, output_dim_grid_nodes, Height, Width)`。
- 分布式模式可选择保持分区输出或聚合到一个或所有 rank。

## 形状转换

1. 非分布式输入从 `(1,C,H,W)` reshape 为 `(H*W,C)`。
2. grid、mesh、边特征被嵌入到 `hidden_dim`。
3. G2M 编码生成 mesh 节点表示和保留 grid 编码表示。
4. processor 在 mesh 图上迭代更新节点和边。
5. M2G 解码将 mesh 表示回传到 grid 节点。
6. finale MLP 映射为 `output_dim_grid_nodes`。
7. 输出从 `(H*W,C_out)` 恢复为 `(1,C_out,H,W)`。

## 常见修改点

- 修改 `input_dim_grid_nodes/output_dim_grid_nodes` 以适配变量集合。
- 调整 `mesh_level`、`multimesh` 和 `khop_neighbors` 控制图连接范围。
- 在 `MessagePassing` 与 `GraphTransformer` 之间选择 processor。
- 调整 `processor_layers`、`hidden_dim` 和 `aggregation` 控制容量。
- 开启分区、CuGraph 或 checkpoint 优化大图训练与推理。

## 实现风险

- 非分布式模式硬性要求 batch size 为 1。
- processor 层数必须大于 2。
- 分区相关标志互斥关系复杂，`global_features_on_rank_0` 与 `expect_partitioned_input` 不能同时启用。
- 图对象和图特征需要在 `to()` 中同步迁移设备。
- GraphTransformer 分支对 attention mask 调用形式需要与底层实现兼容。

## 启动方式

Python API 启动示例：

```sh
python -c "import torch; from onescience.models.graphcast import GraphCastNet; model=GraphCastNet(mesh_level=6, multimesh_level=None, multimesh=True, input_res=(721,1440), input_dim_grid_nodes=237, input_dim_mesh_nodes=3, input_dim_edges=4, output_dim_grid_nodes=227, processor_type='MessagePassing', khop_neighbors=32, num_attention_heads=4, processor_layers=16, hidden_layers=1, hidden_dim=512, aggregation='sum', activation_fn='silu', norm_type='LayerNorm', use_cugraphops_encoder=False, use_cugraphops_processor=False, use_cugraphops_decoder=False, do_concat_trick=False, recompute_activation=False, partition_size=1, partition_group_name=None, use_lat_lon_partitioning=False, expect_partitioned_input=False, global_features_on_rank_0=False, produce_aggregated_output=True, produce_aggregated_output_on_all_ranks=True); x=torch.randn(1,237,721,1440); y=model(x); print(y.shape)"
```

## 输入模式

- 默认输入是 `(1, input_dim_grid_nodes, Height, Width)`。
- 默认参数：`mesh_level=6`，`multimesh_level=None`，`multimesh=True`，`input_res=(721, 1440)`，`input_dim_grid_nodes=237`，`input_dim_mesh_nodes=3`，`input_dim_edges=4`，`output_dim_grid_nodes=227`。
- 默认 processor 参数：`processor_type="MessagePassing"`，`khop_neighbors=32`，`num_attention_heads=4`，`processor_layers=16`，`hidden_layers=1`，`hidden_dim=512`，`aggregation="sum"`，`activation_fn="silu"`，`norm_type="LayerNorm"`。
- 默认运行/分区参数：`use_cugraphops_encoder=False`，`use_cugraphops_processor=False`，`use_cugraphops_decoder=False`，`do_concat_trick=False`，`recompute_activation=False`，`partition_size=1`，`partition_group_name=None`，`use_lat_lon_partitioning=False`，`expect_partitioned_input=False`，`global_features_on_rank_0=False`，`produce_aggregated_output=True`，`produce_aggregated_output_on_all_ranks=True`。
- 默认输入 shape：`(1, 237, 721, 1440)`。
- batch size 默认只能为 1。
- 输入变量应按训练时的 grid node feature 顺序排列。
- 分布式模式下需根据分区策略准备全局或分区节点特征。

## 运行时接口

- `forward(grid_nfeat)`：完整推理入口。
- `prepare_input(invar, expect_partitioned_input, global_features_on_rank_0)`：将输入整理为节点特征。
- `custom_forward(grid_nfeat)`：执行编码、processor、解码主体。
- `encoder_forward(grid_nfeat)`：执行嵌入、G2M 编码和 processor 首段。
- `decoder_forward(mesh_efeat_processed, mesh_nfeat_processed, grid_nfeat_encoded)`：执行 processor 末段、M2G 解码和输出 MLP。
- `prepare_output(outvar, produce_aggregated_output, produce_aggregated_output_on_all_ranks)`：将节点输出恢复为网格或分区结果。
- `set_checkpoint_model(checkpoint_flag)`：设置整模 checkpoint。
- `set_checkpoint_processor(checkpoint_segments)`：设置 processor 分段 checkpoint。
- `set_checkpoint_encoder(checkpoint_flag)`：设置 encoder checkpoint。
- `set_checkpoint_decoder(checkpoint_flag)`：设置 decoder checkpoint。
- `to(*args, **kwargs)`：迁移模型、图和图特征设备。

## 主要函数

- `forward`
- `prepare_input`
- `custom_forward`
- `encoder_forward`
- `decoder_forward`
- `prepare_output`
- `set_checkpoint_model`
- `set_checkpoint_processor`
- `set_checkpoint_encoder`
- `set_checkpoint_decoder`
- `to`

## 运行资源

- 默认全球图规模大，推荐 GPU。
- 分区或 CuGraph 路径适合大规模训练和多设备部署。
- checkpoint 可降低训练显存，但会增加计算时间。
- 需要图构造和图消息传递相关运行依赖。

## 运行限制

- 默认非分布式 batch size 不可大于 1。
- 输入输出特征维度必须与模型初始化一致。
- 分区输入和全局 rank 输入的标志不能冲突。
- 修改网格分辨率会重建图，权重迁移需谨慎。

## 规划决策

### 描述

GraphCast 规划知识用于在全球天气任务中选择图网格模型，编排网格特征到 mesh 表示、mesh 传播、再回到经纬网格的完整流程。

### 适用场景

- 需要在规则经纬网格和非结构 mesh 之间传播信息。
- 任务关注全球尺度长距离依赖。
- batch size 为 1 可以接受，或已有分布式图分区方案。
- 需要可控的消息传递层数、mesh level 和输出变量维度。

### 输入

- 输入网格分辨率。
- grid node 输入特征维度与输出特征维度。
- mesh level、processor 类型和 processor 层数。
- 是否启用分区、CuGraph、checkpoint。

### 输出

- 聚合后的经纬网格预测张量。
- 或分布式场景下的分区节点预测结果。

### 流程

1. 根据数据变量集合确定输入/输出 feature 维度。
2. 根据分辨率和性能预算选择 `mesh_level` 与 processor 类型。
3. 实例化模型并构建图。
4. 根据显存设置 checkpoint 或分区策略。
5. 调用 `forward` 并恢复输出。
6. 做物理变量反归一化与范围检查。

### 约束

- 非分布式默认只支持 batch size 1。
- processor 层数至少为 3。
- 图构造绑定输入分辨率。
- 分区参数必须与运行环境和数据切分方式一致。

### 下一阶段建议

- 为生产环境固化图缓存，避免重复构图成本。
- 对分区模式建立专门的输入输出适配器。
- 为 checkpoint 策略做显存与速度基准测试。

### 备选方案

- 若无法满足图依赖或 batch size 限制，可改用 Pangu/FengWu 等规则网格模型。
- 若分布式配置失败，先回退到 `partition_size=1` 验证单卡逻辑。
- 若显存不足，优先降低 mesh level 或 hidden_dim，再考虑分区。

## 组件契约入口

- ../contracts/graph.md
- ../contracts/graphcastprocessor.md
- ../contracts/graphcastprocessorgraphtransformer.md
- ../contracts/graphcastencoderembedder.md
- ../contracts/graphcastdecoderembedder.md
- ../contracts/meshgraphencoder.md
- ../contracts/meshgraphdecoder.md
- ../contracts/meshgraphmlp.md
- ../contracts/cugraphcsc.md
- ../contracts/meshedgeblock.md
- ../contracts/meshnodeblock.md

## 源码锚点

- `{onescience_path}/onescience/src/onescience/models/graphcast/graph_cast_net.py`
- `{onescience_path}/onescience/src/onescience/models/graphcast/graph_cast_processor.py`
- `{onescience_path}/onescience/src/onescience/modules/utils/graphcast/graph.py`
- `{onescience_path}/onescience/src/onescience/modules/embedding/graphcast_embedder.py`
- `{onescience_path}/onescience/src/onescience/modules/encoder/mesh_graph_encoder.py`
- `{onescience_path}/onescience/src/onescience/modules/decoder/mesh_graph_decoder.py`
- `{onescience_path}/onescience/src/onescience/modules/mlp/mesh_graph_mlp.py`
- `{onescience_path}/onescience/src/onescience/modules/edge/mesh_edge_block.py`
- `{onescience_path}/onescience/src/onescience/modules/node/mesh_node_block.py`
- `{onescience_path}/onescience/src/onescience/modules/utils/gnnlayer_utils.py`
