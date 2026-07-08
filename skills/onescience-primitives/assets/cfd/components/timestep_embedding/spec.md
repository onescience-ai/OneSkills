# component_info
timestep_embedding 位于 embedding 模块，是无状态函数原语，用于生成扩散模型、时间条件模型或 PDE rollout 中的标量时间步嵌入。

# purpose
- 做什么：把时间步标量转成固定维度周期特征。
- 解决问题：让 MLP/Transformer 可以接收连续或离散 timestep 条件。
- 适用场景：扩散噪声等级、时间条件预测、rollout step 编码。
- 不适用场景：需要可学习日历特征、空间位置编码或多变量时间序列编码。

# input_schema
- `timesteps`: 一维张量 `(N,)`，可为整数或浮点，设备决定输出设备。
- `dim`: 输出嵌入维度，正整数。
- `max_period`: 控制最低频率，默认 `10000`。
- `repeat_only`: 源码保留参数，当前实现未使用。

# output_schema
`embedding`: `(N, dim)`；前半部分为 cos，后半部分为 sin，`dim` 为奇数时末尾补零。

# parameters
- `timesteps`：时间步或噪声等级。
- `dim`：下游条件层期望的维度。
- `max_period=10000`：最大周期尺度。
- `repeat_only=False`：当前不改变行为。

# key_dependencies
- torch
- math

# usage_and_risks
- 源码奇数维补零分支使用三维切片写法，若运行到奇数 `dim` 可能触发索引问题，应优先使用偶数维或先修正实现。
- timesteps 必须是一维；多维输入需先展平或重组。
- 输出未经过可学习投影，下游通常还需 MLP。

# code_references
- `{onescience_path}/onescience/src/onescience/modules/embedding/timestep_embedding.py`
