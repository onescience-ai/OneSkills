# Datapipe: PDENNEvalDatapipe

## 基本信息

- Datapipe 名称：`PDENNEvalDatapipe`
- 数据类型：`cfd`
- 主要任务：`PDEBench neural-operator dataset evaluation`
- 数据组织方式：`pdebench_hdf5_or_h5_files`

## pipeline_responsibility

负责将 PDEBench 风格 HDF5/H5 数据读取为不同神经算子模型族所需的样本协议，覆盖 FNO、DeepONet、MPNN、UNet、UNO 和 PINO。

## 管道架构

```text
HDF5 数据
  single_file=true
    -> tensor / density / pressure / Vx/Vy/Vz / coordinates
    -> 一次性加载并降采样
  single_file=false
    -> seed groups
      -> data
      -> grid/x,y,z,t
      -> optional global_maximums

共同处理
  reduced_batch
  reduced_resolution
  reduced_resolution_t
  initial_step
  test_ratio 划分 train / val

模型族输出
  FNO / DeepONet / UNO / PINO
    -> (history, target, grid)
  UNet
    -> (history, target)
  MPNN
    -> flattened datapoints + coordinates + variables
    -> GraphCreator 在训练阶段构图
  PINO
    -> train + pde residual + val dataloader
```

## 数据加载

- 从 `datapipe.source.data_dir/datapipe.source.file_name` 打开 HDF5/H5 文件。
- 单文件模式一次性读取主要 tensor 和坐标网格。
- 多文件模式按 seed/group 懒加载，常见结构包括 `<seed>/data` 与 `<seed>/grid/*`。
- 支持从 `tensor` 或 `density/pressure/Vx/Vy/Vz` 等键构造数据。

## 采样策略

- `reduced_batch` 对样本维降采样。
- `reduced_resolution` 对空间维降采样。
- `reduced_resolution_t` 对时间维降采样。
- `test_ratio` 划分 train/val。
- `initial_step` 决定 history 输入时间步数。
- PINO 的 PDE residual 路径可使用独立降采样参数。

## 数据转换

- 构造或读取坐标网格 `grid`。
- 将目标完整轨迹保留为监督 `target`。
- 按模型族差异返回 history、grid 或 flatten 后的 datapoints。
- MPNN 额外构造 `PDE` 与 `GraphCreator`，真正图构造通常在训练循环中完成。
- PINO 暴露 `dx`、`dt`，并额外提供 PDE loss 数据流。

## 输入规格

- `datapipe.source.data_dir`
- `datapipe.source.file_name`
- `datapipe.data.single_file`
- `datapipe.data.initial_step`
- `datapipe.data.reduced_resolution`
- `datapipe.data.reduced_resolution_t`
- `datapipe.data.reduced_batch`
- `datapipe.data.test_ratio`
- `datapipe.dataloader.batch_size`
- MPNN 额外需要 PDE 名称、变量、时空域、分辨率、邻居数和时间窗口。
- PINO 额外需要 PDE residual 降采样和 grid norm 配置。

## 输出规格

- `PDEBenchFNODatapipe`: `(history, target, grid)`。
- `PDEBenchDeepONetDatapipe`: `(history, target, grid)`，并暴露 `dx`、`dt`。
- `PDEBenchMPNNDatapipe`: `(flattened_datapoints, coordinates, variables)`，并暴露 `pde`、`graph_creator`。
- `PDEBenchUNetDatapipe`: `(history, target)`。
- `PDEBenchUNODatapipe`: `(history, target, grid)`。
- `PDEBenchPINODatapipe`: `(history, target, grid)`，并提供 `pde_dataloader()`。

## 约束条件

- 同一源码文件内不同 datapipe 返回协议不同。
- 当前没有统一 `test_dataloader()`。
- 多文件、3D、Maxwell/global_maximums 等分支并不完全等价。
- MPNN 多文件路径存在占位/简化实现，正式使用前需复核。
- 不应从该原语推断存在 `PDEBenchLSMDatapipe` 或 `pdenneval.lsm`。

## 启动方式

Python API 启动示例：

```python
from omegaconf import OmegaConf
from onescience.datapipes.cfd.PDENNEval import PDEBenchFNODatapipe

cfg = OmegaConf.load("conf/pdebench_fno.yaml")
datapipe = PDEBenchFNODatapipe(cfg, distributed=False)
train_loader, train_sampler = datapipe.train_dataloader()
val_loader, val_sampler = datapipe.val_dataloader()
```

