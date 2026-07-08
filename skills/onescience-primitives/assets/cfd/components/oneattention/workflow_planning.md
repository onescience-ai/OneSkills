# description
在任务编排中将 OneAttention 视作注意力分发器：先判断数据拓扑和注意力语义，再选择具体 style，并把 shape/mask/坐标准备工作安排在它之前。

# when_to_use
当上层模块需要注意力机制但希望通过统一配置切换 Earth、Transolver、线性、窗口或 Protenix 注意力时使用。

# inputs
- 数据拓扑：规则网格、非结构化点云、token 序列或 pair/atom 表征。
- 空间维度：1D/2D/3D。
- 复杂度预算：token 数、head 数、显存上限。
- 所需偏置：窗口 mask、pair bias、物理切片或坐标信息。

# outputs
- 选定的 `style`。
- 对应构造参数字典。
- 上游需要准备的 mask、shapelist、坐标或 pair 表征清单。
- 与后续 transformer block 的 shape 约定。

# procedure
1. 判断输入是规则网格、非结构点云还是结构化 token。
2. 根据维度和物理语义筛选 attention family。
3. 核对底层 style 的 forward 签名与上游张量。
4. 在模型构造时实例化 OneAttention。
5. 在首个 batch 上检查输出 shape 与 residual 分支是否一致。

# constraints
style 必须在注册表中；kwargs 必须属于目标实现；OneAttention 不改变输入输出结构，不应承担数据预处理职责。

# next_phase_recommendation
若注意力用于新模型，下一阶段应补充最小 shape 测试，并记录 style 与 datapipe 输出字段之间的映射。

# fallback
style 不匹配时退回底层具体 attention 源码确认签名；显存不足时优先切换窗口/线性/物理切片注意力或减少 token、head、slice_num。
