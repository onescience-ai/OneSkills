# launch
主要通过 Python API 在模型配置或上层模块中实例化，不是独立 CLI 入口。下面的命令会从源码模块导入组件并打印完整构造签名，便于确认全部 API 参数：

```sh
python -c "from onescience.modules.utils.graphcast.graph import Graph; import inspect; print(inspect.signature(Graph))"
```

在真实任务中应由对应模型配置传入尺寸、通道数和隐空间维度等参数。

# input_schema
- 图节点特征：`(N_nodes, feature_dim)`
- 图边特征：`(N_edges, feature_dim)`
- 图结构：DGL 图或等价的源/目标索引关系。

默认参数信息：

- `Graph` 构造默认参数：`mesh_level=6`，`multimesh=True`，`khop_neighbors=0`，`dtype=torch.float`
- `Graph.create_mesh_graph` 调用默认参数：`verbose=True`
- `Graph.create_g2m_graph` 调用默认参数：`verbose=True`
- `Graph.create_m2g_graph` 调用默认参数：`verbose=True`

# runtime_interfaces
- `Graph`：实例化后通过 `khop_adj_all_k`, `create_mesh_graph`, `create_g2m_graph`, `create_m2g_graph` 等运行时接口参与流水线。

# main_functions
- `khop_adj_all_k`
- `create_mesh_graph`
- `create_g2m_graph`
- `create_m2g_graph`

# execution_resources
- 运行设备由上层任务决定，训练和高分辨率推理通常建议使用 GPU。
- 图构建、邻居搜索或大分辨率气象场处理会占用较多内存，批量大小需随网格规模调整。
- 需要保证依赖库和 OneScience 模块路径可用，并与模型配置中的精度、设备和维度设置一致。

# operation_limits
- 不负责完整数据预处理、变量标准化、训练循环或损失函数编排。
- 仅在输入形状、变量顺序、图结构和上下游组件契约一致时可稳定工作。
- 源码中未声明的 CLI 参数、自动下载或外部数据读取能力不应假定存在。
