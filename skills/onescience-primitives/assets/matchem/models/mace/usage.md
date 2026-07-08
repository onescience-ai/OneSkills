# launch
推荐通过 OneScience MACE demo YAML 启动训练，先 dry-run 检查最终命令与数据路径，再正式运行：

``` sh
cd examples/matchem/mace/demo
bash run.sh --config configs/water_1dcu.yaml --dry-run
bash run.sh --config configs/water_1dcu.yaml
```

直接使用训练入口时，可按单卡 water 配置展开为完整参数：

``` sh
python examples/matchem/mace/train.py --model=MACE --default_dtype=float64 --num_interactions=2 --num_channels=64 --max_L=0 --correlation=3 --train_file="${ONESCIENCE_DATASETS_DIR}/matchem/mace/water/water_train.xyz" --test_file="${ONESCIENCE_DATASETS_DIR}/matchem/mace/water/water_test.xyz" --valid_fraction=0.05 --E0s=isolated --energy_key=TolEnergy --forces_key=force --seed=123 --device=cuda --r_max=6.0 --batch_size=2 --valid_batch_size=4 --max_num_epochs=10 --forces_weight=1000 --energy_weight=10 --scheduler_patience=15 --patience=30 --eval_interval=1 --error_table=PerAtomMAE --ema --swa --restart_latest --save_cpu
```

foundation model 微调时，典型配置使用 `foundation_model=medium`、`foundation_model_elements=true`、较小学习率、EMA/SWA，并通过多卡 launcher 执行。

# input_schema
训练数据准备：

- `train_file`：`.xyz` 或 `.extxyz` 训练集路径，必填。
- `valid_file` 或 `valid_fraction`：验证集文件或从训练集切分比例；demo 默认示例 `valid_fraction=0.05`。
- `test_file`：测试集路径，可选但推荐提供。
- `energy_key`：能量字段，示例默认 `TolEnergy`。
- `forces_key`：力字段，示例默认 `force`。
- `stress_key` / `virials_key`：应力或 virial 字段，可选。
- `E0s`：原子参考能方式，常用 `average`、`isolated`、`foundation` 或显式字典；water 示例使用 `isolated`。
- `foundation_model`：可选，传入 `small`、`medium`、`large`、`medium-mpa-0`、`medium-omat-0` 或本地模型后进入 fine-tuning。

模型 forward 数据：

- `positions`: `(NumAtoms, 3)`。
- `node_attrs`: `(NumAtoms, NumElements)`。
- `edge_index`: `(2, NumEdges)`。
- `batch`: `(NumAtoms,)`。
- `cell`: `(NumGraphs, 3, 3)`。
- `shifts` / `unit_shifts`: `(NumEdges, 3)`。
- `head`: 多头任务 id，未显式多头时使用默认 head。

常用训练默认参数：

- `model=MACE`。
- `default_dtype=float64`。
- `num_interactions=2`。
- `num_channels=64` 或 `128`。
- `max_L=0` 或 `2`。
- `correlation=3`。
- `r_max=4.0` 到 `6.0`，water 示例为 `6.0`。
- `batch_size=2`，`valid_batch_size=4`。
- `energy_weight=10`，`forces_weight=1000` 在 water 示例中用于偏重力监督。
- `ema=true`，`swa=true`。

forward 默认参数：

- `training=False`。
- `compute_force=True`。
- `compute_virials=False`。
- `compute_stress=False`。
- `compute_displacement=False`。
- `compute_hessian=False`。
- `compute_edge_forces=False`。
- `compute_atomic_stresses=False`。
- `lammps_mliap=False`。

# runtime_interfaces
- 构造接口：`MACE(...)`，创建能量-力势函数模型。
- 构造接口：`ScaleShiftMACE(atomic_inter_scale, atomic_inter_shift, **kwargs)`，创建带 interaction energy scale/shift 的模型。
- 推理接口：`model.forward(data, training=False, compute_force=True, ...)`。
- 输出求导接口：通过 forward 内部的 `get_outputs` 从能量生成力、应力、virial、Hessian 与边力。
- 训练入口：demo YAML 将 `train_args` 转换成训练脚本参数，`launch` 决定单进程或多进程启动方式。
- 下游接口：训练得到的模型可用于 ASE calculator、LAMMPS 部署、MD、结构弛豫与评估脚本。

# main_functions
- `forward`

# execution_resources
- CPU 可用于数据检查、小 batch smoke test 或加载模型结构。
- 实际训练和含力/应力的推理建议使用 GPU/DCU；资源消耗随原子数、边数、`num_channels`、`max_L`、`num_interactions` 和 batch size 增长。
- 计算 `forces` 需要坐标梯度；计算 `stress` / `virials` 需要晶胞 displacement；计算 `hessian` 或逐原子 stress 会显著增加显存与时间。
- 建议环境具备材料数据处理、自动微分、等变张量运算和 ASE/LAMMPS 相关依赖。
- 多卡训练优先使用 demo YAML 与 `run.sh --dry-run` 检查最终 launcher、环境变量和数据文件。

# operation_limits
- 输入必须是邻居图形式；模型本身不负责从裸 xyz 文本直接构造 `edge_index`。
- extxyz 字段名必须与配置中的 `energy_key`、`forces_key`、`stress_key`、`virials_key` 对齐。
- `r_max` 决定邻域图和 checkpoint 结构兼容性，foundation model 微调时不应随意更改。
- `E0s`、能量单位、力单位、stress/virial 符号必须与训练数据一致。
- 对未见元素、元素表截断或 foundation 元素不一致的情况，模型泛化和权重加载都可能失败。
- 大体系 MD 不应只看验证误差，还要做能量漂移、力异常值和短程碰撞稳定性检查。
- 偶极预测不是普通 `MACE` 的默认输出，需要使用偶极扩展类并提供 `charges` 等额外字段。
