# description
把 timestep_embedding 规划为条件信号准备阶段，用于在进入主干前生成时间/噪声向量。

# when_to_use
需要把标量 step 或 diffusion noise level 注入 MLP、Transformer 或条件归一化时使用。

# inputs
- timestep 来源和形状。
- 下游条件维度。
- 是否需要连续时间。
- 设备和 dtype 约束。

# outputs
- `(N, dim)` 时间步嵌入。
- 与下游条件层的字段映射。
- 是否需要额外可学习投影的建议。

# procedure
1. 从 batch 读取 timestep。
2. 转为一维张量并移动到目标设备。
3. 选择偶数 `dim`。
4. 调用函数生成 embedding。
5. 送入下游条件 MLP 或加到 token 上。

# constraints
dim 应与下游层匹配；优先使用偶数维；不要把它当作空间位置编码。

# next_phase_recommendation
若任务对时间语义复杂，可在该嵌入后增加可学习 MLP，并为奇数维补零逻辑添加测试或修复。

# fallback
若奇数维报错，改用偶数维或修复补零切片；若固定频率效果不足，换成可学习时间 embedding。
