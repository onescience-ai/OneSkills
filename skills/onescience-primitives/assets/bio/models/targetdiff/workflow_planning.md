# description

TargetDiff 规划知识用于直接基于 `ScorePosNet3D` 的张量接口构建蛋白口袋条件配体扩散训练、似然估计、embedding 提取或反向采样代码。

# when_to_use

- 已有蛋白口袋原子坐标/特征和配体训练样本，需要训练 TargetDiff。
- 已有初始化配体坐标/类型，需要执行反向扩散采样。
- 需要固定坐标提取 embedding 或估计 diffusion likelihood。
- 属性预测任务需要独立构建 `PropPredNet` 系列。

# inputs

- checkpoint 对应的 model config。
- `protein_atom_feature_dim` 与 `ligand_atom_feature_dim`。
- 蛋白 `protein_pos`、`protein_v`、`batch_protein`。
- 训练的 clean `ligand_pos`、`ligand_v`、`batch_ligand`，或采样的初始化 position/type。
- 采样的 `num_steps`、`center_pos_mode` 与 `pos_only`。

# outputs

- 前向 position/type predictions 与 hidden representations。
- `get_diffusion_loss` 的 position、type 和总 loss。
- `sample_diffusion` 的最终 position/type 与可选轨迹。
- likelihood KL 或属性模型输出。

# procedure

1. 从 checkpoint 保存的配置确定 diffusion schedule、refine net 和 feature dimensions。
2. 召回 `biology_targetdiff_dataset`，用与训练一致的 featurizer 构造蛋白/配体张量和 batch index。
3. 实例化 `ScorePosNet3D(config, protein_dim, ligand_dim)` 并加载 state dict。
4. 训练调用 `get_diffusion_loss`，对返回的 `loss` 反向传播。
5. 推理初始化配体原子数、position 和 type，调用 `sample_diffusion`。
6. embedding/likelihood 任务分别调用 `fetch_embedding`/`likelihood_estimation`。
7. 若为性质任务，独立实例化 `PropPredNet` 或 `PropPredNetEnc`。

# constraints

- 模型接口只接收源码签名中的 config 与张量参数。
- feature dimensions、atom vocabulary、config 与 checkpoint 必须一致。
- protein 与 ligand batch index 必须描述同一组图。
- 生成坐标/类型不是完整化学分子，后处理不属于模型前向。

# next_phase_recommendation

- 训练结果进入 optimizer、validation 和 checkpoint 流程。
- 采样结果进入成键、价态、化学有效性与口袋适配评估。
- 需要 scoring 时把有效分子交给 docking/打分模型。

# fallback

- state dict 失败时恢复 checkpoint 内的 config 与 feature vocabulary。
- 数值或坐标异常时检查 center mode 和 batch mapping。
- 显存不足时减少 ligand batch/采样轨迹或步数，但记录质量影响。
- 无效分子率高时先检查 `biology_targetdiff_dataset`、atom vocabulary 与后处理，不擅改模型层名。
