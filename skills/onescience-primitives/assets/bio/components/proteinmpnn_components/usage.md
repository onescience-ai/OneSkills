# launch

该原语描述 ProteinMPNN 的骨架图特征器、编码层和自回归解码层。通常由完整 `ProteinMPNN` 自动构造；只有开发新架构或调试中间表征时才单独调用组件。

```sh
python -c "from onescience.models.proteinmpnn.protein_mpnn_utils import ProteinFeatures, EncLayer, DecLayer; import inspect; print(inspect.signature(ProteinFeatures)); print(inspect.signature(ProteinFeatures.forward)); print(inspect.signature(EncLayer)); print(inspect.signature(EncLayer.forward)); print(inspect.signature(DecLayer)); print(inspect.signature(DecLayer.forward))"
```

# input_schema

- `X`：`[batch, residues, atoms, 3]` 骨架坐标；`mask` 为有效残基。
- `residue_idx` 和 `chain_encoding_all` 控制位置偏移与跨链边特征。
- `ProteinFeatures` 输出邻接边特征 `E` 与邻居索引 `E_idx`；维度由 `edge_features` 和 `top_k` 决定。
- `EncLayer` 输入节点/边 embedding、邻居索引与 mask；`DecLayer` 还接收序列条件和自回归 attention mask。

# runtime_interfaces

- `ProteinFeatures`：坐标到 KNN 几何图。
- `EncLayer`：同时更新节点和边 embedding。
- `DecLayer`：按解码顺序更新序列表征。
- `gather_edges`、`gather_nodes`、`cat_neighbors_nodes`：邻域张量操作。
- `ProteinMPNN.forward/sample/tied_sample`：推荐的完整模型编排接口。

# main_functions

- `ProteinFeatures.forward`
- `EncLayer.forward`
- `DecLayer.forward`
- `gather_edges`
- `gather_nodes`
- `cat_neighbors_nodes`

# execution_resources

- 依赖 PyTorch；图内存随链长和 `k_neighbors` 增长。
- 坐标、mask、链编码和组件参数必须位于同一设备。
- 训练时坐标增强由 `augment_eps` 控制，推理通常应与 checkpoint 配置保持一致。

# operation_limits

- 组件只构造/更新内部图表征，不完成序列采样、约束解析或结构文件读取。
- `chain_M` 的设计位点含义与 padding `mask` 不同，不能混用。
- 缺失主链原子、错误链编号或不连续 batch 会导致错误几何关系。
