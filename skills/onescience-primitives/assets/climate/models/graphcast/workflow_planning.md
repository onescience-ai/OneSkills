# description

GraphCast 规划知识用于在全球天气任务中选择图网格模型，编排网格特征到 mesh 表示、mesh 传播、再回到经纬网格的完整流程。

# when_to_use

- 需要在规则经纬网格和非结构 mesh 之间传播信息。
- 任务关注全球尺度长距离依赖。
- batch size 为 1 可以接受，或已有分布式图分区方案。
- 需要可控的消息传递层数、mesh level 和输出变量维度。

# inputs

- 输入网格分辨率。
- grid node 输入特征维度与输出特征维度。
- mesh level、processor 类型和 processor 层数。
- 是否启用分区、CuGraph、checkpoint。

# outputs

- 聚合后的经纬网格预测张量。
- 或分布式场景下的分区节点预测结果。

# procedure

1. 根据数据变量集合确定输入/输出 feature 维度。
2. 根据分辨率和性能预算选择 `mesh_level` 与 processor 类型。
3. 实例化模型并构建图。
4. 根据显存设置 checkpoint 或分区策略。
5. 调用 `forward` 并恢复输出。
6. 做物理变量反归一化与范围检查。

# constraints

- 非分布式默认只支持 batch size 1。
- processor 层数至少为 3。
- 图构造绑定输入分辨率。
- 分区参数必须与运行环境和数据切分方式一致。

# next_phase_recommendation

- 为生产环境固化图缓存，避免重复构图成本。
- 对分区模式建立专门的输入输出适配器。
- 为 checkpoint 策略做显存与速度基准测试。

# fallback

- 若无法满足图依赖或 batch size 限制，可改用 Pangu/FengWu 等规则网格模型。
- 若分布式配置失败，先回退到 `partition_size=1` 验证单卡逻辑。
- 若显存不足，优先降低 mesh level 或 hidden_dim，再考虑分区。
