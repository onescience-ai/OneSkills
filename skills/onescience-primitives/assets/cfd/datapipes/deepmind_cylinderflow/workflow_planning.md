# description

该原语用于选择 DeepMind MeshGraphNet 风格圆柱流 rollout 数据流，把 TFRecord 轨迹拆成逐时间步图样本。

# when_to_use

- 数据是 DeepMind 风格 `meta.json + split.tfrecord`。
- 任务是瞬态圆柱绕流或相似网格时序预测。
- 模型需要 DGL 图、边特征、节点类型 one-hot 和 rollout mask。
- 训练流程来自 Vortex_shedding_mgn 或兼容 MeshGraphNet。

# inputs

- TFRecord 数据根目录。
- 每个 split 的轨迹数量和时间步数。
- 训练噪声标准差。
- 统计量输出目录和 batch 参数。

# outputs

- train/val/test GraphDataLoader。
- 训练图样本和验证/测试 rollout 解包样本。
- 节点/边归一化统计量。

# procedure

1. 校验 `meta.json` 与 TFRecord 文件存在。
2. 先运行训练 split 生成统计量。
3. 确认节点输入和目标维度与模型配置一致。
4. 设置每条轨迹展开时间步，控制总样本量。
5. 在训练脚本中区分 train 与 val/test 返回协议。

# constraints

- 依赖 TensorFlow 和 DGL。
- 图拓扑来自 cells，缺失 cells 无法构造边。
- 该协议以 rollout 为中心，不适合静态单步几何回归。

# next_phase_recommendation

若新数据仍是 TFRecord 轨迹但字段稍有不同，优先写解析适配；若是粒子拉格朗日数据，使用 DeepMindLagrangian；若是规则网格，改用 CFDBench 或 PDENNEval。

# fallback

- 统计量缺失时先单独初始化训练集。
- 环境缺 TensorFlow/DGL 时先转换为 h5/npy，再选择其它 datapipe。
- batch 内存不足时降低 batch size 或减少 `num_steps`。
