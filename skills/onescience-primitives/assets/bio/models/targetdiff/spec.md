# architecture_overview

TargetDiff 的主模型是 `onescience.models.targetdiff.molopt_score_model.ScorePosNet3D`。它在蛋白口袋条件下联合建模配体三维坐标的连续扩散与原子类型的 categorical diffusion，refine net 由配置选择 `uni_o2` 或 `egnn`；属性预测是 `property_pred.prop_model` 中独立的 `PropPredNet`/`PropPredNetEnc`。

# parameter_scale

- `ScorePosNet3D(config, protein_atom_feature_dim, ligand_atom_feature_dim)`。
- `hidden_dim`、`num_diffusion_timesteps`、position/atom beta schedule、`loss_v_weight`、time embedding、center mode 与 refine-net 参数均从 `config` 读取。
- `ligand_atom_feature_dim` 同时决定离散类别数和 `v_inference` 输出维度。
- 蛋白/配体特征维度由实际 featurizer 决定，不能把某个数据转换器的维度当成通用常量。

# architecture_structure

```text
protein positions/features + ligand positions/types
  -> protein_atom_emb + ligand_atom_emb
  -> optional node indicator and time embedding
  -> compose_context
  -> UniTransformerO2TwoUpdateGeneral or EGNN
  -> ligand coordinates + atom-type logits

training: perturb x0/v0 -> forward -> position loss + categorical KL
sampling: reverse timesteps -> coordinate posterior + categorical posterior
```

# input_schema

- `forward(protein_pos, protein_v, batch_protein, init_ligand_pos, init_ligand_v, batch_ligand, time_step=None, return_all=False, fix_x=False)`。
- positions 的末维为 3；`protein_v` 是连续蛋白原子特征；`init_ligand_v` 是离散类别索引。
- `batch_protein` 与 `batch_ligand` 将节点映射到图，且必须描述相同 batch 的口袋/配体对。
- `get_diffusion_loss` 使用 clean ligand position/type；`sample_diffusion` 使用初始化 ligand position/type，并接受 `num_steps`、`center_pos_mode`、`pos_only`。

# output_schema

- `forward` 返回 `pred_ligand_pos`、`pred_ligand_v`、`final_h`、`final_ligand_h`；`return_all=True` 时再返回逐层 position/type 预测。
- `get_diffusion_loss` 返回 `loss_pos`、`loss_v`、`loss` 及训练诊断张量。
- `sample_diffusion` 返回最终 `pos`、`v` 和 `pos_traj`、`v_traj`、`v0_traj`、`vt_traj`。
- `likelihood_estimation` 返回 position 与 atom-type KL；`fetch_embedding` 返回固定坐标的前向结果。

# shape_transformations

1. 配体类别索引 one-hot 后映射到 hidden embedding；蛋白特征单独线性映射。
2. `compose_context` 将两类节点拼成统一图并生成 ligand mask。
3. refine net 更新所有 hidden，只提取 ligand 节点产生坐标与类别 logits。
4. 训练将每图 timestep 展开到 ligand nodes 计算 position MSE 与 categorical KL。
5. 采样按反向 timestep 更新 ligand position/type，并把中心偏移加回最终坐标。

# key_dependencies

当前没有与 TargetDiff refine net 或属性网络一一对应的独立 bio component primitive；构建代码时直接引用本模型的生成、等变网络与属性预测源码模块。

# common_modification_points

- 通过 `config.model_type` 在源码支持的 `uni_o2` 与 `egnn` 间切换。
- 修改 ligand atom vocabulary 时同步修改 featurizer、`ligand_atom_feature_dim` 和 checkpoint。
- 训练调用 `get_diffusion_loss`；推理按源码签名调用 `sample_diffusion`。
- 性质预测使用 `PropPredNet` 系列独立构建，不混入生成模型的 diffusion loss。

# implementation_risks

- checkpoint 的 config 决定网络结构和 diffusion schedule，不能只用外部采样参数重建。
- `center_pos_mode` 在训练和采样阶段必须一致，否则坐标系不一致。
- `pos_only=True` 不更新 atom type，只适用于已有类型的坐标优化。
- 轨迹会复制到 CPU 并随步数增长，占用大量内存。
- 模型输出只是原子坐标与类型，化学成键和有效性需要独立后处理。

# code_references

- `{onescience_path}/onescience/src/onescience/models/targetdiff/molopt_score_model.py`
- `{onescience_path}/onescience/src/onescience/models/targetdiff/uni_transformer.py`
- `{onescience_path}/onescience/src/onescience/models/targetdiff/egnn.py`
- `{onescience_path}/onescience/src/onescience/models/targetdiff/common.py`
- `{onescience_path}/onescience/src/onescience/models/targetdiff/property_pred/prop_model.py`
- `{onescience_path}/onescience/src/onescience/models/targetdiff/property_pred/prop_egnn.py`
