# description
OneEncoder 是输入进入模型主干前的表示转换阶段，规划时先判定数据拓扑，再选择 encoder family。

# when_to_use
需要通过统一配置切换不同编码器，或上层模型希望隐藏底层 encoder import 路径时使用。

# inputs
- 数据形态：规则网格、点云、显式图、天气 token 或 atom/pair 特征。
- 目标隐维度与下游 decoder/trunk 需求。
- 是否需要多尺度 skip。
- 是否已有位置编码、边特征和 graph。

# outputs
- encoder style 与参数。
- 输入字段映射。
- 输出结构说明。
- 与 transformer/decoder 的 shape 契约。

# procedure
1. 判断数据拓扑和空间维度。
2. 选择 encoder family。
3. 让 datapipe 输出字段与 forward 签名对齐。
4. 实例化并跑一批 shape 检查。
5. 将输出结构传给后续 trunk/decoder 规划。

# constraints
encoder 与 decoder/trunk 必须在隐藏维度和结构语义上匹配；Graph family 必须具备有效拓扑。

# next_phase_recommendation
补充 encoder-to-decoder 的最小联调样例，记录 skip、节点和边表征的命名约定。

# fallback
若输入不是目标 encoder 支持的形态，先增加预处理或改用更匹配的 encoder；若权重加载失败，检查是否需要裸权重前缀适配。
