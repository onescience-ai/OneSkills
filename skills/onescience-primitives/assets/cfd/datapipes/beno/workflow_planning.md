# description

该原语用于选择 BENO 异构图数据协议，将规则底网格椭圆 PDE 数据变成场分支和边界分支共同驱动的图样本。

# when_to_use

- 数据由 RHS、解场和边界条件三类数组组成。
- 模型需要 BENO 风格 `G1/G2/G1+2` 异构图。
- 任务强调边界条件和内部场共同决定标量解。
- 希望预处理后缓存，减少重复构图成本。

# inputs

- 三组 npy 文件和文件前缀。
- 训练/测试样本数。
- 网格分辨率、邻域采样参数和缓存目录。
- 目标是否需要保持 BENO 默认归一化协议。

# outputs

- train/test 图 dataloader。
- 缓存的 `.pt` 异构图样本列表。
- 每个样本的节点特征、边特征、边界信息和监督目标。

# procedure

1. 校验三个 npy 文件是否存在且样本数一致。
2. 校验 `BC` 是否能 reshape 到固定边界点协议。
3. 设置 `cache_dir`，避免重复预处理。
4. 初始化训练集并生成缓存。
5. 初始化测试集，确认目标尺度与评估逻辑匹配。
6. 将 dataloader 接入 BENO 或兼容模型。

# constraints

- 当前实现强依赖固定列布局和边界点数。
- 训练和测试目标尺度不同。
- 图构建参数与底网格分辨率不匹配会导致样本语义错误。

# next_phase_recommendation

若新数据仍是椭圆 PDE 但边界点数不同，先修改预处理 reshape 与边界特征逻辑；若数据是时序 CFD 或规则网格基准，优先考虑 CFDBench、PDEBench 或 DeepCFD。

# fallback

- 缓存损坏时删除对应 `cached_<prefix>_<mode>_<count>.pt` 后重建。
- 边界点数不匹配时先离线重采样边界到 128 点。
- 预处理过慢时先用小 `ntrain/ntest` 验证协议，再放大数据规模。
