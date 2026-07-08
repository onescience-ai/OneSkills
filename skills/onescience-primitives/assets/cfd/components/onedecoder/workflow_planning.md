# description
将 OneDecoder 作为隐表征到输出空间的恢复阶段，规划时优先确认上游表征来源和下游 loss/head 期望。

# when_to_use
当模型已经得到 trunk/processor 隐状态，需要按配置切换具体解码器时使用。

# inputs
- 上游 encoder/processor 的输出结构。
- 目标输出是网格场、节点状态、状态增量还是 atom 表征。
- 维度、尺度数、通道数、skip 顺序。
- 下游 head 或 loss 对输出的约束。

# outputs
- decoder style 与参数。
- 输入字段映射。
- 输出 shape/语义说明。
- 与后续 head 或 rollout 的连接策略。

# procedure
1. 匹配 encoder family。
2. 核对隐藏维度、尺度数和拓扑字段。
3. 构造 OneDecoder。
4. 用样例 batch 验证输出是否能接入 head/loss。
5. 记录输出是绝对物理量还是增量。

# constraints
不要跨 family 混用 encoder/decoder；Graph decoder 需要图拓扑；U-Net decoder 需要尺度对齐的 skip。

# next_phase_recommendation
为目标模型补充端到端 shape smoke test，并明确 decoder 输出到物理变量的映射。

# fallback
若 shape 不匹配，先回退到对应 encoder-decoder 成对实现；若图字段缺失，改用网格 decoder 或补齐构图预处理。
