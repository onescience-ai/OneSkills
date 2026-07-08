# Datapipe: ShapeNetCarDatapipe

## 基本信息

- Datapipe 名称：`ShapeNetCarDatapipe`
- 数据类型：`cfd`
- 主要任务：`3d car aerodynamics geometry-conditioned regression`
- 数据组织方式：`vtk_simulation_dirs_or_preprocessed_npy_cache`

## pipeline_responsibility

负责把汽车外流场 VTK 文件或预处理缓存转换为 PyG `Data` 图样本，覆盖 fold 划分、VTK 读取、表面/体点拼接、SDF、法向量、归一化和构图。

## 管道架构

```text
数据根目录
  param0 ... param8
    sample/
      quadpress_smpl.vtk
        -> 表面点 / 压力
      hexvelo_smpl.vtk
        -> 体点 / 速度

可选预处理缓存
  preprocessed_save_dir/param*/sample/
    x.npy / y.npy / pos.npy / surf.npy / edge_index.npy

样本构造
  VTK 读取或缓存读取
  -> 表面压力点 + 外部速度点
  -> SDF + normal
  -> x: [pos_x, pos_y, pos_z, sdf, normal_x, normal_y, normal_z]
  -> y: [v_x, v_y, v_z, p]
  -> surf
  -> cfd_mesh edge_index 或 radius_graph
  -> PyG Data
```

## 数据加载

- 从 `source.data_dir/param*/<sample>/` 发现样本。
- 读取 `quadpress_smpl.vtk` 和 `hexvelo_smpl.vtk`。
- 若 `source.preprocessed=True` 且缓存存在，优先读取 `x/y/pos/surf/edge_index.npy`。
- 从 `source.stats_dir` 读取或写入 `mean_in.npy`、`std_in.npy`、`mean_out.npy`、`std_out.npy`。

## 采样策略

- 当前 fold 逻辑依赖 `param0` 到 `param8` 九个参数分组。
- `data.splits.fold_id` 指定验证 fold，其余 fold 作为训练。
- 一个 dataset 样本对应一个汽车几何工况，不是时间窗。
- datapipe 默认构造 train/val loader；源码中 Dataset 支持 mode 但 Datapipe 未暴露 test loader。

## 数据转换

- 从 VTK 点和单元恢复表面压力、外部速度和网格边。
- 计算点到表面的 SDF 与方向。
- 计算或读取表面法向量。
- 将外部速度点和表面压力点拼成统一点集。
- 按训练统计量标准化输入和输出。
- 当 `model_hparams.cfd_mesh=True` 时复用 CFD 网格边；否则按半径图重新构边。

## 输入规格

- `<data_dir>/param*/<sample>/quadpress_smpl.vtk`。
- `<data_dir>/param*/<sample>/hexvelo_smpl.vtk`。
- 可选缓存：`<preprocessed_save_dir>/<param*>/<sample>/{x,y,pos,surf,edge_index}.npy`。
- 必需配置：`source.data_dir`、`source.preprocessed_save_dir`、`source.stats_dir`、`data.splits.fold_id`、`model_hparams.cfd_mesh/r/max_neighbors`。

## 输出规格

- 返回 `Data`。
- `Data.x`: `[NumPoints, 7]`，通常为 `[pos_x, pos_y, pos_z, sdf, normal_x, normal_y, normal_z]`。
- `Data.y`: `[NumPoints, 4]`，通常为 `[v_x, v_y, v_z, p]`。
- `Data.pos`: `[NumPoints, 3]`。
- `Data.surf`: 表面点标记。
- `Data.edge_index`: `[2, NumEdges]`。

## 约束条件

- 目录结构默认存在 `param0` 到 `param8`。
- VTK 文件名和字段语义需符合 `quadpress/hexvelo` 约定。
- `surf` 和压力通道被下游 Transolver-Car-Design 损失显式使用。
- 该原语默认 PyG Data 协议，不适合直接喂给 DGL 模型。
- 没有单独 `test_dataloader()`。

## 启动方式

Python API 启动示例：

