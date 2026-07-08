# component_info
`uma_loss` 是 UMA loss 族组件，定位为多任务材料势函数训练的损失注册与分布式归约层。它通过 registry/Hydra class path 调用，为 energy、forces、stress 等任务提供基础误差函数和 DDP 修正封装。

# purpose
- 用途：计算 UMA 单任务和多任务 loss，并修正 DDP 下样本数或原子数不均衡造成的梯度尺度偏差。
- 解决问题：在不同物理量、mask 和 reduction 策略下得到一致的训练标量。
- 适用场景：UMA energy/forces/stress 多任务训练、per-atom 标量任务、向量力任务、DDP 训练。
- 不适用场景：模型输出 head 构造、normalizer 参数估计、图构建。

# input_schema
- `pred` / `input`: 预测张量，shape 必须与 target 或 mask 约定一致。
- `target`: 标签张量，会被 view 到 input shape，NaN/Inf 在部分封装中会被处理。
- `natoms`: `(NumGraphs,)`，用于 per-atom 或 per-structure reduction。
- `mult_mask`: 任务 mask，首维需与 input/target 对齐。
- `coefficient`: 任务损失系数。
- normalizer / element reference 后处理结果：通常在进入 loss 前完成。
- DDP 上下文：全局样本数通过 `distutils.all_reduce` 修正。

# output_schema
- 单任务标量 loss。
- `DDPMTLoss`: 输出乘以 `coefficient` 且经 mask、reduction、DDP 修正后的标量。
- `DDPLoss`: 输出经基础 loss 与 mean/sum reduction 后的标量。
- 训练 unit 可将多个任务 loss 聚合为总 loss dict。

# parameters
- `loss_fn`: 基础 loss 模块，如 MAE/MSE/L2Norm。
- `loss_name`: registry 中的 loss 名称。
- `reduction`: `"mean"`、`"sum"` 或 `"per_structure"`。
- `coefficient`: loss 系数。
- `normalizer`: 配置层常见字段，通常在 loss 前后处理。
- `element_references`: 能量参考修正，通常由训练 unit 管理。

# key_dependencies
- `uma_head.py`
- `uma_normalization.py`
- `mlip_unit.py`
- `registry.py`
- `distutils.py`
- `gp_utils.py`

# usage_and_risks
- 典型使用：UMA Hydra `tasks_list` 为每个 property 指定 loss 名称、coefficient 和 reduction，训练 unit 读取 head 输出并调用 loss。
- `natoms` 缺失或错误会污染 per-atom/per-structure loss。
- force 向量任务应优先使用向量范数或明确 reduction，避免改变训练目标。
- normalizer/element reference 与 head 输出不匹配会导致能量偏移。
- 多任务 key 与 head output key 不一致会在训练首步失败。
- DDP 下不要绕过封装直接对本地 batch 求 mean。

# code_references
- `{onescience_path}/onescience/src/onescience/modules/loss/uma_loss.py`
- `{onescience_path}/onescience/src/onescience/utils/uma/units/mlip_unit/mlip_unit.py`
