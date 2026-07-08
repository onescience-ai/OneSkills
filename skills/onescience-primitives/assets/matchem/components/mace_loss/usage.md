# launch
Python API 示例：

``` python
from onescience.modules.loss.mace_loss import WeightedEnergyForcesLoss

loss_fn = WeightedEnergyForcesLoss(
    energy_weight=10.0,
    forces_weight=1000.0,
)
loss = loss_fn(reference=batch, prediction=outputs)
```

完整训练命令示例：

``` sh
python examples/matchem/mace/train.py --model=MACE --loss=weighted --energy_weight=10 --forces_weight=1000 --stress_weight=0 --num_interactions=2 --num_channels=64 --max_L=0 --correlation=3 --r_max=6.0 --train_file="${ONESCIENCE_DATASETS_DIR}/matchem/mace/water/water_train.xyz" --valid_fraction=0.05 --test_file="${ONESCIENCE_DATASETS_DIR}/matchem/mace/water/water_test.xyz" --energy_key=TolEnergy --forces_key=force --E0s=isolated --batch_size=2 --valid_batch_size=4 --max_num_epochs=10 --device=cuda
```

# input_schema
训练 batch：

reference
  energy: (NumGraphs,) 或 (NumGraphs, NumHeads)
    体系参考能量
  forces: (NumAtoms, 3)
    参考力
  stress: (NumGraphs, 3, 3) 或等价扁平形态
    可选
  virials: (NumGraphs, 3, 3)
    可选
  dipole: (NumGraphs, 3)
    偶极任务可选
  ptr / batch
    每图原子数与归一化
  weights
    样本或任务权重

prediction
  energy / forces / stress / virials / dipole
    模型输出字段需与 loss 类匹配

# runtime_interfaces
- `reduce_loss(raw_loss, ddp=None)`：DDP 下同步 loss 尺度。
- `mean_squared_error_energy(...)`：基础能量 MSE。
- `weighted_mean_squared_error_energy(...)`：带权能量 MSE。
- `weighted_mean_absolute_error_energy(...)`：带权能量 MAE。
- `mean_squared_error_forces(...)`：力 MSE。
- `conditional_mse_forces(...)`：条件力 MSE。
- `conditional_huber_forces(...)`：条件力 Huber。
- `weighted_mean_squared_stress(...)`：应力 MSE。
- `weighted_mean_squared_virials(...)`：virial MSE。
- `WeightedEnergyForcesLoss.forward(reference, prediction)`：能量-力组合。
- `UniversalLoss.forward(reference, prediction)`：通用组合损失。

# main_functions
- `reduce_loss`
- `mean_squared_error_energy`
- `weighted_mean_squared_error_energy`
- `weighted_mean_absolute_error_energy`
- `weighted_mean_squared_stress`
- `weighted_mean_squared_virials`
- `mean_squared_error_forces`
- `mean_normed_error_forces`
- `weighted_mean_squared_error_dipole`
- `conditional_mse_forces`
- `conditional_huber_forces`
- `forward`

# execution_resources
- loss 本身计算成本通常低于模型 forward。
- 含 forces/stress/virial 的损失要求模型输出已完成对应自动微分，主要资源消耗发生在 forward。
- DDP 训练需要分布式上下文正确初始化。
- 大 batch 下 force loss 张量规模随原子数增长。

# operation_limits
- 字段名必须与模型输出和 batch 标签一致。
- stress/virial 的 shape、符号和单位必须提前校准。
- per-atom energy 标准化依赖 `ptr` 或 `batch` 正确。
- loss 下降不等价于 MD、结构弛豫或材料性质稳定。
- 对多头任务需确认 head 对齐后再聚合 loss。
