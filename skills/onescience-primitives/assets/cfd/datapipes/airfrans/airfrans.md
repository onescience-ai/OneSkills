# Datapipe: AirfRANSDatapipe

## 基本信息

- Datapipe 名称：`AirfRANSDatapipe`
- 数据类型：`cfd`
- 主要任务：`2d airfoil flow-field regression`
- 数据组织方式：`per_simulation_dir_with_vtu_vtp_and_manifest`

## pipeline_responsibility

负责把 AirfRANS 翼型工况目录中的 `manifest.json`、内部流场网格和翼型表面文件组织成点级图样本，覆盖样本划分、VTK 解析、可选裁剪、单元采样、归一化、下采样和构图。

## 管道架构

```text
数据根目录
  manifest.json
    -> train_name 全集
      -> train / val 按 val_split_ratio 切分
    -> test_name

单个仿真目录
  <sim>_internal.vtu
    -> pos / U / p / nut / implicit_distance
  <sim>_aerofoil.vtp
    -> 表面 U / p / nut / Normals

样本构造
  全量网格或 uniform/mesh 单元采样
    -> x: [pos_x, pos_y, u_inf_x, u_inf_y, sdf, normal_x, normal_y]
    -> y: [v_x, v_y, p, nut]
    -> surf
    -> 训练统计量归一化
    -> train/val 点级 subsampling
    -> 可选 radius_graph edge_index
    -> PyG Data
```

## 数据加载

- 从 `source.data_dir/manifest.json` 读取训练全集、测试集名称列表。
- 对每个样本读取 `<sim>/<sim>_internal.vtu` 和 `<sim>/<sim>_aerofoil.vtp`。
- 从样本名中解析来流速度和攻角，用于构造入口条件特征。
- 从 `source.stats_dir` 读取或写入 `mean_in.npy`、`std_in.npy`、`mean_out.npy`、`std_out.npy`。

## 采样策略

- train/val 由 `manifest[train_name]` 按 `val_split_ratio` 切分，test 由 `manifest[test_name]` 给出。
- `sample_strategy=null` 时使用内部网格全量点。
- `sample_strategy="uniform"` 时按单元面积和表面线段长度加权采样。
- `sample_strategy="mesh"` 时按单元数量近似均匀采样。
- train/val 若点数超过 `data.subsampling`，再随机保留固定数量点；test 不做该下采样。

## 数据转换

- 可选 `data.crop=(xmin, xmax, ymin, ymax)` 对内部网格裁剪。
- 全量模式下用 `U_x == 0` 推断表面点，并将 aerofoil 法向量对齐到内部表面点。
- 采样模式下在体单元和表面线单元内插值得到点坐标与场值。
- 输入和输出按训练集统计量标准化。
- 当 `model_hparams.build_graph=True` 时，按坐标用半径和最大邻居数生成 `edge_index`。

## 输入规格

- 数据目录：`<data_dir>/manifest.json`。
- 样本文件：`<data_dir>/<sim_name>/<sim_name>_internal.vtu`、`<data_dir>/<sim_name>/<sim_name>_aerofoil.vtp`。
- 必需字段：
  - internal: `U`、`p`、`nut`、`implicit_distance`
  - aerofoil: `U`、`p`、`nut`、`Normals`
- 关键配置：`source.data_dir`、`source.stats_dir`、`data.splits.*`、`data.sampling.*`、`model_hparams.*`。

## 输出规格

- 返回 `Data`。
- `Data.x`: `[NumPoints, 7]`, float, `[pos_x, pos_y, u_inf_x, u_inf_y, sdf, normal_x, normal_y]`。
- `Data.y`: `[NumPoints, 4]`, float, `[v_x, v_y, p, nut]`。
- `Data.pos`: `[NumPoints, 2]`。
- `Data.surf`: `[NumPoints]` 或 `[NumPoints, 1]` 的表面布尔标记。
- `Data.edge_index`: `[2, NumEdges]`，未构图时为空或 `None`。

## 约束条件

- `manifest.json` 必须包含配置引用的 split 键。
- 样本名需满足代码中的下划线分段解析规则，否则来流条件构造会失败。
- 归一化统计量只能由训练集生成；val/test 初始化时若统计量不存在会报错。
- VTK 字段名和表面点对齐假设是硬约束。
- 该原语面向二维翼型非结构网格，不适合直接处理三维车体或规则栅格数据。

## 启动方式

Python API 启动示例：

```python
from omegaconf import OmegaConf
from onescience.datapipes.cfd import AirfRANSDatapipe

cfg = OmegaConf.load("conf/airfrans.yaml")
datapipe = AirfRANSDatapipe(cfg.datapipe, distributed=False)
train_loader, train_sampler = datapipe.train_dataloader()
val_loader, val_sampler = datapipe.val_dataloader()
test_loader = datapipe.test_dataloader()
```

