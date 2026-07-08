# description
在规划中把 OneEdge 放在节点更新之前，用于从当前节点状态和边属性计算新的边消息。

# when_to_use
当模型需要通过统一入口切换或复用不同 边更新 实现时使用。

# inputs
- 数据拓扑与空间维度。
- 上下游模块的 shape/字段契约。
- 目标 style 的参数需求。
- 资源预算与失败容忍度。

# outputs
- 选定 style。
- 构造参数。
- 运行时输入字段映射。
- 输出语义和后续连接策略。

# procedure
1. 从任务数据形态筛选候选 style。
2. 回到目标 style 源码确认构造参数与 forward 参数。
3. 准备最小 batch 验证 shape。
4. 接入上游和下游模块。
5. 记录限制条件和 fallback。

# constraints
不跨语义混用 style；不把 wrapper 当作数据适配层；新增底层实现后必须注册。

# next_phase_recommendation
为被选 style 增加端到端 smoke test，并补充示例配置。

# fallback
若 style 不支持当前输入，改用同 family 更匹配实现；若无可用 style，先实现专用适配层或回退到底层模块直接调用。
