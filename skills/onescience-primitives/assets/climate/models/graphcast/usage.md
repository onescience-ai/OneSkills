# launch

Python API 启动示例：

```sh
python -c "import torch; from onescience.models.graphcast import GraphCastNet; model=GraphCastNet(mesh_level=6, multimesh_level=None, multimesh=True, input_res=(721,1440), input_dim_grid_nodes=237, input_dim_mesh_nodes=3, input_dim_edges=4, output_dim_grid_nodes=227, processor_type='MessagePassing', khop_neighbors=32, num_attention_heads=4, processor_layers=16, hidden_layers=1, hidden_dim=512, aggregation='sum', activation_fn='silu', norm_type='LayerNorm', use_cugraphops_encoder=False, use_cugraphops_processor=False, use_cugraphops_decoder=False, do_concat_trick=False, recompute_activation=False, partition_size=1, partition_group_name=None, use_lat_lon_partitioning=False, expect_partitioned_input=False, global_features_on_rank_0=False, produce_aggregated_output=True, produce_aggregated_output_on_all_ranks=True); x=torch.randn(1,237,721,1440); y=model(x); print(y.shape)"
```

# input_schema

- 默认输入是 `(1, input_dim_grid_nodes, Height, Width)`。
- 默认参数：`mesh_level=6`，`multimesh_level=None`，`multimesh=True`，`input_res=(721, 1440)`，`input_dim_grid_nodes=237`，`input_dim_mesh_nodes=3`，`input_dim_edges=4`，`output_dim_grid_nodes=227`。
- 默认 processor 参数：`processor_type="MessagePassing"`，`khop_neighbors=32`，`num_attention_heads=4`，`processor_layers=16`，`hidden_layers=1`，`hidden_dim=512`，`aggregation="sum"`，`activation_fn="silu"`，`norm_type="LayerNorm"`。
- 默认运行/分区参数：`use_cugraphops_encoder=False`，`use_cugraphops_processor=False`，`use_cugraphops_decoder=False`，`do_concat_trick=False`，`recompute_activation=False`，`partition_size=1`，`partition_group_name=None`，`use_lat_lon_partitioning=False`，`expect_partitioned_input=False`，`global_features_on_rank_0=False`，`produce_aggregated_output=True`，`produce_aggregated_output_on_all_ranks=True`。
- 默认输入 shape：`(1, 237, 721, 1440)`。
- batch size 默认只能为 1。
- 输入变量应按训练时的 grid node feature 顺序排列。
- 分布式模式下需根据分区策略准备全局或分区节点特征。

# runtime_interfaces

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

# main_functions

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

# execution_resources

- 默认全球图规模大，推荐 GPU。
- 分区或 CuGraph 路径适合大规模训练和多设备部署。
- checkpoint 可降低训练显存，但会增加计算时间。
- 需要图构造和图消息传递相关运行依赖。

# operation_limits

- 默认非分布式 batch size 不可大于 1。
- 输入输出特征维度必须与模型初始化一致。
- 分区输入和全局 rank 输入的标志不能冲突。
- 修改网格分辨率会重建图，权重迁移需谨慎。
