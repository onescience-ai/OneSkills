# pipeline_responsibility

负责将 PDEBench 风格 HDF5/H5 数据读取为不同神经算子模型族所需的样本协议，覆盖 FNO、DeepONet、MPNN、UNet、UNO 和 PINO。

# pipeline_architecture

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

# data_loading

- 从 `datapipe.source.data_dir/datapipe.source.file_name` 打开 HDF5/H5 文件。
- 单文件模式一次性读取主要 tensor 和坐标网格。
- 多文件模式按 seed/group 懒加载，常见结构包括 `<seed>/data` 与 `<seed>/grid/*`。
- 支持从 `tensor` 或 `density/pressure/Vx/Vy/Vz` 等键构造数据。

# sampling_strategy

- `reduced_batch` 对样本维降采样。
- `reduced_resolution` 对空间维降采样。
- `reduced_resolution_t` 对时间维降采样。
- `test_ratio` 划分 train/val。
- `initial_step` 决定 history 输入时间步数。
- PINO 的 PDE residual 路径可使用独立降采样参数。

# data_transform

- 构造或读取坐标网格 `grid`。
- 将目标完整轨迹保留为监督 `target`。
- 按模型族差异返回 history、grid 或 flatten 后的 datapoints。
- MPNN 额外构造 `PDE` 与 `GraphCreator`，真正图构造通常在训练循环中完成。
- PINO 暴露 `dx`、`dt`，并额外提供 PDE loss 数据流。

# input_schema

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

# output_schema

- `PDEBenchFNODatapipe`: `(history, target, grid)`。
- `PDEBenchDeepONetDatapipe`: `(history, target, grid)`，并暴露 `dx`、`dt`。
- `PDEBenchMPNNDatapipe`: `(flattened_datapoints, coordinates, variables)`，并暴露 `pde`、`graph_creator`。
- `PDEBenchUNetDatapipe`: `(history, target)`。
- `PDEBenchUNODatapipe`: `(history, target, grid)`。
- `PDEBenchPINODatapipe`: `(history, target, grid)`，并提供 `pde_dataloader()`。

# constraints

- 同一源码文件内不同 datapipe 返回协议不同。
- 当前没有统一 `test_dataloader()`。
- 多文件、3D、Maxwell/global_maximums 等分支并不完全等价。
- MPNN 多文件路径存在占位/简化实现，正式使用前需复核。
- 不应从该原语推断存在 `PDEBenchLSMDatapipe` 或 `pdenneval.lsm`。

# code_references

- `{onescience_path}/onescience/src/onescience/datapipes/cfd/PDENNEval.py`
- `{onescience_path}/onescience/examples/cfd/PDEBench/`
- `{onescience_path}/onescience/src/onescience/datapipes/core/base_dataset.py`