CLI 示例：

```sh
python train.py --config-name airfrans datapipe.source.data_dir=/data/AirfRANS datapipe.source.stats_dir=/data/AirfRANS/stats datapipe.data.splits.train_name=full_train datapipe.data.splits.test_name=full_test datapipe.dataloader.batch_size=4
```

## 输入规格

- 准备包含 `manifest.json` 的 AirfRANS 根目录。
- 每个 manifest 样本名必须对应同名子目录，子目录内包含 internal vtu 和 aerofoil vtp。
- 配置 `source.stats_dir` 为可写目录，训练阶段首次运行会生成归一化统计量。
- 确认样本名能解析出 `Uinf` 和攻角。

## 运行接口

- `AirfRANSDataset(config, mode, coef_norm=None)`: 构造指定 split 的样本集。
- `AirfRANSDatapipe(params, distributed)`: 构造 train/val/test 数据管道。
- `train_dataloader()`: 返回训练 loader 和可选 sampler。
- `val_dataloader()`: 返回验证 loader 和可选 sampler。
- `test_dataloader()`: 返回测试 loader。

## 主要函数

- `__getitem__`
- `train_dataloader`
- `val_dataloader`
- `test_dataloader`

## 执行资源

- 需要 CPU 读取 VTK、执行几何采样和归一化统计。
- 构图使用点间半径邻域，点数较大时内存和 CPU/GPU 邻接构造开销会上升。
- 依赖 VTK 读取能力、数值数组处理能力和图样本 batch 能力。
- 分布式训练可通过 datapipe 的 `distributed=True` 启用 sampler。

## 操作限制

- 不支持没有 `manifest.json` 的散文件数据。
- 不支持字段名偏离 AirfRANS 约定的 VTK 文件。
- 测试阶段不做点级 subsampling，超大网格可能造成显存或内存压力。
- 训练/验证/测试的统计量必须一致，不能分别独立归一化。

## 规划决策

### 描述

该原语用于在任务编排中选择 AirfRANS 风格二维翼型流场数据读取、采样、归一化与图构建流程。决策重点是确认数据是否符合 manifest + 每样本 VTK 目录协议，以及模型是否需要点云/图形式的流场监督。

### 使用时机

- 用户数据是二维翼型外流场，目标为速度、压力、湍流黏度等点级预测。
- 需要把非结构网格转换为 `Data.x/Data.y/pos/surf/edge_index` 协议。
- 训练模型依赖几何点坐标、SDF、法向量和来流条件。
- 需要在全量网格与单元采样之间切换。

### 输入

- AirfRANS 根目录。
- `manifest.json` 中 train/test split 键名。
- 采样策略、采样点数、裁剪范围、图半径和最大邻居数。
- 是否已有训练统计量。

### 输出

- train/val/test dataloader。
- 每个样本的点级输入特征、监督目标、表面标记和可选图边。
- 训练集归一化统计量文件。

### 执行步骤

1. 校验目录中是否存在 `manifest.json` 和样本 VTK 文件。
2. 校验样本名解析规则和 VTK 字段。
3. 先初始化训练集，生成或读取归一化统计量。
4. 根据任务规模选择 `sample_strategy` 与 `subsampling`。
5. 若模型需要图结构，开启 `build_graph` 并设置半径与邻居数。
6. 构造 datapipe 并接入训练、验证和测试流程。

### 约束

- val/test 依赖训练统计量。
- 数据 split 与样本命名不是自动推断的通用协议。
- 表面点识别与法向量对齐依赖 AirfRANS 的数据生成约定。

### 下一阶段建议

若新数据集仍是翼型但字段或命名不同，优先写适配层统一 manifest、字段名和边界条件解析；若是三维几何流场，转向 ShapeNetCar 或 DrivAerML 路线；若是规则网格 benchmark，转向 CFDBench 或 PDEBench 路线。

### 回退策略

- 统计量缺失时先只运行训练集初始化生成统计量。
- VTK 字段不匹配时先做离线转换，保持 `U/p/nut/implicit_distance/Normals` 协议。
- 点数过大时启用采样和 subsampling。
- 构图失败时先关闭 `build_graph`，让模型或训练脚本自行处理邻接关系。

## 源码锚点

- `{onescience_path}/onescience/src/onescience/datapipes/cfd/AirfRANS.py`
- `{onescience_path}/onescience/src/onescience/datapipes/core/base_dataset.py`
- `{onescience_path}/onescience/src/onescience/utils/transolver/reorganize.py`
