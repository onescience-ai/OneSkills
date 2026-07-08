# pipeline_responsibility

负责把 AirfRANS 翼型工况目录中的 `manifest.json`、内部流场网格和翼型表面文件组织成点级图样本，覆盖样本划分、VTK 解析、可选裁剪、单元采样、归一化、下采样和构图。

# pipeline_architecture

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

# data_loading

- 从 `source.data_dir/manifest.json` 读取训练全集、测试集名称列表。
- 对每个样本读取 `<sim>/<sim>_internal.vtu` 和 `<sim>/<sim>_aerofoil.vtp`。
- 从样本名中解析来流速度和攻角，用于构造入口条件特征。
- 从 `source.stats_dir` 读取或写入 `mean_in.npy`、`std_in.npy`、`mean_out.npy`、`std_out.npy`。

# sampling_strategy

- train/val 由 `manifest[train_name]` 按 `val_split_ratio` 切分，test 由 `manifest[test_name]` 给出。
- `sample_strategy=null` 时使用内部网格全量点。
- `sample_strategy="uniform"` 时按单元面积和表面线段长度加权采样。
- `sample_strategy="mesh"` 时按单元数量近似均匀采样。
- train/val 若点数超过 `data.subsampling`，再随机保留固定数量点；test 不做该下采样。

# data_transform

- 可选 `data.crop=(xmin, xmax, ymin, ymax)` 对内部网格裁剪。
- 全量模式下用 `U_x == 0` 推断表面点，并将 aerofoil 法向量对齐到内部表面点。
- 采样模式下在体单元和表面线单元内插值得到点坐标与场值。
- 输入和输出按训练集统计量标准化。
- 当 `model_hparams.build_graph=True` 时，按坐标用半径和最大邻居数生成 `edge_index`。

# input_schema

- 数据目录：`<data_dir>/manifest.json`。
- 样本文件：`<data_dir>/<sim_name>/<sim_name>_internal.vtu`、`<data_dir>/<sim_name>/<sim_name>_aerofoil.vtp`。
- 必需字段：
  - internal: `U`、`p`、`nut`、`implicit_distance`
  - aerofoil: `U`、`p`、`nut`、`Normals`
- 关键配置：`source.data_dir`、`source.stats_dir`、`data.splits.*`、`data.sampling.*`、`model_hparams.*`。

# output_schema

- 返回 `Data`。
- `Data.x`: `[NumPoints, 7]`, float, `[pos_x, pos_y, u_inf_x, u_inf_y, sdf, normal_x, normal_y]`。
- `Data.y`: `[NumPoints, 4]`, float, `[v_x, v_y, p, nut]`。
- `Data.pos`: `[NumPoints, 2]`。
- `Data.surf`: `[NumPoints]` 或 `[NumPoints, 1]` 的表面布尔标记。
- `Data.edge_index`: `[2, NumEdges]`，未构图时为空或 `None`。

# constraints

- `manifest.json` 必须包含配置引用的 split 键。
- 样本名需满足代码中的下划线分段解析规则，否则来流条件构造会失败。
- 归一化统计量只能由训练集生成；val/test 初始化时若统计量不存在会报错。
- VTK 字段名和表面点对齐假设是硬约束。
- 该原语面向二维翼型非结构网格，不适合直接处理三维车体或规则栅格数据。

# code_references

- `{onescience_path}/onescience/src/onescience/datapipes/cfd/AirfRANS.py`
- `{onescience_path}/onescience/src/onescience/datapipes/core/base_dataset.py`
- `{onescience_path}/onescience/src/onescience/utils/transolver/reorganize.py`
