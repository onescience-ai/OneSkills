# description
`uma_embedding` 的规划决策用于确定 UMA backbone 输入阶段应注入哪些结构和条件信息，包括边度、charge、spin 与 dataset。它是多数据集、多电荷自旋状态和 MoE/normalizer 对齐的前置决策点。

# when_to_use
- 需要新增或修改 UMA dataset 条件。
- 需要启用 charge/spin 条件训练或推理。
- 需要调整 edge degree embedding 通道或 cutoff。
- 需要排查 dataset key 映射、条件缺失或 checkpoint shape mismatch。
- 不用于选择输出 head 的具体 loss 权重。

# inputs
- 数据字段：atomic numbers、edge_index、edge_distance、batch、charge、spin、dataset。
- 数据集列表：训练和推理中所有 dataset 名称。
- backbone 配置：sphere channels、lmax/mmax、edge channels、cutoff。
- checkpoint 来源：是否依赖已有 embedding table 或边通道。
- 多任务配置：head wrapper、normalizer、MoE 路由是否使用 dataset 条件。

# outputs
- embedding 配置：edge degree、charge/spin、dataset embedding 是否启用。
- dataset 映射表：dataset 名称到 embedding id 的稳定映射。
- 通道兼容性判断：是否可加载旧 checkpoint。
- 验证计划：单 batch 条件向量、dataset 覆盖、edge embedding shape。
- 风险清单：dataset 漏项、charge/spin 缺失、通道错配。

# procedure
1. 列出训练、验证、推理会出现的所有 dataset 名称。
2. 判断模型是否需要 dataset embedding，并与 head wrapper/normalizer 同步。
3. 判断 charge/spin 是否是物理必要条件；若启用，确认数据字段可靠。
4. 检查 edge degree embedding 与 backbone `sphere_channels`、`lmax/mmax`、edge channels 是否一致。
5. 若加载 checkpoint，保持 embedding table 大小和通道配置不变，新增 dataset 时制定初始化策略。
6. 单 batch forward，打印 embedding shape 和 dataset id 映射。
7. 与 head/loss 联调，确认 dataset 条件不会与输出 key 错配。

# constraints
- dataset 名称必须稳定且大小写一致。
- 不用默认值掩盖 charge/spin 缺失，除非模型训练时明确支持。
- edge embedding 通道不能独立于 block 修改。
- dataset embedding、normalizer 和 head wrapper 应使用同一 dataset 列表。
- checkpoint embedding table 大小变化需要显式处理新增权重。

# next_phase_recommendation
- 为多数据集任务建立 dataset registry，记录顺序、normalizer 和 head 前缀。
- 对 charge/spin 模型增加推理输入校验。
- 对 edge embedding 改动建立 checkpoint 兼容报告。
- 与 `uma_head` 联合检查 dataset-specific 输出。

# fallback
- dataset 映射失败：回退到单 dataset 或扩展 `dataset_list` 后重新初始化 embedding。
- charge/spin 缺失：关闭对应 embedding 或补齐可靠标签。
- edge shape mismatch：恢复 checkpoint 原始通道配置。
- 多数据集 loss 错配：统一 dataset list、head wrapper 和 normalizer。
- 显存不足：启用 edge embedding chunk 或降低 cutoff/edge channels。
