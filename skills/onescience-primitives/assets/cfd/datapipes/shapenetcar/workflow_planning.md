# description

该原语用于三维汽车外流场几何回归任务，将 VTK 仿真结果转为 PyG 点云图，并保留表面标记用于压力损失。

# when_to_use

- 数据是汽车或类似三维几何外流场 VTK。
- 目标为速度和表面压力等点级物理量回归。
- 模型需要 `Data(pos, x, y, surf, edge_index)`。
- 需要复用 Transolver-Car-Design 类训练流程。

# inputs

- ShapeNetCar 风格数据根目录。
- 预处理缓存目录和统计目录。
- fold_id。
- 是否使用 CFD 原始网格边，或半径图参数。

# outputs

- train/val PyG DataLoader。
- 点级图样本和训练统计量。
- 可复用的预处理 npy 缓存。

# procedure

1. 校验 `param*` 目录和 VTK 文件。
2. 确定 fold_id 与训练/验证划分。
3. 若首次运行，允许生成预处理缓存和统计量。
4. 根据模型选择 `cfd_mesh` 或 radius graph。
5. 检查 `surf` 与压力通道是否满足损失函数假设。

# constraints

- VTK 字段语义和文件名是强约束。
- fold 规则不是通用随机划分。
- 输出协议绑定 PyG，不是 DGL。
- test 需要自行构造 Dataset 或扩展 Datapipe。

# next_phase_recommendation

若新车体数据目录结构不同，先写样本发现和 split 适配；若数据是 DrivAerML 分片图，使用 DrivAerML FigConvUNet；若是二维翼型，使用 AirfRANS。

# fallback

- VTK 读取慢时启用并复用预处理缓存。
- 缺少原始 CFD 边时关闭 `cfd_mesh`，使用半径图。
- 统计量缺失时先初始化训练集生成统计文件。
