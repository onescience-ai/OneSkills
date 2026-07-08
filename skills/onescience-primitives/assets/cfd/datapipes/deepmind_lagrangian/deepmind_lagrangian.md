# Datapipe: DeepmindLagrangianDatapipe

## 基本信息

- Datapipe 名称：`DeepmindLagrangianDatapipe`
- 数据类型：`cfd`
- 主要任务：`lagrangian particle dynamics rollout prediction`
- 数据组织方式：`split_tfrecord_particle_trajectories_with_metadata_json`

## pipeline_responsibility

负责把 DeepMind 粒子轨迹数据转换为动态半径图样本，处理 TFRecord bytes 解析、历史速度窗口、边界距离特征、粒子类型编码、随机游走噪声、归一化目标和时间积分辅助。

## 管道架构

```text
数据目录
  metadata.json
    -> sequence_length / dt / bounds / dim
    -> vel_mean/std, acc_mean/std
    -> default_connectivity_radius
  <split>.tfrecord
    -> particle_type
    -> position sequence

样本窗口
  positions[t-history : t+1]
    -> position_t
    -> velocity_history
    -> boundary_features
    -> node_type_onehot
    -> radius graph
    -> edge features
    -> next_position / next_velocity / next_acceleration
```

## 数据加载

- 从 `datapipe.source.data_dir/metadata.json` 读取统计量和物理元数据。
- 根据 `cfg.data.<split>.split` 读取对应 `<split>.tfrecord`。
- 使用 TensorFlow 解析序列化 bytes 字段，得到粒子类型和位置序列。
- 每个 split 可限制 `num_sequences` 和 `num_steps`。

## 采样策略

- 一个 item 对应一条轨迹上的一个历史窗口。
- `num_history` 决定输入历史速度帧数量。
- train/valid/test split 名称由配置指定，valid 使用 `mode="valid"`。
- 图边在每个样本中按当前位置和半径动态重建。

## 数据转换

- 根据连续位置计算速度和加速度。
- 训练阶段对动态粒子注入随机游走噪声，运动学粒子通过 mask 排除。
- 计算边界距离/裁剪特征。
- 粒子类型转 one-hot。
- 使用 `torch.cdist` 半径邻接构图，并写入边相对位移与距离特征。
- 提供反归一化和时间积分辅助。

## 输入规格

- `<data_dir>/metadata.json`。
- `<data_dir>/<split>.tfrecord`。
- 必需配置：`data.num_history`、`data.noise_std`、`data.num_node_types`。
- 每个 split 需配置 `split`、`num_sequences`、可选 `num_steps`。

## 输出规格

- 返回 `DGLGraph`。
- `ndata["x"]`: `[position_t, velocity_history, boundary_features, node_type_onehot]` 拼接特征。
- `ndata["y"]`: `[next_position, next_velocity, next_acceleration]`。
- `ndata["pos"]`: 当前粒子位置。
- `ndata["mask"]`: 动态粒子或训练目标 mask。
- `ndata["t"]`: 时间索引。
- `edata["x"]`: 半径图边特征。

## 约束条件

- 依赖 TensorFlow compat v1 和 DGL。
- 半径图基于全对全距离，粒子数很大时成本高。
- metadata 中统计量和物理元数据必须完整。
- split 配置分布在 `cfg.data.*` 和 `cfg.datapipe.*`，生成配置时需保持一致。

## 启动方式

Python API 启动示例：

```python
from omegaconf import OmegaConf
from onescience.datapipes.cfd import DeepMindLagrangianDatapipe

cfg = OmegaConf.load("conf/lagrangian.yaml")
datapipe = DeepMindLagrangianDatapipe(cfg, distributed=False)
train_loader = datapipe.train_dataloader()
val_loader = datapipe.val_dataloader()
test_loader = datapipe.test_dataloader()
```

CLI 示例：

```sh
python train.py --config-name lagrangian datapipe.source.data_dir=/data/lagrangian data.num_history=5 data.noise_std=0.0003 data.train.split=train data.valid.split=valid data.test.split=test datapipe.dataloader.train.batch_size=2
```

## 输入规格

- 数据根目录包含 `metadata.json` 和 split 对应 TFRecord。
- `metadata.json` 需要包含速度/加速度均值方差、时间步长、边界、维度和默认连接半径。
- `particle_type` 和 `position` 必须符合源码解析逻辑。

## 运行接口

- `DeepMindLagrangianDataset(config, mode)`: 构造一个 split 的动态图样本。
- `DeepMindLagrangianDatapipe(cfg, distributed=False)`: 构造 train/valid/test loader。
- `train_dataloader()`: 返回训练 GraphDataLoader。
- `val_dataloader()`: 返回验证 GraphDataLoader。
- `test_dataloader()`: 返回测试 GraphDataLoader。

## 主要函数

- `__getitem__`
- `denormalize_velocity`
- `denormalize_acceleration`
- `unpack_targets`
- `unpack_inputs`
- `time_integrator`
- `train_dataloader`
- `val_dataloader`
- `test_dataloader`

## 执行资源

- 需要 TensorFlow 读取 TFRecord。
- 需要 DGL 存储和 batch 图。
- 半径图构建使用全对全距离，粒子数大时 CPU/GPU 与内存压力明显。
- 分布式通过 `GraphDataLoader(..., use_ddp=...)` 控制。

## 操作限制

- 不支持欧拉规则网格输入。
- 粒子数过大时动态构图可能成为瓶颈。
- `valid` 文件名和配置名需要一致。
- rollout 中若位置更新后邻接改变，应复用 `graph_update` 更新边。

## 规划决策

### 描述

该原语用于拉格朗日粒子仿真任务编排，将粒子历史窗口转换为可 rollout 的动态图样本。

### 使用时机

- 数据是粒子轨迹而不是固定网格场。
- 模型需要预测下一步位置、速度或加速度。
- 任务要求动态重建邻接关系。
- 训练中需要噪声增强提高 rollout 稳定性。

### 输入

- `metadata.json` 与 split TFRecord。
- 历史步数、连接半径、粒子类型数量。
- split 名称、序列数和时间步数。
- 噪声标准差和 dataloader 参数。

### 输出

- train/valid/test GraphDataLoader。
- 每个样本的 DGLGraph。
- 反归一化、输入/目标解包和时间积分辅助接口。

### 执行步骤

1. 校验 metadata 统计量、边界和半径配置。
2. 确认 TFRecord 的 split 名称与配置一致。
3. 设置 `num_history` 以匹配模型输入维度。
4. 根据粒子数评估半径图构建成本。
5. 构造 datapipe 并在 rollout 阶段使用 `graph_update`。

### 约束

- 粒子类型编码数量必须覆盖数据中全部类型。
- 动态粒子 mask 决定哪些节点参与训练目标。
- 半径过大将显著增加边数，半径过小可能断开物理邻域。

### 下一阶段建议

若数据是网格圆柱流 TFRecord，优先 DeepMind CylinderFlow；若需要规则网格 operator learning，优先 PDENNEval；若要处理 VTK 几何外流场，使用 AirfRANS 或 ShapeNetCar。

### 回退策略

- 粒子数太大时减小半径、下采样粒子或预计算邻接。
- TFRecord 解析失败时先转换为中间 npy/h5 格式验证字段。
- rollout 发散时降低噪声或检查统计量与时间步长。

## 源码锚点

- `{onescience_path}/onescience/src/onescience/datapipes/cfd/deepmind_lagrangian.py`
- `{onescience_path}/onescience/examples/cfd/Vortex_shedding_mgn/`
- `{onescience_path}/onescience/src/onescience/datapipes/core/base_dataset.py`
