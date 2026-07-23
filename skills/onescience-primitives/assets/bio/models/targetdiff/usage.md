# launch

TargetDiff 是蛋白口袋条件的小分子三维扩散模型。模型原语的核心入口为 `ScorePosNet3D`：训练使用 `get_diffusion_loss`，推理先为每个口袋构造初始配体坐标和原子类型，再调用 `sample_diffusion`。

```sh
python -c "from onescience.models.targetdiff.molopt_score_model import ScorePosNet3D; import inspect; print(inspect.signature(ScorePosNet3D)); print(inspect.signature(ScorePosNet3D.forward)); print(inspect.signature(ScorePosNet3D.get_diffusion_loss)); print(inspect.signature(ScorePosNet3D.sample_diffusion)); print(inspect.signature(ScorePosNet3D.likelihood_estimation))"
```

# input_schema

- 蛋白输入：`protein_pos [N_protein, 3]`、`protein_v [N_protein, protein_feature_dim]`、`batch_protein [N_protein]`。
- 配体输入：坐标 `[N_ligand, 3]`、离散原子类型 `[N_ligand]`、`batch_ligand [N_ligand]`；batch 索引必须从零连续编号并与蛋白 batch 一一对应。
- 按 `FeaturizeProteinAtom` 默认配置，蛋白特征为元素、氨基酸类型、是否主链共 27 维；按 `FeaturizeLigandAtom(mode="add_aromatic")` 为 13 类离散原子特征。若修改 transform，构造维度必须同步修改。
- 主要配置包括 `hidden_dim`、`model_type`、`num_diffusion_timesteps`、位置/原子类型 beta schedule、`model_mean_type`、时间嵌入、中心化策略和 `loss_v_weight`。
- `get_diffusion_loss` 返回含 `loss`、`loss_pos`、`loss_v` 及重建预测的字典。
- `sample_diffusion` 返回最终配体坐标/类型以及坐标和原子类型轨迹；调用方负责按 batch 拆分分子并恢复中心偏移。

# runtime_interfaces

- `ScorePosNet3D(config, protein_atom_feature_dim, ligand_atom_feature_dim)`：TargetDiff 完整生成模型。
- `ScorePosNet3D.forward(...)`：给定扩散时间步预测配体坐标和原子类型 logits。
- `ScorePosNet3D.get_diffusion_loss(...)`：训练损失入口。
- `ScorePosNet3D.sample_diffusion(...)`：反向扩散推理入口。
- `ScorePosNet3D.likelihood_estimation(...)`、`fetch_embedding(...)`：似然项估计与表征提取。
- `PropPredNet`：独立的性质预测模型，不替代生成模型。

# main_functions

- `ScorePosNet3D.forward`
- `ScorePosNet3D.get_diffusion_loss`
- `ScorePosNet3D.sample_diffusion`
- `ScorePosNet3D.likelihood_estimation`
- `ScorePosNet3D.fetch_embedding`
- `PropPredNet.forward`

# execution_resources

- 依赖 PyTorch、PyTorch Geometric、`torch_scatter` 及 TargetDiff 图网络依赖。
- 上游应召回 datapipe 资源 `biology_targetdiff_dataset`，使用 `onescience.datapipes.targetdiff` 与 `onescience.utils.targetdiff.transforms` 产生口袋图、配体图和 batch 字段。
- GPU/DCU 适合训练和批量采样；耗时主要由口袋/配体原子数、扩散步数、图邻域和批量大小决定。
- checkpoint 必须与特征维度、原子类别数、扩散日程和 refine network 配置一致。

# operation_limits

- TargetDiff 需要已定义的蛋白结合口袋，不负责从全蛋白自动发现口袋。
- 模型生成原子类型和三维坐标，不保证成键、价态、连通性或化学有效性；输出必须经过分子重建和过滤。
- `sample_diffusion` 不读取结构文件、不决定每个样本的配体原子数，也不保存 SDF；这些职责属于数据准备和推理包装层。
- 训练与推理必须使用相同的中心化、元素集合、芳香性编码和单位。
