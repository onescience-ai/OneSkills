# description

该原语用于在 CFD benchmark 编排中读取规则网格 case，并根据任务选择静态监督或自回归预测协议。

# when_to_use

- 数据是二维规则网格 CFD case 目录。
- 需要复用 CFD_Benchmark 训练路线。
- 任务关注速度场和 case 级物理参数。
- 需要同时构造 train/val/test。

# inputs

- CFDBench 根目录和 `data_name`。
- `task_type`、`split_ratios`、随机种子。
- 是否归一化物性参数和边界条件。
- 自回归任务的 `delta_time`。

# outputs

- train/val/test dataloader。
- 静态或自回归 batch 字典。
- case 参数张量、速度场张量和 mask。

# procedure

1. 根据 `data_name` 判断 problem 与 subset 是否受支持。
2. 检查每个 case 是否含 `case.json/u.npy/v.npy`。
3. 根据任务选择静态或 `auto` 模式。
4. 设定 split 和随机种子以保证实验可复现。
5. 构造 datapipe，并在训练脚本中使用对应 collate 协议。

# constraints

- 只支持速度双通道加 mask。
- split 随运行配置生成，实验记录需保存 seed 和 ratios。
- problem 特定 mask 逻辑与 case.json 字段绑定。

# next_phase_recommendation

若需要压力、温度等更多变量，先扩展 `_load_raw_*` 和 collate；若任务转为 PDEBench HDF5 格式，使用 PDENNEval；若数据是非结构网格或几何点云，使用 AirfRANS、ShapeNetCar 或 DrivAerML。

# fallback

- `data_name` 不匹配时手动整理目录到受支持命名。
- `delta_time` 不整除时改用数据原生时间步间隔。
- 内存压力大时降低 batch size 或缩短时间序列。