CLI 示例：

```sh
python train.py --config-name pdebench_fno datapipe.source.data_dir=/data/PDEBench datapipe.source.file_name=2D_CFD_Rand_M0.1.hdf5 datapipe.data.single_file=true datapipe.data.initial_step=10 datapipe.data.reduced_resolution=1 datapipe.data.reduced_resolution_t=1 datapipe.data.reduced_batch=1 datapipe.dataloader.batch_size=8
```

## 输入规格

- 输入为 PDEBench 风格 HDF5/H5 文件。
- 单文件模式需要文件内直接包含主 tensor 或可组合字段。
- 多文件模式需要 seed/group 结构和 grid 子组。
- 选择 datapipe 类时必须与训练模型族匹配。

## 运行接口

- `PDEBenchFNODatapipe`: FNO 样本协议。
- `PDEBenchDeepONetDatapipe`: DeepONet 样本协议。
- `PDEBenchMPNNDatapipe`: MPNN 数据与图创建器。
- `PDEBenchUNetDatapipe`: UNet 样本协议。
- `PDEBenchUNODatapipe`: UNO 样本协议。
- `PDEBenchPINODatapipe`: PINO 监督与 PDE residual 数据流。
- `train_dataloader()`: 返回训练 loader 和 sampler。
- `val_dataloader()`: 返回验证 loader 和 sampler。
- `pde_dataloader()`: 仅 PINO 提供。

## 主要函数

- `__getitem__`
- `train_dataloader`
- `val_dataloader`
- `pde_dataloader`

## 执行资源

- 需要 HDF5 读取能力。
- 单文件模式可能一次性占用较多内存。
- 多文件懒加载降低初始化内存但增加运行期 I/O。
- MPNN 图构造会额外消耗训练期计算资源。

## 操作限制

- 没有统一测试 loader。
- 不同 datapipe 的 batch 解包方式不可混用。
- 3D 或特殊物理分支需逐类检查字段。
- PINO 和 MPNN 某些分支保留简化逻辑，正式 benchmark 前应补测试。

## 规划决策

### 描述

该原语用于 PDEBench/PDE neural operator 任务编排，在同一 HDF5 数据源上按模型族选择合适的数据协议。

### 使用时机

- 用户数据是 PDEBench 风格 HDF5/H5。
- 目标是 FNO、DeepONet、UNet、UNO、PINO 或 MPNN。
- 需要空间/时间降采样和 initial_step 历史输入。
- 需要多模型评估但允许每个模型使用不同 batch 协议。

### 输入

- HDF5 数据路径和文件名。
- 是否单文件、降采样参数、initial_step、test_ratio。
- 目标模型族。
- 模型族特定参数，例如 MPNN 的 PDE 定义或 PINO 的 PDE residual 配置。

### 输出

- 对应模型族的 train/val dataloader。
- 模型所需 history、target、grid 或 graph creator。
- PINO 的 PDE residual dataloader。

### 执行步骤

1. 先确认任务模型族，不要只按文件名选择 datapipe。
2. 打开 HDF5 检查字段键和维度。
3. 设定降采样和 initial_step，确保输出 shape 匹配模型。
4. 根据模型族实例化对应 Datapipe。
5. 在训练脚本中按该 datapipe 的协议解包 batch。

### 约束

- 返回协议差异是核心约束。
- 不存在统一的默认 LSM datapipe。
- 部分源码分支需要补齐或验证后才能用于正式实验。

### 下一阶段建议

若用户要求 CFD_Benchmark 默认 FNO/U-Net/LSM 路线，先核对模型卡和示例路径；若数据不是 HDF5，而是 case 目录或 pickle，改用 CFDBench 或 DeepCFD；若数据是非结构网格，改用 AirfRANS/ShapeNetCar。

### 回退策略

- 字段不匹配时先离线转换为 PDEBench 标准键。
- 内存不足时从 single_file 切换到多文件懒加载。
- 模型协议不清时先打印一个 batch 的结构再接训练。

## 源码锚点

- `{onescience_path}/onescience/src/onescience/datapipes/cfd/PDENNEval.py`
- `{onescience_path}/onescience/examples/cfd/PDEBench/`
- `{onescience_path}/onescience/src/onescience/datapipes/core/base_dataset.py`
