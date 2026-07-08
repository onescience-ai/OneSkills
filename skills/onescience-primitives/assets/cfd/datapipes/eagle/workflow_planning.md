# description

该原语用于网格时序预测任务，将不同规模仿真轨迹窗口整理成可 batch 的 padded 字典。

# when_to_use

- 数据由 split 文本和仿真目录组成。
- 每个样本有不等节点数、边数或 cluster 数。
- 训练需要时间窗口而不是单帧样本。
- 模型使用 mesh edges、mask 或 cluster pooling。

# inputs

- 数据根目录、split 目录和可选 cluster 目录。
- train/valid/test 窗口长度。
- cluster 数、是否 one-hot 节点类型、是否保留 cells。
- batch size 和 num_workers。

# outputs

- train/val/test DataLoader。
- padding 后的速度、压力、节点、边、mask 和 cluster batch。
- 可选归一化/反归一化能力。

# procedure

1. 校验 split 文件名和路径。
2. 抽查 `sim.npz` 字段和 `triangles.npy` 形状。
3. 根据模型选择 `with_cells` 和 `n_cluster`。
4. 设置窗口长度，确认训练脚本如何切分输入/目标。
5. 构造 datapipe 并监控空样本过滤情况。

# constraints

- `n_cluster` 不是任意整数。
- padding 会放大显存占用。
- 归一化统计量不可自动适配新数据分布。

# next_phase_recommendation

若需要 DGL/PyG 图对象，增加图对象包装层；若数据已经是规则网格张量，用 CFDBench 或 DeepCFD；若是粒子轨迹，用 DeepMindLagrangian。

# fallback

- 空 batch 出现时先清理坏样本或降低 batch size。
- cluster 文件缺失时设置 `n_cluster=1` 或关闭 cluster 分支。
- padding 过大时按节点数分桶采样或降低 batch size。
