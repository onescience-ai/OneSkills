# component_info
`mace_loss` 是 MACE loss 族组件，定位为材料势函数训练中的监督目标集合。它通过直接导入或训练工具间接调用，把模型输出的 energy、forces、stress、virials、dipole 与 batch 标签进行加权比较，并处理分布式训练下的 loss 归约。

# purpose
- 用途：定义 MACE 能量、力、应力、virial、dipole 及组合损失。
- 解决问题：让不同物理量以可控权重共同训练，并在 DDP 下保持 loss 尺度一致。
- 适用场景：MACE 从头训练、foundation fine-tuning、多物理量监督、偶极任务。
- 不适用场景：数据读取字段映射、模型 forward、物理导数计算。

# input_schema
- `reference`: MACE `Batch`，通常包含 `energy`、`forces`、`stress`、`virials`、`dipole`、`ptr`、`batch`、权重字段。
- `prediction`: 模型输出 dict，通常包含 `energy`、`forces`、`stress`、`virials`、`dipole`。
- `ptr` 或 `batch`: 用于每图原子数和 per-atom energy 归一化。
- `weight` 字段：按构型或原子对不同样本加权。
- DDP 上下文：`reduce_loss` 根据分布式状态修正标量。

# output_schema
- 输出单标量 loss。
- 组合 loss 由 energy、forces、stress、virials、dipole 等子项加权求和。
- per-atom energy loss 依赖每图原子数归一化。
- Huber/conditional loss 按指定阈值或 mask 对 force 子项处理。

# parameters
- `energy_weight`: 能量损失权重。
- `forces_weight`: 力损失权重。
- `stress_weight`: 应力损失权重。
- `virials_weight`: virial 损失权重。
- `dipole_weight`: 偶极损失权重。
- `huber_delta`: Huber 损失阈值。
- `loss`: loss 类型或条件分支。
- `compute_stress`: 是否训练 stress。
- `compute_virials`: 是否训练 virial。
- 典型 fine-tuning：`energy_weight=1~20`，`forces_weight=10~1000`，`stress_weight=0~20`。

# key_dependencies
- `mace_func_utils.py`
- `mace_block.py`
- `torch_geometric.py`
- `torch_tools.py`
- `train.py`

# usage_and_risks
- 典型使用：训练脚本根据配置选择 `WeightedEnergyForcesLoss`、`UniversalLoss` 或含 stress/virial/dipole 的组合类。
- 新增 property 时，需要同步增加 prediction/reference 字段和 loss 组合。
- `ptr` 或 `batch` 错误会污染 per-atom energy 标准化。
- stress 与 virial 的符号和单位经常不同，不能只靠字段名判断。
- 力权重过大可能牺牲能量绝对值和下游热力学稳定性。
- 不应把 DDP 下的 `reduce_loss` 简化为普通 `.mean()`。

# code_references
- `{onescience_path}/onescience/src/onescience/modules/loss/mace_loss.py`
- `{onescience_path}/onescience/examples/matchem/mace/train.py`
