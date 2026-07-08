# component_info

TargetDiff 是靶点条件三维小分子扩散生成组件，主要负责在蛋白口袋上下文中生成配体坐标和原子类型；源码包括 `ScorePosNet3D` 扩散主模型、`UniTransformerO2TwoUpdateGeneral` 等变注意力网络、EGNN 备选 refine net 和属性预测网络。

# architecture_overview

TargetDiff 的主模型 `ScorePosNet3D` 同时建模两类随机变量：

- 配体原子坐标：连续高斯扩散
- 配体原子类型：离散 categorical 扩散

蛋白和配体节点先被嵌入到统一上下文图中，再由 refine net 更新节点特征和配体坐标。默认配置使用 `uni_o2`，即蛋白-配体统一图上的二阶等变 Transformer；也可切换到 EGNN。

# parameter_scale

训练配置中的默认主干参数：

- `model_mean_type=C0`
- `beta_schedule=sigmoid`
- `beta_start=1.e-7`
- `beta_end=2.e-3`
- `v_beta_schedule=cosine`
- `v_beta_s=0.01`
- `num_diffusion_timesteps=1000`
- `loss_v_weight=100.0`
- `sample_time_method=symmetric`
- `time_emb_dim=0`
- `center_pos_mode=protein`
- `node_indicator=true`
- `model_type=uni_o2`
- `num_blocks=1`
- `num_layers=9`
- `hidden_dim=128`
- `n_heads=16`
- `edge_feat_dim=4`
- `num_r_gaussian=20`
- `knn=32`
- `num_node_types=8`
- `cutoff_mode=knn`
- `ew_net_type=global`
- `num_x2h=1`
- `num_h2x=1`
- `r_max=10.0`

# architecture_structure

输入上下文
  protein_pos: (N_protein, 3)
  protein_v: (N_protein, F_protein)
  ligand_pos: (N_ligand, 3)
  ligand_v: (N_ligand,)
    -> protein_atom_emb
    -> ligand_atom_emb
    -> compose_context
    -> h_all, pos_all, batch_all, mask_ligand

refine net
  UniTransformerO2TwoUpdateGeneral
    -> build edge graph(knn/radius/hybrid)
    -> edge type: ligand-ligand / ligand-protein / protein-ligand / protein-protein
    -> X2H attention: update hidden states
    -> H2X attention: update ligand coordinates only

扩散输出
  final ligand hidden
    -> v_inference
    -> pred_ligand_v
  final ligand coordinates
    -> pred_ligand_pos

采样循环
  t = T-1 ... 0
    -> predict x0 or noise
    -> q_pos_posterior
    -> categorical posterior
    -> update position and atom type

# input_schema

- 模型初始化：
  - `config`: 训练配置中的 model 节
  - `protein_atom_feature_dim`: 蛋白原子特征维度
  - `ligand_atom_feature_dim`: 配体原子类型/特征维度
- `ScorePosNet3D.forward` 输入：
  - `protein_pos`
  - `protein_v`
  - `batch_protein`
  - `init_ligand_pos`
  - `init_ligand_v`
  - `batch_ligand`
  - `time_step`
  - `return_all`
  - `fix_x`
- 采样脚本输入：
  - `config`: sampling YAML
  - `--data_id`: 测试集样本 ID
  - `--device`: 默认 `cuda:0`
  - `--batch_size`: 默认 `100`
  - `--result_path`: 默认 `./outputs`
- sampling YAML 默认字段：
  - `sample.seed=2021`
  - `sample.num_samples=100`
  - `sample.num_steps=1000`
  - `sample.pos_only=false`
  - `sample.center_pos_mode=protein`
  - `sample.sample_num_atoms=prior`

# output_schema

- `ScorePosNet3D.forward` 输出：
  - `pred_ligand_pos`: 预测配体坐标或干净坐标
  - `pred_ligand_v`: 配体原子类型 logits
  - `final_h`: 全上下文节点最终表征
  - `final_ligand_h`: 配体节点最终表征
  - 可选 `layer_pred_ligand_pos`
  - 可选 `layer_pred_ligand_v`
- `sample_diffusion` 输出：
  - `pos`: 最终配体坐标
  - `v`: 最终配体原子类型
  - `pos_traj`: 坐标轨迹
  - `v_traj`: 原子类型轨迹
  - `v0_traj`: 干净原子类型预测轨迹
  - `vt_traj`: 后验原子类型轨迹
- 采样脚本落盘：
  - `sample.yml`
  - `result_{data_id}.pt`

# shape_transformations

中心化
  protein_pos, ligand_pos
    -> center_pos(mode="protein")
    -> centered protein and ligand coordinates

初始配体
  sample_num_atoms=prior
    -> pocket size
    -> sampled ligand atom count
    -> init_ligand_pos around protein center
    -> init_ligand_v from uniform categorical logits

上下文图
  protein nodes + ligand nodes
    -> h_all: (N_protein + N_ligand, hidden_dim)
    -> pos_all: (N_protein + N_ligand, 3)
    -> mask_ligand: (N_total,)

扩散采样
  ligand_pos_t: (N_ligand, 3)
  ligand_v_t: (N_ligand,)
    -> model prediction
    -> posterior position mean
    -> categorical atom posterior
    -> ligand_pos_{t-1}, ligand_v_{t-1}

# key_dependencies

- `ScorePosNet3D`
- `UniTransformerO2TwoUpdateGeneral`
- `AttentionLayerO2TwoUpdateNodeGeneral`
- `BaseX2HAttLayer`
- `BaseH2XAttLayer`
- `EGNN`
- `PropPredNet`
- `PropPredNetEnc`
- `compose_context`
- `compose_context_prop`
- `FeaturizeProteinAtom`
- `FeaturizeLigandAtom`
- `FeaturizeLigandBond`

# common_modification_points

- 生成数量和速度优先调整 `sample.num_samples`、`sample.num_steps`、`--batch_size`。
- 只优化坐标时启用 `sample.pos_only=true`，但默认会同时采样原子类型。
- 控制配体原子数时修改 `sample.sample_num_atoms`，可选 `prior`、`range`、`ref`。
- 改主干结构时在配置中切换 `model_type=uni_o2|egnn`。
- 改图连接方式时调整 `cutoff_mode`、`knn`、`r_max`。
- 若需要性质预测，使用 `PropPredNet` 或 `PropPredNetEnc`，不要混入生成采样循环。

# implementation_risks

- sampling checkpoint 内保存的训练配置会覆盖/决定模型结构，外部 sampling YAML 只控制采样层参数。
- `--data_id` 必须对应测试集有效样本，否则无法取到蛋白口袋。
- `sample_num_atoms=prior` 依赖 pocket size 估计，可能采样出不合适的原子数。
- 生成结果只包含坐标和原子类型，后续仍需成键、价态、化学有效性和对接/打分过滤。
- `center_pos_mode` 必须和训练/采样约定一致，错误中心化会影响坐标还原。
- 大 batch、1000 步采样和轨迹保存会带来显著显存与磁盘压力。

# code_references

- `{onescience_path}/onescience/src/onescience/models/targetdiff`
