# architecture_overview

GenScore 是蛋白-配体图对的混合密度模型。`GenScore` 接收独立的 ligand encoder 与 target encoder，组合两侧节点表征，对有效配体-靶点节点对预测高斯混合参数，同时输出配体原子类型和键类型；源码提供 `GraphTransformer` 与 `GatedGCN` 两类可选编码器。

# parameter_scale

- `GenScore(ligand_model, target_model, in_channels, hidden_dim, n_gaussians, dropout_rate=0.15, dist_threhold=1000)`。
- 参数名在源码中是 `dist_threhold`，构建代码必须保留该拼写。
- `inference._build_encoder` 的 GraphTransformer/GatedGCN 路径均使用 6 层和 `dropout_rate=0.15`，GraphTransformer 使用 4 个 attention heads；这些是该辅助构建函数的配置，不是 `GenScore` 类的固定常量。

# architecture_structure

```text
ligand graph -> ligand encoder -> ligand node embeddings
target graph -> target encoder -> target node embeddings
  -> dense ligand-target node pairs + validity mask
  -> MLP
  -> pi / sigma / mu

ligand node and edge embeddings
  -> atom_types / bond_types
```

# input_schema

- 构造器需要两个返回带 `x`、`pos`、`batch` 的图编码器。
- `forward(data_ligand, data_target)` 接收 PyTorch Geometric 风格的配体与靶点 batch。
- 编码后两侧 batch size 必须可配对；配体还必须提供 `edge_index` 供键类型头使用。
- 高层 `scoring(prot, lig, modpath, ...)` 负责从结构输入构造 `VSDataset`、编码器和 checkpoint 模型。

# output_schema

`GenScore.forward` 返回七元组：

1. `pi`：节点对的高斯混合权重。
2. `sigma`：高斯尺度。
3. `mu`：高斯均值。
4. `dist.unsqueeze(1).detach()`：节点对距离目标。
5. `atom_types`：配体节点原子类型 logits。
6. `bond_types`：配体边键类型 logits。
7. `C_batch`：每个有效节点对所属的 batch 索引。

# shape_transformations

1. 两个图编码器产生节点 embedding 与坐标。
2. `to_dense_batch` 将节点整理为 `(B, N_l, C)` 和 `(B, N_t, C)`。
3. 展开为 `(B, N_l, N_t, 2C)`，再按两侧有效 mask 压平。
4. MLP 将节点对表征映射到 `n_gaussians` 个混合参数。
5. 原子与键分类头分别作用于配体节点和配体边。

# key_dependencies

当前没有与 GenScore 编码器一一对应的独立 bio component primitive；构建代码时直接使用模型源码中的 GraphTransformer、GatedGCN 与 GenScore。

# common_modification_points

- 在 `GraphTransformer` 与 `GatedGCN` 之间切换时，保持两侧 encoder 输出通道等于 `in_channels`。
- 修改图特征时同步更新 ligand/target node 与 edge feature 维度。
- 若需要最终标量 score，复用损失或 `run_an_eval_epoch` 的混合密度后处理，不要把 `forward` 七元组误写为标量。
- 原子/残基贡献分析属于高层 scoring 分支，不改变模型前向返回协议。

# implementation_risks

- 配体和靶点图 batch 对齐错误会导致节点对与 `C_batch` 失配。
- 输入 encoder 若不保留 `x`、`pos`、`batch`，`GenScore.forward` 无法执行。
- checkpoint 与 encoder 类型或特征维度不一致时不能直接加载。
- 距离计算包含固定 reshape 逻辑，改变靶点坐标组织前必须核验源码假设。

# code_references

- `{onescience_path}/onescience/src/onescience/models/genscore/model/model.py`
- `{onescience_path}/onescience/src/onescience/models/genscore/inference.py`
- `{onescience_path}/onescience/src/onescience/models/genscore/train.py`
