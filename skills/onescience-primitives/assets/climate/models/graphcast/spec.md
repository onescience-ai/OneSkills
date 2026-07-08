# architecture_overview

GraphCastNet 是网格-网格图模型。它从经纬网格构造 mesh graph、grid-to-mesh graph、mesh-to-grid graph，再完成编码、mesh 处理和解码。
它的主路径是规则经纬网格到非结构 mesh，再从 mesh 回到规则网格。processor 可选择消息传递或图 Transformer。

# parameter_scale

- 默认输入网格 `(721,1440)`。
- 默认 `input_dim_grid_nodes=237`，`output_dim_grid_nodes=227`。
- 默认 `hidden_dim=512`，`processor_layers=16`。
- 默认 `mesh_level=6`，可使用 multimesh。
- 参数规模主要由 embedding MLP、G2M/M2G 编解码器、processor 层和 finale MLP 决定。

# architecture_structure

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

# input_schema

- 非分布式默认输入：`(Batch=1, input_dim_grid_nodes, Height, Width)`。
- 分布式模式可输入分区后的节点特征，取决于 `expect_partitioned_input`。
- 默认不支持 batch size 大于 1。

# output_schema

- 聚合输出默认为 `(1, output_dim_grid_nodes, Height, Width)`。
- 分布式模式可选择保持分区输出或聚合到一个或所有 rank。

# shape_transformations

1. 非分布式输入从 `(1,C,H,W)` reshape 为 `(H*W,C)`。
2. grid、mesh、边特征被嵌入到 `hidden_dim`。
3. G2M 编码生成 mesh 节点表示和保留 grid 编码表示。
4. processor 在 mesh 图上迭代更新节点和边。
5. M2G 解码将 mesh 表示回传到 grid 节点。
6. finale MLP 映射为 `output_dim_grid_nodes`。
7. 输出从 `(H*W,C_out)` 恢复为 `(1,C_out,H,W)`。

# key_dependencies

- `graph`
- `graphcastprocessor`
- `graphcastprocessorgraphtransformer`
- `graphcastencoderembedder`
- `graphcastdecoderembedder`
- `meshgraphencoder`
- `meshgraphdecoder`
- `meshgraphmlp`
- `cugraphcsc`
- `meshedgeblock`
- `meshnodeblock`

# common_modification_points

- 修改 `input_dim_grid_nodes/output_dim_grid_nodes` 以适配变量集合。
- 调整 `mesh_level`、`multimesh` 和 `khop_neighbors` 控制图连接范围。
- 在 `MessagePassing` 与 `GraphTransformer` 之间选择 processor。
- 调整 `processor_layers`、`hidden_dim` 和 `aggregation` 控制容量。
- 开启分区、CuGraph 或 checkpoint 优化大图训练与推理。

# implementation_risks

- 非分布式模式硬性要求 batch size 为 1。
- processor 层数必须大于 2。
- 分区相关标志互斥关系复杂，`global_features_on_rank_0` 与 `expect_partitioned_input` 不能同时启用。
- 图对象和图特征需要在 `to()` 中同步迁移设备。
- GraphTransformer 分支对 attention mask 调用形式需要与底层实现兼容。

# code_references

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