```python
from omegaconf import OmegaConf
from onescience.datapipes.cfd import ShapeNetCarDatapipe

cfg = OmegaConf.load("conf/transolver_car.yaml")
datapipe = ShapeNetCarDatapipe(cfg.datapipe, distributed=False)
train_loader, train_sampler = datapipe.train_dataloader()
val_loader, val_sampler = datapipe.val_dataloader()
```

CLI 示例：

```sh
python train.py --config-name transolver_car datapipe.source.data_dir=/data/ShapeNetCar datapipe.source.preprocessed_save_dir=/data/ShapeNetCar/preprocessed datapipe.source.stats_dir=/data/ShapeNetCar/stats datapipe.source.preprocessed=true datapipe.data.splits.fold_id=0 datapipe.model_hparams.cfd_mesh=true datapipe.dataloader.batch_size=1
```

## 输入规格

- 原始数据按 `param*/sample/` 组织。
- 每个样本至少包含 `quadpress_smpl.vtk` 和 `hexvelo_smpl.vtk`。
- 若启用预处理缓存，缓存目录需包含 `x.npy/y.npy/pos.npy/surf.npy/edge_index.npy`。
- 统计目录需可写，训练阶段会生成归一化统计量。

## 运行接口

- `ShapeNetCarDataset(config, mode, coef_norm=None)`: 构造 train/val 样本。
- `ShapeNetCarDatapipe(params, distributed)`: 构造 train/val dataloader。
- `train_dataloader()`: 返回训练 PyGDataLoader 和 sampler。
- `val_dataloader()`: 返回验证 PyGDataLoader 和 sampler。

## 主要函数

- `__getitem__`
- `train_dataloader`
- `val_dataloader`

## 执行资源

- 首次从 VTK 预处理需要较多 CPU 和 I/O。
- SDF、法向量和边构造对点数敏感。
- PyG 图 batch 显存与节点数、边数相关。
- 使用预处理缓存可显著降低后续初始化成本。

## 操作限制

- Datapipe 类没有暴露 `test_dataloader`。
- fold 划分依赖固定 param 目录结构。
- 若只有表面点或只有体点，需要重新定义 `x/y/surf` 协议。
- 半径图构造参数不合理会导致边过密或图断裂。

## 规划决策

### 描述

该原语用于三维汽车外流场几何回归任务，将 VTK 仿真结果转为 PyG 点云图，并保留表面标记用于压力损失。

### 使用时机

- 数据是汽车或类似三维几何外流场 VTK。
- 目标为速度和表面压力等点级物理量回归。
- 模型需要 `Data(pos, x, y, surf, edge_index)`。
- 需要复用 Transolver-Car-Design 类训练流程。

### 输入

- ShapeNetCar 风格数据根目录。
- 预处理缓存目录和统计目录。
- fold_id。
- 是否使用 CFD 原始网格边，或半径图参数。

### 输出

- train/val PyG DataLoader。
- 点级图样本和训练统计量。
- 可复用的预处理 npy 缓存。

### 执行步骤

1. 校验 `param*` 目录和 VTK 文件。
2. 确定 fold_id 与训练/验证划分。
3. 若首次运行，允许生成预处理缓存和统计量。
4. 根据模型选择 `cfd_mesh` 或 radius graph。
5. 检查 `surf` 与压力通道是否满足损失函数假设。

### 约束

- VTK 字段语义和文件名是强约束。
- fold 规则不是通用随机划分。
- 输出协议绑定 PyG，不是 DGL。
- test 需要自行构造 Dataset 或扩展 Datapipe。

### 下一阶段建议

若新车体数据目录结构不同，先写样本发现和 split 适配；若数据是 DrivAerML 分片图，使用 DrivAerML FigConvUNet；若是二维翼型，使用 AirfRANS。

### 回退策略

- VTK 读取慢时启用并复用预处理缓存。
- 缺少原始 CFD 边时关闭 `cfd_mesh`，使用半径图。
- 统计量缺失时先初始化训练集生成统计文件。

## 源码锚点

- `{onescience_path}/onescience/src/onescience/datapipes/cfd/ShapeNetCar.py`
- `{onescience_path}/onescience/examples/cfd/Transolver-Car-Design/train.py`
- `{onescience_path}/onescience/examples/cfd/Transolver-Car-Design/conf/transolver_car.yaml`
