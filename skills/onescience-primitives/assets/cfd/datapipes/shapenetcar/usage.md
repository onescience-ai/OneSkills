# launch

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

# input_schema

- 原始数据按 `param*/sample/` 组织。
- 每个样本至少包含 `quadpress_smpl.vtk` 和 `hexvelo_smpl.vtk`。
- 若启用预处理缓存，缓存目录需包含 `x.npy/y.npy/pos.npy/surf.npy/edge_index.npy`。
- 统计目录需可写，训练阶段会生成归一化统计量。

# runtime_interfaces

- `ShapeNetCarDataset(config, mode, coef_norm=None)`: 构造 train/val 样本。
- `ShapeNetCarDatapipe(params, distributed)`: 构造 train/val dataloader。
- `train_dataloader()`: 返回训练 PyGDataLoader 和 sampler。
- `val_dataloader()`: 返回验证 PyGDataLoader 和 sampler。

# main_functions

- `__getitem__`
- `train_dataloader`
- `val_dataloader`

# execution_resources

- 首次从 VTK 预处理需要较多 CPU 和 I/O。
- SDF、法向量和边构造对点数敏感。
- PyG 图 batch 显存与节点数、边数相关。
- 使用预处理缓存可显著降低后续初始化成本。

# operation_limits

- Datapipe 类没有暴露 `test_dataloader`。
- fold 划分依赖固定 param 目录结构。
- 若只有表面点或只有体点，需要重新定义 `x/y/surf` 协议。
- 半径图构造参数不合理会导致边过密或图断裂。
