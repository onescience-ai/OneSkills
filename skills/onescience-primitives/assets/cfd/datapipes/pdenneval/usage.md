# launch

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

# input_schema

- 输入为 PDEBench 风格 HDF5/H5 文件。
- 单文件模式需要文件内直接包含主 tensor 或可组合字段。
- 多文件模式需要 seed/group 结构和 grid 子组。
- 选择 datapipe 类时必须与训练模型族匹配。

# runtime_interfaces

- `PDEBenchFNODatapipe`: FNO 样本协议。
- `PDEBenchDeepONetDatapipe`: DeepONet 样本协议。
- `PDEBenchMPNNDatapipe`: MPNN 数据与图创建器。
- `PDEBenchUNetDatapipe`: UNet 样本协议。
- `PDEBenchUNODatapipe`: UNO 样本协议。
- `PDEBenchPINODatapipe`: PINO 监督与 PDE residual 数据流。
- `train_dataloader()`: 返回训练 loader 和 sampler。
- `val_dataloader()`: 返回验证 loader 和 sampler。
- `pde_dataloader()`: 仅 PINO 提供。

# main_functions

- `__getitem__`
- `train_dataloader`
- `val_dataloader`
- `pde_dataloader`

# execution_resources

- 需要 HDF5 读取能力。
- 单文件模式可能一次性占用较多内存。
- 多文件懒加载降低初始化内存但增加运行期 I/O。
- MPNN 图构造会额外消耗训练期计算资源。

# operation_limits

- 没有统一测试 loader。
- 不同 datapipe 的 batch 解包方式不可混用。
- 3D 或特殊物理分支需逐类检查字段。
- PINO 和 MPNN 某些分支保留简化逻辑，正式 benchmark 前应补测试。
