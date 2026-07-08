# description

该原语用于在任务编排中选择 AirfRANS 风格二维翼型流场数据读取、采样、归一化与图构建流程。决策重点是确认数据是否符合 manifest + 每样本 VTK 目录协议，以及模型是否需要点云/图形式的流场监督。

# when_to_use

- 用户数据是二维翼型外流场，目标为速度、压力、湍流黏度等点级预测。
- 需要把非结构网格转换为 `Data.x/Data.y/pos/surf/edge_index` 协议。
- 训练模型依赖几何点坐标、SDF、法向量和来流条件。
- 需要在全量网格与单元采样之间切换。

# inputs

- AirfRANS 根目录。
- `manifest.json` 中 train/test split 键名。
- 采样策略、采样点数、裁剪范围、图半径和最大邻居数。
- 是否已有训练统计量。

# outputs

- train/val/test dataloader。
- 每个样本的点级输入特征、监督目标、表面标记和可选图边。
- 训练集归一化统计量文件。

# procedure

1. 校验目录中是否存在 `manifest.json` 和样本 VTK 文件。
2. 校验样本名解析规则和 VTK 字段。
3. 先初始化训练集，生成或读取归一化统计量。
4. 根据任务规模选择 `sample_strategy` 与 `subsampling`。
5. 若模型需要图结构，开启 `build_graph` 并设置半径与邻居数。
6. 构造 datapipe 并接入训练、验证和测试流程。

# constraints

- val/test 依赖训练统计量。
- 数据 split 与样本命名不是自动推断的通用协议。
- 表面点识别与法向量对齐依赖 AirfRANS 的数据生成约定。

# next_phase_recommendation

若新数据集仍是翼型但字段或命名不同，优先写适配层统一 manifest、字段名和边界条件解析；若是三维几何流场，转向 ShapeNetCar 或 DrivAerML 路线；若是规则网格 benchmark，转向 CFDBench 或 PDEBench 路线。

# fallback

- 统计量缺失时先只运行训练集初始化生成统计量。
- VTK 字段不匹配时先做离线转换，保持 `U/p/nut/implicit_distance/Normals` 协议。
- 点数过大时启用采样和 subsampling。
- 构图失败时先关闭 `build_graph`，让模型或训练脚本自行处理邻接关系。
