# launch

GenScore 是蛋白口袋—配体复合物打分模型。训练/推理代码应先用图编码器构造 `GenScore`，再传入成对的 PyTorch Geometric 配体图和靶标图。

```sh
python -c "from onescience.models.genscore.model.model import GenScore; from onescience.models.genscore.inference import scoring; import inspect; print(inspect.signature(GenScore)); print(inspect.signature(GenScore.forward)); print(inspect.signature(scoring))"
```

# input_schema

- `ligand_graph`、`target_graph`：PyTorch Geometric `Data`/`Batch`，至少包含 `x`、`pos`、`edge_index`、`batch`；边编码器还会读取 `edge_attr`。
- 两个图 batch 的复合物数量和样本顺序必须一致，坐标单位必须一致。
- 构造参数：`in_channels` 为编码器输出宽度，`hidden_dim` 为混合层宽度，`n_gaussians` 为混合密度分量数，`dropout_rate` 控制正则化，源码参数名为 `dist_threhold`。
- 输出七元组 `(pi, sigma, mu, dist, atom_types, bond_types, C_batch)`：混合密度参数、原子对距离、原子/键辅助预测及原子对所属 batch。
- 最终亲和力或排序分数应由训练时采用的 GenScore 损失/后处理基于上述输出计算。

# runtime_interfaces

- `GenScore`：组合配体编码器、靶标编码器与混合密度头的完整模型。
- `GenScore.forward(data_ligand, data_target)`：核心训练与推理前向。
- `GraphTransformer`、`GatedGCN`：可选图编码器实现。
- `onescience.models.genscore.inference.scoring`：从结构文件构图、加载权重并执行批量打分的高层 Python 接口。
- `onescience.models.genscore.train._build_encoder`：按训练配置创建匹配的双编码器。

# main_functions

- `GenScore.forward`
- `GenScore.compute_euclidean_distances_matrix`
- `scoring`
- `_build_encoder`

# execution_resources

- 依赖 PyTorch、PyTorch Geometric、RDKit/DGL 相关分子处理依赖和匹配编码器的 checkpoint。
- 数据准备应召回 datapipe 资源 `biology_genscore_dataset`，并由 `onescience.datapipes.genscore` 生成模型所需的图字段。
- GPU 适合训练和大批量打分；小批量可在 CPU 上运行，但图构建可能成为瓶颈。

# operation_limits

- GenScore 是复合物打分模型，不生成配体或蛋白结构。
- checkpoint 必须与 `gt`/`gatedgcn` 编码器、特征维度和高斯分量数一致。
- 原子贡献和残基贡献属于模型归因信号，不是严格的物理能量分解。
- 全蛋白输入需先确定口袋，否则大量无关原子会影响效率和分数解释。
