# Contract: TimestepEmbedding

## 基本信息

- 组件名：`TimestepEmbedding`
- 所属模块族：`embedding`
- 统一入口：`not_applicable`
- 注册名：`style="TimestepEmbedding"`

## 组件说明
timestep_embedding 位于 embedding 模块，是无状态函数原语，用于生成扩散模型、时间条件模型或 PDE rollout 中的标量时间步嵌入。

## 用途
- 做什么：把时间步标量转成固定维度周期特征。
- 解决问题：让 MLP/Transformer 可以接收连续或离散 timestep 条件。
- 适用场景：扩散噪声等级、时间条件预测、rollout step 编码。
- 不适用场景：需要可学习日历特征、空间位置编码或多变量时间序列编码。

## 输入规格
- `timesteps`: 一维张量 `(N,)`，可为整数或浮点，设备决定输出设备。
- `dim`: 输出嵌入维度，正整数。
- `max_period`: 控制最低频率，默认 `10000`。
- `repeat_only`: 源码保留参数，当前实现未使用。

## 输出规格
`embedding`: `(N, dim)`；前半部分为 cos，后半部分为 sin，`dim` 为奇数时末尾补零。

## 参数
- `timesteps`：时间步或噪声等级。
- `dim`：下游条件层期望的维度。
- `max_period=10000`：最大周期尺度。
- `repeat_only=False`：当前不改变行为。

## 关键依赖
- torch
- math

## 使用注意与风险
- 源码奇数维补零分支使用三维切片写法，若运行到奇数 `dim` 可能触发索引问题，应优先使用偶数维或先修正实现。
- timesteps 必须是一维；多维输入需先展平或重组。
- 输出未经过可学习投影，下游通常还需 MLP。

## 启动方式
Python API 启动示例：

``` sh
python -c "import torch; from onescience.modules.embedding.timestep_embedding import timestep_embedding; print(timestep_embedding(torch.arange(4), dim=128).shape)"
```

## 输入规格
从 batch 中提取 timestep、噪声 level 或 rollout index，转成与模型同设备的一维张量；dim 与后续条件投影层保持一致。

## 运行接口
- `timestep_embedding(timesteps, dim, max_period=10000, repeat_only=False)`：返回正弦时间步嵌入。

## 主要函数
- `timestep_embedding`

## 执行资源
CPU/GPU 均可，计算量很小；输出设备跟随 `timesteps.device`。

## 操作限制
仅生成固定正弦特征，不学习时间语义；当前实现对奇数维存在潜在索引风险。

## 规划决策

### 描述
把 timestep_embedding 规划为条件信号准备阶段，用于在进入主干前生成时间/噪声向量。

### 使用时机
需要把标量 step 或 diffusion noise level 注入 MLP、Transformer 或条件归一化时使用。

### 输入
- timestep 来源和形状。
- 下游条件维度。
- 是否需要连续时间。
- 设备和 dtype 约束。

### 输出
- `(N, dim)` 时间步嵌入。
- 与下游条件层的字段映射。
- 是否需要额外可学习投影的建议。

### 执行步骤
1. 从 batch 读取 timestep。
2. 转为一维张量并移动到目标设备。
3. 选择偶数 `dim`。
4. 调用函数生成 embedding。
5. 送入下游条件 MLP 或加到 token 上。

### 约束
dim 应与下游层匹配；优先使用偶数维；不要把它当作空间位置编码。

### 下一阶段建议
若任务对时间语义复杂，可在该嵌入后增加可学习 MLP，并为奇数维补零逻辑添加测试或修复。

### 回退策略
若奇数维报错，改用偶数维或修复补零切片；若固定频率效果不足，换成可学习时间 embedding。

## 源码锚点

- `{onescience_path}/onescience/src/onescience/modules/embedding/timestep_embedding.py`
