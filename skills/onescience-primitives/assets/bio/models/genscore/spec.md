# component_info

GenScore 是蛋白-配体图打分模型组件，面向虚拟筛选、pose 排序和贡献分析；它将配体和蛋白口袋分别编码为图表征，再对配体-靶点节点对进行混合密度预测，并通过推理工具输出 CSV 排序结果或原子/残基贡献矩阵。

# architecture_overview

GenScore 采用双图编码器结构：

- 配体分支处理小分子原子、键和坐标图
- 蛋白分支处理口袋原子/残基图
- 两个分支可同时使用 GraphTransformer 或 GatedGCN
- 配体节点与蛋白节点做两两组合
- 输出高斯混合参数、距离项、原子类型和键类型辅助预测

该模型更适合作为候选构象打分器，而不是构象生成器。

# parameter_scale

- 默认 encoder: `gt`
- 可选 encoder: `gt`、`gatedgcn`
- 默认节点特征维度：
  - ligand: `num_node_featsl=41`
  - protein: `num_node_featsp=41`
- 默认边特征维度：
  - ligand: `num_edge_featsl=10`
  - protein: `num_edge_featsp=5`
- 默认隐藏维度：
  - `hidden_dim0=128`
  - `hidden_dim=128`
- 默认高斯分量数 `n_gaussians=10`
- 默认 dropout `dropout_rate=0.15`
- GraphTransformer 默认层数 `num_layers=6`，注意力头数 `num_attention_heads=4`
- GatedGCN 默认层数 `num_layers=6`

# architecture_structure

输入图组织
  ligand graph
    -> ligand encoder(GraphTransformer 或 GatedGCN)
    -> h_l: (N_ligand_nodes, hidden_dim)
  protein/pocket graph
    -> target encoder(GraphTransformer 或 GatedGCN)
    -> h_t: (N_target_nodes, hidden_dim)

节点对交互
  h_l -> dense batch: (Batch, N_l, C)
  h_t -> dense batch: (Batch, N_t, C)
  repeat and concat
    -> C: (Batch, N_l, N_t, 2C)
    -> MLP

预测头
  pair representation
    -> z_pi
    -> z_sigma
    -> z_mu
  ligand node representation
    -> atom_types
  ligand edge representation
    -> bond_types

# input_schema

- CLI 推理输入：
  - `--prot`: 蛋白或口袋 PDB 文件
  - `--lig`: 配体 SDF/MOL2 文件
  - `--model`: GenScore checkpoint
  - `--encoder`: `gt` 或 `gatedgcn`
  - `--outprefix`: 输出文件前缀
  - `--gen_pocket`: 从蛋白和参考配体生成口袋
  - `--cutoff`: 口袋和相互作用截断距离
  - `--reflig`: 生成口袋时的参考配体
  - `--atom_contribution`: 输出原子贡献
  - `--res_contribution`: 输出残基贡献
- 训练输入：
  - `*_ids.npy`
  - `*_lig.pt`
  - `*_prot.pt`
  - label 数据包含在 PDBbindDataset 构造数据中

# output_schema

- 常规推理：
  - `{outprefix}.csv`
  - 字段：`id`、`score`
- 原子贡献推理：
  - `{outprefix}_at.csv`
  - 第一列为 score，其余列为配体原子贡献
- 残基贡献推理：
  - `{outprefix}_res.csv`
  - 第一列为 score，其余列为蛋白残基贡献
- `GenScore.forward` 原始输出：
  - `pi`: 高斯混合权重
  - `sigma`: 高斯尺度
  - `mu`: 高斯均值
  - `dist`: 配体-蛋白节点对距离
  - `atom_types`: 配体原子类型预测
  - `bond_types`: 配体键类型预测
  - `C_batch`: 节点对所属 batch

# shape_transformations

图编码
  ligand Data
    -> h_l.x: (N_l, C)
    -> h_l.pos: (N_l, 3)
  target Data
    -> h_t.x: (N_t, C)
    -> h_t.pos: (N_t, 3)

batch 化
  h_l.x -> to_dense_batch -> (Batch, N_l_max, C)
  h_t.x -> to_dense_batch -> (Batch, N_t_max, C)

节点对组合
  h_l repeat -> (Batch, N_l, N_t, C)
  h_t repeat -> (Batch, N_l, N_t, C)
  concat -> (valid_pairs, 2C)
  MLP -> (valid_pairs, hidden_dim)

输出
  mixture heads -> (valid_pairs, n_gaussians)
  dist -> (valid_pairs, 1)
  atom_types -> (N_l_total, 17)
  bond_types -> (N_lig_edges, 4)

# key_dependencies

- `GenScore`
- `GraphTransformer`
- `GatedGCN`
- `MultiHeadAttentionLayer`
- `GatedGCNLayer`
- `VSDataset`
- `PDBbindDataset`
- `run_an_eval_epoch`
- `run_a_train_epoch`
- `EarlyStopping`

# common_modification_points

- 快速推理优先调整 `--batch_size` 和 `--num_workers`。
- 已有口袋文件时不要启用 `--gen_pocket`；只有输入全蛋白且有参考配体时才启用。
- 需要可解释性时二选一启用 `--atom_contribution` 或 `--res_contribution`，两者不能同时启用。
- 需要更换主干时用 `--encoder gt|gatedgcn`，并保证 checkpoint 与 encoder 匹配。
- 训练新数据时优先调整 `hidden_dim0`、`hidden_dim`、`n_gaussians`、`dist_threhold` 和 `dist_threhold2`，不要先改输出头结构。

# implementation_risks

- `--gen_pocket` 必须同时提供 `--reflig`，否则解析参数时会报错。
- 原子贡献和残基贡献不能同时启用。
- checkpoint 的 encoder 类型和模型结构必须一致，否则权重加载会失败。
- PDB、SDF/MOL2 解析失败或配体多构象格式异常会导致数据集构造失败。
- 源码中字段名使用 `dist_threhold`，拼写与常见 `threshold` 不一致，配置时应保持源码字段名。
- 推理结果是模型分数，不应直接解释为实验结合自由能。

# code_references

- `{onescience_path}/onescience/src/onescience/models/genscore`
