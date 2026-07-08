# pipeline_responsibility

负责把汽车外流场 VTK 文件或预处理缓存转换为 PyG `Data` 图样本，覆盖 fold 划分、VTK 读取、表面/体点拼接、SDF、法向量、归一化和构图。

# pipeline_architecture

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

# data_loading

- 从 `source.data_dir/param*/<sample>/` 发现样本。
- 读取 `quadpress_smpl.vtk` 和 `hexvelo_smpl.vtk`。
- 若 `source.preprocessed=True` 且缓存存在，优先读取 `x/y/pos/surf/edge_index.npy`。
- 从 `source.stats_dir` 读取或写入 `mean_in.npy`、`std_in.npy`、`mean_out.npy`、`std_out.npy`。

# sampling_strategy

- 当前 fold 逻辑依赖 `param0` 到 `param8` 九个参数分组。
- `data.splits.fold_id` 指定验证 fold，其余 fold 作为训练。
- 一个 dataset 样本对应一个汽车几何工况，不是时间窗。
- datapipe 默认构造 train/val loader；源码中 Dataset 支持 mode 但 Datapipe 未暴露 test loader。

# data_transform

- 从 VTK 点和单元恢复表面压力、外部速度和网格边。
- 计算点到表面的 SDF 与方向。
- 计算或读取表面法向量。
- 将外部速度点和表面压力点拼成统一点集。
- 按训练统计量标准化输入和输出。
- 当 `model_hparams.cfd_mesh=True` 时复用 CFD 网格边；否则按半径图重新构边。

# input_schema

- `<data_dir>/param*/<sample>/quadpress_smpl.vtk`。
- `<data_dir>/param*/<sample>/hexvelo_smpl.vtk`。
- 可选缓存：`<preprocessed_save_dir>/<param*>/<sample>/{x,y,pos,surf,edge_index}.npy`。
- 必需配置：`source.data_dir`、`source.preprocessed_save_dir`、`source.stats_dir`、`data.splits.fold_id`、`model_hparams.cfd_mesh/r/max_neighbors`。

# output_schema

- 返回 `Data`。
- `Data.x`: `[NumPoints, 7]`，通常为 `[pos_x, pos_y, pos_z, sdf, normal_x, normal_y, normal_z]`。
- `Data.y`: `[NumPoints, 4]`，通常为 `[v_x, v_y, v_z, p]`。
- `Data.pos`: `[NumPoints, 3]`。
- `Data.surf`: 表面点标记。
- `Data.edge_index`: `[2, NumEdges]`。

# constraints

- 目录结构默认存在 `param0` 到 `param8`。
- VTK 文件名和字段语义需符合 `quadpress/hexvelo` 约定。
- `surf` 和压力通道被下游 Transolver-Car-Design 损失显式使用。
- 该原语默认 PyG Data 协议，不适合直接喂给 DGL 模型。
- 没有单独 `test_dataloader()`。

# code_references

- `{onescience_path}/onescience/src/onescience/datapipes/cfd/ShapeNetCar.py`
- `{onescience_path}/onescience/examples/cfd/Transolver-Car-Design/train.py`
- `{onescience_path}/onescience/examples/cfd/Transolver-Car-Design/conf/transolver_car.yaml`
