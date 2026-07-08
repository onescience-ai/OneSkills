# description
`uma_escn_md_block` 的规划决策用于确定 UMA backbone 单层消息传递的表达规模、前馈类型和显存策略。它要求在精度、速度、显存、checkpoint 兼容和等变几何一致性之间做取舍。

# when_to_use
- 需要调整 UMA backbone 层宽、角动量或前馈类型。
- 需要排查 eSCNMD forward shape、SO3 mapping 或显存问题。
- 需要决定是否开启 activation checkpoint。
- 需要在普通 backbone 与 MoE backbone 中复用 block。
- 不用于配置输出 head 或 loss。

# inputs
- 任务规模：原子数、边数、材料复杂度。
- 模型配置：`sphere_channels`、`hidden_channels`、`lmax`、`mmax`、层数、`ff_type`。
- 几何对象：edge_index、edge_distance、rotation、Wigner、SO3 mapping。
- checkpoint 来源：是否要求加载预训练权重。
- 资源约束：显存、训练时间、是否 MoE。

# outputs
- block 参数建议：通道、角动量、前馈类型、norm/activation。
- checkpoint 兼容性判断。
- 显存策略：是否启用 activation checkpoint 和 chunk 大小。
- 验证计划：单层 forward、整网 forward、输出 shape 和数值稳定性检查。
- 风险清单：SO3 mapping 错位、edge shape 错、旧权重不兼容。

# procedure
1. 若加载预训练 UMA，优先读取并固定 backbone 结构参数。
2. 根据资源预算估算边数和球谐特征规模。
3. 选择 `ff_type`，先使用 checkpoint 或 demo 默认，再评估 grid/spectral 差异。
4. 在单层 block 上做 forward shape 验证。
5. 若显存不足，优先开启 activation checkpoint 或降低通道/角动量。
6. MoE 场景下检查 `set_mole_ac_start_index` 和 chunk 语义。
7. 与 head/loss 联调前，确认 block 输出 shape 与 node embedding 契约一致。

# constraints
- `lmax/mmax/sphere_channels` 必须贯穿 embedding、block 和 head。
- SO3 mapping 与 rotation 信息必须来自同一次图构建/初始化。
- 不在 block 层处理 dataset key 或 loss key。
- checkpoint 结构不兼容时不要强行跳过关键权重。
- activation checkpoint 不是数值修复手段，只是资源策略。

# next_phase_recommendation
- 建立 backbone 配置卡，记录角动量、通道、ff_type 和 checkpoint。
- 对显存敏感任务做 batch size 与 chunk size 网格测试。
- 对 MoE 任务增加专家路由和 chunk 索引单元测试。
- 与 `uma_head` 对齐 node embedding shape 后再进入训练。

# fallback
- shape mismatch：回退到 checkpoint 原始 backbone 配置。
- 显存不足：降低通道/角动量或开启 activation checkpoint。
- SO3 mapping 异常：重新初始化 rotation/mapping，并用小 batch 验证。
- MoE chunk 错误：关闭 checkpoint 或 MoE wrapper，先跑普通 block。
- 旧权重加载失败：重新初始化改动层，或改回原结构微调。
