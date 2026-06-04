# Contract: mace_loss.py

## 基本信息

- 组件名：`MACE Loss Family`
- 所属模块族：`materials / mace / loss`
- 统一入口：`direct_import`
- 注册名：`not_applicable`
- 主源码：`./onescience/src/onescience/modules/loss/mace_loss.py`

## 组件职责

定义 MACE 训练中的能量、力、应力、virial、dipole 多种损失函数，并处理 DDP 场景下的 loss 归约修正。

覆盖组合：

- `WeightedEnergyForcesLoss`
- `WeightedForcesLoss`
- `WeightedEnergyForcesStressLoss`
- `WeightedHuberEnergyForcesStressLoss`
- `UniversalLoss`
- `WeightedEnergyForcesVirialsLoss`
- `DipoleSingleLoss`
- `WeightedEnergyForcesDipoleLoss`
- `WeightedEnergyForcesL1L2Loss`

## 输入契约

- reference：MACE `Batch`，通常包含 `energy`、`forces`、`stress`、`virials`、`dipole`、`ptr`、权重字段
- prediction：模型输出 dict，字段名通常为 `energy`、`forces`、`stress`、`virials`
- DDP：需要通过 `reduce_loss` 保持多卡 loss 尺度一致

`energy_key/forces_key/stress_key` 是数据读取阶段的字段映射；进入 loss 后通常已经规范化为 batch 字段。

## 输出契约

- 输出单标量 loss
- 不同 loss 类按子项权重加权求和
- per-atom energy loss 依赖 `ptr` 或 `batch` 计算每图原子数

## 关键参数

- `energy_weight`
- `forces_weight`
- `stress_weight`
- `virials_weight`
- `dipole_weight`
- `huber_delta`
- `loss`
- `compute_stress`
- `compute_virials`

典型 MACE fine-tuning：

- `energy_weight=1~20`
- `forces_weight=10~1000`
- `stress_weight=0~20`

## 典型调用位置

- `examples/matchem/mace/train.py`
- `onescience.utils.mace.tools.train`
- `get_loss_fn(...)`
- 多头 fine-tuning 与 foundation fine-tuning

## 常见修改点

- 新增 property：增加对应 prediction/reference 字段和 loss 组合。
- 调整 E/F/S 权重：根据任务目标决定，不要只追求训练 loss。
- stress/virial 任务：同步确认数据单位、符号和 tensor shape。
- DDP loss：不要用普通 `.mean()` 替换已有归约。

## 风险点

- `ptr` 或 `batch` 错误会污染 per-atom 标准化。
- `stress` 和 `virials` 的符号约定经常不同，不能只靠字段名判断。
- 力权重过大可能牺牲能量绝对值；下游性质要单独验证。
- 训练 loss 下降不代表 MD、GSFE、弹性、缺陷能稳定。

## 下钻关系

- 数据字段：`../datapipes/materials_mace.md`
- 模型输出：`./mace_func_utils.md`
- fine-tuning 配置：`./mace_finetuning_utils.md`

## 源码锚点

- `./onescience/src/onescience/modules/loss/mace_loss.py`
- `./onescience/examples/matchem/mace/train.py`
