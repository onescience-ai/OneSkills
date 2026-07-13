# description

用于规划小分子图到 latent 条件的编码阶段，适合分子生成、优化或蛋白-配体任务中的 ligand 表征候选。

# when_to_use

- 输入是 SMILES/SDF 转换得到的 atom/bond feature。
- 任务需要小分子 latent 表征。
- 希望为 TargetDiff、GenScore 或 DiffDock 增加分子图候选编码器。

# inputs

- atom/bond 离散特征。
- mask、neighbor list。
- MolSculptor encoder 配置。

# outputs

- prefix atom latent。
- 图编码器适配建议。
- 与 decoder/diffusion 的连接方式。

# procedure

1. 标准化分子并提取 atom/bond feature。
2. 检查类别编号和 mask。
3. 调用 graph encoder 得到 prefix latent。
4. 连接 SMILES decoder 或 diffusion transformer。

# constraints

- 不读取蛋白 pocket。
- 不保证分子合法性。
- atom/bond 词表必须匹配训练配置。

# next_phase_recommendation

若目标是生成，接 diffusion transformer 或 SMILES decoder；若目标是评分，需要另接任务 head。

# fallback

若图特征缺失，先退回 RDKit 标准化和特征化流程；若大分子超出原子上限，裁剪或提高 padding 配置。
